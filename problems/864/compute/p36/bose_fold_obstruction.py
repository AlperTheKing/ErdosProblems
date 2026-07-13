#!/usr/bin/env python3
"""Exact uncolored obstruction for the centered C20 interval frontier.

A Bose-Chowla modular Sidon set modulo q^2-1 is folded modulo
(q^2-1)/2 and cut at its largest cyclic gap.  The resulting ordinary set
has nu_A(d) <= 2, but it need not have all sum collisions at one center.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any


COMPUTE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COMPUTE_DIR / "p12"))

from algebraic_scan import bose_chowla  # noqa: E402
from search_interval_lemmas import (  # noqa: E402
    compute_metrics,
    difference_counts,
)


def modular_difference_counts(points: tuple[int, ...], modulus: int) -> Counter[int]:
    counts: Counter[int] = Counter()
    for left in points:
        for right in points:
            if left != right:
                counts[(right - left) % modulus] += 1
    return counts


def unordered_sum_counts(points: tuple[int, ...]) -> Counter[int]:
    counts: Counter[int] = Counter()
    for index, left in enumerate(points):
        for right in points[index:]:
            counts[left + right] += 1
    return counts


def fold_and_cut(q: int) -> dict[str, Any]:
    if q % 2 == 0:
        raise ValueError("q must be odd so that the quotient has fold factor two")

    original_modulus, bose, field_data = bose_chowla(q)
    if original_modulus != q * q - 1:
        raise AssertionError("unexpected Bose-Chowla modulus")
    folded_modulus = original_modulus // 2
    folded = tuple(sorted({value % folded_modulus for value in bose}))
    if len(folded) != q:
        raise AssertionError("folding identified two Bose-Chowla marks")

    modular_counts = modular_difference_counts(folded, folded_modulus)
    modular_max = max(modular_counts.values(), default=0)
    if modular_max > 2:
        raise AssertionError("folded set is not a modular 2-Golomb ruler")

    cyclic_gaps = [
        folded[index + 1] - folded[index]
        for index in range(len(folded) - 1)
    ]
    cyclic_gaps.append(folded_modulus + folded[0] - folded[-1])
    cut_index = max(range(q), key=lambda index: cyclic_gaps[index])
    cut_start = folded[(cut_index + 1) % q]
    points = tuple(
        sorted((value - cut_start) % folded_modulus + 1 for value in folded)
    )
    n = points[-1]
    if points[0] != 1:
        raise AssertionError("largest-gap cut was not endpoint normalized")
    if n != folded_modulus - cyclic_gaps[cut_index] + 1:
        raise AssertionError("cut diameter mismatch")

    ordinary_counts = difference_counts(points)
    ordinary_max = max(ordinary_counts.values(), default=0)
    if ordinary_max > 2:
        raise AssertionError("ordinary difference multiplicity exceeds two")

    metrics = compute_metrics(points, n)
    h = metrics.h
    lhs = Fraction(metrics.m_h, n) * (
        1 + Fraction(2 * metrics.z_h, h * h)
    )
    rhs = Fraction(4, 3) + Fraction(3, 2) * (
        Fraction(h, n) + Fraction(metrics.k - 1, h)
    )
    excess = lhs - rhs
    if excess != Fraction(metrics.c20_margin, 6 * n * h * h):
        raise AssertionError("rational and cleared C20 margins disagree")

    sums = unordered_sum_counts(points)
    repeated_sums = tuple(
        sorted((value, count) for value, count in sums.items() if count >= 2)
    )
    admissible = len(repeated_sums) <= 1

    # This is LG33 with 8 rather than 9 on N(k-1)H, equivalently a
    # coefficient-2 rather than coefficient-9/4 cardinality charge.
    coefficient_two_margin = (
        8 * n * metrics.z_h
        - 12 * h * h * metrics.ambient_holes
        + 3 * h**3
        - 12 * h * h
        - 8 * n * (metrics.k - 1) * h
    )

    return {
        "q": q,
        "original_modulus": original_modulus,
        "folded_modulus": folded_modulus,
        "field": field_data,
        "largest_cyclic_gap": cyclic_gaps[cut_index],
        "cut_start": cut_start,
        "modular_max_difference_multiplicity": modular_max,
        "ordinary_max_difference_multiplicity": ordinary_max,
        "admissible": admissible,
        "repeated_sum_value_count": len(repeated_sums),
        "max_unordered_sum_multiplicity": max(sums.values()),
        "first_repeated_sums": [list(item) for item in repeated_sums[:10]],
        "c20_lhs": f"{lhs.numerator}/{lhs.denominator}",
        "c20_rhs": f"{rhs.numerator}/{rhs.denominator}",
        "c20_excess": f"{excess.numerator}/{excess.denominator}",
        "coefficient_two_cleared_margin": coefficient_two_margin,
        **metrics.record(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, nargs="*", default=[11, 19, 31, 43, 61, 101])
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p36/bose_fold_obstruction.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = [fold_and_cut(q) for q in args.q]
    result = {
        "arithmetic": "integer/rational",
        "construction": "Bose-Chowla fold by two followed by largest-gap cut",
        "records": records,
        "c20_failure_count": sum(
            record["c20_cleared_margin"] > 0 for record in records
        ),
        "admissible_c20_failure_count": sum(
            record["admissible"] and record["c20_cleared_margin"] > 0
            for record in records
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "q_values": args.q,
                "c20_failure_count": result["c20_failure_count"],
                "admissible_c20_failure_count": result["admissible_c20_failure_count"],
                "first_failure_q": next(
                    (
                        record["q"]
                        for record in records
                        if record["c20_cleared_margin"] > 0
                    ),
                    None,
                ),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
