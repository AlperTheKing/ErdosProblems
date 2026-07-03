"""Exact positivity for the y=1,u=1,s4,a=b=f=1 family.

Set

    y=1, u=1, s4=0, a=b=f=1.

Then `s4=0` gives

    c = (x(1+v)+v-1)/2.

Use

    x = 1+X, v = 1+V, e = c+E, d = 1+D.

For X,V,E,D>=0 all S7 feasibility inequalities hold:

* s3 = c-x = V(x+1)/2 >= 0,
* s1 = e-v >= c-v >= 0,
* s2 = d+e-1-v >= 0,
* s5 = e-c >= 0,
* s6 and s7 are then nonnegative.

The cleared numerator of Phi is coefficientwise positive in X,V,E,D.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    X, V, E, D = sp.symbols("X V E D", nonnegative=True)
    a = b = f = u = y = sp.Integer(1)
    x = 1 + X
    v = 1 + V
    c = sp.factor((x * (1 + v) + v - 1) / 2)
    e = c + E
    d = 1 + D

    assert sp.factor(c - x) == sp.factor(V * (x + 1) / 2)
    assert sp.factor(c - v) == sp.factor(X * (V + 2) / 2)

    m = x * u + x * v + y * v
    n = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    phi = 2 * (n**2 - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f))

    numerator, denominator = sp.together(phi).as_numer_denom()
    assert denominator != 0
    poly = sp.Poly(sp.expand(numerator), X, V, E, D)
    coeffs = [sp.Integer(coeff) for coeff in poly.coeffs()]
    assert len(coeffs) == 296
    assert min(coeffs) == 4
    assert all(coeff > 0 for coeff in coeffs)
    print("PASS y=1,u=1,s4,a=b=f=1 family is coefficientwise positive")


if __name__ == "__main__":
    main()
