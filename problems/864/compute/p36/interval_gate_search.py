#!/usr/bin/env python3
"""Exact finite gates for interval-degree formulations of centered C20.

All arithmetic used for decisions is integral.  Sets are endpoint-normalized
subsets of [0, N-1].  The three nested structural classes are:

* ``difference_two``: every positive difference has multiplicity at most 2;
* ``coherent``: duplicated differences all have the same reflection center;
* ``admissible``: at most one unordered sum (diagonals included) is repeated.

The coherent condition is checked independently from sum admissibility.  The
audit therefore also tests their expected equivalence on the finite domain.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


def ceil_cuberoot_square(n: int) -> int:
    target = n * n
    lo, hi = 1, n
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid * mid >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


@dataclass(frozen=True)
class Structure:
    difference_two: bool
    coherent: bool
    admissible: bool
    duplicate_centers: tuple[int, ...]
    repeated_sums: tuple[int, ...]


def classify(a: tuple[int, ...]) -> Structure:
    difference_reps: dict[int, list[tuple[int, int]]] = {}
    for right_index in range(1, len(a)):
        right = a[right_index]
        for left_index in range(right_index):
            left = a[left_index]
            difference_reps.setdefault(right - left, []).append((right, left))

    difference_two = all(len(reps) <= 2 for reps in difference_reps.values())
    centers: list[int] = []
    if difference_two:
        for reps in difference_reps.values():
            if len(reps) == 2:
                (right_1, left_1), (right_2, left_2) = reps
                center_1 = right_1 + left_2
                center_2 = right_2 + left_1
                if center_1 != center_2:
                    raise AssertionError("equal differences gave unequal cross sums")
                centers.append(center_1)
    duplicate_centers = tuple(sorted(set(centers)))
    coherent = difference_two and len(duplicate_centers) <= 1

    sum_counts: dict[int, int] = {}
    for right_index, right in enumerate(a):
        for left in a[: right_index + 1]:
            pair_sum = left + right
            sum_counts[pair_sum] = sum_counts.get(pair_sum, 0) + 1
    repeated_sums = tuple(sorted(value for value, count in sum_counts.items() if count >= 2))
    admissible = len(repeated_sums) <= 1

    return Structure(
        difference_two=difference_two,
        coherent=coherent,
        admissible=admissible,
        duplicate_centers=duplicate_centers,
        repeated_sums=repeated_sums,
    )


def profile(a: tuple[int, ...], n: int) -> dict[str, int | list[int]]:
    h = ceil_cuberoot_square(n)
    counts = [0] * h
    weighted_pairs = 0
    for right_index in range(1, len(a)):
        right = a[right_index]
        for left in a[:right_index]:
            difference = right - left
            if difference < h:
                counts[difference] += 1
                weighted_pairs += h - difference

    d_weight = sum(
        h - difference
        for difference in range(1, h)
        if counts[difference] == 2
    )
    q_weight = sum(
        h - difference
        for difference in range(1, h)
        if counts[difference] == 0
    )
    z = weighted_pairs - h * (h - 1) // 2
    gaps = [right - left for left, right in zip(a, a[1:])]
    m = h + sum(min(h, gap) for gap in gaps)
    g = n + h - 1 - m
    k = len(a)
    s = h * h + 2 * z

    if s != h + 2 * weighted_pairs:
        raise AssertionError("centered second-moment identity failed")
    if max(counts, default=0) <= 2 and z != d_weight - q_weight:
        raise AssertionError("D-Q identity failed in the difference-two class")
    if g != sum(max(0, gap - h) for gap in gaps):
        raise AssertionError("endpoint-normalized gap identity failed")

    # Positive means failure.  This is 6*N*H^2 times the C20 excess.
    c20_margin = (
        6 * m * s
        - 8 * n * h * h
        - 9 * h * h * h
        - 9 * n * (k - 1) * h
    )
    # Positive means failure of the P33 sufficient linear gap inequality.
    lg33_margin = (
        8 * n * z
        - 12 * h * h * g
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
        "G": g,
        "W": weighted_pairs,
        "D": d_weight,
        "Q": q_weight,
        "Z": z,
        "S": s,
        "max_interval_degree": max(
            sum(1 for value in a if start <= value < start + h)
            for start in range(-(h - 1), n)
        ),
        "c20_margin": c20_margin,
        "lg33_margin": lg33_margin,
        "lg33_domain": int(3 * m >= 2 * n),
    }


def endpoint_sets(n: int) -> Iterable[tuple[int, ...]]:
    interior_count = n - 2
    for mask in range(1 << interior_count):
        yield (0,) + tuple(
            index + 1 for index in range(interior_count) if mask & (1 << index)
        ) + (n - 1,)


def audit(max_n: int) -> dict[str, object]:
    classes = ("difference_two", "coherent", "admissible")
    counts = {name: 0 for name in classes}
    c20_failures = {name: 0 for name in classes}
    lg33_failures = {name: 0 for name in classes}
    first_c20_failure: dict[str, dict[str, object] | None] = {
        name: None for name in classes
    }
    first_lg33_failure: dict[str, dict[str, object] | None] = {
        name: None for name in classes
    }
    equivalence_failures: list[dict[str, object]] = []
    total = 0

    for n in range(2, max_n + 1):
        for a in endpoint_sets(n):
            total += 1
            structure = classify(a)
            if structure.coherent != structure.admissible:
                equivalence_failures.append(
                    {
                        "A": list(a),
                        "N": n,
                        "coherent": structure.coherent,
                        "admissible": structure.admissible,
                        "duplicate_centers": list(structure.duplicate_centers),
                        "repeated_sums": list(structure.repeated_sums),
                    }
                )

            row: dict[str, object] | None = None
            for name in classes:
                if not getattr(structure, name):
                    continue
                counts[name] += 1
                if row is None:
                    row = profile(a, n)
                    row["duplicate_centers"] = list(structure.duplicate_centers)
                    row["repeated_sums"] = list(structure.repeated_sums)
                if int(row["c20_margin"]) > 0:
                    c20_failures[name] += 1
                    if first_c20_failure[name] is None:
                        first_c20_failure[name] = row.copy()
                if int(row["lg33_domain"]) and int(row["lg33_margin"]) > 0:
                    lg33_failures[name] += 1
                    if first_lg33_failure[name] is None:
                        first_lg33_failure[name] = row.copy()

    return {
        "arithmetic": "integer",
        "domain": f"endpoint-normalized subsets of [0,N-1], 2 <= N <= {max_n}",
        "total_sets": total,
        "class_counts": counts,
        "c20_failure_counts": c20_failures,
        "lg33_failure_counts": lg33_failures,
        "first_c20_failure": first_c20_failure,
        "first_lg33_failure": first_lg33_failure,
        "coherent_admissible_equivalence_failure_count": len(equivalence_failures),
        "first_equivalence_failure": equivalence_failures[:1],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=22)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p36/interval_gate_N22.json"),
    )
    args = parser.parse_args()
    result = audit(args.max_n)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
