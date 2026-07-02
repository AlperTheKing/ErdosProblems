"""Split-coordinate normal form for the hard y=1, s3=0, s7=0 face.

On the s3,s7 half-face, the active-face normal form has two nonnegative
capacity gaps

    R = c-e >= 0,
    H = b+c-d-e >= 0.

The lower bound b>=1 is awkward for coefficient certificates if one uses
(d,R,H) directly.  This file records a nonnegative split parametrization of
that constraint:

    d = 1 + D1 + D2,
    b = 1 + D1 + P,
    R = D2 + Q,
    c = e + R.

Then H = P+Q and d-1 = D1+D2 <= (b-1)+R with equality.  Conversely, any
nonnegative tuple (b-1,R,d-1,H) with H=b+R-d can be represented by choosing a
split of d-1 between b-1 and R.  Thus a coefficient certificate in these split
variables proves the original s3,s7 half-face after choosing such a split.

This is a target-preparation artifact, not a positivity proof.
"""

from __future__ import annotations

import sympy as sp

import _codex_sib_s7_y1_fj_support_inventory as inv


def main() -> None:
    a, _b, _c, _d, e, f, x, u, v = inv.VARS
    D1, D2, P, Q = sp.symbols("D1 D2 P Q", nonnegative=True)

    d = 1 + D1 + D2
    b = 1 + D1 + P
    R = D2 + Q
    c = e + R
    H = b + c - d - e
    m_active = a * e + d * f + e * f
    x_expr = b + c - 1
    u_expr = (m_active - v * (x_expr + 1)) / x_expr

    subs = {
        _b: b,
        _c: c,
        _d: d,
        x: x_expr,
        u: u_expr,
    }

    s3 = sp.factor(inv.SLACKS["s3"].subs(subs))
    s4 = sp.factor(inv.SLACKS["s4"].subs(subs))
    s5 = sp.factor(inv.SLACKS["s5"].subs(subs))
    s6 = sp.factor(inv.SLACKS["s6"].subs(subs))
    s7 = sp.factor(inv.SLACKS["s7"].subs(subs))

    assert s3 == 0
    assert s7 == 0
    assert sp.factor(H - (P + Q)) == 0
    assert sp.factor(R - (D2 + Q)) == 0
    assert sp.factor((d - 1) - (D1 + D2)) == 0
    assert sp.factor((b - 1) - (D1 + P)) == 0
    assert sp.factor((b - 1) + R - (d - 1) - H) == 0

    assert sp.factor(s6 - a * R) == 0
    assert sp.factor(s5 - f * H) == 0
    assert sp.factor(s4 - (a * R + f * H)) == 0

    print("S3S7-SPLIT d=1+D1+D2, b=1+D1+P, R=D2+Q, H=P+Q")
    print("S3S7-SPLIT s6=aR, s5=fH, s4=aR+fH, s7=0")
    print("PASS y=1 s3,s7 split-coordinate normal form is exact")


if __name__ == "__main__":
    main()
