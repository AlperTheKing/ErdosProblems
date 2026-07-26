"""SCS 3.2.11 wrapper for the pinned H-eliminated plateau-face SDP.

Default execution only builds and canonicalizes the identical reduced model.
A numerical solve requires both ``--solve`` and a new explicit ``--output``
path.  The fixed SCS settings are:

    eps_abs=eps_rel=1e-7, max_iters=200000,
    time_limit_secs=3600, acceleration_lookback=20, normalize=True.

Any exported point is numerical steering data only.  Exact reconstruction in
the sealed integer kernel and exact replay remain mandatory for a proof.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

import cvxpy as cp
import numpy as np
import scs


HERE = Path(__file__).resolve().parent
MODEL_SOURCE = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP.py"
EXPECTED_MODEL_SOURCE_SHA256 = (
    "C040263A69AE8DE4B09CB3F3C6DA1E094A90E2CB711E3917DF9AD5749C8831F1"
)
EXPECTED_SCS_VERSION = "3.2.11"
EXPECTED_A_SHAPE = (16369, 3045)
EXPECTED_A_NNZ = 8_574_476
EXPECTED_ZERO_CONE = 388
EXPECTED_NONNEGATIVE_CONE = 543
EXPECTED_PSD_ORDERS = [
    154,
    32,
    35,
    40,
    5,
    32,
    6,
    8,
    33,
    6,
    6,
    7,
    6,
    4,
    7,
    8,
    6,
    5,
    4,
    4,
    6,
    5,
    4,
    4,
    6,
    11,
]
SCS_OPTIONS = {
    "eps_abs": 1e-7,
    "eps_rel": 1e-7,
    "max_iters": 200_000,
    "time_limit_secs": 3600.0,
    "acceleration_lookback": 20,
    "normalize": True,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_pinned_model_module():
    observed_hash = sha256(MODEL_SOURCE)
    if observed_hash != EXPECTED_MODEL_SOURCE_SHA256:
        raise AssertionError(
            "reduced-SDP source SHA-256 mismatch: "
            f"{observed_hash} != {EXPECTED_MODEL_SOURCE_SHA256}"
        )
    if scs.__version__ != EXPECTED_SCS_VERSION:
        raise AssertionError(
            f"SCS version {scs.__version__} != {EXPECTED_SCS_VERSION}"
        )
    if cp.SCS not in cp.installed_solvers():
        raise RuntimeError("CVXPY does not expose the pinned SCS solver")
    spec = importlib.util.spec_from_file_location(
        "codex_r10_c5_reduced_sdp_scs_pinned", MODEL_SOURCE
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {MODEL_SOURCE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def canonicalize_scs(model) -> dict[str, object]:
    """Canonicalize for SCS and reject any model/cone/order drift."""
    started = time.perf_counter()
    data, _chain, _inverse = model.problem.get_problem_data(cp.SCS)
    seconds = time.perf_counter() - started
    a_matrix = data["A"].tocsc()
    dims = data["dims"]
    if a_matrix.shape != EXPECTED_A_SHAPE:
        raise AssertionError(f"unexpected SCS A shape {a_matrix.shape}")
    if a_matrix.nnz != EXPECTED_A_NNZ:
        raise AssertionError(f"unexpected SCS A nnz {a_matrix.nnz}")
    if int(dims.zero) != EXPECTED_ZERO_CONE:
        raise AssertionError(f"unexpected zero cone {dims.zero}")
    if int(dims.nonneg) != EXPECTED_NONNEGATIVE_CONE:
        raise AssertionError(
            f"unexpected nonnegative cone {dims.nonneg}"
        )
    if list(map(int, dims.psd)) != EXPECTED_PSD_ORDERS:
        raise AssertionError(f"unexpected PSD cones {dims.psd}")
    if dims.soc or int(dims.exp) or dims.p3d:
        raise AssertionError(f"unexpected non-PSD cone data {dims}")
    if (
        not np.all(np.isfinite(a_matrix.data))
        or not np.all(np.isfinite(data["b"]))
        or not np.all(np.isfinite(data["c"]))
    ):
        raise AssertionError("nonfinite SCS canonical data")
    if np.any(a_matrix.data == 0.0):
        raise AssertionError("SCS canonical A contains an explicit zero")
    if np.any(np.diff(a_matrix.indptr) == 0):
        raise AssertionError("SCS canonical A has a zero column")
    a_csr = a_matrix.tocsr()
    if np.any(np.diff(a_csr.indptr) == 0):
        raise AssertionError("SCS canonical A has a zero row")
    coefficient_abs = np.abs(a_matrix.data)
    summary = {
        "status": "PASS",
        "scope": "SCS build/canonicalization only; no solve",
        "solver": f"SCS {scs.__version__}",
        "variables": int(a_matrix.shape[1]),
        "A_shape": list(map(int, a_matrix.shape)),
        "A_nnz": int(a_matrix.nnz),
        "zero_cone": int(dims.zero),
        "nonnegative_cone": int(dims.nonneg),
        "PSD_cones": list(map(int, dims.psd)),
        "zero_rows": 0,
        "zero_columns": 0,
        "coefficient_min_abs": float(coefficient_abs.min()),
        "coefficient_max_abs": float(coefficient_abs.max()),
        "seconds": seconds,
        "solver_called": False,
    }
    return summary


def numeric_scalar(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, (bool, int, float, str)) or value is None:
        return value
    return str(value)


def selected_scs_info(stats) -> dict[str, object]:
    """Keep scalar SCS diagnostics without exporting large x/y/s duplicates."""
    if not isinstance(stats.extra_stats, dict):
        return {}
    info = stats.extra_stats.get("info")
    if not isinstance(info, dict):
        return {}
    keys = (
        "status_val",
        "iter",
        "scale_updates",
        "scale",
        "pobj",
        "dobj",
        "res_pri",
        "res_dual",
        "gap",
        "res_infeas",
        "res_unbdd_a",
        "res_unbdd_p",
        "comp_slack",
        "solve_time",
        "setup_time",
        "lin_sys_time",
        "cone_time",
        "accel_time",
        "rejected_accel_steps",
        "accepted_accel_steps",
        "status",
    )
    return {
        key: numeric_scalar(info[key])
        for key in keys
        if key in info
    }


def solve_scs(model):
    print(
        "REDUCED_SDP_SCS_SOLVE_START "
        f"solver=SCS version={scs.__version__} "
        f"options={json.dumps(SCS_OPTIONS, sort_keys=True)}"
    )
    started = time.perf_counter()
    value = model.problem.solve(
        solver=cp.SCS,
        verbose=True,
        warm_start=False,
        **SCS_OPTIONS,
    )
    elapsed = time.perf_counter() - started
    print(
        "REDUCED_SDP_SCS_SOLVE_DONE "
        f"status={model.problem.status!r} objective={value!r} "
        f"wall_seconds={elapsed:.6f}"
    )
    return value, elapsed


def solve_metadata(
    model,
    value,
    elapsed: float,
) -> dict[str, object]:
    stats = model.problem.solver_stats
    return {
        "solver": "SCS",
        "solver_version": scs.__version__,
        "status": model.problem.status,
        "objective": float(value),
        "wall_seconds": float(elapsed),
        "solve_time": (
            None if stats.solve_time is None else float(stats.solve_time)
        ),
        "setup_time": (
            None if stats.setup_time is None else float(stats.setup_time)
        ),
        "num_iters": (
            None if stats.num_iters is None else int(stats.num_iters)
        ),
        "options": SCS_OPTIONS,
        "model_source_sha256": EXPECTED_MODEL_SOURCE_SHA256,
        "wrapper_source_sha256": sha256(Path(__file__)),
        "scs_info": selected_scs_info(stats),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--solve",
        action="store_true",
        help="explicitly authorize the pinned SCS 3.2.11 solve",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="new .npz destination required together with --solve",
    )
    args = parser.parse_args()
    if args.solve and args.output is None:
        parser.error("--solve requires an explicit --output NEW_FILE.npz")
    if args.output is not None and not args.solve:
        parser.error("--output is accepted only together with --solve")
    if args.output is not None:
        output = args.output.resolve()
        if output.suffix.lower() != ".npz":
            parser.error("--output must end in .npz")
        if not output.parent.is_dir():
            parser.error(f"output directory does not exist: {output.parent}")
        if output.exists():
            parser.error(f"refusing to overwrite existing output: {output}")
        args.output = output
    return args


def main() -> int:
    args = parse_args()
    reduced = load_pinned_model_module()
    model = reduced.build_model()
    build_summary = canonicalize_scs(model)
    print(json.dumps(build_summary, indent=2, sort_keys=True))
    if not args.solve:
        print(
            "REDUCED_SDP_SCS_BUILD_ONLY_PASS "
            "solver_called=false no_file_written=true"
        )
        return 0

    value, elapsed = solve_scs(model)
    if model.problem.status not in {cp.OPTIMAL, cp.OPTIMAL_INACCURATE}:
        raise RuntimeError(
            f"SCS returned status {model.problem.status}; "
            "no numerical solution archive written"
        )
    if value is None or not np.isfinite(value):
        raise RuntimeError("SCS returned no finite objective value")
    if (
        model.nu_live.value is None
        or model.face_coordinates.value is None
        or model.margin.value is None
    ):
        raise RuntimeError("SCS status has no primal variable values")

    diagnostics, arrays = reduced.reconstruct_and_diagnose(
        model,
        model.nu_live.value,
        model.face_coordinates.value,
        float(model.margin.value),
    )
    metadata = solve_metadata(model, value, elapsed)
    output_hash = reduced.export_solution(
        args.output,
        model,
        diagnostics,
        arrays,
        metadata,
        overwrite=False,
    )
    print(json.dumps(diagnostics, indent=2, sort_keys=True))
    print(json.dumps(metadata, indent=2, sort_keys=True))
    print(f"OUTPUT={args.output}")
    print(f"SHA256_OUTPUT={output_hash}")
    print(
        "REDUCED_SDP_SCS_NUMERICAL_RESULT_WRITTEN "
        "exact_reconstruction_required=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
