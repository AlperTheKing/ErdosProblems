"""Exact positivity for a y=1,u=1 capacity critical survivor family.

The numerical critical-leaf scan for y=1,u=1,s6=0 found a noncentral positive
family with active constraints

    d=f=1,  s1=s2=s3=s7=0,

on the s6 capacity branch.  The same equations also make s6=s7=0.  This file
checks the exact parameterization and proves Phi>0 on the whole family.

Write c=e=v=t and b>=1.  Then

    x=b+t-1,
    a=(b*t+b+t^2-2)/t.

The remaining capacity slacks are s4=s5=b-1.  After clearing denominators, the
Phi numerator has the form

    P(b,t) = P0(T) + B * P1(B,T),   B=b-1, T=t-1,

where P1 has nonnegative coefficients and P0 has no roots on T>=0 and P0(0)>0.
"""

from __future__ import annotations

import sympy as sp


def coeffs_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef >= 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


def main() -> None:
    b, t, B0, T0 = sp.symbols("b t B0 T0", positive=True)
    y = u = d = f = sp.Integer(1)
    c = e = v = t
    x = b + t - 1
    q = u + v
    a = sp.factor((b * t + b + t ** 2 - 2) / t)

    S = a + b + c + d + e + f
    N = S + x + y + u + v
    m = x * q + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Bexpr = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + y * v * Bexpr / (e * Y) - S)

    caps = {
        "s4": Y,
        "s5": a * e + b * f + c * f,
        "s6": a * c + d * f + e * f,
        "s7": a * e + d * f + e * f,
    }
    slacks = {name: sp.factor(expr - m) for name, expr in caps.items()}
    assert slacks == {"s4": b - 1, "s5": b - 1, "s6": 0, "s7": 0}
    assert sp.factor(e - v) == 0
    assert sp.factor(d + e - q) == 0
    assert sp.factor(b + c - y - x) == 0
    assert sp.factor(x - 1 - (b + t - 2)) == 0
    assert sp.factor(a - 1 - ((t + 1) * (b + t - 2)) / t) == 0

    P, den = sp.together(Phi).as_numer_denom()
    assert den != 0

    shifted = sp.expand(P.subs({b: B0 + 1, t: T0 + 1}))
    P0 = sp.expand(shifted.subs(B0, 0))
    P1 = sp.factor((shifted - P0) / B0)
    assert coeffs_nonnegative(P1, (B0, T0))

    poly0 = sp.Poly(P0, T0)
    assert poly0.eval(0) > 0
    assert poly0.count_roots(0, sp.oo) == 0

    print("PASS y=1,u=1 s6/s7 critical survivor family is positive")


if __name__ == "__main__":
    main()
