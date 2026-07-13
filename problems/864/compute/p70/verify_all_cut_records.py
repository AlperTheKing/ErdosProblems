#!/usr/bin/env python3
"""Independent exact verifier for selected Ruzsa all-cut records."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


def ruzsa_lift(p: int, primitive_root: int, e: int) -> tuple[int, ...]:
    b = p - 1
    values = []
    for index in range(b):
        residue_p = e * (pow(primitive_root, index, p) - 1) % p
        quotient = (index - residue_p) % b
        values.append(residue_p + p * quotient)
    values.sort()
    if len(values) != b or len(set(values)) != b or values[0] != 0:
        raise AssertionError("invalid CRT lift")
    return tuple(values)


def supports(values: tuple[int, ...]) -> tuple[set[int], set[int]]:
    sums = {
        values[i] + values[j]
        for j in range(len(values))
        for i in range(j + 1)
    }
    differences = {
        values[j] - values[i]
        for j in range(len(values))
        for i in range(j)
    }
    b = len(values)
    if len(sums) != b * (b + 1) // 2:
        raise AssertionError("integer Sidon check failed")
    if len(differences) != b * (b - 1) // 2:
        raise AssertionError("positive-difference uniqueness failed")
    return sums, differences


def represented_bits(sums: set[int], differences: set[int]) -> int:
    sum_bits = 0
    for value in sums:
        sum_bits |= 1 << value
    result = 0
    for difference in differences:
        result |= sum_bits << difference
    return result


def verify_reflection(values: tuple[int, ...], center: int) -> None:
    reflected = tuple(sorted(set(values) | {center - value for value in values}))
    if len(reflected) != 2 * len(values):
        raise AssertionError("reflected blocks are not disjoint")
    counts: Counter[int] = Counter()
    for j, right in enumerate(reflected):
        for left in reflected[: j + 1]:
            counts[left + right] += 1
    repeated = {value: count for value, count in counts.items() if count >= 2}
    if repeated != {center: len(values)}:
        raise AssertionError(("reflected census failed", repeated))


def verify_record(record: dict) -> dict:
    p = int(record["p"])
    b = int(record["size"])
    if b != p - 1:
        raise AssertionError("unexpected Ruzsa size")
    values = ruzsa_lift(p, int(record["primitive_root"]), int(record["base_exponential"]))
    if values[-1] != int(record["span"]):
        raise AssertionError("span mismatch")
    sums, differences = supports(values)
    if len(sums) != int(record["literal_unordered_sum_support"]):
        raise AssertionError("sum-support mismatch")
    if len(differences) != int(record["positive_difference_support"]):
        raise AssertionError("difference-support mismatch")

    center = int(record["first_center_below_3size2"])
    start = 2 * values[-1] + 1
    if center < start or center >= 3 * b * b:
        raise AssertionError("center outside the searched interval")
    occupied = represented_bits(sums, differences)
    if (occupied >> center) & 1:
        raise AssertionError("claimed center is represented")
    if center > start:
        interval_mask = ((1 << (center - start)) - 1) << start
        if occupied & interval_mask != interval_mask:
            first_missing = next(
                value for value in range(start, center) if not ((occupied >> value) & 1)
            )
            raise AssertionError(("earlier center is missing", first_missing))

    verify_reflection(values, center)
    exact_ratio = Fraction(center, b * b)
    if exact_ratio != Fraction(record["center_over_size2"]):
        raise AssertionError("ratio mismatch")
    return {
        "p": p,
        "cuts": p - 1,
        "e": int(record["base_exponential"]),
        "span": values[-1],
        "center": center,
        "ratio": str(exact_ratio),
        "numerator_gap_below_3": 3 * b * b - center,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    verified = []
    for artifact in args.artifacts:
        data = json.loads(artifact.read_text(encoding="utf-8"))
        records = data["records"]
        keyed = sorted(records, key=lambda record: Fraction(record["center_over_size2"]))
        for label, record in (("best", keyed[0]), ("worst", keyed[-1])):
            result = verify_record(record)
            result["kind"] = label
            result["source"] = str(artifact)
            verified.append(result)

    payload = {"arithmetic": "exact integers and fractions", "verified": verified}
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)


if __name__ == "__main__":
    main()
