"""Exact check of the canonical nonperiodic carry potential.

For T acting on nonnegative functions by

  (T f)(d) = (30/31) sum_{m*d'+q_m=d} f(d'),

the affine function phi(d)=d+28/59 satisfies T phi <= phi.  Equality
occurs exactly for d=28 mod 30, where all three inverse branches exist.

Consequently every fixed-count multiplicity obeys

  R_v(d) <= (59/28) * (31/30)^|v| * (d+28/59).

The script verifies the 30 symbolic residue inequalities and checks the
multiplicity corollary against every exact endpoint through word length 10.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


BRANCHES = ((2, 0, 0), (3, 1, 1), (5, 3, 2))
WEIGHT = Fraction(30, 31)
C = Fraction(28, 59)


def symbolic_residue_rows():
    rows = []
    for residue in range(30):
        active = [
            (multiplier, shift)
            for multiplier, shift, _ in BRANCHES
            if (residue - shift) % multiplier == 0
        ]
        slope = Fraction(1) - WEIGHT * sum(
            (Fraction(1, multiplier) for multiplier, _ in active),
            Fraction(0),
        )
        intercept = (
            C
            - WEIGHT * len(active) * C
            + WEIGHT
            * sum(
                (
                    Fraction(shift, multiplier)
                    for multiplier, shift in active
                ),
                Fraction(0),
            )
        )
        minimum_slack = slope * residue + intercept
        assert slope >= 0
        assert minimum_slack >= 0
        rows.append(
            {
                "residue": residue,
                "branches": [multiplier for multiplier, _ in active],
                "slack_slope": f"{slope.numerator}/{slope.denominator}",
                "slack_intercept": (
                    f"{intercept.numerator}/{intercept.denominator}"
                ),
                "slack_at_residue": (
                    f"{minimum_slack.numerator}/{minimum_slack.denominator}"
                ),
            }
        )
    return rows


def phi(value: int) -> Fraction:
    return Fraction(value) + C


def transfer(value: int) -> Fraction:
    result = Fraction(0)
    for multiplier, shift, _ in BRANCHES:
        if (value - shift) % multiplier == 0:
            parent = (value - shift) // multiplier
            if parent >= 0:
                result += WEIGHT * phi(parent)
    return result


def brute_layers(max_length: int):
    layers = [{(0, 0, 0): {0: 1}}]
    for _ in range(max_length):
        current = {}
        for counts, offsets in layers[-1].items():
            for multiplier, shift, index in BRANCHES:
                new_counts = list(counts)
                new_counts[index] += 1
                target = current.setdefault(tuple(new_counts), {})
                for offset, multiplicity in offsets.items():
                    image = multiplier * offset + shift
                    target[image] = target.get(image, 0) + multiplicity
        layers.append(current)
    return layers


def verify_multiplicity(max_length: int):
    layers = brute_layers(max_length)
    checks = 0
    equalities = 0
    worst_ratio = Fraction(0)
    subprobability_checks = 0
    largest_subprobability = Fraction(0)
    near_canonical = []
    for length, layer in enumerate(layers):
        scale = Fraction(59, 28) * Fraction(31, 30) ** length
        total_by_offset = {}
        for offsets in layer.values():
            for offset, multiplicity in offsets.items():
                bound = scale * phi(offset)
                assert multiplicity <= bound
                checks += 1
                equalities += Fraction(multiplicity) == bound
                worst_ratio = max(
                    worst_ratio, Fraction(multiplicity) / bound
                )
                total_by_offset[offset] = (
                    total_by_offset.get(offset, 0) + multiplicity
                )
        for offset, multiplicity in total_by_offset.items():
            probability = (
                Fraction(multiplicity)
                * WEIGHT**length
                * phi(0)
                / phi(offset)
            )
            assert probability <= 1
            subprobability_checks += 1
            largest_subprobability = max(
                largest_subprobability, probability
            )

        if length > 0:
            candidates = list(layer)
            target = (
                Fraction(15 * length, 31),
                Fraction(10 * length, 31),
                Fraction(6 * length, 31),
            )
            counts = min(
                candidates,
                key=lambda item: (
                    sum(
                        abs(Fraction(item[index]) - target[index])
                        for index in range(3)
                    ),
                    item,
                ),
            )
            maximum = max(layer[counts].values())
            normalized = (
                float(Fraction(maximum) * WEIGHT**length)
                * length**0.5
            )
            near_canonical.append(
                {
                    "length": length,
                    "counts": counts,
                    "max_multiplicity": maximum,
                    "sqrt_n_maxR_over_(31/30)^n": normalized,
                }
            )
    return {
        "endpoint_checks": checks,
        "equalities": equalities,
        "largest_exact_to_bound_ratio": float(worst_ratio),
        "largest_ratio_fraction": (
            f"{worst_ratio.numerator}/{worst_ratio.denominator}"
        ),
        "subprobability_checks": subprobability_checks,
        "largest_subprobability": float(largest_subprobability),
        "near_canonical_rows": near_canonical,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-limit", type=int, default=1_000_000)
    parser.add_argument("--word-length", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    residue_rows = symbolic_residue_rows()
    direct_checks = 0
    equality_values = []
    for value in range(args.check_limit + 1):
        slack = phi(value) - transfer(value)
        assert slack >= 0
        direct_checks += 1
        if slack == 0:
            equality_values.append(value)

    result = {
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "weight": "30/31",
        "potential": "d+28/59",
        "residue_rows": residue_rows,
        "symbolic_equalities": [
            row["residue"]
            for row in residue_rows
            if row["slack_slope"] == "0/1"
            and row["slack_intercept"] == "0/1"
        ],
        "direct_integer_checks": direct_checks,
        "first_equality_values": equality_values[:20],
        "multiplicity_check": verify_multiplicity(args.word_length),
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.output is not None:
        args.output.write_text(rendered + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
