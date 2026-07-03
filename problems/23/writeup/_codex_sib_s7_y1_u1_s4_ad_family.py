"""Exact positivity for the y=1,u=1,s4,a=d=1 family.

Set

    y=1, u=1, s4=0, a=d=1.

Let

    x = 1+X,  v = 1+V,  m = x(1+v)+v,
    t = b+c-2,  q = c-1.

Then

    b = 1+t-q,  c = 1+q,
    f = (m-c)/(b+c).

The constraints are:

    f>=1       <=> t+q <= M3,
    b>=1,c>=1 <=> 0 <= q <= t,
    s3>=0     <=> t >= X,

where

    M3 = m-3 = XV+2X+2V.

Since `M3/2 >= X,V`, the feasible domain is covered by four chambers:

1. Universal high:      M3/2 <= t <= M3,           q <= M3-t.
2. X<=V low:           X <= t <= V,               q <= t, e=v+E.
3. X<=V middle:        V <= t <= M3/2,            q <= t, e=1+t+E.
4. X>=V middle:        X <= t <= M3/2,            q <= t, e=1+t+E.

The lower bound `e>=max(v,b+c-1)` is encoded by the chamber choice.
Every bounded variable is certified in the Bernstein basis.
"""

from __future__ import annotations

from math import comb

import sympy as sp


def phi_expr(
    X: sp.Expr,
    V: sp.Expr,
    t: sp.Expr,
    q: sp.Expr,
    e: sp.Expr,
) -> sp.Expr:
    a = d = u = y = sp.Integer(1)
    x = 1 + X
    v = 1 + V
    m = x * (1 + v) + v
    b = 1 + t - q
    c = 1 + q
    f = sp.cancel((m - c) / (b + c))
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
    *,
    expected_coeffs: int,
    expected_terms: int,
    expected_min: int,
    unbounded: tuple[sp.Symbol, ...],
) -> None:
    R, S = sp.symbols("R S", nonnegative=True)
    numerator, _ = sp.together(expr).as_numer_denom()
    coeffs = [numerator]
    for var in (R, S):
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
    R, S, E = sp.symbols("R S E", nonnegative=True)

    # Universal high chamber: M3/2 <= t <= M3, q <= M3-t.
    X, V = sp.symbols("X V", nonnegative=True)
    M3 = X * V + 2 * X + 2 * V
    t = M3 / 2 + R * M3 / 2
    q = S * (M3 - t)
    e = 1 + t + E
    assert_bernstein_positive(
        "high_all",
        phi_expr(X, V, t, q, e),
        expected_coeffs=30,
        expected_terms=12450,
        expected_min=8,
        unbounded=(X, V, E),
    )

    # X<=V low chamber: V=X+H, X <= t <= V, e=v+E.
    X, H = sp.symbols("X H", nonnegative=True)
    V = X + H
    M3 = X * V + 2 * X + 2 * V
    t = X + R * H
    q = S * t
    e = 1 + V + E
    assert_bernstein_positive(
        "x_le_v_low",
        phi_expr(X, V, t, q, e),
        expected_coeffs=32,
        expected_terms=9400,
        expected_min=2,
        unbounded=(X, H, E),
    )

    # X<=V middle chamber: V <= t <= M3/2, e=1+t+E.
    width = sp.factor(M3 / 2 - V)
    t = V + R * width
    q = S * t
    e = 1 + t + E
    assert_bernstein_positive(
        "x_le_v_mid",
        phi_expr(X, V, t, q, e),
        expected_coeffs=36,
        expected_terms=17375,
        expected_min=8,
        unbounded=(X, H, E),
    )

    # X>=V middle chamber: X=V+H, X <= t <= M3/2, e=1+t+E.
    V, H = sp.symbols("V H", nonnegative=True)
    X = V + H
    M3 = X * V + 2 * X + 2 * V
    width = sp.factor(M3 / 2 - X)
    t = X + R * width
    q = S * t
    e = 1 + t + E
    assert_bernstein_positive(
        "x_ge_v_mid",
        phi_expr(X, V, t, q, e),
        expected_coeffs=36,
        expected_terms=17375,
        expected_min=8,
        unbounded=(V, H, E),
    )

    print("PASS y=1,u=1,s4,a=d=1 family is Bernstein-positive")


if __name__ == "__main__":
    main()
