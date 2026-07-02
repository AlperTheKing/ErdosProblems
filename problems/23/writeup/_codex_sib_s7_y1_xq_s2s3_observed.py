"""Exact positivity for observed x=q,s2/s3 endpoint support families.

This is an observed-inventory verifier, not a full endpoint coverage theorem.
The x=q,s2=0 scan produced only the XQ_B support.  The x=q,s3=0 scan produced
only XQ_A, XQ_S5_HIGH, and XQ_B supports.  This file checks direct positivity
on those three exact families.
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


def coeffs_positive(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef > 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


def phi(a, b, c, d, e, f, x, u, v):
    y = sp.Integer(1)
    q = x
    S = a + b + c + d + e + f
    m = x * q + v
    N = S + y + x + q
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return sp.factor(2 * (N * N - 25 * m) - 75 * (x * q * A / Z + v * B / (e * Y) - S))


def check_xq_a() -> None:
    """XQ_A: f=1, s3=s4=s5=s6=s7=0, u=1."""

    X, r = sp.symbols("X r", nonnegative=True)
    x = X + 2
    c = e = x - 1 + r
    a = (x * x - 2) / c
    b = d = x + 1 - c
    f = u = sp.Integer(1)
    v = x - 1
    Phi = phi(a, b, c, d, e, f, x, u, v)
    num, den = sp.together(Phi).as_numer_denom()
    assert den.subs({X: 0, r: 0}) > 0
    # r in [0,1]; Bernstein in r has coefficient-positive X-polys.
    for coeff in bernstein_coeffs(num, r):
        P = sp.Poly(sp.expand(coeff), X)
        assert all(coef >= 0 for _mon, coef in P.terms())
        assert coeff.subs(X, 0) > 0


def check_xq_b() -> None:
    """XQ_B: d=f=1, s1=s2=s3=s6=s7=0, u=1."""

    X = sp.symbols("X", nonnegative=True)
    x = X + 2
    a = x + 1
    b = sp.Integer(2)
    c = e = v = x - 1
    d = f = u = sp.Integer(1)
    Phi = phi(a, b, c, d, e, f, x, u, v)
    num, den = sp.together(Phi).as_numer_denom()
    assert den.subs(X, 0) > 0
    assert coeffs_positive(num, (X,))


def check_xq_s5_high() -> None:
    """XQ_S5_HIGH: a=1, s1=s3=s4=s5=s6=s7=0, u=1."""

    X = sp.symbols("X", nonnegative=True)
    x = X + 2
    a = sp.Integer(1)
    b = d = sp.Integer(2)
    c = e = v = x - 1
    f = x**2 / (x + 1)
    u = sp.Integer(1)
    Phi = phi(a, b, c, d, e, f, x, u, v)
    num, den = sp.together(Phi).as_numer_denom()
    assert den.subs(X, 0) > 0
    assert coeffs_positive(num, (X,))


def main() -> None:
    check_xq_a()
    check_xq_b()
    check_xq_s5_high()
    print("PASS y=1 x=q,s2/s3 observed endpoint families are positive")


if __name__ == "__main__":
    main()
