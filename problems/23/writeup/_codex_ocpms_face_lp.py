"""LP probe for the dominant endpoint face of the seven-cut PMS target.

Dominant endpoint face:

    w9=w5, w7=w6, w2=w3, w1=w4.

With core variables

    a=w0, b=w3, c=w4, p=w5, q=w6, r=w8,

the remaining quadratic cut constraints are:

    A = a*q + b*r + p*r - (c*p + b*q + q*p) >= 0
    B = a*p + b*r + p*r - (c*p + b*q + q*p) >= 0
    C = a*q + c*r + q*r - (c*p + b*q + q*p) >= 0

This searches for a coefficientwise certificate after shifting every core
variable by one.  It is only a proof-route probe; any positive result needs
an exact rational cleanup before use.
"""

from itertools import product

import numpy as np
import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


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


def face_target_and_constraints():
    a, b, c, p, q, r = sp.symbols("a b c p q r")
    vars_ = (a, b, c, p, q, r)
    w = [a, c, b, b, c, p, q, q, r, p]
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w

    z27 = w6 * (w0 * w5 + w3 * w8 + w5 * w8)
    i27 = w0 * w5 + w0 * w6 + w3 * w6 + w3 * w8 + w5 * w6 + w5 * w8 + w6 * w8
    z19 = w5 * (w0 * w6 + w4 * w8 + w6 * w8)
    i19 = w0 * w5 + w0 * w6 + w4 * w5 + w4 * w8 + w5 * w6 + w5 * w8 + w6 * w8
    z79 = (
        w0 * w5 * w6
        + w3 * w4 * w8
        + w3 * w6 * w8
        + w4 * w5 * w8
        + w5 * w6 * w8
    )
    i79 = (
        w0 * w5
        + w0 * w6
        + w3 * w4
        + w3 * w6
        + w3 * w8
        + w4 * w5
        + w4 * w8
        + w5 * w6
        + w5 * w8
        + w6 * w8
    )

    n = sum(w)
    m = w1 * w9 + w2 * w7 + w7 * w9
    endpoint = w1 + w2 + w7 + w9
    den = z27 * z19 * z79
    numer = (2 * (n * n - 25 * m) - 75 * (endpoint - n)) * den
    numer -= 75 * w2 * w7 * i27 * z19 * z79
    numer -= 75 * w1 * w9 * i19 * z27 * z79
    numer -= 75 * w7 * w9 * i79 * z27 * z19

    g = [
        w0 * w6 + w3 * w8 + w5 * w8 - m,
        w0 * w5 + w3 * w8 + w5 * w8 - m,
        w0 * w6 + w4 * w8 + w6 * w8 - m,
    ]

    x = sp.symbols("x0:6")
    shift = {v: x[i] + 1 for i, v in enumerate(vars_)}
    return poly_dict(numer.subs(shift), x), [poly_dict(expr.subs(shift), x) for expr in g]


def solve(max_deg):
    target, constraints = face_target_and_constraints()
    nvars = 6
    candidates = [(gi, mono) for gi in range(len(constraints)) for mono in monoms(nvars, max_deg)]
    touched = set(target)
    for gi, mono in candidates:
        for gm in constraints[gi]:
            touched.add(add(mono, gm))
    touched = sorted(touched, key=lambda m: (total(m), m))
    row_id = {m: i for i, m in enumerate(touched)}

    rows = []
    cols = []
    vals = []
    for j, (gi, mono) in enumerate(candidates):
        for gm, coeff in constraints[gi].items():
            rows.append(row_id[add(mono, gm)])
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
    print("degree", max_deg, "terms", len(target), "candidates", len(candidates), "status", res.status, res.message)
    if res.success:
        nz = [(candidates[i], res.x[i]) for i in range(len(candidates)) if res.x[i] > 1e-8]
        print("nonzero", len(nz))
        for item in nz[:120]:
            print(item)
    return res.success


def main():
    for deg in range(0, 7):
        if solve(deg):
            break


if __name__ == "__main__":
    main()
