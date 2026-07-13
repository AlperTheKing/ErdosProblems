"""Exact residue-gate audit for P34.

For an even modulus m, enumerate R contained in the odd residues of Z/mZ
with R disjoint from R+R+R.  The audit records whether R is contained in a
proper congruence class beyond parity and the asymptotic pair-sum capacity
for equal-size modular fibers over R.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path


def three_free(residues: tuple[int, ...], modulus: int) -> bool:
    residue_set = set(residues)
    pair_sums = {(a + b) % modulus for a in residues for b in residues}
    return all((s + c) % modulus not in residue_set for s in pair_sums for c in residues)


def congruence_gcd(residues: tuple[int, ...], modulus: int) -> int:
    base = residues[0]
    value = modulus
    for residue in residues[1:]:
        value = math.gcd(value, residue - base)
    return value


def ordered_sum_profile(residues: tuple[int, ...], modulus: int) -> tuple[int, ...]:
    counts = [0] * modulus
    for a in residues:
        for b in residues:
            counts[(a + b) % modulus] += 1
    return tuple(counts)


def row_for(residues: tuple[int, ...], modulus: int) -> dict[str, object]:
    size = len(residues)
    divisor = congruence_gcd(residues, modulus)
    profile = ordered_sum_profile(residues, modulus)
    peak = max(profile)
    coefficient = Fraction(modulus * peak, 2 * size * size)
    return {
        "modulus": modulus,
        "R": list(residues),
        "size": size,
        "congruence_gcd": divisor,
        "primitive_beyond_parity": divisor == 2,
        "coarse_coset_alone_blocks_3R": (2 * residues[0]) % divisor != 0,
        "ordered_pair_peak": peak,
        "pair_support": sum(value > 0 for value in profile),
        "balanced_modular_fiber_lower_coefficient": str(coefficient),
        "balanced_modular_fiber_lower_float": float(coefficient),
    }


def enumerate_modulus(modulus: int) -> dict[str, object]:
    odds = tuple(range(1, modulus, 2))
    valid: list[dict[str, object]] = []
    for mask in range(1, 1 << len(odds)):
        residues = tuple(odds[index] for index in range(len(odds)) if mask >> index & 1)
        if three_free(residues, modulus):
            valid.append(row_for(residues, modulus))

    if not valid:
        return {
            "modulus": modulus,
            "valid_count": 0,
            "maximum_size": 0,
            "maximum_examples": [],
            "primitive_count": 0,
            "best_primitive_examples": [],
        }

    max_size = max(row["size"] for row in valid)
    maximum = [row for row in valid if row["size"] == max_size]
    primitive = [row for row in valid if row["primitive_beyond_parity"]]
    best_primitive: list[dict[str, object]] = []
    if primitive:
        best_value = min(Fraction(row["balanced_modular_fiber_lower_coefficient"]) for row in primitive)
        best_primitive = [
            row
            for row in primitive
            if Fraction(row["balanced_modular_fiber_lower_coefficient"]) == best_value
        ]

    return {
        "modulus": modulus,
        "valid_count": len(valid),
        "maximum_size": max_size,
        "maximum_examples": maximum[:8],
        "primitive_count": len(primitive),
        "best_primitive_examples": best_primitive[:8],
    }


def audit(max_modulus: int) -> dict[str, object]:
    if max_modulus < 2:
        raise ValueError("max_modulus must be at least 2")
    rows = [enumerate_modulus(modulus) for modulus in range(2, max_modulus + 1, 2)]

    # Literal regression witnesses: the first collapses to one class mod 6;
    # the second genuinely uses both odd classes modulo 4.
    assert three_free((1, 7), 12)
    assert congruence_gcd((1, 7), 12) == 6
    assert three_free((1, 7), 16)
    assert congruence_gcd((1, 7), 16) == 2

    primitive_rows = [
        example
        for row in rows
        for example in row["best_primitive_examples"]
    ]
    global_best: list[dict[str, object]] = []
    if primitive_rows:
        value = min(
            Fraction(row["balanced_modular_fiber_lower_coefficient"])
            for row in primitive_rows
        )
        global_best = [
            row
            for row in primitive_rows
            if Fraction(row["balanced_modular_fiber_lower_coefficient"]) == value
        ]

    return {
        "max_modulus": max_modulus,
        "total_nonempty_subsets": sum(
            (1 << (modulus // 2)) - 1
            for modulus in range(2, max_modulus + 1, 2)
        ),
        "moduli": rows,
        "global_best_primitive_examples": global_best,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-modulus", type=int, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = audit(args.max_modulus)
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "max_modulus": report["max_modulus"],
                "global_best_primitive_examples": report["global_best_primitive_examples"],
                "per_modulus": [
                    {
                        "modulus": row["modulus"],
                        "valid_count": row["valid_count"],
                        "maximum_size": row["maximum_size"],
                        "primitive_count": row["primitive_count"],
                    }
                    for row in report["moduli"]
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()


