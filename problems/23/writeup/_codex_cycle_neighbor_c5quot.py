"""Quotient gate for the cycle-neighbor Hall atom on C5 blow-ups.

The full atom gate enumerates all shortest rows, which is too slow for large
nonuniform blow-ups.  This script uses the five-class symmetry for the cut that
leaves A0-A1 bad in a complete C5 blow-up.

For sizes n0..n4 and fixed bad edge f=(a in A0, b in A1), enumerate only:
  y_i = |Y cap A_i| and endpoint flags A=[a in Y], B=[b in Y].

The formula computes the total atom mass whose four cycle-neighbor ports are
contained in Y.  It is exact Fraction arithmetic.
"""

from __future__ import annotations

import argparse
from fractions import Fraction as F


def demand(parts: list[int], y: list[int], a_in: int, b_in: int) -> F:
    n0, n1, n2, n3, n4 = parts
    y0, y1, y2, y3, y4 = y
    A = F(a_in)
    B = F(b_in)
    # Class 0 shared vertex: x=a, Q endpoint u0=a.
    term0 = B * F(y1 * y4 * y4, n4 * n4)
    # Class 1 shared vertex: x=b, Q endpoint u1=b.
    term1 = A * F(y0 * y2 * y2, n2 * n2)
    # Class 4 shared vertex.
    term4 = A * F(y0 * n1 * y3 * y3, n4 * n3 * n3)
    # Class 2 shared vertex.
    term2 = B * F(y1 * n0 * y3 * y3, n2 * n3 * n3)
    # Class 3 shared vertex.
    term3 = F(n0 * n1 * y4 * y4 * y2 * y2, n3 * n4 * n4 * n2 * n2)
    return term0 + term1 + term2 + term3 + term4


def worst(parts: list[int]):
    best = None
    best_nonempty = None
    n0, n1, n2, n3, n4 = parts
    for y0 in range(n0 + 1):
        for y1 in range(n1 + 1):
            for y2 in range(n2 + 1):
                for y3 in range(n3 + 1):
                    for y4 in range(n4 + 1):
                        y = [y0, y1, y2, y3, y4]
                        rhs = sum(y)
                        for A in (0, 1):
                            if A > y0:
                                continue
                            for B in (0, 1):
                                if B > y1:
                                    continue
                                lhs = demand(parts, y, A, B)
                                margin = lhs - rhs
                                rec = (margin, lhs, rhs, tuple(y), A, B)
                                if best is None or rec > best:
                                    best = rec
                                if rhs > 0 and (
                                    best_nonempty is None or rec > best_nonempty
                                ):
                                    best_nonempty = rec
    return best, best_nonempty


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=0)
    ap.add_argument("--max-k", type=int, default=0)
    args = ap.parse_args()

    ks = [args.k] if args.k else range(1, args.max_k + 1)
    for k in ks:
        parts = [k + 1, k, k + 1, k, k + 1]
        (margin, lhs, rhs, y, A, B), nonempty = worst(parts)
        if nonempty is None:
            nem = "nonempty=none"
            nem_ok = True
        else:
            nmargin, nlhs, nrhs, ny, nA, nB = nonempty
            nem = (
                f"nonempty_margin={nmargin} nonempty_lhs={nlhs} "
                f"nonempty_rhs={nrhs} nonempty_y={ny} nonempty_A={nA} "
                f"nonempty_B={nB}"
            )
            nem_ok = nmargin <= 0
        print(
            f"k={k} N={sum(parts)} margin={margin} lhs={lhs} rhs={rhs} "
            f"y={y} A={A} B={B} ok={margin <= 0} {nem} "
            f"nonempty_ok={nem_ok}",
            flush=True,
        )
        if margin > 0 or not nem_ok:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
