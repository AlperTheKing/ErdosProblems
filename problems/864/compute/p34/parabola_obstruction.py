"""Exact finite-field parabola obstruction for P34.

For every odd prime q, S={(x,x^2): x in F_q} is Sidon, including diagonal
sums, but 3S-S is the whole plane.  Therefore every affine image and every
translate of S meets its own threefold sumset.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


Point = tuple[int, int]


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    for divisor in range(2, int(value**0.5) + 1):
        if value % divisor == 0:
            return False
    return True


def add(left: Point, right: Point, q: int) -> Point:
    return ((left[0] + right[0]) % q, (left[1] + right[1]) % q)


def scale(coefficient: int, point: Point, q: int) -> Point:
    return (coefficient * point[0] % q, coefficient * point[1] % q)


def parabola(value: int, q: int) -> Point:
    return (value % q, value * value % q)


def coverage_witness(target: Point, q: int) -> tuple[int, int, int, int]:
    """Return a,b,c,x with P(a)+P(b)+P(c)-P(x)=target."""

    u, v = target
    inverse_two = pow(2, -1, q)
    product = (u * u - v) * inverse_two % q
    a = (u + 1) % q
    b = (u + product) % q
    c = 0
    x = (u + 1 + product) % q
    return a, b, c, x


def signed_combination(a: int, b: int, c: int, x: int, q: int) -> Point:
    total = add(add(parabola(a, q), parabola(b, q), q), parabola(c, q), q)
    return add(total, scale(-1, parabola(x, q), q), q)


def audit_prime(q: int) -> dict[str, int]:
    if q == 2 or not is_prime(q):
        raise ValueError("q must be an odd prime")

    pair_sums: dict[Point, tuple[int, int]] = {}
    for a in range(q):
        for b in range(a, q):
            value = add(parabola(a, q), parabola(b, q), q)
            if value in pair_sums:
                raise AssertionError((q, value, pair_sums[value], (a, b)))
            pair_sums[value] = (a, b)

    covered: set[Point] = set()
    translations_checked = 0
    for u in range(q):
        for v in range(q):
            target = (u, v)
            witness = coverage_witness(target, q)
            assert signed_combination(*witness, q) == target
            covered.add(target)

            translation = (u, v)
            obstruction_target = scale(-2, translation, q)
            a, b, c, x = coverage_witness(obstruction_target, q)
            left = add(parabola(x, q), translation, q)
            right = add(
                add(
                    add(parabola(a, q), translation, q),
                    add(parabola(b, q), translation, q),
                    q,
                ),
                add(parabola(c, q), translation, q),
                q,
            )
            assert left == right
            translations_checked += 1

    assert len(pair_sums) == q * (q + 1) // 2
    assert len(covered) == q * q
    return {
        "q": q,
        "pair_sums": len(pair_sums),
        "covered_targets": len(covered),
        "translations_checked": translations_checked,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-prime", type=int, default=43)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    reports = [
        audit_prime(q)
        for q in range(3, args.max_prime + 1, 2)
        if is_prime(q)
    ]
    result = {
        "max_prime": args.max_prime,
        "prime_count": len(reports),
        "reports": reports,
        "total_targets": sum(row["covered_targets"] for row in reports),
        "total_translations": sum(row["translations_checked"] for row in reports),
    }
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)


if __name__ == "__main__":
    main()
