"""Exact closure of easy one-step drops from XQ_S5_HIGH.

XQ_S5_HIGH is the observed x=q, y=1, s5-capacity support

    a=1, s1=s3=s4=s5=s6=s7=0, u=1,

which reduces to

    b=d=2, c=e=v=x-1, f=x^2/(x+1), x>=2.

This file closes the easy drop faces s4, s6, and s7.  In each case the
remaining equations have a Groebner basis containing f*(d-2) and x^2*(d-2).
Since f>0 and x>0 on the positive domain, d=2, and the remaining basis then
forces the closed XQ_S5_HIGH family.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, x, u, v = sp.symbols("a b c d e f x u v")
    y = sp.Integer(1)
    m = x * u + x * v + y * v
    Y = a * c + b * f + c * f
    slacks = {
        "a1": a - 1,
        "s1": e - v,
        "s3": b + c - x - y,
        "s4": Y - m,
        "s5": a * e + b * f + c * f - m,
        "s6": a * c + d * f + e * f - m,
        "s7": a * e + d * f + e * f - m,
        "u1": u - 1,
        "xq": x - u - v,
    }
    active = ("a1", "s1", "s3", "s4", "s5", "s6", "s7", "u1", "xq")
    forced = {
        "a - 1",
        "b - 2",
        "c - x + 1",
        "d - 2",
        "e - x + 1",
        "u - 1",
        "v - x + 1",
        "f*x + f - x**2",
    }

    for missing in ("s4", "s6", "s7"):
        eqs = [slacks[name] for name in active if name != missing]
        G = sp.groebner(eqs, a, b, c, d, e, f, u, v, x, order="lex")
        basis = {sp.factor(poly.as_expr()) for poly in G.polys}
        assert sp.factor(f * (d - 2)) in basis, missing
        assert sp.factor(x**2 * (d - 2)) in basis, missing

        # Add d=2, justified by f>0 and x>0, and verify the closed family basis.
        G2 = sp.groebner([*eqs, d - 2], a, b, c, d, e, f, u, v, x, order="lex")
        basis2 = {str(poly.as_expr()) for poly in G2.polys}
        assert forced <= basis2, (missing, basis2)

    print("PASS y=1 XQ_S5_HIGH easy drops s4/s6/s7 force the closed family")


if __name__ == "__main__":
    main()