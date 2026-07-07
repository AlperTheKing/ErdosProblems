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
import clarabel
import numpy as np
from scipy import sparse
from scipy.linalg import qr

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


def solve_clarabel_l1(A, target: np.ndarray, *, threads: int, max_iter: int, tol: float):
    rows, cols = A.shape
    q = np.ones(cols)
    P = sparse.csc_matrix((cols, cols))
    constraints = sparse.vstack([A, -sparse.identity(cols, format="csc")], format="csc")
    rhs = np.concatenate([target, np.zeros(cols)])
    cones = [clarabel.NonnegativeConeT(rows), clarabel.NonnegativeConeT(cols)]
    settings = clarabel.DefaultSettings()
    settings.verbose = False
    settings.max_iter = int(max_iter)
    settings.tol_gap_abs = tol
    settings.tol_gap_rel = tol
    settings.tol_feas = tol
    if threads > 0 and hasattr(settings, "max_threads"):
        settings.max_threads = int(threads)
    sol = clarabel.DefaultSolver(P, q, constraints, rhs, cones, settings).solve()
    x = np.array(sol.x)
    residual = target - A.dot(x)
    return sol, x, residual


def select_qr_rows(A, cols: list[int], residual: np.ndarray, *, tight_tol: float, oversample: int, qr_tol: float):
    need = len(cols)
    if need == 0:
        return [], {"candidate_rows": 0, "qr_rank": 0}
    tight = np.flatnonzero(np.abs(residual) <= tight_tol)
    if len(tight) < need:
        limit = min(len(residual), max(need, oversample * need + 50))
        candidates = np.argsort(np.abs(residual))[:limit]
        candidate_source = "smallest_residual"
    else:
        candidates = tight
        if len(candidates) > oversample * need + 50:
            order = np.argsort(np.abs(residual[candidates]))
            candidates = candidates[order[: oversample * need + 50]]
        candidate_source = "tight_rows"

    sub = np.asarray(A[candidates][:, cols].todense())
    _, R, piv = qr(sub.T, mode="economic", pivoting=True)
    diag = np.abs(np.diag(R))
    tol = max(float(diag.max()) * qr_tol, qr_tol) if diag.size else qr_tol
    rank = int(np.sum(diag > tol))
    selected = [int(candidates[int(i)]) for i in piv[:need]]
    return selected, {
        "candidate_rows": int(len(candidates)),
        "candidate_source": candidate_source,
        "qr_rank": rank,
        "qr_tol_effective": tol,
        "residual_abs_min": float(np.min(np.abs(residual))) if residual.size else 0.0,
        "residual_min": float(np.min(residual)) if residual.size else 0.0,
        "residual_negative_count_tol": int(np.sum(residual < -tight_tol)),
    }


def export_core(path: Path, target_frac, col_maps, basic_cols: list[int], tight_rows: list[int]) -> dict[str, object]:
    if len(basic_cols) != len(tight_rows):
        raise RuntimeError(f"basis core is not square: {len(basic_cols)} cols vs {len(tight_rows)} rows")

    row_pos = {row: i for i, row in enumerate(tight_rows)}
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.name + ".tmp")
    term_count = 0
    nnz_by_col: list[int] = []
    with tmp_path.open("w", encoding="utf-8") as f:
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
    tmp_path.replace(path)

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
    ap.add_argument("--selector", choices=["highs-basis", "clarabel-support"], default="highs-basis")
    ap.add_argument("--threads", type=int, default=32)
    ap.add_argument("--time-limit", type=float, default=600.0)
    ap.add_argument("--clarabel-max-iter", type=int, default=400)
    ap.add_argument("--clarabel-tol", type=float, default=1.0e-9)
    ap.add_argument("--support-threshold", type=float, default=1.0e-4)
    ap.add_argument("--tight-row-tol", type=float, default=1.0e-7)
    ap.add_argument("--qr-oversample", type=int, default=4)
    ap.add_argument("--qr-tol", type=float, default=1.0e-9)
    ap.add_argument("--out-core", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    prepared, columns, _m, _b = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    target_frac = list(prepared.p_beta)
    target = np.array([float(x) for x in target_frac], dtype=np.float64)
    col_maps = build_exact_column_maps(columns)
    A = build_float_matrix(col_maps, len(target_frac))

    payload: dict[str, object] = {
        "schema": "eq_odl1_rung2_feasibility_basis_core_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": prepared.chart.generator_names[args.dominant],
        "band": args.band,
        "support": args.support,
        "selector": args.selector,
        "solver": args.solver,
        "presolve": args.presolve,
        "threads": args.threads,
        "variables": len(columns),
        "constraints": len(target_frac),
    }
    if args.selector == "highs-basis":
        h, run_status, model_status, basis, sol = solve_basis(
            A,
            target,
            solver=args.solver,
            presolve=args.presolve,
            threads=args.threads,
            time_limit=args.time_limit,
        )
        basic = highspy.HighsBasisStatus.kBasic
        core_cols = [j for j, st in enumerate(basis.col_status) if st == basic]
        selected_rows = [i for i, st in enumerate(basis.row_status) if st != basic]
        model_status_text = h.modelStatusToString(model_status)
        payload.update({
            "run_status": str(run_status),
            "model_status": model_status_text,
            "float_nonzero": sum(1 for x in sol.col_value if x > 1e-9),
            "core_cols": len(core_cols),
            "selected_rows": len(selected_rows),
            "square": len(core_cols) == len(selected_rows),
        })
        if "Optimal" in model_status_text:
            payload["export_core"] = export_core(args.out_core, target_frac, col_maps, core_cols, selected_rows)
    else:
        sol, x, residual = solve_clarabel_l1(
            A,
            target,
            threads=args.threads,
            max_iter=args.clarabel_max_iter,
            tol=args.clarabel_tol,
        )
        core_cols = [int(j) for j, value in enumerate(x) if value > args.support_threshold]
        selected_rows, row_meta = select_qr_rows(
            A,
            core_cols,
            residual,
            tight_tol=args.tight_row_tol,
            oversample=args.qr_oversample,
            qr_tol=args.qr_tol,
        )
        square = len(core_cols) == len(selected_rows)
        rank_ok = row_meta.get("qr_rank", 0) >= len(core_cols)
        payload.update({
            "clarabel_status": str(sol.status),
            "clarabel_obj": float(getattr(sol, "obj_val", float("nan"))),
            "float_nonzero": sum(1 for value in x if value > 1e-9),
            "support_threshold": args.support_threshold,
            "core_cols": len(core_cols),
            "selected_rows": len(selected_rows),
            "square": square,
            "rank_ok": rank_ok,
            "row_selection": row_meta,
        })
        if str(sol.status) in {"Solved", "AlmostSolved"} and square and rank_ok:
            payload["export_core"] = export_core(args.out_core, target_frac, col_maps, core_cols, selected_rows)

    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "status": payload.get("model_status", payload.get("clarabel_status")),
        "variables": payload["variables"],
        "float_nonzero": payload["float_nonzero"],
        "core_cols": payload["core_cols"],
        "selected_rows": payload["selected_rows"],
        "square": payload["square"],
        "rank_ok": payload.get("rank_ok"),
        "exported": "export_core" in payload,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
