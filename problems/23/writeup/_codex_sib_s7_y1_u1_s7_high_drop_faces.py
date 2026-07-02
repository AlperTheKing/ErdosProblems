"""Exact closure of one-step drop faces from the U1_S7_HIGH support.

The U1_S7_HIGH observed support is on the y=1,u=1,s7 capacity branch:

    a=c=d=e=f=x=v=1,      b>=1,

with active equations

    a1,c1,d1,e1,f1,s1,s2,s6,s7,u1,v1,x1.

This file checks that dropping any one non-branch active equation forces the
same high boundary family again.  That family is already proved positive in
_codex_sib_s7_y1_more_high_boundaries.py.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, x, u, v = sp.symbols("a b c d e f x u v")
    y = sp.Integer(1)
    m = x * u + x * v + y * v
    slacks = {
        "a1": a - 1,
        "c1": c - 1,
        "d1": d - 1,
        "e1": e - 1,
        "f1": f - 1,
        "s1": e - v,
        "s2": d + e - u - v,
        "s6": a * c + d * f + e * f - m,
        "s7": a * e + d * f + e * f - m,
        "u1": u - 1,
        "v1": v - 1,
        "x1": x - 1,
    }
    active = tuple(slacks)
    target = {"a - 1", "c - 1", "d - 1", "e - 1", "f - 1", "u - 1", "v - 1", "x - 1"}

    # u1 is the branch equation in this chart, so the refined face keeps it.
    for missing in (name for name in active if name != "u1"):
        eqs = [expr for name, expr in slacks.items() if name != missing]
        G = sp.groebner(eqs, a, c, d, e, f, u, v, x, b, order="lex")
        basis = {str(poly.as_expr()) for poly in G.polys}
        assert target <= basis, (missing, basis)

    # Record the surviving b-ray and its slack profile.
    subs = {a: 1, c: 1, d: 1, e: 1, f: 1, u: 1, v: 1, x: 1}
    s3 = b + c - x - y
    s4 = a * c + b * f + c * f - m
    s5 = a * e + b * f + c * f - m
    assert sp.factor(s3.subs(subs) - (b - 1)) == 0
    assert sp.factor(s4.subs(subs) - (b - 1)) == 0
    assert sp.factor(s5.subs(subs) - (b - 1)) == 0

    print("PASS y=1 U1_S7_HIGH one-step drop faces force the closed b-ray")


if __name__ == "__main__":
    main()