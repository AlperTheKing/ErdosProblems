"""Exact s3-descent on the b=1 boundary of the y=1,x=q,s2,s7 face.

The previous gate proves that on the y=1, x=q, s2=0, s7=0 half-face,
Phi is nondecreasing in b, so a minimum descends to either s3=0 or b=1.
This file closes the remaining b=1 boundary.

On b=1 and s7=0, write

    a=1+A, e=1+E, d=1+D, f=1+F,
    c=e+d+H.

Then H=s3.  The face equations give

    x=q=d+e,
    v=ae+f(d+e)-(d+e)^2,
    u=d+e-v.

The cleared numerator of dPhi/dH has coefficientwise nonnegative expansion in
A,E,D,F,H.  Since the denominator is positive, Phi is nondecreasing in s3 on
this boundary, and every minimum reduces to s3=0.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    A, E, D, F, H = sp.symbols("A E D F H", nonnegative=True)
    vars_ = (A, E, D, F, H)

    a = 1 + A
    e = 1 + E
    d = 1 + D
    f = 1 + F
    b = sp.Integer(1)
    c = e + d + H
    y = sp.Integer(1)
    x = q = d + e

    v = a * e + f * x - x**2
    u = x - v
    S = a + b + c + d + e + f
    m = x * q + v
    N = S + x + y + q
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    AA = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    BB = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = 2 * (N * N - 25 * m) - 75 * (x * q * AA / Z + y * v * BB / (e * Y) - S)

    s2 = d + e - u - v
    s3 = b + c - x - y
    s7 = a * e + d * f + e * f - m
    assert sp.factor(s2) == 0
    assert sp.factor(s3 - H) == 0
    assert sp.factor(s7) == 0

    dphi = sp.diff(Phi, H)
    num, den = sp.together(dphi).as_numer_denom()
    assert sp.factor(den - e * Y**2 * Z**2) == 0

    poly = sp.Poly(sp.expand(num), *vars_)
    bad = [(mon, coef) for mon, coef in poly.terms() if coef < 0]
    assert not bad, bad[:5]
    assert any(coef > 0 for _mon, coef in poly.terms())

    print("PASS y=1 x=q,s2,s7,b=1 boundary has exact s3-descent")


if __name__ == "__main__":
    main()
