"""Derivative certificate probe for mask47 lift, bucket y>=x and d<=s.

This is the bucket containing the closest rational step-monotonicity examples.

Parametrization:
  q = p + d + e,
  x = 1 + h,
  y = x + d,
  d,e,h >= 0.

On mask47 with D0=m active, a is determined by r:
  a=(x*p+y*q+q*p-r*(y+p))/p.

The a=1 boundary gives the upper endpoint r0.  Since a increases as r
decreases, monotonicity in a is equivalent to -dF/dr >= 0 on 1<=r<=r0.

The script checks Bernstein coefficients for -dF/dr on that interval after
clearing denominators and shifting p=1+P.
"""

from __future__ import annotations

import argparse
import sympy as sp

from _codex_ocpms_mask47_subcase_lt import pms_numerator_for_mask47


def power_to_bernstein(poly, theta):
    p = sp.Poly(poly, theta)
    degree = p.degree()
    coeff = [p.coeff_monomial(theta**i) for i in range(degree + 1)]
    out = []
    for k in range(degree + 1):
        b = 0
        for i in range(k + 1):
            b += coeff[i] * sp.binomial(k, i) / sp.binomial(degree, i)
        out.append(sp.factor(b))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-heavy", action="store_true")
    args = ap.parse_args()
    if not args.run_heavy:
        print("SKIP_HEAVY: rerun with --run-heavy to start the d<=s derivative Bernstein probe.")
        return

    p, h, d, e, r, theta = sp.symbols("p h d e r theta", positive=True)
    P, H, D, E = sp.symbols("P H D E", nonnegative=True)

    x = 1 + h
    y = x + d
    s = d + e
    q = p + s
    r0 = sp.factor((x * p + y * q + q * p - p) / (y + p))

    num, den = pms_numerator_for_mask47(p, s, x, y, r)
    deriv_num = sp.expand(-(sp.diff(num, r) * den - num * sp.diff(den, r)))
    print("degree_r", sp.Poly(deriv_num, r).degree())
    print("r0", sp.factor(r0))

    transformed = sp.expand(deriv_num.subs(r, 1 + theta * (r0 - 1)))
    bern = power_to_bernstein(transformed, theta)

    ok = True
    for i, coeff in enumerate(bern):
        coeff_num, coeff_den = sp.together(coeff).as_numer_denom()
        shifted = sp.Poly(
            sp.expand(coeff_num.subs({p: P + 1, h: H, d: D, e: E})),
            P,
            H,
            D,
            E,
        )
        terms = shifted.terms()
        neg = [(m, c) for m, c in terms if c < 0]
        print(
            "B",
            i,
            "den",
            sp.factor(coeff_den),
            "terms",
            len(terms),
            "negative",
            len(neg),
            "min_coeff",
            min(c for _, c in terms),
        )
        if neg:
            ok = False
            print("first_negative", neg[0])
            break
    print("VERDICT", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()
