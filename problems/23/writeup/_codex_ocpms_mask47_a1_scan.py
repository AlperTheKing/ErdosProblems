"""Reduced exact integer scan for the mask-47 a=1 boundary.

This is diagnostic only.  On mask 47 with a=w0=1 and D0=m active,
the variables reduce to p=w5=w9, q=w6=w7, x=w1=w4, y=w2=w3, and

  r = (x*p + y*q + q*p - p) / (y+p).

We scan integer p,q,x,y, keep integer r and all seven inequalities, then
classify the hard complement q>=p and p*x<q*y by y>=x / y<x and by
d=y-x compared with s=q-p when y>=x.
"""

from fractions import Fraction
import argparse


def pms_margin(w):
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = map(Fraction, w)
    z27 = w6 * (w0 * w5 + w3 * w8 + w5 * w8)
    a27 = w0 * w5 + w0 * w6 + w3 * w6 + w3 * w8 + w5 * w6 + w5 * w8 + w6 * w8
    z19 = w5 * (w0 * w6 + w4 * w8 + w6 * w8)
    a19 = w0 * w5 + w0 * w6 + w4 * w5 + w4 * w8 + w5 * w6 + w5 * w8 + w6 * w8
    z79 = w0 * w5 * w6 + w3 * w4 * w8 + w3 * w6 * w8 + w4 * w5 * w8 + w5 * w6 * w8
    a79 = (
        w0 * w5
        + w0 * w6
        + w3 * w4
        + w3 * w6
        + w3 * w8
        + w4 * w5
        + w4 * w8
        + w5 * w6
        + w5 * w8
        + w6 * w8
    )
    core = w0 + w3 + w4 + w5 + w6 + w8
    endpoints = w1 + w2 + w7 + w9
    f0 = 2 * (core + endpoints) ** 2 + 75 * core - 225 * w1 * w9 - 225 * w2 * w7 - 200 * w7 * w9
    reservoir = (
        75 * (Fraction(7, 3) - a19 / z19) * w1 * w9
        + 75 * (Fraction(7, 3) - a27 / z27) * w2 * w7
        + 75 * (2 - a79 / z79) * w7 * w9
    )
    return f0 + reservoir


def ok(w):
    w0, w1, w2, w3, w4, w5, w6, w7, w8, w9 = w
    m = w1 * w9 + w2 * w7 + w7 * w9
    return (
        w5 >= w9
        and w6 >= w7
        and w3 + w5 >= w2 + w9
        and w4 + w6 >= w1 + w7
        and w0 * w6 + w3 * w8 + w5 * w8 >= m
        and w0 * w5 + w3 * w8 + w5 * w8 >= m
        and w0 * w6 + w4 * w8 + w6 * w8 >= m
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-weight", type=int, default=40)
    args = ap.parse_args()
    B = args.max_weight

    buckets = {}
    total = 0
    kept = 0
    failures = []
    for p in range(1, B + 1):
        for q in range(p, B + 1):
            for x in range(1, B + 1):
                for y in range(1, B + 1):
                    num = x * p + y * q + q * p - p
                    den = y + p
                    if num % den:
                        continue
                    r = num // den
                    if not (1 <= r <= B):
                        continue
                    w = (1, x, y, y, x, p, q, q, r, p)
                    total += 1
                    if not ok(w):
                        continue
                    if not (q >= p and x * p < q * y):
                        continue
                    kept += 1
                    s = q - p
                    if y >= x:
                        d = y - x
                        if d <= s:
                            bucket = "y>=x,d<=s"
                        else:
                            bucket = "y>=x,d>s"
                    else:
                        bucket = "y<x"
                    margin = pms_margin(w)
                    if margin < 0:
                        failures.append((w, margin))
                    best = buckets.get(bucket)
                    if best is None or margin < best[0]:
                        buckets[bucket] = (margin, w)
    print("B", B, "total_a1_integer", total, "kept_hard", kept, "failures", len(failures))
    for bucket in sorted(buckets):
        margin, w = buckets[bucket]
        print(bucket, "min_margin", margin, "w", w)
    if failures:
        print("first_failure", failures[0])
        raise SystemExit(1)
    print("VERDICT PASS")


if __name__ == "__main__":
    main()
