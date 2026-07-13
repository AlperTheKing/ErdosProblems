#!/usr/bin/env python3
"""Audit a C14 result with exact rational arithmetic and C00 support counts."""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path


A = (3, 9, 27, 33, 51, 69, 81, 84, 87, 99)
B = (2, 5, 14, 17, 26, 41, 44, 50, 53, 65, 77, 80, 98)


def stored_fraction(value: dict[str, str]) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--hyperbola", type=Path, required=True)
    args = parser.parse_args()

    result = json.loads(args.result.read_text(encoding="ascii"))
    hyperbola = json.loads(args.hyperbola.read_text(encoding="ascii"))
    w = sum((Fraction(1, a) for a in A), start=Fraction())
    w += sum((Fraction(1, 2 * b) for b in B), start=Fraction())
    assert w == Fraction(
        int(result["W"]["numerator"]),
        int(result["W"]["denominator"]),
    )
    threshold = 1 - 1 / w
    assert threshold == stored_fraction(result["collision_threshold_1_minus_1_over_W"])

    support_by_x = {
        row["X"]: row["distinct_products"]
        for row in hyperbola["checkpoints"]
    }
    pairs_by_x = {
        row["X"]: row["pairs"]
        for row in hyperbola["checkpoints"]
    }
    checked = 0
    for row in result["checkpoints"]:
        x = row["X"]
        mass = row["parent_mass_M"]
        union_size = row["union_U"]
        delta = row["collision_tax_Delta"]
        energy = int(row["affine_energy_sum_r2"])
        assert row["Q"] == support_by_x[x]
        assert delta == mass - union_size
        assert stored_fraction(row["affine_energy_over_M"]) == Fraction(energy, mass)
        assert stored_fraction(row["affine_energy_over_M_minus_W"]) == Fraction(energy, mass) - w
        assert stored_fraction(row["Delta_over_M"]) == Fraction(delta, mass)
        assert (
            stored_fraction(row["Delta_over_M_minus_1_minus_1_over_W"])
            == Fraction(delta, mass) - threshold
        )
        checked += 1

    limit = result["limit"]
    assert result["cross_color_pair_count_to_limit"] == pairs_by_x[limit]
    print(f"checkpoints_audited={checked}")
    print("Q_matches_C00=true")
    print("cross_color_pair_count_matches_C00=true")
    print("all_exact_rational_fields_recomputed=true")


if __name__ == "__main__":
    main()
