"""Active-face normal forms for the hard y=1, s3=0 SIB-S7 charts.

This is a bookkeeping certificate for the remaining coverage theorem.  It
turns the two hard capacity faces into explicit gap parametrizations.

On s3=0, put R0=c-e and H=b+c-d-e.  The pair structure gives opposite
half-faces:

* s7=0: feasibility forces R0>=0, and the remaining capacity slacks are
  s6=a*R0, s5=f*H, s4=a*R0+f*H.

* s6=0: feasibility forces R1=e-c>=0, and the remaining capacity slacks are
  s7=a*R1, s4=f*H, s5=a*R1+f*H, where now H=b+c-d-e.

Thus both hard charts reduce to two nonnegative ridge gaps plus the two
ordinary endpoint slacks.  The s7 half is the one where direct c-e descent
survived exact rational stress; the s6 half needs a different descent.
"""

from __future__ import annotations

import sympy as sp

import _codex_sib_s7_y1_fj_support_inventory as inv


def main() -> None:
    a, b, c, d, e, f, x, u, v = inv.VARS
    R = sp.symbols("R")

    # Common y=1, s3=0 substitution.
    subs_s3 = {x: b + c - 1}
    s4 = inv.SLACKS["s4"].subs(subs_s3)
    s5 = inv.SLACKS["s5"].subs(subs_s3)
    s6 = inv.SLACKS["s6"].subs(subs_s3)
    s7 = inv.SLACKS["s7"].subs(subs_s3)
    H = b + c - d - e

    # s7=0 half-face: c=e+R and m=ae+df+ef.
    subs_s7 = {
        c: e + R,
        u: (a * e + d * f + e * f - v * (b + e + R)) / (b + e + R - 1),
    }
    H7 = sp.factor(H.subs(subs_s7))
    assert sp.factor(s7.subs(subs_s7)) == 0
    assert sp.factor(s6.subs(subs_s7) - a * R) == 0
    assert sp.factor(s5.subs(subs_s7) - f * H7) == 0
    assert sp.factor(s4.subs(subs_s7) - (a * R + f * H7)) == 0

    # s6=0 half-face: e=c+R and m=ac+df+ef.
    subs_s6 = {
        e: c + R,
        u: (a * c + d * f + (c + R) * f - v * (b + c)) / (b + c - 1),
    }
    H6 = sp.factor(H.subs(subs_s6))
    assert sp.factor(s6.subs(subs_s6)) == 0
    assert sp.factor(s7.subs(subs_s6) - a * R) == 0
    assert sp.factor(s4.subs(subs_s6) - f * H6) == 0
    assert sp.factor(s5.subs(subs_s6) - (a * R + f * H6)) == 0

    print("S3-ACTIVE s7=0: c=e+R, s6=aR, s5=fH, s4=aR+fH")
    print("S3-ACTIVE s6=0: e=c+R, s7=aR, s4=fH, s5=aR+fH")
    print("PASS y=1 s3 active capacity faces have exact two-gap normal forms")


if __name__ == "__main__":
    main()
