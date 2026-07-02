"""Quotient slack-CAGE checker for balanced odd-cycle blowups.

Consider the balanced blowup C_L[t] of an odd cycle, with the alternating cut
that leaves only the edge class A_{L-1}A_0 bad.  Fix a row Q containing one
distinguished vertex q_i in each class A_i.  By clone symmetry, a subset U is
summarized by:

    c_i = |U cap A_i|,
    e_i = 1_{q_i in U}.

For fixed counts c_i, the slack-CAGE left side is maximized by e_i=1 whenever
c_i>0, since the right side does not depend on e_i.  Thus all subsets reduce
to the count vectors c_i in {0,...,t}.

The exact inequality checked is

    D_Q(U) <= |U| + sigma(U) + eta,

where eta = (L^2/25 - 1)t^2, and sigma is B-boundary minus M-boundary.
"""

from __future__ import annotations

import argparse
from fractions import Fraction as F
from itertools import product


def boundary_between(a: int, b: int, t: int) -> int:
    return t * (a + b) - 2 * a * b


def check(L: int, t: int):
    eta = F(L * L * t * t, 25) - t * t
    min_margin = (F(10**18), None)
    violations = []
    checks = 0
    denom = t ** (L - 2)

    for c in product(range(t + 1), repeat=L):
        checks += 1
        size = sum(c)
        # Maximize over whether the distinguished Q vertex is included.
        lhs = F(0)
        for i, ci in enumerate(c):
            if ci == 0:
                continue
            prod_other = 1
            for j, cj in enumerate(c):
                if i != j:
                    prod_other *= cj
            lhs += F(prod_other, denom)

        b_boundary = sum(boundary_between(c[i], c[i + 1], t) for i in range(L - 1))
        m_boundary = boundary_between(c[L - 1], c[0], t)
        sigma = b_boundary - m_boundary
        rhs = F(size + sigma) + eta
        margin = rhs - lhs
        if margin < min_margin[0]:
            min_margin = (margin, c, lhs, rhs, size, sigma, eta)
        if margin < 0:
            violations.append((c, lhs, rhs, margin, size, sigma, eta))
            break

    return checks, min_margin, violations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lengths", default="5,7,9")
    ap.add_argument("--tmax", type=int, default=10)
    ap.add_argument("--stop-first", action="store_true")
    args = ap.parse_args()

    total = 0
    first = None
    for L in [int(x) for x in args.lengths.split(",") if x.strip()]:
        for t in range(1, args.tmax + 1):
            checks, min_margin, violations = check(L, t)
            total += checks
            print(
                f"C{L}[{t}] checks={checks} min_margin={min_margin}",
                flush=True,
            )
            if violations and first is None:
                first = (L, t, violations[0])
            if first is not None and args.stop_first:
                break
        if first is not None and args.stop_first:
            break

    print("=== quotient slack-CAGE odd-cycle blowups ===")
    print("checks:", total)
    print("first:", first or "")
    print("VERDICT:", "HOLDS" if first is None else "FAILS")


if __name__ == "__main__":
    main()
