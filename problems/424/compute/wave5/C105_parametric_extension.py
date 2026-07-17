#!/usr/bin/env python3
"""Exact sparse audit of the recurrent C105 d=8 affine family."""

from __future__ import annotations

import argparse
import json
from functools import lru_cache

import sympy


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3
STATE_NAME = {
    OTHER: "other_hole",
    GENERATED: "generated",
    SPLITLESS: "structural_splitless",
    HARD: "hard",
}
COEFFICIENT = 3 * 13 * 43 * 557


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


@lru_cache(maxsize=None)
def factor_pairs(n: int) -> tuple[tuple[int, int], ...]:
    product = n + 1
    divisors = [1]
    for prime, exponent in sympy.factorint(product).items():
        previous = tuple(divisors)
        power = 1
        for _ in range(exponent):
            power *= int(prime)
            divisors.extend(value * power for value in previous)
    return tuple(sorted(
        (left, product // left)
        for left in divisors
        if 2 <= left < product // left
        and allowed(left)
        and allowed(product // left)
    ))


@lru_cache(maxsize=None)
def state(n: int) -> int:
    if n in (2, 3):
        return GENERATED
    if not allowed(n):
        return OTHER
    pairs = factor_pairs(n)
    if any(state(left) == GENERATED and state(right) == GENERATED
           for left, right in pairs):
        return GENERATED
    if not pairs:
        return SPLITLESS
    if n % 2 == 0:
        product = n + 1
        if product % 3 or not allowed(product // 3) or product // 3 == 3:
            return HARD
    return OTHER


def seed_root(n: int) -> int:
    if n < 3 or n % 2 == 0:
        raise AssertionError(("seed_root", n))
    while n % 2:
        n = (n + 1) // 2
    return n


def pair_audit(h: int) -> tuple[int, int, list[dict[str, object]]]:
    rows = []
    structural_count = 0
    for left, right in factor_pairs(h):
        structural = False
        endpoints = []
        for endpoint in (left, right):
            endpoint_state = state(endpoint)
            if endpoint_state == GENERATED:
                root = None
                root_state = None
            else:
                root = seed_root(endpoint)
                root_state = state(root)
                structural |= root_state == SPLITLESS
            endpoints.append({
                "value": endpoint,
                "state": STATE_NAME[endpoint_state],
                "root": root,
                "root_state": None if root_state is None else STATE_NAME[root_state],
            })
        structural_count += int(structural)
        rows.append({
            "pair": [left, right],
            "endpoints": endpoints,
            "counted_in_s": structural,
        })
    return len(rows), structural_count, rows


def audit(prime_limit: int) -> dict[str, object]:
    hard_rows = []
    for q in sympy.primerange(5, prime_limit + 1):
        q = int(q)
        if q % 3 != 2 or COEFFICIENT % q == 0:
            continue
        h = COEFFICIENT * q - 1
        if state(h) != HARD:
            continue
        d, s, rows = pair_audit(h)
        if d != 8:
            raise AssertionError((q, h, d))
        hard_rows.append({"q": q, "h": h, "d": d, "s": s, "pairs": rows})

    zero_rows = [row for row in hard_rows if row["s"] == 0]
    return {
        "schema": "C105-parametric-extension-v1",
        "prime_limit": prime_limit,
        "coefficient": COEFFICIENT,
        "family": "h_q=934089*q-1 for prime q=2 mod 3",
        "exact_integer_acceptance": True,
        "hard_count": len(hard_rows),
        "zero_s_count": len(zero_rows),
        "hard_rows": hard_rows,
        "zero_s_q": [row["q"] for row in zero_rows],
        "zero_s_h": [row["h"] for row in zero_rows],
        "cache": {
            "state_entries": state.cache_info().currsize,
            "factor_pair_entries": factor_pairs.cache_info().currsize,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prime-limit", type=int, default=1_000_000)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = audit(args.prime_limit)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="ascii", newline="\n") as handle:
            handle.write(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
