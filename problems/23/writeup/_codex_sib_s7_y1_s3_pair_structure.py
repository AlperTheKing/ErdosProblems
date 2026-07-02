"""Pair structure on the hard y=1, s3=0 SIB-S7 capacity charts.

This is a structural bookkeeping artifact for the remaining y=1 coverage theorem.
On the s3 branch, the capacity differences factor into two signed gaps:

    R = c - e,
    H = b + c - d - e.

In particular, s6=0 forces e>=c from s7>=0, while s7=0 forces c>=e
from s6>=0.  This mirrors the useful x=q pair-structure gates and boxes the
hard s3/s6 and s3/s7 charts into opposite c-vs-e half-faces.
"""

from __future__ import annotations

import sympy as sp

import _codex_sib_s7_y1_fj_support_inventory as inv


def main() -> None:
    a, b, c, d, e, f, x, u, v = inv.VARS
    subs_s3 = {x: b + c - 1}
    R = c - e
    H = b + c - d - e

    s4 = inv.SLACKS["s4"].subs(subs_s3)
    s5 = inv.SLACKS["s5"].subs(subs_s3)
    s6 = inv.SLACKS["s6"].subs(subs_s3)
    s7 = inv.SLACKS["s7"].subs(subs_s3)

    assert sp.factor(s4 - s5 - a * R) == 0
    assert sp.factor(s6 - s7 - a * R) == 0
    assert sp.factor(s4 - s6 - f * H) == 0
    assert sp.factor(s5 - s7 - f * H) == 0
    assert sp.factor(s4 - s7 - (a * R + f * H)) == 0
    assert sp.factor(s5 - s6 - (-a * R + f * H)) == 0

    # Capacity-active sign consequences, written as identities suitable for
    # proof text: s7 = s6-aR and s6 = s7+aR.  Thus s6=0 implies
    # s7=-aR, so feasibility forces R<=0; s7=0 implies s6=aR,
    # so feasibility forces R>=0.
    assert sp.factor(s7 - (s6 - a * R)) == 0
    assert sp.factor(s6 - (s7 + a * R)) == 0

    print("S3-PAIR s4-s5 = s6-s7 = a*(c-e)")
    print("S3-PAIR s4-s6 = s5-s7 = f*(b+c-d-e)")
    print("S3-PAIR s4-s7 = a*(c-e)+f*(b+c-d-e)")
    print("S3-PAIR s5-s6 = -a*(c-e)+f*(b+c-d-e)")
    print("PASS y=1 s3 branch capacity pair structure is exact")


if __name__ == "__main__":
    main()

