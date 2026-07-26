"""Exact modular dimension of block 0 after the rank-22 exposure.

The sealed first-face block is parameterized by 582 exact invariant
coordinates.  The rank-22 exposure forces its order-154 quotient matrix R to
annihilate the exposure range.  This script constructs those linear equations
exactly and measures their rank over fresh prime fields.

No solver is called, and no nonemptiness claim is made.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
CANONICAL_PATH = HERE / "CODEX_R10_c5_FACE_REDUCED_SDP_CANONICALIZE.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
EXACT_Z_PATH = HERE / "CODEX_R10_c5_FACE_KERNEL_PARAMETERIZATION_data.npz"
EXPOSURE_PATH = (
    HERE / "CODEX_R10_SECOND_FACE_BLOCK0_RANK22_EXACT_data.npz"
)
PRIMES = (1_000_133, 1_000_151, 1_000_153)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def unpack_csr(archive, name: str) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive[f"{name}_data"].astype(np.int64),
            archive[f"{name}_indices"].astype(np.int32),
            archive[f"{name}_indptr"].astype(np.int64),
        ),
        shape=tuple(map(int, archive[f"{name}_shape"])),
        dtype=np.int64,
    )


def modular_row_rank(matrix: sp.csr_matrix, prime: int) -> int:
    pivots: dict[int, dict[int, int]] = {}
    matrix = matrix.tocsr()
    for row_index in range(matrix.shape[0]):
        start = int(matrix.indptr[row_index])
        stop = int(matrix.indptr[row_index + 1])
        row = {
            int(column): int(value) % prime
            for column, value in zip(
                matrix.indices[start:stop], matrix.data[start:stop]
            )
            if int(value) % prime
        }
        while row:
            pivot = min(row)
            base = pivots.get(pivot)
            if base is None:
                inverse = pow(row[pivot], -1, prime)
                pivots[pivot] = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value * inverse % prime
                }
                break
            factor = row[pivot]
            for column, value in base.items():
                updated = (row.get(column, 0) - factor * value) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
    return len(pivots)


def reduced_product_mod(
    left: sp.csr_matrix, right: sp.csr_matrix, prime: int
) -> sp.csr_matrix:
    left_mod = left.copy()
    right_mod = right.copy()
    left_mod.data %= prime
    right_mod.data %= prime
    product = (left_mod @ right_mod).tocsr()
    product.data %= prime
    product.eliminate_zeros()
    return product


def main() -> None:
    builder = load_module("codex_r10_face2_dim_base", BASE_PATH)
    canonical = load_module("codex_r10_face2_dim_canonical", CANONICAL_PATH)
    model = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    exact = np.load(EXACT_Z_PATH, allow_pickle=False)
    exposure = np.load(EXPOSURE_PATH, allow_pickle=False)
    exact_z = unpack_csr(exact, "exact_basis")
    block_z = exact_z[:1946, :582].tocsr()
    free = canonical.free_coordinates(blowup, model)[0]
    ids = model.gram_orbits[0].entry_ids[
        np.ix_(free, free)
    ].astype(np.int64)

    center = exposure["center_matrix"].astype(np.int64)
    pivots = exposure["pivot_columns"].astype(int)
    range_rows = center[pivots, :]
    if range_rows.shape != (22, 154):
        raise AssertionError(range_rows.shape)

    output_rows = []
    output_columns = []
    output_values = []
    for matrix_row in range(154):
        orbit_ids = ids[matrix_row]
        for range_row in range(22):
            coefficients = np.zeros(1946, dtype=np.int64)
            np.add.at(
                coefficients,
                orbit_ids,
                range_rows[range_row],
            )
            nonzero = np.flatnonzero(coefficients)
            row_index = matrix_row * 22 + range_row
            output_rows.extend([row_index] * len(nonzero))
            output_columns.extend(nonzero.tolist())
            output_values.extend(coefficients[nonzero].tolist())
    annihilation_q = sp.csr_matrix(
        (output_values, (output_rows, output_columns)),
        shape=(154 * 22, 1946),
        dtype=np.int64,
    )
    print(
        f"annihilation_q={annihilation_q.shape}"
        f" nnz={annihilation_q.nnz}"
        f" block_z={block_z.shape} nnz={block_z.nnz}"
    )
    ranks = []
    nnz = []
    for prime in PRIMES:
        face_constraints = reduced_product_mod(
            annihilation_q, block_z, prime
        )
        rank = modular_row_rank(face_constraints, prime)
        ranks.append(rank)
        nnz.append(face_constraints.nnz)
        print(
            f"prime={prime} rank={rank}"
            f" new_face_dimension={582-rank}"
            f" product_nnz={face_constraints.nnz}"
        )
    if len(set(ranks)) != 1:
        raise AssertionError(ranks)
    print(
        f"PASS ranks={ranks} new_block0_invariant_face_dimension="
        f"{582-ranks[0]} scope=linear_second_face_only"
    )


if __name__ == "__main__":
    main()
