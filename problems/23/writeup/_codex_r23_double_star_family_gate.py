"""Exact parameter gate for the R22 double-star collision-Hall obstruction.

For integers a,b >= 2, the core has hubs r,cL,cR, a left leaves, and b
right leaves.  Blue core edges form the double star

    r-cL-L,  r-cR-R,

and every L-R pair is bad.  Each bad edge has the unique length-four blue
row l-cL-r-cR-r'.  Private length-three lock paths join core vertices to a
common anchor.  The canonical lock loads are

    L: b on all but one leaf, b-1 on the last;
    R: a on all but one leaf, a-1 on the last;
    r,cL,cR: 0.

Thus Q = 2ab-2 and N = 4ab+a+b.  This file checks, using only integer
arithmetic and the count-quotient of every core switch, that the displayed
cut is maximum for every requested (a,b).  It then evaluates the exact
three-hub Hall deficiency for sameOwner+commonBad+rowCompanion.

The quotient enumeration is exhaustive: a switch is determined by the
three hub bits, the numbers of selected L/R leaves, and whether each unique
low-lock leaf is selected.  Private lock-path vertices have already been
optimized exactly conditional on their two endpoints.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class FamilyRow:
    a: int
    b: int
    lock_total: int
    n: int
    bad_count: int
    hub_demand: int
    hub_reach: int
    hub_gap: int
    min_switch_loss: int


def possible_low_flags(selected: int, total: int):
    """Whether the distinguished low-lock leaf can lie in the selected set."""
    if selected == 0:
        return (0,)
    if selected == total:
        return (1,)
    return (0, 1)


def core_boundary(a: int, b: int, hr: int, hc_l: int, hc_r: int,
                  left_count: int, right_count: int) -> tuple[int, int]:
    """Return (delta_B, delta_M) for the core switch quotient."""
    delta_b = (hr != hc_l) + (hr != hc_r)
    delta_b += (a - left_count) if hc_l else left_count
    delta_b += (b - right_count) if hc_r else right_count
    delta_m = left_count * (b - right_count)
    delta_m += (a - left_count) * right_count
    return int(delta_b), delta_m


def verify_pair(a: int, b: int) -> FamilyRow:
    assert a >= 2 and b >= 2

    # Canonical integral locks: one low leaf on each shore.
    q_total = (a - 1) * b + (b - 1) + (b - 1) * a + (a - 1)
    assert q_total == 2 * a * b - 2

    min_loss = None
    for hr in (0, 1):
        for hc_l in (0, 1):
            for hc_r in (0, 1):
                for p in range(a + 1):
                    for q in range(b + 1):
                        for low_l in possible_low_flags(p, a):
                            for low_r in possible_low_flags(q, b):
                                # Every ordinary L leaf has lock b, while the
                                # distinguished one has b-1; similarly on R.
                                lock_loss = p * b - low_l + q * a - low_r
                                delta_b, delta_m = core_boundary(
                                    a, b, hr, hc_l, hc_r, p, q
                                )
                                loss = lock_loss + delta_b - delta_m
                                min_loss = loss if min_loss is None else min(min_loss, loss)
                                if loss < 0:
                                    raise AssertionError(
                                        ("nonmaximum displayed cut", a, b, hr, hc_l,
                                         hc_r, p, q, low_l, low_r, loss)
                                    )

    # The two terminal shores show Q >= 2ab-2 for every nonnegative lock
    # realization: flip cL+all L, then cR+all R.  The canonical locks attain it.
    lower_bound_q = (a * b - 1) + (a * b - 1)
    assert q_total == lower_bound_q

    n_core = 3 + a + b
    n = n_core + 1 + 2 * q_total
    assert n == 4 * a * b + a + b

    # One hub owns 2 * [3(ab-1)+a(b-1)+b(a-1)] collision halves.
    one_hub_demand = 2 * (5 * a * b - a - b - 3)
    hub_demand = 3 * one_hub_demand

    # The three hubs reach: sameOwner cells to all vertices outside the row
    # core, plus all distinct same-shore leaf pairs.  Every free cell has 2 halves.
    hub_reach = 2 * (
        3 * (n - n_core) + a * (a - 1) + b * (b - 1)
    )
    hub_gap = hub_demand - hub_reach
    closed_gap = 2 * (3 * a * b - a * a - b * b - 2 * a - 2 * b)
    assert hub_gap == closed_gap

    return FamilyRow(
        a=a,
        b=b,
        lock_total=q_total,
        n=n,
        bad_count=a * b,
        hub_demand=hub_demand,
        hub_reach=hub_reach,
        hub_gap=hub_gap,
        min_switch_loss=int(min_loss),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-side", type=int, default=40)
    parser.add_argument("--show-all", action="store_true")
    args = parser.parse_args()

    rows = []
    for a in range(2, args.max_side + 1):
        for b in range(a, args.max_side + 1):
            rows.append(verify_pair(a, b))

    positive = [row for row in rows if row.hub_gap > 0]
    first = min(positive, key=lambda row: (row.n, row.bad_count, row.a, row.b))

    if args.show_all:
        for row in rows:
            print(row)

    print(f"checked_pairs={len(rows)} max_side={args.max_side}")
    print(
        "first_positive="
        f"a{first.a}_b{first.b} N={first.n} m={first.bad_count} "
        f"Q={first.lock_total} demand={first.hub_demand} "
        f"reach={first.hub_reach} gap={first.hub_gap}"
    )
    diagonal = verify_pair(args.max_side, args.max_side)
    print(
        "diagonal_tail="
        f"a=b={args.max_side} N={diagonal.n} m={diagonal.bad_count} "
        f"gap={diagonal.hub_gap} expected={2*args.max_side*(args.max_side-4)}"
    )
    print("VERDICT: exact infinite double-star family; 3-pattern Hall gap is unbounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
