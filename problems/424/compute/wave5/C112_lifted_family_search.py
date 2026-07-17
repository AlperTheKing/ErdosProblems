#!/usr/bin/env python3
"""Exact sparse search obtained by lifting a C105 d=8,s=0 hard hole.

If N0=h0+1 and ell is a new plus prime, every admissible pair of N0
splits into two admissible pairs of ell*N0.  This searches that doubled
factor-pair family without constructing the closure on a contiguous range.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
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

BASE_Q = 2_213
BASE_N = 3 * 13 * 43 * 557 * BASE_Q
BASE_H = BASE_N - 1


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
    return 1 + (n - 1) // ((n - 1) & -(n - 1))


def endpoint_row(endpoint: int) -> dict[str, object]:
    endpoint_state = state(endpoint)
    if endpoint_state == GENERATED:
        root = None
        root_state = None
    else:
        root = seed_root(endpoint)
        root_state = state(root)
        if root_state == GENERATED:
            raise AssertionError(("generated root of hole", endpoint, root))
    return {
        "value": endpoint,
        "state": STATE_NAME[endpoint_state],
        "root": root,
        "root_state": None if root_state is None else STATE_NAME[root_state],
    }


def pair_audit(h: int) -> tuple[int, int, list[dict[str, object]]]:
    rows = []
    structural_count = 0
    for left, right in factor_pairs(h):
        endpoints = [endpoint_row(left), endpoint_row(right)]
        structural = any(
            row["root_state"] == "structural_splitless" for row in endpoints
        )
        structural_count += int(structural)
        rows.append({
            "pair": [left, right],
            "endpoints": endpoints,
            "counted_in_s": structural,
        })
    return len(rows), structural_count, rows


def base_blockers() -> tuple[int, ...]:
    if state(BASE_H) != HARD:
        raise AssertionError(("base is not hard", BASE_H, state(BASE_H)))
    d, s, rows = pair_audit(BASE_H)
    if (d, s) != (8, 0):
        raise AssertionError(("base statistics", BASE_H, d, s))
    blockers = []
    for row in rows:
        missing = [
            endpoint["value"]
            for endpoint in row["endpoints"]
            if endpoint["state"] != "generated"
        ]
        if len(missing) != 1:
            raise AssertionError(("base pair lacks unique blocker", row))
        blockers.append(int(missing[0]))
    return tuple(sorted(blockers))


def audit(prime_limit: int, stop_on_falsifier: bool) -> dict[str, object]:
    blockers = base_blockers()
    tested = 0
    hard_count = 0
    maximum_deficit = -1
    extremal = None
    falsifier = None
    first_generated_blocker_counts = {str(blocker): 0 for blocker in blockers}
    candidate_digest = hashlib.sha256()
    largest_ell_tested = None

    for ell_value in sympy.primerange(7, prime_limit + 1):
        ell = int(ell_value)
        if ell % 3 != 1 or BASE_N % ell == 0:
            continue
        tested += 1
        largest_ell_tested = ell

        # The old pair's other endpoint is generated.  Thus ell*m must be a
        # hole for every unique old blocker m, or the lifted h is generated.
        first_generated_blocker = next(
            (blocker for blocker in blockers
             if state(ell * blocker) == GENERATED),
            0,
        )
        candidate_digest.update(struct.pack("<QQ", ell, first_generated_blocker))
        if first_generated_blocker:
            first_generated_blocker_counts[str(first_generated_blocker)] += 1
            continue

        h = ell * BASE_N - 1
        h_state = state(h)
        if h_state != HARD:
            raise AssertionError(("blocker criterion mismatch", ell, h, h_state))
        d, s, rows = pair_audit(h)
        if d != 16:
            raise AssertionError(("lifted pair count", ell, h, d))
        hard_count += 1
        deficit = d - s
        record = {
            "ell": ell,
            "h": h,
            "d": d,
            "s": s,
            "deficit": deficit,
            "pairs": rows,
        }
        if deficit > maximum_deficit:
            maximum_deficit = deficit
            extremal = record
        if deficit >= 9:
            falsifier = record
            if stop_on_falsifier:
                break

    return {
        "schema": "C112-lifted-family-search-v1",
        "family": "h=ell*(2067138957)-1 for prime ell=1 mod 3",
        "prime_limit": prime_limit,
        "stop_on_falsifier": stop_on_falsifier,
        "exact_integer_acceptance": True,
        "base": {
            "q": BASE_Q,
            "h": BASE_H,
            "N": BASE_N,
            "d": 8,
            "s": 0,
            "unique_blockers": list(blockers),
        },
        "plus_primes_tested": tested,
        "largest_ell_tested": largest_ell_tested,
        "largest_source_tested": (
            None if largest_ell_tested is None
            else largest_ell_tested * BASE_N - 1
        ),
        "first_generated_blocker_counts": first_generated_blocker_counts,
        "candidate_digest": {
            "algorithm": "SHA-256 of little-endian uint64 (ell,first_generated_blocker)",
            "sha256": candidate_digest.hexdigest(),
        },
        "hard_lifts": hard_count,
        "maximum_deficit": maximum_deficit,
        "extremal": extremal,
        "falsifier": falsifier,
        "cache": {
            "state_entries": state.cache_info().currsize,
            "factor_pair_entries": factor_pairs.cache_info().currsize,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prime-limit", type=int, default=100_000)
    parser.add_argument("--output")
    parser.add_argument("--continue-after-falsifier", action="store_true")
    args = parser.parse_args()
    result = audit(args.prime_limit, not args.continue_after_falsifier)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="ascii", newline="\n") as handle:
            handle.write(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
