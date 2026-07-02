from __future__ import annotations

from fractions import Fraction
import sys

import numpy as np
import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def monoms(n, deg):
    def rec(i, left, cur):
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


def total(m):
    return sum(m)


def pterms(expr, vars_):
    return {
        tuple(m): sp.Rational(c)
        for m, c in sp.Poly(sp.expand(expr), *vars_).terms()
    }


def probe(cap: str, deg: int) -> None:
    a, b, c, d, e, f, v = sp.symbols("a b c d e f v", positive=True)
    vars_ = (a, b, c, d, e, f, v)
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
    q = 1 + v
    x = (M - v) / q
    N = S + 1 + x + q
    Phi = 2 * (N * N - 25 * M) - 75 * (x * q * A / Z + v * B / (e * Y) - S)

    phi_num, phi_den = sp.together(Phi).as_numer_denom()
    dv = sp.diff(Phi, v)
    dv_num, dv_den = sp.together(dv).as_numer_denom()
    assert phi_den != 0 and dv_den != 0

    shift = {var: var + 1 for var in vars_}
    target = pterms(phi_num.subs(shift), vars_)
    slacks = {
        "x1": x - 1,
        "v1": v - 1,
        "s1": e - v,
        "s2": d + e - q,
        "s3": b + c - x - 1,
        # On this implication branch we assume dPhi/dv >= 0.
        "dv": dv_num,
    }
    for on, om in caps.items():
        if on != cap:
            slacks[on] = om - M

    # Clear positive denominators appearing in rational slacks x1/s3 by multiplying by q.
    # Also clear derivative denominator by using dv_num directly.
    cleared = {}
    for name, expr in slacks.items():
        num, den = sp.together(expr).as_numer_denom()
        cleared[name] = num
    slack_q = [(name, pterms(expr.subs(shift), vars_)) for name, expr in cleared.items()]

    candidates = [
        (i, mono)
        for i in range(len(slack_q))
        for mono in monoms(len(vars_), deg)
    ]
    touched = set(target)
    for i, mono in candidates:
        for sm in slack_q[i][1]:
            touched.add(add(mono, sm))
    touched = sorted(touched, key=lambda m: (total(m), m))
    rid = {m: i for i, m in enumerate(touched)}

    rows = []
    cols = []
    vals = []
    for j, (si, mono) in enumerate(candidates):
        for sm, c0 in slack_q[si][1].items():
            rows.append(rid[add(mono, sm)])
            cols.append(j)
            vals.append(float(c0))
    mat = coo_matrix((vals, (rows, cols)), shape=(len(touched), len(candidates))).tocsr()
    rhs = np.array([float(target.get(m0, 0)) for m0 in touched])
    res = linprog(np.ones(len(candidates)), A_ub=mat, b_ub=rhs, bounds=(0, None), method="highs")
    print(cap, "deg", deg, "rows", len(touched), "cand", len(candidates), "success", res.success)
    if not res.success:
        return

    rem = dict(target)
    nz = 0
    for j, val in enumerate(res.x):
        if val <= 1e-9:
            continue
        fr = Fraction(float(val)).limit_denominator(1_000_000)
        coef = sp.Rational(fr.numerator, fr.denominator)
        si, mono = candidates[j]
        nz += 1
        for sm, cc in slack_q[si][1].items():
            rem[add(mono, sm)] = rem.get(add(mono, sm), 0) - coef * cc
    neg = [cc for cc in rem.values() if cc < 0]
    print("exact", "nz", nz, "neg", len(neg), "min", min(rem.values()))


if __name__ == "__main__":
    probe(sys.argv[1], int(sys.argv[2]))
