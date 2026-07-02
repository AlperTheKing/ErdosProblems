"""Exactifying verifier for y=1,x=1,u=1,s_j=0, j=4..7.

This closes the u=1 endpoint leaves from the y=1,x=1 capacity v-fiber
reduction.  The script first finds a sparse nonnegative slack-cone certificate
with a deterministic linear program, then rationalizes the coefficients and
verifies the certificate exactly in SymPy.

The exact branch equations are x=y=u=1 and capacity s_j=0, hence

    v = (M_j - 1)/2,

where M_j is the active capacity right-hand side.  After shifting a..f by 1,
the cleared numerator of Phi is checked to be coefficientwise nonnegative after
subtracting nonnegative rational multiples of the shifted feasibility slacks.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product

import numpy as np
import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def monoms(n: int, deg: int):
    def rec(i: int, left: int, cur: list[int]):
        if i == n:
            yield tuple(cur)
            return
        for k in range(left + 1):
            cur.append(k)
            yield from rec(i + 1, left - k, cur)
            cur.pop()

    yield from rec(0, deg, [])


def add(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x + y for x, y in zip(a, b))


def total(m: tuple[int, ...]) -> int:
    return sum(m)


def poly_terms(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> dict[tuple[int, ...], sp.Rational]:
    return {tuple(m): sp.Rational(c) for m, c in sp.Poly(sp.expand(expr), *vars_).terms()}


def build_branch(cap_name: str, max_deg: int = 5):
    a, b, c, d, e, f = sp.symbols("a b c d e f", positive=True)
    vars_ = (a, b, c, d, e, f)
    x = sp.Integer(1)
    y = sp.Integer(1)
    u = sp.Integer(1)

    S = a + b + c + d + e + f
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    caps = {
        "s4": Y,
        "s5": a * e + b * f + c * f,
        "s6": a * c + d * f + e * f,
        "s7": a * e + d * f + e * f,
    }
    Mj = caps[cap_name]
    v = sp.Rational(1, 2) * (Mj - 1)
    m = Mj
    N = S + x + y + u + v
    Phi = 2 * (N * N - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - S)
    num = sp.together(Phi).as_numer_denom()[0]
    shift = {var: var + 1 for var in vars_}
    target = poly_terms(num.subs(shift), vars_)

    slacks = {
        "v": v - 1,
        "s1": e - v,
        "s2": d + e - (u + v),
        "s3": b + c - 2,
    }
    for other_name, other_M in caps.items():
        if other_name != cap_name:
            slacks[other_name] = other_M - Mj

    slack_polys = [(name, poly_terms(expr.subs(shift), vars_)) for name, expr in slacks.items()]
    candidates = [(si, mono) for si in range(len(slack_polys)) for mono in monoms(6, max_deg)]

    touched = set(target)
    for si, mono in candidates:
        for sm in slack_polys[si][1]:
            touched.add(add(mono, sm))
    touched = sorted(touched, key=lambda m: (total(m), m))
    row_id = {m: i for i, m in enumerate(touched)}

    rows: list[int] = []
    cols: list[int] = []
    vals: list[float] = []
    for j, (si, mono) in enumerate(candidates):
        for sm, coeff in slack_polys[si][1].items():
            rows.append(row_id[add(mono, sm)])
            cols.append(j)
            vals.append(float(coeff))
    matrix = coo_matrix((vals, (rows, cols)), shape=(len(touched), len(candidates))).tocsr()
    rhs = np.array([float(target.get(m, 0)) for m in touched])
    return vars_, target, slack_polys, candidates, matrix, rhs


def solve_and_verify(cap_name: str) -> int:
    _vars, target, slack_polys, candidates, matrix, rhs = build_branch(cap_name)
    res = linprog(
        np.ones(len(candidates)),
        A_ub=matrix,
        b_ub=rhs,
        bounds=(0, None),
        method="highs",
    )
    assert res.success, (cap_name, res.status, res.message)

    remainder = dict(target)
    nz = 0
    for j, value in enumerate(res.x):
        if value <= 1e-8:
            continue
        frac = Fraction(float(value)).limit_denominator(1_000_000)
        coeff = sp.Rational(frac.numerator, frac.denominator)
        if coeff <= 0:
            continue
        nz += 1
        si, mono = candidates[j]
        for sm, slack_coeff in slack_polys[si][1].items():
            mm = add(mono, sm)
            remainder[mm] = remainder.get(mm, sp.Rational(0)) - coeff * slack_coeff

    negatives = [(m, c) for m, c in remainder.items() if c < 0]
    assert not negatives, (cap_name, negatives[:10])
    return nz


def main() -> None:
    counts = {cap: solve_and_verify(cap) for cap in ("s4", "s5", "s6", "s7")}
    print("PASS y=1,x=1,u=1 capacity endpoints s4..s7 exactified slack certificates", counts)


if __name__ == "__main__":
    main()
