#!/usr/bin/env python3
"""Independent exact verifier for B05 periodic composition-cover certificates."""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from math import gcd, lcm
from pathlib import Path


EXPECTED_D = (2, 3, 5, 9, 14, 17, 26, 27, 33, 41, 44, 50, 51, 53, 65, 69, 77, 80, 81, 84)


def evaluate_word(word: list[int]) -> tuple[int, int]:
    slope, intercept = 1, 0
    for d in word:
        if d not in EXPECTED_D:
            raise ValueError(f"word letter {d} is not in D")
        slope, intercept = d * slope, d * intercept + d - 2
    if not word:
        raise ValueError("identity map is not allowed")
    return slope, intercept


def verify(data: dict) -> dict[str, int | str]:
    if tuple(data["D"]) != EXPECTED_D:
        raise ValueError("certificate D does not equal the fixed twenty-element set")
    if data.get("coordinate") != "u=x-1":
        raise ValueError("unexpected coordinate")

    q = int(data["domain"]["modulus"])
    residues = tuple(sorted(set(map(int, data["domain"]["residues"]))))
    if q < 1 or not residues or residues[0] < 0 or residues[-1] >= q:
        raise ValueError("invalid periodic domain")
    residue_set = set(residues)

    maps: list[tuple[int, int, list[int]]] = []
    for item in data["maps"]:
        word = list(map(int, item["word_application_order"]))
        slope, intercept = evaluate_word(word)
        if (slope, intercept) != (int(item["slope"]), int(item["intercept"])):
            raise ValueError(f"incorrect affine coefficients for word {word}")
        if any((slope * r + intercept) % q not in residue_set for r in residues):
            raise ValueError(f"map {word} does not preserve the domain")
        maps.append((slope, intercept, word))

    if not maps:
        raise ValueError("empty map family")
    reciprocal_sum = sum((Fraction(1, slope) for slope, _, _ in maps), Fraction())
    if reciprocal_sum != 1:
        raise ValueError(f"reciprocal slope sum is {reciprocal_sum}, not 1")

    for i, (a, b, word_i) in enumerate(maps):
        for c, d, word_j in maps[i + 1 :]:
            common_modulus = q * gcd(a, c)
            for r in residues:
                left = a * r + b
                for s in residues:
                    right = c * s + d
                    if (left - right) % common_modulus == 0:
                        raise ValueError(
                            f"images of {word_i} and {word_j} intersect "
                            f"from domain residues {r},{s}"
                        )

    seed = data["safe_seed"]
    x0, u0 = int(seed["x0"]), int(seed["u0"])
    x, y = map(int, seed["witness"])
    if x not in EXPECTED_D or y not in EXPECTED_D or x == y:
        raise ValueError("seed witness must be two distinct elements of D")
    if x0 != x * y - 1 or u0 != x0 - 1 or x0 <= max(EXPECTED_D):
        raise ValueError("safe seed identity or size check failed")
    if u0 % q not in residue_set:
        raise ValueError("safe seed is outside the periodic domain")

    period = q
    for slope, _, _ in maps:
        period = lcm(period, q * slope)
    if period <= 2_000_000:
        target = {n for n in range(period) if n % q in residue_set}
        images: list[set[int]] = []
        for slope, intercept, _ in maps:
            image = {
                (slope * n + intercept) % period
                for n in range(period)
                if n % q in residue_set
            }
            images.append(image)
        union: set[int] = set()
        for image in images:
            if union & image:
                raise ValueError("finite-period replay found overlapping images")
            union |= image
        if union != target:
            raise ValueError("finite-period replay does not cover the domain")
        replay = period
    else:
        replay = "skipped-period-too-large"

    return {
        "maps": len(maps),
        "modulus": q,
        "residue_count": len(residues),
        "safe_seed": x0,
        "finite_replay_period": replay,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    data = json.loads(args.certificate.read_text(encoding="ascii"))
    print(json.dumps(verify(data), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
