"""Exact positivity for the y=1,u=1,s1 endpoint s6 active family.

The s1 endpoint scan on the s6 capacity branch found a boundary family with

    v=e, u=1, d=1, b=1, s3=s4=s5=s7=0

and s6 as the active capacity.  These equations force

    c=e=v=x,       1 <= f <= c,
    a=(c^2-cf+2c-f)/c.

Set f=1+F and c=f+H=1+F+H.  The remaining domain is F,H>=0.  After clearing
denominators, the Phi numerator has the form

    P = P0(H) + F*P1(F,H),

where P1 has nonnegative coefficients and P0 has no roots on H>=0.
"""

from __future__ import annotations

import sympy as sp


def coeffs_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef >= 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


def main() -> None:
    c, f, F0, H0 = sp.symbols("c f F0 H0", positive=True)
    y = u = d = b = sp.Integer(1)
    e = v = x = c
    q = u + v
    a = sp.factor((c ** 2 - c * f + 2 * c - f) / c)

    S = a + b + c + d + e + f
    N = S + x + y + u + v
    m = x * q + v
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
    assert sp.factor(a - 1 - ((c - f) * (c + 1)) / c) == 0

    P, den = sp.together(Phi).as_numer_denom()
    assert den != 0

    shifted = sp.expand(P.subs({f: F0 + 1, c: F0 + H0 + 1}))
    P0 = sp.expand(shifted.subs(F0, 0))
    P1 = sp.factor((shifted - P0) / F0)
    assert coeffs_nonnegative(P1, (F0, H0))

    poly0 = sp.Poly(P0, H0)
    assert poly0.eval(0) > 0
    assert poly0.count_roots(0, sp.oo) == 0

    print("PASS y=1,u=1,s1 endpoint s6 active family is positive")


if __name__ == "__main__":
    main()
