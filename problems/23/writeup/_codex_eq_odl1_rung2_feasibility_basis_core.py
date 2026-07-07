#!/usr/bin/env python3
"""Export a full-source feasibility basis core for one Rung-2 row.

This is the broad-row replacement for the old family/dynamic-Markowitz core:

    find a floating basic feasible solution of
        A_src x <= target,  x >= 0
    over the full source column set, then export the square subsystem formed by
    basic structural columns and tight rows.  The exported core is still solved
    exactly by the modular CRT pipeline; the floating LP is only a selector.
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


def build_exact_column_maps(columns) -> list[dict[int, Fraction]]:
    maps: list[dict[int, Fraction]] = []
    for col in columns:
        d: dict[int, Fraction] = {}
        for row, coeff in col.terms:
            d[row] = d.get(row, Fraction(0)) + coeff
        maps.append(d)
    return maps


def build_float_matrix(col_maps: list[dict[int, Fraction]], rows: int):
    ri: list[int] = []
    cj: list[int] = []
    vv: list[float] = []
    for j, d in enumerate(col_maps):
        for row, coeff in d.items():
            ri.append(row)
            cj.append(j)
            vv.append(float(coeff))
    return sparse.csc_matrix((vv, (ri, cj)), shape=(rows, len(col_maps)))


def solve_basis(A, target: np.ndarray, *, solver: str, presolve: str, threads: int, time_limit: float):
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


def export_core(path: Path, target_frac, col_maps, basic_cols: list[int], tight_rows: list[int]) -> dict[str, object]:
    if len(basic_cols) != len(tight_rows):
        raise RuntimeError(f"basis core is not square: {len(basic_cols)} cols vs {len(tight_rows)} rows")

    row_pos = {row: i for i, row in enumerate(tight_rows)}
    path.parent.mkdir(parents=True, exist_ok=True)
    term_count = 0
    nnz_by_col: list[int] = []
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "meta", "dimension": len(basic_cols)}) + "\n")
        for j, source_col in enumerate(basic_cols):
            f.write(json.dumps({"type": "col", "col": j, "source_col": int(source_col)}) + "\n")
        for i, source_row in enumerate(tight_rows):
            f.write(json.dumps({"type": "selected_row", "row": i, "source_row": int(source_row)}) + "\n")
        for i, row in enumerate(tight_rows):
            f.write(json.dumps({"type": "rhs", "row": i, "value": fmt_fraction(target_frac[row])}) + "\n")
        for j, source_col in enumerate(basic_cols):
            nnz = 0
            for source_row, coeff in col_maps[source_col].items():
                i = row_pos.get(source_row)
                if i is None or coeff == 0:
                    continue
                f.write(json.dumps({"type": "term", "row": i, "col": j, "value": fmt_fraction(coeff)}) + "\n")
                term_count += 1
                nnz += 1
            nnz_by_col.append(nnz)

    return {
        "core": str(path),
        "dimension": len(basic_cols),
        "terms": term_count,
        "nnz_by_col_min": min(nnz_by_col) if nnz_by_col else 0,
        "nnz_by_col_max": max(nnz_by_col) if nnz_by_col else 0,
        "basic_cols_prefix": basic_cols[:20],
        "tight_rows_prefix": tight_rows[:20],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, required=True)
    ap.add_argument("--dominant", type=int, required=True)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--solver", choices=["simplex", "ipm", "choose"], default="simplex")
    ap.add_argument("--presolve", choices=["on", "off", "choose"], default="on")
    ap.add_argument("--threads", type=int, default=32)
    ap.add_argument("--time-limit", type=float, default=600.0)
    ap.add_argument("--out-core", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    prepared, columns, _m, _b = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    target_frac = list(prepared.p_beta)
    target = np.array([float(x) for x in target_frac], dtype=np.float64)
    col_maps = build_exact_column_maps(columns)
    A = build_float_matrix(col_maps, len(target_frac))

    h, run_status, model_status, basis, sol = solve_basis(
        A,
        target,
        solver=args.solver,
        presolve=args.presolve,
        threads=args.threads,
        time_limit=args.time_limit,
    )
    basic = highspy.HighsBasisStatus.kBasic
    basic_cols = [j for j, st in enumerate(basis.col_status) if st == basic]
    tight_rows = [i for i, st in enumerate(basis.row_status) if st != basic]
    model_status_text = h.modelStatusToString(model_status)
    payload: dict[str, object] = {
        "schema": "eq_odl1_rung2_feasibility_basis_core_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": prepared.chart.generator_names[args.dominant],
        "band": args.band,
        "support": args.support,
        "solver": args.solver,
        "presolve": args.presolve,
        "threads": args.threads,
        "run_status": str(run_status),
        "model_status": model_status_text,
        "variables": len(columns),
        "constraints": len(target_frac),
        "float_nonzero": sum(1 for x in sol.col_value if x > 1e-9),
        "basic_cols": len(basic_cols),
        "tight_rows": len(tight_rows),
        "square": len(basic_cols) == len(tight_rows),
    }
    if "Optimal" in model_status_text:
        payload["export_core"] = export_core(args.out_core, target_frac, col_maps, basic_cols, tight_rows)

    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "model_status": payload["model_status"],
        "variables": payload["variables"],
        "float_nonzero": payload["float_nonzero"],
        "basic_cols": payload["basic_cols"],
        "tight_rows": payload["tight_rows"],
        "square": payload["square"],
        "exported": "export_core" in payload,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
