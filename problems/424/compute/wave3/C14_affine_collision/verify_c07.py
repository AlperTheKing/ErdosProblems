#!/usr/bin/env python3
"""Independent exact trial-divisor replay of the C07 affine census at 1e5."""

from __future__ import annotations

from collections import Counter
from math import isqrt


A = (3, 9, 27, 33, 51, 69, 81, 84, 87, 99)
B = (2, 5, 14, 17, 26, 41, 44, 50, 53, 65, 77, 80, 98)
EXPECTED = {
    1_000: (118, 113, 93, 20, 153),
    10_000: (1_591, 1_350, 1_188, 162, 1_688),
    100_000: (20_391, 17_905, 15_367, 2_538, 23_265),
}


def closure(limit: int) -> bytearray:
    """Ascending recurrence using direct factor-pair trials, without an SPF sieve."""
    member = bytearray(limit + 1)
    member[2] = member[3] = 1
    for n in range(4, limit + 1):
        product = n + 1
        for divisor in range(2, isqrt(product) + 1):
            if product % divisor:
                continue
            quotient = product // divisor
            if divisor < quotient and member[divisor] and member[quotient]:
                member[n] = 1
                break
    assert not member[8] and not member[24]
    return member


def main() -> None:
    limit = max(EXPECTED)
    member = closure(limit // 2)
    g0 = [n for n, present in enumerate(member) if present and n % 3 == 0]
    g2 = [n for n, present in enumerate(member) if present and n % 3 == 2]
    support = {
        a * b
        for a in g0
        for b in g2
        if a * b <= limit
    }

    rows: dict[int, tuple[int, int, int, int, int]] = {}
    for x in EXPECTED:
        q = sum(n <= x for n in support)
        images = Counter()
        for n in support:
            for a in A:
                image = a * (n - 1)
                if image <= x:
                    images[image] += 1
            for b in B:
                image = b * (2 * n - 3)
                if image <= x:
                    images[image] += 1
        mass = sum(images.values())
        union_size = len(images)
        collision_tax = mass - union_size
        energy = sum(value * value for value in images.values())
        rows[x] = (q, mass, union_size, collision_tax, energy)

    assert rows == EXPECTED, (rows, EXPECTED)
    print("independent_algorithm=trial_divisors_plus_Counter")
    for x, row in rows.items():
        print(f"X={x} Q={row[0]} M={row[1]} U={row[2]} Delta={row[3]} E_aff={row[4]}")
    print("matches_C07=true")


if __name__ == "__main__":
    main()
