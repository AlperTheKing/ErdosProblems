"""Exact positivity for observed x=q,s1 endpoint support families.

The x=q,s1=0 endpoint scan produced only three support families, all subfaces
of already-closed x=q families.  This file records direct one-parameter
positivity checks for them:

  A: f=1, s1=s3=s4=s5=s6=s7=0, u=1.
  B: a=1, s1=s3=s4=s5=s6=s7=0, u=1.
  C: d=f=1, s1=s2=s3=s6=s7=0, u=1.

In every case y=1 and x=q, hence v=x-1.  Put t=x-1 >= 1.
"""

from __future__ import annotations

import sympy as sp


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


def check_family_a() -> None:
    T = sp.symbols("T", nonnegative=True)
    t = 1 + T
    x = t + 1
    a = t + 2 - 1 / t
    b = d = sp.Integer(2)
    c = e = v = t
    f = u = sp.Integer(1)
    Phi = phi(a, b, c, d, e, f, x, u, v)
    num, den = sp.together(Phi).as_numer_denom()
    assert den.subs(T, 0) > 0
    assert coeffs_positive(num, (T,))


def check_family_b() -> None:
    T = sp.symbols("T", nonnegative=True)
    t = 1 + T
    x = t + 1
    a = sp.Integer(1)
    b = d = sp.Integer(2)
    c = e = v = t
    f = x**2 / (x + 1)
    u = sp.Integer(1)
    Phi = phi(a, b, c, d, e, f, x, u, v)
    num, den = sp.together(Phi).as_numer_denom()
    assert den.subs(T, 0) > 0
    assert coeffs_positive(num, (T,))


def check_family_c() -> None:
    T = sp.symbols("T", nonnegative=True)
    t = 1 + T
    x = t + 1
    a = t + 2
    b = sp.Integer(2)
    c = e = v = t
    d = f = u = sp.Integer(1)
    Phi = phi(a, b, c, d, e, f, x, u, v)
    num, den = sp.together(Phi).as_numer_denom()
    assert den.subs(T, 0) > 0
    assert coeffs_positive(num, (T,))


def main() -> None:
    check_family_a()
    check_family_b()
    check_family_c()
    print("PASS y=1 x=q,s1 observed endpoint families are positive")


if __name__ == "__main__":
    main()
