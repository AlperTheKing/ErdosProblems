"""Exact pair-structure identities for the y=1, x=q, s1 endpoint.

This is a narrowing artifact for the x=q endpoint coverage theorem, not a
positivity closure.  On y=1 and x=q, the endpoint s1=0 means e=v.  The four
capacity slacks then split into two paired differences:

    s4 - s5 = s6 - s7 = a(c-e),
    s4 - s6 = s5 - s7 = f(s3 - s2 + 1).

Consequently the active capacity face determines two signs in any feasible
minimum:

    s4=0 or s6=0  => c <= e,
    s5=0 or s7=0  => c >= e,
    s4=0 or s5=0  => s2 >= s3 + 1,
    s6=0 or s7=0  => s2 <= s3 + 1.

The observed x=q,s1 survivor families all live on the ridges exposed by these
paired signs.  The remaining coverage task is to prove descent to those ridges
or exclude the open half-faces.
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

    assert sp.factor(s4 - s5 - a * (c - e)) == 0
    assert sp.factor(s6 - s7 - a * (c - e)) == 0
    assert sp.factor(s4 - s6 - f * (s3 - s2 + 1)) == 0
    assert sp.factor(s5 - s7 - f * (s3 - s2 + 1)) == 0

    # Feasible sign consequences, encoded as exact identities modulo the active
    # capacity equation.  Example: on s4=0, s5=-a(c-e) and
    # s6=-f(s3-s2+1), so feasibility gives c<=e and s2>=s3+1.
    assert sp.factor(s5 + a * (c - e) - s4) == 0
    assert sp.factor(s6 + f * (s3 - s2 + 1) - s4) == 0
    assert sp.factor(s4 - a * (c - e) - s5) == 0
    assert sp.factor(s7 + f * (s3 - s2 + 1) - s5) == 0
    assert sp.factor(s7 + a * (c - e) - s6) == 0
    assert sp.factor(s4 - f * (s3 - s2 + 1) - s6) == 0
    assert sp.factor(s6 - a * (c - e) - s7) == 0
    assert sp.factor(s5 - f * (s3 - s2 + 1) - s7) == 0

    print("PASS y=1 x=q,s1 endpoint has exact paired capacity-sign structure")


if __name__ == "__main__":
    main()

