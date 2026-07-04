import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import highspy
import numpy as np
from scipy.sparse import csc_matrix, lil_matrix

sys.path.append("problems/23/writeup")
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_source_solution_check as source_check


def compute_residual(prepared, columns, vals):
    residual = prepared.p_beta[:]
    for source_col, val in vals.items():
        if not val:
            continue
        for row, coeff in columns[source_col].terms:
            residual[row] -= coeff * val
    return residual


def build_row_to_neg_cols(columns):
    out = {}
    for c, col in enumerate(columns):
        for row, coeff in col.terms:
            if coeff < 0:
                out.setdefault(row, []).append(c)
    return out


def status_name(status):
    return str(status).split(".")[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--source-solution", type=Path, required=True)
    ap.add_argument("--time-limit", type=float, default=300.0)
    ap.add_argument("--threshold", type=float, default=0.0)
    ap.add_argument("--margin", type=float, default=0.0)
    ap.add_argument("--active-margin", type=float, default=0.0)
    ap.add_argument("--candidate-mode", choices=["active-negative", "all"], default="active-negative")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    vals = source_check.read_source_solution(args.source_solution)
    residual = compute_residual(prepared, columns, vals)
    active = sorted(i for i, x in enumerate(residual) if x < 0)
    if args.candidate_mode == "all":
        candidates = list(range(len(columns)))
    else:
        row_to_neg_cols = build_row_to_neg_cols(columns)
        candidates = sorted({c for row in active for c in row_to_neg_cols.get(row, [])})
    col_index = {c: j for j, c in enumerate(candidates)}

    row_count = len(residual)
    mat = lil_matrix((row_count, len(candidates)), dtype=float)
    active_set = set(active)
    row_upper = [
        float(x) - args.margin - (args.active_margin if r in active_set else 0.0)
        for r, x in enumerate(residual)
    ]
    for c, j in col_index.items():
        for row, coeff in columns[c].terms:
            mat[row, j] = float(coeff)

    lp = highspy.HighsLp()
    lp.num_col_ = len(candidates)
    lp.num_row_ = row_count
    lp.col_cost_ = [1.0] * len(candidates)
    lp.col_lower_ = [0.0] * len(candidates)
    lp.col_upper_ = [highspy.kHighsInf] * len(candidates)
    lp.row_lower_ = [-highspy.kHighsInf] * row_count
    lp.row_upper_ = row_upper
    csc = csc_matrix(mat)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.num_col_ = len(candidates)
    lp.a_matrix_.num_row_ = row_count
    lp.a_matrix_.start_ = csc.indptr.astype(np.int32).tolist()
    lp.a_matrix_.index_ = csc.indices.astype(np.int32).tolist()
    lp.a_matrix_.value_ = csc.data.astype(float).tolist()

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", args.time_limit)
    h.setOptionValue("primal_feasibility_tolerance", 1e-10)
    h.setOptionValue("dual_feasibility_tolerance", 1e-10)
    h.passModel(lp)
    h.run()
    status = h.modelStatusToString(h.getModelStatus())
    info = h.getInfo()
    out = {
        "schema": "source_patch_highspy_basis_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "source_solution": str(args.source_solution),
        "row_count": row_count,
        "column_count": len(columns),
        "candidate_count": len(candidates),
        "candidate_mode": args.candidate_mode,
        "initial_negative_rows": active,
        "margin": args.margin,
        "active_margin": args.active_margin,
        "model_status": status,
        "objective": getattr(info, "objective_function_value", None),
    }
    if status.lower().find("optimal") >= 0:
        sol = h.getSolution()
        basis = h.getBasis()
        y = list(sol.col_value)
        repaired = [float(x) for x in residual]
        used = []
        for val, c in zip(y, candidates):
            if val <= 1e-12:
                continue
            used.append((c, float(val)))
            for row, coeff in columns[c].terms:
                repaired[row] -= float(coeff) * float(val)
        col_status = [status_name(s) for s in basis.col_status]
        row_status = [status_name(s) for s in basis.row_status]
        out.update({
            "used_count": len(used),
            "min_residual_float": min(repaired),
            "negative_residual_count": sum(1 for x in repaired if x < args.threshold),
            "used": [{"source_col": c, "t": v, "status": col_status[col_index[c]]} for c, v in used],
            "basic_cols": [candidates[i] for i, s in enumerate(col_status) if s == "kBasic"],
            "upper_rows": [i for i, s in enumerate(row_status) if s == "kUpper"],
            "tight_rows": [i for i, (activity, upper) in enumerate(zip(sol.row_value, row_upper)) if abs(activity - upper) <= 1e-7],
            "row_status_counts": {s: row_status.count(s) for s in sorted(set(row_status))},
            "col_status_counts": {s: col_status.count(s) for s in sorted(set(col_status))},
        })
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "out": str(args.out),
        "model_status": out["model_status"],
        "candidate_count": out["candidate_count"],
        "used_count": out.get("used_count"),
        "basic_cols": len(out.get("basic_cols", [])),
        "upper_rows": len(out.get("upper_rows", [])),
        "negative_residual_count": out.get("negative_residual_count"),
        "min_residual_float": out.get("min_residual_float"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
