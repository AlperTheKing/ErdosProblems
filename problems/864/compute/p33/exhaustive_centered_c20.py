#!/usr/bin/env python3
"""Exact endpoint-normalized search for centered C20 and LG33."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


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


def record_for(a: tuple[int, ...], n: int) -> dict[str, Any]:
    h = ceil_cuberoot_square(n)
    k = len(a)
    counts = [0] * h
    for right_index in range(1, k):
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
            raise AssertionError("admissible set has difference multiplicity above two")
        weight = h - difference
        weighted_pairs += weight * count
        if count == 2:
            d_weight += weight
        elif count == 0:
            q_weight += weight

    z = d_weight - q_weight
    if h * h + 2 * z != h + 2 * weighted_pairs:
        raise AssertionError("centered identity failed")

    gaps = [right - left for left, right in zip(a, a[1:])]
    m = h + sum(min(h, gap) for gap in gaps)
    truncation = sum(max(0, gap - h) for gap in gaps)
    if truncation != n + h - 1 - m:
        raise AssertionError("endpoint-normalized gap identity failed")

    c20_margin6 = (
        6 * m * (h * h + 2 * z)
        - 8 * n * h * h
        - 9 * h * h * h
        - 9 * n * (k - 1) * h
    )
    raw_over_four_thirds = 3 * m * (h * h + 2 * z) - 4 * n * h * h
    correction_denominator = 3 * h * (h * h + n * (k - 1))
    required_coefficient = Fraction(raw_over_four_thirds, correction_denominator)

    lg33_margin = (
        8 * n * z
        - 12 * h * h * truncation
        + 3 * h * h * h
        - 12 * h * h
        - 9 * n * (k - 1) * h
    )

    return {
        "A": list(a),
        "N": n,
        "k": k,
        "H": h,
        "M": m,
        "D": d_weight,
        "Q": q_weight,
        "Z": z,
        "T": truncation,
        "weighted_pair_overlap": weighted_pairs,
        "required_coefficient": (
            f"{required_coefficient.numerator}/{required_coefficient.denominator}"
        ),
        "required_coefficient_numerator": required_coefficient.numerator,
        "required_coefficient_denominator": required_coefficient.denominator,
        "c20_margin6": c20_margin6,
        "lg33_margin": lg33_margin,
        "lg33_in_domain": 3 * m >= 2 * n,
    }


def better_fraction(candidate: dict[str, Any], current: dict[str, Any] | None) -> bool:
    if current is None:
        return True
    left = (
        candidate["required_coefficient_numerator"]
        * current["required_coefficient_denominator"]
    )
    right = (
        current["required_coefficient_numerator"]
        * candidate["required_coefficient_denominator"]
    )
    return left > right


def search_n(n: int) -> dict[str, Any]:
    if n < 2:
        raise ValueError("N must be at least two")

    a = [0]
    sum_counts: dict[int, int] = {0: 1}
    admissible_count = 0
    pruned_additions = 0
    c20_failure_count = 0
    lg33_failure_count = 0
    best_c20: dict[str, Any] | None = None
    best_lg33: dict[str, Any] | None = None

    def evaluate_leaf() -> None:
        nonlocal admissible_count, c20_failure_count, lg33_failure_count
        nonlocal best_c20, best_lg33

        admissible_count += 1
        record = record_for(tuple(a), n)
        if record["c20_margin6"] > 0:
            c20_failure_count += 1
        if record["lg33_in_domain"] and record["lg33_margin"] > 0:
            lg33_failure_count += 1
        if better_fraction(record, best_c20):
            best_c20 = record
        if record["lg33_in_domain"] and (
            best_lg33 is None or record["lg33_margin"] > best_lg33["lg33_margin"]
        ):
            best_lg33 = record

    def try_add(x: int, repeated_labels: int, continuation: Any) -> None:
        nonlocal pruned_additions
        changed: list[tuple[int, int]] = []
        new_repeated = repeated_labels
        valid = True
        for old_point in (*a, x):
            pair_sum = x + old_point
            old_count = sum_counts.get(pair_sum, 0)
            sum_counts[pair_sum] = old_count + 1
            changed.append((pair_sum, old_count))
            if old_count == 1:
                new_repeated += 1
            if new_repeated > 1:
                valid = False
                break
        if valid:
            a.append(x)
            continuation(new_repeated)
            a.pop()
        else:
            pruned_additions += 1
        for pair_sum, old_count in reversed(changed):
            if old_count:
                sum_counts[pair_sum] = old_count
            else:
                del sum_counts[pair_sum]

    def recurse(x: int, repeated_labels: int) -> None:
        if x == n - 1:
            try_add(x, repeated_labels, lambda _: evaluate_leaf())
            return

        recurse(x + 1, repeated_labels)
        try_add(x, repeated_labels, lambda value: recurse(x + 1, value))

    recurse(1, 0)
    if best_c20 is None or best_lg33 is None:
        raise AssertionError("search domain unexpectedly empty")

    return {
        "N": n,
        "total_endpoint_normalized_subsets": 1 << (n - 2),
        "admissible_count": admissible_count,
        "pruned_additions": pruned_additions,
        "c20_failure_count": c20_failure_count,
        "lg33_failure_count": lg33_failure_count,
        "best_c20": best_c20,
        "best_lg33": best_lg33,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=2)
    parser.add_argument("--max-n", type=int, default=24)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p33/exhaustive_N24.json"),
    )
    args = parser.parse_args()

    results = [search_n(n) for n in range(args.min_n, args.max_n + 1)]
    best = max(
        (row["best_c20"] for row in results),
        key=lambda row: Fraction(
            row["required_coefficient_numerator"],
            row["required_coefficient_denominator"],
        ),
    )
    summary = {
        "arithmetic": "integer/rational",
        "domain": (
            f"all A subset [0,N-1] with endpoints included, "
            f"{args.min_n} <= N <= {args.max_n}"
        ),
        "total_subset_count": sum(
            row["total_endpoint_normalized_subsets"] for row in results
        ),
        "admissible_count": sum(row["admissible_count"] for row in results),
        "c20_failure_count": sum(row["c20_failure_count"] for row in results),
        "lg33_failure_count": sum(row["lg33_failure_count"] for row in results),
        "strongest_required_coefficient": best,
        "by_N": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "by_N"}))


if __name__ == "__main__":
    main()
