"""Factor-LCM denominator clearing for mask47 r=1 h-lift.

The product-of-denominators sparse certificate is too large.  This script
factors each denominator, builds the polynomial LCM, and clears denominators
against that smaller positive common denominator.
"""

from __future__ import annotations

import argparse

import sympy as sp

from _codex_ocpms_mask47_den_factor_probe import to_expr
from _codex_ocpms_mask47_step_r1_hlift_sparsepoly import make_base, step_terms
from _codex_ocpms_mask47_step_r1_sparsepoly import Rat


def factor_key(expr):
    return sp.srepr(sp.factor(expr))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["epos", "e0_dpos"], default="e0_dpos")
    args = ap.parse_args()
    p, d, e, h, n = make_base(args.split)
    zero = Rat.const(0, n)
    terms = step_terms(p, d, e, h, n, 1) + step_terms(p, d, e, zero, n, -1)
    syms = sp.symbols("x0:" + str(n), nonnegative=True)

    numerators = []
    denom_factors = []
    lcm = {}
    factor_exprs = {}
    for idx, term in enumerate(terms):
        num = to_expr(term.num, syms)
        den = to_expr(term.den, syms)
        fl = sp.factor_list(den)[1]
        numerators.append(num)
        denom_factors.append(fl)
        print("term", idx, "den_terms", len(term.den), "factor_count", len(fl), flush=True)
        for fac, exp in fl:
            fac = sp.factor(fac)
            key = factor_key(fac)
            factor_exprs[key] = fac
            lcm[key] = max(lcm.get(key, 0), exp)

    print("lcm_factor_count", len(lcm), flush=True)
    numerator = 0
    for idx, (num, fl) in enumerate(zip(numerators, denom_factors)):
        have = {factor_key(sp.factor(fac)): exp for fac, exp in fl}
        mult = 1
        for key, exp in lcm.items():
            need = exp - have.get(key, 0)
            if need:
                mult *= factor_exprs[key] ** need
        numerator += num * mult
        numerator = sp.expand(numerator)
        print("assembled", idx, "terms", len(sp.Poly(numerator, *syms).terms()), flush=True)

    poly = sp.Poly(numerator, *syms)
    terms_poly = poly.terms()
    neg = [(monom, c) for monom, c in terms_poly if c < 0]
    print("terms", len(terms_poly), "negative", len(neg), "min_coeff", min(c for _, c in terms_poly), flush=True)
    if neg:
        print("first_negative", neg[0], flush=True)
        raise SystemExit(1)
    print("VERDICT PASS", flush=True)


if __name__ == "__main__":
    main()
