"""Sparse-polynomial h-monotonicity probe for mask-47 current-r=1 step.

Target:
  StepDiff(p,d,e,h+1) - StepDiff(p,d,e,h) >= 0

where
  q=p+d+e, x=1+h, y=x+d, current r=1.

The hard-complement domain d+e>0 is split into:
  epos      e>=1, d>=0
  e0_dpos   e=0, d>=1
"""

from __future__ import annotations

import argparse

from _codex_ocpms_mask47_step_r1_sparsepoly import (
    Rat,
    clear_terms,
    padd,
    pconst,
    pms_terms,
    pvar,
)


def step_terms(p: Rat, d: Rat, e: Rat, h: Rat, n: int, sign: int):
    one = Rat.const(1, n)
    q = p.add(d).add(e)
    x = one.add(h)
    y = x.add(d)
    r = one
    a_num = x.mul(p).add(y.mul(q)).add(q.mul(p)).sub(y).sub(p)
    a = a_num.div(p)
    r_prev = one.add(p.div(y.add(p)))
    current = (a, x, y, y, x, p, q, q, r, p)
    previous = (a.sub(one), x, y, y, x, p, q, q, r_prev, p)
    return pms_terms(current, n, sign) + pms_terms(previous, n, -sign)


def make_base(split: str):
    n = 4 if split == "epos" else 3
    p = Rat.poly(padd(pvar(0, n), pconst(1, n)), n)
    if split == "epos":
        d = Rat.poly(pvar(1, n), n)
        e = Rat.poly(padd(pvar(2, n), pconst(1, n)), n)
        h = Rat.poly(pvar(3, n), n)
    elif split == "e0_dpos":
        d = Rat.poly(padd(pvar(1, n), pconst(1, n)), n)
        e = Rat.const(0, n)
        h = Rat.poly(pvar(2, n), n)
    else:
        raise ValueError(split)
    return p, d, e, h, n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["epos", "e0_dpos"], default="epos")
    args = ap.parse_args()
    p, d, e, h, n = make_base(args.split)
    one = Rat.const(1, n)
    terms = step_terms(p, d, e, h.add(one), n, 1) + step_terms(p, d, e, h, n, -1)
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
