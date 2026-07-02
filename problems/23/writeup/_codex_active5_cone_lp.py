"""Coefficient-cone LP probe for active-5 seed stability.

Diagnostic only.  It tries to certify the shifted numerator

    2*(N^2 - 25m) - 75*(I(row)-N)

as a coefficientwise nonnegative polynomial plus nonnegative multiples of
selected qmax slack polynomials.
"""

from __future__ import annotations

import argparse
import contextlib
import io
from itertools import product

import numpy as np
import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_active5_symbolic_margin import parse_row, symbolic_margin
    from _codex_c5lift_weighted_quotient_gate import EQ, SIB, edges_of
    from _codex_seed_qmax_constraints import constraint, value


def poly_dict(expr, vars_):
    return {tuple(m): int(c) for m, c in sp.Poly(sp.expand(expr), *vars_).terms()}


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def total(m):
    return sum(m)


def monoms(n, deg):
    for exps in product(range(deg + 1), repeat=n):
        if sum(exps) <= deg:
            yield exps


def qmax_slacks(g6, side, weights, tight_only=True):
    n, _E = edges_of(g6)
    out = []
    for mask in range(1, (1 << n) - 1):
        if not (mask & 1):
            continue
        c = constraint(g6, side, mask)
        if c is None:
            continue
        val = value(c, weights)
        if tight_only and val != 0:
            continue
        expr = 0
        # Variables are named later as w0,...,w9.
        out.append((mask, c, val))
    return out


def slack_expr(c, w):
    return sum(sign * w[a] * w[b] for (a, b), sign in c.items())


def fmt_mask(mask, n):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", choices=["eq", "sib"], required=True)
    ap.add_argument("--side", required=True)
    ap.add_argument("--row", required=True)
    ap.add_argument("--max-deg", type=int, default=2)
    ap.add_argument("--all-constraints", action="store_true")
    args = ap.parse_args()

    g6 = EQ if args.graph == "eq" else SIB
    side = tuple(int(c) for c in args.side)
    row = parse_row(args.row)
    w, n, _M, _terms, _I, _m, _margin, numer, _denom, _poly = symbolic_margin(g6, args.side, row)
    xs = sp.symbols(f"x0:{n}", nonnegative=True)
    shift = {w[i]: xs[i] + 1 for i in range(n)}
    target = poly_dict(numer.subs(shift), xs)

    slacks = qmax_slacks(g6, side, (1,) * n, tight_only=not args.all_constraints)
    slack_polys = []
    for mask, c, val in slacks:
        slack_polys.append((mask, poly_dict(slack_expr(c, w).subs(shift), xs)))

    candidates = [
        (si, mono)
        for si in range(len(slack_polys))
        for mono in monoms(n, args.max_deg)
    ]

    touched = set(target)
    for si, mono in candidates:
        for sm in slack_polys[si][1]:
            touched.add(add(mono, sm))
    touched = sorted(touched, key=lambda m: (total(m), m))
    row_id = {m: i for i, m in enumerate(touched)}

    rows = []
    cols = []
    vals = []
    for j, (si, mono) in enumerate(candidates):
        for sm, coeff in slack_polys[si][1].items():
            rows.append(row_id[add(mono, sm)])
            cols.append(j)
            vals.append(coeff)
    matrix = coo_matrix((vals, (rows, cols)), shape=(len(touched), len(candidates))).tocsr()
    rhs = np.array([target.get(m, 0) for m in touched], dtype=float)

    res = linprog(
        c=np.zeros(len(candidates)),
        A_ub=matrix,
        b_ub=rhs,
        bounds=(0, None),
        method="highs",
        options={"presolve": True},
    )
    print("graph", args.graph)
    print("side", args.side)
    print("row", row)
    print("tight_only", not args.all_constraints)
    print("slacks", len(slack_polys))
    print("max_deg", args.max_deg)
    print("target_terms", len(target), "target_min", min(target.values()))
    print("rows", len(touched), "candidates", len(candidates))
    print("status", res.status, res.message)
    print("success", bool(res.success))
    if res.success:
        nz = [(candidates[i], res.x[i]) for i in range(len(candidates)) if res.x[i] > 1e-8]
        print("nonzero", len(nz))
        for (si, mono), coeff in nz[:120]:
            mask = slack_polys[si][0]
            print(coeff, fmt_mask(mask, n), mono)


if __name__ == "__main__":
    main()
