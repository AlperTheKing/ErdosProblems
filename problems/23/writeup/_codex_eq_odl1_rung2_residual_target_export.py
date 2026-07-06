#!/usr/bin/env python3
"""Export an exact residual as a sparse Bernstein target-beta JSON.

This is a data-plumbing helper for quotient/face-split diagnostics.  Given a
nonnegative source-column solution in the ordinary Rung-2 support LP, it writes
the full residual vector

    target_beta - sum_j value_j * column_j

in the same sparse JSON format accepted by the source-solution checker and the
quotient probe's ``--target-beta-json`` option.  It does not certify the
residual; downstream exact replay still owns acceptance.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_source_solution_check as source_check
import _codex_eq_odl1_rung2_modular_replay as replay


def fraction_record(q: Fraction) -> dict[str, int]:
    return {"num": q.numerator, "den": q.denominator}


def run(args: argparse.Namespace) -> dict[str, object]:
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    if args.target_beta_json:
        target_beta = source_check.read_target_beta(args.target_beta_json, len(prepared.p_beta))
        target_mode = "custom"
    else:
        target_beta = prepared.p_beta
        target_mode = "prepared_p_beta"

    vals = source_check.read_source_solution(args.solution)
    invalid_cols = [c for c in vals if c < 0 or c >= len(columns)]
    if invalid_cols:
        raise ValueError(f"invalid source columns: {invalid_cols[:10]}")

    residual = target_beta[:]
    for source_col, val in vals.items():
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val

    sparse = [
        {
            "row": int(row),
            "beta": list(prepared.betas[row]),
            **fraction_record(value),
        }
        for row, value in enumerate(residual)
        if value
    ]
    negative_rows = [(i, x) for i, x in enumerate(residual) if x < 0]
    positive_rows = [(i, x) for i, x in enumerate(residual) if x > 0]
    neg_vals = [v for v in vals.values() if v < 0]
    payload: dict[str, object] = {
        "schema": "eq_odl1_rung2_residual_target_beta_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "solution": str(args.solution),
        "target_beta_json": str(args.target_beta_json) if args.target_beta_json else None,
        "target_mode": target_mode,
        "columns": len(columns),
        "nonzero_source_columns": sum(1 for x in vals.values() if x),
        "solution_negative_count": len(neg_vals),
        "solution_min": replay.fmt_fraction(min(vals.values()) if vals else Fraction(0)),
        "solution_max": replay.fmt_fraction(max(vals.values()) if vals else Fraction(0)),
        "row_count": len(residual),
        "target_beta_sparse": sparse,
        "residual_nonzero_count": len(sparse),
        "residual_positive_count": len(positive_rows),
        "residual_negative_count": len(negative_rows),
        "residual_zero_count": sum(1 for x in residual if x == 0),
        "residual_min": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        "residual_max": replay.fmt_fraction(max(residual) if residual else Fraction(0)),
        "negative_rows_prefix": [
            {"row": int(i), "beta": list(prepared.betas[i]), "residual": replay.fmt_fraction(x)}
            for i, x in negative_rows[:20]
        ],
    }
    return payload


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--target-beta-json", type=Path, default=None)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "chart": out["chart"],
                "dominant": out["dominant"],
                "residual_nonzero_count": out["residual_nonzero_count"],
                "residual_negative_count": out["residual_negative_count"],
                "residual_min": out["residual_min"],
                "summary": str(args.summary),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
