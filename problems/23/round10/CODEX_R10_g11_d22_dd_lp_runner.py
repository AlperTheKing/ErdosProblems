"""Explicit solve/export wrapper for the sealed-G DD LP.

The pinned model source is build-only.  Running this wrapper without both
``--solve`` and ``--output NEW_FILE.npz`` only rebuilds/audits that model and
does not launch an optimizer or write a file.  The exported Gram vector is the
full 8,647-coordinate numerical q vector; it is steering data for later exact
reconstruction, not an exact certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
MODEL_SOURCE = HERE / "CODEX_R10_g11_d22_dd_lp_v2.py"
EXPECTED_MODEL_SOURCE_SHA256 = (
    "5D067D1D579168C2C87E2ACCEF5287D5EAC2E64930F514224A3D22CE6DAB4153"
)

METHOD = "highs-ipm"
SOLVER_OPTIONS = {
    "presolve": True,
    "dual_feasibility_tolerance": 1e-9,
    "primal_feasibility_tolerance": 1e-9,
    "ipm_optimality_tolerance": 1e-10,
    "time_limit": 1800.0,
    "disp": True,
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
            "DD model source SHA-256 mismatch: "
            f"{observed_hash} != {EXPECTED_MODEL_SOURCE_SHA256}"
        )
    spec = importlib.util.spec_from_file_location(
        "codex_r10_g11_d22_dd_lp_v2_pinned", MODEL_SOURCE
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {MODEL_SOURCE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def solve(model):
    # Kept inside the explicit solve path so importing/building this wrapper
    # cannot accidentally initialize or invoke an optimizer.
    from scipy.optimize import linprog

    print(
        "DD_LP_SOLVE_START "
        f"method={METHOD} options={SOLVER_OPTIONS} "
        "scope=numerical_steering_only"
    )
    result = linprog(
        model.objective,
        A_ub=model.a_ub,
        b_ub=model.b_ub,
        A_eq=model.a_eq,
        b_eq=model.b_eq,
        bounds=model.bounds,
        method=METHOD,
        options=SOLVER_OPTIONS,
    )
    print(
        "DD_LP_SOLVE_DONE "
        f"success={result.success} status={result.status} "
        f"message={result.message!r} nit={getattr(result, 'nit', None)} "
        f"crossover_nit={getattr(result, 'crossover_nit', None)}"
    )
    return result


def diagnose(dd, model, result):
    if not result.success or result.status != 0 or result.x is None:
        raise RuntimeError(
            "refusing diagnostics/export for unsuccessful solve: "
            f"status={result.status}, message={result.message}"
        )
    vector = np.asarray(result.x, dtype=np.float64)
    if vector.shape != (dd.VARIABLE_COUNT,):
        raise AssertionError(f"wrong solution shape {vector.shape}")
    if not np.all(np.isfinite(vector)):
        raise AssertionError("solver returned a nonfinite solution")

    nu = vector[: dd.LIVE_COUNT]
    z = vector[dd.LIVE_COUNT : dd.LIVE_COUNT + dd.FACE_DIMENSION]
    margin = float(vector[model.margin_column])
    shared_absolute = vector[model.absolute_start :]
    full_q = np.asarray(model.numerical_basis @ z).reshape(-1)
    if full_q.shape != (dd.GRAM_COUNT,):
        raise AssertionError(f"wrong reconstructed full-q shape {full_q.shape}")

    equality_residual = np.asarray(
        model.a_eq @ vector - model.b_eq
    ).reshape(-1)
    inequality_residual = np.asarray(
        model.a_ub @ vector - model.b_ub
    ).reshape(-1)
    h_residual = np.asarray(
        model.plateau.gram_face @ full_q
    ).reshape(-1)
    original_affine_residual = np.asarray(
        model.affine_nu @ nu
        + model.affine_q @ full_q
        - model.affine_rhs
    ).reshape(-1)
    absolute_slack = (
        shared_absolute
        - np.abs(full_q[model.offdiagonal_coordinates])
    )

    quotient_orders: list[int] = []
    quotient_min_eigenvalues: list[float] = []
    quotient_min_diagonals: list[float] = []
    quotient_min_dd_slacks: list[float] = []
    q_offset = 0
    for orbit, free in zip(
        model.plateau.base.gram_orbits,
        model.plateau.free_coordinates,
    ):
        local_size = int(orbit.variable.size)
        free = list(map(int, free))
        quotient_orders.append(len(free))
        if free:
            local_q = full_q[q_offset : q_offset + local_size]
            quotient = local_q[
                orbit.entry_ids[np.ix_(free, free)]
            ]
            if not np.allclose(
                quotient, quotient.T, rtol=0.0, atol=0.0
            ):
                raise AssertionError("reconstructed quotient is not symmetric")
            diagonal = np.diag(quotient)
            radii = np.sum(np.abs(quotient), axis=1) - np.abs(diagonal)
            quotient_min_eigenvalues.append(
                float(np.linalg.eigvalsh(quotient)[0])
            )
            quotient_min_diagonals.append(float(np.min(diagonal)))
            quotient_min_dd_slacks.append(
                float(np.min(diagonal - radii))
            )
        else:
            quotient_min_eigenvalues.append(float("nan"))
            quotient_min_diagonals.append(float("nan"))
            quotient_min_dd_slacks.append(float("nan"))
        q_offset += local_size
    if q_offset != dd.GRAM_COUNT:
        raise AssertionError(f"consumed {q_offset} full-q coordinates")

    finite_eigenvalues = np.asarray(
        quotient_min_eigenvalues, dtype=np.float64
    )
    finite_diagonals = np.asarray(
        quotient_min_diagonals, dtype=np.float64
    )
    finite_dd_slacks = np.asarray(
        quotient_min_dd_slacks, dtype=np.float64
    )
    diagnostics = {
        "objective_value": float(result.fun),
        "margin": margin,
        "minimum_live_nu": float(np.min(nu)),
        "minimum_live_margin_slack": float(np.min(nu - margin)),
        "minimum_shared_absolute": float(np.min(shared_absolute)),
        "minimum_absolute_envelope_slack": float(np.min(absolute_slack)),
        "minimum_quotient_diagonal": float(
            np.nanmin(finite_diagonals)
        ),
        "minimum_quotient_dd_slack": float(
            np.nanmin(finite_dd_slacks)
        ),
        "minimum_quotient_eigenvalue": float(
            np.nanmin(finite_eigenvalues)
        ),
        "equality_residual_inf": float(
            np.max(np.abs(equality_residual))
        ),
        "inequality_residual_max": float(
            np.max(inequality_residual)
        ),
        "inequality_violation_max": float(
            max(0.0, np.max(inequality_residual))
        ),
        "original_H_residual_inf": float(
            np.max(np.abs(h_residual))
        ),
        "original_affine_residual_inf": float(
            np.max(np.abs(original_affine_residual))
        ),
    }
    print(
        "DD_LP_DIAGNOSTICS "
        + " ".join(f"{key}={value:.16e}" for key, value in diagnostics.items())
    )
    payload = {
        "vector": vector,
        "live_nu": nu,
        "kernel_coordinates": z,
        "margin": np.asarray([margin], dtype=np.float64),
        "shared_absolute": shared_absolute,
        "full_q": full_q,
        "quotient_orders": np.asarray(quotient_orders, dtype=np.int32),
        "quotient_min_eigenvalues": finite_eigenvalues,
        "quotient_min_diagonals": finite_diagonals,
        "quotient_min_dd_slacks": finite_dd_slacks,
        "diagnostics": diagnostics,
    }
    return payload


def export(output: Path, dd, model, result, payload) -> None:
    # The path was validated before the solve and is checked again immediately
    # before the only write performed by this wrapper.
    output = output.resolve()
    if output.suffix.lower() != ".npz":
        raise ValueError("--output must have suffix .npz")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")

    diagnostics = payload["diagnostics"]
    fields = {
        "format_version": np.asarray([1], dtype=np.int32),
        "role": np.asarray(
            [
                "numerical DD-LP steering point; "
                "not an exact certificate"
            ]
        ),
        "solver_method": np.asarray([METHOD]),
        "solver_status_code": np.asarray([int(result.status)], dtype=np.int32),
        "solver_success": np.asarray([bool(result.success)]),
        "solver_message": np.asarray([str(result.message)]),
        "solver_iterations": np.asarray(
            [int(getattr(result, "nit", -1))], dtype=np.int64
        ),
        "objective_value": np.asarray(
            [float(result.fun)], dtype=np.float64
        ),
        "variables": payload["vector"],
        "live_multiplier_values": payload["live_nu"],
        "numerical_kernel_coordinates": payload["kernel_coordinates"],
        "margin": payload["margin"],
        "shared_absolute_values": payload["shared_absolute"],
        "full_gram_coordinates": payload["full_q"],
        "quotient_orders": payload["quotient_orders"],
        "quotient_min_eigenvalues": payload[
            "quotient_min_eigenvalues"
        ],
        "quotient_min_diagonals": payload["quotient_min_diagonals"],
        "quotient_min_dd_slacks": payload["quotient_min_dd_slacks"],
        "model_source_sha256": np.asarray(
            [EXPECTED_MODEL_SOURCE_SHA256]
        ),
        "runner_source_sha256": np.asarray([sha256(Path(__file__))]),
    }
    for key, value in model.hashes.items():
        fields[f"pinned_{key}_sha256"] = np.asarray([value])
    for key, value in diagnostics.items():
        fields[key] = np.asarray([value], dtype=np.float64)
    np.savez_compressed(output, **fields)
    print(
        f"DD_LP_EXPORT path={output} "
        f"sha256={sha256(output)} full_q_length={payload['full_q'].size}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--solve",
        action="store_true",
        help="explicitly launch the pinned HiGHS-IPM solve",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="new .npz path; required with --solve and never overwritten",
    )
    args = parser.parse_args()
    if args.solve and args.output is None:
        parser.error("--solve requires --output")
    if args.output is not None and not args.solve:
        parser.error("--output requires --solve")
    if args.output is not None:
        candidate = args.output.resolve()
        if candidate.suffix.lower() != ".npz":
            parser.error("--output must have suffix .npz")
        if candidate.exists():
            parser.error(f"refusing to overwrite existing output: {candidate}")
        args.output = candidate
    return args


def main() -> int:
    args = parse_args()
    dd = load_pinned_model_module()
    model = dd.build_model()
    if not args.solve:
        print(
            "DD_LP_RUNNER_BUILD_ONLY no_solver_launched=true "
            "no_file_written=true"
        )
        return 0

    result = solve(model)
    if not result.success or result.status != 0:
        print("DD_LP_EXPORT_SKIPPED reason=unsuccessful_solve")
        return 2
    payload = diagnose(dd, model, result)
    export(args.output, dd, model, result, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
