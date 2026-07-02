from __future__ import annotations

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


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def total(a):
    return sum(a)


def pterms(expr, vars_):
    return {tuple(m): sp.Rational(c) for m, c in sp.Poly(sp.expand(expr), *vars_).terms()}


def probe(cap: str, deg: int) -> bool:
    a, b, c, d, e, f = sp.symbols("a b c d e f", positive=True)
    y = sp.Integer(1)
    u = sp.Integer(1)
    v = sp.Integer(1)
    q = 1 + v
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
    M = caps[cap]
    x = (M - v) / q
    m = x * q + v
    N = S + x + y + u + v
    Phi = 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - S)
    target_expr = sp.together(Phi).as_numer_denom()[0]
    vars_ = (a, b, c, d, e, f)
    shift = {z: z + 1 for z in vars_}
    target = pterms(target_expr.subs(shift), vars_)

    slacks = {
        "x1": x - 1,
        "s2": d + e - 2,
        "s3": b + c - 1 - x,
    }
    for name, expr in caps.items():
        if name != cap:
            slacks[name] = expr - M

    slack_terms = [(name, pterms(sp.together(expr).as_numer_denom()[0].subs(shift), vars_)) for name, expr in slacks.items()]
    candidates = [(i, mono) for i in range(len(slack_terms)) for mono in monoms(len(vars_), deg)]

    touched = set(target)
    for i, mono in candidates:
        for sm in slack_terms[i][1]:
            touched.add(add(mono, sm))
    touched = sorted(touched, key=lambda z: (total(z), z))
    row = {m0: i for i, m0 in enumerate(touched)}

    rows = []
    cols = []
    vals = []
    for j, (si, mono) in enumerate(candidates):
        for sm, coef in slack_terms[si][1].items():
            rows.append(row[add(mono, sm)])
            cols.append(j)
            vals.append(float(coef))
    mat = coo_matrix((vals, (rows, cols)), shape=(len(touched), len(candidates))).tocsr()
    rhs = np.array([float(target.get(m0, 0)) for m0 in touched])
    res = linprog(np.ones(len(candidates)), A_ub=mat, b_ub=rhs, bounds=(0, None), method="highs")
    print(cap, "deg", deg, "rows", len(touched), "cand", len(candidates), "success", res.success)
    return bool(res.success)


def main() -> None:
    for deg in range(0, 5):
        ok_all = True
        for cap in ("s4", "s5", "s6", "s7"):
            ok_all = probe(cap, deg) and ok_all
        if ok_all:
            break


if __name__ == "__main__":
    main()
