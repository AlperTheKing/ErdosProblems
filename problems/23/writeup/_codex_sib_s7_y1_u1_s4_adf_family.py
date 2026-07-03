"""Exact positivity for the y=1,u=1,s4,a=d=f=1 family.

Set

    y=1, u=1, s4=0, a=d=f=1.

Then

    s4 = b + 2c - m,
    m = x(1+v)+v,

so write

    x = 1+X,  v = 1+V,
    M3 = m-3 = XV + 2X + 2V,
    c = 1 + R*M3/2,
    b = 1 + (1-R)*M3,      0 <= R <= 1.

The remaining feasibility constraints reduce to

    e >= v,
    e >= b+c-1.

The latter dominates everywhere because

    b+c-1-v = (2*M3 - R*M3 - 2V)/2 >= (M3-2V)/2 = X(V+2)/2 >= 0.

Thus the minimum is on

    e = b+c-1+E,     E>=0.

The cleared numerator is nonnegative in the Bernstein basis in `R`.
"""

from __future__ import annotations

from math import comb

import sympy as sp


def phi_expr(b: sp.Expr, c: sp.Expr, e: sp.Expr, x: sp.Expr, v: sp.Expr) -> sp.Expr:
    a = d = f = u = y = sp.Integer(1)
    m = x * u + x * v + y * v
    n = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return 2 * (n**2 - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f))


def bernstein_coeffs(poly: sp.Expr, var: sp.Symbol) -> list[sp.Expr]:
    p = sp.Poly(poly, var)
    degree = p.degree()
    power_coeffs = [p.coeff_monomial(var**i) for i in range(degree + 1)]
    out = []
    for k in range(degree + 1):
        coeff = 0
        for i in range(k + 1):
            coeff += power_coeffs[i] * sp.Rational(comb(k, i), comb(degree, i))
        out.append(sp.factor(coeff))
    return out


def coeff_stats(expr: sp.Expr, variables: tuple[sp.Symbol, ...]) -> tuple[int, sp.Integer, int]:
    numerator, denominator = sp.together(expr).as_numer_denom()
    den_poly = sp.Poly(denominator, *variables)
    den_coeffs = [sp.Integer(c) for c in den_poly.coeffs()]
    assert den_coeffs
    assert all(c > 0 for c in den_coeffs)
    poly = sp.Poly(numerator, *variables)
    coeffs = [sp.Integer(c) for c in poly.coeffs()]
    neg = sum(1 for c in coeffs if c < 0)
    return len(coeffs), min(coeffs), neg


def main() -> None:
    X, V, R, E = sp.symbols("X V R E", nonnegative=True)
    x = 1 + X
    v = 1 + V
    m = x * (1 + v) + v
    M3 = sp.factor(m - 3)
    assert M3 == V * X + 2 * V + 2 * X

    c = 1 + R * M3 / 2
    b = 1 + (1 - R) * M3
    e = b + c - 1 + E
    assert sp.simplify((b + c - 1) - v - (M3 * (2 - R) - 2 * V) / 2) == 0

    numerator, _ = sp.together(phi_expr(b, c, e, x, v)).as_numer_denom()
    bcoeffs = bernstein_coeffs(numerator, R)
    assert len(bcoeffs) == 5

    total_terms = 0
    min_coeff = None
    for coeff in bcoeffs:
        terms, this_min, neg = coeff_stats(coeff, (X, V, E))
        assert neg == 0, (terms, this_min, neg)
        assert this_min >= 0, (terms, this_min)
        total_terms += terms
        min_coeff = this_min if min_coeff is None else min(min_coeff, this_min)

    assert total_terms == 675
    assert min_coeff == 4
    print("PASS y=1,u=1,s4,a=d=f=1 family is Bernstein-positive")


if __name__ == "__main__":
    main()

