"""Exact positivity for the q=t top face of y=1,u=1,s4,a=1.

Family:

    y=1, u=1, s4=0, a=1.

This certifies the top face of the chamber V>=X, q>=V:

    q = t = M3/2,

where x=1+X, v=1+V, V=X+H, and M3=x(1+v)+v-3.
Since e>=c=1+q already implies d+e>=b+c=2+t, the remaining feasible
region is simply

    e = 1+q+E,  d = 1+D.

The selected capacity equation s4=0 gives f=(m-c)/(b+c).  After clearing
positive denominators, the numerator is coefficientwise nonnegative in
X,H,D,E.
"""

from __future__ import annotations

import sympy as sp


X, H, D, E = sp.symbols("X H D E", nonnegative=True)


def hand_cleared_numerator(d: sp.Expr, e: sp.Expr) -> sp.Expr:
    V = X + H
    x = 1 + X
    v = 1 + V
    m = sp.expand(x * (1 + v) + v)
    M3 = sp.expand(m - 3)
    q = M3 / 2
    t = q
    h = 2 + t
    c = 1 + q
    C = m - c
    z = e * m + d * C
    p_term = m - v

    sc_num = h * (3 + t + d + e) + C
    n_num = sc_num + h * (x + 2 + v)
    a_num = h * (m + e) + (d + e) * (h * h + C)
    b_num = h * m + e * (h * (1 + h) + C)
    base_num = 2 * n_num * n_num - 50 * m * h * h + 75 * sc_num * h
    return sp.expand(
        base_num * z * e * m
        - 75 * p_term * a_num * h * e * m
        - 75 * v * b_num * h * z
    )


def main() -> None:
    V = X + H
    x = 1 + X
    v = 1 + V
    m = sp.expand(x * (1 + v) + v)
    q = (m - 3) / 2
    d = 1 + D
    e = 1 + q + E
    numerator = hand_cleared_numerator(d, e)
    poly = sp.Poly(numerator, X, H, D, E)
    coeffs = [sp.Integer(c) if c.is_Integer else c for c in poly.coeffs()]
    negatives = [c for c in coeffs if c < 0]
    assert not negatives, negatives[:5]
    assert len(coeffs) == 855, len(coeffs)
    assert min(coeffs) == sp.Rational(1, 8), min(coeffs)
    print(
        "PASS y=1,u=1,s4,a=1 q=t=M3/2 top face coefficientwise-positive "
        f"terms={len(coeffs)} min={min(coeffs)}"
    )


if __name__ == "__main__":
    main()

