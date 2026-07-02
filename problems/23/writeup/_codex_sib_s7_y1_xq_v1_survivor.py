"""Exact positivity for the x=q, v=1 endpoint survivor family.

The x=q endpoint scan found a clean positive endpoint family on the s6/s7
capacity faces with

    v=1, d=f=1, s2=s3=s6=s7=0.

Solving these equations in the positive domain gives

    e=c=t, b=2, x=t+1, u=t, a=t+1+1/t.

This is not one of the earlier x=q,u=1 survivor families, so we record it as
a separate exact endpoint survivor.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, x, t = sp.symbols("a b c d e f x t", positive=True)

    y = sp.Integer(1)
    v = sp.Integer(1)
    u = x - v
    m = x * (u + v) + v
    Y = a * c + b * f + c * f
    s2 = d + e - x
    s3 = b + c - x - 1
    s6 = a * c + d * f + e * f - m
    s7 = a * e + d * f + e * f - m

    G = sp.groebner(
        [d - 1, f - 1, v - 1, s2, s3, s6, s7],
        a,
        b,
        c,
        d,
        e,
        f,
        x,
        order="lex",
    )
    basis = {sp.factor(poly.as_expr()) for poly in G.polys}
    assert sp.factor(a * c - x**2 + x - 1) in basis
    assert sp.factor(a * x - a - x**2 + x - 1) in basis
    assert sp.factor(b + c - x - 1) in basis
    assert sp.factor((c - x + 1) * (x**2 - x + 1)) in basis
    assert sp.factor(d - 1) in basis
    assert sp.factor(e - x + 1) in basis
    assert sp.factor(f - 1) in basis
    # Since x>=2 on the x=q,v=1 feasible endpoint, x^2-x+1>0;
    # hence c=x-1, then e=c, b=2, and a=t+1+1/t with t=x-1.

    # Positive branch parameterization.
    c0 = e0 = t
    b0 = sp.Integer(2)
    d0 = f0 = sp.Integer(1)
    x0 = t + 1
    u0 = t
    a0 = t + 1 + 1 / t

    assert sp.factor(s2.subs({a: a0, b: b0, c: c0, d: d0, e: e0, f: f0, x: x0})) == 0
    assert sp.factor(s3.subs({a: a0, b: b0, c: c0, d: d0, e: e0, f: f0, x: x0})) == 0
    assert sp.factor(s6.subs({a: a0, b: b0, c: c0, d: d0, e: e0, f: f0, x: x0})) == 0
    assert sp.factor(s7.subs({a: a0, b: b0, c: c0, d: d0, e: e0, f: f0, x: x0})) == 0

    N = a0 + b0 + c0 + d0 + e0 + f0 + x0 + y + u0 + v
    Y0 = a0 * c0 + b0 * f0 + c0 * f0
    Z0 = e0 * Y0 + d0 * f0 * (b0 + c0)
    A0 = (
        b0 * d0
        + c0 * d0
        + d0 * f0
        + a0 * c0
        + a0 * e0
        + b0 * f0
        + b0 * e0
        + c0 * f0
        + c0 * e0
        + e0 * f0
    )
    B0 = a0 * c0 + a0 * e0 + b0 * f0 + b0 * e0 + c0 * f0 + c0 * e0 + e0 * f0
    m0 = x0 * (u0 + v) + v
    Phi = sp.factor(
        2 * (N**2 - 25 * m0)
        - 75 * (x0 * (u0 + v) * A0 / Z0 + y * v * B0 / (e0 * Y0) - (a0 + b0 + c0 + d0 + e0 + f0))
    )
    num, den = sp.together(Phi).as_numer_denom()
    num = sp.factor(num)
    den = sp.factor(den)
    assert den == t**2 * (t**2 + 2 * t + 3) * (t**3 + 2 * t**2 + 4 * t + 2)
    assert all(coef > 0 for coef in sp.Poly(num, t).all_coeffs())

    print("PASS y=1 x=q,v=1 endpoint survivor family is positive")


if __name__ == "__main__":
    main()
