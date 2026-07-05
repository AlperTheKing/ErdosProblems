#!/usr/bin/env python3
"""Audit source-column certificates for face-split fallback design.

This is diagnostic only: it does not certify a chart.  It classifies the
available cone columns for one chart/dominant pair and, when given a source
solution JSONL, reports how much of that solution uses the dominant generator
columns that would vanish on the face G_dom = 0.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

sys.path.append("problems/23/writeup")

import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_source_solution_check as source_check


def fmt(q: Fraction) -> str:
    if q == 0:
        return "0"
    if q.denominator == 1:
        return str(q.numerator)
    if abs(q.numerator).bit_length() > 256 or q.denominator.bit_length() > 256:
        sign = "-" if q < 0 else ""
        return f"{sign}num_bits={abs(q.numerator).bit_length()}/den_bits={q.denominator.bit_length()}"
    return f"{q.numerator}/{q.denominator}"


def family_key(col) -> str:
    return f"{col.kind}:{col.name}"


def run(args: argparse.Namespace) -> dict[str, object]:
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    dominant_name = prepared.chart.generator_names[args.dominant]

    family_counts = Counter(family_key(c) for c in columns)
    kind_counts = Counter(c.kind for c in columns)
    dominant_gen_cols = [i for i, c in enumerate(columns) if c.kind == "gen" and c.name == dominant_name]
    dominant_delta_cols = [i for i, c in enumerate(columns) if c.kind == "delta" and c.name.startswith(dominant_name + "-")]

    out: dict[str, object] = {
        "schema": "eq_odl1_rung2_face_split_audit_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": dominant_name,
        "band": args.band,
        "support": args.support,
        "rows": len(prepared.betas),
        "columns": len(columns),
        "kind_counts": dict(sorted(kind_counts.items())),
        "dominant_gen_column_count": len(dominant_gen_cols),
        "dominant_delta_column_count": len(dominant_delta_cols),
        "family_counts_prefix": dict(sorted(family_counts.items())[: args.family_prefix]),
        "face_column_count_strong_drop_dominant_gen": len(columns) - len(dominant_gen_cols),
    }

    if args.solution:
        vals = source_check.read_source_solution(args.solution)
        used = {c: v for c, v in vals.items() if v}
        if any(c < 0 or c >= len(columns) for c in used):
            bad = [c for c in used if c < 0 or c >= len(columns)]
            raise ValueError(f"solution has invalid source columns: {bad[:10]}")

        used_kind_counts: Counter[str] = Counter()
        used_family_counts: Counter[str] = Counter()
        used_family_l1: defaultdict[str, Fraction] = defaultdict(Fraction)
        dominant_gen_l1 = Fraction(0)
        dominant_gen_signed = Fraction(0)
        for source_col, val in used.items():
            col = columns[source_col]
            key = family_key(col)
            used_kind_counts[col.kind] += 1
            used_family_counts[key] += 1
            used_family_l1[key] += abs(val)
            if source_col in dominant_gen_cols:
                dominant_gen_l1 += abs(val)
                dominant_gen_signed += val

        residual = prepared.p_beta[:]
        residual_without_dominant_gen = prepared.p_beta[:]
        for source_col, val in used.items():
            if not val:
                continue
            col = columns[source_col]
            for row, coeff in col.terms:
                residual[row] -= coeff * val
                if source_col not in dominant_gen_cols:
                    residual_without_dominant_gen[row] -= coeff * val

        neg = [(i, x) for i, x in enumerate(residual) if x < 0]
        neg_no_dom = [(i, x) for i, x in enumerate(residual_without_dominant_gen) if x < 0]
        out["solution"] = str(args.solution)
        out["solution_nonzero_columns"] = len(used)
        out["solution_negative_count"] = sum(1 for v in used.values() if v < 0)
        out["used_kind_counts"] = dict(sorted(used_kind_counts.items()))
        out["used_family_counts_prefix"] = dict(sorted(used_family_counts.items())[: args.family_prefix])
        out["dominant_gen_used_count"] = sum(1 for c in used if c in dominant_gen_cols)
        out["dominant_gen_used_abs_sum"] = fmt(dominant_gen_l1)
        out["dominant_gen_used_signed_sum"] = fmt(dominant_gen_signed)
        out["full_negative_residual_count"] = len(neg)
        out["full_min_residual"] = fmt(min(residual) if residual else Fraction(0))
        out["drop_dominant_gen_negative_residual_count"] = len(neg_no_dom)
        out["drop_dominant_gen_min_residual"] = fmt(
            min(residual_without_dominant_gen) if residual_without_dominant_gen else Fraction(0)
        )
        out["negative_rows_prefix"] = [
            {"row": int(i), "residual": fmt(x), "beta": list(prepared.betas[i])}
            for i, x in neg[: args.row_prefix]
        ]
        out["drop_dominant_gen_negative_rows_prefix"] = [
            {"row": int(i), "residual": fmt(x), "beta": list(prepared.betas[i])}
            for i, x in neg_no_dom[: args.row_prefix]
        ]
        out["used_family_abs_sum_prefix"] = {
            k: fmt(v) for k, v in sorted(used_family_l1.items())[: args.family_prefix]
        }

    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--solution", type=Path)
    ap.add_argument("--family-prefix", type=int, default=40)
    ap.add_argument("--row-prefix", type=int, default=20)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    out = run(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "chart": out["chart"],
        "dominant": out["dominant"],
        "dominant_name": out["dominant_name"],
        "columns": out["columns"],
        "dominant_gen_column_count": out["dominant_gen_column_count"],
        "solution_nonzero_columns": out.get("solution_nonzero_columns"),
        "dominant_gen_used_count": out.get("dominant_gen_used_count"),
        "full_negative_residual_count": out.get("full_negative_residual_count"),
        "drop_dominant_gen_negative_residual_count": out.get("drop_dominant_gen_negative_residual_count"),
        "out": str(args.out),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
