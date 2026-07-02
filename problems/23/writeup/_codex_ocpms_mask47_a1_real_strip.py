"""Bernstein certificate for the real a=1 strip y>=x, y-x>q-p.

This closes the real-weight gap left by the integer-only argument.

Mask 47 active constraints:
  w5=w9, w6=w7, linL, linR, D0=m.

Boundary:
  a=w0=1.

Parametrization of the remaining real strip:
  q=p+s,
  x=1+h,
  y=x+s+e,
  0 <= e <= s/(p+s).

The upper bound on e is forced by D19>=m.  Indeed on this boundary the
cleared D19 slack is

  h*(s-e*(2p+s)) + s*(p+s+1)
    - e*(e*(p+s)+p^2+2ps+p+s^2).

At h=0 its positive root is e=s/(p+s), and for e>s/(p+s) the h coefficient
is already negative, so D19>=m is impossible for h>=0.

Set e=z*s/(p+s), 0<=z<=1.  This script verifies that the PMS margin numerator
has nonnegative Bernstein coefficients in z after shifting p=1+P, s=S,
h=H.
"""

from math import comb

import sympy as sp

from _codex_ocpms_mask47_subcase_lt import pms_numerator_for_mask47


def main() -> None:
    p, s, h, z, theta = sp.symbols("p s h z theta", positive=True)
    P, S, H = sp.symbols("P S H", nonnegative=True)

    e = z * s / (p + s)
    q = p + s
    x = 1 + h
    y = x + s + e
    r = sp.factor((x * p + y * q + q * p - p) / (y + p))

    num, den = pms_numerator_for_mask47(p, s, x, y, r)
    # Work with the numerator after clearing all positive denominators.
    expr = sp.together(num / den).as_numer_denom()[0]
    degree = sp.Poly(expr, z).degree()
    transformed = sp.Poly(sp.expand(expr.subs(z, theta)), theta)

    ok = True
    for k in range(degree + 1):
        coeff = sum(
            transformed.coeff_monomial(theta**i)
            * sp.Rational(comb(k, i), comb(degree, i))
            for i in range(k + 1)
        )
        coeff_num, coeff_den = sp.together(coeff).as_numer_denom()
        shifted = sp.Poly(
            sp.expand(coeff_num.subs({p: P + 1, s: S, h: H})),
            P,
            S,
            H,
        )
        neg = [(monom, c) for monom, c in shifted.terms() if c < 0]
        print(
            "B",
            k,
            "den",
            sp.factor(coeff_den),
            "terms",
            len(shifted.terms()),
            "negative",
            len(neg),
            "min_coeff",
            min(c for _, c in shifted.terms()),
        )
        if neg:
            ok = False
            print("first_negative", neg[0])
    print("degree_z", degree)
    print("VERDICT", "PASS" if ok else "FAIL")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
