"""Exact positivity for the y=1,u=1,a=b=d=f=1 capacity family.

This closes the broad lower-bound family exposed by the post-inactive u1 shape
profile.  Set

    y=1, u=1, a=b=d=f=1.

Then s5=s6 and

    s4 - s5 = c-e,
    s7 - s5 = e-c.

Thus feasible s5=0 or s6=0 forces c=e and reduces to the common ridge.  The
only full-dimensional capacity faces are s4=0 with e>=c>=v and s7=0 with
c>=e>=v.  Both have coefficientwise-positive cleared Phi numerators in natural
nonnegative coordinates.
"""

from __future__ import annotations

import sympy as sp


def phi_expr(c: sp.Expr, e: sp.Expr, v: sp.Expr, x: sp.Expr) -> sp.Expr:
    a = b = d = f = u = y = sp.Integer(1)
    m = x * u + x * v + y * v
    n = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return 2 * (n**2 - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f))


def assert_positive_poly(expr: sp.Expr, variables: tuple[sp.Symbol, ...]) -> None:
    numerator, denominator = sp.together(expr).as_numer_denom()
    assert sp.factor(denominator) != 0
    poly = sp.Poly(sp.expand(numerator), *variables)
    coeffs = [sp.Integer(coeff) for coeff in poly.coeffs()]
    assert len(coeffs) == 130
    assert min(coeffs) == 8
    assert all(coeff > 0 for coeff in coeffs)


def main() -> None:
    c, e, v, x = sp.symbols("c e v x", positive=True)
    m = x * (1 + v) + v
    s4 = 2 * c + 1 - m
    s5 = c + e + 1 - m
    s6 = c + e + 1 - m
    s7 = 2 * e + 1 - m
    assert sp.expand(s5 - s6) == 0
    assert sp.expand(s4 - s5 - (c - e)) == 0
    assert sp.expand(s7 - s5 - (e - c)) == 0

    R, E, V = sp.symbols("R E V", nonnegative=True)
    v4 = 1 + V
    c4 = 1 + V + R
    e4 = c4 + E
    x4 = (1 + 2 * c4 - v4) / (1 + v4)
    assert_positive_poly(phi_expr(c4, e4, v4, x4), (R, E, V))

    C, R2, V2 = sp.symbols("C R2 V2", nonnegative=True)
    v7 = 1 + V2
    e7 = v7 + R2
    c7 = e7 + C
    x7 = (1 + 2 * e7 - v7) / (1 + v7)
    assert_positive_poly(phi_expr(c7, e7, v7, x7), (C, R2, V2))

    print("PASS y=1,u=1,a=b=d=f=1 capacity family is coefficientwise positive")


if __name__ == "__main__":
    main()
