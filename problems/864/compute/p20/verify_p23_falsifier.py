"""Audit the apparent P23 falsifier to the P20 candidate C20.

P23 stores positive duplicate weight, while C20 uses the centered defect
duplicate_weight - missing_weight. The p=503 set fails only under the
wrong convention and satisfies C20 under the stated centered convention.
Only Python integer arithmetic is used.
"""

from __future__ import annotations

import json
from collections import Counter


P = 503


def prime_factors(n: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            factors.append(divisor)
            while n % divisor == 0:
                n //= divisor
        divisor += 1
    if n > 1:
        factors.append(n)
    return factors


def primitive_root(p: int) -> int:
    factors = prime_factors(p - 1)
    for g in range(2, p):
        if all(pow(g, (p - 1) // factor, p) != 1 for factor in factors):
            return g
    raise AssertionError("primitive root not found")


def ceil_two_thirds(n: int) -> int:
    target = n * n
    low, high = 1, n
    while low < high:
        middle = (low + high) // 2
        if middle**3 >= target:
            high = middle
        else:
            low = middle + 1
    return low


def main() -> None:
    p = P
    g = primitive_root(p)
    modulus = p * (p - 1)
    c = sorted(
        {
            (pow(g, x, p) + p * ((x - pow(g, x, p)) % (p - 1))) % modulus
            for x in range(1, p)
        }
    )
    assert len(c) == p - 1

    owners: dict[int, tuple[int, int]] = {}
    for x in c:
        for y in c:
            if x == y:
                continue
            difference = (x - y) % modulus
            assert difference not in owners
            owners[difference] = (x, y)

    b = [2 * x for x in c]
    sigma = 4 * (modulus - 1) + 1
    a = sorted(set(b) | {sigma - x for x in b})
    n = sigma + 1
    k = len(a)
    assert k == 2 * (p - 1)

    sums = Counter(
        a[i] + a[j] for i in range(k) for j in range(i, k)
    )
    repeated = sorted((value, count) for value, count in sums.items() if count > 1)
    assert repeated == [(sigma, p - 1)]

    h = ceil_two_thirds(n)
    assert (h - 1) ** 3 < n * n <= h**3
    m_h = h + sum(min(h, y - x) for x, y in zip(a, a[1:]))

    differences = Counter(
        a[j] - a[i] for i in range(k) for j in range(i + 1, k)
    )
    assert max(differences.values()) == 2
    duplicate_weight = sum(
        (h - difference) * (count - 1)
        for difference, count in differences.items()
        if difference < h
    )
    missing_weight = sum(
        h - difference
        for difference in range(1, h)
        if difference not in differences
    )
    z_h = duplicate_weight - missing_weight

    # Six times C20 after clearing the positive denominator N*H^2.
    left = 6 * m_h * (h * h + 2 * z_h)
    right = (
        8 * n * h * h
        + 9 * h**3
        + 9 * n * h * (k - 1)
    )
    centered_margin = left - right
    duplicate_only_left = 6 * m_h * (h * h + 2 * duplicate_weight)
    duplicate_only_margin = duplicate_only_left - right
    assert duplicate_only_margin > 0
    assert centered_margin < 0

    print(
        json.dumps(
            {
                "status": "P23_DOES_NOT_FALSIFY_C20",
                "prime": p,
                "primitive_root": g,
                "N": n,
                "k": k,
                "H": h,
                "M_H": m_h,
                "duplicate_weight": duplicate_weight,
                "missing_weight": missing_weight,
                "centered_Z_H": z_h,
                "duplicate_only_cleared_margin": duplicate_only_margin,
                "centered_cleared_margin": centered_margin,
                "exceptional_sum": sigma,
                "exceptional_multiplicity": p - 1,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
