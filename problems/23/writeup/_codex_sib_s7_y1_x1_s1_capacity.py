"""Exact certificates for y=1,x=1,s1=0,s_j=0, j=4..7.

These are endpoint leaves from the y=1,x=1 capacity v-fiber reduction.  On
y=x=1 and s1=0, v=e.  On capacity face s_j=0, u = M_j - 2e.

For each j, after shifting a,b,c,d,e,f by 1, the cleared numerator of Phi is a
coefficient-nonnegative polynomial plus nonnegative rational multiples of
shifted feasibility slacks.
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
    v = e

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
            ("s2", (0, 0, 0, 0, 0, 2), sp.Rational(22)),
            ("s2", (0, 0, 1, 0, 0, 0), sp.Rational(2675, 4)),
            ("s2", (0, 0, 1, 0, 0, 1), sp.Rational(1057, 2)),
            ("s2", (0, 1, 0, 0, 0, 1), sp.Rational(477, 2)),
            ("s2", (1, 0, 0, 0, 0, 0), sp.Rational(4415, 8)),
            ("s2", (1, 0, 0, 0, 0, 1), sp.Rational(6581, 16)),
            ("s2", (1, 0, 1, 0, 0, 1), sp.Rational(385, 4)),
            ("s2", (2, 0, 0, 0, 0, 0), sp.Rational(2833, 16)),
            ("s7", (0, 0, 0, 0, 0, 0), sp.Rational(375, 2)),
            ("s7", (0, 0, 1, 0, 0, 0), sp.Rational(525, 4)),
            ("s7", (0, 0, 1, 0, 0, 1), sp.Rational(153, 2)),
            ("s7", (0, 0, 2, 0, 0, 0), sp.Rational(144)),
            ("s7", (0, 1, 1, 0, 0, 0), sp.Rational(7, 2)),
            ("s7", (1, 0, 1, 0, 0, 0), sp.Rational(1745, 2)),
            ("s7", (1, 0, 2, 0, 0, 0), sp.Rational(335, 2)),
            ("s7", (2, 0, 1, 0, 0, 0), sp.Rational(173, 4)),
        ],
        "s5": [
            ("u", (1, 0, 1, 0, 1, 0), sp.Rational(6877, 24)),
            ("s2", (0, 0, 0, 0, 0, 0), sp.Rational(350)),
            ("s2", (0, 0, 0, 0, 0, 1), sp.Rational(270)),
            ("s2", (0, 0, 0, 0, 0, 2), sp.Rational(22)),
            ("s2", (0, 0, 0, 0, 2, 0), sp.Rational(1813, 12)),
            ("s2", (0, 0, 0, 1, 0, 0), sp.Rational(392)),
            ("s2", (0, 0, 1, 0, 0, 1), sp.Rational(663, 2)),
            ("s2", (0, 0, 2, 0, 0, 1), sp.Rational(65, 4)),
            ("s2", (0, 1, 0, 0, 0, 1), sp.Rational(477, 2)),
            ("s2", (1, 0, 0, 0, 0, 0), sp.Rational(190)),
            ("s2", (1, 0, 0, 0, 1, 0), sp.Rational(1226, 3)),
            ("s2", (1, 0, 0, 0, 2, 0), sp.Rational(1993, 6)),
            ("s2", (1, 0, 0, 1, 1, 0), sp.Rational(547, 9)),
            ("s4", (0, 0, 0, 0, 1, 0), sp.Rational(16379, 12)),
            ("s4", (0, 0, 0, 0, 2, 0), sp.Rational(1597, 12)),
            ("s4", (0, 0, 0, 1, 1, 0), sp.Rational(5489, 18)),
            ("s4", (1, 0, 0, 2, 0, 0), sp.Rational(151, 9)),
            ("s4", (1, 0, 1, 0, 1, 0), sp.Rational(131, 8)),
            ("s4", (3, 0, 0, 0, 0, 0), sp.Rational(10)),
            ("s6", (0, 0, 0, 0, 0, 0), sp.Rational(1255)),
            ("s6", (0, 0, 0, 0, 1, 2), sp.Rational(22)),
            ("s6", (0, 1, 0, 0, 1, 0), sp.Rational(329, 6)),
            ("s6", (0, 2, 0, 0, 1, 0), sp.Rational(5)),
            ("s6", (1, 0, 0, 0, 0, 0), sp.Rational(391, 3)),
            ("s6", (1, 0, 0, 0, 1, 1), sp.Rational(88)),
            ("s6", (1, 0, 0, 1, 0, 0), sp.Rational(218, 9)),
            ("s6", (1, 0, 0, 1, 0, 1), sp.Rational(10)),
            ("s6", (1, 0, 1, 0, 0, 0), sp.Rational(3421, 24)),
            ("s6", (1, 0, 1, 0, 1, 0), sp.Rational(3085, 6)),
            ("s6", (1, 1, 0, 0, 1, 0), sp.Rational(16)),
            ("s6", (2, 0, 0, 0, 1, 0), sp.Rational(9)),
            ("s7", (1, 0, 0, 0, 1, 0), sp.Rational(391, 3)),
            ("s7", (2, 0, 0, 0, 1, 0), sp.Rational(94)),
        ],
        "s6": [
            ("u", (0, 0, 0, 0, 1, 0), sp.Rational(5, 2)),
            ("u", (0, 1, 0, 0, 1, 0), sp.Rational(29, 2)),
            ("u", (0, 1, 1, 0, 1, 0), sp.Rational(54)),
            ("u", (0, 2, 0, 0, 1, 0), sp.Rational(22)),
            ("s2", (0, 0, 0, 0, 0, 0), sp.Rational(600)),
            ("s2", (0, 0, 0, 0, 0, 1), sp.Rational(270)),
            ("s2", (0, 0, 0, 0, 0, 2), sp.Rational(22)),
            ("s2", (0, 0, 0, 0, 1, 1), sp.Rational(403)),
            ("s2", (0, 0, 0, 0, 1, 2), sp.Rational(1)),
            ("s2", (0, 0, 0, 0, 2, 0), sp.Rational(473)),
            ("s2", (0, 0, 0, 0, 2, 1), sp.Rational(47, 2)),
            ("s2", (0, 0, 0, 1, 0, 1), sp.Rational(222)),
            ("s2", (0, 0, 0, 1, 1, 0), sp.Rational(344)),
            ("s2", (0, 0, 1, 0, 2, 0), sp.Rational(1257, 4)),
            ("s2", (0, 0, 2, 0, 0, 0), sp.Rational(49)),
            ("s2", (0, 1, 0, 0, 2, 0), sp.Rational(52)),
            ("s2", (1, 0, 0, 0, 0, 0), sp.Rational(190)),
            ("s2", (1, 0, 0, 0, 2, 0), sp.Rational(485, 4)),
            ("s2", (1, 0, 1, 0, 0, 0), sp.Rational(620)),
            ("s2", (1, 0, 2, 0, 0, 0), sp.Rational(184)),
            ("s4", (0, 0, 0, 0, 1, 0), sp.Rational(565, 2)),
            ("s4", (0, 0, 0, 0, 2, 0), sp.Rational(455)),
            ("s4", (0, 0, 1, 0, 2, 0), sp.Rational(1161, 4)),
            ("s4", (0, 0, 2, 0, 1, 0), sp.Rational(5, 4)),
            ("s4", (0, 1, 0, 0, 1, 0), sp.Rational(1035, 2)),
            ("s4", (0, 1, 0, 0, 1, 1), sp.Rational(70)),
            ("s4", (0, 1, 0, 0, 2, 0), sp.Rational(40)),
            ("s4", (0, 1, 1, 0, 1, 0), sp.Rational(317, 4)),
            ("s4", (1, 0, 0, 0, 2, 0), sp.Rational(437, 4)),
            ("s4", (1, 1, 0, 0, 1, 0), sp.Rational(57, 4)),
            ("s5", (0, 0, 0, 0, 0, 0), sp.Rational(360)),
            ("s7", (0, 0, 0, 1, 0, 0), sp.Rational(235)),
            ("s7", (1, 0, 1, 0, 0, 0), sp.Rational(463)),
            ("s7", (2, 0, 1, 0, 0, 0), sp.Rational(15)),
        ],
        "s7": [
            ("s2", (0, 0, 0, 0, 0, 0), sp.Rational(1599, 2)),
            ("s2", (0, 0, 0, 0, 0, 1), sp.Rational(784)),
            ("s2", (0, 0, 0, 0, 0, 2), sp.Rational(22)),
            ("s2", (0, 0, 0, 0, 1, 0), sp.Rational(1751, 2)),
            ("s2", (0, 0, 0, 0, 1, 1), sp.Rational(486)),
            ("s2", (0, 0, 0, 1, 0, 0), sp.Rational(1493, 4)),
            ("s2", (0, 0, 1, 0, 1, 0), sp.Rational(530)),
            ("s2", (0, 1, 0, 0, 1, 0), sp.Rational(289)),
            ("s2", (0, 1, 0, 0, 1, 1), sp.Rational(147)),
            ("s2", (0, 1, 0, 1, 0, 0), sp.Rational(135)),
            ("s2", (1, 0, 0, 0, 0, 0), sp.Rational(415)),
            ("s2", (1, 0, 0, 0, 1, 0), sp.Rational(410)),
            ("s2", (1, 0, 1, 0, 1, 0), sp.Rational(219)),
            ("s2", (1, 1, 0, 0, 1, 0), sp.Rational(12)),
            ("s2", (2, 0, 0, 0, 0, 0), sp.Rational(2)),
            ("s4", (0, 0, 0, 0, 0, 0), sp.Rational(900)),
            ("s4", (0, 0, 0, 0, 1, 0), sp.Rational(1185, 2)),
            ("s4", (0, 0, 0, 1, 0, 0), sp.Rational(135, 4)),
            ("s4", (0, 0, 1, 0, 0, 0), sp.Rational(35, 2)),
            ("s4", (0, 0, 1, 0, 1, 0), sp.Rational(383)),
            ("s4", (0, 1, 0, 0, 0, 0), sp.Rational(515, 4)),
            ("s4", (0, 1, 0, 0, 1, 0), sp.Rational(280)),
            ("s4", (0, 1, 1, 0, 1, 0), sp.Rational(15)),
            ("s4", (0, 2, 0, 0, 1, 0), sp.Rational(31, 2)),
        ],
    }

    shift = {var: var + 1 for var in vars_}

    for cap_name, Mj in caps.items():
        u = Mj - 2 * e
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

    print("PASS y=1,x=1,s1=0 capacity endpoints s4..s7 exact slack certificates")


if __name__ == "__main__":
    main()
