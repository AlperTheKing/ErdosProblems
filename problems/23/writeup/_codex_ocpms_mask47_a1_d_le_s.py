"""Coefficient-positive certificate for mask-47, a=1, d<=s.

Mask 47 active constraints:
  w5=w9, w6=w7, linL, linR, D0=m.

Boundary:
  a=w0=1.

Parametrization:
  q=p+s,
  x=1+h,
  y=x+d,
  s=d+e, with d,e,h>=0.

Then q>=p and d<=s.  The D0=m equation gives
  r=(x*p+y*q+q*p-p)/(y+p).

This script verifies that the exact PMS margin numerator, after clearing
positive denominators and shifting p=1+P, d=D, e=E, h=H, has only
nonnegative coefficients.
"""

import sympy as sp

from _codex_ocpms_mask47_subcase_lt import pms_numerator_for_mask47


def main() -> None:
    p, d, e, h = sp.symbols("p d e h", positive=True)
    P, D, E, H = sp.symbols("P D E H", nonnegative=True)

    s = d + e
    q = p + s
    x = 1 + h
    y = x + d
    r = sp.factor((x * p + y * q + q * p - p) / (y + p))

    num, den = pms_numerator_for_mask47(p, s, x, y, r)
    num, den = sp.together(num / den).as_numer_denom()
    shifted = sp.Poly(
        sp.expand(num.subs({p: P + 1, d: D, e: E, h: H})),
        P,
        D,
        E,
        H,
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
