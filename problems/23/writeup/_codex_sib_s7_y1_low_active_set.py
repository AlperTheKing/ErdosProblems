"""Exact check for the low active set found in y=1 S7 capacity scans.

This is not a full y=1 capacity proof. It records the algebraic content of
the only low FJ basin found by the numerical active-set scans:

    y = 1, u = 1, b = d = f = 1,
    s1 = s2 = s3 = s4 = s5 = s6 = s7 = 0.

The equations reduce exactly to the central seven-tight curve

    c = e = v = x = t,
    a = t + 1 - 1/t,       t >= 1,

whose positivity is already checked in _codex_sib_s7_gate.py and
_codex_sib_s7_seventight_y1.py by Sturm/Bernstein.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, c, e, x, v, t = sp.symbols("a c e x v t", positive=True)
    b = d = f = u = y = sp.Integer(1)

    m = x * u + x * v + y * v
    Y = a * c + b * f + c * f
    s1 = e - v
    s2 = d + e - u - v
    s3 = b + c - x - y
    s4 = Y - m
    s5 = a * e + b * f + c * f - m
    s6 = a * c + d * f + e * f - m
    s7 = a * e + d * f + e * f - m

    reduced = [sp.factor(expr.subs({e: v, x: c})) for expr in [s1, s2, s3, s4, s5, s6, s7]]
    assert reduced[:3] == [0, 0, 0]
    assert sp.factor(reduced[5] - reduced[3] - (v - c)) == 0
    assert sp.factor(reduced[6] - reduced[4] - (v - c)) == 0
    assert sp.factor(reduced[4] - reduced[3] - a * (v - c)) == 0
    assert sp.factor(reduced[6] - reduced[3] - (a + 1) * (v - c)) == 0

    reduced_vc = [sp.factor(expr.subs({e: c, v: c, x: c})) for expr in [s4, s5, s6, s7]]
    assert all(expr == reduced_vc[0] for expr in reduced_vc)
    assert sp.factor(reduced_vc[0] - (a * c - c * c - c + 1)) == 0

    subs = {
        c: t,
        e: t,
        v: t,
        x: t,
        a: t + 1 - 1 / t,
    }
    for name, expr in {
        "s1": s1,
        "s2": s2,
        "s3": s3,
        "s4": s4,
        "s5": s5,
        "s6": s6,
        "s7": s7,
    }.items():
        assert sp.factor(expr.subs(subs)) == 0, name

    central_a = ((1 + t) ** 2 - 1 - (1 + t)) / t
    assert sp.factor(central_a - (t + 1 - 1 / t)) == 0

    print("PASS y=1 low active set reduces to central seven-tight curve")


if __name__ == "__main__":
    main()
