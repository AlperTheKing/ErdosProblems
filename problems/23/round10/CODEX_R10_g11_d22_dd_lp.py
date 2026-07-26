"""Build-only diagonally-dominant LP on the exact Gamma_11 plateau face.

This is a sufficient inner approximation to the quotient PSD constraints in
``CODEX_R10_g11_d22_plateau_face.py``.  It makes the exact substitution

    q in ker(H)

at the level of dimensions, but deliberately uses a fresh blockwise
orthonormal basis obtained from a direct QR factorization of ``H.T`` for
numerical coordinates.  The pinned exact integer kernel artifact proves the
underlying 2,518-dimensional parameterization and is the required target for
any later exact reconstruction.

For each nonempty quotient principal matrix R, the LP imposes

    R_ii - sum_{j != i} |R_ij| >= margin.

Absolute values are linearized with one shared auxiliary per invariant Gram
coordinate that occurs off the diagonal.  Multiplicities in every matrix row
are counted explicitly.  Gershgorin's theorem then gives
``lambda_min(R) >= margin``.  Thus a solution with positive margin is a
sufficient strict-interior point for the plateau-face SDP.  Failure of this LP
would exclude only the diagonally-dominant subcone, not the full PSD cone.

The default action only constructs and audits the LP matrices.  No solver is
launched and no file is written unless an explicit future ``--solve`` flag is
given; export additionally requires ``--output``.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import importlib.util
from pathlib import Path
import sys

import numpy as np
import scipy.linalg as la
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
PLATEAU_SOURCE = HERE / "CODEX_R10_g11_d22_plateau_face.py"
ROW_DATA_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
KERNEL_DATA_PATH = (
    HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
)

EXPECTED_PLATEAU_SOURCE_SHA256 = (
    "110579CCFA3372BFEB377B857271F509CAC1D771C2E95627E0880FD026D3678A"
)
EXPECTED_ROW_DATA_SHA256 = (
    "F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C"
)
EXPECTED_KERNEL_DATA_SHA256 = (
    "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C"
)

LIVE_COUNT = 526
GRAM_COUNT = 8647
FACE_DIMENSION = 2518
AFFINE_RANK = 388
QUOTIENT_DIAGONAL_COUNT = 460
OFFDIAGONAL_COORDINATE_COUNT = 4524
OFFDIAGONAL_PAIR_COUNT = 14994
VARIABLE_COUNT = 7569
INEQUALITY_COUNT = 10034


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


def unpack_csr(archive, name: str, dtype=None) -> sp.csr_matrix:
    matrix = sp.csr_matrix(
        (
            archive[f"{name}_data"],
            archive[f"{name}_indices"],
            archive[f"{name}_indptr"],
        ),
        shape=tuple(map(int, archive[f"{name}_shape"])),
    )
    if dtype is not None:
        matrix = matrix.astype(dtype)
    return matrix


@dataclass
class KernelAudit:
    numerical_basis: sp.csr_matrix
    maximum_h_residual: float
    maximum_orthogonality_residual: float
    minimum_qr_pivot: float
    exact_basis_nnz: int


@dataclass
class DDModel:
    plateau: object
    numerical_basis: sp.csr_matrix
    affine_nu: sp.csr_matrix
    affine_q: sp.csr_matrix
    affine_rhs: np.ndarray
    offdiagonal_coordinates: np.ndarray
    diagonal_coordinates: np.ndarray
    a_eq: sp.csr_matrix
    b_eq: np.ndarray
    a_ub: sp.csr_matrix
    b_ub: np.ndarray
    objective: np.ndarray
    bounds: list[tuple[float | None, float | None]]
    margin_column: int
    absolute_start: int
    kernel_audit: KernelAudit


def exact_kernel_gate(
    plateau,
    kernel_archive,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    exact_basis = unpack_csr(
        kernel_archive, "exact_basis", dtype=np.int64
    )
    gram_face = plateau.gram_face.astype(np.int64)
    if exact_basis.shape != (GRAM_COUNT, FACE_DIMENSION):
        raise AssertionError(
            f"wrong exact kernel shape {exact_basis.shape}"
        )
    if exact_basis.nnz != 347912:
        raise AssertionError(
            f"wrong exact kernel nnz {exact_basis.nnz}"
        )
    exact_product = gram_face @ exact_basis
    exact_product.eliminate_zeros()
    if exact_product.nnz:
        raise AssertionError("pinned exact basis does not satisfy H Z=0")
    if kernel_archive["rank_by_prime"].tolist() != [2518, 2518]:
        raise AssertionError("pinned exact basis lost certified rank")
    if kernel_archive["rank_primes"].tolist() != [1000003, 2000003]:
        raise AssertionError("unexpected exact-basis rank primes")

    q_offsets = kernel_archive["gram_offsets"].astype(np.int64)
    qdims = kernel_archive["gram_qdims"].astype(np.int64)
    face_dims = kernel_archive["gram_face_dimensions"].astype(np.int64)
    face_offsets = kernel_archive["face_column_offsets"].astype(np.int64)
    if not np.array_equal(
        q_offsets, plateau.equality_archive["gram_offsets"]
    ):
        raise AssertionError("exact basis has the wrong Gram offsets")
    if not np.array_equal(
        qdims, plateau.equality_archive["gram_qdims"]
    ):
        raise AssertionError("exact basis has the wrong Gram dimensions")
    if int(face_dims.sum()) != FACE_DIMENSION:
        raise AssertionError("wrong sum of exact block face dimensions")
    if face_offsets[0] != 0:
        raise AssertionError("first exact face-column offset is not zero")
    expected_face_offsets = np.cumsum(
        np.concatenate(([0], face_dims[:-1]))
    )
    if not np.array_equal(face_offsets, expected_face_offsets):
        raise AssertionError("exact face-column offsets are not consecutive")

    # Hash pinning plus these exact identities imports the independently gated
    # full-rank integer parameterization without trusting its embedded float
    # QR data.
    return (
        q_offsets,
        qdims,
        face_dims,
        face_offsets,
        int(exact_basis.nnz),
    )


def fresh_direct_h_kernel(
    gram_face: sp.csr_matrix,
    q_offsets: np.ndarray,
    qdims: np.ndarray,
    face_dims: np.ndarray,
) -> tuple[sp.csr_matrix, float, float, float]:
    """Return a fresh orthonormal block basis from direct QR of H_b.T."""
    blocks: list[sp.csr_matrix] = []
    row_offset = 0
    maximum_h_residual = 0.0
    maximum_orthogonality_residual = 0.0
    minimum_qr_pivot = float("inf")

    for block_index, (q_offset, qdim, face_dim) in enumerate(
        zip(q_offsets, qdims, face_dims)
    ):
        q_offset = int(q_offset)
        qdim = int(qdim)
        face_dim = int(face_dim)
        face_rank = qdim - face_dim
        block_h = gram_face[
            row_offset : row_offset + face_rank,
            q_offset : q_offset + qdim,
        ].astype(np.float64)

        if face_rank == 0:
            block_basis = np.eye(qdim)
            block_h_residual = 0.0
            block_qr_pivot = 1.0
        elif face_dim == 0:
            block_basis = np.zeros((qdim, 0), dtype=np.float64)
            block_h_residual = 0.0
            # The full-rank one-dimensional blocks have exact pivot 1.
            block_qr_pivot = 1.0
        else:
            direct_q, direct_r = la.qr(
                block_h.toarray().T,
                mode="full",
                overwrite_a=True,
                check_finite=False,
            )
            block_basis = direct_q[:, face_rank:]
            pivots = np.abs(np.diag(direct_r[:face_rank, :face_rank]))
            block_qr_pivot = float(np.min(pivots))
            block_h_residual = float(
                np.max(np.abs(block_h @ block_basis))
            )

        if block_basis.shape != (qdim, face_dim):
            raise AssertionError(
                f"block {block_index} numerical basis shape "
                f"{block_basis.shape} != {(qdim, face_dim)}"
            )
        if face_dim:
            block_orthogonality = float(
                np.max(
                    np.abs(
                        block_basis.T @ block_basis
                        - np.eye(face_dim)
                    )
                )
            )
        else:
            block_orthogonality = 0.0
        maximum_h_residual = max(
            maximum_h_residual, block_h_residual
        )
        maximum_orthogonality_residual = max(
            maximum_orthogonality_residual, block_orthogonality
        )
        minimum_qr_pivot = min(minimum_qr_pivot, block_qr_pivot)
        blocks.append(sp.csr_matrix(block_basis))
        row_offset += face_rank

    if row_offset != gram_face.shape[0]:
        raise AssertionError(
            f"consumed {row_offset} H rows, expected {gram_face.shape[0]}"
        )
    numerical_basis = sp.block_diag(blocks, format="csr")
    if numerical_basis.shape != (GRAM_COUNT, FACE_DIMENSION):
        raise AssertionError(
            f"wrong numerical basis shape {numerical_basis.shape}"
        )

    global_h_residual = float(
        np.max(np.abs(gram_face @ numerical_basis))
    )
    maximum_h_residual = max(
        maximum_h_residual, global_h_residual
    )
    if maximum_h_residual > 5e-13:
        raise AssertionError(
            f"direct-H kernel residual too large: {maximum_h_residual}"
        )
    if maximum_orthogonality_residual > 5e-13:
        raise AssertionError(
            "direct-H kernel orthogonality residual too large: "
            f"{maximum_orthogonality_residual}"
        )
    return (
        numerical_basis,
        maximum_h_residual,
        maximum_orthogonality_residual,
        minimum_qr_pivot,
    )


def quotient_dd_structure(plateau):
    """Return diagonal IDs and multiplicity-counted off-diagonal rows."""
    dd_specs: list[tuple[int, dict[int, int]]] = []
    offdiagonal_set: set[int] = set()
    offdiagonal_pairs = 0
    q_offset = 0

    for orbit, free in zip(
        plateau.base.gram_orbits, plateau.free_coordinates
    ):
        entry_ids = orbit.entry_ids
        quotient_order = len(free)
        offdiagonal_pairs += quotient_order * (quotient_order - 1) // 2
        for row_coordinate in free:
            diagonal = q_offset + int(
                entry_ids[row_coordinate, row_coordinate]
            )
            multiplicities: dict[int, int] = {}
            for column_coordinate in free:
                if row_coordinate == column_coordinate:
                    continue
                global_coordinate = q_offset + int(
                    entry_ids[row_coordinate, column_coordinate]
                )
                multiplicities[global_coordinate] = (
                    multiplicities.get(global_coordinate, 0) + 1
                )
                offdiagonal_set.add(global_coordinate)
            dd_specs.append((diagonal, multiplicities))
        q_offset += int(orbit.variable.size)

    if q_offset != GRAM_COUNT:
        raise AssertionError(f"consumed {q_offset} Gram coordinates")
    if len(dd_specs) != QUOTIENT_DIAGONAL_COUNT:
        raise AssertionError(
            f"expected {QUOTIENT_DIAGONAL_COUNT} quotient rows, "
            f"got {len(dd_specs)}"
        )
    if len(offdiagonal_set) != OFFDIAGONAL_COORDINATE_COUNT:
        raise AssertionError(
            f"expected {OFFDIAGONAL_COORDINATE_COUNT} shared "
            f"off-diagonal coordinates, got {len(offdiagonal_set)}"
        )
    if offdiagonal_pairs != OFFDIAGONAL_PAIR_COUNT:
        raise AssertionError(
            f"expected {OFFDIAGONAL_PAIR_COUNT} off-diagonal pairs, "
            f"got {offdiagonal_pairs}"
        )
    return (
        dd_specs,
        np.asarray(sorted(offdiagonal_set), dtype=np.int32),
        offdiagonal_pairs,
    )


def build_model() -> DDModel:
    hashes = {
        "plateau_source": sha256(PLATEAU_SOURCE),
        "row_data": sha256(ROW_DATA_PATH),
        "exact_kernel": sha256(KERNEL_DATA_PATH),
    }
    expected_hashes = {
        "plateau_source": EXPECTED_PLATEAU_SOURCE_SHA256,
        "row_data": EXPECTED_ROW_DATA_SHA256,
        "exact_kernel": EXPECTED_KERNEL_DATA_SHA256,
    }
    if hashes != expected_hashes:
        raise AssertionError(f"pinned SHA-256 mismatch: {hashes}")

    plateau_module = load_module(
        "codex_r10_dd_plateau_source", PLATEAU_SOURCE
    )
    plateau = plateau_module.build_model()
    row_archive = np.load(ROW_DATA_PATH, allow_pickle=False)
    kernel_archive = np.load(KERNEL_DATA_PATH, allow_pickle=False)

    (
        q_offsets,
        qdims,
        face_dims,
        _face_offsets,
        exact_basis_nnz,
    ) = exact_kernel_gate(plateau, kernel_archive)
    (
        numerical_basis,
        maximum_h_residual,
        maximum_orthogonality_residual,
        minimum_qr_pivot,
    ) = fresh_direct_h_kernel(
        plateau.gram_face,
        q_offsets,
        qdims,
        face_dims,
    )
    kernel_audit = KernelAudit(
        numerical_basis=numerical_basis,
        maximum_h_residual=maximum_h_residual,
        maximum_orthogonality_residual=(
            maximum_orthogonality_residual
        ),
        minimum_qr_pivot=minimum_qr_pivot,
        exact_basis_nnz=exact_basis_nnz,
    )

    affine_nu = unpack_csr(
        row_archive, "affine_nu", dtype=np.float64
    )
    affine_q = unpack_csr(
        row_archive, "affine_gram", dtype=np.float64
    )
    affine_rhs = np.asarray(
        row_archive["affine_rhs"], dtype=np.float64
    )
    if affine_nu.shape != (AFFINE_RANK, LIVE_COUNT):
        raise AssertionError(f"wrong affine-nu shape {affine_nu.shape}")
    if affine_q.shape != (AFFINE_RANK, GRAM_COUNT):
        raise AssertionError(f"wrong affine-q shape {affine_q.shape}")

    dd_specs, offdiagonal, _offdiagonal_pairs = (
        quotient_dd_structure(plateau)
    )
    off_to_absolute = {
        int(coordinate): index
        for index, coordinate in enumerate(offdiagonal)
    }

    margin_column = LIVE_COUNT + FACE_DIMENSION
    absolute_start = margin_column + 1
    number_absolute = len(offdiagonal)
    number_variables = absolute_start + number_absolute
    if number_variables != VARIABLE_COUNT:
        raise AssertionError(
            f"expected {VARIABLE_COUNT} variables, got {number_variables}"
        )

    affine_z = (affine_q @ numerical_basis).tocsr()
    a_eq = sp.hstack(
        [
            affine_nu,
            affine_z,
            sp.csr_matrix((AFFINE_RANK, 1 + number_absolute)),
        ],
        format="csr",
    )
    b_eq = affine_rhs.copy()

    # nu_j >= margin.
    a_nu = sp.hstack(
        [
            -sp.eye(LIVE_COUNT, format="csr"),
            sp.csr_matrix((LIVE_COUNT, FACE_DIMENSION)),
            sp.csr_matrix(np.ones((LIVE_COUNT, 1))),
            sp.csr_matrix((LIVE_COUNT, number_absolute)),
        ],
        format="csr",
    )

    # q_ii - sum_{j != i}|q_ij| >= margin.  The auxiliary
    # coefficient is the number of matrix entries in that row represented by
    # the shared invariant coordinate.
    diagonal_coordinates = np.asarray(
        [diagonal for diagonal, _ in dd_specs], dtype=np.int32
    )
    count_rows: list[int] = []
    count_columns: list[int] = []
    count_values: list[float] = []
    for row_index, (_diagonal, multiplicities) in enumerate(dd_specs):
        for coordinate, multiplicity in multiplicities.items():
            count_rows.append(row_index)
            count_columns.append(off_to_absolute[coordinate])
            count_values.append(float(multiplicity))
    multiplicity_matrix = sp.csr_matrix(
        (count_values, (count_rows, count_columns)),
        shape=(QUOTIENT_DIAGONAL_COUNT, number_absolute),
    )
    a_dd = sp.hstack(
        [
            sp.csr_matrix(
                (QUOTIENT_DIAGONAL_COUNT, LIVE_COUNT)
            ),
            -numerical_basis[diagonal_coordinates, :],
            sp.csr_matrix(
                np.ones((QUOTIENT_DIAGONAL_COUNT, 1))
            ),
            multiplicity_matrix,
        ],
        format="csr",
    )

    # shared_absolute_g >= +/- q_g.
    offdiagonal_map = numerical_basis[offdiagonal, :]
    zero_nu = sp.csr_matrix(
        (number_absolute, LIVE_COUNT)
    )
    zero_margin = sp.csr_matrix((number_absolute, 1))
    minus_identity = -sp.eye(number_absolute, format="csr")
    a_absolute_positive = sp.hstack(
        [zero_nu, offdiagonal_map, zero_margin, minus_identity],
        format="csr",
    )
    a_absolute_negative = sp.hstack(
        [zero_nu, -offdiagonal_map, zero_margin, minus_identity],
        format="csr",
    )

    a_ub = sp.vstack(
        [a_nu, a_dd, a_absolute_positive, a_absolute_negative],
        format="csr",
    )
    b_ub = np.zeros(a_ub.shape[0], dtype=np.float64)
    if a_eq.shape != (AFFINE_RANK, VARIABLE_COUNT):
        raise AssertionError(f"wrong equality shape {a_eq.shape}")
    if a_ub.shape != (INEQUALITY_COUNT, VARIABLE_COUNT):
        raise AssertionError(f"wrong inequality shape {a_ub.shape}")

    objective = np.zeros(VARIABLE_COUNT, dtype=np.float64)
    objective[margin_column] = -1.0
    # Every variable is formally free.  The two absolute-value inequalities
    # imply each shared auxiliary is nonnegative.  No explicit margin>=0 row
    # is included; the optimized margin itself decides strict feasibility.
    bounds = [(None, None)] * VARIABLE_COUNT

    projected_affine = sp.hstack(
        [affine_nu, affine_z], format="csr"
    )
    singular_values = np.linalg.svd(
        projected_affine.toarray(), compute_uv=False
    )
    if singular_values[-1] <= 0:
        raise AssertionError("projected affine map lost row rank")

    print(
        "DD_LP_BUILD graph=Gamma_11 c=25 d=2 cuts=56 "
        f"nu={LIVE_COUNT} z={FACE_DIMENSION} margin=1 "
        f"shared_abs={number_absolute} variables={VARIABLE_COUNT}"
    )
    print(
        "DD_LP_EXACT_KERNEL "
        f"shape={(GRAM_COUNT, FACE_DIMENSION)} "
        f"nnz={exact_basis_nnz} HZ=exact_zero rank={FACE_DIMENSION}"
    )
    print(
        "DD_LP_NUMERIC_KERNEL "
        f"shape={numerical_basis.shape} nnz={numerical_basis.nnz} "
        f"H_residual_inf={maximum_h_residual:.12e} "
        "orthogonality_residual_inf="
        f"{maximum_orthogonality_residual:.12e} "
        f"minimum_qr_pivot={minimum_qr_pivot:.12e}"
    )
    print(
        "DD_LP_PROJECTED_AFFINE "
        f"shape={projected_affine.shape} nnz={projected_affine.nnz} "
        f"sigma_max={singular_values[0]:.12e} "
        f"sigma_min={singular_values[-1]:.12e} "
        f"condition_2={singular_values[0] / singular_values[-1]:.12e}"
    )
    print(
        "DD_LP_GERSHGORIN "
        f"diagonal_rows={len(dd_specs)} "
        f"offdiagonal_pairs={OFFDIAGONAL_PAIR_COUNT} "
        f"shared_coordinates={number_absolute} "
        "multiplicity_counted=true"
    )
    print(
        "DD_LP_CANONICAL "
        f"equalities={a_eq.shape[0]} inequalities={a_ub.shape[0]} "
        f"rows={a_eq.shape[0] + a_ub.shape[0]} "
        f"variables={a_eq.shape[1]} "
        f"equality_nnz={a_eq.nnz} inequality_nnz={a_ub.nnz} "
        f"total_nnz={a_eq.nnz + a_ub.nnz}"
    )
    print(
        "DD_LP_HASHES "
        f"plateau_source={hashes['plateau_source']} "
        f"row_data={hashes['row_data']} "
        f"exact_kernel={hashes['exact_kernel']}"
    )

    return DDModel(
        plateau=plateau,
        numerical_basis=numerical_basis,
        affine_nu=affine_nu,
        affine_q=affine_q,
        affine_rhs=affine_rhs,
        offdiagonal_coordinates=offdiagonal,
        diagonal_coordinates=diagonal_coordinates,
        a_eq=a_eq,
        b_eq=b_eq,
        a_ub=a_ub,
        b_ub=b_ub,
        objective=objective,
        bounds=bounds,
        margin_column=margin_column,
        absolute_start=absolute_start,
        kernel_audit=kernel_audit,
    )


def solve_model(model: DDModel, method: str):
    # Imported here so the default build-only path has no solver call.
    from scipy.optimize import linprog

    print(
        f"DD_LP_SOLVE_START method={method} "
        "scope=numerical_steering_only"
    )
    result = linprog(
        model.objective,
        A_ub=model.a_ub,
        b_ub=model.b_ub,
        A_eq=model.a_eq,
        b_eq=model.b_eq,
        bounds=model.bounds,
        method=method,
        options={
            "presolve": True,
            "dual_feasibility_tolerance": 1e-9,
            "primal_feasibility_tolerance": 1e-9,
            "ipm_optimality_tolerance": 1e-10,
            "time_limit": 1800,
            "disp": True,
        },
    )
    print(
        f"DD_LP_SOLVE_DONE status={result.status} "
        f"message={result.message!r}"
    )
    if result.x is None:
        return result, None

    vector = np.asarray(result.x, dtype=np.float64)
    nu = vector[:LIVE_COUNT]
    z = vector[LIVE_COUNT : LIVE_COUNT + FACE_DIMENSION]
    q = np.asarray(model.numerical_basis @ z).reshape(-1)
    margin = float(vector[model.margin_column])
    equality_residual = float(
        np.max(np.abs(model.a_eq @ vector - model.b_eq))
    )
    inequality_residual = float(
        np.max(model.a_ub @ vector - model.b_ub)
    )
    original_h_residual = float(
        np.max(np.abs(model.plateau.gram_face @ q))
    )
    original_affine_residual = float(
        np.max(
            np.abs(
                model.affine_nu @ nu
                + model.affine_q @ q
                - model.affine_rhs
            )
        )
    )
    minimum_eigenvalue = float("inf")
    q_offset = 0
    for orbit, free in zip(
        model.plateau.base.gram_orbits,
        model.plateau.free_coordinates,
    ):
        local_q = q[q_offset : q_offset + int(orbit.variable.size)]
        if free:
            principal = local_q[
                orbit.entry_ids[np.ix_(free, free)]
            ]
            minimum_eigenvalue = min(
                minimum_eigenvalue,
                float(np.linalg.eigvalsh(principal)[0]),
            )
        q_offset += int(orbit.variable.size)
    diagnostics = {
        "margin": margin,
        "minimum_live_nu": float(np.min(nu)),
        "minimum_quotient_eigenvalue": minimum_eigenvalue,
        "equality_residual_inf": equality_residual,
        "inequality_residual_max": inequality_residual,
        "original_H_residual_inf": original_h_residual,
        "original_affine_residual_inf": original_affine_residual,
    }
    print(
        "DD_LP_DIAGNOSTICS "
        + " ".join(f"{key}={value:.12e}" for key, value in diagnostics.items())
    )
    return result, (vector, q, diagnostics)


def export_solution(
    output: Path,
    result,
    payload,
    model: DDModel,
) -> None:
    if output.suffix.lower() != ".npz":
        raise ValueError("--output must have suffix .npz")
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    if payload is None:
        raise RuntimeError("solver returned no vector to export")
    vector, q, diagnostics = payload
    np.savez_compressed(
        output,
        solver_status=np.asarray([str(result.message)]),
        objective_value=np.asarray([float(result.fun)]),
        variables=vector,
        live_multiplier_values=vector[:LIVE_COUNT],
        numerical_kernel_coordinates=vector[
            LIVE_COUNT : LIVE_COUNT + FACE_DIMENSION
        ],
        gram_orbit_values=q,
        shared_absolute_values=vector[model.absolute_start :],
        margin=np.asarray([diagnostics["margin"]]),
        equality_residual_inf=np.asarray(
            [diagnostics["equality_residual_inf"]]
        ),
        original_H_residual_inf=np.asarray(
            [diagnostics["original_H_residual_inf"]]
        ),
        original_affine_residual_inf=np.asarray(
            [diagnostics["original_affine_residual_inf"]]
        ),
        minimum_live_nu=np.asarray(
            [diagnostics["minimum_live_nu"]]
        ),
        minimum_quotient_eigenvalue=np.asarray(
            [diagnostics["minimum_quotient_eigenvalue"]]
        ),
        plateau_source_sha256=np.asarray(
            [EXPECTED_PLATEAU_SOURCE_SHA256]
        ),
        row_data_sha256=np.asarray([EXPECTED_ROW_DATA_SHA256]),
        exact_kernel_data_sha256=np.asarray(
            [EXPECTED_KERNEL_DATA_SHA256]
        ),
    )
    print(f"DD_LP_EXPORT path={output}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--solve",
        action="store_true",
        help="explicitly launch the numerical LP; default is build-only",
    )
    parser.add_argument(
        "--method",
        default="highs-ipm",
        choices=("highs-ipm", "highs-ds"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="optional .npz export; requires --solve and refuses overwrite",
    )
    args = parser.parse_args()
    if args.output is not None and not args.solve:
        parser.error("--output requires explicit --solve")

    model = build_model()
    if not args.solve:
        print(
            "DD_LP_BUILD_ONLY no_solver_launched=true "
            "no_file_written=true"
        )
        return 0

    result, payload = solve_model(model, args.method)
    if args.output is not None:
        export_solution(args.output, result, payload, model)
    return 0 if result.status == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
