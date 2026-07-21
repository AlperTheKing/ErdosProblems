#!/usr/bin/env python3
"""Independent scalar verifier for an AJT F_5, n=8 matrix certificate."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Sequence

MODULUS = 5
DIMENSION = 8
TORUS_VALUES = (1, 2, 3, 4)
TORUS_SIZE = len(TORUS_VALUES) ** DIMENSION
INVERSE_MOD_5 = (0, 1, 3, 2, 4)

Matrix = tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class VerificationResult:
    accepted: bool
    reason: str
    rank: int
    checked: int
    witness: tuple[int, ...] | None = None


def read_matrix(path: Path) -> Matrix:
    """Read exactly 64 decimal integers and reduce them modulo 5."""
    try:
        text = path.read_text(encoding="ascii")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read ASCII matrix file: {exc}") from exc

    tokens = text.split()
    if len(tokens) != DIMENSION * DIMENSION:
        raise ValueError(
            f"expected exactly 64 integers, found {len(tokens)} token(s)"
        )

    try:
        entries = [int(token, 10) % MODULUS for token in tokens]
    except ValueError as exc:
        raise ValueError("matrix contains a non-integer token") from exc

    return tuple(
        tuple(entries[row * DIMENSION : (row + 1) * DIMENSION])
        for row in range(DIMENSION)
    )


def rank_mod_5(matrix: Sequence[Sequence[int]]) -> int:
    """Compute row rank by scalar Gaussian elimination over F_5."""
    if len(matrix) != DIMENSION or any(len(row) != DIMENSION for row in matrix):
        raise ValueError("matrix must be 8 by 8")

    work = [[entry % MODULUS for entry in row] for row in matrix]
    pivot_row = 0

    for column in range(DIMENSION):
        pivot = next(
            (
                row
                for row in range(pivot_row, DIMENSION)
                if work[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            continue

        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = INVERSE_MOD_5[work[pivot_row][column]]
        for col in range(column, DIMENSION):
            work[pivot_row][col] = (work[pivot_row][col] * inverse) % MODULUS

        for row in range(DIMENSION):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor == 0:
                continue
            for col in range(column, DIMENSION):
                work[row][col] = (
                    work[row][col] - factor * work[pivot_row][col]
                ) % MODULUS

        pivot_row += 1
        if pivot_row == DIMENSION:
            break

    return pivot_row


def verify_matrix(matrix: Sequence[Sequence[int]]) -> VerificationResult:
    """Verify nonsingularity and exhaustive torus coverage."""
    rank = rank_mod_5(matrix)
    if rank != DIMENSION:
        return VerificationResult(False, "singular", rank, 0)

    reduced = tuple(
        tuple(entry % MODULUS for entry in row) for row in matrix
    )
    checked = 0
    for point in product(TORUS_VALUES, repeat=DIMENSION):
        checked += 1
        covered = False
        for row in reduced:
            dot_product = sum(
                coefficient * coordinate
                for coefficient, coordinate in zip(row, point)
            )
            if dot_product % MODULUS == 0:
                covered = True
                break
        if not covered:
            return VerificationResult(
                False, "uncovered", rank, checked, tuple(point)
            )

    if checked != TORUS_SIZE:
        raise AssertionError("internal torus enumeration count mismatch")
    return VerificationResult(True, "covered", rank, checked)


def run_self_test() -> int:
    identity = tuple(
        tuple(1 if row == col else 0 for col in range(DIMENSION))
        for row in range(DIMENSION)
    )
    result = verify_matrix(identity)
    expected_witness = (1,) * DIMENSION
    if (
        result.accepted
        or result.reason != "uncovered"
        or result.rank != DIMENSION
        or result.witness != expected_witness
    ):
        print(f"SELF-TEST FAIL: identity result was {result}")
        return 2

    print(
        "SELF-TEST PASS: identity rejected with uncovered witness "
        + " ".join(map(str, expected_witness))
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify an 8x8 integer matrix as an AJT counterexample over F_5."
        )
    )
    parser.add_argument("matrix", nargs="?", type=Path, help="plain 8x8 matrix file")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="check that the identity matrix is rejected",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()
    if args.matrix is None:
        parser.error("a matrix file is required unless --self-test is used")

    try:
        matrix = read_matrix(args.matrix)
    except ValueError as exc:
        print(f"INPUT ERROR: {exc}")
        return 2

    result = verify_matrix(matrix)
    if result.accepted:
        print(
            f"PASS: rank={result.rank}; covered all {result.checked} "
            "nowhere-zero vectors"
        )
        return 0
    if result.reason == "singular":
        print(f"FAIL: singular modulo 5; rank={result.rank}")
        return 1

    assert result.witness is not None
    print(
        f"FAIL: uncovered witness after {result.checked} check(s): "
        + " ".join(map(str, result.witness))
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
