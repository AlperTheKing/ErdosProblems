#!/usr/bin/env python3
"""Exact pure-divisor relaxation for the C116 eight-exception frontier."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def smallest_prime_factors(limit: int) -> list[int]:
    spf = list(range(limit + 1))
    for p in range(2, math.isqrt(limit - 1) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, limit, p):
            if spf[multiple] == multiple:
                spf[multiple] = p
    return spf


def divisors(n: int, spf: list[int]) -> list[int]:
    out = [1]
    while n > 1:
        p = spf[n]
        old = tuple(out)
        power = 1
        while n % p == 0:
            n //= p
            power *= p
            out.extend(d * power for d in old)
    return out


def pairs_for_product(product: int, spf: list[int]) -> list[tuple[int, int]]:
    out = []
    for a in divisors(product, spf):
        if a < 2 or a * a >= product:
            continue
        b = product // a
        if allowed(a) and allowed(b):
            out.append((a, b))
    return sorted(out)


def seed_root(p: int) -> int:
    shifted = p - 1
    return 1 + shifted // (shifted & -shifted)


def certificate(product: int, pairs: list[tuple[int, int]], structural: list[bool]) -> dict:
    rows = []
    forced = 0
    at_least_one = 0
    for a, b in pairs:
        ra, rb = seed_root(a), seed_root(b)
        sa, sb = structural[ra], structural[rb]
        forced += int(sa and sb)
        at_least_one += int(sa or sb)
        rows.append({"pair": [a, b], "roots": [ra, rb], "structural": [sa, sb]})
    return {
        "h": product - 1,
        "product": product,
        "d": len(pairs),
        "forced_both_structural": forced,
        "at_least_one_structural": at_least_one,
        "two_forced_slack": 2 * forced - len(pairs) + 8,
        "one_forced_slack": forced - len(pairs) + 8,
        "pairs": rows,
    }


def scan(limit: int) -> dict:
    spf = smallest_prime_factors(limit + 2)
    structural = [False] * (limit + 1)
    minimum_two = None
    minimum_one = None
    first_two_failure = None
    first_one_failure = None
    max_d = 0
    tested = 0

    # Every seed root is even and smaller than the odd endpoint.  Precompute
    # literal splitlessness from its complete allowed factor-pair set.
    for r in range(2, limit + 1, 2):
        if allowed(r):
            structural[r] = not pairs_for_product(r + 1, spf)

    for product in range(3, limit + 2, 2):
        h = product - 1
        if not allowed(h):
            continue
        seed_three_easy = (
            product % 3 == 0
            and product // 3 != 3
            and allowed(product // 3)
        )
        if seed_three_easy:
            continue
        pairs = pairs_for_product(product, spf)
        if not pairs:
            continue
        tested += 1
        forced = sum(structural[seed_root(a)] and structural[seed_root(b)] for a, b in pairs)
        two_slack = 2 * forced - len(pairs) + 8
        one_slack = forced - len(pairs) + 8
        max_d = max(max_d, len(pairs))
        if minimum_two is None or two_slack < minimum_two[0]:
            minimum_two = (two_slack, certificate(product, pairs, structural))
        if minimum_one is None or one_slack < minimum_one[0]:
            minimum_one = (one_slack, certificate(product, pairs, structural))
        if two_slack < 0 and first_two_failure is None:
            first_two_failure = certificate(product, pairs, structural)
        if one_slack < 0 and first_one_failure is None:
            first_one_failure = certificate(product, pairs, structural)

    return {
        "schema": "C121-pure-divisor-relaxation-v1",
        "limit_h": limit,
        "exactness": "integer SPF enumeration; no closure membership used",
        "tested_products_with_pairs": tested,
        "maximum_d": max_d,
        "first_failure_2forced_ge_d_minus_8": first_two_failure,
        "first_failure_forced_ge_d_minus_8": first_one_failure,
        "minimum_two_forced_slack": None if minimum_two is None else minimum_two[1],
        "minimum_one_forced_slack": None if minimum_one is None else minimum_one[1],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = scan(args.limit)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
