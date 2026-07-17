#!/usr/bin/env python3
"""Independent verifier for C103 exact JSON artifacts."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path


def ratio_less(a_num: int, a_den: int, b_num: int, b_den: int) -> bool:
    return a_num * b_den < b_num * a_den


def divisors_below_sqrt(n: int):
    for left in range(2, math.isqrt(n) + 1):
        if n % left == 0 and left < n // left:
            yield left


def replay(limit: int) -> dict:
    member = bytearray(limit + 1)
    member[2] = member[3] = 1
    min_depth = [0] * (limit + 1)
    min_leaves = [0] * (limit + 1)
    min_leaves[2] = min_leaves[3] = 1
    depth_histogram = Counter({0: 2})
    leaf_histogram = Counter({1: 2})

    count = 2
    small_root_count = 0
    no_small_root_count = 0
    multiple_root_count = 0
    total_root_witnesses = 0
    first_without_small_root = 0
    checkpoints = []
    powers_two = []
    next_decade = 10
    next_power_two = 16

    bands = []
    band_lo = 10
    band_hi = min(99, limit)
    band_min = None
    band_max = None

    for value in range(4, limit + 1):
        witnesses = []
        for left in divisors_below_sqrt(value + 1):
            right = (value + 1) // left
            if member[left] and member[right]:
                witnesses.append((left, right))
        if witnesses:
            member[value] = 1
            min_depth[value] = min(
                1 + max(min_depth[left], min_depth[right])
                for left, right in witnesses
            )
            min_leaves[value] = min(
                min_leaves[left] + min_leaves[right]
                for left, right in witnesses
            )
            count += 1
            depth_histogram[min_depth[value]] += 1
            leaf_histogram[min_leaves[value]] += 1
            total_root_witnesses += len(witnesses)
            multiple_root_count += len(witnesses) >= 2
            if any(left in (2, 3, 5) for left, _ in witnesses):
                small_root_count += 1
            else:
                no_small_root_count += 1
                if first_without_small_root == 0:
                    first_without_small_root = value

        if value == next_decade:
            checkpoints.append([value, count])
            next_decade *= 10
        if value == next_power_two:
            powers_two.append([value, count])
            next_power_two *= 2

        if value >= band_lo:
            if band_min is None or ratio_less(count, value, band_min[1], band_min[0]):
                band_min = [value, count]
            if band_max is None or ratio_less(band_max[1], band_max[0], count, value):
                band_max = [value, count]
            if value == band_hi:
                bands.append({"range": [band_lo, band_hi], "min": band_min, "max": band_max})
                if value != limit:
                    band_lo = value + 1
                    band_hi = min(limit, band_lo * 10 - 1)
                    band_min = None
                    band_max = None

    if not checkpoints or checkpoints[-1][0] != limit:
        checkpoints.append([limit, count])
    if not powers_two or powers_two[-1][0] != limit:
        powers_two.append([limit, count])
    return {
        "limit": limit,
        "count": count,
        "density": [count, limit],
        "max_min_depth": max(depth_histogram),
        "max_min_leaves": max(leaf_histogram),
        "nonseed_members": count - 2,
        "members_with_root_factor_2_3_or_5": small_root_count,
        "members_without_root_factor_2_3_or_5": no_small_root_count,
        "first_without_root_factor_2_3_or_5": first_without_small_root,
        "members_with_multiple_root_witnesses": multiple_root_count,
        "total_root_witnesses": total_root_witnesses,
        "min_depth_histogram": [[key, depth_histogram[key]] for key in sorted(depth_histogram)],
        "min_leaf_histogram": [[key, leaf_histogram[key]] for key in sorted(leaf_histogram)],
        "checkpoints": checkpoints,
        "power_two_checkpoints": powers_two,
        "decade_density_extrema": bands,
    }


def verify_probe(path: Path) -> None:
    observed = json.loads(path.read_text(encoding="ascii"))
    expected = replay(observed["limit"])
    for key, value in expected.items():
        if observed[key] != value:
            raise AssertionError((key, observed[key], value))


def verify_entropy(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="ascii"))
    counts = tuple(payload["type_counts_per_block"])
    slopes = tuple(payload["slopes"])
    block_length = sum(counts)
    q = math.prod(slope**count for slope, count in zip(slopes, counts))
    assert int(payload["Q"]) == q
    assert int(payload["entropy_base_over_Q"][0]) == 31**31
    assert int(payload["entropy_base_over_Q"][1]) == 30**31
    first = None
    for row in payload["rows"]:
        m = row["m"]
        words = math.factorial(block_length * m) // math.prod(
            math.factorial(count * m) for count in counts
        )
        cutoff = 9 * q**m
        assert int(row["words"]) == words
        assert int(row["cutoff"]) == cutoff
        assert row["words_gt_cutoff"] == (words > cutoff)
        if first is None and words > cutoff:
            first = m
    assert payload["first_m_with_exact_word_count_gt_9Q^m"] == first
    certificate = payload["all_m_ge_15_certificate"]
    start = certificate["start_m"]
    start_linear = 31 * start + 1
    next_linear = 31 * (start + 1) + 1
    assert int(certificate["base_case"]["lhs"]) == 31 ** (31 * start)
    assert int(certificate["base_case"]["rhs"]) == 9 * start_linear**2 * 30 ** (31 * start)
    assert certificate["base_case"]["holds"]
    assert int(certificate["monotone_step_at_start"]["lhs"]) == 31**31 * start_linear**2
    assert int(certificate["monotone_step_at_start"]["rhs"]) == 30**31 * next_linear**2
    assert certificate["monotone_step_at_start"]["holds"]


def main() -> None:
    sys.set_int_max_str_digits(0)
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--entropy", type=Path, required=True)
    args = parser.parse_args()
    verify_probe(args.probe)
    verify_entropy(args.entropy)
    print("verified probe and entropy artifacts")


if __name__ == "__main__":
    main()
