#!/usr/bin/env python3
"""Build an exact active-face repair core for a degenerate Rung-2 row.

This is a candidate generator, not an acceptance gate.  It builds the guarded
active-face LP described in F6_ACTIVE_FACE_REPAIR_GPTPRO.md, uses HiGHS only to
choose an active face, and exports the corresponding square rational system for
the existing modular exact replay.  The produced repair is accepted only after
exact replay plus the official source checker.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import highspy
import numpy as np
from scipy.sparse import csc_matrix, lil_matrix

sys.path.append("problems/23/writeup")
sys.path.append("tmp")

import _codex_eq_odl1_rung2_modular_replay as replay
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_source_solution_check as source_check


def fmt_fraction(x: Fraction) -> str:
    if x == 0:
        return "0"
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def compute_residual(prepared, columns, vals: dict[int, Fraction]) -> list[Fraction]:
    residual = prepared.p_beta[:]
    for source_col, val in vals.items():
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    return residual


def column_maps(columns, cols: set[int]) -> dict[int, dict[int, Fraction]]:
    return {c: dict(columns[c].terms) for c in sorted(cols)}


def one_plus_scale(prepared, row: int) -> Fraction:
    return Fraction(1) + abs(prepared.p_beta[row])


def threshold_rows(
    prepared,
    residual: list[Fraction],
    threshold_pow: int,
    cap: int,
) -> list[int]:
    out = []
    denom = Fraction(1, 1 << threshold_pow)
    for row, val in enumerate(residual):
        if val < 0:
            continue
        scale = one_plus_scale(prepared, row)
        if val <= denom * scale:
            out.append((val / scale, row))
    out.sort()
    return [row for _score, row in out[:cap]]


def damage_rows(
    prepared,
    columns,
    residual: list[Fraction],
    gain_cols: set[int],
    threshold_pow: int,
    cap: int,
) -> list[int]:
    if not gain_cols:
        return []
    damaged = set()
    for c in gain_cols:
        for row, coeff in columns[c].terms:
            if coeff > 0:
                damaged.add(row)
    out = []
    denom = Fraction(1, 1 << threshold_pow)
    for row in damaged:
        val = residual[row]
        if val < 0:
            continue
        scale = one_plus_scale(prepared, row)
        if val <= denom * scale:
            out.append((val / scale, row))
    out.sort()
    return [row for _score, row in out[:cap]]


def select_gain_cols(columns, hard_rows: list[int]) -> set[int]:
    hard = set(hard_rows)
    gain = set()
    for c, col in enumerate(columns):
        for row, coeff in col.terms:
            if row in hard and coeff < 0:
                gain.add(c)
                break
    return gain


def top_gain_cols(
    columns,
    col_maps: dict[int, dict[int, Fraction]],
    hard_rows: list[int],
    r0: list[int],
    gain_cols: set[int],
    per_hard: int,
) -> set[int]:
    out = set()
    r0_set = set(r0)
    for hard in hard_rows:
        ranked = []
        for c in gain_cols:
            cmap = col_maps[c]
            bad = cmap.get(hard, Fraction(0))
            if bad >= 0:
                continue
            damage = Fraction(1)
            for row in r0_set:
                coeff = cmap.get(row, Fraction(0))
                if coeff > 0:
                    damage += coeff
            ranked.append((float((-bad) / damage), c))
        ranked.sort(reverse=True)
        out.update(c for _score, c in ranked[:per_hard])
    return out


def status_name(status) -> str:
    return str(status).split(".")[-1]


def solve_highs(
    columns,
    col_maps: dict[int, dict[int, Fraction]],
    r0: list[int],
    j0: list[int],
    rhs: dict[int, Fraction],
    costs: list[float],
    z_hard_rows: list[int] | None,
    time_limit: float,
):
    z_hard_rows = z_hard_rows or []
    z_pos = {row: len(j0) + i for i, row in enumerate(z_hard_rows)}
    total_cols = len(j0) + len(z_hard_rows)
    row_index = {row: i for i, row in enumerate(r0)}
    mat = lil_matrix((len(r0), total_cols), dtype=float)
    row_upper = [0.0] * len(r0)
    scales = []
    for row in r0:
        scale = max(1.0, abs(float(rhs[row])))
        scales.append(scale)
        row_upper[row_index[row]] = float(rhs[row]) / scale
    for j, c in enumerate(j0):
        cmap = col_maps[c]
        for row in r0:
            coeff = cmap.get(row, Fraction(0))
            if coeff:
                mat[row_index[row], j] = float(coeff) / scales[row_index[row]]
    for row, zcol in z_pos.items():
        mat[row_index[row], zcol] = -1.0 / scales[row_index[row]]

    lp = highspy.HighsLp()
    inf = highspy.kHighsInf
    lp.num_col_ = total_cols
    lp.num_row_ = len(r0)
    lp.col_cost_ = costs + [1.0] * len(z_hard_rows)
    lp.col_lower_ = [0.0] * total_cols
    lp.col_upper_ = [inf] * total_cols
    lp.row_lower_ = [-inf] * len(r0)
    lp.row_upper_ = row_upper
    csc = csc_matrix(mat)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.num_col_ = total_cols
    lp.a_matrix_.num_row_ = len(r0)
    lp.a_matrix_.start_ = csc.indptr.astype(np.int32).tolist()
    lp.a_matrix_.index_ = csc.indices.astype(np.int32).tolist()
    lp.a_matrix_.value_ = csc.data.astype(float).tolist()

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", time_limit)
    h.setOptionValue("primal_feasibility_tolerance", 1e-10)
    h.setOptionValue("dual_feasibility_tolerance", 1e-10)
    h.setOptionValue("solver", "simplex")
    h.passModel(lp)
    h.run()
    model_status = h.getModelStatus()
    info = h.getInfo()
    out = {
        "model_status": h.modelStatusToString(model_status),
        "objective": getattr(info, "objective_function_value", None),
    }
    if "optimal" not in out["model_status"].lower():
        return out
    solution = h.getSolution()
    basis = h.getBasis()
    col_status = [status_name(s) for s in basis.col_status]
    row_status = [status_name(s) for s in basis.row_status]
    y = list(solution.col_value)
    out.update(
        {
            "values": y,
            "basic_var_positions": [i for i, s in enumerate(col_status) if s == "kBasic" and i < len(j0)],
            "basic_z_positions": [i - len(j0) for i, s in enumerate(col_status) if s == "kBasic" and i >= len(j0)],
            "upper_row_positions": [i for i, s in enumerate(row_status) if s == "kUpper"],
            "tight_row_positions": [
                i
                for i, (activity, upper) in enumerate(zip(solution.row_value, row_upper))
                if abs(activity - upper) <= 1e-7
            ],
            "row_status_counts": {s: row_status.count(s) for s in sorted(set(row_status))},
            "col_status_counts": {s: col_status.count(s) for s in sorted(set(col_status))},
        }
    )
    return out


def build_rhs_for_final_vars(
    residual: list[Fraction],
    vals: dict[int, Fraction],
    col_maps: dict[int, dict[int, Fraction]],
    r0: list[int],
    j0: list[int],
    margins: dict[int, Fraction],
) -> dict[int, Fraction]:
    old = set(vals)
    rhs = {}
    for row in r0:
        val = residual[row] - margins.get(row, Fraction(0))
        for c in j0:
            if c in old:
                val += col_maps[c].get(row, Fraction(0)) * vals[c]
        rhs[row] = val
    return rhs


def export_core(
    path: Path,
    meta_path: Path,
    j0: list[int],
    r0: list[int],
    basic_positions: list[int],
    upper_positions: list[int],
    rhs: dict[int, Fraction],
    col_maps: dict[int, dict[int, Fraction]],
    summary: dict,
) -> None:
    if len(basic_positions) != len(upper_positions):
        raise RuntimeError(f"basis not square: {len(basic_positions)} cols vs {len(upper_positions)} rows")
    basic_cols = [j0[i] for i in basic_positions]
    upper_rows = [r0[i] for i in upper_positions]
    row_pos = {row: i for i, row in enumerate(upper_rows)}
    terms = []
    for local_col, source_col in enumerate(basic_cols):
        cmap = col_maps[source_col]
        for source_row, local_row in row_pos.items():
            coeff = cmap.get(source_row, Fraction(0))
            if coeff:
                terms.append((local_row, local_col, coeff))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "meta", "dimension": len(basic_cols), "terms": len(terms)}) + "\n")
        for local_col, source_col in enumerate(basic_cols):
            f.write(json.dumps({"type": "col", "col": local_col, "source_col": source_col}) + "\n")
        for local_row, source_row in enumerate(upper_rows):
            f.write(json.dumps({"type": "selected_row", "row": local_row, "source_row": source_row}) + "\n")
            f.write(json.dumps({"type": "rhs", "row": local_row, "value": fmt_fraction(rhs[source_row])}) + "\n")
        for row, col, value in terms:
            f.write(json.dumps({"type": "term", "row": row, "col": col, "value": fmt_fraction(value)}) + "\n")
    meta = dict(summary)
    meta.update(
        {
            "out_core": str(path),
            "basic_cols": basic_cols,
            "upper_rows": upper_rows,
            "dimension": len(basic_cols),
            "terms": len(terms),
        }
    )
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")


def run(args):
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    vals = source_check.read_source_solution(args.source_solution)
    residual = compute_residual(prepared, columns, vals)
    hard_rows = [int(x) for x in args.hard_row]
    if not hard_rows:
        hard_rows = [row for row, val in enumerate(residual) if val < 0]
    extra_rows = set(int(x) for x in args.extra_row)

    gain_cols = select_gain_cols(columns, hard_rows)
    # Need maps for all old columns and all potential gain columns before scoring.
    old_cols = {c for c, v in vals.items() if v > 0}
    map_cols = old_cols | gain_cols
    col_maps = column_maps(columns, map_cols)
    tight = threshold_rows(prepared, residual, args.tight_guard_pow, args.tight_cap)
    damage = damage_rows(prepared, columns, residual, gain_cols, args.damage_guard_pow, args.damage_cap)
    r0 = sorted(set(hard_rows) | set(tight) | set(damage) | extra_rows)
    top_gain = top_gain_cols(columns, col_maps, hard_rows, r0, gain_cols, args.top_gain)
    j0 = sorted(old_cols | top_gain)
    col_maps = column_maps(columns, set(j0))

    hard_margin = {
        row: Fraction(1, 1 << args.hard_margin_pow) * one_plus_scale(prepared, row)
        for row in hard_rows
    }
    margins = hard_margin
    rhs_margin = build_rhs_for_final_vars(residual, vals, col_maps, r0, j0, margins)
    zero_margins = {row: Fraction(0) for row in hard_rows}
    rhs_zero = build_rhs_for_final_vars(residual, vals, col_maps, r0, j0, zero_margins)

    zero_costs = [0.0] * len(j0)
    stage1 = solve_highs(columns, col_maps, r0, j0, rhs_margin, zero_costs, hard_rows, args.time_limit)
    margin_used = "hard"
    if "optimal" not in stage1["model_status"].lower() or (stage1.get("objective") is not None and float(stage1["objective"]) > args.objective_tol):
        stage1_zero = solve_highs(columns, col_maps, r0, j0, rhs_zero, zero_costs, hard_rows, args.time_limit)
        stage1["fallback_zero_margin"] = stage1_zero
        margin_used = "zero"
        margins = zero_margins
        rhs = rhs_zero
        if "optimal" not in stage1_zero["model_status"].lower() or (
            stage1_zero.get("objective") is not None and float(stage1_zero["objective"]) > args.objective_tol
        ):
            return {
                "schema": "exact_active_face_repair_core_v1",
                "status": "stage1_failed",
                "stage1": stage1,
                "hard_rows": hard_rows,
                "r0_count": len(r0),
                "j0_count": len(j0),
            }
    else:
        rhs = rhs_margin

    weights = []
    for c in j0:
        w = Fraction(1)
        cmap = col_maps[c]
        for row in r0:
            w += abs(cmap.get(row, Fraction(0)))
        weights.append(float(w))
    stage2 = solve_highs(columns, col_maps, r0, j0, rhs, weights, None, args.time_limit)
    summary = {
        "schema": "exact_active_face_repair_core_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "source_solution": str(args.source_solution),
        "hard_rows": hard_rows,
        "extra_rows": sorted(extra_rows),
        "initial_negative_rows": [row for row, val in enumerate(residual) if val < 0],
        "initial_full_negative_residual_count": sum(1 for val in residual if val < 0),
        "initial_min_residual": replay.fmt_fraction(min(residual) if residual else Fraction(0)),
        "old_support_count": len(old_cols),
        "gain_col_count": len(gain_cols),
        "top_gain_count": len(top_gain),
        "tight_guard_count": len(tight),
        "damage_guard_count": len(damage),
        "r0_count": len(r0),
        "j0_count": len(j0),
        "margin_used": margin_used,
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
    export_core(args.out_core, args.meta, j0, r0, basic_positions, upper_positions, rhs, col_maps, summary)
    summary["status"] = "core_exported"
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--source-solution", type=Path, required=True)
    ap.add_argument("--hard-row", type=int, action="append", default=[])
    ap.add_argument("--extra-row", type=int, action="append", default=[])
    ap.add_argument("--hard-margin-pow", type=int, default=30)
    ap.add_argument("--tight-guard-pow", type=int, default=36)
    ap.add_argument("--damage-guard-pow", type=int, default=30)
    ap.add_argument("--tight-cap", type=int, default=256)
    ap.add_argument("--damage-cap", type=int, default=512)
    ap.add_argument("--top-gain", type=int, default=512)
    ap.add_argument("--objective-tol", type=float, default=1e-9)
    ap.add_argument("--time-limit", type=float, default=240.0)
    ap.add_argument("--out-core", type=Path, required=True)
    ap.add_argument("--meta", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": out.get("status"),
                "r0_count": out.get("r0_count"),
                "j0_count": out.get("j0_count"),
                "basic_var_count": out.get("basic_var_count"),
                "upper_row_count": out.get("upper_row_count"),
                "margin_used": out.get("margin_used"),
                "out_core": str(args.out_core) if out.get("status") == "core_exported" else None,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
