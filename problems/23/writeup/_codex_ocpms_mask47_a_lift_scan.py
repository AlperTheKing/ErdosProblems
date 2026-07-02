"""Exact integer scan for lifting mask-47 a=1 boundary to a>1.

Diagnostic only.  For integer mask47 points in the hard complement
q>=p and p*x<q*y, compare the PMS margin at a>=1 with the a=1 boundary
margin for the same (p,q,x,y), when the boundary r is integral.

If all differences are nonnegative in a large box, that supports a future
monotonicity/boundary-lift lemma.  If not, the first lower interior point is
the next face to attack.
"""

from fractions import Fraction
import argparse

from _codex_ocpms_mask47_a1_scan import ok, pms_margin


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-weight", type=int, default=40)
    ap.add_argument("--strict-interior", action="store_true")
    args = ap.parse_args()
    B = args.max_weight

    compared = 0
    lower = []
    best_diff = None
    best = None
    for a in range(2 if args.strict_interior else 1, B + 1):
        for p in range(1, B + 1):
            for q in range(p, B + 1):
                for x in range(1, B + 1):
                    for y in range(1, B + 1):
                        if not (x * p < q * y):
                            continue
                        num = x * p + y * q + q * p - a * p
                        den = y + p
                        if num % den:
                            continue
                        r = num // den
                        if not (1 <= r <= B):
                            continue
                        w = (a, x, y, y, x, p, q, q, r, p)
                        if not ok(w):
                            continue

                        num0 = x * p + y * q + q * p - p
                        if num0 % den:
                            continue
                        r0 = num0 // den
                        if not (1 <= r0 <= B):
                            continue
                        w0 = (1, x, y, y, x, p, q, q, r0, p)
                        if not ok(w0):
                            continue

                        compared += 1
                        diff = pms_margin(w) - pms_margin(w0)
                        if best_diff is None or diff < best_diff:
                            best_diff = diff
                            best = (w, w0)
                        if diff < 0:
                            lower.append((diff, w, w0))
                            print("LOWER", diff, "w", w, "boundary", w0)
                            raise SystemExit(1)

    print("B", B, "compared", compared, "lower", len(lower))
    print("best_diff", best_diff, "w", best[0] if best else None, "boundary", best[1] if best else None)
    print("VERDICT PASS")


if __name__ == "__main__":
    main()

