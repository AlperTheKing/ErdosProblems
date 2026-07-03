"""Exact positivity for the y=1,u=1,s4,a=c=d=f=1 family.

Set

    y=1, u=1, s4=0, a=c=d=f=1.

Then `s4=0` gives

    b = x(1+v)+v-2.

With `x=1+X`, `v=1+V`, this is

    b = 1 + VX + 2V + 2X,

so `b>=1` and `s3=b-x>=0`. The remaining feasibility inequalities are
implied by taking `e=b+E`:

    s1=s2=e-v>=0,
    s5=e-1>=0,
    s6=e-b>=0,
    s7=2e-b-1>=0.

For X,V,E>=0, the cleared numerator of Phi is coefficientwise positive.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    X, V, E = sp.symbols("X V E", nonnegative=True)
    a = c = d = f = u = y = sp.Integer(1)
    x = 1 + X
    v = 1 + V
    b = sp.factor(x * (1 + v) + v - 2)
    e = b + E

    assert b == 1 + V * X + 2 * V + 2 * X
    assert sp.factor(b - x) == sp.factor(V * X + 2 * V + X)
    assert sp.factor(e - v) == sp.factor(E + V * X + V + 2 * X)

    m = x * u + x * v + y * v
    n = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    phi = 2 * (n**2 - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f))

    numerator, denominator = sp.together(phi).as_numer_denom()
    assert denominator != 0
    poly = sp.Poly(sp.expand(numerator), X, V, E)
    coeffs = [sp.Integer(coeff) for coeff in poly.coeffs()]
    assert len(coeffs) == 135
    assert min(coeffs) == 2
    assert all(coeff > 0 for coeff in coeffs)
    print("PASS y=1,u=1,s4,a=c=d=f=1 family is coefficientwise positive")


if __name__ == "__main__":
    main()
