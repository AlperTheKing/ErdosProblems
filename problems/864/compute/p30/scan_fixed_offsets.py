"""Scan explicit top-layer centers over every natural Ruzsa cut.

For each prime p, exponential cut coordinate e, and rational alpha, test

    M = 2*p*(p-1) + floor(alpha*p*(p-1))

against the exact integer support S(B)+Delta+(B).  Diagonal pair sums are
included.  No affine multipliers or Singer sets are scanned.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

from scan_canonical_cuts import crt_coordinate, primitive_root, selected_primes


DEFAULT_OFFSETS = ("1/2", "3/5", "2/3", "7/10", "3/4", "4/5")


def parse_fraction(text: str) -> Fraction:
    value = Fraction(text)
    if not 0 <= value < 1:
        raise argparse.ArgumentTypeError("offset must lie in [0,1)")
    return value


def cut_points(p: int, g: int, e: int) -> tuple[int, ...]:
    points: list[int] = []
    power = 1
    for index in range(p - 1):
        exponential = (e * (power - 1)) % p
        points.append(crt_coordinate(index, exponential, p))
        power = (power * g) % p
    return tuple(sorted(points))


def supports(points: tuple[int, ...]) -> tuple[set[int], set[int]]:
    size = len(points)
    sums = {
        points[i] + points[j]
        for i in range(size)
        for j in range(i, size)
    }
    differences = {
        points[j] - points[i]
        for i in range(size)
        for j in range(i + 1, size)
    }
    if len(sums) != size * (size + 1) // 2:
        raise AssertionError("literal unordered-sum collision")
    if len(differences) != size * (size - 1) // 2:
        raise AssertionError("positive-difference collision")
    return sums, differences


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prime-min", type=int, default=5)
    parser.add_argument("--prime-max", type=int, default=257)
    parser.add_argument(
        "--offsets",
        type=parse_fraction,
        nargs="+",
        default=[parse_fraction(x) for x in DEFAULT_OFFSETS],
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    records: list[dict[str, object]] = []
    for p in selected_primes(args.prime_min, args.prime_max):
        g = primitive_root(p)
        modulus = p * (p - 1)
        centers = {
            str(alpha): 2 * modulus + (alpha.numerator * modulus) // alpha.denominator
            for alpha in args.offsets
        }
        hole_coordinates = {str(alpha): [] for alpha in args.offsets}

        for e in range(1, p):
            points = cut_points(p, g, e)
            sums, differences = supports(points)
            for label, center in centers.items():
                hit = any(center - pair_sum in differences for pair_sum in sums)
                if not hit:
                    if center <= 2 * points[-1]:
                        raise AssertionError((p, e, center, points[-1]))
                    hole_coordinates[label].append(e)

        row = {
            "p": p,
            "primitive_root": g,
            "modulus": modulus,
            "size": p - 1,
            "offsets": {
                label: {
                    "center": centers[label],
                    "center_over_size2": str(
                        Fraction(centers[label], (p - 1) * (p - 1))
                    ),
                    "hole_cut_count": len(hole_coordinates[label]),
                    "first_hole_exponential": (
                        hole_coordinates[label][0] if hole_coordinates[label] else None
                    ),
                    "hole_exponentials": hole_coordinates[label],
                }
                for label in centers
            },
        }
        records.append(row)
        counts = " ".join(
            f"{label}:{len(hole_coordinates[label])}" for label in centers
        )
        print(f"p={p} {counts}")

    payload = {
        "prime_min": args.prime_min,
        "prime_max": args.prime_max,
        "records": records,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="ascii",
        )


if __name__ == "__main__":
    main()
