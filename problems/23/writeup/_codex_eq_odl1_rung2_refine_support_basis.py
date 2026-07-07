#!/usr/bin/env python3
"""Refine a Clarabel support into a reduced HiGHS basis core.

Input is any core-like JSONL containing `{"type":"col","source_col":...}`.
Only the source column support is used.  We solve

    min 1'x  subject to A_support x <= target, x >= 0

over the reduced support, then export the square subsystem determined by the
HiGHS basis.  The exported core is still solved and checked exactly downstream.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import highspy
import numpy as np
from scipy import sparse

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import _codex_eq_odl1_rung2_scipy_core_probe as probe


def fmt_fraction(q: Fraction) -> str:
    if q == 0:
        return "0"
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def read_support(path: Path) -> list[int]:
    cols: dict[int, int] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("type") == "col":
                cols[int(rec["col"])] = int(rec["source_col"])
    return [cols[i] for i in range(len(cols))]


def build_col_maps(columns, support_cols: list[int]) -> list[dict[int, Fraction]]:
    maps: list[dict[int, Fraction]] = []
    for source_col in support_cols:
        d: dict[int, Fraction] = {}
        for row, coeff in columns[source_col].terms:
            d[row] = d.get(row, Fraction(0)) + coeff
        maps.append(d)
    return maps


def build_matrix(col_maps: list[dict[int, Fraction]], row_count: int):
    ri: list[int] = []
    cj: list[int] = []
    vv: list[float] = []
    for j, d in enumerate(col_maps):
        for row, coeff in d.items():
            ri.append(row)
            cj.append(j)
            vv.append(float(coeff))
    return sparse.csc_matrix((vv, (ri, cj)), shape=(row_count, len(col_maps)))


def solve_reduced(A, target: np.ndarray, *, solver: str, presolve: str, threads: int, time_limit: float):
    inf = highspy.kHighsInf
    rows, cols = A.shape
    lp = highspy.HighsLp()
    lp.num_col_ = cols
    lp.num_row_ = rows
    lp.col_cost_ = np.ones(cols)
    lp.sense_ = highspy.ObjSense.kMinimize
    lp.col_lower_ = np.zeros(cols)
    lp.col_upper_ = np.full(cols, inf)
    lp.row_lower_ = np.full(rows, -inf)
    lp.row_upper_ = target.copy()

    Acsc = sparse.csc_matrix(A)
    mat = highspy.HighsSparseMatrix()
    mat.format_ = highspy.MatrixFormat.kColwise
    mat.num_col_ = cols
    mat.num_row_ = rows
    mat.start_ = Acsc.indptr.tolist()
    mat.index_ = Acsc.indices.tolist()
    mat.value_ = Acsc.data.tolist()
    lp.a_matrix_ = mat

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("solver", solver)
    h.setOptionValue("presolve", presolve)
    h.setOptionValue("time_limit", float(time_limit))
    if threads > 0:
        h.setOptionValue("threads", int(threads))
    h.passModel(lp)
    run_status = h.run()
    return h, run_status, h.getModelStatus(), h.getBasis(), h.getSolution()


def export_core(path: Path, target_frac, source_cols: list[int], col_maps, basic_reduced_cols: list[int], active_rows: list[int]):
    if len(basic_reduced_cols) != len(active_rows):
        raise RuntimeError(f"basis not square: {len(basic_reduced_cols)} cols vs {len(active_rows)} rows")
    row_pos = {row: i for i, row in enumerate(active_rows)}
    tmp_path = path.with_name(path.name + ".tmp")
    term_count = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with tmp_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "meta", "dimension": len(basic_reduced_cols)}) + "\n")
        for j, reduced_col in enumerate(basic_reduced_cols):
            f.write(json.dumps({"type": "col", "col": j, "source_col": int(source_cols[reduced_col])}) + "\n")
        for i, source_row in enumerate(active_rows):
            f.write(json.dumps({"type": "selected_row", "row": i, "source_row": int(source_row)}) + "\n")
        for i, source_row in enumerate(active_rows):
            f.write(json.dumps({"type": "rhs", "row": i, "value": fmt_fraction(target_frac[source_row])}) + "\n")
        for j, reduced_col in enumerate(basic_reduced_cols):
            for source_row, coeff in col_maps[reduced_col].items():
                i = row_pos.get(source_row)
                if i is None:
                    continue
                f.write(json.dumps({"type": "term", "row": i, "col": j, "value": fmt_fraction(coeff)}) + "\n")
                term_count += 1
    tmp_path.replace(path)
    return {"dimension": len(basic_reduced_cols), "terms": term_count, "core": str(path)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--support-core", type=Path, required=True)
    ap.add_argument("--out-core", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--solver", choices=["simplex", "ipm", "choose"], default="simplex")
    ap.add_argument("--presolve", choices=["on", "off", "choose"], default="on")
    ap.add_argument("--threads", type=int, default=32)
    ap.add_argument("--time-limit", type=float, default=600.0)
    args = ap.parse_args()

    prepared, columns, _m, _b = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    source_cols = read_support(args.support_core)
    col_maps = build_col_maps(columns, source_cols)
    A = build_matrix(col_maps, len(prepared.p_beta))
    target = np.array([float(x) for x in prepared.p_beta], dtype=np.float64)
    h, run_status, model_status, basis, sol = solve_reduced(
        A,
        target,
        solver=args.solver,
        presolve=args.presolve,
        threads=args.threads,
        time_limit=args.time_limit,
    )
    basic = highspy.HighsBasisStatus.kBasic
    basic_cols = [j for j, st in enumerate(basis.col_status) if st == basic]
    active_rows = [i for i, st in enumerate(basis.row_status) if st != basic]
    model_status_text = h.modelStatusToString(model_status)
    payload: dict[str, object] = {
        "schema": "eq_odl1_rung2_refine_support_basis_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "support_core": str(args.support_core),
        "support_columns": len(source_cols),
        "solver": args.solver,
        "presolve": args.presolve,
        "threads": args.threads,
        "run_status": str(run_status),
        "model_status": model_status_text,
        "float_nonzero": sum(1 for x in sol.col_value if x > 1e-9),
        "basic_cols": len(basic_cols),
        "active_rows": len(active_rows),
        "square": len(basic_cols) == len(active_rows),
    }
    if "Optimal" in model_status_text and payload["square"]:
        payload["export_core"] = export_core(args.out_core, prepared.p_beta, source_cols, col_maps, basic_cols, active_rows)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "model_status": model_status_text,
        "support_columns": len(source_cols),
        "float_nonzero": payload["float_nonzero"],
        "basic_cols": len(basic_cols),
        "active_rows": len(active_rows),
        "square": payload["square"],
        "exported": "export_core" in payload,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
