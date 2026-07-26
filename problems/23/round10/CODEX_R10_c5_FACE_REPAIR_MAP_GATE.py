"""Independent structural gate for the sparse exact plateau repair map.

This replay does not import the repair-map producer.  It reconstructs the
388x388 selected-coordinate matrix from the two pinned source archives,
checks H*D=0 exactly, proves nonsingularity over a fresh prime, and performs a
fraction-free exact solve/check.  No SDP is built or run.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from sympy.polys.domains import ZZ
from sympy.polys.matrices import DomainMatrix


HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "CODEX_R10_c5_FACE_REPAIR_MAP_data.npz"
ROW_DATA_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
LOG_PATH = HERE / "CODEX_R10_c5_FACE_REPAIR_MAP_GATE.log"

EXPECTED_DATA_SHA256 = (
    "2F82F46A5C740164D47AB74F532C8D7BBED3AE97270894A18BA04D8F78DFF8D2"
)
EXPECTED_ROW_DATA_SHA256 = (
    "F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C"
)
EXPECTED_BLOWUP_SHA256 = (
    "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730"
)
PRIME = 1_000_000_007


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest().upper()


def unpack_csr(archive, name: str) -> sp.csr_matrix:
    return sp.csr_matrix(
        (
            archive[f"{name}_data"].astype(np.int64),
            archive[f"{name}_indices"].astype(np.int32),
            archive[f"{name}_indptr"].astype(np.int64),
        ),
        shape=tuple(int(value) for value in archive[f"{name}_shape"]),
        dtype=np.int64,
    )


def sparse_equal(left: sp.spmatrix, right: sp.spmatrix) -> bool:
    difference = left.astype(np.int64).tocsr() - right.astype(np.int64).tocsr()
    difference.eliminate_zeros()
    return difference.shape == left.shape == right.shape and difference.nnz == 0


def modular_rank(matrix: sp.csr_matrix, prime: int) -> int:
    pivots: dict[int, dict[int, int]] = {}
    for row_index in range(matrix.shape[0]):
        row = {
            int(column): int(value) % prime
            for column, value in zip(
                matrix.indices[
                    matrix.indptr[row_index] : matrix.indptr[row_index + 1]
                ],
                matrix.data[
                    matrix.indptr[row_index] : matrix.indptr[row_index + 1]
                ],
            )
            if int(value) % prime
        }
        while row:
            pivot = min(row)
            base = pivots.get(pivot)
            if base is None:
                inverse = pow(row[pivot], prime - 2, prime)
                pivots[pivot] = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value * inverse % prime
                }
                break
            factor = row[pivot]
            for column, value in base.items():
                updated = (
                    row.get(column, 0) - factor * value
                ) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
    return len(pivots)


def main() -> None:
    hashes = {
        "data": sha256(DATA_PATH),
        "row_data": sha256(ROW_DATA_PATH),
        "blowup": sha256(BLOWUP_PATH),
    }
    expected = {
        "data": EXPECTED_DATA_SHA256,
        "row_data": EXPECTED_ROW_DATA_SHA256,
        "blowup": EXPECTED_BLOWUP_SHA256,
    }
    if hashes != expected:
        raise AssertionError(f"pinned SHA-256 mismatch: {hashes}")

    data = np.load(DATA_PATH, allow_pickle=False)
    row_data = np.load(ROW_DATA_PATH, allow_pickle=False)
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    if int(data["format_version"][0]) != 1:
        raise AssertionError("unsupported repair-map format")
    selected = data["selected_live_nu_columns"].astype(np.int32)
    if len(selected) != 322 or len(set(map(int, selected))) != 322:
        raise AssertionError("wrong multiplier repair-coordinate set")
    if not np.array_equal(
        data["selected_live_nu_orbit_ids"],
        row_data["live_multiplier_orbits"][selected],
    ):
        raise AssertionError("selected live-orbit IDs are wrong")

    affine_nu = unpack_csr(row_data, "affine_nu")
    affine_gram = unpack_csr(row_data, "affine_gram")
    gram_face = unpack_csr(blowup, "gram_face")
    directions = unpack_csr(data, "gram_directions")
    stored_repair = unpack_csr(data, "repair_matrix")
    if directions.shape != (8647, 66):
        raise AssertionError("wrong Gram-direction shape")
    if stored_repair.shape != (388, 388):
        raise AssertionError("wrong repair-matrix shape")

    hd = gram_face @ directions
    hd.eliminate_zeros()
    if hd.nnz:
        raise AssertionError("a Gram repair direction leaves ker(H)")
    rebuilt = sp.hstack(
        [affine_nu[:, selected], affine_gram @ directions],
        format="csr",
    )
    if not sparse_equal(rebuilt, stored_repair):
        raise AssertionError("stored repair matrix does not match source maps")

    metadata = data["gram_direction_metadata"].astype(np.int64)
    if metadata.shape != (66, 5):
        raise AssertionError("wrong direction-metadata shape")
    blocks, counts = np.unique(metadata[:, 0], return_counts=True)
    block_histogram = dict(zip(map(int, blocks), map(int, counts)))
    if block_histogram != {0: 64, 1: 1, 5: 1}:
        raise AssertionError("unexpected repair-direction block support")

    fresh_rank = modular_rank(stored_repair, PRIME)
    if fresh_rank != 388:
        raise AssertionError("repair matrix loses fresh-prime rank")

    exact_matrix = DomainMatrix.from_list_sympy(
        388, 388, stored_repair.toarray().tolist()
    ).convert_to(ZZ)
    rhs_values = data["affine_rhs"].astype(np.int64)
    exact_rhs = DomainMatrix.from_list_sympy(
        388, 1, [[int(value)] for value in rhs_values]
    ).convert_to(ZZ)
    numerator, denominator = exact_matrix.solve_den(exact_rhs)
    denominator = int(denominator)
    if exact_matrix.matmul(numerator) != exact_rhs.mul(denominator):
        raise AssertionError("fraction-free exact repair solve did not replay")
    denominator_bits = abs(denominator).bit_length()
    numerator_bits = max(
        abs(int(value)).bit_length()
        for row in numerator.to_list()
        for value in row
    )

    messages = [
        "SOURCE_HASHES_PASS",
        "REPAIR_COORDINATES_PASS live_nu=322 gram=66 total=388",
        "DIRECTION_SUPPORT_PASS blocks={0:64,1:1,5:1}",
        "FACE_PRESERVATION_PASS H_times_D=0_exact",
        "REPAIR_MATRIX_PASS shape=388x388 nnz=14316",
        f"FRESH_PRIME_RANK_PASS p={PRIME} rank={fresh_rank}",
        f"EXACT_SOLVE_PASS denominator_bits={denominator_bits} "
        f"maximum_numerator_bits={numerator_bits}",
        "NO_DENSE_PROJECTOR: selected-coordinate solve only",
        "NO_SOLVER_RUN: structural reconstruction gate only",
        f"SHA256_DATA={hashes['data']}",
        f"SHA256_GATE={sha256(Path(__file__))}",
    ]
    text = "\n".join(messages) + "\n"
    LOG_PATH.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")
    print(f"LOG={LOG_PATH.resolve()}")
    print(f"SHA256_LOG={sha256(LOG_PATH)}")


if __name__ == "__main__":
    main()
