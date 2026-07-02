"""Exact certificate for the SIB S7 subface y=1,x=1,v=1,s4=0.

This is one endpoint of the y=1 capacity-fiber reduction.  On this face,

    m = u + 2 = Y,      u = Y - 2.

After shifting a,b,c,d,e,f by 1, the cleared numerator of Phi is a
coefficient-nonnegative polynomial plus nonnegative multiples of the shifted
s2 and s7 slacks.  Therefore Phi >= 0 on this subface.
"""

from __future__ import annotations

import sympy as sp


def coeffs_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef >= 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


def monomial(vars_: tuple[sp.Symbol, ...], exps: tuple[int, ...]) -> sp.Expr:
    out = sp.Integer(1)
    for var, exp in zip(vars_, exps):
        out *= var ** exp
    return out


def main() -> None:
    a, b, c, d, e, f = sp.symbols("a b c d e f", positive=True)
    vars_ = (a, b, c, d, e, f)
    x = sp.Integer(1)
    y = sp.Integer(1)
    v = sp.Integer(1)

    S = a + b + c + d + e + f
    Y = a * c + b * f + c * f
    u = Y - 2
    m = Y
    N = S + x + y + u + v
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = sp.factor(2 * (N * N - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - S))

    # Cleared shifted numerator on the face.
    num = sp.together(Phi).as_numer_denom()[0]
    shift = {var: var + 1 for var in vars_}
    P = sp.expand(num.subs(shift))

    # Shifted feasibility slacks still active on this subface.
    Y0 = Y.subs(shift)
    s2 = sp.expand((d + e - (u + v)).subs(shift))  # d+e-u-v
    s7 = sp.expand((a * e + d * f + e * f - m).subs(shift))
    assert sp.factor(s2 - (d + e - Y0 + 3)) == 0
    assert sp.factor(s7 - (a * e + d * f + e * f - Y).subs(shift)) == 0

    cert = [
        (s2, (0, 0, 0, 0, 0, 0), sp.Rational(350)),
        (s2, (0, 0, 0, 0, 0, 1), sp.Rational(270)),
        (s2, (0, 0, 0, 0, 0, 2), sp.Rational(1101, 2)),
        (s2, (0, 0, 1, 0, 0, 0), sp.Rational(800)),
        (s2, (0, 1, 0, 0, 0, 1), sp.Rational(195, 2)),
        (s2, (0, 2, 0, 0, 0, 1), sp.Rational(107, 4)),
        (s2, (1, 0, 0, 0, 0, 0), sp.Rational(190)),
        (s2, (1, 0, 1, 0, 0, 0), sp.Rational(1745, 2)),
        (s2, (1, 0, 1, 0, 0, 1), sp.Rational(385, 4)),
        (s2, (2, 0, 1, 0, 0, 0), sp.Rational(173, 4)),
        (s7, (0, 0, 0, 0, 0, 0), sp.Rational(375, 2)),
        (s7, (0, 0, 1, 0, 0, 1), sp.Rational(605)),
        (s7, (0, 0, 2, 0, 0, 0), sp.Rational(144)),
        (s7, (0, 1, 1, 0, 0, 0), sp.Rational(7, 2)),
        (s7, (1, 0, 0, 0, 0, 0), sp.Rational(1185, 4)),
        (s7, (1, 0, 1, 0, 1, 0), sp.Rational(295)),
        (s7, (1, 0, 2, 0, 0, 0), sp.Rational(335, 2)),
    ]

    remainder = P
    for slack, exps, coeff in cert:
        remainder = sp.expand(remainder - coeff * monomial(vars_, exps) * slack)

    assert coeffs_nonnegative(remainder, vars_)
    assert sp.Poly(remainder, *vars_).coeff_monomial((0, 0, 0, 0, 0, 0)) == 375
    print("PASS y=1,x=1,v=1,s4=0 exact slack certificate")


if __name__ == "__main__":
    main()
