#!/usr/bin/env python3
"""SciPy active-core probe for a Rung-2 reduced-support LP solution.

This is a fallback when direct highspy basis extraction is too slow.  It solves the
same reduced-support LP with SciPy/HiGHS, computes positive columns and tight rows
from the floating solution, and reports whether the induced exact subsystem is a
plausible basis-replay target.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

import _codex_eq_odl1_rung2_support_lp as support


def fmt_fraction(q: Fraction) -> str:
    if q == 0:
        return "0"
    if abs(q.numerator).bit_length() < 1024 and q.denominator.bit_length() < 1024:
        return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"
    sign = "-" if q < 0 else ""
    return f"{sign}num_bits={abs(q.numerator).bit_length()}/den_bits={q.denominator.bit_length()}"


def build_lp(k: int, dominant: int, band: str, support_mode: str):
    prepared = support.prepare_chart(k)
    gen_names = prepared.chart.generator_names
    columns = support.selected_degree2_columns(
        prepared.p_beta,
        prepared.beta_index,
        prepared.gen_polys,
        gen_names,
        dominant,
        support_mode,
        None,
    )
    columns.extend(support.selected_band_columns(prepared.p_beta, prepared.beta_index, band, support_mode, None))
    rows = []
    cols = []
    data = []
    for j, col in enumerate(columns):
        for i, coeff in col.terms:
            rows.append(i)
            cols.append(j)
            data.append(float(coeff))
    mat = coo_matrix((data, (rows, cols)), shape=(len(prepared.betas), len(columns))).tocsr()
    b_ub = np.array([float(v) for v in prepared.p_beta], dtype=float)
    return prepared, columns, mat, b_ub


def exact_replay_subset(prepared, columns, positive_cols: list[int], active_rows: list[int], max_exact_dim: int):
    out: dict[str, object] = {
        "positive_cols": len(positive_cols),
        "active_rows": len(active_rows),
        "square_core": len(positive_cols) == len(active_rows),
        "attempted_exact_solve": False,
    }
    if len(positive_cols) != len(active_rows):
        return out
    if len(positive_cols) > max_exact_dim:
        out["exact_solve_skipped_reason"] = f"core dimension {len(positive_cols)} exceeds max_exact_dim {max_exact_dim}"
        return out
    import sympy as sp

    row_pos = {row: i for i, row in enumerate(active_rows)}
    mat = [[Fraction(0) for _ in positive_cols] for _ in active_rows]
    for cpos, col_index in enumerate(positive_cols):
        for row, coeff in columns[col_index].terms:
            rpos = row_pos.get(row)
            if rpos is not None:
                mat[rpos][cpos] = coeff
    rhs = [prepared.p_beta[row] for row in active_rows]
    out["attempted_exact_solve"] = True
    try:
        M = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in row] for row in mat])
        b = sp.Matrix([sp.Rational(x.numerator, x.denominator) for x in rhs])
        sol = M.LUsolve(b)
    except Exception as exc:
        out["exact_solve_error"] = repr(exc)
        return out
    q = [Fraction(0) for _ in columns]
    neg_sol = 0
    min_sol = None
    for col_index, value in zip(positive_cols, sol):
        val = Fraction(int(value.p), int(value.q))
        q[col_index] = val
        min_sol = val if min_sol is None else min(min_sol, val)
        if val < 0:
            neg_sol += 1
    residual = prepared.p_beta[:]
    for val, col in zip(q, columns):
        if not val:
            continue
        for i, coeff in col.terms:
            residual[i] -= coeff * val
    out.update({
        "exact_nonzero": sum(1 for v in q if v),
        "exact_negative_solution_count": neg_sol,
        "exact_min_solution": fmt_fraction(min_sol or Fraction(0)),
        "exact_negative_residual_count": sum(1 for r in residual if r < 0),
        "exact_min_residual": fmt_fraction(min(residual) if residual else Fraction(0)),
        "exact_ok": neg_sol == 0 and all(r >= 0 for r in residual),
    })
    return out



def stable_column_weight(col, mode: str) -> float:
    if mode == "sum":
        return 1.0
    # Deterministic small perturbations: objective stays positive but breaks ties.
    h = 1469598103934665603
    for part in (col.kind, col.name, str(col.multiplier_exp)):
        for b in part.encode("utf-8"):
            h ^= b
            h = (h * 1099511628211) & ((1 << 64) - 1)
    frac = (h % 1000003) / 1000003.0
    if mode == "lex-small":
        return 1.0 + 1.0e-6 * frac
    if mode == "lex-large":
        return 1.0 + 1.0e-3 * frac
    if mode == "family":
        family = {"gen": 0.0, "delta": 0.37, "band": 0.73}.get(col.kind, 0.19)
        return 1.0 + 1.0e-4 * family + 1.0e-7 * frac
    raise ValueError(mode)

def run(args):
    prepared, columns, mat, b_ub = build_lp(args.chart, args.dominant, args.band, args.support)
    c = np.array([stable_column_weight(col, args.objective) for col in columns], dtype=float)
    res = linprog(c=c, A_ub=mat, b_ub=b_ub, bounds=[(0, None)] * len(columns), method=args.method, options={"time_limit": args.time_limit})
    out: dict[str, object] = {
        "schema": "eq_odl1_rung2_scipy_core_probe_v1",
        "chart": args.chart,
        "dominant": args.dominant,
        "dominant_name": prepared.chart.generator_names[args.dominant],
        "band": args.band,
        "support": args.support,
        "method": args.method,
        "objective_mode": args.objective,
        "variables": len(columns),
        "constraints": len(prepared.betas),
        "lp_status": int(res.status),
        "lp_message": res.message,
        "success": bool(res.success),
    }
    if not res.success:
        return out
    residual = b_ub - mat.dot(res.x)
    marginals = np.array(res.ineqlin.marginals, dtype=float)
    lower_marginals = np.array(res.lower.marginals, dtype=float)
    positive_cols = [i for i, x in enumerate(res.x) if x > args.x_tol]
    active_rows = [i for i, r in enumerate(residual) if abs(r) <= args.row_tol]
    dual_rows = [i for i, y in enumerate(marginals) if abs(y) > args.dual_tol]
    lower_dual_cols = [i for i, y in enumerate(lower_marginals) if abs(y) > args.dual_tol]
    out.update({
        "objective": float(res.fun),
        "float_nonzero": len(positive_cols),
        "float_min_residual": float(residual.min()),
        "float_max_residual": float(residual.max()),
        "float_active_rows": len(active_rows),
        "float_dual_rows": len(dual_rows),
        "float_lower_dual_cols": len(lower_dual_cols),
        "x_tol": args.x_tol,
        "row_tol": args.row_tol,
        "dual_tol": args.dual_tol,
    })
    out["exact_subset_probe"] = exact_replay_subset(prepared, columns, positive_cols, active_rows, args.max_exact_dim)
    if len(dual_rows) == len(positive_cols):
        out["exact_dualrow_subset_probe"] = exact_replay_subset(prepared, columns, positive_cols, dual_rows, args.max_exact_dim)
    else:
        out["exact_dualrow_subset_probe"] = {
            "positive_cols": len(positive_cols),
            "dual_rows": len(dual_rows),
            "square_core": False,
            "attempted_exact_solve": False,
        }
    if args.qr_select and len(dual_rows) >= len(positive_cols) and positive_cols:
        import scipy.linalg as la
        sub = mat[dual_rows, :][:, positive_cols].toarray()
        # Pivot columns of sub.T, which selects independent rows of sub.
        _q, rmat, piv = la.qr(sub.T, mode="economic", pivoting=True)
        diag = np.abs(np.diag(rmat))
        rank = int(np.sum(diag > args.qr_tol))
        selected_rows = [int(dual_rows[int(p)]) for p in piv[: min(len(positive_cols), len(piv))]]
        out["qr_dualrow_selection"] = {
            "candidate_dual_rows": len(dual_rows),
            "positive_cols": len(positive_cols),
            "rank_estimate": rank,
            "qr_tol": args.qr_tol,
            "square_independent_core_exists_float": rank >= len(positive_cols),
            "selected_dual_rows_prefix": selected_rows[: args.store_selected_prefix],
        }
        if rank >= len(positive_cols):
            out["exact_qr_subset_probe"] = exact_replay_subset(prepared, columns, positive_cols, selected_rows[:len(positive_cols)], args.max_exact_dim)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--dominant", type=int, default=7)
    ap.add_argument("--band", default="near_2s_minus_1")
    ap.add_argument("--support", default="negative")
    ap.add_argument("--method", default="highs", choices=["highs", "highs-ds", "highs-ipm"])
    ap.add_argument("--objective", default="sum", choices=["sum", "lex-small", "lex-large", "family"])
    ap.add_argument("--time-limit", type=float, default=60.0)
    ap.add_argument("--x-tol", type=float, default=1e-9)
    ap.add_argument("--row-tol", type=float, default=1e-8)
    ap.add_argument("--dual-tol", type=float, default=1e-9)
    ap.add_argument("--max-exact-dim", type=int, default=700)
    ap.add_argument("--qr-select", action="store_true")
    ap.add_argument("--qr-tol", type=float, default=1e-9)
    ap.add_argument("--store-selected-prefix", type=int, default=20)
    ap.add_argument("--summary", type=Path, default=Path("tmp/eq_odl1_rung2_scipy_core_probe_v1.json"))
    args = ap.parse_args()
    out = run(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "success": out.get("success"),
        "float_nonzero": out.get("float_nonzero"),
        "float_active_rows": out.get("float_active_rows"),
        "exact_subset_probe": out.get("exact_subset_probe"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()




