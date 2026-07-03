#!/usr/bin/env python3
"""Row-generation oracle for the EQ CERT-2 chart LP.

The full chart LP has a moderate number of columns but many coefficient
constraints.  This script solves an equivalent cutting-plane sequence:

1. start with every negative target coefficient row;
2. solve the restricted LP;
3. exact/float-evaluate all residual rows;
4. add violated rows and repeat.

SciPy/HiGHS remains only an oracle.  A final certificate is accepted only if
the rationalized coefficients pass the exact residual check from
_codex_eq_cert2_chart_lp.py.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import clarabel
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csc_matrix, coo_matrix, eye, vstack

import _codex_eq_cert2_chart_lp as base


def build_scaled_matrix(row_mons, columns, term_maps, target):
    row_index = {mon: i for i, mon in enumerate(row_mons)}
    row_scale = [max(1.0, abs(float(target.get(mon, Fraction(0))))) for mon in row_mons]
    entries = []
    for j, mp in enumerate(term_maps):
        for mon, coeff in mp.items():
            if mon not in row_index:
                continue
            i = row_index[mon]
            value = float(coeff)
            row_scale[i] = max(row_scale[i], abs(value))
            entries.append((i, j, value))
    matrix = coo_matrix(
        (
            [value / row_scale[i] for i, _j, value in entries],
            ([i for i, _j, _value in entries], [j for _i, j, _value in entries]),
        ),
        shape=(len(row_mons), len(columns)),
    ).tocsr()
    rhs = [float(target.get(mon, Fraction(0))) / row_scale[i] for i, mon in enumerate(row_mons)]
    return matrix, rhs


def float_residual(target, term_maps, solution):
    residual = {mon: float(coeff) for mon, coeff in target.items()}
    for value, mp in zip(solution, term_maps):
        if value <= 1e-10:
            continue
        for mon, coeff in mp.items():
            residual[mon] = residual.get(mon, 0.0) - value * float(coeff)
    return residual



def solve_lp(matrix, rhs, objective, method, oracle, time_limit, threads):
    if oracle == "scipy":
        return solve_lp_scipy(matrix, rhs, objective, method, time_limit, threads)
    if oracle == "clarabel":
        return solve_lp_clarabel(matrix, rhs, objective, time_limit, threads)
    raise ValueError(f"unknown oracle {oracle!r}")


def solve_lp_scipy(matrix, rhs, objective, method, time_limit, threads):
    options = {
        k: v
        for k, v in {
            "time_limit": time_limit if time_limit > 0 else None,
            "threads": threads if threads > 0 else None,
        }.items()
        if v is not None
    }
    return linprog(
        c=[0.0 if objective == "zero" else 1.0] * matrix.shape[1],
        A_ub=matrix,
        b_ub=rhs,
        bounds=[(0, None)] * matrix.shape[1],
        method=method,
        options=options,
    )


def solve_lp_clarabel(matrix, rhs, objective, time_limit, threads):
    n = matrix.shape[1]
    a_stack = vstack([matrix, -eye(n, format="csr")], format="csc")
    b_stack = np.array([*rhs, *([0.0] * n)], dtype=float)
    q = np.array([0.0 if objective == "zero" else 1.0] * n, dtype=float)
    p_mat = csc_matrix((n, n), dtype=float)
    cones = [clarabel.NonnegativeConeT(a_stack.shape[0])]
    settings = clarabel.DefaultSettings()
    settings.verbose = False
    if time_limit > 0:
        settings.time_limit = time_limit
    if threads > 0:
        settings.max_threads = threads
    solver = clarabel.DefaultSolver(p_mat, q, a_stack, b_stack, cones, settings)
    sol = solver.solve()

    class Result:
        pass

    res = Result()
    status = str(sol.status)
    res.status = 0 if status in {"Solved", "AlmostSolved"} else 1
    res.message = status
    res.success = res.status == 0
    res.x = np.array(sol.x, dtype=float)
    return res

def run(args):
    target, generators, meta = base.build_chart(args.chart)
    columns = base.repair_columns(target, generators, args.support, args.max_columns_per_generator or None)
    term_maps = [base.column_terms(col, generators[col.gen_index]) for col in columns]
    all_mons = sorted(set(target) | set().union(*(set(mp) for mp in term_maps)))
    row_set = {mon for mon, coeff in target.items() if coeff < 0}
    history = []
    solution = None

    for iteration in range(args.iterations):
        row_mons = sorted(row_set)
        matrix, rhs = build_scaled_matrix(row_mons, columns, term_maps, target)
        print(
            "iter",
            iteration,
            "rows",
            len(row_mons),
            "cols",
            len(columns),
            "nnz",
            matrix.nnz,
            flush=True,
        )
        res = solve_lp(matrix, rhs, args.objective, args.method, args.oracle, args.time_limit, args.threads)
        event = {
            "iteration": iteration,
            "oracle": args.oracle,
            "rows": len(row_mons),
            "columns": len(columns),
            "nonzeros": int(matrix.nnz),
            "lp_status": int(res.status),
            "lp_message": res.message,
            "success": bool(res.success),
        }
        print("LP", res.status, res.message, flush=True)
        history.append(event)
        if not res.success:
            return {
                "schema": "eq_cert2_chart_rowgen_v1",
                "chart": args.chart,
                "meta": meta,
                "history": history,
                "final": "LP_FAIL",
            }
        solution = res.x
        residual = float_residual(target, term_maps, solution)
        violated = sorted(mon for mon in all_mons if residual.get(mon, 0.0) < -args.tolerance)
        event["float_nonzero"] = int(sum(1 for x in solution if x > 1e-9))
        event["violated"] = len(violated)
        event["worst_residual"] = min((residual.get(mon, 0.0) for mon in all_mons), default=0.0)
        print(
            "violated",
            event["violated"],
            "worst",
            event["worst_residual"],
            "nonzero",
            event["float_nonzero"],
            flush=True,
        )
        if not violated:
            break
        before = len(row_set)
        row_set.update(violated)
        event["added_rows"] = len(row_set) - before
        if event["added_rows"] == 0:
            break

    exact = None
    if solution is not None:
        for max_den in args.max_den:
            coeffs = [Fraction(str(x)).limit_denominator(max_den) for x in solution]
            ok, check = base.exact_residual_check(target, generators, columns, coeffs)
            print("exact", max_den, ok, check["residual_min_coeff"], check["seed_residual"], flush=True)
            exact = {"max_denominator": max_den, "ok": ok, **check}
            if ok:
                break

    return {
        "schema": "eq_cert2_chart_rowgen_v1",
        "chart": args.chart,
        "support": args.support,
        "meta": meta,
        "columns": len(columns),
        "history": history,
        "exact": exact,
        "final": "EXACT_OK" if exact and exact.get("ok") else "NO_EXACT_CERT",
    }


def parse_ints(text: str):
    return [int(x) for x in text.split(",") if x.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", type=int, default=0)
    ap.add_argument("--support", choices=["repair", "all"], default="repair")
    ap.add_argument("--max-columns-per-generator", type=int, default=0)
    ap.add_argument("--iterations", type=int, default=6)
    ap.add_argument("--time-limit", type=float, default=60.0)
    ap.add_argument("--oracle", choices=["scipy", "clarabel"], default="scipy")
    ap.add_argument("--method", choices=["highs", "highs-ds", "highs-ipm"], default="highs")
    ap.add_argument("--objective", choices=["zero", "sum"], default="zero")
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--tolerance", type=float, default=1e-7)
    ap.add_argument("--max-den", default="10,25,50,100,250,1000")
    ap.add_argument("--summary", default="tmp/eq_cert2_chart0_rowgen_v1.json")
    args = ap.parse_args()
    args.max_den = parse_ints(args.max_den)
    out = run(args)
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    if out["final"] == "EXACT_OK":
        print("PASS exact rowgen ChartCert", args.summary)
    else:
        print(out["final"], args.summary)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

