"""Exact positivity for the s2-branch critical survivor families.

The y=1,s2=0 capacity-critical scan found only high positive families on
the s4 and s7 branches, both with b=f=1 and s1=s5=0.  This file proves the
corresponding whole active families positive, so the critical subfamilies are
harmless.

Family A: s4 capacity, b=f=1, e=v=c, s5=0.
Use parameters d>=1, c>=x>=1 and

    a=(x(c+d)-1)/c.

The remaining feasibility is d>=1, 1<=x<=c.  With x=1+X, c=x+C, d=1+D,
the cleared Phi numerator is P0(X)+R, where R has nonnegative coefficients
and P0 has no roots on X>=0.

Family B: s7 capacity, b=f=1, e=v, d=c-e+1, s5=0.
Use x>=1, c>=x, c>=e and

    a=(x(c+1)-c+e-1)/e.

With x=1+X, e=1+E, c=1+X+E+H, all coefficients of the cleared Phi numerator
are nonnegative.
"""

from __future__ import annotations

import sympy as sp


def coeffs_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef >= 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


def phi_num(a: sp.Expr, b: sp.Expr, c: sp.Expr, d: sp.Expr, e: sp.Expr, f: sp.Expr, x: sp.Expr, v: sp.Expr) -> sp.Expr:
    y = sp.Integer(1)
    q = d + e
    S = a + b + c + d + e + f
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    M = x * q + v
    N = S + y + x + q
    Phi = 2 * (N * N - 25 * M) - 75 * ((M - v) * A / Z + v * B / (e * Y) - S)
    return sp.together(Phi).as_numer_denom()[0]


def family_s4() -> None:
    X, C, D = sp.symbols("X C D", nonnegative=True)
    x = 1 + X
    c = x + C
    d = 1 + D
    b = f = sp.Integer(1)
    e = v = c
    a = sp.factor((x * (c + d) - 1) / c)

    assert sp.factor(a - 1 - (X * (c + d) + D) / c) == 0

    P = sp.expand(phi_num(a, b, c, d, e, f, x, v))
    P0 = sp.expand(P.subs({C: 0, D: 0}))
    rest = sp.expand(P - P0)
    assert coeffs_nonnegative(rest, (X, C, D))

    poly0 = sp.Poly(sp.cancel(P0 / (X + 1)), X)
    assert poly0.eval(0) > 0
    assert poly0.count_roots(0, sp.oo) == 0


def family_s7() -> None:
    X, E, H = sp.symbols("X E H", nonnegative=True)
    x = 1 + X
    e = v = 1 + E
    c = 1 + X + E + H
    d = c - e + 1
    b = f = sp.Integer(1)
    a = sp.factor((x * (c + 1) - c + e - 1) / e)

    assert sp.factor(a - 1 - X * (E + H + X + 2) / (E + 1)) == 0

    P = sp.expand(phi_num(a, b, c, d, e, f, x, v))
    assert coeffs_nonnegative(P, (X, E, H))


def main() -> None:
    family_s4()
    family_s7()
    print("PASS y=1,s2 survivor families on s4/s7 are positive")


if __name__ == "__main__":
    main()
