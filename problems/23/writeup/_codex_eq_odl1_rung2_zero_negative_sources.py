#!/usr/bin/env python3
"""Zero negative source coefficients in an EQ-ODL1 source solution.

This is a representation-preparation step for the sources-only fallback:
remove unresolved negative source coefficients, then let a nonnegative
additive repair certificate pay for the exact residual they expose.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import _codex_eq_odl1_rung2_source_solution_check as source_check


def fmt_fraction(x: Fraction) -> str:
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-solution", type=Path, required=True)
    ap.add_argument("--source-out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    vals = source_check.read_source_solution(args.source_solution)
    negatives = {c: v for c, v in vals.items() if v < 0}
    zeroed = {c: v for c, v in vals.items() if v > 0}

    args.source_out.parent.mkdir(parents=True, exist_ok=True)
    with args.source_out.open("w", encoding="utf-8") as f:
        for c in sorted(zeroed):
            v = zeroed[c]
            f.write(
                json.dumps(
                    {"source_col": int(c), "num": v.numerator, "den": v.denominator},
                    sort_keys=True,
                )
                + "\n"
            )

    payload = {
        "schema": "eq_odl1_rung2_zero_negative_sources_v1",
        "input_solution": str(args.source_solution),
        "output_solution": str(args.source_out),
        "input_nonzero": sum(1 for v in vals.values() if v),
        "output_nonzero": len(zeroed),
        "zeroed_negative_count": len(negatives),
        "zeroed_negative_detail": [
            {"source_col": int(c), "value": fmt_fraction(v)}
            for c, v in sorted(negatives.items())
        ],
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "zeroed_negative_count": payload["zeroed_negative_count"],
                "output_nonzero": payload["output_nonzero"],
                "source_out": str(args.source_out),
                "summary": str(args.summary),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
