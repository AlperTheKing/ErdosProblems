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
import _codex_eq_odl1_rung2_full_residual_check as fullcheck
import _codex_eq_odl1_rung2_scipy_core_probe as probe
import probe_rung2_multirepair_lp as base


def collapsed_source_values(source_cols, sol):
    vals = {}
    for val, source_col in zip(sol, source_cols):
        vals[source_col] = vals.get(source_col, Fraction(0)) + val
    return vals


def status_name(status):
    return str(status).split('.')[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--core", type=Path, required=True)
    ap.add_argument("--solution", type=Path, required=True)
    ap.add_argument("--time-limit", type=float, default=300.0)
    ap.add_argument("--margin", type=float, default=0.0)
    ap.add_argument("--margin-row", type=int, action="append", default=[])
    ap.add_argument("--source-margin", type=float)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    dim, source_cols, _selected_rows = fullcheck.read_core_maps(args.core)
    sol0 = fullcheck.read_solution(args.solution, dim)
    prepared, columns, _mat, _b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    residual = base.compute_residual(prepared, columns, source_cols, sol0)
    source_vals = collapsed_source_values(source_cols, sol0)
    negative_source = sorted(c for c, v in source_vals.items() if v < 0)
    candidates = list(range(len(columns)))
    col_index = {c: i for i, c in enumerate(candidates)}

    row_count = len(residual)
    total_rows = row_count + len(negative_source)
    mat = lil_matrix((total_rows, len(candidates)), dtype=float)
    row_upper = [0.0] * total_rows
    margin_rows = set(args.margin_row)
    for r, val in enumerate(residual):
        row_margin = args.margin if not margin_rows or r in margin_rows else 0.0
        row_upper[r] = float(val) - row_margin
    for c, j in col_index.items():
        for row, coeff in columns[c].terms:
            mat[row, j] = float(coeff)
    for i, c in enumerate(negative_source):
        row = row_count + i
        src_margin = args.margin if args.source_margin is None else args.source_margin
        row_upper[row] = float(source_vals[c]) - src_margin
        mat[row, col_index[c]] = -1.0

    csc = csc_matrix(mat)
    lp = highspy.HighsLp()
    lp.num_col_ = len(candidates)
    lp.num_row_ = total_rows
    lp.col_cost_ = [1.0] * len(candidates)
    lp.col_lower_ = [0.0] * len(candidates)
    inf = highspy.kHighsInf
    lp.col_upper_ = [inf] * len(candidates)
    lp.row_lower_ = [-inf] * total_rows
    lp.row_upper_ = row_upper
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.num_col_ = len(candidates)
    lp.a_matrix_.num_row_ = total_rows
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
    model_status = h.getModelStatus()
    info = h.getInfo()
    out = {
        "schema": "rung2_highspy_basis_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "row_count": row_count,
        "total_rows": total_rows,
        "column_count": len(columns),
        "negative_source": negative_source,
        "margin": args.margin,
        "margin_rows": sorted(margin_rows),
        "source_margin": args.margin if args.source_margin is None else args.source_margin,
        "model_status": h.modelStatusToString(model_status),
        "objective": getattr(info, "objective_function_value", None),
    }
    if h.modelStatusToString(model_status).lower().find("optimal") >= 0:
        solution = h.getSolution()
        basis = h.getBasis()
        y = list(solution.col_value)
        repaired = [float(x) for x in residual]
        source_float = {c: float(v) for c, v in source_vals.items()}
        used = []
        for val, c in zip(y, candidates):
            if val <= 1e-11:
                continue
            used.append((c, float(val)))
            source_float[c] = source_float.get(c, 0.0) + float(val)
            for row, coeff in columns[c].terms:
                repaired[row] -= float(coeff) * float(val)
        col_status = [status_name(s) for s in basis.col_status]
        row_status = [status_name(s) for s in basis.row_status]
        out.update({
            "used_count": len(used),
            "min_residual_float": min(repaired),
            "negative_residual_count": sum(1 for x in repaired if x < -1e-9),
            "min_source_float": min(source_float.values()) if source_float else 0.0,
            "negative_source_count": sum(1 for x in source_float.values() if x < -1e-9),
            "used": [{"source_col": c, "t": v, "status": col_status[col_index[c]]} for c, v in used],
            "basic_cols": [candidates[i] for i, s in enumerate(col_status) if s == "kBasic"],
            "upper_rows": [i for i, s in enumerate(row_status) if s == "kUpper"],
            "tight_rows": [i for i, (activity, upper) in enumerate(zip(solution.row_value, row_upper)) if abs(activity - upper) <= 1e-7],
            "row_status_counts": {s: row_status.count(s) for s in sorted(set(row_status))},
            "col_status_counts": {s: col_status.count(s) for s in sorted(set(col_status))},
        })
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "out": str(args.out),
        "model_status": out["model_status"],
        "objective": out.get("objective"),
        "used_count": out.get("used_count"),
        "basic_cols": len(out.get("basic_cols", [])),
        "negative_residual_count": out.get("negative_residual_count"),
        "negative_source_count": out.get("negative_source_count"),
        "min_residual_float": out.get("min_residual_float"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()

