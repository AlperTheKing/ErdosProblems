"""Exact certificates for y=1,x=1,v=1,s_j=0, j=4..7.

These are endpoint leaves produced by the y=1 capacity-fiber and x=1 v-fiber
reductions.  On y=x=v=1 and s_j=0, the capacity equality determines

    u = M_j - 2,

where M_j is the right-hand side of s_j.  For each j, after shifting
a,b,c,d,e,f by 1, the cleared numerator of Phi is a coefficient-nonnegative
polynomial plus nonnegative multiples of the shifted feasibility slacks.
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
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    caps = {
        "s4": Y,
        "s5": a * e + b * f + c * f,
        "s6": a * c + d * f + e * f,
        "s7": a * e + d * f + e * f,
    }

    certificates = {
        "s4": [
            ("s2", (0, 0, 0, 0, 0, 0), sp.Rational(350)),
            ("s2", (0, 0, 0, 0, 0, 1), sp.Rational(270)),
            ("s2", (0, 0, 0, 0, 0, 2), sp.Rational(1101, 2)),
            ("s2", (0, 0, 1, 0, 0, 0), sp.Rational(800)),
            ("s2", (0, 1, 0, 0, 0, 1), sp.Rational(195, 2)),
            ("s2", (0, 2, 0, 0, 0, 1), sp.Rational(107, 4)),
            ("s2", (1, 0, 0, 0, 0, 0), sp.Rational(190)),
            ("s2", (1, 0, 1, 0, 0, 0), sp.Rational(1745, 2)),
            ("s2", (1, 0, 1, 0, 0, 1), sp.Rational(385, 4)),
            ("s2", (2, 0, 1, 0, 0, 0), sp.Rational(173, 4)),
            ("s7", (0, 0, 0, 0, 0, 0), sp.Rational(375, 2)),
            ("s7", (0, 0, 1, 0, 0, 1), sp.Rational(605)),
            ("s7", (0, 0, 2, 0, 0, 0), sp.Rational(144)),
            ("s7", (0, 1, 1, 0, 0, 0), sp.Rational(7, 2)),
            ("s7", (1, 0, 0, 0, 0, 0), sp.Rational(1185, 4)),
            ("s7", (1, 0, 1, 0, 1, 0), sp.Rational(295)),
            ("s7", (1, 0, 2, 0, 0, 0), sp.Rational(335, 2)),
        ],
        "s5": [
            ("s2", (0, 0, 0, 0, 0, 0), sp.Rational(350)),
            ("s2", (0, 0, 0, 0, 0, 1), sp.Rational(270)),
            ("s2", (0, 0, 0, 0, 0, 2), sp.Rational(22)),
            ("s2", (0, 0, 1, 0, 0, 1), sp.Rational(663, 2)),
            ("s2", (0, 0, 2, 0, 0, 1), sp.Rational(65, 4)),
            ("s2", (0, 1, 0, 0, 0, 1), sp.Rational(477, 2)),
            ("s2", (0, 1, 0, 0, 1, 0), sp.Rational(105)),
            ("s2", (0, 1, 0, 0, 2, 0), sp.Rational(85)),
            ("s2", (1, 0, 0, 0, 0, 0), sp.Rational(190)),
            ("s2", (1, 0, 0, 0, 1, 0), sp.Rational(345, 2)),
            ("s2", (1, 0, 0, 0, 2, 0), sp.Rational(226)),
            ("s2", (2, 0, 0, 0, 0, 0), sp.Rational(205, 2)),
            ("s2", (2, 0, 0, 0, 1, 0), sp.Rational(290)),
            ("s2", (2, 0, 1, 0, 0, 0), sp.Rational(126)),
            ("s4", (0, 3, 0, 0, 0, 0), sp.Rational(24)),
            ("s4", (1, 0, 0, 0, 0, 0), sp.Rational(905, 2)),
            ("s4", (1, 0, 0, 0, 1, 0), sp.Rational(1607)),
            ("s4", (1, 0, 0, 0, 2, 0), sp.Rational(437)),
            ("s4", (1, 0, 1, 0, 0, 0), sp.Rational(623)),
            ("s4", (1, 0, 1, 0, 1, 0), sp.Rational(207)),
            ("s4", (1, 1, 0, 0, 0, 0), sp.Rational(9, 2)),
            ("s4", (2, 0, 0, 1, 0, 0), sp.Rational(40)),
            ("s4", (2, 0, 1, 0, 0, 0), sp.Rational(102)),
            ("s6", (0, 0, 0, 0, 0, 0), sp.Rational(895, 2)),
        ],
        "s6": [
            ("s2", (0, 0, 0, 0, 0, 0), sp.Rational(685)),
            ("s2", (0, 0, 0, 0, 0, 1), sp.Rational(714)),
            ("s2", (0, 0, 0, 0, 0, 2), sp.Rational(22)),
            ("s2", (0, 0, 0, 0, 1, 1), sp.Rational(479)),
            ("s2", (0, 0, 1, 0, 0, 0), sp.Rational(422)),
            ("s2", (0, 0, 2, 0, 0, 0), sp.Rational(49)),
            ("s2", (1, 0, 0, 0, 0, 0), sp.Rational(190)),
            ("s2", (1, 0, 1, 0, 0, 0), sp.Rational(661)),
            ("s2", (1, 0, 2, 0, 0, 0), sp.Rational(184)),
            ("s2", (2, 0, 1, 0, 0, 0), sp.Rational(15)),
            ("s4", (0, 0, 0, 0, 0, 0), sp.Rational(75)),
        ],
        "s7": [
            ("s2", (0, 0, 0, 0, 0, 0), sp.Rational(677)),
            ("s2", (0, 0, 0, 0, 0, 1), sp.Rational(714)),
            ("s2", (0, 0, 0, 0, 0, 2), sp.Rational(22)),
            ("s2", (0, 0, 0, 0, 1, 0), sp.Rational(1950)),
            ("s2", (0, 0, 0, 0, 1, 1), sp.Rational(1133)),
            ("s2", (0, 0, 0, 0, 2, 0), sp.Rational(542)),
            ("s2", (0, 0, 0, 1, 0, 0), sp.Rational(4)),
            ("s2", (0, 0, 0, 1, 1, 0), sp.Rational(51)),
            ("s2", (0, 1, 0, 0, 1, 0), sp.Rational(271)),
            ("s2", (0, 1, 0, 0, 2, 0), sp.Rational(149)),
            ("s2", (1, 0, 0, 0, 0, 0), sp.Rational(190)),
            ("s2", (1, 0, 0, 0, 1, 0), sp.Rational(829)),
            ("s2", (1, 0, 0, 0, 2, 0), sp.Rational(172)),
            ("s4", (0, 0, 0, 0, 0, 0), sp.Rational(75)),
        ],
    }

    shift = {var: var + 1 for var in vars_}
    shifted_caps = {name: sp.expand(cap.subs(shift)) for name, cap in caps.items()}

    for cap_name, Mj in caps.items():
        u = Mj - 2
        m = Mj
        N = S + x + y + u + v
        Phi = sp.factor(2 * (N * N - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - S))
        P = sp.expand(sp.together(Phi).as_numer_denom()[0].subs(shift))

        shifted_slacks = {
            "u": sp.expand((u - 1).subs(shift)),
            "s2": sp.expand((d + e - (u + v)).subs(shift)),
            "s3": sp.expand((b + c - x - y).subs(shift)),
        }
        for other_name, other_M in caps.items():
            if other_name != cap_name:
                shifted_slacks[other_name] = sp.expand((other_M - Mj).subs(shift))

        remainder = P
        for slack_name, exps, coeff in certificates[cap_name]:
            remainder = sp.expand(remainder - coeff * monomial(vars_, exps) * shifted_slacks[slack_name])

        assert coeffs_nonnegative(remainder, vars_), cap_name
        assert sp.Poly(remainder, *vars_).coeff_monomial((0, 0, 0, 0, 0, 0)) == 375, cap_name

    print("PASS y=1,x=1,v=1 capacity endpoints s4..s7 exact slack certificates")


if __name__ == "__main__":
    main()
