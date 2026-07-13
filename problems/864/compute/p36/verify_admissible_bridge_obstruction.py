#!/usr/bin/env python3
"""Exact admissible obstruction to a coefficient-2 C20 gap bridge."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any


sys.path.insert(0, str(Path(__file__).resolve().parent))
from search_interval_lemmas import compute_metrics, difference_counts  # noqa: E402


DEFAULT_SAMPLE_ID = "ruzsa-9ab2ac138632"


def unordered_sum_counts(points: tuple[int, ...]) -> Counter[int]:
    counts: Counter[int] = Counter()
    for index, left in enumerate(points):
        for right in points[index:]:
            counts[left + right] += 1
    return counts


def load_sample(path: Path, sample_id: str) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("sample_id") == sample_id:
                return record
    raise KeyError(sample_id)


def audit(record: dict[str, Any]) -> dict[str, Any]:
    points = tuple(record["A"])
    n = int(record["N"])
    sums = unordered_sum_counts(points)
    repeated = tuple(sorted((value, count) for value, count in sums.items() if count >= 2))
    if len(repeated) != 1:
        raise AssertionError("sample is not literally 864-admissible")
    sigma, exceptional_multiplicity = repeated[0]
    if sigma != record["exceptional_sum"]:
        raise AssertionError("archived exceptional sum mismatch")

    reflected_core = tuple(value for value in points if sigma - value in points)
    residual = tuple(value for value in points if sigma - value not in points)
    if reflected_core != points or residual:
        raise AssertionError("sample is not a fully reflected core")
    midpoint = sigma // 2 if sigma % 2 == 0 and sigma // 2 in points else None
    lower = tuple(value for value in points if 2 * value < sigma)
    upper = tuple(value for value in points if 2 * value > sigma)
    if midpoint is not None or len(lower) != len(upper):
        raise AssertionError("unexpected midpoint or unbalanced reflection")

    lower_sums = unordered_sum_counts(lower)
    if max(lower_sums.values(), default=0) != 1:
        raise AssertionError("lower half is not Sidon including diagonals")
    lower_differences = difference_counts(lower)
    signed_forbidden = {
        pair_sum + difference
        for pair_sum in lower_sums
        for difference in lower_differences
    }
    if sigma in signed_forbidden:
        raise AssertionError("signed-ruler hole condition failed")

    metrics = compute_metrics(points, n)
    h = metrics.h
    central_gap = upper[0] - lower[-1]
    if central_gap < h:
        raise AssertionError("the two reflected halves are not H-separated")

    lower_m = h + sum(
        min(h, right - left) for left, right in zip(lower, lower[1:])
    )
    lower_w = sum(
        (h - difference) * multiplicity
        for difference, multiplicity in lower_differences.items()
        if difference < h
    )
    if metrics.m_h != 2 * lower_m:
        raise AssertionError("cross-free support identity failed")
    if metrics.w_h != 2 * lower_w:
        raise AssertionError("cross-free overlap identity failed")
    if metrics.z_h != 2 * lower_w - h * (h - 1) // 2:
        raise AssertionError("cross-free centered identity failed")

    bridge_numerator = (
        8 * n * metrics.z_h
        - 12 * h * h * metrics.ambient_holes
        + 3 * h**3
        - 12 * h * h
    )
    cardinality_unit = n * (metrics.k - 1) * h
    coefficient_two_margin = bridge_numerator - 8 * cardinality_unit
    lg33_margin = bridge_numerator - 9 * cardinality_unit
    if coefficient_two_margin <= 0 or lg33_margin > 0:
        raise AssertionError("expected coefficient separation did not occur")
    required_coefficient = Fraction(bridge_numerator, 4 * cardinality_unit)

    lhs = Fraction(metrics.m_h, n) * (
        1 + Fraction(2 * metrics.z_h, h * h)
    )
    rhs = Fraction(4, 3) + Fraction(3, 2) * (
        Fraction(h, n) + Fraction(metrics.k - 1, h)
    )
    if lhs - rhs != Fraction(metrics.c20_margin, 6 * n * h * h):
        raise AssertionError("C20 rational/cleared mismatch")
    if metrics.c20_margin > 0:
        raise AssertionError("this bridge obstruction is not a C20 counterexample")

    return {
        "sample_id": record["sample_id"],
        "admissible": True,
        "exceptional_sum": sigma,
        "exceptional_multiplicity": exceptional_multiplicity,
        "fully_reflected": True,
        "midpoint": midpoint,
        "residual_size": len(residual),
        "lower_half": list(lower),
        "lower_half_size": len(lower),
        "lower_half_M_H": lower_m,
        "lower_half_W_H": lower_w,
        "central_gap": central_gap,
        "cross_free_at_H": True,
        "signed_ruler_hole_verified": True,
        "required_cardinality_coefficient": (
            f"{required_coefficient.numerator}/{required_coefficient.denominator}"
        ),
        "coefficient_two_cleared_margin": coefficient_two_margin,
        "lg33_cleared_margin": lg33_margin,
        "c20_lhs": f"{lhs.numerator}/{lhs.denominator}",
        "c20_rhs": f"{rhs.numerator}/{rhs.denominator}",
        "c20_excess": f"{(lhs - rhs).numerator}/{(lhs - rhs).denominator}",
        **metrics.record(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("problems/864/compute/p20/results/samples.jsonl"),
    )
    parser.add_argument("--sample-id", default=DEFAULT_SAMPLE_ID)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p36/admissible_bridge_obstruction.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = audit(load_sample(args.input, args.sample_id))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "sample_id": result["sample_id"],
                "coefficient_two_cleared_margin": result["coefficient_two_cleared_margin"],
                "lg33_cleared_margin": result["lg33_cleared_margin"],
                "c20_cleared_margin": result["c20_cleared_margin"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
