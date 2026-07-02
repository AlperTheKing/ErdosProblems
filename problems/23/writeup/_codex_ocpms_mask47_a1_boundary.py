"""Exact shifted-coefficient probe for the hard mask-47 boundary a=w0=1.

Mask 47 active constraints:
  w5=w9, w6=w7, linL, linR, D0=m.

Use variables:
  p=w5=w9, q=w6=w7, x=w1, y=w2, r=w8, a=w0.

Then w3=y, w4=x and D0=m solves
  a=(x*p+y*q+q*p-r*(y+p))/p.

The closest unresolved integer ray is
  (a,x,y,w3,w4,p,q,w7,r,w9) = (1,1,2,2,1,t-1,t,t,t,t-1).

So test the a=1 boundary directly:
  q=p+s, x=1+h, y=x+d, s,d,h>=0,
  r=(x*p+y*q+q*p-p)/(y+p).

The script reports whether the exact PMS margin numerator has only
nonnegative shifted coefficients after clearing denominators.
"""

import sympy as sp

from _codex_ocpms_mask47_subcase_lt import pms_numerator_for_mask47


def main() -> None:
    p, s, h, d = sp.symbols("p s h d", positive=True)
    P, S, H, D = sp.symbols("P S H D", nonnegative=True)

    q = p + s
    x = 1 + h
    y = x + d
    r = sp.factor((x * p + y * q + q * p - p) / (y + p))

    num, den = pms_numerator_for_mask47(p, s, x, y, r)
    num, den = sp.together(num / den).as_numer_denom()
    shifted = sp.Poly(
        sp.expand(num.subs({p: P + 1, s: S, h: H, d: D})),
        P,
        S,
        H,
        D,
    )
    neg = [(monom, c) for monom, c in shifted.terms() if c < 0]
    print("r", r)
    print("den", sp.factor(den))
    print(
        "terms",
        len(shifted.terms()),
        "negative",
        len(neg),
        "min_coeff",
        min(c for _, c in shifted.terms()),
    )
    if neg:
        print("first_negative", neg[0])
        raise SystemExit(1)
    print("VERDICT PASS")


if __name__ == "__main__":
    main()
