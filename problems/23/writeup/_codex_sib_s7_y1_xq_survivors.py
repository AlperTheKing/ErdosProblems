"""Exact positivity checks for noncentral x=q,u=1 survivor supports.

The y=1 capacity basin scan found two positive noncentral support families on
the balanced fiber x=q with u=1.  This file records their exact reductions and
checks Phi >= 0 on each family.

These checks do not close the full x=q branch; they remove the finite survivor
supports observed by the scanner so the remaining FJ task is smaller.
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


def coeffs_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef >= 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


def phi_expr(a, b, c, d, e, f, x):
    y = sp.Integer(1)
    q = x
    u = sp.Integer(1)
    v = x - 1
    m = x * x + x - 1
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return sp.factor(2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f)))


def main() -> None:
    # Family A: f=1, s3=0, all four capacities tight, x=q, u=1.
    # Equations reduce to:
    #   e=c, a=(x^2-2)/c, b=d=x+1-c, x>=2, x-1<=c<=x.
    X, r = sp.symbols("X r", nonnegative=True)
    x = 2 + X
    c = x - 1 + r
    a = (x * x - 2) / c
    b = d = x + 1 - c
    e = c
    f = sp.Integer(1)
    Phi = phi_expr(a, b, c, d, e, f, x)
    num, den = sp.together(Phi).as_numer_denom()
    assert den.subs({X: 0, r: 0}) > 0

    # r is in [0,1].  Bernstein coefficients in r are coefficient-positive in X.
    for coeff in bernstein_coeffs(num, r):
        assert coeffs_nonnegative(coeff, (X,))
        assert coeff.subs(X, 0) > 0

    # Family B: d=f=1, s1=s2=s3=s6=s7=0, x=q, u=1.
    # Equations reduce to:
    #   a=x+1, b=2, c=e=x-1, x>=2.
    a2 = x + 1
    b2 = sp.Integer(2)
    c2 = e2 = x - 1
    d2 = f2 = sp.Integer(1)
    Phi2 = sp.factor(phi_expr(a2, b2, c2, d2, e2, f2, x))
    num2, den2 = sp.together(Phi2).as_numer_denom()
    assert den2.subs(X, 0) > 0
    assert coeffs_nonnegative(num2, (X,))
    assert num2.subs(X, 0) > 0

    print("PASS y=1 x=q,u=1 survivor families are positive")


if __name__ == "__main__":
    main()
