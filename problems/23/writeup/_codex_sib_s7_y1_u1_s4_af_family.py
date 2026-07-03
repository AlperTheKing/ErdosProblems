"""Exact positivity for the y=1,u=1,s4,a=f=1 family.

Set

    y=1, u=1, s4=0, a=f=1.

Then

    m = x(1+v)+v,
    b + 2c = m.

Write

    x = 1+X, v = 1+V, q = c-1,
    M3 = m-3 = XV+2X+2V,
    c = 1+q, b = 1+M3-2q, 0 <= q <= M3/2.

The feasibility constraints reduce to

    e >= v,
    e >= c,
    d >= 1,
    d+e >= b+c.

The final inequality is certified by four exact chambers:

1. q <= V, e between v and b+c-1, d=b+c-e+D.
2. q <= V, e >= b+c-1, d=1+D.
3. q >= V, e between c and b+c-1, d=b+c-e+D.
4. q >= V, e >= b+c-1, d=1+D.

Every bounded variable is checked in the Bernstein basis, with unbounded
variables having coefficientwise-positive numerator and denominator.
"""

from __future__ import annotations

from math import comb

import sympy as sp


def phi_expr(b: sp.Expr, c: sp.Expr, d: sp.Expr, e: sp.Expr, x: sp.Expr, v: sp.Expr) -> sp.Expr:
    a = f = u = y = sp.Integer(1)
    m = x * (1 + v) + v
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


def assert_bernstein_positive(
    name: str,
    expr: sp.Expr,
    bounded: tuple[sp.Symbol, ...],
    unbounded: tuple[sp.Symbol, ...],
    *,
    expected_coeffs: int,
    expected_terms: int,
    expected_min: int,
) -> None:
    numerator, _ = sp.together(expr).as_numer_denom()
    coeffs = [numerator]
    for var in bounded:
        next_coeffs: list[sp.Expr] = []
        for coeff in coeffs:
            next_coeffs.extend(bernstein_coeffs(coeff, var))
        coeffs = next_coeffs

    total_terms = 0
    min_coeff = None
    for coeff in coeffs:
        terms, this_min, neg = coeff_stats(coeff, unbounded)
        assert neg == 0, (name, terms, this_min, neg)
        assert this_min >= 0, (name, terms, this_min)
        total_terms += terms
        min_coeff = this_min if min_coeff is None else min(min_coeff, this_min)

    assert len(coeffs) == expected_coeffs, (name, len(coeffs), expected_coeffs)
    assert total_terms == expected_terms, (name, total_terms, expected_terms)
    assert min_coeff == expected_min, (name, min_coeff, expected_min)


def main() -> None:
    X, V, R, S, D, E = sp.symbols("X V R S D E", nonnegative=True)
    x = 1 + X
    v = 1 + V
    m = x * (1 + v) + v
    M3 = sp.factor(m - 3)
    assert M3 == X * V + 2 * X + 2 * V

    # q <= V.
    q = R * V
    b = 1 + M3 - 2 * q
    c = 1 + q
    high_e = 1 + M3 - q  # b+c-1

    e = v + S * (high_e - v)
    d = b + c - e + D
    assert_bernstein_positive(
        "q_le_v_segment",
        phi_expr(b, c, d, e, x, v),
        (R, S),
        (X, V, D),
        expected_coeffs=18,
        expected_terms=2136,
        expected_min=2,
    )

    e = high_e + E
    d = 1 + D
    assert_bernstein_positive(
        "q_le_v_ray",
        phi_expr(b, c, d, e, x, v),
        (R,),
        (X, V, D, E),
        expected_coeffs=5,
        expected_terms=1480,
        expected_min=2,
    )

    # q >= V.
    width = sp.factor(M3 / 2 - V)
    q = V + R * width
    b = 1 + M3 - 2 * q
    c = 1 + q
    high_e = 1 + M3 - q

    e = c + S * (high_e - c)
    d = b + c - e + D
    assert_bernstein_positive(
        "q_ge_v_segment",
        phi_expr(b, c, d, e, x, v),
        (R, S),
        (X, V, D),
        expected_coeffs=15,
        expected_terms=1868,
        expected_min=4,
    )

    e = high_e + E
    d = 1 + D
    assert_bernstein_positive(
        "q_ge_v_ray",
        phi_expr(b, c, d, e, x, v),
        (R,),
        (X, V, D, E),
        expected_coeffs=5,
        expected_terms=1480,
        expected_min=4,
    )

    print("PASS y=1,u=1,s4,a=f=1 family is Bernstein-positive")


if __name__ == "__main__":
    main()
