"""Exact determinant gate for a 132-coordinate kernel principal chart."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from sympy.polys.domains import ZZ
from sympy.polys.matrices import DomainMatrix


HERE = Path(__file__).resolve().parent
DATA = HERE / "CODEX_R10_ZERO_NU_BLOCK0_KERNEL132_SPARSE_data.npz"
EXPECTED_DATA_SHA256 = (
    "840E253D2F161666DD457F54B5A92FFF464081425D5055CBCB6D1E1D5309EFEB"
)
P = list(range(108)) + [
    109,
    110,
    111,
    112,
    113,
    116,
    117,
    118,
    119,
    120,
    121,
    122,
    123,
    124,
    125,
    126,
    127,
    128,
    129,
    133,
    134,
    135,
    136,
    143,
]
EXPECTED_DETERMINANT = -(2**92) * (3**22)
PRIMES = (1_000_151, 1_000_159, 1_000_171)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def rank_mod_prime(matrix: list[list[int]], prime: int) -> int:
    rows = [
        [int(value) % prime for value in row] for row in matrix
    ]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next(
            (
                index
                for index in range(rank, len(rows))
                if rows[index][column]
            ),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, prime)
        rows[rank] = [
            value * inverse % prime for value in rows[rank]
        ]
        for index in range(rank + 1, len(rows)):
            factor = rows[index][column]
            if factor:
                rows[index] = [
                    (left - factor * right) % prime
                    for left, right in zip(rows[index], rows[rank])
                ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def main() -> None:
    observed = sha256(DATA)
    if observed != EXPECTED_DATA_SHA256:
        raise AssertionError(f"data SHA-256 mismatch: {observed}")
    artifact = np.load(DATA, allow_pickle=False)
    kernel = [
        [int(value) for value in row]
        for row in artifact["kernel_rows_decimal"]
    ]
    if len(kernel) != 132 or any(len(row) != 154 for row in kernel):
        raise AssertionError("wrong kernel dimensions")
    if len(P) != 132 or len(set(P)) != 132:
        raise AssertionError("P is not a 132-element coordinate set")
    chart = [[row[column] for column in P] for row in kernel]
    determinant = int(
        DomainMatrix.from_list_sympy(
            132, 132, chart
        ).convert_to(ZZ).det()
    )
    if determinant != EXPECTED_DETERMINANT:
        raise AssertionError(f"determinant mismatch: {determinant}")
    ranks = [rank_mod_prime(chart, prime) for prime in PRIMES]
    residues = [determinant % prime for prime in PRIMES]
    if ranks != [132, 132, 132] or not all(residues):
        raise AssertionError((ranks, residues))
    print(
        json.dumps(
            {
                "status": "PASS",
                "P": P,
                "chart_shape": [132, 132],
                "determinant": str(determinant),
                "determinant_factorization": "-2^92*3^22",
                "fresh_primes": list(PRIMES),
                "fresh_prime_ranks": ranks,
                "determinant_residues": residues,
                "consequence": (
                    "for symmetric Q with S*Q=0, "
                    "Q is PSD iff Q[P,P] is PSD"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
