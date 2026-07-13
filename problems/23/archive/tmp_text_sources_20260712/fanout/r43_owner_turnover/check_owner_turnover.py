"""Exact owner-balance turnover for one support-constant middle detour.

This is a local pair-count identity.  It does not assert the global Hall
theorem.  Counts include collision-half demand and unreserved same-owner
FreeHalf capacity at one active owner.
"""

from hashlib import sha256
from itertools import product
import json


COMMON = ("a", "x", "y", "b")
PATH = {"x", "y"}


def owner_collision_demand(counts):
    return 2 * sum(max(value - 1, 0) for value in counts.values())


def owner_same_first_capacity(counts, active_zero_pairs):
    total = 0
    for vertex in COMMON:
        if counts[vertex] == 0:
            total += 2 - int(vertex in active_zero_pairs)
    return total


def owner_balance(counts, active_zero_pairs):
    return (
        owner_same_first_capacity(counts, active_zero_pairs)
        - owner_collision_demand(counts)
    )


def leaving_middle_case(row_count, endpoint_counts):
    old = {
        "self": row_count,
        "a": endpoint_counts[0],
        "x": 1,
        "y": 1,
        "b": endpoint_counts[1],
    }
    new = dict(old)
    new["self"] -= 1
    for vertex in COMMON:
        new[vertex] -= 1
    before = owner_balance(old, set())
    after = owner_balance(new, PATH)
    return after - before


def entering_middle_case(row_count, endpoint_counts):
    old = {
        "self": row_count,
        "a": endpoint_counts[0],
        "x": 0,
        "y": 0,
        "b": endpoint_counts[1],
    }
    new = dict(old)
    new["self"] += 1
    for vertex in COMMON:
        new[vertex] += 1
    before = owner_balance(old, PATH)
    after = owner_balance(new, set())
    return after - before


def main():
    leaving_checked = 0
    entering_checked = 0
    aggregate_histogram = {}

    for row_count in range(1, 9):
        for endpoint_counts in product(range(1, row_count + 1), repeat=2):
            delta = leaving_middle_case(row_count, endpoint_counts)
            expected = 6 + 2 * int(row_count >= 2)
            assert delta == expected
            leaving_checked += 1

    for row_count in range(0, 9):
        endpoint_range = range(0, row_count + 1)
        for endpoint_counts in product(endpoint_range, repeat=2):
            delta = entering_middle_case(row_count, endpoint_counts)
            expected = -6 - 2 * int(row_count >= 1)
            assert delta == expected
            entering_checked += 1

    for leaving_rows in range(1, 9):
        for entering_rows in range(0, 9):
            delta = (
                6 + 2 * int(leaving_rows >= 2)
                - 6 - 2 * int(entering_rows >= 1)
            )
            aggregate_histogram[str(delta)] = aggregate_histogram.get(str(delta), 0) + 1

    payload = {
        "schema": "R43_OWNER_TURNOVER_V1",
        "leavingCasesChecked": leaving_checked,
        "enteringCasesChecked": entering_checked,
        "leavingMiddleBalanceGain": "6 + 2*1[rowCount(m)>=2]",
        "enteringMiddleBalanceGain": "-6 - 2*1[rowCount(v)>=1]",
        "aggregateHistogramForRowCounts0To8": aggregate_histogram,
        "balance": "unreserved same-first FreeHalf capacity minus collision-half demand",
        "scope": "local exact identity; companion/P4/P5/common-blue and global matching not yet used",
        "verdict": "PASS",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("canonical_sha256=" + sha256(canonical.encode("ascii")).hexdigest())


if __name__ == "__main__":
    main()
