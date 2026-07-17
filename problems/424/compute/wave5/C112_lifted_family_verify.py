#!/usr/bin/env python3
"""Independent exact replay of the C112 lifted-family search claim."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter
from functools import cache

import sympy


OTHER = 0
GENERATED = 1
SPLITLESS = 2
HARD = 3
BASE_N = 3 * 13 * 43 * 557 * 2_213
BASE_H = BASE_N - 1


def allowed(value: int) -> bool:
    return value >= 2 and value % 3 != 1


@cache
def pairs(value: int) -> tuple[tuple[int, int], ...]:
    product = value + 1
    return tuple(
        (left, product // left)
        for left_value in sympy.divisors(product)
        for left in (int(left_value),)
        if 2 <= left < product // left
        and allowed(left)
        and allowed(product // left)
    )


@cache
def closure_state(value: int) -> int:
    if value in (2, 3):
        return GENERATED
    if not allowed(value):
        return OTHER
    value_pairs = pairs(value)
    generated_pair = False
    for left, right in value_pairs:
        if closure_state(left) == GENERATED:
            if closure_state(right) == GENERATED:
                generated_pair = True
                break
    if generated_pair:
        return GENERATED
    if not value_pairs:
        return SPLITLESS
    if value % 2 == 0:
        product = value + 1
        parent = product // 3 if product % 3 == 0 else None
        if parent is None or not allowed(parent) or parent == 3:
            return HARD
    return OTHER


def seed_root(value: int) -> int:
    if value < 3 or value % 2 == 0:
        raise ValueError(("seed_root", value))
    while value % 2:
        value = (value + 1) // 2
    return value


def replay(prime_limit: int) -> dict[str, object]:
    if closure_state(BASE_H) != HARD:
        raise RuntimeError("base is not hard")

    blockers = []
    generated_complements = []
    for left, right in pairs(BASE_H):
        states = (closure_state(left), closure_state(right))
        if states.count(GENERATED) != 1:
            raise RuntimeError(("base pair does not have one generated endpoint", left, right))
        blocker = right if states[0] == GENERATED else left
        generated = left if states[0] == GENERATED else right
        root = seed_root(blocker)
        if closure_state(root) in (GENERATED, SPLITLESS):
            raise RuntimeError(("base blocker root is not reducible missing", blocker, root))
        blockers.append(blocker)
        generated_complements.append(generated)

    blockers.sort()
    tested = 0
    largest_ell = None
    failures = []
    counts: Counter[int] = Counter()
    digest = hashlib.sha256()
    for ell_value in sympy.primerange(7, prime_limit + 1):
        ell = int(ell_value)
        if ell % 3 != 1 or BASE_N % ell == 0:
            continue
        tested += 1
        largest_ell = ell
        first = 0
        for blocker in blockers:
            if closure_state(ell * blocker) == GENERATED:
                first = blocker
                counts[blocker] += 1
                break
        if first == 0:
            failures.append(ell)
        digest.update(struct.pack("<QQ", ell, first))

    return {
        "prime_limit": prime_limit,
        "base_h": BASE_H,
        "base_pair_count": len(pairs(BASE_H)),
        "base_unique_blockers": blockers,
        "base_generated_complements": sorted(generated_complements),
        "plus_primes_tested": tested,
        "largest_ell_tested": largest_ell,
        "largest_source_tested": (
            None if largest_ell is None else largest_ell * BASE_N - 1
        ),
        "first_generated_blocker_counts": {
            str(blocker): counts[blocker] for blocker in blockers
        },
        "unblocked_ell": failures,
        "candidate_digest_sha256": digest.hexdigest(),
        "cache": {
            "state_entries": closure_state.cache_info().currsize,
            "pair_entries": pairs.cache_info().currsize,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    with open(args.claim, encoding="ascii") as handle:
        claim = json.load(handle)
    result = replay(int(claim["prime_limit"]))
    checks = {
        "base_h": claim["base"]["h"] == result["base_h"],
        "base_pair_count": claim["base"]["d"] == result["base_pair_count"],
        "base_unique_blockers": (
            claim["base"]["unique_blockers"] == result["base_unique_blockers"]
        ),
        "plus_primes_tested": (
            claim["plus_primes_tested"] == result["plus_primes_tested"]
        ),
        "largest_ell_tested": (
            claim["largest_ell_tested"] == result["largest_ell_tested"]
        ),
        "largest_source_tested": (
            claim["largest_source_tested"] == result["largest_source_tested"]
        ),
        "first_generated_blocker_counts": (
            claim["first_generated_blocker_counts"]
            == result["first_generated_blocker_counts"]
        ),
        "candidate_digest": (
            claim["candidate_digest"]["sha256"]
            == result["candidate_digest_sha256"]
        ),
        "no_unblocked_prime": not result["unblocked_ell"],
        "no_hard_lift": claim["hard_lifts"] == 0,
        "no_falsifier": claim["falsifier"] is None,
    }
    if not all(checks.values()):
        raise RuntimeError(checks)
    payload = json.dumps({
        "schema": "C112-lifted-family-independent-replay-v1",
        "status": "PASS",
        "checks": checks,
        "replay": result,
    }, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="ascii", newline="\n") as handle:
            handle.write(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
