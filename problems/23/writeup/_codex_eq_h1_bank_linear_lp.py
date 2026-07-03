"""Search for a linear EQ h=1 bank cone certificate.

Multiplier ansatz:

    P_j = c_{j,0} + sum_i c_{j,i+1} x_i,  all c>=0.

Search uses scipy; exact acceptance checks rationalized coefficients by SymPy.
"""

from __future__ import annotations

from fractions import Fraction

import sympy as sp
from scipy.optimize import linprog


xs = sp.symbols("x0:10", nonnegative=True)
ws = [1 + x for x in xs]
w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = ws
mons = [sp.Integer(1), *xs]

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


def exact_expr(coeffs: list[Fraction]) -> sp.Expr:
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


def exact_check(coeffs: list[Fraction]) -> tuple[bool, int, Fraction, list[Fraction]]:
    poly = sp.Poly(exact_expr(coeffs), *xs)
    vals = [Fraction(int(c.p), int(c.q)) for c in poly.coeffs()]
    neg = [v for v in vals if v < 0]
    return not neg, len(vals), min(vals), neg[:10]


def main() -> None:
    base = coeff_map(eta25)
    term_maps = []
    for f in F:
        for mon in mons:
            term_maps.append(coeff_map(f * mon))
    monoms = sorted(set(base) | set().union(*(set(mp) for mp in term_maps)))

    a_ub = []
    b_ub = []
    for monom in monoms:
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
    print("raw_nonzero", len(nonzero), nonzero[:30])
    for max_den in (10, 25, 50, 100, 250, 1000, 5000):
        coeffs = [Fraction(str(x)).limit_denominator(max_den) for x in raw]
        ok, terms, mn, neg = exact_check(coeffs)
        print("try", max_den, "ok", ok, "terms", terms, "min", mn, "neg", neg[:3])
        if ok:
            print("PASS EQ-bank linear multiplier certificate")
            for j in range(7):
                chunk = coeffs[j * len(mons):(j + 1) * len(mons)]
                print("P", j + 1, chunk)
            return


if __name__ == "__main__":
    main()
