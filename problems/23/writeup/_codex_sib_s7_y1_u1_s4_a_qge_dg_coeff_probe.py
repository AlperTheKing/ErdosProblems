"""Coefficient split for the q>=V chamber d-slack derivative.

The full derivative expansion in the unbounded slack G is large. This probe
uses the fact that the cleared numerator is cubic in d, derives the derivative
numerator coefficients by hand, then checks the four G-coefficients separately.
"""

from __future__ import annotations

from math import comb

import sympy as sp


X, H, J, R, S, U = sp.symbols("X H J R S U", nonnegative=True)
J_TRUE = X * (X + H + 2)


def bernstein_coeffs(poly: sp.Expr, var: sp.Symbol) -> list[sp.Expr]:
    p = sp.Poly(poly, var)
    degree = p.degree()
    power_coeffs = [p.coeff_monomial(var**i) for i in range(degree + 1)]
    return [
        sum(
            power_coeffs[i] * sp.Rational(comb(k, i), comb(degree, i))
            for i in range(k + 1)
        )
        for k in range(degree + 1)
    ]


def common_quantities():
    V = X + H
    x = 1 + X
    v = 1 + V
    m = 3 + 2 * V + J
    q = V + S * J / 2
    t = q + R * (1 - S) * J
    W = t - q
    h = 2 + t
    c = 1 + q
    C = m - c
    return V, x, v, m, q, t, W, h, c, C


def derivative_coeffs_in_d(e: sp.Expr) -> tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr]:
    V, x, v, m, q, t, W, h, c, C = common_quantities()
    em = e * m
    p_term = m - v

    sc0 = h * (3 + t + e) + C
    n0 = sc0 + h * (x + 2 + v)
    base2 = 2 * h * h
    base1 = 4 * h * n0 + 75 * h * h
    base0 = 2 * n0 * n0 - 50 * m * h * h + 75 * h * sc0

    anum1 = h * h + C
    anum0 = h * (m + e) + e * (h * h + C)
    b_num = h * m + e * (h * (1 + h) + C)

    # N(d) = a3*d^3 + a2*d^2 + a1*d + a0 is the cleared numerator.
    a3 = base2 * C * em
    a2 = (base2 * em + base1 * C) * em
    a1 = (base1 * em + base0 * C) * em - 75 * p_term * anum1 * h * em - 75 * v * b_num * h * C
    a0 = base0 * em * em - 75 * p_term * anum0 * h * em - 75 * v * b_num * h * em

    # For Phi=N/z, z=em+C*d, the d-derivative numerator is N'(d)*z - N(d)*C.
    m0 = em * a1 - C * a0
    m1 = 2 * em * a2
    m2 = 3 * em * a3 + C * a2
    m3 = 2 * C * a3
    return m0, m1, m2, m3


def derivative_coeffs_in_g(d0: sp.Expr, e: sp.Expr) -> tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr]:
    m0, m1, m2, m3 = derivative_coeffs_in_d(e)
    g0 = m0 + m1 * d0 + m2 * d0 * d0 + m3 * d0 * d0 * d0
    g1 = m1 + 2 * m2 * d0 + 3 * m3 * d0 * d0
    g2 = m2 + 3 * m3 * d0
    g3 = m3
    return g0, g1, g2, g3


def check_positive(name: str, expr: sp.Expr) -> tuple[int, int, sp.Expr]:
    coeffs = [expr]
    for var in (R, S, U):
        next_coeffs: list[sp.Expr] = []
        for coeff in coeffs:
            next_coeffs.extend(bernstein_coeffs(coeff, var))
        coeffs = next_coeffs

    total_terms = 0
    min_coeff = None
    for coeff in coeffs:
        true_coeff = coeff.subs(J, J_TRUE)
        poly = sp.Poly(true_coeff, X, H)
        raw_coeffs = [sp.Integer(c) if c.is_Integer else c for c in poly.coeffs()]
        negatives = [c for c in raw_coeffs if c < 0]
        assert not negatives, (name, negatives[:5])
        total_terms += len(raw_coeffs)
        this_min = min(raw_coeffs)
        min_coeff = this_min if min_coeff is None else min(min_coeff, this_min)
    assert min_coeff is not None
    return len(coeffs), total_terms, min_coeff


def main() -> None:
    V, x, v, m, q, t, W, h, c, C = common_quantities()
    e = 1 + q + U * W
    d0 = 1 + W - U * W
    print("PROBE q>=V dG coefficient split start", flush=True)
    coeffs_g = derivative_coeffs_in_g(d0, e)
    print("PROBE manual G coefficients ready", flush=True)
    print(f"PROBE G_degree={len(coeffs_g) - 1}", flush=True)
    for k, coeff in enumerate(coeffs_g):
        stats = check_positive(f"dG_G{k}", coeff)
        print(f"dG_G{k}: coeffs={stats[0]} terms={stats[1]} min={stats[2]}", flush=True)
    print("PASS q>=V dG coefficient split", flush=True)


if __name__ == "__main__":
    main()