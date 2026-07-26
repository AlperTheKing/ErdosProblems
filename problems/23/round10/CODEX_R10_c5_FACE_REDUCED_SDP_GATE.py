"""Independent no-solve audit of the guarded reduced-SDP fallback.

The audit verifies pinned sources, executes the default build-only CLI path
with ``Problem.solve`` replaced by a tripwire, rechecks canonical dimensions,
and exercises reconstruction/export with deterministic mock arrays.  It never
invokes an optimization solver.
"""

from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

import cvxpy as cp
import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP.py"
CANONICAL_SOURCE = (
    HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_CANONICALIZE.py"
)
EXACT_KERNEL_PATH = (
    HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
)
NUMERICAL_KERNEL_PATH = (
    HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL_data.npz"
)
LOG_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_GATE.log"

EXPECTED_SHA256 = {
    "source": "C040263A69AE8DE4B09CB3F3C6DA1E094A90E2CB711E3917DF9AD5749C8831F1",
    "canonical_source": "2FD5C5D55D87828DD8FF8121FB2644C61DAC78166736B2B066A9A582140C1799",
    "exact_kernel": "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C",
    "numerical_kernel": "CBD479AF7071FC95ABF02AB2193738C75359E39672F1421E0C7D1B2FCFB199D3",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest().upper()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def static_source_audit(source_text: str) -> dict[str, object]:
    tree = ast.parse(source_text)
    solve_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "solve"
    ]
    export_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "savez_compressed"
    ]
    assert len(solve_calls) == 1
    assert len(export_calls) == 1
    solve_line = int(solve_calls[0].lineno)
    guard_line = next(
        line_number
        for line_number, line in enumerate(source_text.splitlines(), start=1)
        if line.strip() == "if not args.solve:"
    )
    assert guard_line < solve_line
    assert "--solve requires an explicit --output PATH.npz" in source_text
    assert "--output is accepted only together with --solve" in source_text
    assert "refusing to overwrite" in source_text
    assert "DEFAULT_OUTPUT" not in source_text
    return {
        "solve_call_count": len(solve_calls),
        "solve_call_line": solve_line,
        "default_return_guard_line": guard_line,
        "npz_export_call_count": len(export_calls),
        "implicit_default_output_absent": True,
    }


