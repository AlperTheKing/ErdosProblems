"""Exact Fraction gate for the half-offset C5 quotient CAGE template."""

from __future__ import annotations

import argparse
from fractions import Fraction as F

import numpy as np
from scipy.optimize import linprog
import sympy as sp

from _codex_cage_c5quot_ydep import VARS, AEQ, BEQ, BOUNDS, c5_data

LAYER_CLASS = [0, 4, 3, 2, 1]
H_EXACT = [F(25, 12), F(35, 12), F(35, 12), F(25, 12)]


def ratios(k, template):
    if template == "old":
        return [
            F(2 * k - 2, 2 * k - 1),
            F(2 * k - 2, 2 * k - 3),
            F(2 * k - 2, 2 * k - 1),
            F(2 * k + 1, 2 * k - 1),
        ]
    if template == "universal":
        return [
            F(2 * k - 1, 2 * k),
            F(k, k - 1),
            F(2 * k - 1, 2 * k),
            F(k, k - 1),
        ]
    raise ValueError(template)


def float_lp(k, template):
    rf = np.array([float(x) for x in ratios(k, template)])
    sizes, _n, m, _S, cap = c5_data(k)
    denom = sizes * cap
    aub = []
    bub = []
    for cls in range(5):
        row = []
        for i, j, t in VARS:
            coeff = (rf[t] if LAYER_CLASS[i] == cls else 0.0) + (1.0 / rf[t] if LAYER_CLASS[j] == cls else 0.0)
            row.append(m * coeff)
        aub.append(row)
        bub.append(denom[cls])
    c = np.array([100 * i + 10 * j + t for i, j, t in VARS], dtype=float)
    return linprog(c, A_ub=np.array(aub), b_ub=np.array(bub), A_eq=AEQ, b_eq=BEQ, bounds=BOUNDS, method="highs")


def verify(k, beta, template):
    r = ratios(k, template)
    sizes = [k + 1, k, k + 1, k, k + 1]
    n = 5 * k + 3
    sload = [k, k + 1, k, k + 1, k]
    cap = [n - x for x in sload]
    m = k * (k + 1)

    for pair in [(i, j) for i in range(5) for j in range(i + 1, 5)]:
        acc = sum(beta[pos] for pos, (i, j, _t) in enumerate(VARS) if (i, j) == pair)
        if acc != 1:
            return False, f"pair {pair} sum {acc}"
    for t in range(4):
        acc = sum(beta[pos] for pos, (_i, _j, tt) in enumerate(VARS) if tt == t)
        if acc != H_EXACT[t]:
            return False, f"gap {t} sum {acc}"
    for cls in range(5):
        acc = F(0)
        for val, (i, j, t) in zip(beta, VARS):
            if LAYER_CLASS[i] == cls:
                acc += m * val * r[t]
            if LAYER_CLASS[j] == cls:
                acc += m * val / r[t]
        rhs = sizes[cls] * cap[cls]
        if acc > rhs:
            return False, f"class {cls} load {acc} > {rhs}"
    return True, "ok"


def exact_rows(k, template):
    r = ratios(k, template)
    rows = []
    rhs = []
    # Pair rows.
    for pair in [(i, j) for i in range(5) for j in range(i + 1, 5)]:
        rows.append([F(1) if (i, j) == pair else F(0) for i, j, _t in VARS])
        rhs.append(F(1))
    # Gap rows.
    for t in range(4):
        rows.append([F(1) if tt == t else F(0) for _i, _j, tt in VARS])
        rhs.append(H_EXACT[t])
    # Class load rows.
    sizes = [k + 1, k, k + 1, k, k + 1]
    n = 5 * k + 3
    sload = [k, k + 1, k, k + 1, k]
    cap = [n - x for x in sload]
    m = k * (k + 1)
    for cls in range(5):
        row = []
        for i, j, t in VARS:
            coeff = F(0)
            if LAYER_CLASS[i] == cls:
                coeff += m * r[t]
            if LAYER_CLASS[j] == cls:
                coeff += m / r[t]
            row.append(coeff)
        rows.append(row)
        rhs.append(F(sizes[cls] * cap[cls]))
    return rows, rhs


def sp_rational(x: F):
    return sp.Rational(x.numerator, x.denominator)


def repair_from_support(k, beta_float, template, tol=1e-9):
    support = [i for i, x in enumerate(beta_float) if x > tol]
    rows, rhs = exact_rows(k, template)
    # Always impose pair/gap rows.  Add class rows that are tight in the
    # floating LP solution.
    chosen = list(range(14))
    for ridx in range(14, 19):
        lhs = sum(float(c) * beta_float[i] for i, c in enumerate(rows[ridx]))
        if abs(lhs - float(rhs[ridx])) <= 1e-7 * max(1.0, abs(float(rhs[ridx]))):
            chosen.append(ridx)

    mat = [[sp_rational(rows[r][c]) for c in support] for r in chosen]
    vec = [sp_rational(rhs[r]) for r in chosen]
    A = sp.Matrix(mat)
    b = sp.Matrix(vec)
    sol, params = sp.linsolve((A, b)).args[0], None
    free = sorted([s for expr in sol for s in expr.free_symbols], key=str)
    if free:
        # Try zero first; this is often the lexicographic vertex.
        subs = {s: sp.Rational(0) for s in free}
        sol = [expr.subs(subs) for expr in sol]
    beta = [F(0) for _ in VARS]
    for idx, val in zip(support, sol):
        beta[idx] = F(int(sp.numer(val)), int(sp.denom(val)))
    return beta


def rationalize(k, denom, template):
    res = float_lp(k, template)
    if not res.success:
        return False, f"float LP failed: {res.message}", None
    beta = [F(float(x)).limit_denominator(denom) for x in res.x]
    ok, msg = verify(k, beta, template)
    if not ok:
        try:
            beta = repair_from_support(k, res.x, template)
            ok, msg = verify(k, beta, template)
        except Exception as exc:
            msg = f"{msg}; repair failed: {exc!r}"
    return ok, msg, beta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=2)
    ap.add_argument("--kmax", type=int, default=20)
    ap.add_argument("--denom", type=int, default=10**9)
    ap.add_argument("--template", choices=["old", "universal"], default="universal")
    ap.add_argument("--dump-fail", action="store_true")
    args = ap.parse_args()

    for k in range(args.k, args.kmax + 1):
        ok, msg, beta = rationalize(k, args.denom, args.template)
        print(f"k={k} ok={ok} msg={msg}", flush=True)
        if not ok:
            if args.dump_fail and beta is not None:
                for val, var in zip(beta, VARS):
                    if val:
                        print(val, var)
            break


if __name__ == "__main__":
    main()
