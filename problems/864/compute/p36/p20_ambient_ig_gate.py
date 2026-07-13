#!/usr/bin/env python3
"""Audit IG(0), IG(1), IG(2), and C20 on all ambient-N P20 samples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from interval_gate_search import ceil_cuberoot_square, classify


def ambient_profile(sample: dict[str, Any]) -> dict[str, Any]:
    a = tuple(int(value) for value in sample["A"])
    n = int(sample["N"])
    if not a or not (1 <= a[0] <= a[-1] <= n):
        raise AssertionError(f"invalid ambient sample {sample['sample_id']}")
    h = ceil_cuberoot_square(n)
    k = len(a)
    counts = [0] * h
    weighted_pairs = 0
    for right_index in range(1, k):
        right = a[right_index]
        for left in a[:right_index]:
            difference = right - left
            if difference < h:
                counts[difference] += 1
                weighted_pairs += h - difference

    if max(counts, default=0) > 2:
        raise AssertionError(f"difference multiplicity above two: {sample['sample_id']}")
    z = weighted_pairs - h * (h - 1) // 2
    d_weight = sum(h - d for d in range(1, h) if counts[d] == 2)
    q_weight = sum(h - d for d in range(1, h) if counts[d] == 0)
    if z != d_weight - q_weight:
        raise AssertionError(f"centered identity failed: {sample['sample_id']}")

    gaps = [right - left for left, right in zip(a, a[1:])]
    m = h + sum(min(h, gap) for gap in gaps)
    g = n + h - 1 - m
    ambient_gap_certificate = (
        (a[0] - 1)
        + (n - a[-1])
        + sum(max(0, gap - h) for gap in gaps)
    )
    if g != ambient_gap_certificate:
        raise AssertionError(f"ambient gap identity failed: {sample['sample_id']}")

    s = h * h + 2 * z
    c20_margin = (
        6 * m * s
        - 8 * n * h * h
        - 9 * h * h * h
        - 9 * n * (k - 1) * h
    )
    result = {
        "sample_id": sample["sample_id"],
        "kind": sample["kind"],
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
        "c20_margin": c20_margin,
    }
    for coefficient in range(3):
        result[f"ig{coefficient}_margin"] = (
            2 * n * z
            - 3 * h * h * g
            - coefficient * n * (k - 1) * h
        )
    return result


def audit(path: Path) -> dict[str, Any]:
    counts = {"samples": 0, "admissibility_failures": 0, "c20_failures": 0}
    failures = {str(coefficient): 0 for coefficient in range(3)}
    first_failure: dict[str, dict[str, Any] | None] = {
        str(coefficient): None for coefficient in range(3)
    }
    largest_margin: dict[str, dict[str, Any] | None] = {
        str(coefficient): None for coefficient in range(3)
    }

    for line in path.read_text(encoding="utf-8").splitlines():
        sample = json.loads(line)
        row = ambient_profile(sample)
        counts["samples"] += 1
        shifted = tuple(value - row["A"][0] for value in row["A"])
        if not classify(shifted).admissible:
            counts["admissibility_failures"] += 1
        if int(row["c20_margin"]) > 0:
            counts["c20_failures"] += 1
        for coefficient in range(3):
            key = str(coefficient)
            margin_key = f"ig{coefficient}_margin"
            margin = int(row[margin_key])
            if largest_margin[key] is None or margin > int(
                largest_margin[key][margin_key]
            ):
                largest_margin[key] = row.copy()
            if margin > 0:
                failures[key] += 1
                if first_failure[key] is None:
                    first_failure[key] = row.copy()

    return {
        "arithmetic": "integer",
        "counts": counts,
        "IG_failure_counts": failures,
        "first_IG_failure": first_failure,
        "largest_IG_margin": largest_margin,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--samples",
        type=Path,
        default=Path("problems/864/compute/p20/results/samples.jsonl"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p36/p20_ambient_ig_gate.json"),
    )
    args = parser.parse_args()
    result = audit(args.samples)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
