"""Derivative Bernstein probe for mask-47 boundary-lift monotonicity.

Diagnostic target:

  On the mask-47 hard complement q>=p, p*x<q*y, D0=m, prove
  F(a,r(a)) is nondecreasing in a.

Since r(a)=(x*p+y*q+q*p-a*p)/(y+p), this is equivalent to

  - dF/dr >= 0

on the feasible r-interval.  This script tests the easiest complement
subcase y<x:

  q=p+s, x=y+e, p,y>=1, s,e>=0,

over the interval 1 <= r <= r0 where r0 is the a=1 boundary.  It checks
whether the numerator of -dF/dr has nonnegative Bernstein coefficients after
the standard shifts.
"""

from __future__ import annotations

import sympy as sp
import argparse

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
        print("SKIP_HEAVY: rerun with --run-heavy to start the derivative Bernstein probe.")
        return

    p, s, y, e, r, theta = sp.symbols("p s y e r theta", positive=True)
    P, S, Y, E = sp.symbols("P S Y E", nonnegative=True)

    q = p + s
    x = y + e
    r0 = sp.factor((x * p + y * q + q * p - p) / (y + p))

    num, den = pms_numerator_for_mask47(p, s, x, y, r)
    deriv_num = sp.expand(-(sp.diff(num, r) * den - num * sp.diff(den, r)))
    degree_r = sp.Poly(deriv_num, r).degree()
    print("degree_r", degree_r)
    print("r0", sp.factor(r0))

    transformed = sp.expand(deriv_num.subs(r, 1 + theta * (r0 - 1)))
    bern = power_to_bernstein(transformed, theta)

    ok = True
    for i, coeff in enumerate(bern):
        coeff_num, coeff_den = sp.together(coeff).as_numer_denom()
        shifted = sp.Poly(
            sp.expand(coeff_num.subs({p: P + 1, s: S, y: Y + 1, e: E})),
            P,
            S,
            Y,
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
