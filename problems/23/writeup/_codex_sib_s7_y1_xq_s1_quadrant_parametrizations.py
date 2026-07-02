"""Exact quadrant parametrizations for y=1, x=q, s1=0 capacity faces.

Let r=c-e and h=s3-s2+1.  The pair-structure identities give

    s4-s5 = s6-s7 = a*r,
    s4-s6 = s5-s7 = f*h.

On each active capacity face, feasibility fixes the signs of r and h.  This
script records the resulting explicit nonnegative two-gap coordinates.  It is a
narrowing artifact for the x=q,s1 coverage theorem, not a closure certificate.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, x = sp.symbols("a b c d e f x", positive=True)
    y = sp.Integer(1)
    v = e
    m = x * x + e
    Y = a * c + b * f + c * f

    s2 = d + e - x
    s3 = b + c - x - y
    s4 = Y - m
    s5 = a * e + b * f + c * f - m
    s6 = a * c + d * f + e * f - m
    s7 = a * e + d * f + e * f - m

    r = c - e
    h = s3 - s2 + 1
    assert sp.factor(h - (b + c - d - e)) == 0

    # Universal pair identities.
    assert sp.factor(s4 - s5 - a * r) == 0
    assert sp.factor(s6 - s7 - a * r) == 0
    assert sp.factor(s4 - s6 - f * h) == 0
    assert sp.factor(s5 - s7 - f * h) == 0

    # s4=0: feasibility gives r<=0 and h<=0.  Put R=-r=e-c, H=-h=s2-s3-1.
    R = -r
    H = -h
    assert sp.factor(s5 - (s4 + a * R)) == 0
    assert sp.factor(s6 - (s4 + f * H)) == 0
    assert sp.factor(s7 - (s4 + a * R + f * H)) == 0

    # s5=0: feasibility gives r>=0 and h<=0.  Put R=r=c-e, H=-h.
    R = r
    H = -h
    assert sp.factor(s4 - (s5 + a * R)) == 0
    assert sp.factor(s7 - (s5 + f * H)) == 0
    assert sp.factor(s6 - (s5 + a * R + f * H)) == 0

    # s6=0: feasibility gives r<=0 and h>=0.  Put R=-r, H=h.
    R = -r
    H = h
    assert sp.factor(s7 - (s6 + a * R)) == 0
    assert sp.factor(s4 - (s6 + f * H)) == 0
    assert sp.factor(s5 - (s6 + a * R + f * H)) == 0

    # s7=0: feasibility gives r>=0 and h>=0.  Put R=r, H=h.
    R = r
    H = h
    assert sp.factor(s6 - (s7 + a * R)) == 0
    assert sp.factor(s5 - (s7 + f * H)) == 0
    assert sp.factor(s4 - (s7 + a * R + f * H)) == 0

    print("PASS y=1 x=q,s1 capacity faces have exact two-gap quadrant parametrizations")


if __name__ == "__main__":
    main()