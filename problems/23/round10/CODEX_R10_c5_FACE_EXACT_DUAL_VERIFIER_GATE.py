"""Independent no-solver, no-input gate for the exact dual verifier."""

from __future__ import annotations

import ast
import contextlib
from fractions import Fraction
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

import cvxpy as cp


HERE = Path(__file__).resolve().parent
SOURCE_PATH = HERE / "CODEX_R10_c5_FACE_EXACT_DUAL_VERIFIER.py"
EXPECTED_SOURCE_SHA256 = (
    "9366CCD624C32CAC644D9E6DE79F17EA758450893EAE77D935A2AFFE42F72A60"
)


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


def static_audit(source: str) -> dict[str, object]:
    tree = ast.parse(source)
    calls = [
        node for node in ast.walk(tree) if isinstance(node, ast.Call)
    ]
    solver_calls = [
        node for node in calls
        if isinstance(node.func, ast.Attribute)
        and node.func.attr in {
            "solve", "solve_scs", "installed_solvers", "get_problem_data"
        }
    ]
    write_calls = [
        node for node in calls
        if isinstance(node.func, ast.Attribute)
        and node.func.attr in {
            "write_text", "write_bytes", "save", "savez", "savez_compressed"
        }
    ]
    if solver_calls:
        raise AssertionError("exact verifier contains a solver/canonicalizer call")
    if write_calls:
        raise AssertionError("exact verifier contains a file-write call")
    required = (
        "Z^T(A_q^T lambda - C^*(gamma,S)) = 0",
        "cone_weight - beta != 1",
        "separating requires exact lambda^T b < 0",
        "exposing_face requires primal_witness",
        "floats and booleans are forbidden",
        "EXACT_DUAL_VERIFIER_BUILD_ONLY_PASS",
    )
    for text in required:
        if text not in source:
            raise AssertionError(f"missing exact semantic gate text: {text}")
    return {
        "solver_or_canonicalizer_calls": 0,
        "file_write_calls": 0,
        "semantic_gate_markers": "PASS",
    }


def main() -> int:
    observed = sha256(SOURCE_PATH)
    if observed != EXPECTED_SOURCE_SHA256:
        raise AssertionError(
            f"exact verifier source drift: {observed}"
        )
    source = SOURCE_PATH.read_text(encoding="utf-8")
    static = static_audit(source)
    module = load_module("codex_r10_exact_dual_gate_target", SOURCE_PATH)

    solver_calls = 0
    candidate_calls = 0
    original_solve = cp.Problem.solve
    original_verify_candidate = module.verify_candidate
    original_argv = sys.argv

    def forbidden_solve(*_args, **_kwargs):
        nonlocal solver_calls
        solver_calls += 1
        raise AssertionError("default path attempted a solver call")

    def forbidden_candidate(*_args, **_kwargs):
        nonlocal candidate_calls
        candidate_calls += 1
        raise AssertionError("default path attempted candidate processing")

    stdout = io.StringIO()
    before = {
        path.resolve()
        for pattern in ("*.npz", "*.json", "*.pkl")
        for path in HERE.glob(pattern)
    }
    try:
        cp.Problem.solve = forbidden_solve
        module.verify_candidate = forbidden_candidate
        sys.argv = [str(SOURCE_PATH)]
        with contextlib.redirect_stdout(stdout):
            return_code = module.main()
    finally:
        sys.argv = original_argv
        module.verify_candidate = original_verify_candidate
        cp.Problem.solve = original_solve
    after = {
        path.resolve()
        for pattern in ("*.npz", "*.json", "*.pkl")
        for path in HERE.glob(pattern)
    }
    if return_code != 0 or solver_calls != 0 or candidate_calls != 0:
        raise AssertionError("default tripwire path failed")
    if before != after:
        raise AssertionError("default path changed an artifact file")
    if "EXACT_DUAL_VERIFIER_BUILD_ONLY_PASS" not in stdout.getvalue():
        raise AssertionError("default build-only marker missing")

    context = module.build_context()
    summary = module.schema_summary(context)
    if summary["fixed_cone"]["affine_rows"] != 388:
        raise AssertionError("affine row count drift")
    if summary["fixed_cone"]["PSD_upper_triangle_entries"] != 15438:
        raise AssertionError("PSD coordinate count drift")
    if summary["solver_called"] is not False:
        raise AssertionError("schema lost the no-solver marker")

    rank_one, _ = module.exact_psd(
        [
            [Fraction(1), Fraction(1)],
            [Fraction(1), Fraction(1)],
        ],
        "rank-one test",
    )
    rank_two, _ = module.exact_psd(
        [
            [Fraction(2), Fraction(1)],
            [Fraction(1), Fraction(1)],
        ],
        "positive-definite test",
    )
    if rank_one != 1 or rank_two != 2:
        raise AssertionError("exact PSD self-tests returned wrong ranks")
    indefinite_rejected = False
    try:
        module.exact_psd(
            [
                [Fraction(0), Fraction(1)],
                [Fraction(1), Fraction(0)],
            ],
            "indefinite test",
        )
    except ValueError:
        indefinite_rejected = True
    if not indefinite_rejected:
        raise AssertionError("exact PSD gate accepted an indefinite matrix")
    float_rejected = False
    try:
        module.parse_fraction(0.0, "float test")
    except TypeError:
        float_rejected = True
    if not float_rejected:
        raise AssertionError("exact fraction gate accepted a float")

    output = {
        "status": "PASS",
        "scope": "independent build-only exact-dual gate",
        "source_sha256": observed,
        "static": static,
        "tripwires": {
            "solver_calls": solver_calls,
            "candidate_calls": candidate_calls,
            "artifact_set_unchanged": True,
        },
        "structure": {
            "H_shape": list(context.gram_face.shape),
            "Z_shape": list(context.exact_basis.shape),
            "HZ_nnz": int((context.gram_face @ context.exact_basis).nnz),
            "scalar_blocks": 16,
            "PSD_blocks": 26,
            "PSD_upper_triangle_entries": 15438,
        },
        "self_tests": {
            "rank_one_PSD": "PASS",
            "positive_definite": "PASS",
            "indefinite_rejection": "PASS",
            "float_rejection": "PASS",
        },
        "solver_invoked": False,
        "candidate_processed": False,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    print(
        "EXACT_DUAL_VERIFIER_GATE_PASS "
        "solver_invoked=false candidate_processed=false"
    )
    print(f"SHA256_GATE={sha256(Path(__file__))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
