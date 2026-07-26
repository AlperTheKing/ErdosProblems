"""Guarded solve-capable reduced SDP for the Gamma_11 plateau face.

Default execution is build/canonicalization only.  A numerical solve requires
both ``--solve`` and an explicit ``--output`` path.  The numerical direct-H QR
basis is used only for steering; the sealed exact-Z artifact remains the
required basis for exact reconstruction and proof replay.

This source is deliberately add-only relative to the audited plateau files.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import cvxpy as cp
import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
CANONICAL_SOURCE = (
    HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_CANONICALIZE.py"
)
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
ROW_REDUCTION_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
EXACT_KERNEL_PATH = (
    HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
)
NUMERICAL_KERNEL_PATH = (
    HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL_data.npz"
)

EXPECTED_SHA256 = {
    "canonical_source": "2FD5C5D55D87828DD8FF8121FB2644C61DAC78166736B2B066A9A582140C1799",
    "base": "AB2F222EAE5052FD3DCD64311D05419E4150759C1DB4BD33E5AE30D313CDFEEE",
    "blowup": "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730",
    "equality": "08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F",
    "row_reduction": "F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C",
    "exact_kernel": "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C",
    "numerical_kernel": "CBD479AF7071FC95ABF02AB2193738C75359E39672F1421E0C7D1B2FCFB199D3",
}
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


def unpack_csr(archive, name: str, dtype) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive[f"{name}_data"].astype(dtype),
            archive[f"{name}_indices"].astype(np.int32),
            archive[f"{name}_indptr"].astype(np.int64),
        ),
        shape=tuple(int(value) for value in archive[f"{name}_shape"]),
        dtype=dtype,
    )


@dataclass
class ReducedSdpModel:
    hashes: dict[str, str]
    base: object
    blowup: object
    equality: object
    row_reduction: object
    exact_kernel: object
    numerical_kernel: object
    forced: np.ndarray
    live: np.ndarray
    g: sp.csr_matrix
    h: sp.csr_matrix
    affine_nu: sp.csr_matrix
    affine_q: sp.csr_matrix
    affine_y: sp.csr_matrix
    affine_rhs: np.ndarray
    free_by_block: list[list[int]]
    quotient_orders: list[int]
    psd_orders: list[int]
    nu_live: cp.Variable
    face_coordinates: cp.Variable
    margin: cp.Variable
    problem: cp.Problem


def build_model() -> ReducedSdpModel:
    paths = {
        "canonical_source": CANONICAL_SOURCE,
        "base": BASE_PATH,
        "blowup": BLOWUP_PATH,
        "equality": EQUALITY_PATH,
        "row_reduction": ROW_REDUCTION_PATH,
        "exact_kernel": EXACT_KERNEL_PATH,
        "numerical_kernel": NUMERICAL_KERNEL_PATH,
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned input hash mismatch: {hashes}")

    canonical = load_module(
        "codex_r10_reduced_sdp_canonical_helpers", CANONICAL_SOURCE
    )
    builder = load_module("codex_r10_reduced_sdp_base", BASE_PATH)
    base = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    row_reduction = np.load(ROW_REDUCTION_PATH, allow_pickle=False)
    exact_kernel = np.load(EXACT_KERNEL_PATH, allow_pickle=False)
    numerical_kernel = np.load(NUMERICAL_KERNEL_PATH, allow_pickle=False)

    forced = equality["forced_multiplier_orbits"].astype(np.int32)
    live = equality["live_multiplier_orbits"].astype(np.int32)
    if len(forced) != 2085 or len(live) != 526:
        raise AssertionError("multiplier face dimensions mismatch")
    if not np.array_equal(forced, blowup["forced_multiplier_orbits"]):
        raise AssertionError("forced multiplier ordering mismatch")
    if not np.array_equal(live, blowup["live_multiplier_orbits"]):
        raise AssertionError("live multiplier ordering mismatch")
    if sorted(map(int, np.concatenate((forced, live)))) != list(range(2611)):
        raise AssertionError("forced/live multiplier partition mismatch")

    g = unpack_csr(numerical_kernel, "numerical_basis", np.float64)
    h = unpack_csr(blowup, "gram_face", np.float64)
    exact_shape = tuple(
        int(value) for value in exact_kernel["exact_basis_shape"]
    )
    if exact_shape != (8647, 2518):
        raise AssertionError("sealed exact-Z shape mismatch")
    if g.shape != exact_shape or h.shape != (6129, 8647):
        raise AssertionError("kernel basis dimensions mismatch")
    if numerical_kernel["role"].tolist() != [
        "numerical-only direct-H QR; never an exact certificate"
    ]:
        raise AssertionError("numerical kernel role mismatch")
    h_residual = float(np.max(np.abs(h @ g)))
    if h_residual > 1e-12:
        raise AssertionError(f"numerical kernel H residual={h_residual}")

    q_offsets = blowup["gram_offsets"].astype(np.int64)
    q_dimensions = blowup["gram_qdims"].astype(np.int64)
    face_dimensions = equality["gram_face_dimensions"].astype(np.int64)
    face_offsets = exact_kernel["face_column_offsets"].astype(np.int64)
    if not np.array_equal(
        numerical_kernel["gram_offsets"], q_offsets
    ) or not np.array_equal(
        numerical_kernel["gram_qdims"], q_dimensions
    ):
        raise AssertionError("numerical kernel Gram ordering mismatch")
    if not np.array_equal(
        numerical_kernel["gram_face_dimensions"], face_dimensions
    ) or not np.array_equal(
        numerical_kernel["face_column_offsets"], face_offsets
    ):
        raise AssertionError("numerical kernel face ordering mismatch")

    affine_nu = unpack_csr(row_reduction, "affine_nu", np.float64)
    affine_q = unpack_csr(row_reduction, "affine_gram", np.float64)
    affine_rhs = row_reduction["affine_rhs"].astype(np.float64)
    if (
        affine_nu.shape != (388, 526)
        or affine_q.shape != (388, 8647)
        or affine_rhs.shape != (388,)
    ):
        raise AssertionError("reduced affine dimensions mismatch")
    affine_y = (affine_q @ g).tocsr()
    if affine_y.shape != (388, 2518):
        raise AssertionError("face affine dimensions mismatch")

    free_by_block = canonical.free_coordinates(blowup, base)
    quotient_orders = [len(free) for free in free_by_block]
    nu_live = cp.Variable(526, name="live_multiplier_orbits")
    face_coordinates = cp.Variable(2518, name="gram_face_coordinates")
    margin = cp.Variable(name="relative_margin")
    constraints: list[cp.Constraint] = [
        affine_nu @ nu_live
        + affine_y @ face_coordinates
        == affine_rhs,
        nu_live >= margin,
        margin >= 0,
    ]
    psd_orders: list[int] = []
    scalar_cones = 0
    for block, (orbit, free) in enumerate(
        zip(base.gram_orbits, free_by_block)
    ):
        order = len(free)
        if order == 0:
            continue
        q0 = int(q_offsets[block])
        qdim = int(q_dimensions[block])
        f0 = int(face_offsets[block])
        fdim = int(face_dimensions[block])
        local_q = (
            g[q0 : q0 + qdim, f0 : f0 + fdim]
            @ face_coordinates[f0 : f0 + fdim]
        )
        ids = orbit.entry_ids[np.ix_(free, free)].astype(np.int64)
        if order == 1:
            constraints.append(local_q[int(ids[0, 0])] >= margin)
            scalar_cones += 1
        else:
            principal = cp.reshape(
                local_q[ids.reshape(-1)],
                (order, order),
                order="C",
            )
            constraints.append(
                principal - margin * np.eye(order) >> 0
            )
            psd_orders.append(order)
    if scalar_cones != 16 or psd_orders != EXPECTED_PSD_ORDERS:
        raise AssertionError("quotient cone ordering mismatch")

    problem = cp.Problem(cp.Maximize(margin), constraints)
    if not problem.is_dcp():
        raise AssertionError("reduced SDP is not DCP")
    return ReducedSdpModel(
        hashes=hashes,
        base=base,
        blowup=blowup,
        equality=equality,
        row_reduction=row_reduction,
        exact_kernel=exact_kernel,
        numerical_kernel=numerical_kernel,
        forced=forced,
        live=live,
        g=g,
        h=h,
        affine_nu=affine_nu,
        affine_q=affine_q,
        affine_y=affine_y,
        affine_rhs=affine_rhs,
        free_by_block=free_by_block,
        quotient_orders=quotient_orders,
        psd_orders=psd_orders,
        nu_live=nu_live,
        face_coordinates=face_coordinates,
        margin=margin,
        problem=problem,
    )


def canonicalize(model: ReducedSdpModel) -> dict[str, object]:
    started = time.perf_counter()
    data, _chain, _inverse = model.problem.get_problem_data(cp.CLARABEL)
    seconds = time.perf_counter() - started
    a_matrix = data["A"].tocsc()
    dims = data["dims"]
    if a_matrix.shape != (16369, 3045) or a_matrix.nnz != 8_574_476:
        raise AssertionError(
            f"canonical A mismatch: {a_matrix.shape}/{a_matrix.nnz}"
        )
    if (
        int(dims.zero) != 388
        or int(dims.nonneg) != 543
        or list(map(int, dims.psd)) != model.psd_orders
        or dims.soc
        or int(dims.exp)
        or dims.p3d
    ):
        raise AssertionError(f"canonical cone mismatch: {dims}")
    if (
        not np.all(np.isfinite(a_matrix.data))
        or not np.all(np.isfinite(data["b"]))
        or not np.all(np.isfinite(data["c"]))
    ):
        raise AssertionError("non-finite canonical data")
    return {
        "status": "PASS",
        "scope": "build/canonicalization only; no solve",
        "variables": int(a_matrix.shape[1]),
        "A_shape": list(a_matrix.shape),
        "A_nnz": int(a_matrix.nnz),
        "zero_cone": int(dims.zero),
        "nonnegative_cone": int(dims.nonneg),
        "PSD_cones": list(map(int, dims.psd)),
        "seconds": seconds,
        "solver_called": False,
        "input_sha256": model.hashes,
    }


def reconstruct_and_diagnose(
    model: ReducedSdpModel,
    nu_live: np.ndarray,
    face_coordinates: np.ndarray,
    margin: float,
) -> tuple[dict[str, object], dict[str, np.ndarray]]:
    nu_live = np.asarray(nu_live, dtype=np.float64).reshape(-1)
    face_coordinates = np.asarray(
        face_coordinates, dtype=np.float64
    ).reshape(-1)
    margin = float(margin)
    if nu_live.shape != (526,) or face_coordinates.shape != (2518,):
        raise ValueError("solver variable dimensions mismatch")
    if (
        not np.all(np.isfinite(nu_live))
        or not np.all(np.isfinite(face_coordinates))
        or not np.isfinite(margin)
    ):
        raise ValueError("non-finite solver variables")

    q = np.asarray(model.g @ face_coordinates).reshape(-1)
    nu = np.zeros(2611, dtype=np.float64)
    nu[model.live] = nu_live
    if not np.all(nu[model.forced] == 0):
        raise AssertionError("forced multiplier reconstruction failed")

    equality = model.equality
    normalization_live = unpack_csr(
        equality, "normalization_live", np.float64
    )
    target_nu_live = unpack_csr(
        equality, "target_nu_live", np.float64
    )
    target_q = unpack_csr(equality, "target_gram", np.float64)
    normalization_residual = (
        normalization_live @ nu_live
        - equality["normalization_rhs"].astype(np.float64)
    )
    target_residual = (
        target_nu_live @ nu_live
        + target_q @ q
        - equality["target_rhs"].astype(np.float64)
    )
    retained_residual = (
        model.affine_nu @ nu_live
        + model.affine_q @ q
        - model.affine_rhs
    )
    h_residual = np.asarray(model.h @ q).reshape(-1)

    q_offsets = model.blowup["gram_offsets"].astype(np.int64)
    quotient_min_eigenvalues = np.full(52, np.nan, dtype=np.float64)
    quotient_margin_gaps = np.full(52, np.nan, dtype=np.float64)
    ambient_min_eigenvalues = np.full(52, np.nan, dtype=np.float64)
    maximum_symmetry_residual = 0.0
    for block, (orbit, free) in enumerate(
        zip(model.base.gram_orbits, model.free_by_block)
    ):
        q0 = int(q_offsets[block])
        local = q[
            q0 : q0 + int(model.blowup["gram_qdims"][block])
        ]
        ambient = local[orbit.entry_ids]
        maximum_symmetry_residual = max(
            maximum_symmetry_residual,
            float(np.max(np.abs(ambient - ambient.T))),
        )
        ambient_min_eigenvalues[block] = float(
            np.linalg.eigvalsh(ambient)[0]
        )
        if free:
            principal = ambient[np.ix_(free, free)]
            minimum = float(np.linalg.eigvalsh(principal)[0])
            quotient_min_eigenvalues[block] = minimum
            quotient_margin_gaps[block] = minimum - margin

    finite_quotient = quotient_min_eigenvalues[
        np.isfinite(quotient_min_eigenvalues)
    ]
    finite_gaps = quotient_margin_gaps[
        np.isfinite(quotient_margin_gaps)
    ]
    residual_inf = max(
        float(np.max(np.abs(normalization_residual))),
        float(np.max(np.abs(target_residual))),
        float(np.max(np.abs(retained_residual))),
        float(np.max(np.abs(h_residual))),
    )
    scale = max(
        1.0,
        float(np.max(np.abs(equality["normalization_rhs"]))),
        float(np.max(np.abs(equality["target_rhs"]))),
    )
    feasibility_tolerance = 1e-7 * scale
    minimum_nu_gap = float(np.min(nu_live - margin))
    minimum_quotient_gap = float(np.min(finite_gaps))
    numerical_strict_feasible = bool(
        margin > feasibility_tolerance
        and residual_inf <= feasibility_tolerance
        and minimum_nu_gap >= -feasibility_tolerance
        and minimum_quotient_gap >= -feasibility_tolerance
    )
    diagnostics = {
        "scope": "numerical steering only; not an exact certificate",
        "margin": margin,
        "nu_min": float(np.min(nu_live)),
        "nu_max": float(np.max(nu_live)),
        "minimum_nu_minus_margin": minimum_nu_gap,
        "minimum_quotient_eigenvalue": float(np.min(finite_quotient)),
        "minimum_quotient_eigenvalue_minus_margin": minimum_quotient_gap,
        "minimum_ambient_eigenvalue": float(
            np.min(ambient_min_eigenvalues)
        ),
        "maximum_symmetry_residual": maximum_symmetry_residual,
        "normalization_residual_inf": float(
            np.max(np.abs(normalization_residual))
        ),
        "target_residual_inf": float(np.max(np.abs(target_residual))),
        "retained_affine_residual_inf": float(
            np.max(np.abs(retained_residual))
        ),
        "H_residual_inf": float(np.max(np.abs(h_residual))),
        "combined_residual_inf": residual_inf,
        "feasibility_tolerance": feasibility_tolerance,
        "numerical_strict_feasible": numerical_strict_feasible,
    }
    arrays = {
        "nu_live": nu_live,
        "nu_full": nu,
        "gram_face_coordinates": face_coordinates,
        "q_full": q,
        "normalization_residual": np.asarray(
            normalization_residual, dtype=np.float64
        ),
        "target_residual": np.asarray(target_residual, dtype=np.float64),
        "retained_affine_residual": np.asarray(
            retained_residual, dtype=np.float64
        ),
        "H_residual": h_residual,
        "quotient_min_eigenvalues": quotient_min_eigenvalues,
        "quotient_margin_gaps": quotient_margin_gaps,
        "ambient_min_eigenvalues": ambient_min_eigenvalues,
    }
    return diagnostics, arrays


def export_solution(
    output_path: Path,
    model: ReducedSdpModel,
    diagnostics: dict[str, object],
    arrays: dict[str, np.ndarray],
    solver_metadata: dict[str, object],
    *,
    overwrite: bool = False,
) -> str:
    output_path = output_path.resolve()
    if output_path.suffix.lower() != ".npz":
        raise ValueError("--output must end in .npz")
    if not output_path.parent.is_dir():
        raise ValueError(f"output directory does not exist: {output_path.parent}")
    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"refusing to overwrite {output_path}; pass --overwrite explicitly"
        )
    payload: dict[str, np.ndarray] = {
        "format_version": np.asarray([1], dtype=np.int32),
        "role": np.asarray(
            ["numerical steering only; exact replay required"]
        ),
        "diagnostics_json": np.asarray(
            [json.dumps(diagnostics, sort_keys=True)]
        ),
        "solver_metadata_json": np.asarray(
            [json.dumps(solver_metadata, sort_keys=True)]
        ),
        "relative_margin": np.asarray(
            [float(diagnostics["margin"])], dtype=np.float64
        ),
        "forced_multiplier_orbits": model.forced.astype(np.int32),
        "live_multiplier_orbits": model.live.astype(np.int32),
    }
    for name, value in model.hashes.items():
        payload[f"{name}_sha256"] = np.asarray([value])
    payload.update(arrays)
    np.savez_compressed(output_path, **payload)
    return sha256(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the reduced plateau SDP; solve only with explicit "
            "--solve and --output."
        )
    )
    parser.add_argument(
        "--solve",
        action="store_true",
        help="explicitly authorize a numerical Clarabel solve",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="explicit .npz destination required with --solve",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="allow replacement of the explicit output path",
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--max-iter", type=int, default=500)
    parser.add_argument("--time-limit", type=float, default=3600.0)
    parser.add_argument("--tol-gap-abs", type=float, default=1e-9)
    parser.add_argument("--tol-gap-rel", type=float, default=1e-9)
    parser.add_argument("--tol-feas", type=float, default=1e-9)
    args = parser.parse_args()
    if args.solve and args.output is None:
        parser.error("--solve requires an explicit --output PATH.npz")
    if not args.solve and args.output is not None:
        parser.error("--output is accepted only together with --solve")
    if args.overwrite and not args.solve:
        parser.error("--overwrite is accepted only together with --solve")
    return args


def main() -> None:
    args = parse_args()
    model = build_model()
    build_summary = canonicalize(model)
    print(json.dumps(build_summary, indent=2, sort_keys=True))
    if not args.solve:
        print("REDUCED_SDP_BUILD_ONLY_PASS: solver_called=false")
        return

    solver_options = {
        "max_iter": args.max_iter,
        "time_limit": args.time_limit,
        "tol_gap_abs": args.tol_gap_abs,
        "tol_gap_rel": args.tol_gap_rel,
        "tol_feas": args.tol_feas,
    }
    solve_started = time.perf_counter()
    value = model.problem.solve(
        solver=cp.CLARABEL,
        verbose=args.verbose,
        warm_start=False,
        **solver_options,
    )
    solve_seconds = time.perf_counter() - solve_started
    if model.problem.status not in {cp.OPTIMAL, cp.OPTIMAL_INACCURATE}:
        raise RuntimeError(
            f"Clarabel returned status {model.problem.status}; "
            "no numerical solution archive written"
        )
    if (
        model.nu_live.value is None
        or model.face_coordinates.value is None
        or model.margin.value is None
    ):
        raise RuntimeError("solver status has no primal variable values")
    diagnostics, arrays = reconstruct_and_diagnose(
        model,
        model.nu_live.value,
        model.face_coordinates.value,
        float(model.margin.value),
    )
    stats = model.problem.solver_stats
    solver_metadata = {
        "solver": "CLARABEL",
        "status": model.problem.status,
        "objective": float(value),
        "wall_seconds": solve_seconds,
        "solve_time": (
            None if stats.solve_time is None else float(stats.solve_time)
        ),
        "setup_time": (
            None if stats.setup_time is None else float(stats.setup_time)
        ),
        "num_iters": (
            None if stats.num_iters is None else int(stats.num_iters)
        ),
        "options": solver_options,
    }
    output_hash = export_solution(
        args.output,
        model,
        diagnostics,
        arrays,
        solver_metadata,
        overwrite=args.overwrite,
    )
    print(json.dumps(diagnostics, indent=2, sort_keys=True))
    print(f"OUTPUT={args.output.resolve()}")
    print(f"SHA256_OUTPUT={output_hash}")
    print(
        "REDUCED_SDP_NUMERICAL_RESULT_WRITTEN: "
        "exact reconstruction and replay still required"
    )


if __name__ == "__main__":
    main()
