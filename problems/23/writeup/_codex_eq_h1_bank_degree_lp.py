"""Search for bounded-degree EQ h=1 bank cone certificates.

Multiplier ansatz for degree d:

    P_j = sum_{|alpha|<=d} c_{j,alpha} x^alpha,  c>=0.

Search uses scipy; exact acceptance checks rationalized coefficients by SymPy.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import combinations_with_replacement

import sympy as sp
from scipy.optimize import linprog


xs = sp.symbols("x0:10", nonnegative=True)
ws = [1 + x for x in xs]
w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = ws

m = w1 * w9 + w2 * w7 + w7 * w9
N = sum(ws)
eta25 = sp.expand(N * N - 25 * m)
F = [
    w5 - w9,
    w6 - w7,
    w3 + w5 - w2 - w9,
    w4 + w6 - w1 - w7,
    w0 * w6 + w3 * w8 + w5 * w8 - m,
    w0 * w5 + w3 * w8 + w5 * w8 - m,
    w0 * w6 + w4 * w8 + w6 * w8 - m,
]


def monomials(max_degree: int):
    out = [sp.Integer(1)]
    for degree in range(1, max_degree + 1):
        for combo in combinations_with_replacement(range(len(xs)), degree):
            mon = sp.Integer(1)
            for i in combo:
                mon *= xs[i]
            out.append(mon)
    return out


def coeff_map(expr: sp.Expr) -> dict[tuple[int, ...], Fraction]:
    poly = sp.Poly(sp.expand(expr), *xs)
    out = {}
    for monom, coeff in poly.terms():
        out[monom] = Fraction(int(coeff.p), int(coeff.q))
    return out


def exact_expr(coeffs: list[Fraction], mons: list[sp.Expr]) -> sp.Expr:
    idx = 0
    expr = eta25
    for f in F:
        mult = 0
        for mon in mons:
            c = coeffs[idx]
            idx += 1
            mult += sp.Rational(c.numerator, c.denominator) * mon
        expr -= f * mult
    return sp.expand(expr)


def exact_check(coeffs: list[Fraction], mons: list[sp.Expr]) -> tuple[bool, int, Fraction, list[Fraction]]:
    poly = sp.Poly(exact_expr(coeffs, mons), *xs)
    vals = [Fraction(int(c.p), int(c.q)) for c in poly.coeffs()]
    neg = [v for v in vals if v < 0]
    return not neg, len(vals), min(vals), neg[:10]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--degree", type=int, default=2)
    args = ap.parse_args()
    mons = monomials(args.degree)
    print("mons", len(mons), "vars", 7 * len(mons))

    base = coeff_map(eta25)
    term_maps = []
    for f in F:
        for mon in mons:
            term_maps.append(coeff_map(f * mon))
    monom_set = sorted(set(base) | set().union(*(set(mp) for mp in term_maps)))
    print("constraints", len(monom_set))

    a_ub = []
    b_ub = []
    for monom in monom_set:
        a_ub.append([float(mp.get(monom, Fraction(0))) for mp in term_maps])
        b_ub.append(float(base.get(monom, Fraction(0))))
    res = linprog(
        c=[1.0] * len(term_maps),
        A_ub=a_ub,
        b_ub=b_ub,
        bounds=[(0, None)] * len(term_maps),
        method="highs",
    )
    print("LP", res.status, res.message)
    if not res.success:
        return
    raw = res.x
    nonzero = [(i, x) for i, x in enumerate(raw) if x > 1e-9]
    print("raw_nonzero", len(nonzero), nonzero[:40])
    for max_den in (10, 25, 50, 100, 250, 1000, 5000, 20000):
        coeffs = [Fraction(str(x)).limit_denominator(max_den) for x in raw]
        ok, terms, mn, neg = exact_check(coeffs, mons)
        print("try", max_den, "ok", ok, "terms", terms, "min", mn, "neg", neg[:3])
        if ok:
            print("PASS EQ-bank degree", args.degree, "multiplier certificate")
            for j in range(7):
                chunk = coeffs[j * len(mons):(j + 1) * len(mons)]
                nz = [(str(mons[i]), c) for i, c in enumerate(chunk) if c]
                print("P", j + 1, nz)
            return


if __name__ == "__main__":
    main()
