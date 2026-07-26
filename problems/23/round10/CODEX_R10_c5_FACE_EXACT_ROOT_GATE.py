"""Independent exact root gate for a future Gamma_11 degree-4 certificate.

This verifier imports neither the reduced SDP constructor nor the exact
reconstruction runner.  It rebuilds Gamma_11, the 56 cyclic-interval cuts,
degree-4 and degree-6 monomials, the full polynomial identity, and every PSD
block using Fraction arithmetic.

There is deliberately no default certificate path.
"""

from __future__ import annotations

import argparse
import math
import pickle
from fractions import Fraction
from pathlib import Path


N = 11
MULTIPLIER_DEGREE = 4
TARGET_DEGREE = 6
C_FIXED = Fraction(25)


def monomials(n: int, degree: int) -> list[tuple[int, ...]]:
    output: list[tuple[int, ...]] = []

    def visit(index: int, remaining: int, prefix: list[int]) -> None:
        if index == n - 1:
            output.append(tuple(prefix + [remaining]))
            return
        for value in range(remaining + 1):
            visit(index + 1, remaining - value, prefix + [value])

    visit(0, degree, [])
    return output


def multinomial(exponent: tuple[int, ...]) -> int:
    output = math.factorial(sum(exponent))
    for value in exponent:
        output //= math.factorial(value)
    return output


def parity_blocks(
    n: int, degree: int
) -> list[list[tuple[int, ...]]]:
    groups: dict[tuple[int, ...], list[tuple[int, ...]]] = {}
    for exponent in monomials(n, degree):
        mask = tuple(value & 1 for value in exponent)
        groups.setdefault(mask, []).append(exponent)
    return [groups[key] for key in sorted(groups)]


def gamma_edges(n: int) -> list[tuple[int, int]]:
    return [
        (left, right)
        for left in range(n)
        for right in range(left + 1, n)
        if 3 * min(right - left, n - (right - left)) > n
    ]


def canonical_mask(side: set[int], n: int) -> int:
    if 0 in side:
        side = set(range(n)) - side
    return sum(1 << (vertex - 1) for vertex in side)


def cyclic_interval_cuts(
    n: int, edges: list[tuple[int, int]]
) -> list[tuple[int, frozenset[int]]]:
    masks = {canonical_mask(set(), n)}
    for length in range(1, 6):
        for start in range(n):
            masks.add(
                canonical_mask(
                    {(start + offset) % n for offset in range(length)},
                    n,
                )
            )
    if len(masks) != 56:
        raise AssertionError(f"rebuilt cut count={len(masks)}")
    output = []
    for mask in sorted(masks):
        side = {
            vertex
            for vertex in range(1, n)
            if (mask >> (vertex - 1)) & 1
        }
        monochromatic = frozenset(
            index
            for index, (left, right) in enumerate(edges)
            if (left in side) == (right in side)
        )
        output.append((mask, monochromatic))
    return output


