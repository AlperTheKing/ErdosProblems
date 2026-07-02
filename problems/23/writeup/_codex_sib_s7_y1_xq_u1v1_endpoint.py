"""Exact positivity for the x=q, u=v=1 endpoint curve.

The x=q endpoint scan found a positive one-dimensional endpoint family on the
s6/s7 capacity faces with

    u=1, v=1, d=f=1, s3=s6=s7=0.

Solving those equations in the positive domain gives

    x=2, c=e=t, b=3-t, a=4/t-1, 1 <= t <= 2.

This curve is not the all-tight low family except at t=1.  It is uniformly
positive, so it can be removed from the x=q,v=1 endpoint inventory.
"""

from __future__ import annotations

import sympy as sp


def bernstein_coeffs(poly: sp.Expr, var: sp.Symbol) -> list[sp.Expr]:
    P = sp.Poly(sp.expand(poly), var)
    n = P.degree()
    coeff = [P.coeff_monomial(var**i) for i in range(n + 1)]
    return [
        sp.factor(sum(coeff[i] * sp.Rational(sp.binomial(k, i), sp.binomial(n, i)) for i in range(k + 1)))
        for k in range(n + 1)
    ]


def main() -> None:
    a, b, c, d, e, f, t, r = sp.symbols("a b c d e f t r", positive=True)
    x = sp.Integer(2)
    y = sp.Integer(1)
    u = sp.Integer(1)
    v = sp.Integer(1)
    m = x * (u + v) + v
    Y = a * c + b * f + c * f
    s3 = b + c - x - y
    s6 = a * c + d * f + e * f - m
    s7 = a * e + d * f + e * f - m

    G = sp.groebner(
        [d - 1, f - 1, s3, s6, s7],
        a,
        b,
        c,
        d,
        e,
        f,
        order="lex",
    )
    basis = {sp.factor(poly.as_expr()) for poly in G.polys}
    assert sp.factor(a * c - 4 + e) in basis
    assert sp.factor(a * e - 4 + e) in basis
    assert sp.factor(b + c - 3) in basis
    assert sp.factor((c - e) * (e - 4)) in basis
    assert sp.factor(d - 1) in basis
    assert sp.factor(f - 1) in basis
    # The alternative branch e=4 forces a=0 from a*e+e-4=0, so it is
    # outside the positive domain. Hence only c=e remains.

    t0 = 1 + r
    subs = {
        c: t0,
        e: t0,
        b: 3 - t0,
        a: 4 / t0 - 1,
        d: 1,
        f: 1,
    }
    for expr in (s3, s6, s7):
        assert sp.factor(expr.subs(subs)) == 0
    assert sp.factor(Y.subs(subs) - (6 - r)) == 0

    N = a + b + c + d + e + f + x + y + u + v
    Z = e * Y + d * f * (b + c)
    A = (
        b * d
        + c * d
        + d * f
        + a * c
        + a * e
        + b * f
        + b * e
        + c * f
        + c * e
        + e * f
    )
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = sp.factor(
        2 * (N**2 - 25 * m)
        - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f))
    )
    Phi_r = sp.factor(Phi.subs(subs))
    num, den = sp.together(Phi_r).as_numer_denom()
    assert sp.factor(den - (r - 6) * (r + 1) ** 2 * (r ** 2 - 5 * r - 9)) == 0

    # Feasibility on the curve is exactly 0 <= r <= 1.  Bernstein
    # positivity on that interval proves Phi > 0.
    coeffs = bernstein_coeffs(num, r)
    assert all(coef > 0 for coef in coeffs)

    print("PASS y=1 x=q,u=v=1 endpoint family is positive")


if __name__ == "__main__":
    main()
