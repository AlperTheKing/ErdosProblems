"""Search for a small EQ h=1 bank cone certificate.

This uses scipy only as a search oracle.  Any found multiplier vector is
rationalized and checked exactly by coefficient positivity of

    eta25 - sum_j c_j F_j.
"""

from __future__ import annotations

from fractions import Fraction

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


def coeff_map(expr: sp.Expr) -> dict[tuple[int, ...], Fraction]:
    poly = sp.Poly(sp.expand(expr), *xs)
    out = {}
    for monom, coeff in poly.terms():
        out[monom] = Fraction(int(coeff.p), int(coeff.q))
    return out


def exact_check(coeffs: list[Fraction]) -> tuple[bool, int, Fraction, list[Fraction]]:
    expr = eta25 - sum(sp.Rational(c.numerator, c.denominator) * f for c, f in zip(coeffs, F))
    poly = sp.Poly(sp.expand(expr), *xs)
    vals = [Fraction(int(c.p), int(c.q)) for c in poly.coeffs()]
    neg = [v for v in vals if v < 0]
    return not neg, len(vals), min(vals), neg[:10]


def main() -> None:
    base = coeff_map(eta25)
    fmaps = [coeff_map(f) for f in F]
    monoms = sorted(set(base) | set().union(*(set(mp) for mp in fmaps)))

    # For each monomial: base_m - sum c_j f_j_m >= 0, c_j>=0.
    a_ub = []
    b_ub = []
    for monom in monoms:
        a_ub.append([float(fmaps[j].get(monom, Fraction(0))) for j in range(7)])
        b_ub.append(float(base.get(monom, Fraction(0))))
    res = linprog(
        c=[1.0] * 7,
        A_ub=a_ub,
        b_ub=b_ub,
        bounds=[(0, None)] * 7,
        method="highs",
    )
    print("LP", res.status, res.message)
    if not res.success:
        return
    raw = res.x
    print("raw", raw)
    for max_den in (10, 25, 50, 100, 250, 1000):
        coeffs = [Fraction(str(x)).limit_denominator(max_den) for x in raw]
        ok, terms, mn, neg = exact_check(coeffs)
        print("try", max_den, coeffs, ok, terms, mn, neg)
        if ok:
            print("PASS EQ-bank constant multiplier certificate", coeffs)
            return


if __name__ == "__main__":
    main()
