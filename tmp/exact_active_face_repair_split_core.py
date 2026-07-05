#!/usr/bin/env python3
"""Split-delta active-face repair core builder.

Old support variables are represented as lambda' = lambda0 + u - v with
u >= 0, v >= 0, and explicit source-bound rows v <= lambda0.  New gain
columns are additive u >= 0.  HiGHS selects an active face; the exported
square core is replayed exactly by the modular solver.
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
import exact_active_face_repair_core as base


def fmt_fraction(x: Fraction) -> str:
    if x == 0:
        return "0"
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def status_name(status) -> str:
    return str(status).split(".")[-1]


def make_variables(
    j0: list[int],
    old_vals: dict[int, Fraction],
    exclude_u: set[int],
    exclude_v: set[int],
) -> list[dict[str, object]]:
    variables = []
    for c in j0:
        if c not in exclude_u:
            variables.append({"kind": "u", "source_col": c, "sign": 1})
        if c in old_vals:
            if c not in exclude_v:
                variables.append({"kind": "v", "source_col": c, "sign": -1, "upper": fmt_fraction(old_vals[c])})
    return variables


def make_rows(
    r0: list[int],
    old_cols: list[int],
    residual: list[Fraction],
    margins: dict[int, Fraction],
    old_vals: dict[int, Fraction],
) -> list[dict[str, object]]:
    rows = []
    for r in r0:
        rows.append({"type": "residual", "source_row": r, "rhs": residual[r] - margins.get(r, Fraction(0))})
    for c in old_cols:
        rows.append({"type": "source_bound", "source_col": c, "rhs": old_vals[c]})
    return rows


def row_coeff(row: dict[str, object], var: dict[str, object], col_maps: dict[int, dict[int, Fraction]]) -> Fraction:
    if row["type"] == "residual":
        source_row = int(row["source_row"])
        source_col = int(var["source_col"])
        sign = int(var["sign"])
        return sign * col_maps[source_col].get(source_row, Fraction(0))
    if row["type"] == "source_bound":
        if var["kind"] == "v" and int(var["source_col"]) == int(row["source_col"]):
            return Fraction(1)
        return Fraction(0)
    raise ValueError(row["type"])


def solve_highs(
    variables: list[dict[str, object]],
    rows: list[dict[str, object]],
    col_maps: dict[int, dict[int, Fraction]],
    costs: list[float],
    hard_rows: list[int] | None,
    time_limit: float,
):
    hard_rows = hard_rows or []
    hard_positions = {
        int(row["source_row"]): i
        for i, row in enumerate(rows)
        if row["type"] == "residual" and int(row["source_row"]) in set(hard_rows)
    }
    z_offset = len(variables)
    total_cols = len(variables) + len(hard_positions)
    mat = lil_matrix((len(rows), total_cols), dtype=float)
    row_upper = []
    scales = []
    for i, row in enumerate(rows):
        rhs = row["rhs"]
        assert isinstance(rhs, Fraction)
        scale = max(1.0, abs(float(rhs)))
        scales.append(scale)
        row_upper.append(float(rhs) / scale)
    for j, var in enumerate(variables):
        for i, row in enumerate(rows):
            coeff = row_coeff(row, var, col_maps)
            if coeff:
                mat[i, j] = float(coeff) / scales[i]
    for z_index, (_source_row, row_pos) in enumerate(hard_positions.items()):
        mat[row_pos, z_offset + z_index] = -1.0 / scales[row_pos]

    lp = highspy.HighsLp()
    inf = highspy.kHighsInf
    lp.num_col_ = total_cols
    lp.num_row_ = len(rows)
    lp.col_cost_ = costs + [1.0] * len(hard_positions)
    lp.col_lower_ = [0.0] * total_cols
    lp.col_upper_ = [inf] * total_cols
    lp.row_lower_ = [-inf] * len(rows)
    lp.row_upper_ = row_upper
    csc = csc_matrix(mat)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.num_col_ = total_cols
    lp.a_matrix_.num_row_ = len(rows)
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
    status = h.modelStatusToString(h.getModelStatus())
    info = h.getInfo()
    out = {"model_status": status, "objective": getattr(info, "objective_function_value", None)}
    if "optimal" not in status.lower():
        return out
    solution = h.getSolution()
    basis = h.getBasis()
    col_status = [status_name(s) for s in basis.col_status]
    row_status = [status_name(s) for s in basis.row_status]
    out.update({
        "values": list(solution.col_value),
        "basic_var_positions": [i for i, s in enumerate(col_status) if s == "kBasic" and i < len(variables)],
        "basic_z_positions": [i - len(variables) for i, s in enumerate(col_status) if s == "kBasic" and i >= len(variables)],
        "upper_row_positions": [i for i, s in enumerate(row_status) if s == "kUpper"],
        "tight_row_positions": [
            i for i, (activity, upper) in enumerate(zip(solution.row_value, row_upper))
            if abs(activity - upper) <= 1e-7
        ],
        "row_status_counts": {s: row_status.count(s) for s in sorted(set(row_status))},
        "col_status_counts": {s: col_status.count(s) for s in sorted(set(col_status))},
    })
    return out


def export_core(
    out_core: Path,
    meta_path: Path,
    variables: list[dict[str, object]],
    rows: list[dict[str, object]],
    col_maps: dict[int, dict[int, Fraction]],
    basic_positions: list[int],
    upper_positions: list[int],
    summary: dict[str, object],
) -> None:
    if len(basic_positions) != len(upper_positions):
        raise RuntimeError(f"basis not square: {len(basic_positions)} cols vs {len(upper_positions)} rows")
    basic_vars = [variables[i] for i in basic_positions]
    upper_rows = [rows[i] for i in upper_positions]
    terms = []
    for local_col, var in enumerate(basic_vars):
        for local_row, row in enumerate(upper_rows):
            coeff = row_coeff(row, var, col_maps)
            if coeff:
                terms.append((local_row, local_col, coeff))
    out_core.parent.mkdir(parents=True, exist_ok=True)
    with out_core.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "meta", "dimension": len(basic_vars), "terms": len(terms)}) + "\n")
        for local_col, var in enumerate(basic_vars):
            f.write(json.dumps({"type": "col", "col": local_col, "source_col": int(var["source_col"])}) + "\n")
        for local_row, row in enumerate(upper_rows):
            rhs = row["rhs"]
            assert isinstance(rhs, Fraction)
            f.write(json.dumps({"type": "rhs", "row": local_row, "value": fmt_fraction(rhs)}) + "\n")
            if row["type"] == "residual":
                f.write(json.dumps({"type": "selected_row", "row": local_row, "source_row": int(row["source_row"])}) + "\n")
        for row, col, value in terms:
            f.write(json.dumps({"type": "term", "row": row, "col": col, "value": fmt_fraction(value)}) + "\n")
    meta = dict(summary)
    meta.update({
        "out_core": str(out_core),
        "dimension": len(basic_vars),
        "terms": len(terms),
        "basic_variables": basic_vars,
        "upper_rows": [
            {k: (fmt_fraction(v) if isinstance(v, Fraction) else v) for k, v in row.items()}
            for row in upper_rows
        ],
    })
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")


def run(args):
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    vals = source_check.read_source_solution(args.source_solution)
    residual = base.compute_residual(prepared, columns, vals)
    hard_rows = [int(x) for x in args.hard_row] or [i for i, v in enumerate(residual) if v < 0]
    extra_rows = set(int(x) for x in args.extra_row)
    old_cols = {c for c, v in vals.items() if v > 0}
    gain_cols = base.select_gain_cols(columns, hard_rows)
    map_cols = old_cols | gain_cols
    col_maps_for_score = base.column_maps(columns, map_cols)
    tight = base.threshold_rows(prepared, residual, args.tight_guard_pow, args.tight_cap)
    damage = base.damage_rows(prepared, columns, residual, gain_cols, args.damage_guard_pow, args.damage_cap)
    r0 = sorted(set(hard_rows) | set(tight) | set(damage) | extra_rows)
    top_gain = base.top_gain_cols(columns, col_maps_for_score, hard_rows, r0, gain_cols, args.top_gain)
    j0 = sorted(old_cols | top_gain)
    col_maps = base.column_maps(columns, set(j0))

    def margins(use_hard: bool) -> dict[int, Fraction]:
        if not use_hard:
            return {row: Fraction(0) for row in hard_rows}
        return {
            row: Fraction(1, 1 << args.hard_margin_pow) * base.one_plus_scale(prepared, row)
            for row in hard_rows
        }

    stage1_margin = margins(True)
    rows_margin = make_rows(r0, sorted(old_cols), residual, stage1_margin, vals)
    variables = make_variables(j0, vals, set(args.exclude_u_col), set(args.exclude_v_col))
    zero_costs = [0.0] * len(variables)
    stage1 = solve_highs(variables, rows_margin, col_maps, zero_costs, hard_rows, args.time_limit)
    margin_used = "hard"
    rows = rows_margin
    if "optimal" not in stage1["model_status"].lower() or (
        stage1.get("objective") is not None and float(stage1["objective"]) > args.objective_tol
    ):
        rows_zero = make_rows(r0, sorted(old_cols), residual, margins(False), vals)
        stage1_zero = solve_highs(variables, rows_zero, col_maps, zero_costs, hard_rows, args.time_limit)
        stage1["fallback_zero_margin"] = {k: v for k, v in stage1_zero.items() if k != "values"}
        margin_used = "zero"
        rows = rows_zero
        if "optimal" not in stage1_zero["model_status"].lower() or (
            stage1_zero.get("objective") is not None and float(stage1_zero["objective"]) > args.objective_tol
        ):
            return {
                "schema": "exact_active_face_repair_split_core_v1",
                "status": "stage1_failed",
                "stage1": {k: v for k, v in stage1.items() if k != "values"},
                "r0_count": len(r0),
                "j0_count": len(j0),
                "variable_count": len(variables),
            }

    weights = []
    for var in variables:
        c = int(var["source_col"])
        w = Fraction(1)
        for row in r0:
            w += abs(col_maps[c].get(row, Fraction(0)))
        weights.append(float(w))
    stage2 = solve_highs(variables, rows, col_maps, weights, None, args.time_limit)
    summary = {
        "schema": "exact_active_face_repair_split_core_v1",
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
        "variable_count": len(variables),
        "margin_used": margin_used,
        "stage1": {k: v for k, v in stage1.items() if k != "values"},
        "stage2": {k: v for k, v in stage2.items() if k != "values"},
    }
    if "optimal" not in stage2["model_status"].lower():
        summary["status"] = "stage2_failed"
        return summary
    summary["status"] = "stage2_optimal"
    summary["basic_var_count"] = len(stage2.get("basic_var_positions", []))
    summary["upper_row_count"] = len(stage2.get("upper_row_positions", []))
    export_core(
        args.out_core,
        args.meta,
        variables,
        rows,
        col_maps,
        stage2.get("basic_var_positions", []),
        stage2.get("upper_row_positions", []),
        summary,
    )
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
    ap.add_argument("--exclude-u-col", type=int, action="append", default=[])
    ap.add_argument("--exclude-v-col", type=int, action="append", default=[])
    ap.add_argument("--objective-tol", type=float, default=1e-9)
    ap.add_argument("--time-limit", type=float, default=240.0)
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
        "variable_count": out.get("variable_count"),
        "basic_var_count": out.get("basic_var_count"),
        "upper_row_count": out.get("upper_row_count"),
        "margin_used": out.get("margin_used"),
        "out_core": str(args.out_core) if out.get("status") == "core_exported" else None,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
