#!/usr/bin/env python3
"""Centered-C20 audit of the fresh P30 p=257 Ruzsa reflections."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

P30_DIR = Path("problems/864/compute/p30")
sys.path.insert(0, str(P30_DIR))
from scan_canonical_cuts import ruzsa_residues  # noqa: E402


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


def audit_record(source: dict[str, Any], residues: tuple[int, ...]) -> dict[str, Any]:
    p = int(source["p"])
    base = int(source["cut_base"])
    modulus = int(source["modulus"])
    center = int(source["first_center_below_3size2"])
    lower = tuple(sorted((value - base) % modulus for value in residues))
    if lower[0] != 0 or lower[-1] != int(source["span"]):
        raise AssertionError("reconstructed cut does not match recorded span")
    reflected_zero = tuple(sorted(set(lower) | {center - value for value in lower}))
    if len(reflected_zero) != 2 * len(lower):
        raise AssertionError("reflected blocks overlap")
    a = tuple(value + 1 for value in reflected_zero)
    n = center + 1
    k = len(a)

    sum_counts = Counter(
        a[left_index] + a[right_index]
        for left_index in range(k)
        for right_index in range(left_index, k)
    )
    repeated = sorted((value, count) for value, count in sum_counts.items() if count > 1)
    expected_repeated = [(center + 2, len(lower))]
    if repeated != expected_repeated:
        raise AssertionError((source["base_index"], repeated[:10], expected_repeated))

    h = ceil_cuberoot_square(n)
    difference_counts = [0] * h
    for right_index in range(1, k):
        right = a[right_index]
        for left_index in range(right_index):
            difference = right - a[left_index]
            if difference < h:
                difference_counts[difference] += 1

    d_weight = 0
    q_weight = 0
    weighted_pairs = 0
    for difference in range(1, h):
        count = difference_counts[difference]
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
    truncation = sum(max(0, right - left - h) for left, right in zip(a, a[1:]))
    ambient_holes = n + h - 1 - m
    if truncation != ambient_holes:
        raise AssertionError("endpoint-normalized gap identity failed")

    c20_margin6 = (
        6 * m * (h * h + 2 * z)
        - 8 * n * h * h
        - 9 * h * h * h
        - 9 * n * (k - 1) * h
    )
    raw_over_four_thirds = 3 * m * (h * h + 2 * z) - 4 * n * h * h
    coefficient_denominator = 3 * h * (h * h + n * (k - 1))
    required = Fraction(raw_over_four_thirds, coefficient_denominator)
    lg33_margin = (
        8 * n * z
        - 12 * h * h * ambient_holes
        + 3 * h * h * h
        - 12 * h * h
        - 9 * n * (k - 1) * h
    )
    return {
        "base_index": source["base_index"],
        "cut_base": base,
        "center": center,
        "span": source["span"],
        "N": n,
        "k": k,
        "H": h,
        "M": m,
        "D": d_weight,
        "Q": q_weight,
        "Z": z,
        "weighted_pair_overlap": weighted_pairs,
        "T": truncation,
        "required_coefficient": f"{required.numerator}/{required.denominator}",
        "required_coefficient_decimal": float(required),
        "required_coefficient_numerator": required.numerator,
        "required_coefficient_denominator": required.denominator,
        "c20_margin6": c20_margin6,
        "lg33_margin": lg33_margin,
    }


def coefficient(record: dict[str, Any]) -> Fraction:
    return Fraction(
        record["required_coefficient_numerator"],
        record["required_coefficient_denominator"],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=P30_DIR / "all_cuts_p257.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p33/audit_p30_p257.json"),
    )
    args = parser.parse_args()

    source = json.loads(args.input.read_text(encoding="utf-8"))
    records = source["records"]
    if not records:
        raise AssertionError("P30 input has no records")
    residue_cache: dict[tuple[int, int], tuple[int, ...]] = {}
    audited: list[dict[str, Any]] = []
    for record in records:
        key = (int(record["p"]), int(record["primitive_root"]))
        if key not in residue_cache:
            residue_cache[key] = ruzsa_residues(*key)
        audited.append(audit_record(record, residue_cache[key]))
    strongest = max(audited, key=coefficient)
    result = {
        "arithmetic": "integer/rational",
        "input": str(args.input).replace("\\", "/"),
        "record_count": len(audited),
        "admissibility_check_count": len(audited),
        "centered_check_count": len(audited),
        "c20_failure_count": sum(row["c20_margin6"] > 0 for row in audited),
        "lg33_failure_count": sum(row["lg33_margin"] > 0 for row in audited),
        "strongest": strongest,
        "records": audited,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "records"}))


if __name__ == "__main__":
    main()
