"""Exact diagnostic for the EQ h=1 bank inequality.

Target from EQ_HEIGHT_LEMMA_GPTPRO.md:

    eta(w) = N(w)^2/25 - m(w) >= 0

on the seven-cut cone.  This first diagnostic checks the raw shifted numerator

    25*eta = N^2 - 25m

after w_i=1+x_i.  If raw coefficient positivity fails, the next step is a
multiplier/cone certificate with F1..F7.
"""

from __future__ import annotations

import sympy as sp


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


def coeff_stats(expr: sp.Expr):
    poly = sp.Poly(sp.expand(expr), *xs)
    coeffs = [sp.Integer(c) if c.is_Integer else c for c in poly.coeffs()]
    neg = [c for c in coeffs if c < 0]
    return len(coeffs), min(coeffs), neg[:10]


def main() -> None:
    terms, min_coeff, neg = coeff_stats(eta25)
    print(f"EQ_BANK_RAW terms={terms} min={min_coeff} negatives={len(neg)} sample={neg}")
    for i, f in enumerate(F, 1):
        t, mn, ng = coeff_stats(f)
        print(f"F{i} terms={t} min={mn} negatives={len(ng)} sample={ng}")


if __name__ == "__main__":
    main()
