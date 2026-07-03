"""Exact positivity for the y=1,u=1,s4,a=c=d=1 family.

Set

    y=1, u=1, s4=0, a=c=d=1.

Write `x=1+X`, `b=x+s`, and `f=1+t`.  The equation `s4=0`
determines

    v = (1 + f(b+1) - x)/(x+1).

Feasibility requires `s>=0`, `v>=1`, and `e>=max(b,v)`.  The proof
splits first by `s>=X` or `X>=s`, then by `b>=v` or `v>=b`.

In the `b>=v` chambers, `t` ranges over a closed interval; we set
`t = L + R*(U-L)` with `0<=R<=1` and verify the cleared numerator in
the Bernstein basis in `R`.  In the `v>=b` chambers, set `t=U+G`.
All remaining variables are nonnegative.
"""

from __future__ import annotations

import sympy as sp


def phi_expr(b: sp.Expr, e: sp.Expr, f: sp.Expr, x: sp.Expr, v: sp.Expr) -> sp.Expr:
    a = c = d = u = y = sp.Integer(1)
    m = x * u + x * v + y * v
    n = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return 2 * (n**2 - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f))


def assert_coeff_nonnegative(expr: sp.Expr, variables: tuple[sp.Symbol, ...], *, expected_terms: int, min_coeff: int) -> None:
    poly = sp.Poly(sp.expand(expr), *variables)
    coeffs = [sp.Integer(coeff) for coeff in poly.coeffs()]
    assert len(coeffs) == expected_terms
    assert min(coeffs) == min_coeff
    assert all(coeff >= 0 for coeff in coeffs)


def assert_rational_coeff_nonnegative(
    expr: sp.Expr,
    variables: tuple[sp.Symbol, ...],
    *,
    expected_terms: int,
    min_coeff: int,
) -> None:
    numerator, denominator = sp.together(expr).as_numer_denom()
    assert_coeff_nonnegative(denominator, variables, expected_terms=sp.Poly(sp.expand(denominator), *variables).length(), min_coeff=1)
    assert_coeff_nonnegative(numerator, variables, expected_terms=expected_terms, min_coeff=min_coeff)


def power_to_bernstein(poly: sp.Expr, var: sp.Symbol) -> list[sp.Expr]:
    p = sp.Poly(sp.expand(poly), var)
    degree = p.degree()
    power_coeffs = [p.coeff_monomial(var**i) for i in range(degree + 1)]
    out = []
    for k in range(degree + 1):
        coeff = 0
        for i in range(k + 1):
            coeff += power_coeffs[i] * sp.binomial(k, i) / sp.binomial(degree, i)
        out.append(sp.factor(coeff))
    return out


def assert_bernstein_nonnegative(
    expr: sp.Expr,
    bernstein_var: sp.Symbol,
    unbounded_vars: tuple[sp.Symbol, ...],
    *,
    expected_bernstein: int,
    expected_total_terms: int,
    min_coeff: int,
) -> None:
    numerator, denominator = sp.together(expr).as_numer_denom()
    den_poly = sp.Poly(sp.expand(denominator), bernstein_var, *unbounded_vars)
    assert all(sp.Integer(coeff) > 0 for coeff in den_poly.coeffs())

    bcoeffs = power_to_bernstein(numerator, bernstein_var)
    assert len(bcoeffs) == expected_bernstein

    total_terms = 0
    mins: list[sp.Integer] = []
    for coeff in bcoeffs:
        poly = sp.Poly(sp.expand(coeff), *unbounded_vars)
        coeffs = [sp.Integer(c) for c in poly.coeffs()]
        total_terms += len(coeffs)
        mins.append(min(coeffs))
        assert all(c >= 0 for c in coeffs)

    assert total_terms == expected_total_terms
    assert min(mins) == min_coeff


def main() -> None:
    # Chamber A: s>=X.  Put s=X+H.
    X, H, R, E, G = sp.symbols("X H R E G", nonnegative=True)
    x = 1 + X
    s = X + H
    b = x + s
    upper = sp.factor((X**2 + 3 * X + s * (1 + X)) / (X + s + 2))

    # A1: b>=v.  Here lower=0 and t=R*upper, 0<=R<=1.
    t = R * upper
    f = 1 + t
    v = sp.factor((1 + f * (b + 1) - x) / (x + 1))
    assert sp.factor(v - 1) == sp.factor((H * R * X + H * R + H + 2 * R * X**2 + 4 * R * X) / (X + 2))
    assert sp.factor(b - v) == sp.factor((1 - R) * (H * X + H + 2 * X**2 + 4 * X) / (X + 2))
    assert_bernstein_nonnegative(phi_expr(b, b + E, f, x, v), R, (X, H, E), expected_bernstein=5, expected_total_terms=1915, min_coeff=0)

    # A2: v>=b.  Put t=upper+G and e=v+E.
    t = upper + G
    f = 1 + t
    v = sp.factor((1 + f * (b + 1) - x) / (x + 1))
    assert sp.factor(v - b) == sp.factor(G * (H + 2 * X + 2) / (X + 2))
    assert_rational_coeff_nonnegative(phi_expr(b, v + E, f, x, v), (X, H, G, E), expected_terms=2115, min_coeff=2)

    # Chamber B: X>=s.  Put X=S+H2, s=S.
    S, H2, R2, E2, G2 = sp.symbols("S H2 R2 E2 G2", nonnegative=True)
    X2 = S + H2
    x = 1 + X2
    s = S
    b = x + s
    upper = sp.factor((X2**2 + 3 * X2 + s * (1 + X2)) / (X2 + s + 2))
    lower = sp.factor(H2 / (X2 + s + 2))

    # B1: b>=v.  Here t=lower+R2*(upper-lower).
    t = sp.factor(lower + R2 * (upper - lower))
    f = 1 + t
    v = sp.factor((1 + f * (b + 1) - x) / (x + 1))
    assert sp.factor(v - 1) == R2 * (H2 + 2 * S)
    assert sp.factor((b - v) - (1 - R2) * (H2 + 2 * S)) == 0
    assert_bernstein_nonnegative(phi_expr(b, b + E2, f, x, v), R2, (S, H2, E2), expected_bernstein=5, expected_total_terms=1514, min_coeff=0)

    # B2: v>=b.  Put t=upper+G2 and e=v+E2.
    t = upper + G2
    f = 1 + t
    v = sp.factor((1 + f * (b + 1) - x) / (x + 1))
    assert sp.factor(v - b) == sp.factor(G2 * (H2 + 2 * S + 2) / (H2 + S + 2))
    assert_rational_coeff_nonnegative(phi_expr(b, v + E2, f, x, v), (S, H2, G2, E2), expected_terms=2379, min_coeff=2)

    print("PASS y=1,u=1,s4,a=c=d=1 family is covered by four exact chambers")


if __name__ == "__main__":
    main()
