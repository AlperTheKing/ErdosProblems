"""Exact Welch-Costas modular obstruction for P34."""

from __future__ import annotations

import argparse
import json
from itertools import combinations_with_replacement
from pathlib import Path


Point = tuple[int, int]


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    for divisor in range(2, int(value**0.5) + 1):
        if value % divisor == 0:
            return False
    return True


def primitive_root(q: int) -> int:
    target = set(range(1, q))
    for candidate in range(2, q):
        if {pow(candidate, exponent, q) for exponent in range(q - 1)} == target:
            return candidate
    raise AssertionError(f"no primitive root modulo {q}")


def add(left: Point, right: Point, n: int, q: int) -> Point:
    return ((left[0] + right[0]) % n, (left[1] + right[1]) % q)


def subtract(left: Point, right: Point, n: int, q: int) -> Point:
    return ((left[0] - right[0]) % n, (left[1] - right[1]) % q)


def audit_prime(q: int) -> dict[str, int]:
    if q <= 3 or not is_prime(q):
        raise ValueError("q must be a prime greater than 3")

    n = q - 1
    generator = primitive_root(q)
    welch = tuple((index, pow(generator, index, q)) for index in range(n))

    pair_sums: dict[Point, tuple[int, int]] = {}
    for i, j in combinations_with_replacement(range(n), 2):
        value = add(welch[i], welch[j], n, q)
        if value in pair_sums:
            raise AssertionError((q, value, pair_sums[value], (i, j)))
        pair_sums[value] = (i, j)

    differences = {
        subtract(left, right, n, q)
        for left in welch
        for right in welch
    }
    assert len(pair_sums) == n * (n + 1) // 2
    assert len(differences) == n * (n - 1) + 1

    coverage = {
        add(pair_sum, difference, n, q)
        for pair_sum in pair_sums
        for difference in differences
    }
    assert len(coverage) == n * q

    threshold_twice = 3 * n * n - n + 2
    group_order_twice = 2 * n * q
    assert group_order_twice < threshold_twice

    return {
        "q": q,
        "order": n * q,
        "size": n,
        "generator": generator,
        "pair_sums": len(pair_sums),
        "differences": len(differences),
        "covered_targets": len(coverage),
        "threshold_margin_twice": threshold_twice - group_order_twice,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-prime", type=int, default=43)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    reports = [
        audit_prime(q)
        for q in range(5, args.max_prime + 1, 2)
        if is_prime(q)
    ]
    result = {
        "max_prime": args.max_prime,
        "prime_count": len(reports),
        "reports": reports,
        "total_targets": sum(row["covered_targets"] for row in reports),
    }
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)


if __name__ == "__main__":
    main()
