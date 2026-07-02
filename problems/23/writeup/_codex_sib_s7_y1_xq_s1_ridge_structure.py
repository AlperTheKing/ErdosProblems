"""Exact ridge identities for the y=1, x=q, s1=0, c=e face.

This is another narrowing artifact for the x=q endpoint coverage theorem.
The pair-structure gate shows that every active capacity face fixes the signs
of c-e and s2-s3-1.  On the first ridge c=e, the remaining split is b versus d:

    s4 = s5,
    s6 = s7,
    s6 - s4 = f(d-b).

Thus an active s4/s5 face forces d>=b, an active s6/s7 face forces b>=d,
and the common ridge b=d makes all four capacity slacks equal.  This is the
exact algebraic target for reducing the x=q,s1 quadrants to lower-dimensional
closed faces.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, d, e, f, x = sp.symbols("a b d e f x", positive=True)
    y = sp.Integer(1)
    c = e
    v = e

    # x=q on the y=1 endpoint means u+v=x, so m=x^2+e.
    m = x * x + e
    Y = a * c + b * f + c * f

    s2 = d + e - x
    s3 = b + c - x - y
    s4 = Y - m
    s5 = a * e + b * f + c * f - m
    s6 = a * c + d * f + e * f - m
    s7 = a * e + d * f + e * f - m

    assert sp.factor(s4 - s5) == 0
    assert sp.factor(s6 - s7) == 0
    assert sp.factor(s6 - s4 - f * (d - b)) == 0
    assert sp.factor(s7 - s5 - f * (d - b)) == 0
    assert sp.factor(s4 - s6 - f * (b - d)) == 0

    # The second paired sign variable collapses to b-d on c=e.
    assert sp.factor((s3 - s2 + 1) - (b - d)) == 0

    # On the subridge b=d all four capacity slacks are the same.
    common = sp.factor(s4.subs(d, b))
    assert sp.factor(s5.subs(d, b) - common) == 0
    assert sp.factor(s6.subs(d, b) - common) == 0
    assert sp.factor(s7.subs(d, b) - common) == 0

    # Feasible active-face sign consequences as exact identities.
    # If s4=0 or s5=0, then s6=s7=f(d-b), so feasibility forces d>=b.
    assert sp.factor(s6 - s4 - f * (d - b)) == 0
    assert sp.factor(s7 - s5 - f * (d - b)) == 0
    # If s6=0 or s7=0, then s4=s5=f(b-d), so feasibility forces b>=d.
    assert sp.factor(s4 - s6 - f * (b - d)) == 0
    assert sp.factor(s5 - s7 - f * (b - d)) == 0

    print("PASS y=1 x=q,s1,c=e ridge has exact b/d paired capacity structure")


if __name__ == "__main__":
    main()
