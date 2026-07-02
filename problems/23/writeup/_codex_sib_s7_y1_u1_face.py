"""Exact reduction of the sibling S7 face y=1,u=1,s2=s3=0.

This closes the endpoint-only branch from the Y1-6 reduction, modulo the four
capacity branches s4=0, s5=0, s6=0, s7=0.

On this face, feasibility forces

    d = 1, v = e, x = b + c - 1.

The resulting five-variable face has Phi strictly increasing in f.  Therefore a
negative point can be moved downward in f until either f=1 or a capacity slack
tightens.  On f=1, Phi is strictly increasing in a, so a negative point can be
moved downward in a until either a=1 or a capacity slack tightens.  Finally,
a=f=1 is feasible only at all ones, where Phi=25.

Thus any negative point on y=1,u=1,s2=s3=0 lies on one of s4=0,...,s7=0.
"""

from __future__ import annotations

import sympy as sp


def coeffs_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef >= 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


def main() -> None:
    a, b, c, e, f = sp.symbols("a b c e f", positive=True)
    y = sp.Integer(1)
    d = sp.Integer(1)
    u = sp.Integer(1)
    v = e
    x = b + c - 1

    S = a + b + c + d + e + f
    N = S + x + y + u + v
    m = x * u + x * v + y * v

    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = sp.factor(2 * (N * N - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - S))

    # These are the collapsed face formulas after y=1,u=1,s2=s3=0.
    assert sp.expand(N - (a + 2 * b + 2 * c + 2 * e + f + 2)) == 0
    assert sp.expand(m - (b * e + b + c * e + c - 1)) == 0

    s4 = sp.factor(Y - m)
    s5 = sp.factor(a * e + b * f + c * f - m)
    s6 = sp.factor(a * c + d * f + e * f - m)
    s7 = sp.factor(a * e + d * f + e * f - m)
    assert s4 == a * c - b * e + b * f - b - c * e + c * f - c + 1
    assert s5 == a * e - b * e + b * f - b - c * e + c * f - c + 1
    assert s6 == a * c - b * e - b - c * e - c + e * f + f + 1
    assert s7 == a * e - b * e - b - c * e - c + e * f + f + 1

    # Phi is strictly increasing in f on the whole collapsed face.
    d_f_num, d_f_den = sp.together(sp.diff(Phi, f)).as_numer_denom()
    assert d_f_den != 0
    A0, B0, C0, E0, F0 = sp.symbols("A0 B0 C0 E0 F0", nonnegative=True)
    shifted_df = sp.expand(d_f_num.subs({
        a: 1 + A0,
        b: 1 + B0,
        c: 1 + C0,
        e: 1 + E0,
        f: 1 + F0,
    }))
    assert coeffs_nonnegative(shifted_df, (A0, B0, C0, E0, F0))
    assert shifted_df.subs({A0: 0, B0: 0, C0: 0, E0: 0, F0: 0}) > 0

    # Along f-decrease, only f=1 or one of the capacity slacks can block.
    for sj in [s4, s5]:
        assert sp.diff(sj, f) == b + c
    for sj in [s6, s7]:
        assert sp.diff(sj, f) == e + 1

    # On f=1, Phi is strictly increasing in a.
    Phi_f1 = sp.factor(Phi.subs(f, 1))
    d_a_num, d_a_den = sp.together(sp.diff(Phi_f1, a)).as_numer_denom()
    assert d_a_den != 0
    shifted_da = sp.expand(d_a_num.subs({
        a: 1 + A0,
        b: 1 + B0,
        c: 1 + C0,
        e: 1 + E0,
    }))
    assert coeffs_nonnegative(shifted_da, (A0, B0, C0, E0))
    assert shifted_da.subs({A0: 0, B0: 0, C0: 0, E0: 0}) > 0

    s4_f1 = sp.factor(s4.subs(f, 1))
    s5_f1 = sp.factor(s5.subs(f, 1))
    s6_f1 = sp.factor(s6.subs(f, 1))
    s7_f1 = sp.factor(s7.subs(f, 1))
    for sj in [s4_f1, s6_f1]:
        assert sp.diff(sj, a) == c
    for sj in [s5_f1, s7_f1]:
        assert sp.diff(sj, a) == e

    # If a=f=1, then feasibility already forces b=c=e=1:
    # s4 = c + 1 - e*(b+c) <= c + 1 - (b+c) = 1-b <= 0.
    s4_a1f1 = sp.factor(s4.subs({a: 1, f: 1}))
    assert sp.factor(s4_a1f1 - (c + 1 - e * (b + c))) == 0
    # Hence s4>=0 with b,c,e>=1 requires b=1 and e=1. Then s5=1-c.
    assert sp.factor(s5.subs({a: 1, f: 1, b: 1, e: 1})) == 1 - c
    assert sp.factor(Phi.subs({a: 1, b: 1, c: 1, e: 1, f: 1})) == 25

    print("PASS y=1,u=1,s2=s3=0 reduces to capacity faces s4..s7")


if __name__ == "__main__":
    main()
