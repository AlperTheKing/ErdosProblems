"""Exact positivity for a broad y=1,u=1,s4 lower-bound family.

Consider the family

    y=1, u=1, s4=0, a=b=d=f=1.

The active equation s4=0 gives

    x = (1 + 2c - v) / (1 + v).

Feasibility is equivalent to e >= c >= v >= 1.  Use the nonnegative
parametrization

    v = 1 + V,
    c = v + R,
    e = c + E.

Then x=(2R+V+2)/(V+2), all denominators are positive, and the cleared numerator
of Phi is coefficientwise positive in R,E,V.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    R, E, V = sp.symbols("R E V", nonnegative=True)
    a = b = d = f = u = y = sp.Integer(1)
    v = 1 + V
    c = 1 + V + R
    e = c + E
    x = sp.factor((1 + 2 * c - v) / (1 + v))

    m = x * u + x * v + y * v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    phi = 2 * (N**2 - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - (a + b + c + d + e + f))

    numerator, denominator = sp.together(phi).as_numer_denom()
    denominator = sp.factor(denominator)
    assert denominator == (V + 2) ** 2 * (2 * R + 2 * V + 3) * (E + R + V + 1) * (
        2 * E * R
        + 2 * E * V
        + 3 * E
        + 2 * R**2
        + 4 * R * V
        + 6 * R
        + 2 * V**2
        + 6 * V
        + 5
    )
    poly = sp.Poly(sp.expand(numerator), R, E, V)
    coeffs = [sp.Integer(coeff) for coeff in poly.coeffs()]
    assert len(coeffs) == 130
    assert min(coeffs) == 8
    assert all(coeff > 0 for coeff in coeffs)
    print("PASS y=1,u=1,s4,a=b=d=f=1 family is coefficientwise positive")


if __name__ == "__main__":
    main()
