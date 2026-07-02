"""Factor denominator polynomials from sparse r=1 h-lift/h-mono probes."""

from __future__ import annotations

import argparse
from fractions import Fraction

import sympy as sp

from _codex_ocpms_mask47_step_r1_hlift_sparsepoly import make_base, step_terms
from _codex_ocpms_mask47_step_r1_sparsepoly import Rat


def to_expr(poly, syms):
    out = 0
    for monom, coeff in poly.items():
        term = sp.Rational(coeff.numerator, coeff.denominator)
        for s, e in zip(syms, monom):
            term *= s**e
        out += term
    return sp.expand(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["epos", "e0_dpos"], default="e0_dpos")
    args = ap.parse_args()
    p, d, e, h, n = make_base(args.split)
    zero = Rat.const(0, n)
    terms = step_terms(p, d, e, h, n, 1) + step_terms(p, d, e, zero, n, -1)
    syms = sp.symbols("x0:" + str(n), nonnegative=True)
    seen = {}
    for idx, term in enumerate(terms):
        key = tuple(sorted(term.den.items()))
        if key in seen:
            print("term", idx, "same_as", seen[key])
            continue
        seen[key] = idx
        expr = to_expr(term.den, syms)
        print("term", idx, "terms", len(term.den))
        print(sp.factor(expr))


if __name__ == "__main__":
    main()
