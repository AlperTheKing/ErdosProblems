#!/usr/bin/env python3
"""Exact smoke round-trip for the Rung-2 hybrid face/lift cone.

This is the validation bridge requested before scaling the hybrid quotient
search.  It starts from an already exact standard source certificate, rewrites
its nonzero columns into the hybrid dictionary:

  * non-dominant generator columns -> face_gen
  * dominance-delta columns        -> face_delta
  * band columns                   -> face_band
  * dominant generator columns     -> lift_base, scaled through the monic
                                      dominant divisor used by the quotient

The emitted custom sparse dictionary is in the same degree-11 Bernstein row
space as the official custom cone checker.  Any remaining nonnegative residual
is exactly the recovered face-base Bernstein slack.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import _codex_eq_odl1_rung2_custom_cone_check as custom_check
import _codex_eq_odl1_rung2_face_split_quotient_probe as quotient
import _codex_eq_odl1_rung2_modular_replay as replay
import _codex_eq_odl1_rung2_source_solution_check as source_check
import _codex_eq_odl1_rung2_support_lp as support


def fraction_record(q: Fraction) -> dict[str, int]:
    return {"num": q.numerator, "den": q.denominator}


def write_solution(path: Path, vals: dict[int, Fraction]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for source_col in sorted(vals):
            val = vals[source_col]
            if val:
                f.write(json.dumps({"source_col": source_col, **fraction_record(val)}, sort_keys=True) + "\n")


def write_target(path: Path, values: list[Fraction]) -> None:
    rows = [
        {"row": i, **fraction_record(value)}
        for i, value in enumerate(values)
        if value
    ]
    if not rows:
        rows = [{"row": 0, "num": 0, "den": 1}]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"target_beta_sparse": rows}, separators=(",", ":"), sort_keys=True), encoding="utf-8")


def scale_terms(terms: tuple[tuple[int, Fraction], ...], scale: Fraction) -> tuple[tuple[int, Fraction], ...]:
    if scale == 1:
        return terms
    return tuple((row, coeff * scale) for row, coeff in terms if coeff * scale)


def dominant_leading_coeff(chart_index: int, dominant: int) -> Fraction:
    chart = quotient.charts.build_chart(chart_index)
    gen_polys = [quotient.homogenize_poly(expr, chart.variables, quotient.GEN_DEGREE) for expr in chart.generators]
    _divisor, _lead_exp, lead_coeff = quotient.monic_normalize(gen_polys[dominant])
    if lead_coeff <= 0:
        raise ValueError(f"dominant leading coefficient must be positive for cone scaling, got {lead_coeff}")
    return lead_coeff


def emit_columns(
    *,
    prepared: support.PreparedChart,
    standard_columns: list[support.Column],
    vals: dict[int, Fraction],
    dominant: int,
    dominant_lc: Fraction,
    args: argparse.Namespace,
) -> tuple[list[custom_check.SparseColumn], dict[int, Fraction], dict[str, Any]]:
    dominant_name = prepared.chart.generator_names[dominant]
    hybrid_columns: list[custom_check.SparseColumn] = []
    hybrid_vals: dict[int, Fraction] = {}
    source_to_hybrid: dict[int, int] = {}
    counts: dict[str, int] = {}

    for source_col in sorted(vals):
        val = vals[source_col]
        if not val:
            continue
        col = standard_columns[source_col]
        if col.kind == "gen" and col.name == dominant_name:
            kind = "lift_base"
            name = f"{dominant_name}_monic_base"
            terms = scale_terms(col.terms, Fraction(1, 1) / dominant_lc)
            out_val = val * dominant_lc
        elif col.kind == "gen":
            kind = "face_gen"
            name = col.name
            terms = col.terms
            out_val = val
        elif col.kind == "delta":
            kind = "face_delta"
            name = col.name
            terms = col.terms
            out_val = val
        elif col.kind == "band":
            kind = "face_band"
            name = col.name
            terms = col.terms
            out_val = val
        else:
            raise ValueError(f"unsupported standard column kind/name: {col.kind}:{col.name}")

        new_idx = len(hybrid_columns)
        source_to_hybrid[source_col] = new_idx
        hybrid_columns.append(
            custom_check.SparseColumn(
                kind=kind,
                name=name,
                multiplier_exp=tuple(int(x) for x in col.multiplier_exp),
                terms=tuple(sorted(terms)),
            )
        )
        hybrid_vals[new_idx] = out_val
        counts[f"{kind}:{name}"] = counts.get(f"{kind}:{name}", 0) + 1

    meta = {
        "source_nonzero_columns": len(vals),
        "hybrid_nonzero_columns": len(hybrid_columns),
        "family_counts": dict(sorted(counts.items())),
        "dominant_leading_coeff": replay.fmt_fraction(dominant_lc),
        "source_to_hybrid_prefix": [
            {"source_col": int(src), "hybrid_col": int(dst)}
            for src, dst in list(source_to_hybrid.items())[:20]
        ],
    }
    return hybrid_columns, hybrid_vals, meta


def contribution(row_count: int, columns: list[custom_check.SparseColumn], vals: dict[int, Fraction]) -> list[Fraction]:
    out = [Fraction(0) for _ in range(row_count)]
    for col_index, val in vals.items():
        if not val:
            continue
        for row, coeff in columns[col_index].terms:
            out[row] += coeff * val
    return out


def write_columns(
    path: Path,
    *,
    prepared: support.PreparedChart,
    dominant: int,
    band: str,
    support_mode: str,
    columns: list[custom_check.SparseColumn],
    mapping_meta: dict[str, Any],
) -> None:
    payload: dict[str, Any] = {
        "schema": "eq_odl1_rung2_hybrid_roundtrip_columns_v1",
        "column_set": "hybrid_combined_nonzero",
        "row_count": len(prepared.p_beta),
        "chart": prepared.k,
        "dominant": dominant,
        "dominant_name": prepared.chart.generator_names[dominant],
        "band": band,
        "support": support_mode,
        "mapping_meta": mapping_meta,
        "columns": [
            {
                "kind": col.kind,
                "name": col.name,
                "multiplier_exp": list(col.multiplier_exp),
                "terms": [
                    {"row": int(row), **fraction_record(coeff)}
                    for row, coeff in col.terms
                ],
            }
            for col in columns
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":"), sort_keys=True), encoding="utf-8")


def run_exact_checker(args: argparse.Namespace) -> dict[str, Any]:
    cmd = [
        sys.executable,
        "-B",
        str(Path("problems/23/writeup/_codex_eq_odl1_rung2_custom_cone_check.py")),
        "--columns-json",
        str(args.columns_json),
        "--target-beta-json",
        str(args.target_beta_json),
        "--solution",
        str(args.hybrid_solution),
        "--summary",
        str(args.check_summary),
    ]
    completed = subprocess.run(cmd, check=False, text=True, capture_output=True)
    return {
        "command": " ".join(cmd),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    prepared = support.prepare_chart(args.chart)
    if prepared.chart.generator_names[args.dominant] != args.dominant_name and args.dominant_name:
        raise ValueError(
            f"dominant name mismatch: index {args.dominant} is "
            f"{prepared.chart.generator_names[args.dominant]!r}, expected {args.dominant_name!r}"
        )
    standard_columns = support.selected_degree2_columns(
        prepared.p_beta,
        prepared.beta_index,
        prepared.gen_polys,
        prepared.chart.generator_names,
        args.dominant,
        args.support,
        None,
    )
    standard_columns.extend(support.selected_band_columns(prepared.p_beta, prepared.beta_index, args.band, args.support, None))
    vals = source_check.read_source_solution(args.source_solution)
    invalid = [idx for idx in vals if idx < 0 or idx >= len(standard_columns)]
    if invalid:
        raise ValueError(f"source solution references invalid standard columns: {invalid[:10]}")

    dominant_lc = dominant_leading_coeff(args.chart, args.dominant)
    hybrid_columns, hybrid_vals, mapping_meta = emit_columns(
        prepared=prepared,
        standard_columns=standard_columns,
        vals=vals,
        dominant=args.dominant,
        dominant_lc=dominant_lc,
        args=args,
    )

    contrib = contribution(len(prepared.p_beta), hybrid_columns, hybrid_vals)
    slack = [target - used for target, used in zip(prepared.p_beta, contrib)]
    negative_slack = [(i, x) for i, x in enumerate(slack) if x < 0]

    write_columns(
        args.columns_json,
        prepared=prepared,
        dominant=args.dominant,
        band=args.band,
        support_mode=args.support,
        columns=hybrid_columns,
        mapping_meta=mapping_meta,
    )
    write_solution(args.hybrid_solution, hybrid_vals)
    write_target(args.target_beta_json, prepared.p_beta)
    write_target(args.recovered_slack_json, slack)

    checker = run_exact_checker(args)
    check_payload = json.loads(args.check_summary.read_text(encoding="utf-8")) if args.check_summary.exists() else {}
    out: dict[str, Any] = {
        "schema": "eq_odl1_rung2_hybrid_roundtrip_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": prepared.chart.generator_names[args.dominant],
        "band": args.band,
        "support": args.support,
        "source_solution": str(args.source_solution),
        "standard_columns": len(standard_columns),
        "standard_nonzero_solution": len([v for v in vals.values() if v]),
        "hybrid_columns": len(hybrid_columns),
        "hybrid_solution": str(args.hybrid_solution),
        "columns_json": str(args.columns_json),
        "target_beta_json": str(args.target_beta_json),
        "recovered_slack_json": str(args.recovered_slack_json),
        "check_summary": str(args.check_summary),
        "mapping_meta": mapping_meta,
        "recovered_slack_nonzero_count": sum(1 for x in slack if x),
        "recovered_slack_zero_count": sum(1 for x in slack if x == 0),
        "recovered_slack_negative_count": len(negative_slack),
        "recovered_slack_min": replay.fmt_fraction(min(slack) if slack else Fraction(0)),
        "recovered_slack_max": replay.fmt_fraction(max(slack) if slack else Fraction(0)),
        "negative_slack_prefix": [
            {"row": int(i), "value": replay.fmt_fraction(value)}
            for i, value in negative_slack[:10]
        ],
        "checker": checker,
        "checker_exact_ok": bool(check_payload.get("exact_ok")),
        "exact_ok": len(negative_slack) == 0 and checker.get("returncode") == 0 and bool(check_payload.get("exact_ok")),
    }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--dominant-name", default="")
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", choices=["negative", "all"], default="negative")
    ap.add_argument("--source-solution", type=Path, required=True)
    ap.add_argument("--columns-json", type=Path, required=True)
    ap.add_argument("--hybrid-solution", type=Path, required=True)
    ap.add_argument("--target-beta-json", type=Path, required=True)
    ap.add_argument("--recovered-slack-json", type=Path, required=True)
    ap.add_argument("--check-summary", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "exact_ok": out["exact_ok"],
                "checker_exact_ok": out["checker_exact_ok"],
                "recovered_slack_negative_count": out["recovered_slack_negative_count"],
                "hybrid_columns": out["hybrid_columns"],
                "summary": str(args.summary),
            },
            sort_keys=True,
        )
    )
    if not out["exact_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
