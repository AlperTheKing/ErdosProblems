"""Exact certificates for y=1,x=1,s2=0,s_j=0, j=4..7.

These are endpoint leaves from the y=1,x=1 capacity v-fiber reduction.  On
x=y=1, s2=0, and capacity face s_j=0, q=d+e and m=M_j determine

    v = d + e - M_j,
    u = 2*M_j - d - e.

For each j, after shifting a,b,c,d,e,f by 1, the cleared numerator of Phi is a
coefficient-nonnegative polynomial plus nonnegative rational multiples of the
shifted feasibility slacks.  For s6 and s7, the shifted numerator is already
coefficientwise nonnegative.
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
            ("u", (0, 0, 0, 0, 0, 0), sp.Rational(759)),
            ("u", (0, 0, 0, 0, 2, 0), sp.Rational(209)),
            ("u", (0, 0, 0, 1, 0, 0), sp.Rational(582)),
            ("u", (0, 0, 0, 1, 0, 1), sp.Rational(630)),
            ("u", (0, 0, 0, 1, 1, 0), sp.Rational(238)),
            ("u", (0, 0, 0, 1, 1, 1), sp.Rational(12)),
            ("u", (0, 0, 1, 1, 0, 0), sp.Rational(322)),
            ("u", (0, 1, 0, 0, 2, 0), sp.Rational(18)),
            ("u", (0, 1, 0, 1, 0, 1), sp.Rational(325)),
            ("u", (0, 2, 0, 1, 0, 0), sp.Rational(27)),
            ("u", (1, 0, 0, 1, 0, 0), sp.Rational(78)),
            ("u", (1, 1, 0, 1, 0, 0), sp.Rational(5)),
            ("v", (0, 0, 0, 0, 3, 0), sp.Rational(11)),
            ("v", (0, 0, 0, 2, 0, 0), sp.Rational(12)),
            ("v", (0, 0, 0, 2, 0, 1), sp.Rational(20)),
            ("v", (0, 0, 0, 2, 1, 0), sp.Rational(42)),
            ("v", (0, 0, 0, 3, 0, 0), sp.Rational(83, 2)),
            ("v", (0, 0, 1, 2, 0, 0), sp.Rational(18)),
            ("v", (0, 1, 0, 2, 0, 0), sp.Rational(10)),
            ("v", (1, 0, 0, 2, 0, 0), sp.Rational(4)),
            ("s1", (0, 0, 0, 2, 1, 0), sp.Rational(151, 2)),
            ("s1", (0, 0, 0, 3, 0, 0), sp.Rational(83, 2)),
            ("s1", (0, 0, 1, 1, 0, 1), sp.Rational(225)),
            ("s1", (0, 1, 0, 1, 0, 0), sp.Rational(378)),
            ("s1", (0, 1, 0, 1, 1, 0), sp.Rational(93, 2)),
            ("s1", (1, 0, 0, 1, 0, 1), sp.Rational(18)),
            ("s5", (0, 0, 0, 3, 0, 0), sp.Rational(4)),
            ("s7", (0, 0, 0, 0, 3, 0), sp.Rational(7, 2)),
            ("s7", (0, 0, 0, 1, 1, 0), sp.Rational(45)),
        ],
        "s5": [
            ("u", (0, 0, 0, 0, 0, 0), sp.Rational(759)),
            ("u", (0, 0, 0, 1, 0, 0), sp.Rational(582)),
            ("u", (0, 0, 0, 1, 0, 1), sp.Rational(630)),
            ("u", (0, 0, 1, 1, 0, 0), sp.Rational(366)),
            ("u", (0, 1, 0, 1, 0, 1), sp.Rational(325)),
            ("u", (0, 2, 0, 1, 0, 0), sp.Rational(27)),
            ("u", (1, 0, 0, 1, 0, 0), sp.Rational(78)),
            ("u", (1, 1, 0, 1, 0, 0), sp.Rational(5)),
            ("v", (0, 0, 0, 1, 2, 0), sp.Rational(51)),
            ("v", (0, 0, 0, 2, 0, 0), sp.Rational(12)),
            ("v", (0, 0, 0, 2, 0, 1), sp.Rational(20)),
            ("v", (0, 0, 0, 2, 1, 0), sp.Rational(12)),
            ("v", (0, 0, 1, 2, 0, 0), sp.Rational(14)),
            ("v", (0, 1, 0, 2, 0, 0), sp.Rational(10)),
            ("v", (1, 0, 0, 2, 0, 0), sp.Rational(4)),
            ("s1", (0, 0, 0, 1, 1, 0), sp.Rational(66)),
            ("s1", (0, 0, 1, 1, 0, 1), sp.Rational(293)),
            ("s1", (0, 0, 2, 1, 0, 0), sp.Rational(5)),
            ("s1", (0, 1, 0, 1, 0, 0), sp.Rational(378)),
            ("s1", (0, 1, 1, 1, 0, 0), sp.Rational(34)),
            ("s1", (1, 0, 0, 1, 0, 1), sp.Rational(18)),
        ],
        "s6": [],
        "s7": [],
    }

    shift = {var: var + 1 for var in vars_}

    for cap_name, Mj in caps.items():
        v = d + e - Mj
        u = 2 * Mj - d - e
        m = Mj
        N = S + x + y + u + v
        Phi = sp.factor(2 * (N * N - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - S))
        P = sp.expand(sp.together(Phi).as_numer_denom()[0].subs(shift))

        shifted_slacks = {
            "u": sp.expand((u - 1).subs(shift)),
            "v": sp.expand((v - 1).subs(shift)),
            "s1": sp.expand((e - v).subs(shift)),
            "s3": sp.expand((b + c - x - y).subs(shift)),
        }
        for other_name, other_M in caps.items():
            if other_name != cap_name:
                shifted_slacks[other_name] = sp.expand((other_M - Mj).subs(shift))

        remainder = P
        for slack_name, exps, coeff in certificates[cap_name]:
            remainder = sp.expand(remainder - coeff * monomial(vars_, exps) * shifted_slacks[slack_name])

        assert coeffs_nonnegative(remainder, vars_), cap_name

    print("PASS y=1,x=1,s2=0 capacity endpoints s4..s7 exact slack certificates")


if __name__ == "__main__":
    main()
