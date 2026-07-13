#!/usr/bin/env python3
"""Exact audit of the GPT-Pro correction delta -> positive part."""

from __future__ import annotations

import json
from collections import Counter
from math import isqrt
from pathlib import Path


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    return all(n % d for d in range(2, isqrt(n) + 1))


def audit(q: int) -> dict[str, object]:
    if q % 2 == 0 or not is_prime(q):
        raise ValueError("q must be an odd prime")
    z = [2 * q * i + (i * i) % q for i in range(q)]
    assert z == sorted(z) and len(set(z)) == q and z[0] == 0
    width = z[-1]
    assert width == 2 * q * q - 2 * q + 1

    sum_reps = Counter(z[i] + z[j] for i in range(q) for j in range(i, q))
    assert len(sum_reps) == q * (q + 1) // 2
    assert max(sum_reps.values()) == 1

    gap = width + 1
    e = [gap + 2 * value for value in z]
    e_sums = Counter(e[i] + e[j] for i in range(q) for j in range(i, q))
    assert max(e_sums.values()) == 1
    triples = {a + b + c for a in e for b in e for c in e}
    assert not (set(e) & triples)
    assert max(e) < 3 * min(e)

    b = 2
    gamma = q * q - q
    h = gamma + width + 1
    delta_twice = 3 * q * q - q + 2 - 2 * h
    assert max(e) == 3 * q * q - q + b - delta_twice
    assert delta_twice == -3 * q * q + 5 * q - 2
    return {
        "q": q,
        "p": q,
        "Z": z,
        "E": e,
        "W": width,
        "G": gap,
        "h": h,
        "delta_numerator": delta_twice,
        "delta_denominator": 2,
        "delta_positive_part_numerator": max(delta_twice, 0),
        "delta_positive_part_denominator": 2,
        "max_E": max(e),
        "max_E_minus_3p2": max(e) - 3 * q * q,
    }


def main() -> None:
    reports = [audit(q) for q in (3, 5, 7, 11, 13, 17, 19, 23, 29, 31)]
    output = Path("problems/864/compute/p54/audit_delta_positive_part.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(reports, indent=2) + "\n", encoding="ascii")
    print(json.dumps({"primes": len(reports), "last": reports[-1]}, indent=2))


if __name__ == "__main__":
    main()
