"""Exact closure of easy one-step drop faces from XQ_A.

XQ_A is the observed 2-dimensional family on the x=q,u=1 chart with

    f=1, s3=s4=s5=s6=s7=0.

This file closes only the easy capacity-drop neighbors drop:s5, drop:s6, and
drop:s7.  In each case the remaining equations imply the XQ_A family again:

    f=1,
    e=c,
    b=d=x+1-c,
    a=(x^2-2)/c.

The hard XQ_A neighbors drop:f1 and drop:s3 are intentionally left open.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, x = sp.symbols("a b c d e f x")
    m = x * x + x - 1
    Y = a * c + b * f + c * f
    sl = {
        "f1": f - 1,
        "s3": b + c - x - 1,
        "s4": Y - m,
        "s5": a * e + b * f + c * f - m,
        "s6": a * c + d * f + e * f - m,
        "s7": a * e + d * f + e * f - m,
    }
    active = ("f1", "s3", "s4", "s5", "s6", "s7")
    for missing in ("s5", "s6", "s7"):
        eqs = [sl[name] for name in active if name != missing]
        G = sp.groebner(eqs, a, b, c, d, e, f, x, order="lex")
        basis = {sp.factor(poly.as_expr()) for poly in G.polys}
        assert sp.factor(a * c - x**2 + 2) in basis, missing
        assert sp.factor(a * e - x**2 + 2) in basis, missing
        assert sp.factor(b + c - x - 1) in basis, missing
        assert sp.factor(d + e - x - 1) in basis, missing
        assert sp.factor(f - 1) in basis, missing
        assert sp.factor((c - e) * (x**2 - 2)) in basis, missing
        # In the x=q chart, v=x-1>=1, hence x>=2 and x^2-2>0, so c=e.
        # Then b=d=x+1-c and a=(x^2-2)/c, exactly XQ_A.
    print("PASS y=1 XQ_A easy capacity-drop faces s5/s6/s7 reduce to XQ_A")


if __name__ == "__main__":
    main()
