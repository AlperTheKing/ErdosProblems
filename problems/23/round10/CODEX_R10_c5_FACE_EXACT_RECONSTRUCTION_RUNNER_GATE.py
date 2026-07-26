"""Self-gate for the future-point exact reconstruction runner.

This audit validates pinned sources, the default/schema-only execution path,
CLI authorization guards, and static presence of every mandatory exact gate.
It deliberately does not call the reconstruction entry point and does not
fabricate a numerical point.
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
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUNNER_PATH = (
    HERE / "CODEX_R10_c5_FACE_EXACT_RECONSTRUCTION_RUNNER.py"
)
ROOT_GATE_PATH = HERE / "CODEX_R10_c5_FACE_EXACT_ROOT_GATE.py"
REPAIR_DATA_PATH = HERE / "CODEX_R10_c5_FACE_REPAIR_MAP_data.npz"
EXACT_KERNEL_PATH = (
    HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
)
NUMERICAL_KERNEL_PATH = (
    HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL_data.npz"
)
LOG_PATH = (
    HERE / "CODEX_R10_c5_FACE_EXACT_RECONSTRUCTION_RUNNER_GATE.log"
)

EXPECTED_SHA256 = {
    "runner": "D87F65FB55A5BE72BF70D564C646EB088CBE97698569BB0E98F62B68C5F8E73B",
    "root_gate": "51B86E6CC14AC7436707C379A37AB936AB6304E193E8BC3BA977BCADE6DCB761",
    "repair_data": "2F82F46A5C740164D47AB74F532C8D7BBED3AE97270894A18BA04D8F78DFF8D2",
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


def containing_function(
    tree: ast.AST, target: ast.AST
) -> str | None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if target in set(ast.walk(node)):
                return node.name
    return None


def static_audit(source: str) -> dict[str, object]:
    tree = ast.parse(source)
    calls = list(
        node for node in ast.walk(tree) if isinstance(node, ast.Call)
    )
    reconstruction_calls = [
        node
        for node in calls
        if isinstance(node.func, ast.Name)
        and node.func.id == "execute_reconstruction"
    ]
    solve_den_calls = [
        node
        for node in calls
        if isinstance(node.func, ast.Attribute)
        and node.func.attr == "solve_den"
    ]
    binary_calls = [
        node
        for node in calls
        if isinstance(node.func, ast.Attribute)
        and node.func.attr == "from_float"
    ]
    subprocess_calls = [
        node
        for node in calls
        if isinstance(node.func, ast.Attribute)
        and node.func.attr == "run"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
    ]
    pickle_writes = [
        node
        for node in calls
        if isinstance(node.func, ast.Attribute)
        and node.func.attr == "dump"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "pickle"
    ]
    assert len(reconstruction_calls) == 1
    assert containing_function(tree, reconstruction_calls[0]) == "main"
    assert len(solve_den_calls) == 1
    assert containing_function(tree, solve_den_calls[0]) == "solve_repair"
    assert len(binary_calls) >= 2
    assert all(
        containing_function(tree, node)
        in {"binary_quotients_from_q", "execute_reconstruction"}
        for node in binary_calls
    )
    assert len(subprocess_calls) == 2
    assert all(
        containing_function(tree, node) == "execute_reconstruction"
        for node in subprocess_calls
    )
    assert len(pickle_writes) == 2
    assert all(
        containing_function(tree, node) == "execute_reconstruction"
        for node in pickle_writes
    )
    required_literals = [
        "if not args.run:",
        "input/output/denominator arguments require explicit --run",
        "one of 56 original normalization rows failed",
        "one of 392 original target rows failed",
        "exact Hq gate failed",
        "Q=B Q[C,C] B^T gate failed",
        "Q4_verify hard rejection",
        "independent root replay failed",
        "nearest integer with ties to even",
    ]
    for literal in required_literals:
        assert literal in source
    return {
        "execute_reconstruction_calls": len(reconstruction_calls),
        "fraction_free_solve_den_calls": len(solve_den_calls),
        "exact_binary_from_float_calls": len(binary_calls),
        "independent_root_subprocess_calls": len(subprocess_calls),
        "atomic_candidate_pickle_writes": len(pickle_writes),
        "mandatory_gate_literals": "PASS",
    }


def root_gate_independence_audit() -> dict[str, object]:
    source = ROOT_GATE_PATH.read_text(encoding="utf-8")
    forbidden = [
        "CODEX_R10_c5_FACE_EXACT_RECONSTRUCTION_RUNNER",
        "CODEX_R10_g11_d22_sdp",
        "Q4_verify",
        "Q4_sos",
    ]
    for name in forbidden:
        if name in source:
            raise AssertionError(f"root gate contains forbidden import {name}")
    tree = ast.parse(source)
    imported_modules = sorted(
        {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        | {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
    )
    return {
        "forbidden_constructor_or_verifier_imports": 0,
        "imported_modules": imported_modules,
        "explicit_certificate_argument": (
            "There is deliberately no default certificate path." in source
        ),
    }


def cli_guard_audit() -> dict[str, object]:
    missing = subprocess.run(
        [sys.executable, str(RUNNER_PATH), "--run"],
        cwd=HERE,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    unauthorized = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--input",
            "DOES_NOT_EXIST.npz",
        ],
        cwd=HERE,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    root_help = subprocess.run(
        [sys.executable, str(ROOT_GATE_PATH), "--help"],
        cwd=HERE,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert missing.returncode == 2
    assert "--run requires" in missing.stderr
    assert unauthorized.returncode == 2
    assert "require explicit --run" in unauthorized.stderr
    assert root_help.returncode == 0
    return {
        "run_without_fields_returncode": missing.returncode,
        "fields_without_run_returncode": unauthorized.returncode,
        "root_gate_help_without_certificate_returncode": root_help.returncode,
    }


def main() -> None:
    paths = {
        "runner": RUNNER_PATH,
        "root_gate": ROOT_GATE_PATH,
        "repair_data": REPAIR_DATA_PATH,
        "exact_kernel": EXACT_KERNEL_PATH,
        "numerical_kernel": NUMERICAL_KERNEL_PATH,
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    assert hashes == EXPECTED_SHA256, hashes
    source = RUNNER_PATH.read_text(encoding="utf-8")
    static = static_audit(source)
    root_independence = root_gate_independence_audit()
    cli = cli_guard_audit()
    module = load_module(
        "codex_r10_exact_reconstruction_runner_gate_target",
        RUNNER_PATH,
    )
    context = module.build_context()
    schema = module.schema_summary(context)
    assert schema["status"] == "READY_BUILD_ONLY"
    assert schema["solver_or_reconstruction_run"] is False
    assert schema["dimensions"]["original_affine_rows"] == 448
    assert schema["dimensions"]["H_rows"] == 6129
    assert schema["dimensions"]["repair_nu_coordinates"] == 322
    assert schema["dimensions"]["repair_gram_directions"] == 66

    reconstruction_tripwire_calls = 0
    original_reconstruction = module.execute_reconstruction
    original_argv = sys.argv

    def forbidden_reconstruction(*_args, **_kwargs):
        nonlocal reconstruction_tripwire_calls
        reconstruction_tripwire_calls += 1
        raise AssertionError("default path attempted reconstruction")

    stdout = io.StringIO()
    try:
        module.execute_reconstruction = forbidden_reconstruction
        sys.argv = [str(RUNNER_PATH)]
        with contextlib.redirect_stdout(stdout):
            module.main()
    finally:
        module.execute_reconstruction = original_reconstruction
        sys.argv = original_argv
    assert reconstruction_tripwire_calls == 0
    assert "EXACT_RECONSTRUCTION_READY_BUILD_ONLY" in stdout.getvalue()

    # Pure arithmetic helper checks only; no candidate construction or repair.
    assert module.round_fraction(Fraction(1, 4), 2) == 0
    assert module.round_fraction(Fraction(3, 4), 2) == 1
    assert module.round_fraction(Fraction(-1, 4), 2) == 0
    assert module.round_fraction(Fraction(-3, 4), 2) == -1
    numerators, denominator = module.common_integer_matrix(
        [
            [Fraction(1, 2), Fraction(1, 3)],
            [Fraction(1, 3), Fraction(1, 2)],
        ]
    )
    assert denominator == 6
    assert numerators == [[3, 2], [2, 3]]

    output = {
        "status": "PASS",
        "scope": (
            "runner default/schema/build self-gate only; no numerical "
            "point and no reconstruction"
        ),
        "hashes": hashes,
        "static": static,
        "root_gate_independence": root_independence,
        "cli_guards": cli,
        "context": {
            "blocks": len(context.blocks),
            "H_shape": list(context.h.shape),
            "repair_shape": list(context.repair_matrix.shape),
            "repair_direction_shape": list(context.directions.shape),
        },
        "default_path": {
            "reconstruction_tripwire_calls": reconstruction_tripwire_calls,
            "ready_marker": "PASS",
        },
        "rounding_helper": "ties-to-even PASS",
        "common_denominator_helper": "PASS",
        "numerical_point_processed": False,
        "certificate_claim": False,
    }
    LOG_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(output, indent=2, sort_keys=True))
    print(
        "EXACT_RECONSTRUCTION_RUNNER_GATE_PASS: "
        "numerical_point_processed=false"
    )
    print(f"LOG={LOG_PATH}")
    print(f"SHA256_GATE={sha256(Path(__file__))}")
    print(f"SHA256_LOG={sha256(LOG_PATH)}")


if __name__ == "__main__":
    main()
