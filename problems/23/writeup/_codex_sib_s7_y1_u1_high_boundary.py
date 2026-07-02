"""Exact positivity for a high y=1,u=1 boundary family.

The basin scan sometimes lands on a high boundary family on the u=1,s4 branch:

    a=b=d=1,       c=e=f=x=v=t.

All capacity slacks are tight.  The cleared Phi numerator is

    25*(2t^3+4t^2+5t+4),

so the family is strictly positive for t>=1.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    t, T = sp.symbols("t T", positive=True)
    a = b = d = y = u = sp.Integer(1)
    c = e = f = x = v = t
    q = u + v
    S = a + b + c + d + e + f
    m = x * q + v
    N = S + x + y + q
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * B / (e * Y) - S)

    caps = {
        "s4": Y,
        "s5": a * e + b * f + c * f,
        "s6": a * c + d * f + e * f,
        "s7": a * e + d * f + e * f,
    }
    assert all(sp.factor(expr - m) == 0 for expr in caps.values())
    assert sp.factor(e - v) == 0
    assert sp.factor(d + e - u - v) == 0
    assert sp.factor(b + c - x - y) == 0

    P, den = sp.together(Phi).as_numer_denom()
    assert den != 0
    assert sp.factor(P - 25 * (2 * t ** 3 + 4 * t ** 2 + 5 * t + 4)) == 0
    shifted = sp.Poly(sp.expand(P.subs(t, T + 1)), T)
    assert all(coef > 0 for coef in shifted.all_coeffs())

    print("PASS y=1,u=1 high boundary family is positive")


if __name__ == "__main__":
    main()
