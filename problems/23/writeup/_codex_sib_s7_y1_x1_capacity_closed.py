"""Exact closure of y=1,x=1 SIB S7 capacity faces.

This removes the remaining interior critical leaf from the x=1 v-fiber split.
On y=x=1 and a capacity face s_j=0, write M_j for the active capacity RHS:

    m = u + 2v = M_j,      u = M_j - 2v.

For fixed core variables a..f, Phi is a convex quadratic in v with

    d^2 Phi / dv^2 = 4.

The feasible interval in v has upper endpoint determined by either u=1 or
s1=0 (v=e).  This script proves exactly that dPhi/dv is still strictly
negative at both possible upper endpoints, by checking that

    e*Y*Z*(-dPhi/dv)

has a coefficientwise nonnegative shift by a..f >= 1 and positive constant
term.  Since dPhi/dv is increasing in v, Phi is decreasing on every feasible
v-fiber.  Hence the minimum occurs at u=1 or s1=0, which are closed by
_codex_sib_s7_y1_x1_u1_capacity.py and
_codex_sib_s7_y1_x1_s1_capacity.py.
"""

from __future__ import annotations

import sympy as sp


def coeffs_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef >= 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


def main() -> None:
    a, b, c, d, e, f, v = sp.symbols("a b c d e f v", positive=True)
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

    shift = {var: var + 1 for var in vars_}

    for cap_name, Mj in caps.items():
        u = Mj - 2 * v
        m = x * u + x * v + y * v
        N = S + x + y + u + v
        Phi = sp.factor(2 * (N * N - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - S))

        assert sp.factor(m - Mj) == 0, cap_name
        assert sp.factor(sp.diff(Phi, v, 2) - 4) == 0, cap_name
        expected_derivative = -4 * N + 75 * (A / Z - B / (e * Y))
        assert sp.factor(sp.diff(Phi, v) - expected_derivative) == 0, cap_name

        for endpoint_name, endpoint_v in {
            "u1": sp.Rational(1, 2) * (Mj - 1),
            "s1": e,
        }.items():
            neg_der_num = sp.together((-sp.diff(Phi, v)).subs(v, endpoint_v) * e * Y * Z).as_numer_denom()[0]
            shifted = sp.expand(neg_der_num.subs(shift))
            assert coeffs_nonnegative(shifted, vars_), (cap_name, endpoint_name)
            constant = sp.Poly(shifted, *vars_).coeff_monomial((0, 0, 0, 0, 0, 0))
            assert constant > 0, (cap_name, endpoint_name, constant)

    print("PASS y=1,x=1 capacity faces: dPhi/dv<0, so only u=1/s1 endpoints remain")


if __name__ == "__main__":
    main()
