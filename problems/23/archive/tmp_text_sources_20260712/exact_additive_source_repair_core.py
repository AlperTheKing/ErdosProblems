#!/usr/bin/env python3
"""Build an exact additive-only repair core for sources-only EQ Rung-2 rows.

This implements the SOURCES_ONLY_SANITIZER_GPTPRO fallback after unresolved
negative source columns have been zeroed.  The base source solution is fixed;
new variables are nonnegative additive source coefficients mu_j.  HiGHS only
selects a guarded active face.  The exported core is replayed exactly by the
existing modular solver, then applied by apply_source_patch_basis_solution.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.append("problems/23/writeup")
sys.path.append("tmp")

import _codex_eq_odl1_rung2_modular_replay as replay
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_source_solution_check as source_check
import exact_active_face_repair_core as af


def hard_margins(prepared, rows: list[int], pow_: int) -> dict[int, Fraction]:
    if pow_ <= 0:
        return {row: Fraction(0) for row in rows}
    return {
        row: Fraction(1, 1 << pow_) * af.one_plus_scale(prepared, row)
        for row in rows
    }


def rhs_from_residual(
    residual: list[Fraction],
    r0: list[int],
    margins: dict[int, Fraction],
) -> dict[int, Fraction]:
    return {row: residual[row] - margins.get(row, Fraction(0)) for row in r0}


def run(args):
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    vals = source_check.read_source_solution(args.source_solution)
    residual = af.compute_residual(prepared, columns, vals)

    hard_rows = [int(x) for x in args.hard_row]
    if not hard_rows:
        hard_rows = [row for row, val in enumerate(residual) if val < 0]
    hard_rows = sorted(set(hard_rows))
    extra_rows = {int(x) for x in args.extra_row}

    neg_sources = [(col, val) for col, val in vals.items() if val < 0]
    if neg_sources and not args.allow_negative_base_sources:
        return {
            "schema": "exact_additive_source_repair_core_v1",
            "status": "negative_base_sources",
            "negative_source_count": len(neg_sources),
            "negative_source_prefix": [
                {"source_col": int(c), "value": replay.fmt_fraction(v)}
                for c, v in neg_sources[:20]
            ],
        }
    if not hard_rows:
        return {
            "schema": "exact_additive_source_repair_core_v1",
            "status": "no_hard_rows",
            "initial_full_negative_residual_count": 0,
            "initial_min_residual": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        }

    gain_cols = af.select_gain_cols(columns, hard_rows)
    map_cols = set(gain_cols)
    col_maps = af.column_maps(columns, map_cols)
    tight = af.threshold_rows(prepared, residual, args.tight_guard_pow, args.tight_cap)
    damage = af.damage_rows(prepared, columns, residual, gain_cols, args.damage_guard_pow, args.damage_cap)
    r0 = sorted(set(hard_rows) | set(tight) | set(damage) | extra_rows)
    top_gain = af.top_gain_cols(columns, col_maps, hard_rows, r0, gain_cols, args.top_gain)
    j0 = sorted(top_gain)
    col_maps = af.column_maps(columns, set(j0))

    if not j0:
        return {
            "schema": "exact_additive_source_repair_core_v1",
            "status": "no_gain_columns",
            "hard_rows": hard_rows,
            "gain_col_count": len(gain_cols),
            "r0_count": len(r0),
        }

    margins = hard_margins(prepared, hard_rows, args.hard_margin_pow)
    rhs = rhs_from_residual(residual, r0, margins)

    zero_costs = [0.0] * len(j0)
    stage1 = af.solve_highs(columns, col_maps, r0, j0, rhs, zero_costs, hard_rows, args.time_limit)
    if (
        "optimal" not in stage1["model_status"].lower()
        or (stage1.get("objective") is not None and float(stage1["objective"]) > args.objective_tol)
    ):
        if args.hard_margin_pow > 0:
            zero_rhs = rhs_from_residual(residual, r0, {row: Fraction(0) for row in hard_rows})
            stage1_zero = af.solve_highs(columns, col_maps, r0, j0, zero_rhs, zero_costs, hard_rows, args.time_limit)
            stage1["fallback_zero_margin"] = {k: v for k, v in stage1_zero.items() if k != "values"}
            if (
                "optimal" in stage1_zero["model_status"].lower()
                and stage1_zero.get("objective") is not None
                and float(stage1_zero["objective"]) <= args.objective_tol
            ):
                rhs = zero_rhs
                margins = {row: Fraction(0) for row in hard_rows}
            else:
                return failed_summary(args, residual, hard_rows, gain_cols, tight, damage, r0, j0, stage1)
        else:
            return failed_summary(args, residual, hard_rows, gain_cols, tight, damage, r0, j0, stage1)

    weights = []
    for c in j0:
        cmap = col_maps[c]
        w = Fraction(1)
        for row in r0:
            w += abs(cmap.get(row, Fraction(0)))
        weights.append(float(w))
    stage2 = af.solve_highs(columns, col_maps, r0, j0, rhs, weights, None, args.time_limit)

    summary = {
        "schema": "exact_additive_source_repair_core_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "source_solution": str(args.source_solution),
        "hard_rows": hard_rows,
        "extra_rows": sorted(extra_rows),
        "initial_full_negative_residual_count": sum(1 for val in residual if val < 0),
        "initial_min_residual": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        "negative_base_source_count": len(neg_sources),
        "gain_col_count": len(gain_cols),
        "top_gain_count": len(top_gain),
        "tight_guard_count": len(tight),
        "damage_guard_count": len(damage),
        "r0_count": len(r0),
        "j0_count": len(j0),
        "hard_margin_pow": args.hard_margin_pow,
        "stage1": {k: v for k, v in stage1.items() if k != "values"},
        "stage2": {k: v for k, v in stage2.items() if k != "values"},
    }
    if "optimal" not in stage2["model_status"].lower():
        summary["status"] = "stage2_failed"
        return summary

    basic_positions = stage2.get("basic_var_positions", [])
    upper_positions = stage2.get("upper_row_positions", [])
    summary["status"] = "stage2_optimal"
    summary["basic_var_count"] = len(basic_positions)
    summary["upper_row_count"] = len(upper_positions)
    af.export_core(args.out_core, args.meta, j0, r0, basic_positions, upper_positions, rhs, col_maps, summary)
    summary["status"] = "core_exported"
    return summary


def failed_summary(args, residual, hard_rows, gain_cols, tight, damage, r0, j0, stage1):
    return {
        "schema": "exact_additive_source_repair_core_v1",
        "status": "stage1_failed",
        "chart": args.chart,
        "dominant": args.dominant,
        "source_solution": str(args.source_solution),
        "hard_rows": hard_rows,
        "initial_full_negative_residual_count": sum(1 for val in residual if val < 0),
        "initial_min_residual": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        "gain_col_count": len(gain_cols),
        "tight_guard_count": len(tight),
        "damage_guard_count": len(damage),
        "r0_count": len(r0),
        "j0_count": len(j0),
        "stage1": {k: v for k, v in stage1.items() if k != "values"},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--source-solution", type=Path, required=True)
    ap.add_argument("--hard-row", type=int, action="append", default=[])
    ap.add_argument("--extra-row", type=int, action="append", default=[])
    ap.add_argument("--hard-margin-pow", type=int, default=0)
    ap.add_argument("--tight-guard-pow", type=int, default=40)
    ap.add_argument("--damage-guard-pow", type=int, default=34)
    ap.add_argument("--tight-cap", type=int, default=256)
    ap.add_argument("--damage-cap", type=int, default=512)
    ap.add_argument("--top-gain", type=int, default=1024)
    ap.add_argument("--objective-tol", type=float, default=1e-9)
    ap.add_argument("--time-limit", type=float, default=300.0)
    ap.add_argument("--allow-negative-base-sources", action="store_true")
    ap.add_argument("--out-core", type=Path, required=True)
    ap.add_argument("--meta", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "status": out.get("status"),
        "r0_count": out.get("r0_count"),
        "j0_count": out.get("j0_count"),
        "basic_var_count": out.get("basic_var_count"),
        "upper_row_count": out.get("upper_row_count"),
        "out_core": str(args.out_core) if out.get("status") == "core_exported" else None,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
