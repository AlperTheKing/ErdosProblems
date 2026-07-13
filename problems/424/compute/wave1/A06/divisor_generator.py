#!/usr/bin/env python3
"""Exact divisor-recursion generator and independent forward cross-check for #424."""

from __future__ import annotations

import argparse
import hashlib
import heapq
import math
from array import array


# OEIS A005244, terms displayed on the main sequence page on 2026-07-13.
OEIS_PREFIX = (
    2, 3, 5, 9, 14, 17, 26, 27, 33, 41, 44, 50, 51, 53, 65, 69, 77,
    80, 81, 84, 87, 98, 99, 101, 105, 122, 125, 129, 131, 134, 137, 149,
    152, 153, 158, 159, 161, 164, 167, 173, 194, 195, 197, 201, 204, 206,
    209, 219, 230, 233, 237, 239, 242, 243, 249,
)


def smallest_prime_factors(limit: int) -> array:
    """Return an SPF table; a zero entry at n >= 2 means that n is prime."""
    spf = array("I", [0]) * (limit + 1)
    for prime in range(2, math.isqrt(limit) + 1):
        if spf[prime] != 0:
            continue
        for multiple in range(prime * prime, limit + 1, prime):
            if spf[multiple] == 0:
                spf[multiple] = prime
    return spf


def divisors_from_spf(value: int, spf: array) -> list[int]:
    """Enumerate all positive divisors of value using exact integer arithmetic."""
    remaining = value
    divisors = [1]
    while remaining > 1:
        prime = spf[remaining]
        if prime == 0:
            prime = remaining
        power = 1
        exponent = 0
        while remaining % prime == 0:
            remaining //= prime
            exponent += 1
        old_divisors = tuple(divisors)
        for _ in range(exponent):
            power *= prime
            divisors.extend(divisor * power for divisor in old_divisors)
    divisors.sort()
    return divisors


def generate_by_divisors(limit: int) -> tuple[bytearray, array]:
    """Compute A through limit by the recurrence on factor pairs of n+1.

    witness[n] is the smaller factor d for a non-seed accepted n, so its other
    factor is exactly (n+1)//d.  Testing d*d < n+1 enforces distinct values.
    """
    member = bytearray(limit + 1)
    witness = array("I", [0]) * (limit + 1)
    for seed in (2, 3):
        if seed <= limit:
            member[seed] = 1

    spf = smallest_prime_factors(limit + 1)
    for n in range(4, limit + 1):
        product = n + 1
        for divisor in divisors_from_spf(product, spf):
            if divisor * divisor >= product:
                break
            quotient = product // divisor
            if member[divisor] and member[quotient]:
                member[n] = 1
                witness[n] = divisor
                break
    return member, witness


def generate_by_forward_closure(limit: int) -> bytearray:
    """Compute the truncated closure by pairing each new value with older ones."""
    member = bytearray(limit + 1)
    queued = bytearray(limit + 1)
    heap: list[int] = []
    for seed in (2, 3):
        if seed <= limit:
            queued[seed] = 1
            heapq.heappush(heap, seed)

    accepted: list[int] = []
    while heap:
        y = heapq.heappop(heap)
        if member[y]:
            continue
        member[y] = 1
        for x in accepted:
            candidate = x * y - 1
            if candidate > limit:
                break
            # Here x is an older accepted value, hence x != y by construction.
            if not member[candidate] and not queued[candidate]:
                queued[candidate] = 1
                heapq.heappush(heap, candidate)
        accepted.append(y)
    return member


def accepted_values(member: bytearray) -> list[int]:
    return [n for n, present in enumerate(member) if present]


def verify_witnesses(member: bytearray, witness: array) -> None:
    for n in range(4, len(member)):
        if not member[n]:
            assert witness[n] == 0
            continue
        divisor = witness[n]
        quotient = (n + 1) // divisor
        assert divisor >= 2
        assert divisor < quotient
        assert divisor * quotient == n + 1
        assert divisor < n and quotient < n
        assert member[divisor] and member[quotient]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    args = parser.parse_args()
    if args.limit < 249:
        parser.error("--limit must be at least 249 for the OEIS prefix check")

    divisor_member, witnesses = generate_by_divisors(args.limit)
    verify_witnesses(divisor_member, witnesses)
    forward_member = generate_by_forward_closure(args.limit)

    assert divisor_member == forward_member
    values = accepted_values(divisor_member)
    assert tuple(values[: len(OEIS_PREFIX)]) == OEIS_PREFIX
    # These would be introduced by 3*3-1 and 5*5-1 if equality were allowed.
    assert not divisor_member[8]
    assert not divisor_member[24]

    digest = hashlib.sha256(divisor_member).hexdigest()
    print(f"limit={args.limit}")
    print(f"member_count={len(values)}")
    print(f"divisor_forward_equal={str(divisor_member == forward_member).lower()}")
    print(f"oeis_prefix_terms={len(OEIS_PREFIX)}")
    print(f"oeis_prefix_equal=true")
    print("distinctness_sentinels=8:false,24:false")
    print(f"membership_bytearray_sha256={digest}")
    print("last_10=" + ",".join(map(str, values[-10:])))


if __name__ == "__main__":
    main()
