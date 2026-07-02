"""Exact structure of the y=1, x=q, s2 endpoint capacity pair.

This is a bridge artifact for the remaining x=q endpoint coverage theorem.
It does not close the endpoint by itself.  It records the exact algebraic
reason that the two feasible s2 endpoint capacity faces s6=0 and s7=0 sit on
opposite sides of the same ridge c=e.

On y=1, x=q and s2=0, we have x=q=d+e.  The s4 and s5 capacity faces are
already ruled out by _codex_sib_s7_y1_xq_s2_impossible_caps.py.  For the two
remaining faces:

  * if s6=0, then s7 = a(e-c), so feasibility forces e>=c;
  * if s7=0, then s6 = a(c-e), so feasibility forces c>=e.

The common ridge c=e is exactly where the observed XQ_B family lives after the
additional boundary equations d=f=1 and s1=s3=0.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f = sp.symbols("a b c d e f", positive=True)
    y = sp.Integer(1)
    x = q = d + e
    s3 = b + c - x - y

    Y = a * c + b * f + c * f
    M6 = a * c + d * f + e * f
    M7 = a * e + d * f + e * f

    # s6=0 face: m=M6.
    s4_on_s6 = Y - M6
    s5_on_s6 = a * e + b * f + c * f - M6
    s7_on_s6 = M7 - M6
    assert sp.factor(s4_on_s6 - f * (s3 + 1)) == 0
    assert sp.factor(s5_on_s6 - (a * (e - c) + f * (s3 + 1))) == 0
    assert sp.factor(s7_on_s6 - a * (e - c)) == 0

    # s7=0 face: m=M7.
    s5_on_s7 = a * e + b * f + c * f - M7
    s4_on_s7 = Y - M7
    s6_on_s7 = M6 - M7
    assert sp.factor(s5_on_s7 - f * (s3 + 1)) == 0
    assert sp.factor(s4_on_s7 - (a * (c - e) + f * (s3 + 1))) == 0
    assert sp.factor(s6_on_s7 - a * (c - e)) == 0

    # On the ridge c=e, the two faces coincide and the remaining capacity
    # slacks s4,s5 reduce to the same positive boundary term f*(s3+1).
    ridge = {e: c}
    assert sp.factor(s7_on_s6.subs(ridge)) == 0
    assert sp.factor(s6_on_s7.subs(ridge)) == 0
    assert sp.factor(s4_on_s6.subs(ridge) - s5_on_s6.subs(ridge)) == 0
    assert sp.factor(s4_on_s7.subs(ridge) - s5_on_s7.subs(ridge)) == 0

    print("PASS y=1 x=q,s2 endpoint has s6/s7 capacity faces separated by c=e")


if __name__ == "__main__":
    main()
