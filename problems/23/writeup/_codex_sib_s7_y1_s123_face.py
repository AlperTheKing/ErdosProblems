"""Exact reduction of the sibling S7 face y=1,s1=s2=s3=0.

This closes the second endpoint-only branch from the Y1-6 reduction, modulo the
four capacity branches s4=0, s5=0, s6=0, s7=0.

On this face,

    v = e, u = d, x = b + c - 1.

The resulting six-variable face has Phi strictly increasing in f.  Thus a
negative point moves down in f until f=1 or a capacity slack tightens.  On f=1,
Phi is strictly increasing in a.  Thus a negative point moves down in a until
a=1 or a capacity slack tightens.  Finally a=f=1 is feasible only at all ones,
where Phi=25.
"""

from __future__ import annotations

import sympy as sp


def coeffs_nonnegative(expr: sp.Expr, vars_: tuple[sp.Symbol, ...]) -> bool:
    return all(coef >= 0 for _mon, coef in sp.Poly(sp.expand(expr), *vars_).terms())


def main() -> None:
    a, b, c, d, e, f = sp.symbols("a b c d e f", positive=True)
    y = sp.Integer(1)
    v = e
    u = d
    x = b + c - 1

    S = a + b + c + d + e + f
    N = S + x + y + u + v
    m = x * u + x * v + y * v

    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = sp.factor(2 * (N * N - 25 * m) - 75 * (x * (u + v) * A / Z + y * v * B / (e * Y) - S))

    assert sp.expand(N - (a + 2 * b + 2 * c + 2 * d + 2 * e + f)) == 0
    assert sp.expand(m - (b * d + b * e + c * d + c * e - d)) == 0

    s4 = sp.factor(Y - m)
    s5 = sp.factor(a * e + b * f + c * f - m)
    s6 = sp.factor(a * c + d * f + e * f - m)
    s7 = sp.factor(a * e + d * f + e * f - m)

    # Phi is strictly increasing in f on the whole collapsed face.
    d_f_num, d_f_den = sp.together(sp.diff(Phi, f)).as_numer_denom()
    assert d_f_den != 0
    A0, B0, C0, D0, E0, F0 = sp.symbols("A0 B0 C0 D0 E0 F0", nonnegative=True)
    shifted_df = sp.expand(d_f_num.subs({
        a: 1 + A0,
        b: 1 + B0,
        c: 1 + C0,
        d: 1 + D0,
        e: 1 + E0,
        f: 1 + F0,
    }))
    assert coeffs_nonnegative(shifted_df, (A0, B0, C0, D0, E0, F0))
    assert shifted_df.subs({A0: 0, B0: 0, C0: 0, D0: 0, E0: 0, F0: 0}) > 0

    # Along f-decrease, only f=1 or capacity slacks can block.
    for sj in [s4, s5]:
        assert sp.diff(sj, f) == b + c
    for sj in [s6, s7]:
        assert sp.diff(sj, f) == d + e

    # On f=1, Phi is strictly increasing in a.
    Phi_f1 = sp.factor(Phi.subs(f, 1))
    d_a_num, d_a_den = sp.together(sp.diff(Phi_f1, a)).as_numer_denom()
    assert d_a_den != 0
    shifted_da = sp.expand(d_a_num.subs({
        a: 1 + A0,
        b: 1 + B0,
        c: 1 + C0,
        d: 1 + D0,
        e: 1 + E0,
    }))
    assert coeffs_nonnegative(shifted_da, (A0, B0, C0, D0, E0))
    assert shifted_da.subs({A0: 0, B0: 0, C0: 0, D0: 0, E0: 0}) > 0

    s4_f1 = sp.factor(s4.subs(f, 1))
    s5_f1 = sp.factor(s5.subs(f, 1))
    s6_f1 = sp.factor(s6.subs(f, 1))
    s7_f1 = sp.factor(s7.subs(f, 1))
    for sj in [s4_f1, s6_f1]:
        assert sp.diff(sj, a) == c
    for sj in [s5_f1, s7_f1]:
        assert sp.diff(sj, a) == e

    # If a=f=1, then s7=-(d+e)(b+c-2), so feasibility forces b=c=1.
    s7_a1f1 = sp.factor(s7.subs({a: 1, f: 1}))
    assert sp.factor(s7_a1f1 + (d + e) * (b + c - 2)) == 0
    # With b=c=1, s6=1-e and s5=2-d-e, so e=d=1.
    assert sp.factor(s6.subs({a: 1, b: 1, c: 1, f: 1})) == 1 - e
    assert sp.factor(s5.subs({a: 1, b: 1, c: 1, e: 1, f: 1})) == 1 - d
    assert sp.factor(Phi.subs({a: 1, b: 1, c: 1, d: 1, e: 1, f: 1})) == 25

    print("PASS y=1,s1=s2=s3=0 reduces to capacity faces s4..s7")


if __name__ == "__main__":
    main()
