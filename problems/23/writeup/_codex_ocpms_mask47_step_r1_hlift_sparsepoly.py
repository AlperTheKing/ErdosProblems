"""Sparse-polynomial h-lift probe for mask-47 current-r=1 step.

Target:
  StepDiff(p,d,e,h) - StepDiff(p,d,e,0) >= 0.

If true on the domain split, the already-closed x=1 face lifts to the full
`r=1, d<=s` bucket.
"""

from __future__ import annotations

import argparse

from _codex_ocpms_mask47_step_r1_hmono_sparsepoly import make_base, step_terms
from _codex_ocpms_mask47_step_r1_sparsepoly import Rat, clear_terms


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["epos", "e0_dpos"], default="e0_dpos")
    args = ap.parse_args()
    p, d, e, h, n = make_base(args.split)
    zero = Rat.const(0, n)
    terms = step_terms(p, d, e, h, n, 1) + step_terms(p, d, e, zero, n, -1)
    print("split", args.split, "nterms", len(terms), flush=True)
    print("term_den_terms", [len(t.den) for t in terms], flush=True)
    numerator = clear_terms(terms, n)
    coeffs = list(numerator.values())
    neg = [(m, c) for m, c in numerator.items() if c < 0]
    print("terms", len(numerator), "negative", len(neg), "min_coeff", min(coeffs), flush=True)
    if neg:
        print("first_negative", neg[0], flush=True)
        raise SystemExit(1)
    print("VERDICT PASS", flush=True)


if __name__ == "__main__":
    main()
