"""Exact positivity for the first broad y=1,u=1,s4,a=1 chamber.

This is only the low chamber of the broader family

    y=1, u=1, s4=0, a=1.

Use

    x = 1+X,  v = 1+V,  V = X+H,
    t = b+c-2 = X + R H,       0 <= R <= 1,
    q = c-1 = S t,             0 <= S <= 1.

Thus X <= t <= V and q <= t.  Since M3/2 >= V, the inequality
q+t <= M3 is automatic, so f>=1.  This is the chamber where
max(v,c)=v and max(v,t)=v for the d/e lower bounds, hence

    e = 1+V+E,  d = 1+D.

The selected capacity equation s4=0 determines

    f = (x(1+v)+v-c)/(b+c).

After clearing the structurally positive denominators, Phi is
nonnegative in the Bernstein basis in R,S and the ordinary monomial basis
in X,H,D,E.
"""

from __future__ import annotations

from math import comb

import sympy as sp


def bernstein_coeffs(poly: sp.Expr, var: sp.Symbol) -> list[sp.Expr]:
    p = sp.Poly(poly, var)
    degree = p.degree()
    power_coeffs = [p.coeff_monomial(var**i) for i in range(degree + 1)]
    out = []
    for k in range(degree + 1):
        out.append(sp.factor(sum(
            power_coeffs[i] * sp.Rational(comb(k, i), comb(degree, i))
            for i in range(k + 1)
        )))
    return out


def phi_expr() -> sp.Expr:
    X, H, R, S, D, E = sp.symbols("X H R S D E", nonnegative=True)
    V = X + H
    t = X + R * H
    q = S * t

    a = u = y = sp.Integer(1)
    x = 1 + X
    v = 1 + V
    b = 1 + t - q
    c = 1 + q
    d = 1 + D
    e = 1 + V + E
    f = sp.cancel((x * (1 + v) + v - c) / (b + c))

    m = x * (1 + v) + v
    n = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f

    M3 = X * V + 2 * X + 2 * V
    assert sp.factor(m - (3 + M3)) == 0
    assert sp.factor(t - X - R * H) == 0
    assert sp.factor(V - t - H * (1 - R)) == 0
    assert sp.factor(t - q - t * (1 - S)) == 0
    assert sp.factor(M3 - 2 * V - X * (V + 2)) == 0

    return 2 * (n**2 - 25 * m) - 75 * (
        x * (u + v) * A / Z + y * v * B / (e * Y)
        - (a + b + c + d + e + f)
    )


def assert_bernstein_positive(name: str, expr: sp.Expr, *, expected_coeffs: int, expected_terms: int, expected_min: sp.Expr) -> None:
    X, H, R, S, D, E = sp.symbols("X H R S D E", nonnegative=True)
    numerator, denominator = sp.together(expr).as_numer_denom()
    assert denominator != 0

    coeffs = [numerator]
    for var in (R, S):
        next_coeffs: list[sp.Expr] = []
        for coeff in coeffs:
            next_coeffs.extend(bernstein_coeffs(coeff, var))
        coeffs = next_coeffs

    total_terms = 0
    min_coeff = None
    for coeff in coeffs:
        poly = sp.Poly(sp.factor(coeff), X, H, D, E)
        raw_coeffs = [sp.Integer(c) if c.is_Integer else c for c in poly.coeffs()]
        assert all(c >= 0 for c in raw_coeffs), name
        total_terms += len(raw_coeffs)
        this_min = min(raw_coeffs)
        min_coeff = this_min if min_coeff is None else min(min_coeff, this_min)

    assert len(coeffs) == expected_coeffs, (name, len(coeffs), expected_coeffs)
    assert total_terms == expected_terms, (name, total_terms, expected_terms)
    assert min_coeff == expected_min, (name, min_coeff, expected_min)


def main() -> None:
    X, H, R, S, D, E = sp.symbols("X H R S D E", nonnegative=True)
    print("START y=1,u=1,s4,a=1 low chamber", flush=True)
    phi = phi_expr()
    print("CHECK a_s4_low_phi", flush=True)
    assert_bernstein_positive(
        "a_s4_low_phi",
        phi,
        expected_coeffs=32,
        expected_terms=23416,
        expected_min=sp.Rational(2, 35),
    )

    assert_bernstein_positive(
        "a_s4_low_dD",
        sp.diff(phi, D),
        expected_coeffs=28,
        expected_terms=11020,
        expected_min=sp.Rational(1, 5),
    )
    assert_bernstein_positive(
        "a_s4_low_dE",
        sp.diff(phi, E),
        expected_coeffs=32,
        expected_terms=45136,
        expected_min=sp.Rational(4, 35),
    )

    print("PASS y=1,u=1,s4,a=1 low chamber is Bernstein-positive")


if __name__ == "__main__":
    main()
