"""Build and audit a diagonally-dominant LP on the Gamma_11 plateau face.

This file is deliberately build-only: it has no optimization call and no
output-writing path.  It constructs a sufficient inner approximation to the
quotient PSD constraints from ``CODEX_R10_g11_d22_plateau_face.py``.

The exact integer artifact proves that the Gram-face kernel has dimension
2,518 and gives the target for any later rational reconstruction.  A separate
sealed float64 artifact supplies numerical coordinates for that same kernel.
The float artifact is loaded byte-for-byte; it is never treated as exact
evidence and is neither recomputed nor pruned here.

For each quotient principal matrix R and each of its rows, the LP imposes

    R_ii - sum_{j != i} u_id(i,j) >= margin,
    u_e >= R_ij,  u_e >= -R_ij.

There is one shared auxiliary u_e per distinct block-local invariant
off-diagonal coordinate, with its row multiplicity counted explicitly.
Consequently a feasible point with positive margin makes every R strictly
diagonally dominant with positive diagonal, hence positive definite by
Gershgorin.  Together with positive live multipliers, exact affine replay
would therefore give a strict-interior point of the fixed plateau face.
Failure or a nonpositive optimum would exclude only this sufficient
diagonally-dominant subcone, not the full PSD cone.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
from pathlib import Path
import sys

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
PLATEAU_SOURCE = HERE / "CODEX_R10_g11_d22_plateau_face.py"
ROW_DATA_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
EXACT_KERNEL_DATA_PATH = (
    HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
)
NUMERICAL_KERNEL_DATA_PATH = (
    HERE / "CODEX_R10_c5_FACE_NUMERICAL_KERNEL_data.npz"
)

EXPECTED_SHA256 = {
    "plateau_source": (
        "110579CCFA3372BFEB377B857271F509CAC1D771C2E95627E0880FD026D3678A"
    ),
    "row_data": (
        "F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C"
    ),
    "exact_kernel": (
        "EA9BE7AEC38FCF14470FEC1D36210FB25C4AAEFF9CE7A49C1B171CE42C02E34C"
    ),
    "numerical_kernel": (
        "CBD479AF7071FC95ABF02AB2193738C75359E39672F1421E0C7D1B2FCFB199D3"
    ),
}
EXPECTED_NUMERICAL_PROVENANCE = {
    "blowup_data_sha256": (
        "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730"
    ),
    "equality_data_sha256": (
        "08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F"
    ),
    "exact_data_sha256": EXPECTED_SHA256["exact_kernel"],
}

LIVE_COUNT = 526
GRAM_COUNT = 8647
FACE_DIMENSION = 2518
AFFINE_RANK = 388
QUOTIENT_DIAGONAL_COUNT = 460
OFFDIAGONAL_COORDINATE_COUNT = 4524
OFFDIAGONAL_PAIR_COUNT = 14994
OFFDIAGONAL_INCIDENCE_COUNT = 29988
NUMERICAL_BASIS_NNZ = 2925200
VARIABLE_COUNT = 7569
INEQUALITY_COUNT = 10034
EQUALITY_NNZ = 629539
INEQUALITY_NNZ = 3856067
CANONICAL_NNZ = 4485606


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


def unpack_csr(archive, name: str, dtype) -> sp.csr_matrix:
    matrix = sp.csr_matrix(
        (
            archive[f"{name}_data"],
            archive[f"{name}_indices"],
            archive[f"{name}_indptr"],
        ),
        shape=tuple(map(int, archive[f"{name}_shape"])),
    )
    return matrix.astype(dtype, copy=False)


@dataclass
class KernelAudit:
    exact_basis_nnz: int
    numerical_basis_nnz: int
    maximum_h_residual: float
    maximum_orthogonality_residual: float
    maximum_block_h_residual: float
    maximum_block_orthogonality_residual: float


@dataclass
class DDModel:
    plateau: object
    numerical_basis: sp.csr_matrix
    affine_nu: sp.csr_matrix
    affine_q: sp.csr_matrix
    affine_rhs: np.ndarray
    offdiagonal_coordinates: np.ndarray
    diagonal_coordinates: np.ndarray
    multiplicity_matrix: sp.csr_matrix
    a_eq: sp.csr_matrix
    b_eq: np.ndarray
    a_ub: sp.csr_matrix
    b_ub: np.ndarray
    objective: np.ndarray
    bounds: list[tuple[float | None, float | None]]
    margin_column: int
    absolute_start: int
    kernel_audit: KernelAudit
    hashes: dict[str, str]


def exact_kernel_gate(
    plateau,
    exact_archive,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    """Import the sealed exact face dimension/order claim and replay HZ=0."""
    exact_basis = unpack_csr(exact_archive, "exact_basis", np.int64)
    gram_face = plateau.gram_face.astype(np.int64)
    if exact_basis.shape != (GRAM_COUNT, FACE_DIMENSION):
        raise AssertionError(f"wrong exact kernel shape {exact_basis.shape}")
    if exact_basis.nnz != 347912:
        raise AssertionError(f"wrong exact kernel nnz {exact_basis.nnz}")
    if not exact_basis.has_canonical_format:
        raise AssertionError("exact kernel CSR is not canonical")

    # This deliberately crude bound dominates every integer dot product in
    # HZ and proves that the int64 replay below cannot overflow.
    int64_bound = (
        int(gram_face.nnz)
        * int(np.max(np.abs(gram_face.data)))
        * int(np.max(np.abs(exact_basis.data)))
    )
    if int64_bound >= np.iinfo(np.int64).max:
        raise AssertionError(f"unsafe exact HZ int64 bound {int64_bound}")
    exact_product = gram_face @ exact_basis
    exact_product.eliminate_zeros()
    if exact_product.nnz:
        raise AssertionError("pinned exact basis does not satisfy H Z=0")
    if exact_archive["rank_primes"].tolist() != [1000003, 2000003]:
        raise AssertionError("unexpected exact-basis rank primes")
    if exact_archive["rank_by_prime"].tolist() != [
        FACE_DIMENSION,
        FACE_DIMENSION,
    ]:
        raise AssertionError("pinned exact basis lost certified rank")

    q_offsets = exact_archive["gram_offsets"].astype(np.int64)
    qdims = exact_archive["gram_qdims"].astype(np.int64)
    face_ranks = qdims - exact_archive[
        "gram_face_dimensions"
    ].astype(np.int64)
    face_dims = exact_archive["gram_face_dimensions"].astype(np.int64)
    face_offsets = exact_archive["face_column_offsets"].astype(np.int64)
    if not np.array_equal(
        q_offsets, plateau.equality_archive["gram_offsets"]
    ):
        raise AssertionError("exact basis has wrong Gram offsets")
    if not np.array_equal(
        qdims, plateau.equality_archive["gram_qdims"]
    ):
        raise AssertionError("exact basis has wrong Gram dimensions")
    if int(face_ranks.sum()) != gram_face.shape[0]:
        raise AssertionError("exact block ranks do not consume H rows")
    if int(face_dims.sum()) != FACE_DIMENSION:
        raise AssertionError("wrong sum of exact block face dimensions")
    expected_face_offsets = np.cumsum(
        np.concatenate(([0], face_dims[:-1]))
    )
    if not np.array_equal(face_offsets, expected_face_offsets):
        raise AssertionError("exact face-column offsets are not consecutive")
    return (
        q_offsets,
        qdims,
        face_ranks,
        face_dims,
        face_offsets,
        int(exact_basis.nnz),
    )


def sealed_numerical_kernel(
    plateau,
    numerical_archive,
    q_offsets: np.ndarray,
    qdims: np.ndarray,
    face_ranks: np.ndarray,
    face_dims: np.ndarray,
    face_offsets: np.ndarray,
) -> tuple[sp.csr_matrix, tuple[float, float, float, float]]:
    """Load the pinned numerical basis unchanged and independently gate it."""
    if numerical_archive["format_version"].tolist() != [1]:
        raise AssertionError("unexpected numerical-kernel format")
    if numerical_archive["role"].tolist() != [
        "numerical-only direct-H QR; never an exact certificate"
    ]:
        raise AssertionError("unexpected numerical-kernel role")
    for key, expected in EXPECTED_NUMERICAL_PROVENANCE.items():
        if numerical_archive[key].tolist() != [expected]:
            raise AssertionError(f"numerical-kernel provenance mismatch: {key}")

    metadata = {
        "gram_offsets": q_offsets,
        "gram_qdims": qdims,
        "gram_constraint_ranks": face_ranks,
        "gram_face_dimensions": face_dims,
        "face_column_offsets": face_offsets,
    }
    for key, expected in metadata.items():
        if not np.array_equal(numerical_archive[key], expected):
            raise AssertionError(f"numerical-kernel ordering mismatch: {key}")

    basis = unpack_csr(
        numerical_archive, "numerical_basis", np.float64
    )
    if basis.shape != (GRAM_COUNT, FACE_DIMENSION):
        raise AssertionError(f"wrong numerical basis shape {basis.shape}")
    if basis.nnz != NUMERICAL_BASIS_NNZ:
        raise AssertionError(f"wrong numerical basis nnz {basis.nnz}")
    if not basis.has_canonical_format or not basis.has_sorted_indices:
        raise AssertionError("numerical basis CSR is not canonical and sorted")
    if not np.all(np.isfinite(basis.data)):
        raise AssertionError("numerical basis contains a nonfinite value")
    if np.any(basis.data == 0.0):
        raise AssertionError("numerical basis contains an explicit zero")
    # The constructor must preserve every stored value and index byte-for-byte.
    if not np.array_equal(
        basis.data, numerical_archive["numerical_basis_data"]
    ):
        raise AssertionError("numerical basis data changed while loading")
    if not np.array_equal(
        basis.indices, numerical_archive["numerical_basis_indices"]
    ):
        raise AssertionError("numerical basis indices changed while loading")
    if not np.array_equal(
        basis.indptr, numerical_archive["numerical_basis_indptr"]
    ):
        raise AssertionError("numerical basis indptr changed while loading")

    q_ends = q_offsets + qdims
    face_ends = face_offsets + face_dims
    coo = basis.tocoo(copy=False)
    row_blocks = np.searchsorted(q_ends, coo.row, side="right")
    column_blocks = np.searchsorted(face_ends, coo.col, side="right")
    if not np.array_equal(row_blocks, column_blocks):
        raise AssertionError("numerical basis has off-block support")

    h = plateau.gram_face.astype(np.float64)
    residual = (h @ basis).tocsr()
    global_h_residual = (
        float(np.max(np.abs(residual.data))) if residual.nnz else 0.0
    )
    gram_error = (
        basis.T @ basis - sp.eye(FACE_DIMENSION, format="csr")
    ).tocsr()
    global_orthogonality = (
        float(np.max(np.abs(gram_error.data)))
        if gram_error.nnz
        else 0.0
    )

    h_row_offset = 0
    maximum_block_h_residual = 0.0
    maximum_block_orthogonality = 0.0
    for block in range(len(q_offsets)):
        q0 = int(q_offsets[block])
        q1 = q0 + int(qdims[block])
        f0 = int(face_offsets[block])
        f1 = f0 + int(face_dims[block])
        r0 = h_row_offset
        r1 = r0 + int(face_ranks[block])
        block_basis = basis[q0:q1, f0:f1]
        block_h = h[r0:r1, q0:q1]
        block_residual = (block_h @ block_basis).tocsr()
        block_h_residual = (
            float(np.max(np.abs(block_residual.data)))
            if block_residual.nnz
            else 0.0
        )
        block_gram_error = (
            block_basis.T @ block_basis
            - sp.eye(int(face_dims[block]), format="csr")
        ).tocsr()
        block_orthogonality = (
            float(np.max(np.abs(block_gram_error.data)))
            if block_gram_error.nnz
            else 0.0
        )
        maximum_block_h_residual = max(
            maximum_block_h_residual, block_h_residual
        )
        maximum_block_orthogonality = max(
            maximum_block_orthogonality, block_orthogonality
        )
        h_row_offset = r1
    if h_row_offset != h.shape[0]:
        raise AssertionError("numerical block rows do not consume H")
    if global_h_residual > 1e-12 or maximum_block_h_residual > 1e-12:
        raise AssertionError("sealed numerical basis fails H residual gate")
    if (
        global_orthogonality > 1e-12
        or maximum_block_orthogonality > 1e-12
    ):
        raise AssertionError(
            "sealed numerical basis fails orthogonality gate"
        )
    return basis, (
        global_h_residual,
        global_orthogonality,
        maximum_block_h_residual,
        maximum_block_orthogonality,
    )


def quotient_dd_structure(plateau):
    """Build direct quotient-row incidence data, including multiplicities."""
    dd_specs: list[tuple[int, dict[int, int]]] = []
    diagonal_set: set[int] = set()
    offdiagonal_set: set[int] = set()
    offdiagonal_pairs = 0
    offdiagonal_incidences = 0
    q_offset = 0

    for block, (orbit, free) in enumerate(
        zip(plateau.base.gram_orbits, plateau.free_coordinates)
    ):
        entry_ids = np.asarray(orbit.entry_ids)
        if not np.array_equal(entry_ids, entry_ids.T):
            raise AssertionError(f"block {block} entry IDs are not symmetric")
        free = list(map(int, free))
        quotient_order = len(free)
        offdiagonal_pairs += quotient_order * (quotient_order - 1) // 2
        for row_coordinate in free:
            diagonal = q_offset + int(
                entry_ids[row_coordinate, row_coordinate]
            )
            diagonal_set.add(diagonal)
            multiplicities: dict[int, int] = {}
            for column_coordinate in free:
                if row_coordinate == column_coordinate:
                    continue
                coordinate = q_offset + int(
                    entry_ids[row_coordinate, column_coordinate]
                )
                multiplicities[coordinate] = (
                    multiplicities.get(coordinate, 0) + 1
                )
                offdiagonal_set.add(coordinate)
                offdiagonal_incidences += 1
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
    if offdiagonal_incidences != OFFDIAGONAL_INCIDENCE_COUNT:
        raise AssertionError(
            f"expected {OFFDIAGONAL_INCIDENCE_COUNT} incidences, "
            f"got {offdiagonal_incidences}"
        )
    if offdiagonal_incidences != 2 * offdiagonal_pairs:
        raise AssertionError("ordered/unordered off-diagonal count mismatch")
    if diagonal_set & offdiagonal_set:
        raise AssertionError(
            "a quotient coordinate occurs both diagonally and off-diagonally"
        )
    return (
        dd_specs,
        np.asarray(sorted(offdiagonal_set), dtype=np.int32),
        offdiagonal_pairs,
        offdiagonal_incidences,
    )


def build_model() -> DDModel:
    paths = {
        "plateau_source": PLATEAU_SOURCE,
        "row_data": ROW_DATA_PATH,
        "exact_kernel": EXACT_KERNEL_DATA_PATH,
        "numerical_kernel": NUMERICAL_KERNEL_DATA_PATH,
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_SHA256:
        raise AssertionError(f"pinned SHA-256 mismatch: {hashes}")

    plateau_module = load_module(
        "codex_r10_dd_plateau_source_v2", PLATEAU_SOURCE
    )
    plateau = plateau_module.build_model()
    with (
        np.load(ROW_DATA_PATH, allow_pickle=False) as row_archive,
        np.load(EXACT_KERNEL_DATA_PATH, allow_pickle=False) as exact_archive,
        np.load(
            NUMERICAL_KERNEL_DATA_PATH, allow_pickle=False
        ) as numerical_archive,
    ):
        (
            q_offsets,
            qdims,
            face_ranks,
            face_dims,
            face_offsets,
            exact_basis_nnz,
        ) = exact_kernel_gate(plateau, exact_archive)
        numerical_basis, residuals = sealed_numerical_kernel(
            plateau,
            numerical_archive,
            q_offsets,
            qdims,
            face_ranks,
            face_dims,
            face_offsets,
        )
        affine_nu = unpack_csr(
            row_archive, "affine_nu", np.float64
        ).copy()
        affine_q = unpack_csr(
            row_archive, "affine_gram", np.float64
        ).copy()
        affine_rhs = np.asarray(
            row_archive["affine_rhs"], dtype=np.float64
        ).copy()

    kernel_audit = KernelAudit(
        exact_basis_nnz=exact_basis_nnz,
        numerical_basis_nnz=int(numerical_basis.nnz),
        maximum_h_residual=residuals[0],
        maximum_orthogonality_residual=residuals[1],
        maximum_block_h_residual=residuals[2],
        maximum_block_orthogonality_residual=residuals[3],
    )
    if affine_nu.shape != (AFFINE_RANK, LIVE_COUNT):
        raise AssertionError(f"wrong affine-nu shape {affine_nu.shape}")
    if affine_q.shape != (AFFINE_RANK, GRAM_COUNT):
        raise AssertionError(f"wrong affine-q shape {affine_q.shape}")
    if affine_rhs.shape != (AFFINE_RANK,):
        raise AssertionError(f"wrong affine RHS shape {affine_rhs.shape}")

    (
        dd_specs,
        offdiagonal,
        offdiagonal_pairs,
        offdiagonal_incidences,
    ) = quotient_dd_structure(plateau)
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

    # nu_j >= margin, represented in A_ub x <= 0 form.
    a_nu = sp.hstack(
        [
            -sp.eye(LIVE_COUNT, format="csr"),
            sp.csr_matrix((LIVE_COUNT, FACE_DIMENSION)),
            sp.csr_matrix(np.ones((LIVE_COUNT, 1))),
            sp.csr_matrix((LIVE_COUNT, number_absolute)),
        ],
        format="csr",
    )

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
    if int(multiplicity_matrix.sum()) != OFFDIAGONAL_INCIDENCE_COUNT:
        raise AssertionError("multiplicity matrix lost quotient incidences")
    a_dd = sp.hstack(
        [
            sp.csr_matrix((QUOTIENT_DIAGONAL_COUNT, LIVE_COUNT)),
            -numerical_basis[diagonal_coordinates, :],
            sp.csr_matrix(np.ones((QUOTIENT_DIAGONAL_COUNT, 1))),
            multiplicity_matrix,
        ],
        format="csr",
    )

    # u_e >= +/-q_e, with one shared u_e for each global block-local ID.
    offdiagonal_map = numerical_basis[offdiagonal, :]
    zero_nu = sp.csr_matrix((number_absolute, LIVE_COUNT))
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
    b_ub = np.zeros(INEQUALITY_COUNT, dtype=np.float64)
    if a_eq.shape != (AFFINE_RANK, VARIABLE_COUNT):
        raise AssertionError(f"wrong equality shape {a_eq.shape}")
    if a_ub.shape != (INEQUALITY_COUNT, VARIABLE_COUNT):
        raise AssertionError(f"wrong inequality shape {a_ub.shape}")
    if a_eq.nnz != EQUALITY_NNZ:
        raise AssertionError(f"wrong equality nnz {a_eq.nnz}")
    if a_ub.nnz != INEQUALITY_NNZ:
        raise AssertionError(f"wrong inequality nnz {a_ub.nnz}")

    objective = np.zeros(VARIABLE_COUNT, dtype=np.float64)
    objective[margin_column] = -1.0
    # All variables are formally free.  The paired inequalities imply u>=0.
    # There is intentionally no t>=0 row: a later optimum's sign is the test.
    bounds = [(None, None)] * VARIABLE_COUNT

    canonical = sp.vstack([a_eq, a_ub], format="csr")
    if canonical.nnz != CANONICAL_NNZ:
        raise AssertionError(f"wrong canonical nnz {canonical.nnz}")
    if not np.all(np.isfinite(canonical.data)):
        raise AssertionError("canonical LP contains a nonfinite coefficient")
    if np.any(canonical.data == 0.0):
        raise AssertionError("canonical LP contains an explicit zero")
    if np.any(np.diff(canonical.indptr) == 0):
        raise AssertionError("canonical LP has a zero row")
    canonical_csc = canonical.tocsc()
    if np.any(np.diff(canonical_csc.indptr) == 0):
        raise AssertionError("canonical LP has a zero column")

    projected_affine = sp.hstack(
        [affine_nu, affine_z], format="csr"
    )
    singular_values = np.linalg.svd(
        projected_affine.toarray(), compute_uv=False
    )
    if singular_values[-1] <= 0.0:
        raise AssertionError("projected affine map lost row rank")

    # Deterministic algebra replay of all DD rows against direct q=Gz values.
    z_probe = np.sin(np.arange(FACE_DIMENSION, dtype=np.float64) + 1.0)
    u_probe = (
        np.cos(np.arange(number_absolute, dtype=np.float64) + 1.0)
        + 2.0
    )
    margin_probe = 0.125
    q_probe = np.asarray(numerical_basis @ z_probe).reshape(-1)
    reduced_probe = np.concatenate(
        [
            np.zeros(LIVE_COUNT),
            z_probe,
            np.asarray([margin_probe]),
            u_probe,
        ]
    )
    observed_dd = np.asarray(a_dd @ reduced_probe).reshape(-1)
    expected_dd = np.empty(QUOTIENT_DIAGONAL_COUNT, dtype=np.float64)
    for row_index, (diagonal, multiplicities) in enumerate(dd_specs):
        radius = sum(
            multiplicity * u_probe[off_to_absolute[coordinate]]
            for coordinate, multiplicity in multiplicities.items()
        )
        expected_dd[row_index] = -q_probe[diagonal] + margin_probe + radius
    dd_replay_residual = float(
        np.max(np.abs(observed_dd - expected_dd))
    )
    if dd_replay_residual > 1e-11:
        raise AssertionError(
            f"DD algebra replay residual {dd_replay_residual}"
        )

    coefficient_abs = np.abs(canonical.data)
    print(
        "DD_LP_BUILD_V2 graph=Gamma_11 c=25 d=2 cuts=56 "
        f"nu={LIVE_COUNT} z={FACE_DIMENSION} margin=1 "
        f"shared_abs={number_absolute} variables={VARIABLE_COUNT}"
    )
    print(
        "DD_LP_EXACT_KERNEL "
        f"shape={(GRAM_COUNT, FACE_DIMENSION)} nnz={exact_basis_nnz} "
        f"HZ=exact_zero rank={FACE_DIMENSION}"
    )
    print(
        "DD_LP_SEALED_NUMERIC_KERNEL "
        f"shape={numerical_basis.shape} nnz={numerical_basis.nnz} "
        f"H_residual_inf={residuals[0]:.12e} "
        f"orthogonality_residual_inf={residuals[1]:.12e} "
        f"block_H_residual_inf={residuals[2]:.12e} "
        f"block_orthogonality_residual_inf={residuals[3]:.12e} "
        "loaded_byte_for_byte=true"
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
        f"offdiagonal_pairs={offdiagonal_pairs} "
        f"offdiagonal_incidences={offdiagonal_incidences} "
        f"shared_coordinates={number_absolute} "
        f"algebra_replay_residual={dd_replay_residual:.12e}"
    )
    print(
        "DD_LP_CANONICAL "
        f"equalities={a_eq.shape[0]} inequalities={a_ub.shape[0]} "
        f"rows={canonical.shape[0]} variables={canonical.shape[1]} "
        f"equality_nnz={a_eq.nnz} inequality_nnz={a_ub.nnz} "
        f"total_nnz={canonical.nnz} zero_rows=0 zero_columns=0 "
        f"coefficient_min_abs={coefficient_abs.min():.12e} "
        f"coefficient_max_abs={coefficient_abs.max():.12e} "
        "cones=Zero(388),Nonnegative(10034),PSD()"
    )
    print(
        "DD_LP_HASHES "
        + " ".join(f"{key}={value}" for key, value in hashes.items())
    )
    print(
        "DD_LP_BUILD_ONLY no_solver_available=true "
        "no_solver_launched=true no_file_written=true"
    )

    return DDModel(
        plateau=plateau,
        numerical_basis=numerical_basis,
        affine_nu=affine_nu,
        affine_q=affine_q,
        affine_rhs=affine_rhs,
        offdiagonal_coordinates=offdiagonal,
        diagonal_coordinates=diagonal_coordinates,
        multiplicity_matrix=multiplicity_matrix,
        a_eq=a_eq,
        b_eq=b_eq,
        a_ub=a_ub,
        b_ub=b_ub,
        objective=objective,
        bounds=bounds,
        margin_column=margin_column,
        absolute_start=absolute_start,
        kernel_audit=kernel_audit,
        hashes=hashes,
    )


def main() -> int:
    build_model()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
