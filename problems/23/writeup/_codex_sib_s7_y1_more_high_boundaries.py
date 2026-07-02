"""Exact positivity for two additional high y=1 boundary clusters.

The active-set coverage scan occasionally finds high positive boundary clusters
not covered by the low survivor files.  This script records exact positivity
for the two observed families:

1. u=1, s7 capacity with a=c=d=e=f=x=v=1 and b>=1.
2. x=q, s5 capacity with a=1, b=d=2, c=e=v=x-1,
   f=x^2/(x+1), x>=2.
"""

from __future__ import annotations

import sympy as sp


def coeffs_positive(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef > 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


def phi(a, b, c, d, e, f, x, y, u, v):
    q = u + v
    S = a + b + c + d + e + f
    m = x * q + v
    N = S + x + y + q
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - S)


def family_u1_s7() -> None:
    b, B0 = sp.symbols("b B0", positive=True)
    one = sp.Integer(1)
    Phi = phi(one, b, one, one, one, one, one, one, one, one)
    P = sp.together(Phi).as_numer_denom()[0]
    shifted = sp.expand(P.subs(b, B0 + 1))
    assert coeffs_positive(shifted, (B0,))
    assert sp.factor(Phi.subs(b, 1)) == 25


def family_xq_s5() -> None:
    x, X0 = sp.symbols("x X0", positive=True)
    a = sp.Integer(1)
    b = d = sp.Integer(2)
    c = e = v = x - 1
    f = x ** 2 / (x + 1)
    y = u = sp.Integer(1)
    Phi = phi(a, b, c, d, e, f, x, y, u, v)
    P = sp.factor(sp.together(Phi).as_numer_denom()[0])
    shifted = sp.expand(P.subs(x, X0 + 2))
    assert coeffs_positive(shifted, (X0,))
    assert Phi.subs(x, 2) > 0


def main() -> None:
    family_u1_s7()
    family_xq_s5()
    print("PASS y=1 additional high boundary families are positive")


if __name__ == "__main__":
    main()
