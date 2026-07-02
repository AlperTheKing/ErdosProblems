"""Strict v-monotonicity on the y=1, x=q, s2 endpoint blocker.

On the endpoint branch y=1, x=q and s2=0, the core variables
``a,b,c,d,e,f`` determine

    x=q=d+e,        u=x-v,        m=x^2+v.

For fixed core variables, the S7 expression Phi is affine and strictly
decreasing in v:

    dPhi/dv = -50 - 75 B/(eY) < 0.

Therefore, for fixed core variables, a local minimum on this endpoint occurs
on the upper envelope of the feasible v-interval.  The s4 and s5 capacity
faces are infeasible on s2 by the existing script.  For the remaining
capacities, the pair-structure identities show:

  * on s6=0 with e>c, all other capacity slacks s4,s5,s7 are strict;
  * on s7=0 with c>e, all other capacity slacks s4,s5,s6 are strict;
  * the ridge c=e is the shared s6/s7 capacity ridge.

This does not close the s6/s7 half-faces by itself: the active capacity is
itself an upper-envelope blocker.  The remaining task is to rule out local
minima on those two open capacity half-faces, or flow them to u=1, s1=0, or
the c=e ridge.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f, v = sp.symbols("a b c d e f v", positive=True)
    y = sp.Integer(1)
    x = q = d + e
    S = a + b + c + d + e + f
    m = x * x + v
    N = S + y + x + q
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    Phi = 2 * (N * N - 25 * m) - 75 * (x * q * A / Z + v * B / (e * Y) - S)

    dphi = sp.factor(sp.diff(Phi, v))
    assert sp.factor(dphi + 50 + 75 * B / (e * Y)) == 0

    s3 = b + c - x - y
    M4 = Y
    M5 = a * e + b * f + c * f
    M6 = a * c + d * f + e * f
    M7 = a * e + d * f + e * f

    # Capacity slacks on s6=0, i.e. v=M6-x^2.
    s4_on_s6 = M4 - M6
    s5_on_s6 = M5 - M6
    s7_on_s6 = M7 - M6
    assert sp.factor(s4_on_s6 - f * (s3 + 1)) == 0
    assert sp.factor(s5_on_s6 - (a * (e - c) + f * (s3 + 1))) == 0
    assert sp.factor(s7_on_s6 - a * (e - c)) == 0

    # Capacity slacks on s7=0, i.e. v=M7-x^2.
    s5_on_s7 = M5 - M7
    s4_on_s7 = M4 - M7
    s6_on_s7 = M6 - M7
    assert sp.factor(s5_on_s7 - f * (s3 + 1)) == 0
    assert sp.factor(s4_on_s7 - (a * (c - e) + f * (s3 + 1))) == 0
    assert sp.factor(s6_on_s7 - a * (c - e)) == 0

    # Feasible interval blockers for increasing v at fixed core.
    u_minus_1 = x - v - 1
    s1 = e - v
    assert sp.diff(u_minus_1, v) == -1
    assert sp.diff(s1, v) == -1

    print("PASS y=1 x=q,s2 endpoint has strict v-monotonicity and s6/s7 upper-envelope structure")


if __name__ == "__main__":
    main()
