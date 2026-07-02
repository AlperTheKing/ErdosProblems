"""Exact closure of the XQ_A one-step drop:f1 face.

In the x=q, y=u=1 chart, the XQ_A support is

    f=1, s3=s4=s5=s6=s7=0.

This script drops only f1, keeping s3=s4=s5=s6=s7=0.  On the positive
branch, the equations imply

    c=e, b=d=x+1-c, a=(x^2+x-1-f(x+1))/c.

The domain is x>=2, x-1<=c<=x, and 1<=f<=fmax where

    fmax = (x^2+x-1-c)/(x+1)

is exactly the boundary a=1.  With c=x-1+r, r in [0,1], and
f=1+T(fmax-1), the cleared Phi numerator is Bernstein-positive in (r,T);
each Bernstein coefficient is a coefficient-positive polynomial in X=x-2.
"""

from __future__ import annotations

import sympy as sp


def power_to_bernstein(poly: sp.Expr, var: sp.Symbol, degree: int) -> list[sp.Expr]:
    P = sp.Poly(poly, var)
    out = [sp.Integer(0)] * (degree + 1)
    for k in range(degree + 1):
        ak = P.coeff_monomial(var**k)
        if ak == 0:
            continue
        for i in range(k, degree + 1):
            out[i] += ak * sp.Rational(sp.binomial(i, k), sp.binomial(degree, k))
    return [sp.factor(c) for c in out]


def assert_coeff_positive_in_X(expr: sp.Expr, X: sp.Symbol, label: str) -> None:
    poly = sp.Poly(sp.factor(expr), X)
    bad = [c for c in poly.all_coeffs() if c < 0]
    assert not bad, (label, sp.factor(expr), bad[:3])


def assert_bernstein_X_positive(
    expr: sp.Expr, bounded: tuple[sp.Symbol, ...], X: sp.Symbol, label: str
) -> None:
    coeffs = [sp.factor(expr)]
    for var in bounded:
        next_coeffs: list[sp.Expr] = []
        for coeff in coeffs:
            degree = sp.Poly(coeff, var).degree()
            next_coeffs.extend(power_to_bernstein(coeff, var, degree))
        coeffs = next_coeffs

    for idx, coeff in enumerate(coeffs):
        assert_coeff_positive_in_X(coeff, X, f"{label}:bernstein[{idx}]")


def main() -> None:
    a, b, c, d, e, f, x = sp.symbols("a b c d e f x")
    X, R, T = sp.symbols("X R T")

    y = sp.Integer(1)
    u = sp.Integer(1)
    v = x - 1
    m = x * u + x * v + y * v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
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
    Phi = 2 * (N**2 - 25 * m) - 75 * (
        x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f)
    )

    # Algebraic reduction of the positive branch.
    s3 = b + c - x - 1
    s4 = Y - m
    s5 = a * e + b * f + c * f - m
    s6 = a * c + d * f + e * f - m
    s7 = a * e + d * f + e * f - m
    assert sp.factor(s4 - s5) == a * (c - e)
    assert sp.factor((s4 - s6).subs(e, c)) == f * (b - d)
    # Since a,f>=1, c=e and then d=b.  With s3=0, b=d=x+1-c.

    bb = x + 1 - c
    branch = {
        e: c,
        b: bb,
        d: bb,
        a: (m - f * (x + 1)) / c,
    }
    assert sp.factor(s3.subs(branch)) == 0
    assert sp.factor(s4.subs(branch)) == 0
    assert sp.factor(s5.subs(branch)) == 0
    assert sp.factor(s6.subs(branch)) == 0
    assert sp.factor(s7.subs(branch)) == 0

    Phi_branch = sp.factor(Phi.subs(branch))
    phi_num = sp.together(Phi_branch).as_numer_denom()[0]

    xx = X + 2
    rr = R
    cc = xx - 1 + rr
    fmax = (xx**2 + xx - 1 - cc) / (xx + 1)
    ff = 1 + T * (fmax - 1)

    # Clear the harmless denominator introduced by fmax.
    expr = sp.together(
        phi_num.subs({x: xx, c: cc, f: ff}) * (xx + 1) ** 3
    ).as_numer_denom()[0]
    expr = sp.factor(expr)
    assert_bernstein_X_positive(expr, (R, T), X, "Phi drop:f1")

    print("PASS y=1 XQ_A drop:f1 face is direct Bernstein-positive")


if __name__ == "__main__":
    main()
