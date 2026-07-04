#!/usr/bin/env python3
"""Exact one-row repair search for a Rung-2 core solution.

The core replay can leave a small number of full LP residual rows negative.
This script scans the full reduced-support column set for a single nonnegative
column increment that repairs the most negative row without violating any other
full LP inequality.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import _codex_eq_odl1_rung2_full_residual_check as fullcheck
import _codex_eq_odl1_rung2_modular_replay as replay
import _codex_eq_odl1_rung2_scipy_core_probe as probe


def fraction_record(q: Fraction) -> dict[str, int]:
    return {"num": int(q.numerator), "den": int(q.denominator)}


def coeff_at(col, row: int) -> Fraction:
    for i, coeff in col.terms:
        if i == row:
            return coeff
    return Fraction(0)


def compute_residual(prepared, columns, source_cols: list[int], sol: list[Fraction]) -> list[Fraction]:
    residual = prepared.p_beta[:]
    for val, source_col in zip(sol, source_cols):
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    return residual


def scan_one_column(prepared, columns, residual: list[Fraction], bad_row: int, source_cols: set[int], max_hits: int):
    bad_residual = residual[bad_row]
    if bad_residual >= 0:
        raise ValueError(f"bad_row is not negative: row={bad_row} residual={bad_residual}")

    hits = []
    blockers: dict[str, int] = {
        "missing_bad_coeff": 0,
        "wrong_bad_sign": 0,
        "too_small_allowance": 0,
    }
    tested = 0
    for source_col, col in enumerate(columns):
        c_bad = coeff_at(col, bad_row)
        if c_bad == 0:
            blockers["missing_bad_coeff"] += 1
            continue
        if c_bad > 0:
            blockers["wrong_bad_sign"] += 1
            continue
        tested += 1
        required = (-bad_residual) / (-c_bad)
        max_t: Fraction | None = None
        limiting_row: int | None = None
        limiting_coeff: Fraction | None = None
        for row, coeff in col.terms:
            if coeff <= 0:
                continue
            bound = residual[row] / coeff
            if max_t is None or bound < max_t:
                max_t = bound
                limiting_row = row
                limiting_coeff = coeff
        if max_t is not None and required > max_t:
            blockers["too_small_allowance"] += 1
            continue
        hits.append(
            {
                "source_col": source_col,
                "already_in_core": source_col in source_cols,
                "required": required,
                "bad_coeff": c_bad,
                "max_t": max_t,
                "limiting_row": limiting_row,
                "limiting_coeff": limiting_coeff,
                "terms": len(col.terms),
                "kind": getattr(col, "kind", None),
                "name": getattr(col, "name", None),
                "multiplier_exp": list(getattr(col, "multiplier_exp", ())) if getattr(col, "multiplier_exp", None) is not None else None,
            }
        )
        if len(hits) >= max_hits:
            break
    return hits, blockers | {"tested_bad_sign_columns": tested}


def apply_repair(prepared, columns, residual: list[Fraction], hit: dict[str, object]) -> list[Fraction]:
    new_residual = residual[:]
    t = hit["required"]
    assert isinstance(t, Fraction)
    col = columns[int(hit["source_col"])]
    for row, coeff in col.terms:
        new_residual[row] -= coeff * t
    return new_residual


def write_repaired_source_solution(path: Path, source_cols: list[int], sol: list[Fraction], repair_hit: dict[str, object]) -> None:
    vals: dict[int, Fraction] = {}
    for source_col, val in zip(source_cols, sol):
        if val:
            vals[source_col] = vals.get(source_col, Fraction(0)) + val
    source_col = int(repair_hit["source_col"])
    t = repair_hit["required"]
    assert isinstance(t, Fraction)
    vals[source_col] = vals.get(source_col, Fraction(0)) + t
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for source_col in sorted(vals):
            val = vals[source_col]
            f.write(json.dumps({"source_col": source_col, "num": val.numerator, "den": val.denominator}) + "\n")


def summarize_hit(hit: dict[str, object]) -> dict[str, object]:
    out: dict[str, object] = {}
    for key, val in hit.items():
        if isinstance(val, Fraction):
            out[key] = replay.fmt_fraction(val)
        elif isinstance(val, tuple):
            out[key] = list(val)
        else:
            out[key] = val
    return out


def run(args):
    dim, source_cols, selected_rows = fullcheck.read_core_maps(args.core)
    sol = fullcheck.read_solution(args.solution, dim)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    residual = compute_residual(prepared, columns, source_cols, sol)
    negative_rows = [(i, x) for i, x in enumerate(residual) if x < 0]
    bad_row = args.bad_row
    if bad_row is None:
        if not negative_rows:
            bad_row = min(range(len(residual)), key=lambda i: residual[i])
        else:
            bad_row = min(negative_rows, key=lambda ix: ix[1])[0]

    hits, blockers = scan_one_column(prepared, columns, residual, bad_row, set(source_cols), args.max_hits)
    out: dict[str, object] = {
        "schema": "eq_odl1_rung2_one_row_repair_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "core": str(args.core),
        "solution": str(args.solution),
        "bad_row": int(bad_row),
        "bad_beta": list(prepared.betas[bad_row]),
        "bad_residual": replay.fmt_fraction(residual[bad_row]),
        "initial_negative_residual_count": sum(1 for x in residual if x < 0),
        "initial_min_residual": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        "columns": len(columns),
        "source_core_columns": len(source_cols),
        "blockers": blockers,
        "single_column_hit_count_reported": len(hits),
        "single_column_hits": [summarize_hit(hit) for hit in hits],
    }
    if hits:
        repaired = apply_repair(prepared, columns, residual, hits[0])
        out["first_hit_exact_ok"] = all(x >= 0 for x in repaired)
        out["first_hit_negative_residual_count"] = sum(1 for x in repaired if x < 0)
        out["first_hit_min_residual"] = replay.fmt_fraction(min(repaired) if repaired else Fraction(0))
        out["first_hit_zero_residual_count"] = sum(1 for x in repaired if x == 0)
        out["first_hit"] = summarize_hit(hits[0])
        if args.repaired_solution:
            write_repaired_source_solution(args.repaired_solution, source_cols, sol, hits[0])
            out["repaired_source_solution"] = str(args.repaired_solution)
    else:
        out["first_hit_exact_ok"] = False
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--dominant", type=int, default=7)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--bad-row", type=int)
    ap.add_argument("--max-hits", type=int, default=20)
    ap.add_argument("--repaired-solution", type=Path)
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_one_row_repair_v1.json"))
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "initial_negative_residual_count": out["initial_negative_residual_count"],
        "bad_row": out["bad_row"],
        "single_column_hit_count_reported": out["single_column_hit_count_reported"],
        "first_hit_exact_ok": out["first_hit_exact_ok"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
