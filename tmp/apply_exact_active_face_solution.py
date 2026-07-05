#!/usr/bin/env python3
"""Apply an exact active-face source solution and report full residuals."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.append("problems/23/writeup")

import _codex_eq_odl1_rung2_modular_replay as replay
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_full_residual_check as fullcheck


def read_core_cols(path: Path) -> dict[int, int]:
    out = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("type") == "col":
                out[int(rec["col"])] = int(rec["source_col"])
    return out


def compute_residual(prepared, columns, vals: dict[int, Fraction]) -> list[Fraction]:
    residual = prepared.p_beta[:]
    for source_col, val in vals.items():
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    return residual


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--source-out", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    local_to_source = read_core_cols(args.core)
    sol = fullcheck.read_solution(args.solution, len(local_to_source))
    vals: dict[int, Fraction] = {}
    for local_col, val in enumerate(sol):
        if val:
            vals[local_to_source[local_col]] = vals.get(local_to_source[local_col], Fraction(0)) + val

    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    residual = compute_residual(prepared, columns, vals)
    neg_rows = [(i, x) for i, x in enumerate(residual) if x < 0]
    neg_vals = [(c, x) for c, x in vals.items() if x < 0]

    args.source_out.parent.mkdir(parents=True, exist_ok=True)
    with args.source_out.open("w", encoding="utf-8") as f:
        for c in sorted(vals):
            val = vals[c]
            if val:
                f.write(json.dumps({"source_col": c, "num": val.numerator, "den": val.denominator}, sort_keys=True) + "\n")

    payload = {
        "schema": "apply_exact_active_face_solution_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "core": str(args.core),
        "solution": str(args.solution),
        "source_solution": str(args.source_out),
        "source_records": sum(1 for v in vals.values() if v),
        "solution_negative_count": len(neg_vals),
        "full_negative_residual_count": len(neg_rows),
        "full_min_residual": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        "full_max_residual": replay.fmt_fraction(max(residual) if residual else Fraction(0)),
        "min_solution_value": replay.fmt_fraction(min(vals.values()) if vals else Fraction(0)),
        "negative_rows_prefix": [
            {"row": int(row), "residual": replay.fmt_fraction(val)}
            for row, val in neg_rows[:20]
        ],
        "negative_source_prefix": [
            {"source_col": int(col), "value": replay.fmt_fraction(val)}
            for col, val in neg_vals[:20]
        ],
    }
    payload["exact_ok"] = (
        payload["solution_negative_count"] == 0
        and payload["full_negative_residual_count"] == 0
    )
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "exact_ok": payload["exact_ok"],
        "full_negative_residual_count": payload["full_negative_residual_count"],
        "solution_negative_count": payload["solution_negative_count"],
        "full_min_residual": payload["full_min_residual"],
        "source_solution": str(args.source_out),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
