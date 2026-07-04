#!/usr/bin/env python3
"""Export modular row bases for a Rung-2 reduced LP core.

Modes:
  sparse-row: previous baseline, rows sorted by original sparsity.
  static-markowitz: columns sorted by original sparsity; pivot row selected by
  original row sparsity and exact coefficient bit-size.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_modular_replay as replay


def solve_lp(args):
    prepared, columns, mat, b_ub = probe.build_lp(args.chart, args.dominant, args.band, args.support)
    c = np.array([probe.stable_column_weight(col, args.objective) for col in columns], dtype=float)
    res = linprog(
        c=c,
        A_ub=mat,
        b_ub=b_ub,
        bounds=[(0, None)] * len(columns),
        method=args.method,
        options={"time_limit": args.time_limit},
    )
    if not res.success:
        return prepared, columns, mat, {"success": False, "lp_status": int(res.status), "lp_message": res.message}
    residual = b_ub - mat.dot(res.x)
    marginals = np.array(res.ineqlin.marginals, dtype=float)
    positive_cols = [i for i, x in enumerate(res.x) if x > args.x_tol]
    dual_rows = [i for i, y in enumerate(marginals) if abs(y) > args.dual_tol]
    return prepared, columns, mat, {
        "success": True,
        "lp_status": int(res.status),
        "lp_message": res.message,
        "objective": float(res.fun),
        "positive_cols": positive_cols,
        "dual_rows": dual_rows,
        "float_nonzero": len(positive_cols),
        "candidate_dual_rows": len(dual_rows),
        "float_min_residual": float(residual.min()),
        "float_max_residual": float(residual.max()),
    }


def coeff_bit_cost(q: Fraction) -> int:
    return abs(q.numerator).bit_length() + q.denominator.bit_length()


def build_candidate_matrix(columns, positive_cols: list[int], dual_rows: list[int], p: int):
    n = len(positive_cols)
    m = len(dual_rows)
    row_local = {row: i for i, row in enumerate(dual_rows)}
    mat = np.zeros((m, n), dtype=np.int64)
    cost = np.zeros((m, n), dtype=np.int16)
    for cpos, col_index in enumerate(positive_cols):
        for row, coeff in columns[col_index].terms:
            rpos = row_local.get(row)
            if rpos is not None:
                mat[rpos, cpos] = (int(mat[rpos, cpos]) + replay.frac_mod(coeff, p)) % p
                old = int(cost[rpos, cpos])
                new = coeff_bit_cost(coeff)
                cost[rpos, cpos] = new if old == 0 else min(old, new)
    row_nnz = np.count_nonzero(mat, axis=1)
    col_nnz = np.count_nonzero(mat, axis=0)
    return mat, cost, row_nnz, col_nnz


def select_sparse_rows(mat: np.ndarray, dual_rows: list[int], row_nnz: np.ndarray, p: int, n: int):
    order = sorted(range(len(dual_rows)), key=lambda i: (int(row_nnz[i]), int(dual_rows[i])))
    work = mat[order, :].copy()
    labels = [int(dual_rows[i]) for i in order]
    rank = 0
    pivot_cols: list[int] = []
    for col in range(n):
        nz = np.flatnonzero(work[rank:, col])
        if nz.size == 0:
            continue
        piv = rank + int(nz[0])
        if piv != rank:
            work[[rank, piv], :] = work[[piv, rank], :]
            labels[rank], labels[piv] = labels[piv], labels[rank]
        inv = pow(int(work[rank, col]), -1, p)
        work[rank, col:] = (work[rank, col:] * inv) % p
        if rank + 1 < work.shape[0]:
            factors = work[rank + 1 :, col].copy()
            rows = np.flatnonzero(factors)
            if rows.size:
                sub = rank + 1 + rows
                work[sub, col:] = (work[sub, col:] - factors[rows, None] * work[rank, col:]) % p
        pivot_cols.append(col)
        rank += 1
        if rank == n:
            break
    return labels[:rank], list(range(n)), pivot_cols


def select_static_markowitz_rows(
    mat: np.ndarray,
    coeff_cost: np.ndarray,
    dual_rows: list[int],
    row_nnz: np.ndarray,
    col_nnz: np.ndarray,
    p: int,
    n: int,
):
    col_order = sorted(range(n), key=lambda j: (int(col_nnz[j]), int(j)))
    work = mat[:, col_order].copy()
    cost = coeff_cost[:, col_order]
    labels = [int(r) for r in dual_rows]
    row_weight = np.array([max(1, int(x)) for x in row_nnz], dtype=np.int64)
    col_weight = np.array([max(1, int(col_nnz[j])) for j in col_order], dtype=np.int64)
    rank = 0
    pivot_cols: list[int] = []
    for col in range(n):
        rel = np.flatnonzero(work[rank:, col])
        if rel.size == 0:
            continue
        rows = rank + rel
        # Static Markowitz-style score. The large factor keeps sparsity primary;
        # coefficient bit-size breaks ties toward smaller exact entries.
        scores = row_weight[rows] * col_weight[col] * 1024 + cost[rows, col].astype(np.int64)
        best = int(rows[int(np.argmin(scores))])
        if best != rank:
            work[[rank, best], :] = work[[best, rank], :]
            row_weight[[rank, best]] = row_weight[[best, rank]]
            labels[rank], labels[best] = labels[best], labels[rank]
        inv = pow(int(work[rank, col]), -1, p)
        work[rank, col:] = (work[rank, col:] * inv) % p
        if rank + 1 < work.shape[0]:
            factors = work[rank + 1 :, col].copy()
            nz = np.flatnonzero(factors)
            if nz.size:
                sub = rank + 1 + nz
                work[sub, col:] = (work[sub, col:] - factors[nz, None] * work[rank, col:]) % p
        pivot_cols.append(col_order[col])
        rank += 1
        if rank == n:
            break
    return labels[:rank], col_order, pivot_cols


def select_dynamic_markowitz_rows(
    mat: np.ndarray,
    coeff_cost: np.ndarray,
    dual_rows: list[int],
    p: int,
    n: int,
):
    """Select a square modular basis with dynamic Markowitz-style pivots.

    This keeps the same exported core format as the previous selectors, but
    chooses pivots from the current active sparse matrix rather than from a
    fixed column order. The primary score is the classical fill estimate
    (row_nnz - 1) * (col_nnz - 1); the secondary score is the original exact
    coefficient bit cost when the pivot is an original entry, with generated
    fill entries deliberately treated as expensive.
    """

    row_dicts: list[dict[int, int]] = []
    col_rows: list[set[int]] = [set() for _ in range(n)]
    for i in range(mat.shape[0]):
        nz = np.flatnonzero(mat[i])
        row: dict[int, int] = {}
        for j0 in nz:
            j = int(j0)
            value = int(mat[i, j]) % p
            if value:
                row[j] = value
                col_rows[j].add(i)
        row_dicts.append(row)

    active_rows: set[int] = set(range(mat.shape[0]))
    active_cols: set[int] = set(range(n))
    selected_rows: list[int] = []
    pivot_cols: list[int] = []
    fill_cost = 4096

    for _rank in range(n):
        best: tuple[int, int, int, int, int] | None = None
        best_row = -1
        best_col = -1
        for i in active_rows:
            row = row_dicts[i]
            active_entries = [j for j, value in row.items() if j in active_cols and value]
            rnnz = len(active_entries)
            if rnnz == 0:
                continue
            for j in active_entries:
                cnnz = sum(1 for rr in col_rows[j] if rr in active_rows)
                if cnnz == 0:
                    continue
                original_cost = int(coeff_cost[i, j]) if int(coeff_cost[i, j]) else fill_cost
                score = ((rnnz - 1) * (cnnz - 1), original_cost, rnnz + cnnz, int(dual_rows[i]), j)
                if best is None or score < best:
                    best = score
                    best_row = i
                    best_col = j
        if best is None:
            break

        pivot_value = row_dicts[best_row][best_col] % p
        inv = pow(int(pivot_value), -1, p)
        pivot_row = {
            j: (value * inv) % p
            for j, value in row_dicts[best_row].items()
            if j in active_cols and value
        }
        pivot_row[best_col] = 1

        affected = [i for i in list(col_rows[best_col]) if i in active_rows and i != best_row]
        for i in affected:
            factor = row_dicts[i].get(best_col, 0) % p
            if not factor:
                continue
            row = row_dicts[i]
            # Maintain column incidence sets exactly so later Markowitz scores
            # see fill introduced by previous eliminations.
            for j, pval in pivot_row.items():
                old = row.get(j, 0)
                new = (old - factor * pval) % p
                if new:
                    row[j] = new
                    col_rows[j].add(i)
                elif old:
                    del row[j]
                    col_rows[j].discard(i)

        active_rows.remove(best_row)
        active_cols.remove(best_col)
        selected_rows.append(int(dual_rows[best_row]))
        pivot_cols.append(best_col)

        for i in list(col_rows[best_col]):
            row_dicts[i].pop(best_col, None)
        col_rows[best_col].clear()

    return selected_rows, pivot_cols, pivot_cols

def fmt_fraction(q: Fraction) -> str:
    return replay.fmt_fraction(q)


def export_core(path: Path, prepared, columns, positive_cols: list[int], selected_rows: list[int]):
    terms, rhs, nnz_by_col = replay.extract_core(prepared, columns, positive_cols, selected_rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "meta", "dimension": len(positive_cols), "terms": len(terms)}) + "\n")
        for j, col_index in enumerate(positive_cols):
            f.write(json.dumps({"type": "col", "col": j, "source_col": int(col_index)}) + "\n")
        for i, row_index in enumerate(selected_rows):
            f.write(json.dumps({"type": "selected_row", "row": i, "source_row": int(row_index)}) + "\n")
        for i, val in enumerate(rhs):
            f.write(json.dumps({"type": "rhs", "row": i, "value": fmt_fraction(val)}) + "\n")
        for i, j, coeff in terms:
            f.write(json.dumps({"type": "term", "row": i, "col": j, "value": fmt_fraction(coeff)}) + "\n")
    return {
        "dimension": len(positive_cols),
        "terms": len(terms),
        "rhs_nonzero": sum(1 for x in rhs if x),
        "nnz_by_col_min": min(nnz_by_col) if nnz_by_col else 0,
        "nnz_by_col_max": max(nnz_by_col) if nnz_by_col else 0,
        "export_core": str(path),
    }


def run(args):
    prepared, columns, _mat, meta = solve_lp(args)
    out: dict[str, object] = {
        "schema": "eq_odl1_rung2_sparse_row_core_v2",
        "chart": args.chart,
        "dominant": args.dominant,
        "band": args.band,
        "support": args.support,
        "objective_mode": args.objective,
        "selector": args.selector,
        "lp": {k: v for k, v in meta.items() if k not in {"positive_cols", "dual_rows"}},
    }
    if not meta.get("success"):
        return out
    positive_cols = list(meta["positive_cols"])
    dual_rows = list(meta["dual_rows"])
    p = replay.prime_list(1)[0]
    mat, coeff_cost, row_nnz, col_nnz = build_candidate_matrix(columns, positive_cols, dual_rows, p)
    if args.selector == "sparse-row":
        selected_rows, col_order, pivot_cols = select_sparse_rows(mat, dual_rows, row_nnz, p, len(positive_cols))
    elif args.selector == "static-markowitz":
        selected_rows, col_order, pivot_cols = select_static_markowitz_rows(mat, coeff_cost, dual_rows, row_nnz, col_nnz, p, len(positive_cols))
    elif args.selector == "dynamic-markowitz":
        selected_rows, col_order, pivot_cols = select_dynamic_markowitz_rows(mat, coeff_cost, dual_rows, p, len(positive_cols))
    else:
        raise ValueError(args.selector)
    ordered_positive_cols = [positive_cols[j] for j in col_order]
    row_index = {r: i for i, r in enumerate(dual_rows)}
    out["selection"] = {
        "prime": p,
        "rank": len(selected_rows),
        "needed": len(positive_cols),
        "selected_rows_prefix": selected_rows[:20],
        "pivot_cols_prefix": pivot_cols[:20],
        "ordered_positive_cols_prefix": ordered_positive_cols[:20],
        "candidate_row_nnz_min": int(row_nnz.min()) if len(row_nnz) else 0,
        "candidate_row_nnz_max": int(row_nnz.max()) if len(row_nnz) else 0,
        "candidate_col_nnz_min": int(col_nnz.min()) if len(col_nnz) else 0,
        "candidate_col_nnz_max": int(col_nnz.max()) if len(col_nnz) else 0,
        "selected_row_nnz_sum": int(sum(row_nnz[row_index[r]] for r in selected_rows)) if selected_rows else 0,
    }
    if len(selected_rows) == len(positive_cols):
        out["core"] = export_core(args.export_core, prepared, columns, ordered_positive_cols, selected_rows)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--dominant", type=int, default=7)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--method", default="highs")
    ap.add_argument("--objective", default="lex-small", choices=["sum", "lex-small", "lex-large", "family"])
    ap.add_argument("--selector", default="sparse-row", choices=["sparse-row", "static-markowitz", "dynamic-markowitz"])
    ap.add_argument("--time-limit", type=float, default=80.0)
    ap.add_argument("--x-tol", type=float, default=1e-9)
    ap.add_argument("--dual-tol", type=float, default=1e-9)
    ap.add_argument("--export-core", type=Path, required=True)
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_sparse_row_core_v2.json"))
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"lp": out.get("lp"), "selection": out.get("selection"), "core": out.get("core")}, sort_keys=True))


if __name__ == "__main__":
    main()
