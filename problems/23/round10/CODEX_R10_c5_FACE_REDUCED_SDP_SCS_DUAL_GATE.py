"""Independent no-solve tripwire gate for the SCS dual-export extension."""

from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

import cvxpy as cp
import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_SCS_DUAL.py"
PRIMARY_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_SCS.py"
MODEL_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP.py"
EXPECTED_SHA256 = {
    "source": "B0C4A2EB4D50C21A6DEB1F0D83D1327546793D6B1D9B10DE9E92DABC7E6C168A",
    "primary": "6BD44D50EBB8E8F2D142F055A0F9C073939B1FBE85A7B1381D29601CD921D319",
    "model": "C040263A69AE8DE4B09CB3F3C6DA1E094A90E2CB711E3917DF9AD5749C8831F1",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def static_audit(source_text: str) -> dict[str, object]:
    tree = ast.parse(source_text)
    calls = [
        node for node in ast.walk(tree) if isinstance(node, ast.Call)
    ]
    direct_solve_calls = [
        node
        for node in calls
        if isinstance(node.func, ast.Attribute)
        and node.func.attr == "solve"
    ]
    delegated_solve_calls = [
        node
        for node in calls
        if isinstance(node.func, ast.Attribute)
        and node.func.attr == "solve_scs"
    ]
    export_calls = [
        node
        for node in calls
        if isinstance(node.func, ast.Attribute)
        and node.func.attr == "savez_compressed"
    ]
    if direct_solve_calls:
        raise AssertionError("dual extension contains a direct solver call")
    if len(delegated_solve_calls) != 1:
        raise AssertionError("expected one pinned delegated solve call")
    if len(export_calls) != 1:
        raise AssertionError("expected one explicit NPZ export call")
    guard_line = next(
        line_number
        for line_number, line in enumerate(
            source_text.splitlines(), start=1
        )
        if line.strip() == "if not args.solve:"
    )
    if guard_line >= int(delegated_solve_calls[0].lineno):
        raise AssertionError("solve delegation is not behind default guard")
    required_text = (
        "--solve requires an explicit --output NEW_FILE.npz",
        "--output is accepted only together with --solve",
        "refusing to overwrite existing output",
        '"raw_canonical_y"',
        '"dual_affine_equalities"',
        '"dual_live_nu_minus_margin"',
        '"dual_margin_nonnegative"',
        '"dual_scalar_quotient_values"',
        '"dual_psd_matrices_flat"',
        '"psd_svec_offsets"',
        '"raw_y_cone_offsets"',
    )
    for text in required_text:
        if text not in source_text:
            raise AssertionError(f"missing guarded dual field/text: {text}")
    return {
        "direct_solve_calls": 0,
        "delegated_solve_calls": 1,
        "delegated_solve_line": int(delegated_solve_calls[0].lineno),
        "default_return_guard_line": guard_line,
        "npz_export_calls": 1,
        "required_dual_fields": "PASS",
        "implicit_default_output_absent": "DEFAULT_OUTPUT" not in source_text,
    }


def main() -> int:
    paths = {
        "source": SOURCE_PATH,
        "primary": PRIMARY_PATH,
        "model": MODEL_PATH,
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned source mismatch: {hashes}")
    source_text = SOURCE_PATH.read_text(encoding="utf-8")
    static = static_audit(source_text)
    module = load_module(
        "codex_r10_c5_scs_dual_tripwire_target", SOURCE_PATH
    )

    solver_calls = 0
    original_solve = cp.Problem.solve

    def forbidden_solve(*_args, **_kwargs):
        nonlocal solver_calls
        solver_calls += 1
        raise AssertionError("default path attempted to invoke a solver")

    original_argv = sys.argv
    stdout = io.StringIO()
    before_npz = {
        path.resolve() for path in HERE.glob("*.npz")
    }
    try:
        cp.Problem.solve = forbidden_solve
        sys.argv = [str(SOURCE_PATH)]
        with contextlib.redirect_stdout(stdout):
            return_code = module.main()
    finally:
        sys.argv = original_argv
        cp.Problem.solve = original_solve
    after_npz = {
        path.resolve() for path in HERE.glob("*.npz")
    }
    if return_code != 0 or solver_calls != 0:
        raise AssertionError("default tripwire path failed")
    if before_npz != after_npz:
        raise AssertionError("default path created or removed an NPZ")
    if "REDUCED_SDP_SCS_DUAL_BUILD_ONLY_PASS" not in stdout.getvalue():
        raise AssertionError("default build-only marker missing")

    primary = module.load_primary_wrapper()
    reduced = primary.load_pinned_model_module()
    model = reduced.build_model()
    canonical = primary.canonicalize_scs(model)
    layout = module.semantic_constraint_layout(model)
    if model.problem.status is not None:
        raise AssertionError("build-only model unexpectedly has a status")
    if (
        model.nu_live.value is not None
        or model.face_coordinates.value is not None
        or model.margin.value is not None
    ):
        raise AssertionError("build-only model unexpectedly has primal values")
    if canonical["A_shape"] != [16369, 3045]:
        raise AssertionError("canonical shape drift")
    if canonical["A_nnz"] != 8_574_476:
        raise AssertionError("canonical nnz drift")
    if layout["semantic_constraint_indices"].shape != (42,):
        raise AssertionError("wrong nonempty-block constraint count")
    if layout["scalar_block_indices"].shape != (16,):
        raise AssertionError("wrong scalar dual count")
    if layout["psd_block_indices"].shape != (26,):
        raise AssertionError("wrong PSD dual count")
    if layout["psd_flat_offsets"][0] != 0:
        raise AssertionError("PSD flat offsets do not start at zero")
    if layout["psd_svec_offsets"][0] != 931:
        raise AssertionError("PSD svec offsets start in wrong cone")
    if layout["psd_svec_offsets"][-1] != 16369:
        raise AssertionError("PSD svec offsets do not close")
    if not np.array_equal(
        layout["raw_y_cone_offsets"],
        np.asarray([0, 388, 931, 16369], dtype=np.int64),
    ):
        raise AssertionError("raw y cone offsets drifted")

    output = {
        "status": "PASS",
        "scope": "build/static/semantic dual audit; no solver invoked",
        "hashes": hashes,
        "static": static,
        "default_path": {
            "solver_tripwire_calls": solver_calls,
            "return_code": return_code,
            "build_only_marker": "PASS",
            "NPZ_set_unchanged": True,
        },
        "canonical": {
            "A_shape": canonical["A_shape"],
            "A_nnz": canonical["A_nnz"],
            "zero_cone": canonical["zero_cone"],
            "nonnegative_cone": canonical["nonnegative_cone"],
            "PSD_cones": canonical["PSD_cones"],
        },
        "semantic_duals": {
            "constraints": 45,
            "affine_equalities": 388,
            "live_nu_minus_margin": 526,
            "margin_nonnegative": 1,
            "scalar_quotient_blocks": 16,
            "PSD_matrices": 26,
            "raw_y_length": 16369,
            "raw_y_cone_offsets": [0, 388, 931, 16369],
            "PSD_svec_offsets_close": True,
        },
        "solver_invoked": False,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    print("REDUCED_SDP_SCS_DUAL_GATE_PASS solver_invoked=false")
    print(f"SHA256_GATE={sha256(Path(__file__))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
