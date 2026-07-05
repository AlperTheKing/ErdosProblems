#!/usr/bin/env python3
"""Exact checker for arbitrary sparse EQ-ODL1 Rung-2 cone dictionaries.

The ordinary source checker rebuilds the standard chart dictionary.  Face-split
fallbacks also need custom lifted dictionaries, for example columns of the form
G_a * generator * multiplier.  This checker keeps the same certificate format
for multipliers, but reads the sparse column matrix from JSON.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import _codex_eq_odl1_rung2_modular_replay as replay
import _codex_eq_odl1_rung2_scipy_core_probe as standard_probe
import _codex_eq_odl1_rung2_source_solution_check as source_check


@dataclass(frozen=True)
class SparseColumn:
    kind: str
    name: str
    multiplier_exp: tuple[int, ...]
    terms: tuple[tuple[int, Fraction], ...]


def fraction_record(q: Fraction) -> dict[str, int]:
    return {"num": q.numerator, "den": q.denominator}


def parse_fraction(value: Any) -> Fraction:
    return source_check.parse_fraction(value)


def read_columns_json(path: Path) -> tuple[list[SparseColumn], int, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "columns" not in data:
        raise ValueError("columns JSON must be an object containing a columns list")
    row_count = int(data["row_count"])
    columns: list[SparseColumn] = []
    for cidx, rec in enumerate(data["columns"]):
        terms = []
        for term in rec.get("terms", []):
            row = int(term["row"])
            if row < 0 or row >= row_count:
                raise ValueError(f"column {cidx} has row out of range: {row}")
            terms.append((row, parse_fraction(term)))
        columns.append(
            SparseColumn(
                kind=str(rec.get("kind", "")),
                name=str(rec.get("name", "")),
                multiplier_exp=tuple(int(x) for x in rec.get("multiplier_exp", [])),
                terms=tuple(sorted(terms)),
            )
        )
    return columns, row_count, data


def build_standard_columns(args: argparse.Namespace) -> tuple[list[SparseColumn], int, list[Fraction], dict[str, Any]]:
    prepared, columns, _mat, _b_ub = standard_probe.build_lp(args.chart, args.dominant, args.band, args.support)
    sparse = [
        SparseColumn(
            kind=str(col.kind),
            name=str(col.name),
            multiplier_exp=tuple(int(x) for x in col.multiplier_exp),
            terms=tuple(col.terms),
        )
        for col in columns
    ]
    meta = {
        "mode": "standard",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": prepared.chart.generator_names[args.dominant],
        "band": args.band,
        "support": args.support,
    }
    return sparse, len(prepared.p_beta), prepared.p_beta, meta


def read_target(path: Path | None, row_count: int, default: list[Fraction] | None) -> tuple[list[Fraction], str]:
    if path is None:
        if default is None:
            raise ValueError("--target-beta-json is required when --columns-json is used")
        return default[:], "prepared_p_beta"
    return source_check.read_target_beta(path, row_count), "custom"


def check_cone(
    vals: dict[int, Fraction],
    columns: list[SparseColumn],
    row_count: int,
    target_beta: list[Fraction],
    *,
    args: argparse.Namespace,
    column_meta: dict[str, Any],
) -> dict[str, Any]:
    if len(target_beta) != row_count:
        raise ValueError(f"target length {len(target_beta)} != row_count {row_count}")
    invalid_cols = [c for c in vals if c < 0 or c >= len(columns)]
    if invalid_cols:
        raise ValueError(f"invalid source columns: {invalid_cols[:10]}")

    residual = target_beta[:]
    for source_col, val in vals.items():
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val

    negative_rows = [(i, x) for i, x in enumerate(residual) if x < 0]
    nonzero_vals = {c: v for c, v in vals.items() if v}
    out: dict[str, Any] = {
        "schema": "eq_odl1_rung2_custom_cone_check_v1",
        "solution": str(args.solution),
        "columns_json": str(args.columns_json) if args.columns_json else None,
        "target_beta_json": str(args.target_beta_json) if args.target_beta_json else None,
        "target_beta_mode": "custom" if args.target_beta_json else "prepared_p_beta",
        "column_meta": column_meta,
        "row_count": row_count,
        "columns": len(columns),
        "column_term_count": sum(len(c.terms) for c in columns),
        "target_beta_nonzero_count": sum(1 for x in target_beta if x),
        "nonzero_source_columns": len(nonzero_vals),
        "solution_negative_count": sum(1 for x in vals.values() if x < 0),
        "solution_min": replay.fmt_fraction(min(vals.values()) if vals else Fraction(0)),
        "solution_max": replay.fmt_fraction(max(vals.values()) if vals else Fraction(0)),
        "full_negative_residual_count": len(negative_rows),
        "full_zero_residual_count": sum(1 for x in residual if x == 0),
        "full_min_residual": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        "full_max_residual": replay.fmt_fraction(max(residual) if residual else Fraction(0)),
        "negative_rows_prefix": [
            {"row": int(i), "residual": replay.fmt_fraction(x)}
            for i, x in negative_rows[:10]
        ],
    }
    out["exact_ok"] = out["solution_negative_count"] == 0 and out["full_negative_residual_count"] == 0
    return out


def run(args: argparse.Namespace) -> dict[str, Any]:
    vals = source_check.read_source_solution(args.solution)
    if args.columns_json:
        columns, row_count, meta = read_columns_json(args.columns_json)
        default_target = None
        column_meta = {
            "mode": "custom",
            "source": str(args.columns_json),
            "schema": meta.get("schema"),
            "column_set": meta.get("column_set"),
            "chart": meta.get("chart"),
            "dominant": meta.get("dominant"),
            "dominant_name": meta.get("dominant_name"),
            "band": meta.get("band"),
        }
    else:
        columns, row_count, default_target, column_meta = build_standard_columns(args)
    target_beta, target_mode = read_target(args.target_beta_json, row_count, default_target)
    out = check_cone(vals, columns, row_count, target_beta, args=args, column_meta=column_meta)
    out["target_beta_mode"] = target_mode
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--columns-json", type=Path, default=None)
    ap.add_argument("--target-beta-json", type=Path, default=None)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--dominant", type=int, default=7)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "exact_ok": out["exact_ok"],
                "solution_negative_count": out["solution_negative_count"],
                "full_negative_residual_count": out["full_negative_residual_count"],
                "full_min_residual": out["full_min_residual"],
                "columns": out["columns"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
