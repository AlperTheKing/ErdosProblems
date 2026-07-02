"""Exact impossibility of two x=q,s2 endpoint capacity faces.

On the y=1, x=q, s2=0 endpoint, we have x=q=d+e.  If s4=0, then

    s6 - s4 = f*(d+e-b-c).

If s5=0, then

    s7 - s5 = f*(d+e-b-c).

But feasibility also requires s3=b+c-x-1>=0, i.e. b+c>=d+e+1.
Therefore d+e-b-c<=-1, so the corresponding remaining capacity slack is
strictly negative.  Thus the s4 and s5 capacity faces are infeasible on
x=q,s2=0.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    a, b, c, d, e, f = sp.symbols("a b c d e f", positive=True)
    x = d + e
    m = x * x + sp.symbols("v", positive=True)
    Y = a * c + b * f + c * f
    s3 = b + c - x - 1
    s4 = Y - m
    s5 = a * e + b * f + c * f - m
    s6 = a * c + d * f + e * f - m
    s7 = a * e + d * f + e * f - m

    assert sp.factor((s6 - s4) - f * (d + e - b - c)) == 0
    assert sp.factor((s7 - s5) - f * (d + e - b - c)) == 0
    assert sp.factor((d + e - b - c) + s3 + 1) == 0

    # Hence s3>=0 and f>=1 imply:
    #   s4=0 => s6 <= -f < 0,
    #   s5=0 => s7 <= -f < 0.
    # Both contradict S7 feasibility.
    print("PASS y=1 x=q,s2 capacity faces s4/s5 are infeasible")


if __name__ == "__main__":
    main()
