"""Exact Fraction scan for r=1 boundary step-difference monotonicity.

Variables for the d<=s bucket:
  p>=1, d>=0, e>=0, h>=0
  q=p+d+e, x=1+h, y=x+d, current r=1.

The strict hard-complement domain is d+e>0.  The adjacent previous point is
  a_prev=a-1, r_prev=1+p/(y+p).

This diagnostic scans whether the step difference increases when incrementing
h, d, or e by one, whenever both points satisfy the seven mask-47 inequalities.
"""

from __future__ import annotations

import argparse
from fractions import Fraction

from _codex_ocpms_mask47_a1_scan import ok, pms_margin


def point(p: int, d: int, e: int, h: int):
    q = p + d + e
    x = 1 + h
    y = x + d
    a = Fraction(x * p + y * q + q * p - y - p, p)
    current = (a, x, y, y, x, p, q, q, Fraction(1), p)
    prev = (a - 1, x, y, y, x, p, q, q, Fraction(1) + Fraction(p, y + p), p)
    return current, prev


def stepdiff(p: int, d: int, e: int, h: int):
    if d + e <= 0:
        return None
    cur, prev = point(p, d, e, h)
    if cur[0] < 1 or prev[0] < 1:
        return None
    if not (ok(cur) and ok(prev)):
        return None
    return pms_margin(cur) - pms_margin(prev)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=12)
    args = ap.parse_args()
    B = args.max

    best = {axis: None for axis in "hde"}
    lower = {axis: 0 for axis in "hde"}
    compared = {axis: 0 for axis in "hde"}
    for p in range(1, B + 1):
        for d in range(0, B + 1):
            for e in range(0, B + 1):
                for h in range(0, B + 1):
                    base = stepdiff(p, d, e, h)
                    if base is None:
                        continue
                    for axis, inc in {
                        "h": (p, d, e, h + 1),
                        "d": (p, d + 1, e, h),
                        "e": (p, d, e + 1, h),
                    }.items():
                        nxt = stepdiff(*inc)
                        if nxt is None:
                            continue
                        delta = nxt - base
                        compared[axis] += 1
                        if best[axis] is None or delta < best[axis][0]:
                            best[axis] = (delta, (p, d, e, h), inc, base, nxt)
                        if delta < 0:
                            lower[axis] += 1
    print("B", B, "compared", compared, "lower", lower)
    for axis in "hde":
        print("axis", axis, "best", best[axis])
    if any(lower.values()):
        print("VERDICT FAIL")
        raise SystemExit(1)
    print("VERDICT PASS")


if __name__ == "__main__":
    main()
