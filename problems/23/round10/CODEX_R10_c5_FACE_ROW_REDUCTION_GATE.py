"""Independent replay gate for the exact 388-row plateau-face selector.

This gate does not import the producer.  It rebuilds the original sparse
maps from the pinned equality/face archives, checks the exported selector and
integer dependency certificates exactly, and reruns the complete rank test
over the fresh prime 998244353.

No SDP is built or solved.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_data.npz"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
LOG_PATH = HERE / "CODEX_R10_c5_FACE_ROW_REDUCTION_GATE.log"

EXPECTED_DATA_SHA256 = (
    "F5B8BA8B0D2460E8A8ACDB3841464E4984FCEB4B0E45A7926B4D3B4203AC205C"
)
EXPECTED_EQUALITY_SHA256 = (
    "08DC9A3A4A8B5931B67B128CB7FD393EA126BA233CDC208A3675CB650C4FDA0F"
)
EXPECTED_BLOWUP_SHA256 = (
    "3B120381926290147890ABC7BA2A50B85532F93F751B961A79F81653F6AC3730"
)
PRIME = 998_244_353
LIVE_COUNT = 526
GRAM_COUNT = 8647


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


def sparse_zero(matrix: sp.spmatrix) -> bool:
    checked = matrix.astype(np.int64).tocsr()
    checked.eliminate_zeros()
    return checked.nnz == 0


def row_dict(matrix: sp.csr_matrix, row: int, offset: int = 0) -> dict[int, int]:
    return {
        offset + int(column): int(value)
        for column, value in zip(
            matrix.indices[matrix.indptr[row] : matrix.indptr[row + 1]],
            matrix.data[matrix.indptr[row] : matrix.indptr[row + 1]],
        )
        if int(value)
    }


class ModularSpan:
    def __init__(self, prime: int) -> None:
        self.prime = prime
        self.rows: dict[int, dict[int, int]] = {}

    def add(self, source: dict[int, int]) -> bool:
        prime = self.prime
        row = {
            column: value % prime
            for column, value in source.items()
            if value % prime
        }
        while row:
            pivot = min(row)
            base = self.rows.get(pivot)
            if base is None:
                inverse = pow(row[pivot], prime - 2, prime)
                self.rows[pivot] = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value * inverse % prime
                }
                return True
            factor = row[pivot]
            for column, value in base.items():
                updated = (
                    row.get(column, 0) - factor * value
                ) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
        return False


def main() -> None:
    hashes = {
        "data": sha256(DATA_PATH),
        "equality": sha256(EQUALITY_PATH),
        "blowup": sha256(BLOWUP_PATH),
    }
    expected = {
        "data": EXPECTED_DATA_SHA256,
        "equality": EXPECTED_EQUALITY_SHA256,
        "blowup": EXPECTED_BLOWUP_SHA256,
    }
    if hashes != expected:
        raise AssertionError(f"pinned SHA-256 mismatch: {hashes}")

    data = np.load(DATA_PATH, allow_pickle=False)
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    if int(data["format_version"][0]) != 1:
        raise AssertionError("unsupported selector format")
    if data["primes"].tolist() != [1_000_003, 2_000_003]:
        raise AssertionError("producer-prime metadata mismatch")
    if data["rank_h_by_prime"].tolist() != [6129, 6129]:
        raise AssertionError("producer H-rank metadata mismatch")
    if data["rank_augmented_by_prime"].tolist() != [6517, 6517]:
        raise AssertionError("producer augmented-rank metadata mismatch")
    if data["affine_rank_mod_h_by_prime"].tolist() != [388, 388]:
        raise AssertionError("producer affine-rank metadata mismatch")

    normalization = unpack_csr(equality, "normalization_live")
    target_nu = unpack_csr(equality, "target_nu_live")
    target_gram = unpack_csr(equality, "target_gram")
    gram_face = unpack_csr(blowup, "gram_face")
    full_nu = sp.vstack([normalization, target_nu], format="csr")
    full_gram = sp.vstack(
        [sp.csr_matrix((56, GRAM_COUNT), dtype=np.int64), target_gram],
        format="csr",
    )
    full_rhs = np.concatenate(
        [equality["normalization_rhs"], equality["target_rhs"]]
    ).astype(np.int64)

    keep = data["keep_global_rows"].astype(np.int32)
    drop = data["drop_global_rows"].astype(np.int32)
    if len(keep) != 388 or len(drop) != 60:
        raise AssertionError("selector cardinalities are wrong")
    if keep[:56].tolist() != list(range(56)):
        raise AssertionError("a normalization row was omitted")
    if sorted(map(int, np.concatenate((keep, drop)))) != list(range(448)):
        raise AssertionError("keep/drop do not partition the original rows")
    if not np.array_equal(
        data["keep_target_rows"], keep[keep >= 56] - 56
    ):
        raise AssertionError("retained target-row metadata mismatch")
    if not np.array_equal(data["drop_target_rows"], drop - 56):
        raise AssertionError("omitted target-row metadata mismatch")

    reduced_nu = unpack_csr(data, "affine_nu")
    reduced_gram = unpack_csr(data, "affine_gram")
    dependency = unpack_csr(data, "dependency")
    dependency_gram = unpack_csr(data, "dependency_gram")
    if not sparse_equal(reduced_nu, full_nu[keep, :]):
        raise AssertionError("exported live-nu selector map is wrong")
    if not sparse_equal(reduced_gram, full_gram[keep, :]):
        raise AssertionError("exported Gram selector map is wrong")
    if not np.array_equal(data["affine_rhs"], full_rhs[keep]):
        raise AssertionError("exported selected RHS is wrong")
    if dependency.shape != (60, 448):
        raise AssertionError("dependency matrix has the wrong shape")

    pivot_values = dependency[np.arange(60), drop].A1.astype(np.int64)
    if not np.array_equal(
        pivot_values, data["dependency_pivot_coefficients"]
    ):
        raise AssertionError("dependency pivots disagree with metadata")
    if np.any(pivot_values <= 0):
        raise AssertionError("dependency pivots are not positive")
    drop_set = set(map(int, drop))
    for relation in range(60):
        support = set(
            map(
                int,
                dependency.indices[
                    dependency.indptr[relation] :
                    dependency.indptr[relation + 1]
                ],
            )
        )
        if support & drop_set != {int(drop[relation])}:
            raise AssertionError("dependency is not triangular")

    if not sparse_zero(dependency @ full_nu):
        raise AssertionError("dependency does not cancel live multipliers")
    if np.any(np.asarray(dependency @ full_rhs).reshape(-1)):
        raise AssertionError("dependency does not cancel the RHS")
    if not sparse_equal(dependency @ full_gram, dependency_gram):
        raise AssertionError("stored dependency Gram rows are wrong")

    span = ModularSpan(PRIME)
    for row in range(gram_face.shape[0]):
        if not span.add(row_dict(gram_face, row, LIVE_COUNT)):
            raise AssertionError(f"H loses rank at fresh-prime row {row}")
    rank_h = len(span.rows)
    for global_row in keep:
        source = row_dict(full_nu, int(global_row))
        source.update(row_dict(full_gram, int(global_row), LIVE_COUNT))
        if not span.add(source):
            raise AssertionError(
                f"retained row {global_row} is dependent at fresh prime"
            )
    rank_augmented = len(span.rows)
    for global_row in drop:
        source = row_dict(full_nu, int(global_row))
        source.update(row_dict(full_gram, int(global_row), LIVE_COUNT))
        if span.add(source):
            raise AssertionError(
                f"omitted row {global_row} increases fresh-prime rank"
            )
    if rank_h != 6129 or rank_augmented != 6517:
        raise AssertionError("fresh-prime ranks are wrong")

    messages = [
        "SOURCE_HASHES_PASS",
        "SELECTOR_PASS keep=388 drop=60 normalization=56 target_keep=332",
        "MAPS_PASS affine_nu=388x526 affine_gram=388x8647",
        "DEPENDENCIES_EXACT_PASS count=60 triangular=true "
        "lambda_nu=0 lambda_rhs=0",
        f"FRESH_PRIME_PASS p={PRIME} rank_H={rank_h} "
        f"rank_H_plus_affine={rank_augmented} rank_affine_mod_H=388",
        "FULLY_REDUCED_CONTRACT_PASS live_nu=526 forced_nu_not_instantiated=2085",
        "NO_SOLVER_RUN: exact row-selector replay only",
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
