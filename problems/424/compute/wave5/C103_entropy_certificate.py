#!/usr/bin/env python3
"""Exact affine-spine entropy certificate for the C103 negative-route audit."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


COUNTS = (15, 10, 6)
SLOPES = (2, 3, 5)
BLOCK_LENGTH = sum(COUNTS)
Q = math.prod(slope**count for slope, count in zip(SLOPES, COUNTS))


def multinomial(m: int) -> int:
    numerator = math.factorial(BLOCK_LENGTH * m)
    denominator = math.prod(math.factorial(count * m) for count in COUNTS)
    return numerator // denominator


def main() -> None:
    sys.set_int_max_str_digits(0)
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-m", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.max_m < 1:
        raise ValueError("--max-m must be positive")

    rows = []
    first_superlinear = None
    for m in range(1, args.max_m + 1):
        words = multinomial(m)
        cutoff = 9 * Q**m
        row = {
            "m": m,
            "words": str(words),
            "cutoff": str(cutoff),
            "words_gt_cutoff": words > cutoff,
            "words_times_den_over_cutoff_num": [str(words), str(cutoff)],
        }
        rows.append(row)
        if first_superlinear is None and words > cutoff:
            first_superlinear = m

    # B/Q = (31/30)^31, where B is the entropy base of this exact type.
    entropy_ratio_num = 31**31
    entropy_ratio_den = 30**31
    # Method-of-types lower bound:
    # W_m >= B^m/(31m+1)^2, hence
    # W_m/(9Q^m) >= (31/30)^(31m)/(9(31m+1)^2).
    lower_bound_rows = []
    for m in range(1, args.max_m + 1):
        lhs = entropy_ratio_num**m
        rhs = 9 * (31 * m + 1) ** 2 * entropy_ratio_den**m
        lower_bound_rows.append(
            {
                "m": m,
                "certified_words_gt_cutoff_by_type_bound": lhs > rhs,
                "comparison": [str(lhs), str(rhs)],
            }
        )

    all_m_start = 15
    start_linear = 31 * all_m_start + 1
    next_linear = 31 * (all_m_start + 1) + 1
    all_m_certificate = {
        "start_m": all_m_start,
        "base_case": {
            "lhs": str(entropy_ratio_num**all_m_start),
            "rhs": str(
                9
                * start_linear**2
                * entropy_ratio_den**all_m_start
            ),
            "holds": entropy_ratio_num**all_m_start
            > 9 * start_linear**2 * entropy_ratio_den**all_m_start,
        },
        "monotone_step_at_start": {
            "lhs": str(entropy_ratio_num * start_linear**2),
            "rhs": str(entropy_ratio_den * next_linear**2),
            "holds": entropy_ratio_num * start_linear**2
            > entropy_ratio_den * next_linear**2,
        },
        "monotonicity": "(31m+1)/(31m+32) increases with m",
    }

    payload = {
        "schema_version": 1,
        "arithmetic": "Python arbitrary-precision integers only",
        "slopes": list(SLOPES),
        "type_counts_per_block": list(COUNTS),
        "block_length": BLOCK_LENGTH,
        "Q": str(Q),
        "entropy_base_over_Q": [str(entropy_ratio_num), str(entropy_ratio_den)],
        "identity": "B/Q=(31/30)^31",
        "first_m_with_exact_word_count_gt_9Q^m": first_superlinear,
        "rows": rows,
        "method_of_types_lower_bound": lower_bound_rows,
        "all_m_ge_15_certificate": all_m_certificate,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
