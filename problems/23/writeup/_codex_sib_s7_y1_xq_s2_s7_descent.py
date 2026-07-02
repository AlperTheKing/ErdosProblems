"""Exact b-descent on the y=1, x=q, s2=0, s7=0 half-face.

This is the mirror-half companion to the s6 descent gate.  On y=1, x=q and
s2=0, the s7=0 capacity face has

    m = ae + df + ef,
    x=q=d+e,
    v = ae + f(d+e) - (d+e)^2,
    u = d+e-v.

The pair-structure identities give

    s5 = f(s3+1),
    s4 = a(c-e) + f(s3+1),
    s6 = a(c-e).

Thus feasibility forces c>=e.  Put

    a=1+A, e=1+E, d=1+D, f=1+F,
    c=e+R, b=1+B.

Then R=c-e and B=b-1 are nonnegative, while s3 is a separate nonnegative
constraint.  This file verifies that the cleared numerator of dPhi/dB is

    P + sum lambda_i mon_i * g_i,

where P has coefficientwise nonnegative expansion and each g_i is one of
u-1, v-1, s1, s3.  Therefore Phi is nondecreasing in B=b-1 on this half-face.
Consequently a minimum on the s7 half-face reduces to either the already
tracked s3=0 boundary or the b=1 boundary.
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
    A, E, D, F, R, B0 = sp.symbols("A E D F R B", nonnegative=True)
    vars_ = (A, E, D, F, R, B0)

    a = 1 + A
    e = 1 + E
    d = 1 + D
    f = 1 + F
    c = e + R
    b = 1 + B0
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

    assert sp.factor(m - (a * e + d * f + e * f)) == 0
    s2 = d + e - u - v
    s3 = b + c - x - y
    s4 = Y - m
    s5 = a * e + b * f + c * f - m
    s6 = a * c + d * f + e * f - m
    assert sp.factor(s2) == 0
    assert sp.factor(s5 - f * (s3 + 1)) == 0
    assert sp.factor(s4 - (a * R + f * (s3 + 1))) == 0
    assert sp.factor(s6 - a * R) == 0

    dphi = sp.diff(Phi, B0)
    num, den = sp.together(dphi).as_numer_denom()
    assert sp.factor(den - e * Y**2 * Z**2) == 0

    constraints = {
        "u1": sp.expand(u - 1),
        "s1": sp.expand(e - v),
        "v1": sp.expand(v - 1),
        "s3": sp.expand(s3),
    }
    cert: list[tuple[str, tuple[int, ...], sp.Rational]] = [
        ("u1", (2, 2, 2, 0, 1, 0), sp.Rational(495, 4)),
        ("u1", (2, 1, 2, 0, 2, 0), sp.Rational(942, 11)),
        ("u1", (1, 4, 2, 0, 0, 0), sp.Rational(24)),
        ("u1", (1, 3, 2, 0, 1, 0), sp.Rational(96)),
        ("s1", (2, 3, 2, 0, 0, 0), sp.Rational(75)),
        ("v1", (3, 5, 1, 0, 0, 0), sp.Rational(397, 6)),
        ("v1", (3, 4, 1, 0, 1, 0), sp.Rational(2753, 12)),
        ("v1", (3, 4, 1, 0, 0, 0), sp.Rational(4289, 20)),
        ("v1", (3, 5, 0, 0, 0, 0), sp.Rational(1201, 10)),
        ("v1", (3, 3, 1, 0, 2, 0), sp.Rational(2703, 11)),
        ("v1", (3, 3, 1, 0, 1, 0), sp.Rational(2987, 5)),
        ("v1", (3, 3, 1, 0, 0, 0), sp.Rational(2851, 20)),
        ("v1", (3, 2, 1, 0, 3, 0), sp.Rational(51)),
        ("v1", (3, 2, 1, 0, 2, 0), sp.Rational(7629, 22)),
        ("v1", (3, 1, 1, 0, 3, 0), sp.Rational(23)),
        ("v1", (2, 4, 2, 0, 0, 0), sp.Rational(97)),
        ("v1", (2, 5, 2, 0, 0, 0), sp.Rational(19, 3)),
        ("v1", (2, 3, 2, 0, 1, 0), sp.Rational(339, 2)),
        ("v1", (2, 4, 2, 0, 1, 0), sp.Rational(96)),
        ("v1", (2, 2, 2, 0, 2, 0), sp.Rational(921, 11)),
        ("v1", (2, 3, 2, 0, 2, 0), sp.Rational(144)),
        ("v1", (2, 4, 1, 0, 2, 0), sp.Rational(25, 33)),
        ("v1", (2, 1, 3, 0, 2, 0), sp.Rational(39, 11)),
        ("v1", (2, 2, 2, 0, 3, 0), sp.Rational(1, 3)),
        ("v1", (1, 1, 2, 3, 0, 2), sp.Rational(27)),
        ("v1", (1, 1, 2, 3, 0, 1), sp.Rational(450)),
        ("v1", (1, 0, 3, 2, 0, 2), sp.Rational(12)),
        ("v1", (1, 0, 2, 3, 0, 2), sp.Rational(63)),
        ("v1", (1, 0, 2, 3, 0, 1), sp.Rational(300)),
        ("v1", (1, 0, 2, 2, 0, 2), sp.Rational(43)),
        ("v1", (1, 0, 3, 2, 0, 1), sp.Rational(50)),
        ("v1", (1, 0, 3, 1, 0, 2), sp.Rational(1)),
        ("v1", (0, 0, 2, 3, 0, 1), sp.Rational(200)),
        ("v1", (0, 0, 3, 2, 0, 1), sp.Rational(50)),
        ("s3", (3, 5, 2, 0, 0, 0), sp.Rational(53, 6)),
        ("s3", (3, 4, 2, 0, 0, 0), sp.Rational(211, 20)),
        ("s3", (3, 4, 1, 0, 2, 0), sp.Rational(312)),
        ("s3", (3, 3, 2, 0, 0, 0), sp.Rational(149, 20)),
        ("s3", (3, 3, 1, 0, 3, 0), sp.Rational(136)),
        ("s3", (3, 2, 2, 0, 3, 0), sp.Rational(24)),
        ("s3", (3, 2, 2, 0, 2, 0), sp.Rational(699, 22)),
        ("s3", (3, 2, 2, 0, 1, 0), sp.Rational(225)),
        ("s3", (3, 2, 1, 0, 3, 0), sp.Rational(718)),
        ("s3", (3, 1, 2, 0, 3, 0), sp.Rational(52)),
        ("s3", (3, 1, 2, 0, 2, 0), sp.Rational(864, 11)),
        ("s3", (2, 6, 1, 0, 0, 0), sp.Rational(624)),
        ("s3", (2, 5, 1, 0, 1, 0), sp.Rational(1992)),
        ("s3", (2, 5, 1, 0, 0, 0), sp.Rational(5586)),
        ("s3", (2, 4, 1, 0, 1, 0), sp.Rational(16122)),
        ("s3", (2, 2, 2, 0, 3, 0), sp.Rational(176)),
        ("s3", (1, 1, 3, 3, 0, 2), sp.Rational(48)),
        ("s3", (1, 1, 3, 2, 0, 2), sp.Rational(144)),
        ("s3", (1, 1, 2, 3, 0, 2), sp.Rational(1196)),
        ("s3", (1, 0, 3, 3, 0, 2), sp.Rational(24)),
        ("s3", (1, 0, 3, 2, 0, 2), sp.Rational(72)),
        ("s3", (1, 0, 3, 1, 0, 2), sp.Rational(72)),
        ("s3", (1, 0, 2, 3, 0, 2), sp.Rational(566)),
        ("s3", (1, 0, 2, 2, 0, 2), sp.Rational(1466)),
        ("s3", (0, 1, 3, 3, 0, 2), sp.Rational(624)),
        ("s3", (0, 1, 3, 3, 0, 1), sp.Rational(150)),
        ("s3", (0, 1, 3, 2, 0, 2), sp.Rational(1008)),
        ("s3", (0, 0, 3, 3, 0, 2), sp.Rational(408)),
        ("s3", (0, 0, 3, 2, 0, 2), sp.Rational(648)),
        ("s3", (0, 0, 3, 1, 0, 2), sp.Rational(456)),
    ]

    residual = sp.expand(num)
    for name, exps, coeff in cert:
        residual -= coeff * monomial(vars_, exps) * constraints[name]

    assert_coeff_nonnegative(residual, vars_, "s7 dPhi/db residual")
    print("PASS y=1 x=q,s2,s7 half-face has exact b-descent to s3=0 or b=1 boundary")


if __name__ == "__main__":
    main()
