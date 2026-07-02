"""Direct coefficient-cone probes for the ten S7 lower-bound faces.

Diagnostic only.  For each face var=1, shift the remaining variables by 1
and try to represent the cleared S7 numerator as a coefficientwise nonnegative
polynomial plus nonnegative monomial multiples of the seven S7 slacks.
"""

from __future__ import annotations

from itertools import product

import numpy as np
import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

NAMES = ("a", "b", "c", "d", "e", "f", "x", "y", "u", "v")


def monoms(n: int, deg: int):
    for exps in product(range(deg + 1), repeat=n):
        if sum(exps) <= deg:
            yield exps


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def poly_dict(expr, vars_):
    P = sp.Poly(sp.expand(expr), *vars_)
    out = {}
    for mon, coef in P.terms():
        if coef.q != 1:
            raise ValueError("non-integer coefficient")
        out[tuple(mon)] = int(coef)
    return out


def build(face: str):
    syms = sp.symbols(" ".join(NAMES), positive=True)
    a, b, c, d, e, f, x, y, u, v = syms
    m = x * u + x * v + y * v
    N = sum(syms)
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    C0 = a + b + c + d + e + f
    num = sp.expand(2 * (N * N - 25 * m) * e * Y * Z - 75 * (e * Y * x * (u + v) * A + Z * y * v * B - e * Y * Z * C0))
    slacks = [
        e - v,
        d + e - u - v,
        b + c - x - y,
        Y - m,
        a * e + b * f + c * f - m,
        a * c + d * f + e * f - m,
        a * e + d * f + e * f - m,
    ]
    face_sym = syms[NAMES.index(face)]
    rem = [s for s in syms if s != face_sym]
    xs = sp.symbols("t0:" + str(len(rem)), nonnegative=True)
    subs = {face_sym: sp.Integer(1)}
    subs.update({s: 1 + xx for s, xx in zip(rem, xs)})
    target = poly_dict(num.subs(subs), xs)
    slack_polys = [poly_dict(s.subs(subs), xs) for s in slacks]
    return target, slack_polys, xs


def try_face(face: str, deg: int):
    target, slacks, xs = build(face)
    n = len(xs)
    mult_mons = list(monoms(n, deg))
    cols = []
    col_names = []
    touched = set(target)
    for j, slack in enumerate(slacks):
        for mm in mult_mons:
            col = {add(mm, mon): coef for mon, coef in slack.items()}
            cols.append(col)
            col_names.append((j + 1, mm))
            touched.update(col)
    touched = sorted(touched, key=lambda z: (sum(z), z))
    row_id = {m: i for i, m in enumerate(touched)}
    rows = []
    columns = []
    vals = []
    for j, col in enumerate(cols):
        for mon, coef in col.items():
            rows.append(row_id[mon])
            columns.append(j)
            vals.append(coef)
    A = coo_matrix((vals, (rows, columns)), shape=(len(touched), len(cols))).tocsr()
    rhs = np.array([target.get(mon, 0) for mon in touched], dtype=float)
    res = linprog(np.zeros(len(cols)), A_ub=A, b_ub=rhs, bounds=(0, None), method="highs")
    print(
        "face", face,
        "deg", deg,
        "target_terms", len(target),
        "mincoef", min(target.values()),
        "rows", len(touched),
        "cols", len(cols),
        "success", bool(res.success),
        "status", res.status,
    )
    if res.success:
        nz = [(col_names[i], res.x[i]) for i in range(len(cols)) if res.x[i] > 1e-8]
        print("  nonzero_slack_cols", len(nz), nz[:20])


def main() -> None:
    for deg in range(0, 2):
        for face in NAMES:
            try_face(face, deg)


if __name__ == "__main__":
    main()
