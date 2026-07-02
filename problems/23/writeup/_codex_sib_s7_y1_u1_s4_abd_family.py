"""Exact positivity for the y=1,u=1,s4,a=b=d=1 family.

Set

    y=1, u=1, a=b=d=1, s4=0.

The equation s4=0 gives

    c = (x(1+v)+v-f)/(1+f).

Feasibility includes `v>=f` from `s3>=0`, and `e>=max(c,v)`.  Since

    c-v = (1+v)(x-f)/(1+f),

the feasible region splits into two chambers:

1. `x>=f`: write `f=1+F`, `x=f+X`, `v=f+R`, `e=c+E`.
2. `f>=x`: write `x=1+X`, `f=x+F`, `v=f+R`, `e=v+E`.

In both chambers, all parameters are nonnegative and the cleared numerator of
Phi is coefficientwise positive.
"""

from __future__ import annotations

import sympy as sp


def phi_expr(c: sp.Expr, e: sp.Expr, f: sp.Expr, x: sp.Expr, v: sp.Expr) -> sp.Expr:
    a = b = d = u = y = sp.Integer(1)
    m = x * u + x * v + y * v
    n = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return 2 * (n**2 - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f))


def assert_positive_chamber(expr: sp.Expr, variables: tuple[sp.Symbol, ...], expected_terms: int) -> None:
    numerator, denominator = sp.together(expr).as_numer_denom()
    assert denominator != 0
    poly = sp.Poly(sp.expand(numerator), *variables)
    coeffs = [sp.Integer(coeff) for coeff in poly.coeffs()]
    assert len(coeffs) == expected_terms
    assert min(coeffs) == 2
    assert all(coeff > 0 for coeff in coeffs)


def main() -> None:
    F, R, X, E = sp.symbols("F R X E", nonnegative=True)

    f1 = 1 + F
    x1 = f1 + X
    v1 = f1 + R
    c1 = sp.factor((x1 * (1 + v1) + v1 - f1) / (1 + f1))
    e1 = c1 + E
    assert sp.factor(c1 - v1) == sp.factor((1 + v1) * (x1 - f1) / (1 + f1))
    assert_positive_chamber(phi_expr(c1, e1, f1, x1, v1), (F, R, X, E), 1213)

    F2, R2, X2, E2 = sp.symbols("F2 R2 X2 E2", nonnegative=True)
    x2 = 1 + X2
    f2 = x2 + F2
    v2 = f2 + R2
    c2 = sp.factor((x2 * (1 + v2) + v2 - f2) / (1 + f2))
    e2 = v2 + E2
    assert sp.factor(v2 - c2) == sp.factor((1 + v2) * (f2 - x2) / (1 + f2))
    assert_positive_chamber(phi_expr(c2, e2, f2, x2, v2), (F2, R2, X2, E2), 1133)

    print("PASS y=1,u=1,s4,a=b=d=1 family is positive in both chambers")


if __name__ == "__main__":
    main()
