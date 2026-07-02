"""Symbolic probe for the mask-47 boundary-lift conjecture.

This is diagnostic, not a proof artifact yet.

Mask 47, hard complement:
  q >= p, p*x < q*y, D0=m active,
  a=w0>=1, r=(x*p+y*q+q*p-a*p)/(y+p).

The already closed boundary is a=1.  The lift conjecture is

  F(a,r(a)) >= F(1,r(1)).

This script tests whether the lift difference is Bernstein-coefficient
positive in the a-direction on the full r>=1 interval for the easiest
symbolic subcase y<x:

  q=p+s, x=y+e, y>=1, e>=0, s>=0.

If this fails, the printed negative coefficient is the next split target.
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
    # Convert power coefficients to Bernstein coefficients on [0,1].
    # If P(theta)=sum_i c_i theta^i=sum_k b_k binom(d,k) theta^k(1-theta)^(d-k),
    # then b_k=sum_{i<=k} c_i * binom(k,i)/binom(d,i).
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
        print("SKIP_HEAVY: rerun with --run-heavy to start the full rational-difference Bernstein probe.")
        return

    p, s, y, e, theta = sp.symbols("p s y e theta", positive=True)
    P, S, Y, E = sp.symbols("P S Y E", nonnegative=True)

    q = p + s
    x = y + e

    # a=1+A, 0<=A<=Amax, with Amax chosen from r(a)=1.
    amax = sp.factor((x * p + y * q + q * p - y - 2 * p) / p)
    a = 1 + theta * amax
    r = sp.factor((x * p + y * q + q * p - a * p) / (y + p))
    r0 = sp.factor((x * p + y * q + q * p - p) / (y + p))

    num, den = pms_numerator_for_mask47(p, s, x, y, r)
    num0, den0 = pms_numerator_for_mask47(p, s, x, y, r0)
    diff_num, diff_den = sp.together(num / den - num0 / den0).as_numer_denom()
    diff_num = sp.factor(diff_num)

    if sp.simplify(diff_num.subs(theta, 0)) != 0:
        raise SystemExit("lift difference is not zero at theta=0")

    degree = sp.Poly(diff_num, theta).degree()
    print("degree_theta", degree)
    print("amax", sp.factor(amax))
    print("diff_den", sp.factor(diff_den))

    bern = power_to_bernstein(diff_num, theta)
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
