#!/usr/bin/env python3
"""Exact priority-queue enumeration for Erdos problem 424."""

from __future__ import annotations

import argparse
import hashlib
import heapq
from bisect import bisect_right
from fractions import Fraction
from itertools import combinations


SEEDS = (2, 3)


def generated_up_to(limit: int) -> list[int]:
    """Return the generated set intersected with [1, limit], in order.

    A candidate is inserted only from a pair of distinct values: initial pairs
    use combinations(SEEDS, 2), and every later pair consists of the newly
    accepted value and one strictly smaller, previously accepted value.
    """
    if limit < 1:
        return []

    values = [seed for seed in SEEDS if seed <= limit]
    accepted = set(values)
    heap: list[int] = []
    queued: set[int] = set()

    def enqueue(candidate: int) -> None:
        if candidate <= limit and candidate not in accepted and candidate not in queued:
            heapq.heappush(heap, candidate)
            queued.add(candidate)

    for x, y in combinations(values, 2):
        assert x != y
        enqueue(x * y - 1)

    while heap:
        value = heapq.heappop(heap)
        queued.remove(value)
        assert value not in accepted
        assert not values or values[-1] < value

        old_values = values
        values = old_values + [value]
        accepted.add(value)

        # Pair value only with older values. Thus x != value by construction.
        for x in old_values:
            assert x != value
            candidate = x * value - 1
            if candidate > limit:
                break
            enqueue(candidate)

    return values


def fixed_point_up_to(limit: int) -> list[int]:
    """Slow independent oracle: literal iteration of the truncated closure."""
    current = {seed for seed in SEEDS if seed <= limit}
    while True:
        additions: set[int] = set()
        for x, y in combinations(sorted(current), 2):
            assert x != y
            candidate = x * y - 1
            if candidate <= limit:
                additions.add(candidate)
        enlarged = current | additions
        if enlarged == current:
            return sorted(current)
        current = enlarged


def canonical_digest(values: list[int]) -> str:
    """SHA-256 of the comma-joined decimal values, with no trailing newline."""
    payload = ",".join(map(str, values)).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def print_census(bounds: list[int]) -> None:
    if not bounds or any(bound < 1 for bound in bounds):
        raise ValueError("census bounds must be positive integers")
    all_values = generated_up_to(max(bounds))
    print("X\tcount\tdensity\tdecimal\tmax_element\tsha256")
    for bound in bounds:
        count = bisect_right(all_values, bound)
        prefix = all_values[:count]
        density = Fraction(count, bound)
        maximum = prefix[-1] if prefix else "-"
        print(
            f"{bound}\t{count}\t{density}\t{count / bound:.12f}\t"
            f"{maximum}\t{canonical_digest(prefix)}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--limit", type=int, help="print every generated value at most LIMIT")
    group.add_argument(
        "--census", type=int, nargs="+", metavar="X", help="print census rows for bounds X"
    )
    group.add_argument(
        "--cross-check",
        type=int,
        metavar="X",
        help="compare the heap generator with the literal fixed-point closure through X",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.limit is not None:
        print(" ".join(map(str, generated_up_to(args.limit))))
    elif args.census is not None:
        print_census(args.census)
    else:
        heap_values = generated_up_to(args.cross_check)
        fixed_values = fixed_point_up_to(args.cross_check)
        if heap_values != fixed_values:
            raise SystemExit("MISMATCH")
        print(
            f"OK X={args.cross_check} count={len(heap_values)} "
            f"sha256={canonical_digest(heap_values)}"
        )


if __name__ == "__main__":
    main()
