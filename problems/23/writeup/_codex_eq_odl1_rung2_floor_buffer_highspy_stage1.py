#!/usr/bin/env python3
"""Direct highspy Stage-1 probe for EQ-ODL1 floor-buffer LPs.

This is a diagnostic solver wrapper only. It builds the same Stage-1 LP as
_codex_eq_odl1_rung2_floor_buffer.py and records whether direct highspy returns
more usefully than scipy.optimize.linprog on the full-support matrix.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import highspy
import numpy as np
from scipy.sparse import coo_matrix, hstack

import _codex_eq_odl1_rung2_floor_buffer as floor_buffer


def build_stage1_matrix(mat, nminus):
    row_count, col_count = mat.shape
    theta_rows = [i for i, x in enumerate(nminus) if x]
    theta_col = coo_matrix(
        ([float(nminus[i]) for i in theta_rows], (theta_rows, [0] * len(theta_rows))),
        shape=(row_count, 1),
    ).tocsr()
    return hstack([mat, theta_col], format="csc")


def solve_highspy_stage1(a_csc, p_beta, *, solver: str, time_limit: float, threads: int, output_flag: bool):
    row_count, col_count = a_csc.shape
    lp = highspy.HighsLp()
    lp.num_col_ = col_count
    lp.num_row_ = row_count
    lp.sense_ = highspy.ObjSense.kMinimize
    lp.col_cost_ = np.concatenate([np.zeros(col_count - 1, dtype=np.float64), np.array([-1.0])])
    lp.col_lower_ = np.zeros(col_count, dtype=np.float64)
    lp.col_upper_ = np.full(col_count, highspy.kHighsInf, dtype=np.float64)
    lp.row_lower_ = np.full(row_count, -highspy.kHighsInf, dtype=np.float64)
    lp.row_upper_ = np.array([float(x) for x in p_beta], dtype=np.float64)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.num_col_ = col_count
    lp.a_matrix_.num_row_ = row_count
    lp.a_matrix_.start_ = a_csc.indptr.astype(np.int64, copy=False)
    lp.a_matrix_.index_ = a_csc.indices.astype(np.int32, copy=False)
    lp.a_matrix_.value_ = a_csc.data.astype(np.float64, copy=False)

    h = highspy.Highs()
    h.setOptionValue("output_flag", bool(output_flag))
    h.setOptionValue("time_limit", float(time_limit))
    if threads > 0:
        h.setOptionValue("threads", int(threads))
    if solver:
        h.setOptionValue("solver", solver)
    status = h.passModel(lp)
    t0 = time.time()
    run_status = h.run()
    elapsed = time.time() - t0
    info = h.getInfo()
    model_status = h.getModelStatus()
    sol = h.getSolution()
    theta = None
    if getattr(sol, "col_value", None) is not None and len(sol.col_value) == col_count:
        theta = float(sol.col_value[-1])
    return {
        "pass_status": str(status),
        "run_status": str(run_status),
        "model_status": str(model_status),
        "elapsed_seconds": elapsed,
        "objective_function_value": getattr(info, "objective_function_value", None),
        "simplex_iteration_count": getattr(info, "simplex_iteration_count", None),
        "ipm_iteration_count": getattr(info, "ipm_iteration_count", None),
        "theta_float": theta,
    }


def run(args):
    t0 = time.time()
    prepared, columns = floor_buffer.build_prepared_columns(args.chart, args.dominant, args.band, args.support)
    selected_seconds = time.time() - t0
    t1 = time.time()
    mat, nminus, _col_l1 = floor_buffer.build_sparse_columns(columns, len(prepared.betas))
    sparse_seconds = time.time() - t1
    t2 = time.time()
    a_stage1 = build_stage1_matrix(mat, nminus)
    stage1_matrix_seconds = time.time() - t2
    result = solve_highspy_stage1(
        a_stage1,
        prepared.p_beta,
        solver=args.solver,
        time_limit=args.time_limit,
        threads=args.threads,
        output_flag=args.output_flag,
    )
    return {
        "schema": "eq_odl1_rung2_floor_buffer_highspy_stage1_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": prepared.chart.generator_names[args.dominant],
        "band": args.band,
        "support": args.support,
        "solver": args.solver,
        "threads": args.threads,
        "time_limit": args.time_limit,
        "rows": mat.shape[0],
        "columns": mat.shape[1],
        "nnz": int(mat.nnz),
        "stage1_columns": a_stage1.shape[1],
        "stage1_nnz": int(a_stage1.nnz),
        "nminus_nonzero_rows": sum(1 for x in nminus if x),
        "selected_seconds": selected_seconds,
        "sparse_seconds": sparse_seconds,
        "stage1_matrix_seconds": stage1_matrix_seconds,
        "highspy": result,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=5)
    ap.add_argument("--dominant", type=int, default=13)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", choices=["negative", "all"], default="negative")
    ap.add_argument("--solver", default="simplex")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--time-limit", type=float, default=60.0)
    ap.add_argument("--output-flag", action="store_true")
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_floor_buffer_highspy_stage1_v1.json"))
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "model_status": out["highspy"].get("model_status"),
        "theta_float": out["highspy"].get("theta_float"),
        "elapsed_seconds": out["highspy"].get("elapsed_seconds"),
        "rows": out["rows"],
        "columns": out["columns"],
        "nnz": out["nnz"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
