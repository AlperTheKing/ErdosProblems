"""Exact brute-force stress for the proposed BANK5-local inequality.

The local model has five positive integer class sizes n0..n4.  The bad
product m=n0*n4 is assumed to be a minimum adjacent product:

  m <= n0*n1, n1*n2, n2*n3, n3*n4.

For a row using one vertex from every class, the proposed flat-cell charge is

  beta = max(0, n4+n0+n0*n4*(1/n1+1/n2+1/n3) - n)

and the proposed local bank is

  n^2/25 - n0*n4.
"""

from __future__ import annotations

import argparse
from fractions import Fraction as F
from itertools import product


def fmt(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=20)
    args = ap.parse_args()

    worst = None
    fail = None
    checked = 0
    for n0, n1, n2, n3, n4 in product(range(1, args.B + 1), repeat=5):
        m = n0 * n4
        if not (m <= n0 * n1 and m <= n1 * n2 and m <= n2 * n3 and m <= n3 * n4):
            continue
        checked += 1
        n = n0 + n1 + n2 + n3 + n4
        mu = F(n4 + n0, 1) + F(n0 * n4, n1) + F(n0 * n4, n2) + F(n0 * n4, n3)
        beta = max(F(0), mu - n)
        bank = F(n * n, 25) - m
        margin = bank - beta
        rec = {
            "margin": margin,
            "sizes": (n0, n1, n2, n3, n4),
            "mu": mu,
            "beta": beta,
            "bank": bank,
        }
        if worst is None or margin < worst["margin"]:
            worst = rec
        if margin < 0:
            fail = rec
            break

    print("=== BANK5-local brute force ===")
    print("B:", args.B)
    print("checked:", checked)
    print("fail:", {k: fmt(v) for k, v in fail.items()} if fail else None)
    if worst:
        print("worst:", {k: fmt(v) for k, v in worst.items()})
    print("VERDICT:", "PASS" if fail is None else "FAIL")


if __name__ == "__main__":
    main()
