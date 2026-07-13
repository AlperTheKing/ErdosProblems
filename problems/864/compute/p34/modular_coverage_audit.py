"""Exhaustive audit of the P34 modular coverage obstruction."""

from __future__ import annotations

import argparse
import json
from itertools import combinations_with_replacement
from pathlib import Path


def pair_sum_values(values: tuple[int, ...], modulus: int) -> list[int]:
    return [(a + b) % modulus for a, b in combinations_with_replacement(values, 2)]


def is_strong_sidon(values: tuple[int, ...], modulus: int) -> bool:
    sums = pair_sum_values(values, modulus)
    return len(sums) == len(set(sums))


def difference_set(values: tuple[int, ...], modulus: int) -> set[int]:
    return {(a - b) % modulus for a in values for b in values}


def three_minus_one(values: tuple[int, ...], modulus: int) -> set[int]:
    sums = set(pair_sum_values(values, modulus))
    differences = difference_set(values, modulus)
    return {(total + difference) % modulus for total in sums for difference in differences}


def triple_set(values: tuple[int, ...], modulus: int) -> set[int]:
    pair_sums = {(a + b) % modulus for a in values for b in values}
    return {(total + c) % modulus for total in pair_sums for c in values}


def parity_lift(values: tuple[int, ...], modulus: int, parity: int) -> tuple[int, ...]:
    return tuple(sorted((parity + 2 * value) % (2 * modulus) for value in values))


def audit(max_order: int) -> dict[str, object]:
    total_subsets = 0
    sidon_subsets = 0
    forced_coverage = 0
    parity_lifts = 0
    per_order: list[dict[str, int]] = []

    for modulus in range(1, max_order + 1):
        order_subsets = 0
        order_sidon = 0
        order_forced = 0
        for mask in range(1, 1 << modulus):
            total_subsets += 1
            order_subsets += 1
            values = tuple(value for value in range(modulus) if mask >> value & 1)
            if not is_strong_sidon(values, modulus):
                continue

            sidon_subsets += 1
            order_sidon += 1
            size = len(values)
            sums = set(pair_sum_values(values, modulus))
            differences = difference_set(values, modulus)
            assert len(sums) == size * (size + 1) // 2
            assert len(differences) == size * (size - 1) + 1

            coverage = three_minus_one(values, modulus)
            threshold = 2 * modulus < 3 * size * size - size + 2
            if threshold:
                assert len(coverage) == modulus
                forced_coverage += 1
                order_forced += 1

            for parity in (0, 1):
                lifted = parity_lift(values, modulus, parity)
                assert len(lifted) == size
                assert is_strong_sidon(lifted, 2 * modulus)
                if threshold:
                    triples = triple_set(lifted, 2 * modulus)
                    assert set(lifted) & triples
                parity_lifts += 1

        per_order.append(
            {
                "order": modulus,
                "subsets": order_subsets,
                "strong_sidon_subsets": order_sidon,
                "forced_coverage_subsets": order_forced,
            }
        )

    return {
        "max_order": max_order,
        "total_nonempty_subsets": total_subsets,
        "strong_sidon_subsets": sidon_subsets,
        "forced_coverage_subsets": forced_coverage,
        "parity_lifts_checked": parity_lifts,
        "per_order": per_order,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-order", type=int, default=18)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = audit(args.max_order)
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)


if __name__ == "__main__":
    main()
