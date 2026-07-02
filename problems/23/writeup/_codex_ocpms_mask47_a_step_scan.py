"""Exact integer step scan for mask-47 a-lift monotonicity.

For the hard complement of mask 47:
  q>=p, p*x<q*y, D0=m active,
  r(a)=(x*p+y*q+q*p-a*p)/(y+p).

The boundary-lift scan checks F(a)>=F(1).  This sharper diagnostic checks
whether F(a)>=F(a-1) for every adjacent integral pair for which both quotient
points are feasible.  A failure would mean the boundary-lift proof cannot be
plain monotonicity in a.
"""

from __future__ import annotations

from fractions import Fraction
import argparse

from _codex_ocpms_mask47_a1_scan import ok, pms_margin


def point(a, p, q, x, y):
    num = x * p + y * q + q * p - a * p
    den = y + p
    r = Fraction(num, den)
    return (a, x, y, y, x, p, q, q, r, p)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-weight", type=int, default=40)
    args = ap.parse_args()
    B = args.max_weight

    compared = 0
    lower = 0
    best_diff: Fraction | None = None
    best = None
    for a in range(2, B + 1):
        for p in range(1, B + 1):
            for q in range(p, B + 1):
                for x in range(1, B + 1):
                    for y in range(1, B + 1):
                        if not (x * p < q * y):
                            continue
                        w = point(a, p, q, x, y)
                        w0 = point(a - 1, p, q, x, y)
                        if not (1 <= w[8] <= B and 1 <= w0[8] <= B):
                            continue
                        if not (ok(w) and ok(w0)):
                            continue
                        compared += 1
                        diff = pms_margin(w) - pms_margin(w0)
                        if best_diff is None or diff < best_diff:
                            best_diff = diff
                            best = (w, w0)
                        if diff < 0:
                            lower += 1
                            print("LOWER", diff, "w", w, "prev", w0)
                            print("VERDICT FAIL")
                            return
    print("B", B, "compared", compared, "lower", lower)
    print("best_diff", best_diff, "w", best[0] if best else None, "prev", best[1] if best else None)
    print("VERDICT PASS")


if __name__ == "__main__":
    main()
