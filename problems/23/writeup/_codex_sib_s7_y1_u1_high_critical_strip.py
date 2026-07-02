"""Exact positivity for the high y=1,u=1 critical strip.

The y=1,u=1 capacity-critical stress finds a high family with

    a=b=d=1,  c=e=v,  x=f,  1 <= f <= e.

This includes the earlier diagonal high boundary c=e=f=x=v, but is broader.
The capacity equalities s5=s6=s7=0 hold automatically, and s4 is the selected
capacity when x=f.  The remaining feasibility condition is s3=e-f>=0.

This file proves a stronger fact: Phi is strictly positive on the full strip
e>=1, 1<=f<=e, by substituting e=1+E and f=1+R*E and checking Bernstein
coefficients in R with coefficient-positive E-polynomials.
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


def coeffs_positive(expr: sp.Expr, var: sp.Symbol) -> bool:
    P = sp.Poly(sp.expand(expr), var)
    return all(coef >= 0 for _mon, coef in P.terms()) and P.eval(0) > 0


def main() -> None:
    e, f, E, R = sp.symbols("e f E R", nonnegative=True)
    one = sp.Integer(1)
    a = b = d = y = u = one
    c = v = e
    x = f
    q = u + v

    S = a + b + c + d + e + f
    m = x * q + v
    N = S + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - S)

    assert sp.factor(Y - m) == 0
    assert sp.factor(a * e + b * f + c * f - m) == 0
    assert sp.factor(a * c + d * f + e * f - m) == 0
    assert sp.factor(a * e + d * f + e * f - m) == 0
    assert sp.factor(e - v) == 0
    assert sp.factor(d + e - u - v) == 0
    assert sp.factor(b + c - x - y - (e - f)) == 0

    num, den = sp.together(Phi).as_numer_denom()
    assert den.subs({e: 1, f: 1}) > 0
    strip_num = sp.factor(num.subs({e: 1 + E, f: 1 + R * E}))
    for coeff in bernstein_coeffs(strip_num, R):
        assert coeffs_positive(coeff, E), sp.factor(coeff)

    print("PASS y=1,u=1 high critical strip is Bernstein-positive")


if __name__ == "__main__":
    main()
