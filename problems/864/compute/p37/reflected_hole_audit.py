"""Exact audit for the reflected P21 three-sum-free reduction.

For a Sidon ruler F subset [0, W] containing 0 and W and an integer
2W < M < 3W, put E = {M - 2f : f in F}.  Then E has one parity and

    E intersect (E + E + E) = empty  iff  M notin 3F - F.

All checks below are literal integer checks.  Unordered pair sums include
diagonals, and triples include repeated summands.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations, combinations_with_replacement


def unordered_sums(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in combinations_with_replacement(values, 2))


def positive_differences(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(values[j] - values[i] for i in range(len(values)) for j in range(i + 1, len(values)))


def is_sidon(values: tuple[int, ...]) -> bool:
    sums = unordered_sums(values)
    return len(sums) == len(set(sums))


def three_minus_one(values: tuple[int, ...]) -> set[int]:
    triples = {
        a + b + c
        for a, b, c in combinations_with_replacement(values, 3)
    }
    return {t - d for t in triples for d in values}


def literal_e_check(values: tuple[int, ...], width: int, center: int) -> dict[str, object]:
    e = tuple(sorted(center - 2 * f for f in values))
    sums = unordered_sums(e)
    triples = {
        a + b + c
        for a, b, c in combinations_with_replacement(e, 3)
    }
    return {
        "E": e,
        "positive": e[0] > 0,
        "same_parity": len({x % 2 for x in e}) == 1,
        "sidon_with_diagonals": len(sums) == len(set(sums)),
        "three_free_with_repetition": not (set(e) & triples),
        "max_E": e[-1],
        "min_E": e[0],
        "expected_min_E": center - 2 * width,
    }


def corner_certificate(values: tuple[int, ...], width: int, center: int) -> dict[str, object]:
    gap = center - 2 * width
    overlap = width - gap
    sums = set(unordered_sums(values))
    diffs = set(positive_differences(values))
    high_sums = sorted(s for s in sums if center - width <= s <= 2 * width)
    high_diffs = sorted(d for d in diffs if gap <= d <= width)
    reflected_diffs = sorted(center - d for d in high_diffs)
    intersection = sorted(set(high_sums) & set(reflected_diffs))
    return {
        "gap": gap,
        "overlap": overlap,
        "high_sums": high_sums,
        "high_diffs": high_diffs,
        "reflected_diffs": reflected_diffs,
        "intersection": intersection,
        "occupied": len(high_sums) + len(high_diffs),
        "capacity": overlap + 1,
        "slack": overlap + 1 - len(high_sums) - len(high_diffs),
    }


def enumerate_rulers(max_width: int, max_examples: int) -> dict[str, object]:
    rulers = 0
    holes = 0
    by_size: dict[int, dict[str, object]] = {}
    examples: list[dict[str, object]] = []

    for width in range(1, max_width + 1):
        interior = range(1, width)
        for count in range(width):
            for middle in combinations(interior, count):
                values = (0, *middle, width)
                if not is_sidon(values):
                    continue
                rulers += 1
                forbidden = three_minus_one(values)
                for center in range(2 * width + 1, 3 * width):
                    if center in forbidden:
                        continue
                    holes += 1
                    check = literal_e_check(values, width, center)
                    if not all(
                        check[key]
                        for key in (
                            "positive",
                            "same_parity",
                            "sidon_with_diagonals",
                            "three_free_with_repetition",
                        )
                    ):
                        raise AssertionError((values, center, check))
                    corner = corner_certificate(values, width, center)
                    if corner["intersection"] or corner["slack"] < 0:
                        raise AssertionError((values, center, corner))

                    size = len(values)
                    record = {
                        "p": size,
                        "W": width,
                        "M": center,
                        "M_over_p2": f"{center}/{size * size}",
                        "F": values,
                        **check,
                        "corner": corner,
                    }
                    current = by_size.get(size)
                    if current is None or center * current["p"] ** 2 < current["M"] * size**2:
                        by_size[size] = record
                    if len(examples) < max_examples:
                        examples.append(record)

    return {
        "max_width": max_width,
        "sidon_rulers": rulers,
        "reflected_top_holes": holes,
        "best_by_size": {str(k): by_size[k] for k in sorted(by_size)},
        "sample_holes": examples,
    }


def fixed_certificates() -> dict[str, object]:
    cases = [
        ((0, 1), 1, 4),
        ((0, 1, 3, 8, 12), 12, 30),
        ((0, 1, 3, 11, 15, 20, 36, 43, 49), 49, 116),
    ]
    output = []
    for values, width, center in cases:
        if not is_sidon(values):
            raise AssertionError((values, "not Sidon"))
        hole = center not in three_minus_one(values)
        check = literal_e_check(values, width, center)
        corner = corner_certificate(values, width, center)
        if not hole or corner["intersection"]:
            raise AssertionError((values, center, hole, corner))
        output.append(
            {
                "p": len(values),
                "F": values,
                "W": width,
                "M": center,
                "hole": hole,
                "literal": check,
                "corner": corner,
            }
        )
    return {"fixed_certificates": output}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=18)
    parser.add_argument("--max-examples", type=int, default=8)
    args = parser.parse_args()
    if args.max_width < 1:
        parser.error("--max-width must be positive")
    result = {
        **fixed_certificates(),
        "enumeration": enumerate_rulers(args.max_width, args.max_examples),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
