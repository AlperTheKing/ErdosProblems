#!/usr/bin/env python3
"""Bounded dual objective gate for selected Rung-2 quotient columns.

For a selected quotient-column set A_J and target b, the Phase-I primal

    A_J x + u+ - u- = b,  x,u+,u- >= 0,  min 1'u+ + 1'u-

has the bounded dual

    max b'y
    s.t. A_j'y <= 0 for every selected structural column j,
         -1 <= y_r <= 1 for every quotient row r.

This script solves that dual directly from a serialized qcolumns cache.  It is
the objective-equivalence gate before replacing the primal artificial master
with pair-interval dual column generation.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np

import _codex_eq_odl1_rung2_face_split_quotient_probe as qprobe

try:
    import highspy
except ImportError:  # pragma: no cover
    highspy = None


QColumn = qprobe.QColumn
Exp = qprobe.Exp
Poly = qprobe.Poly


def load_columns(path: Path) -> tuple[dict[str, Any], list[QColumn], Poly, Poly]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "eq_odl1_rung2_face_split_quotient_qcolumns_v1":
        raise ValueError(f"unsupported qcolumns schema: {payload.get('schema')!r}")
    rem_p = qprobe.poly_from_terms_record(payload["remP_terms"])
    quo_p = qprobe.poly_from_terms_record(payload["quoP_terms"])
    columns = [qprobe.qcolumn_from_record(rec) for rec in payload["columns"]]
    return payload, columns, rem_p, quo_p


def pair_interval_summary(columns: list[QColumn], dominant_name: str) -> dict[str, object]:
    face_gen: dict[tuple[str, Exp], QColumn] = {}
    face_delta: dict[tuple[str, Exp], QColumn] = {}
    other_face = 0
    lift = 0
    for col in columns:
        if col.side == "lift":
            lift += 1
            continue
        if col.side != "face":
            continue
        if col.kind == "face_gen":
            face_gen[(col.name, col.multiplier_exp)] = col
        elif col.kind == "face_delta":
            face_delta[(col.name, col.multiplier_exp)] = col
        else:
            other_face += 1

    pair_objects = 0
    gen_only: list[dict[str, object]] = []
    delta_only: list[dict[str, object]] = []
    for key in face_gen:
        name, exp = key
        delta_key = (f"{dominant_name}-{name}", exp)
        if delta_key in face_delta:
            pair_objects += 1
        else:
            gen_only.append({"family": name, "exp": list(exp)})
    for key in face_delta:
        name, exp = key
        if not name.startswith(f"{dominant_name}-"):
            delta_only.append({"family": name, "exp": list(exp)})
            continue
        gen_name = name[len(dominant_name) + 1:]
        if (gen_name, exp) not in face_gen:
            delta_only.append({"family": name, "exp": list(exp)})

    return {
        "pair_objects": pair_objects,
        "face_gen_columns": len(face_gen),
        "face_delta_columns": len(face_delta),
        "other_face_columns": other_face,
        "lift_columns": lift,
        "pair_closure_ok": not gen_only and not delta_only,
        "gen_only_count": len(gen_only),
        "delta_only_count": len(delta_only),
        "gen_only_examples": gen_only[:10],
        "delta_only_examples": delta_only[:10],
    }


def solve_dual(
    rows: list[tuple[str, Exp]],
    rhs: list[qprobe.Fraction],
    mat,
    *,
    box: float,
    threads: int,
    solver: str,
    time_limit: float,
    verbose: bool,
) -> dict[str, object]:
    if highspy is None:
        raise RuntimeError("highspy is not installed")
    csc = mat.T.tocsc()
    structural_constraints, row_vars = csc.shape
    inf = highspy.kHighsInf

    lp = highspy.HighsLp()
    lp.num_col_ = int(row_vars)
    lp.num_row_ = int(structural_constraints)
    lp.sense_ = highspy.ObjSense.kMaximize
    lp.col_cost_ = [float(x) for x in rhs]
    lp.col_lower_ = [-float(box)] * int(row_vars)
    lp.col_upper_ = [float(box)] * int(row_vars)
    lp.row_lower_ = [-inf] * int(structural_constraints)
    lp.row_upper_ = [0.0] * int(structural_constraints)

    a = highspy.HighsSparseMatrix()
    a.format_ = highspy.MatrixFormat.kColwise
    a.num_col_ = int(row_vars)
    a.num_row_ = int(structural_constraints)
    a.start_ = [int(x) for x in csc.indptr]
    a.index_ = [int(x) for x in csc.indices]
    a.value_ = [float(x) for x in csc.data]
    lp.a_matrix_ = a

    highs = highspy.Highs()
    highs.setOptionValue("output_flag", bool(verbose))
    if solver != "choose":
        highs.setOptionValue("solver", solver)
    if threads > 0:
        highs.setOptionValue("threads", int(threads))
    if time_limit > 0:
        highs.setOptionValue("time_limit", float(time_limit))
    status = highs.passModel(lp)
    if status != highspy.HighsStatus.kOk:
        return {"success": False, "message": f"passModel failed: {status}", "pass_status": int(status)}
    run_status = highs.run()
    model_status = highs.getModelStatus()
    info = highs.getInfo()
    sol = highs.getSolution()
    y = np.array(sol.col_value, dtype=float)
    activity = mat.T.tocsr().dot(y)
    objective = float(getattr(info, "objective_function_value", math.nan))
    return {
        "success": model_status == highspy.HighsModelStatus.kOptimal,
        "run_status": int(run_status),
        "model_status": int(model_status),
        "message": highs.modelStatusToString(model_status),
        "solver": solver,
        "threads": threads,
        "time_limit": time_limit,
        "objective": objective,
        "row_dual_min": float(y.min()) if len(y) else 0.0,
        "row_dual_max": float(y.max()) if len(y) else 0.0,
        "row_dual_nonzero": int(np.sum(np.abs(y) > 1.0e-10)),
        "max_column_activity": float(activity.max()) if len(activity) else 0.0,
        "positive_column_activity_count": int(np.sum(activity > 1.0e-7)),
        "simplex_iteration_count": int(getattr(info, "simplex_iteration_count", -1)),
        "ipm_iteration_count": int(getattr(info, "ipm_iteration_count", -1)),
    }


def run(args: argparse.Namespace) -> dict[str, object]:
    t0 = time.monotonic()
    payload, columns, rem_p, quo_p = load_columns(args.columns_json)
    rows, rhs, mat = qprobe.build_equalities(rem_p, quo_p, columns)
    solve = solve_dual(
        rows,
        rhs,
        mat,
        box=args.box,
        threads=args.solver_threads,
        solver=args.highspy_solver,
        time_limit=args.time_limit,
        verbose=args.verbose,
    )
    expected = None
    if args.expected_objective is not None and solve.get("success"):
        observed = float(solve["objective"])
        expected = {
            "expected_objective": args.expected_objective,
            "abs_diff": abs(observed - args.expected_objective),
            "within_tolerance": abs(observed - args.expected_objective) <= args.objective_tolerance,
            "tolerance": args.objective_tolerance,
        }
    return {
        "schema": "eq_odl1_rung2_dual_objective_gate_v1",
        "columns_json": str(args.columns_json),
        "chart": payload.get("chart"),
        "dominant": payload.get("dominant"),
        "dominant_name": payload.get("dominant_name"),
        "tier": payload.get("tier"),
        "support": payload.get("support"),
        "selected_columns": len(columns),
        "quotient_rows": len(rows),
        "quotient_nnz": int(mat.nnz),
        "rhs_nonzero": sum(1 for x in rhs if x),
        "dual_box": args.box,
        "pair_interval_summary": pair_interval_summary(columns, str(payload.get("dominant_name"))),
        "solve": solve,
        "expected_check": expected,
        "seconds": time.monotonic() - t0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--columns-json", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--box", type=float, default=1.0)
    ap.add_argument("--highspy-solver", choices=["choose", "simplex", "ipm"], default="choose")
    ap.add_argument("--solver-threads", type=int, default=0)
    ap.add_argument("--time-limit", type=float, default=300.0)
    ap.add_argument("--expected-objective", type=float, default=None)
    ap.add_argument("--objective-tolerance", type=float, default=1.0e-4)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "columns": out["selected_columns"],
                "rows": out["quotient_rows"],
                "objective": out["solve"].get("objective"),
                "success": out["solve"].get("success"),
                "expected_check": out.get("expected_check"),
                "pair_closure_ok": out["pair_interval_summary"]["pair_closure_ok"],
                "summary": str(args.summary),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