def ldl_psd_verified(
    source: list[list[Fraction]],
) -> tuple[bool, str]:
    """Symmetric-pivoted exact LDL with explicit exact re-multiplication."""
    size = len(source)
    if any(len(row) != size for row in source):
        return False, "matrix is not square"
    matrix = [
        [Fraction(source[row][column]) for column in range(size)]
        for row in range(size)
    ]
    for row in range(size):
        for column in range(row):
            if matrix[row][column] != matrix[column][row]:
                return False, f"matrix is not symmetric at ({row},{column})"

    work = [row[:] for row in matrix]
    permutation = list(range(size))
    lower = [
        [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]
    diagonal = [Fraction(0)] * size
    for step in range(size):
        pivot = max(
            range(step, size), key=lambda index: work[index][index]
        )
        if work[pivot][pivot] < 0:
            return False, f"negative pivot at step {step}"
        if work[pivot][pivot] == 0:
            for row in range(step, size):
                for column in range(step, size):
                    if work[row][column] != 0:
                        return (
                            False,
                            "zero diagonal with nonzero trailing entry",
                        )
            break
        if pivot != step:
            work[step], work[pivot] = work[pivot], work[step]
            for row in range(size):
                work[row][step], work[row][pivot] = (
                    work[row][pivot],
                    work[row][step],
                )
            for column in range(step):
                lower[step][column], lower[pivot][column] = (
                    lower[pivot][column],
                    lower[step][column],
                )
            permutation[step], permutation[pivot] = (
                permutation[pivot],
                permutation[step],
            )
        pivot_value = work[step][step]
        diagonal[step] = pivot_value
        for row in range(step + 1, size):
            factor = work[row][step] / pivot_value
            lower[row][step] = factor
            if factor:
                for column in range(step, size):
                    work[row][column] -= factor * work[step][column]

    if any(value < 0 for value in diagonal):
        return False, "negative LDL diagonal"
    for row in range(size):
        for column in range(row, size):
            rebuilt = sum(
                lower[row][inner]
                * diagonal[inner]
                * lower[column][inner]
                for inner in range(min(row, column) + 1)
            )
            if rebuilt != matrix[
                permutation[row]
            ][permutation[column]]:
                return (
                    False,
                    f"LDL reconstruction mismatch at ({row},{column})",
                )
    rank = sum(value > 0 for value in diagonal)
    return True, f"rank {rank}"


def verify_payload(payload: dict) -> dict[str, object]:
    if payload.get("m") != 11 or payload.get("n") != N:
        raise AssertionError("certificate is not Gamma_11")
    if payload.get("d") != 2:
        raise AssertionError("certificate multiplier degree is not 4")
    if Fraction(payload.get("c")) != C_FIXED:
        raise AssertionError("certificate c is not exact 25")

    edges = gamma_edges(N)
    cuts = cyclic_interval_cuts(N, edges)
    if list(map(tuple, payload.get("E", []))) != edges:
        raise AssertionError("edge list differs from rebuilt Gamma_11")
    stored_cuts = [
        (int(mask), frozenset(int(value) for value in monochromatic))
        for mask, monochromatic in payload.get("cuts", [])
    ]
    if stored_cuts != cuts:
        raise AssertionError("cut list differs from 56 rebuilt intervals")

    multiplier_monomials = monomials(N, MULTIPLIER_DEGREE)
    multiplier_set = set(multiplier_monomials)
    nu = payload.get("nu")
    if not isinstance(nu, dict):
        raise AssertionError("nu is not a dictionary")
    for key, value in nu.items():
        if not (
            isinstance(key, tuple)
            and len(key) == 2
            and isinstance(key[0], int)
        ):
            raise AssertionError("malformed multiplier key")
        cut_index, exponent = key
        exponent = tuple(exponent)
        if not 0 <= cut_index < len(cuts) or exponent not in multiplier_set:
            raise AssertionError("multiplier key outside rebuilt orders")
        if not isinstance(value, Fraction):
            raise AssertionError("multiplier value is not Fraction")
        if value < 0:
            raise AssertionError("negative multiplier")

    for exponent in multiplier_monomials:
        total = sum(
            nu.get((cut_index, exponent), Fraction(0))
            for cut_index in range(len(cuts))
        )
        expected = C_FIXED * multinomial(exponent)
        if total != expected:
            raise AssertionError(
                f"normalization failure at {exponent}: {total}!={expected}"
            )

    expected_blocks = parity_blocks(N, TARGET_DEGREE)
    qblocks = payload.get("Q")
    if not isinstance(qblocks, list) or len(qblocks) != len(expected_blocks):
        raise AssertionError("wrong number of parity Gram blocks")
    target = {
        exponent: Fraction(multinomial(exponent))
        for exponent in monomials(N, TARGET_DEGREE)
    }
    for (cut_index, exponent), value in nu.items():
        for edge_index in cuts[cut_index][1]:
            left, right = edges[edge_index]
            lifted = list(exponent)
            lifted[left] += 1
            lifted[right] += 1
            key = tuple(lifted)
            target[key] -= value

    gram = {exponent: Fraction(0) for exponent in target}
    psd_ranks: list[int] = []
    for block_index, ((basis, matrix), expected_basis) in enumerate(
        zip(qblocks, expected_blocks)
    ):
        basis = [tuple(exponent) for exponent in basis]
        if basis != expected_basis:
            raise AssertionError(
                f"parity basis mismatch in block {block_index}"
            )
        if len(matrix) != len(basis) or any(
            len(row) != len(basis) for row in matrix
        ):
            raise AssertionError(f"matrix shape mismatch in block {block_index}")
        if any(
            not isinstance(value, Fraction)
            for row in matrix
            for value in row
        ):
            raise AssertionError(
                f"non-Fraction Gram value in block {block_index}"
            )
        for row in range(len(basis)):
            for column in range(len(basis)):
                exponent = tuple(
                    (
                        basis[row][vertex] + basis[column][vertex]
                    )
                    // 2
                    for vertex in range(N)
                )
                gram[exponent] += matrix[row][column]
        ok, information = ldl_psd_verified(matrix)
        if not ok:
            raise AssertionError(
                f"PSD failure in block {block_index}: {information}"
            )
        psd_ranks.append(int(information.split()[-1]))
    if target != gram:
        differing = [
            exponent
            for exponent in target
            if target[exponent] != gram[exponent]
        ]
        first = differing[0]
        raise AssertionError(
            f"full polynomial identity fails at {first}: "
            f"{target[first]}!={gram[first]}"
        )
    return {
        "status": "PASS",
        "scope": "independent exact Gamma_11 degree-4 root replay",
        "edges": len(edges),
        "cuts": len(cuts),
        "multiplier_monomials": len(multiplier_monomials),
        "stored_nonzero_multipliers": len(nu),
        "target_monomials": len(target),
        "parity_blocks": len(qblocks),
        "PSD_rank_sum": sum(psd_ranks),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "certificate",
        type=Path,
        help="explicit exact Q4 pickle produced by the reconstruction runner",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.certificate.open("rb") as handle:
        payload = pickle.load(handle)
    result = verify_payload(payload)
    print(result)
    print("EXACT_ROOT_GATE_PASS")


if __name__ == "__main__":
    main()