def cli_rejection_audit() -> dict[str, object]:
    missing_output = subprocess.run(
        [sys.executable, str(SOURCE_PATH), "--solve"],
        cwd=HERE,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    output_without_solve = subprocess.run(
        [
            sys.executable,
            str(SOURCE_PATH),
            "--output",
            str(HERE / "MUST_NOT_EXIST_AUDIT.npz"),
        ],
        cwd=HERE,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert missing_output.returncode == 2
    assert "--solve requires an explicit --output" in missing_output.stderr
    assert output_without_solve.returncode == 2
    assert "--output is accepted only together with --solve" in (
        output_without_solve.stderr
    )
    assert not (HERE / "MUST_NOT_EXIST_AUDIT.npz").exists()
    return {
        "solve_without_output_returncode": missing_output.returncode,
        "output_without_solve_returncode": output_without_solve.returncode,
        "no_implicit_output_created": True,
    }


def main() -> None:
    hashes = {
        "source": sha256(SOURCE_PATH),
        "canonical_source": sha256(CANONICAL_SOURCE),
        "exact_kernel": sha256(EXACT_KERNEL_PATH),
        "numerical_kernel": sha256(NUMERICAL_KERNEL_PATH),
    }
    assert hashes == EXPECTED_SHA256, hashes
    source_text = SOURCE_PATH.read_text(encoding="utf-8")
    static = static_source_audit(source_text)
    cli_rejections = cli_rejection_audit()
    module = load_module("codex_r10_reduced_sdp_gate_target", SOURCE_PATH)

    # End-to-end default path with a tripwire that forbids any solver call.
    original_solve = cp.Problem.solve
    solve_call_count = 0

    def forbidden_solve(*_args, **_kwargs):
        nonlocal solve_call_count
        solve_call_count += 1
        raise AssertionError("default path attempted to invoke a solver")

    original_argv = sys.argv
    default_output = io.StringIO()
    try:
        cp.Problem.solve = forbidden_solve
        sys.argv = [str(SOURCE_PATH)]
        with contextlib.redirect_stdout(default_output):
            module.main()
    finally:
        sys.argv = original_argv
        cp.Problem.solve = original_solve
    assert solve_call_count == 0
    assert "REDUCED_SDP_BUILD_ONLY_PASS: solver_called=false" in (
        default_output.getvalue()
    )

    model = module.build_model()
    canonical = module.canonicalize(model)
    assert canonical["status"] == "PASS"
    assert canonical["solver_called"] is False
    assert canonical["variables"] == 3045
    assert canonical["A_shape"] == [16369, 3045]
    assert canonical["A_nnz"] == 8_574_476
    assert model.problem.status is None
    assert model.nu_live.value is None
    assert model.face_coordinates.value is None
    assert model.margin.value is None

    # Pure reconstruction and export-schema audit with zero mock data.
    diagnostics, arrays = module.reconstruct_and_diagnose(
        model,
        np.zeros(526, dtype=np.float64),
        np.zeros(2518, dtype=np.float64),
        0.0,
    )
    assert diagnostics["margin"] == 0.0
    assert diagnostics["numerical_strict_feasible"] is False
    assert arrays["nu_full"].shape == (2611,)
    assert arrays["q_full"].shape == (8647,)
    assert arrays["normalization_residual"].shape == (56,)
    assert arrays["target_residual"].shape == (392,)
    assert arrays["retained_affine_residual"].shape == (388,)
    assert arrays["H_residual"].shape == (6129,)
    assert np.all(arrays["nu_full"][model.forced] == 0)
    assert np.all(arrays["q_full"] == 0)

    mock_output = (
        HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_GATE_MOCK.npz"
    )
    if mock_output.exists():
        raise AssertionError("stale task-owned mock export exists")
    archive = None
    try:
        mock_hash = module.export_solution(
            mock_output,
            model,
            diagnostics,
            arrays,
            {
                "solver": "AUDIT_MOCK_NO_SOLVER",
                "status": "NOT_SOLVED",
                "objective": None,
            },
        )
        assert mock_hash == sha256(mock_output)
        archive = np.load(mock_output, allow_pickle=False)
        assert archive["format_version"].tolist() == [1]
        assert archive["role"].tolist() == [
            "numerical steering only; exact replay required"
        ]
        assert archive["nu_live"].shape == (526,)
        assert archive["nu_full"].shape == (2611,)
        assert archive["gram_face_coordinates"].shape == (2518,)
        assert archive["q_full"].shape == (8647,)
        assert archive["exact_kernel_sha256"].tolist() == [
            EXPECTED_SHA256["exact_kernel"]
        ]
        assert archive["numerical_kernel_sha256"].tolist() == [
            EXPECTED_SHA256["numerical_kernel"]
        ]
        try:
            module.export_solution(
                mock_output,
                model,
                diagnostics,
                arrays,
                {"solver": "AUDIT_MOCK_NO_SOLVER"},
            )
        except FileExistsError:
            overwrite_guard = "PASS"
        else:
            raise AssertionError("export overwrite guard did not fire")
    finally:
        if archive is not None:
            archive.close()
        if mock_output.exists():
            mock_output.unlink()

    output = {
        "status": "PASS",
        "scope": "independent build/canonical/export audit; no solver invoked",
        "hashes": hashes,
        "static_source": static,
        "cli_rejections": cli_rejections,
        "default_path": {
            "solver_tripwire_calls": solve_call_count,
            "build_only_marker": "PASS",
        },
        "canonical": canonical,
        "mock_reconstruction": {
            "nu_full_shape": list(arrays["nu_full"].shape),
            "q_full_shape": list(arrays["q_full"].shape),
            "normalization_residual_shape": list(
                arrays["normalization_residual"].shape
            ),
            "target_residual_shape": list(
                arrays["target_residual"].shape
            ),
            "H_residual_shape": list(arrays["H_residual"].shape),
            "forced_nu_zero": True,
        },
        "export_path": {
            "explicit_npz_schema": "PASS",
            "overwrite_guard": overwrite_guard,
            "temporary_artifact_removed": True,
            "solver_metadata": "AUDIT_MOCK_NO_SOLVER",
        },
        "solver_invoked": False,
    }
    LOG_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(output, indent=2, sort_keys=True))
    print("REDUCED_SDP_GATE_PASS: solver_invoked=false")
    print(f"LOG={LOG_PATH}")
    print(f"SHA256_GATE={sha256(Path(__file__))}")
    print(f"SHA256_LOG={sha256(LOG_PATH)}")


if __name__ == "__main__":
    main()
