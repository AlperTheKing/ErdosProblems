"""Exact s3-descent on the y=1, x=q, s2=0, s6=0 half-face.

This closes one of the two open x=q,s2 capacity half-faces up to the already
tracked s3 boundary.

On y=1, x=q and s2=0, write x=q=d+e.  On the s6=0 capacity face,

    m = ac + df + ef,
    v = ac + f(d+e) - (d+e)^2,
    u = d+e-v.

The pair-structure gate gives

    s4 = f(s3+1),
    s5 = a(e-c) + f(s3+1),
    s7 = a(e-c).

Thus the open s6 half-face has e>=c and s3>=0.  Put

    a=1+A, c=1+C, d=1+D, f=1+F,
    e=c+R, b=d+R+1+H.

Then R=e-c and H=s3 are nonnegative.  This file verifies that the cleared
numerator of dPhi/dH is

    P + sum lambda_i * mon_i * (u-1) + sum mu_i * mon_i * (v-1),

where P has only nonnegative coefficients and all lambda_i,mu_i are
nonnegative rationals.  Since the denominator is positive, Phi is
nondecreasing in H=s3 on this half-face.  Hence any minimum on the s6 half-face
reduces to the boundary s3=0.
"""

from __future__ import annotations

import sympy as sp


def monomial(vars_: tuple[sp.Symbol, ...], exps: tuple[int, ...]) -> sp.Expr:
    out = sp.Integer(1)
    for var, exp in zip(vars_, exps):
        out *= var ** exp
    return out


def assert_coeff_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...], label: str) -> None:
    poly = sp.Poly(sp.expand(expr), *vars_)
    bad = [(mon, coef) for mon, coef in poly.terms() if coef < 0]
    assert not bad, (label, bad[:5])


def main() -> None:
    A, C, D, F, R, H = sp.symbols("A C D F R H", nonnegative=True)
    vars_ = (A, C, D, F, R, H)

    a = 1 + A
    c = 1 + C
    d = 1 + D
    f = 1 + F
    e = c + R
    b = d + R + 1 + H
    y = sp.Integer(1)
    x = q = d + e

    v = a * c + f * x - x**2
    u = x - v
    S = a + b + c + d + e + f
    m = x * q + v
    N = S + x + y + q
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    AA = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    BB = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = 2 * (N * N - 25 * m) - 75 * (x * q * AA / Z + y * v * BB / (e * Y) - S)

    # Structural identities on the face.
    assert sp.factor(m - (a * c + d * f + e * f)) == 0
    s2 = d + e - u - v
    s3 = b + c - x - y
    s4 = Y - m
    s5 = a * e + b * f + c * f - m
    s7 = a * e + d * f + e * f - m
    assert sp.factor(s2) == 0
    assert sp.factor(s3 - H) == 0
    assert sp.factor(s4 - f * (H + 1)) == 0
    assert sp.factor(s5 - (a * R + f * (H + 1))) == 0
    assert sp.factor(s7 - a * R) == 0

    dphi = sp.diff(Phi, H)
    num, den = sp.together(dphi).as_numer_denom()
    assert sp.factor(den - e * Y**2 * Z**2) == 0

    u1 = sp.expand(u - 1)
    v1 = sp.expand(v - 1)
    constraints = {"u1": u1, "v1": v1}
    cert: list[tuple[str, tuple[int, ...], sp.Rational]] = [
        ("u1", (2, 3, 3, 0, 0, 0), sp.Rational(16)),
        ("u1", (2, 2, 3, 0, 1, 0), sp.Rational(16)),
        ("v1", (3, 4, 2, 0, 0, 0), sp.Rational(8)),
        ("v1", (3, 5, 1, 0, 0, 0), sp.Rational(27)),
        ("v1", (3, 3, 2, 0, 1, 0), sp.Rational(16)),
        ("v1", (3, 4, 1, 0, 1, 0), sp.Rational(38)),
        ("v1", (3, 2, 2, 0, 2, 0), sp.Rational(22, 3)),
        ("v1", (3, 4, 0, 0, 2, 0), sp.Rational(816)),
        ("v1", (3, 3, 0, 0, 3, 0), sp.Rational(432)),
        ("v1", (1, 0, 4, 3, 1, 0), sp.Rational(31, 3)),
        ("v1", (1, 0, 5, 3, 0, 0), sp.Rational(4)),
        ("v1", (1, 0, 5, 3, 1, 0), sp.Rational(4)),
        ("v1", (1, 0, 4, 3, 0, 0), sp.Rational(25)),
        ("v1", (1, 0, 5, 2, 0, 0), sp.Rational(10)),
        ("v1", (1, 0, 5, 2, 1, 0), sp.Rational(10, 3)),
        ("v1", (1, 0, 4, 3, 2, 0), sp.Rational(65, 9)),
    ]

    residual = sp.expand(num)
    for name, exps, coeff in cert:
        residual -= coeff * monomial(vars_, exps) * constraints[name]

    assert_coeff_nonnegative(residual, vars_, "s6 dPhi/ds3 residual")
    print("PASS y=1 x=q,s2,s6 half-face has exact s3-descent to boundary")


if __name__ == "__main__":
    main()
