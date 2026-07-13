"""Exhaustive exact audit of the modular carry-intersection obstruction."""

from __future__ import annotations

import argparse
import json
from itertools import combinations_with_replacement


def modular_sums(values: tuple[int, ...], modulus: int) -> list[int]:
    return [
        (a + b) % modulus
        for a, b in combinations_with_replacement(values, 2)
    ]


def positive_difference_residues(
    values: tuple[int, ...], modulus: int
) -> list[int]:
    return [
        (values[j] - values[i]) % modulus
        for i in range(len(values))
        for j in range(i + 1, len(values))
    ]


def full_difference_support(values: tuple[int, ...], modulus: int) -> set[int]:
    return {(a - b) % modulus for a in values for b in values}


def audit(max_modulus: int) -> dict[str, int]:
    subsets = 0
    strong_sidon_sets = 0
    oriented_targets = 0
    full_targets = 0
    positive_bound_equalities = 0
    full_bound_equalities = 0

    for modulus in range(2, max_modulus + 1):
        for mask in range(1, 1 << modulus):
            subsets += 1
            values = tuple(i for i in range(modulus) if mask & (1 << i))
            sums = modular_sums(values, modulus)
            if len(sums) != len(set(sums)):
                continue
            strong_sidon_sets += 1
            p = len(values)
            positive_diffs = positive_difference_residues(values, modulus)
            if len(positive_diffs) != p * (p - 1) // 2:
                raise AssertionError((modulus, values, "difference count"))
            if len(positive_diffs) != len(set(positive_diffs)):
                raise AssertionError((modulus, values, "difference collision"))

            sum_support = set(sums)
            positive_support = set(positive_diffs)
            full_support = full_difference_support(values, modulus)
            expected_full_size = p * (p - 1) + 1
            if len(full_support) != expected_full_size:
                raise AssertionError((modulus, values, "full difference support"))

            positive_lower = max(0, p * p - modulus)
            full_lower = max(
                0,
                (3 * p * p - p + 2) // 2 - modulus,
            )
            for target in range(modulus):
                oriented_targets += 1
                positive_count = len(
                    sum_support & {(target - d) % modulus for d in positive_support}
                )
                if positive_count < positive_lower:
                    raise AssertionError(
                        (modulus, values, target, positive_count, positive_lower)
                    )
                if positive_count == positive_lower:
                    positive_bound_equalities += 1

                full_targets += 1
                full_count = len(
                    sum_support & {(target - d) % modulus for d in full_support}
                )
                if full_count < full_lower:
                    raise AssertionError(
                        (modulus, values, target, full_count, full_lower)
                    )
                if full_count == full_lower:
                    full_bound_equalities += 1

    return {
        "max_modulus": max_modulus,
        "nonempty_subsets": subsets,
        "strong_sidon_sets": strong_sidon_sets,
        "oriented_targets": oriented_targets,
        "full_targets": full_targets,
        "positive_bound_equalities": positive_bound_equalities,
        "full_bound_equalities": full_bound_equalities,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-modulus", type=int, default=16)
    args = parser.parse_args()
    if args.max_modulus < 2:
        parser.error("--max-modulus must be at least 2")
    print(json.dumps(audit(args.max_modulus), sort_keys=True))


if __name__ == "__main__":
    main()
