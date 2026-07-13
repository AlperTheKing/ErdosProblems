#!/usr/bin/env python3
"""Exact centered-C20 search around a reflected admissible witness."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


DEFAULT_SEED = (
    1,
    8,
    14,
    17,
    31,
    39,
    51,
    78,
    97,
    99,
    123,
    141,
    151,
    152,
    156,
    192,
    227,
    259,
)


def ceil_cuberoot_square(n: int) -> int:
    target = n * n
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid * mid >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


def reflected_set(lower: tuple[int, ...], center: int) -> tuple[int, ...]:
    result = tuple(sorted(set(lower) | {center - value for value in lower}))
    if len(result) != 2 * len(lower):
        raise ValueError("lower core and its reflection are not disjoint")
    return result


def admissibility(a: tuple[int, ...]) -> tuple[bool, int | None, int]:
    counts: dict[int, int] = {}
    for left_index, left in enumerate(a):
        for right in a[left_index:]:
            pair_sum = left + right
            counts[pair_sum] = counts.get(pair_sum, 0) + 1
    repeated = [(value, count) for value, count in counts.items() if count > 1]
    if len(repeated) > 1:
        return False, None, 0
    if not repeated:
        return True, None, 0
    return True, repeated[0][0], repeated[0][1]


def metrics(lower: tuple[int, ...], center: int) -> dict[str, Any] | None:
    a = reflected_set(lower, center)
    valid, exceptional_sum, exceptional_multiplicity = admissibility(a)
    if not valid:
        return None
    n = center - 1
    if a[0] < 1 or a[-1] > n:
        return None
    h = ceil_cuberoot_square(n)
    counts = [0] * h
    for right_index in range(1, len(a)):
        right = a[right_index]
        for left_index in range(right_index):
            difference = right - a[left_index]
            if difference < h:
                counts[difference] += 1

    d_weight = 0
    q_weight = 0
    weighted_pairs = 0
    for difference in range(1, h):
        count = counts[difference]
        if count > 2:
            raise AssertionError("admissibility failed to force nu(d) <= 2")
        weight = h - difference
        weighted_pairs += weight * count
        if count == 2:
            d_weight += weight
        elif count == 0:
            q_weight += weight
    z = d_weight - q_weight
    if h * h + 2 * z != h + 2 * weighted_pairs:
        raise AssertionError("centered identity failed")

    m = h + sum(min(h, right - left) for left, right in zip(a, a[1:]))
    gap_truncation = sum(
        max(0, right - left - h) for left, right in zip(a, a[1:])
    )
    ambient_holes = n + h - 1 - m
    k = len(a)
    margin6 = (
        6 * m * (h * h + 2 * z)
        - 8 * n * h * h
        - 9 * h * h * h
        - 9 * n * (k - 1) * h
    )
    raw_over_four_thirds = 3 * m * (h * h + 2 * z) - 4 * n * h * h
    coefficient_denominator = 3 * h * (h * h + n * (k - 1))
    coefficient = Fraction(raw_over_four_thirds, coefficient_denominator)
    lg33_margin = (
        8 * n * z
        - 12 * h * h * ambient_holes
        + 3 * h * h * h
        - 12 * h * h
        - 9 * n * (k - 1) * h
    )
    return {
        "lower_core": list(lower),
        "A": list(a),
        "N": n,
        "k": k,
        "exceptional_sum": exceptional_sum,
        "exceptional_multiplicity": exceptional_multiplicity,
        "H": h,
        "M": m,
        "D": d_weight,
        "Q": q_weight,
        "Z": z,
        "weighted_pair_overlap": weighted_pairs,
        "gap_truncation": gap_truncation,
        "ambient_holes": ambient_holes,
        "required_coefficient": f"{coefficient.numerator}/{coefficient.denominator}",
        "required_coefficient_decimal": float(coefficient),
        "required_coefficient_numerator": coefficient.numerator,
        "required_coefficient_denominator": coefficient.denominator,
        "c20_margin6": margin6,
        "lg33_margin": lg33_margin,
    }


def coefficient(record: dict[str, Any]) -> Fraction:
    return Fraction(
        record["required_coefficient_numerator"],
        record["required_coefficient_denominator"],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--center", type=int, default=583)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p33/reflected_neighborhood_e583.json"),
    )
    args = parser.parse_args()

    seed = tuple(DEFAULT_SEED)
    seed_record = metrics(seed, args.center)
    if seed_record is None:
        raise AssertionError("seed is not admissible")
    attempted = 0
    admissible = 0
    better = 0
    failures: list[dict[str, Any]] = []
    best = seed_record
    upper = (args.center - 1) // 2

    for index in range(1, len(seed)):
        for replacement in range(2, upper + 1):
            if replacement in seed or replacement == seed[index]:
                continue
            attempted += 1
            candidate = list(seed)
            candidate[index] = replacement
            lower = tuple(sorted(candidate))
            record = metrics(lower, args.center)
            if record is None:
                continue
            admissible += 1
            if coefficient(record) > coefficient(seed_record):
                better += 1
            if coefficient(record) > coefficient(best):
                best = record
            if record["c20_margin6"] > 0:
                failures.append(record)

    result = {
        "arithmetic": "integer/rational",
        "domain": (
            "all one-point replacements of non-endpoint lower-core entries "
            f"inside [1,{upper}], center={args.center}"
        ),
        "attempted": attempted,
        "admissible": admissible,
        "better_than_seed": better,
        "c20_failure_count": len(failures),
        "seed": seed_record,
        "best": best,
        "failures": failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "failures"}))


if __name__ == "__main__":
    main()
