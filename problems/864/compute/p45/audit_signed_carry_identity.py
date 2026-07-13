#!/usr/bin/env python3
"""Audit the exact signed carry identities and four-set moments from P45."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


def is_integer_sidon(values: list[int]) -> bool:
    sums: set[int] = set()
    for i, left in enumerate(values):
        for right in values[i:]:
            if left + right in sums:
                return False
            sums.add(left + right)
    return True


def carry_profile(values: list[int], h: int, b: int) -> dict:
    values = sorted(values)
    p = len(values)
    if not values or values[0] < 0 or values[-1] >= h:
        raise AssertionError("B is not contained in [0,h-1]")
    if not is_integer_sidon(values):
        raise AssertionError("B is not Sidon in the integers")

    sum_weights: dict[int, int] = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            sum_weights[left + right] = 1 if left == right else 2
    sums = set(sum_weights)
    differences = {left - right for left in values for right in values}
    if any(-b - total_sum in differences for total_sum in sums):
        raise AssertionError("-b lies in 3B-B")

    sum_fibers: dict[int, list[int]] = defaultdict(list)
    difference_fibers: dict[int, list[int]] = defaultdict(list)
    for value in sums:
        sum_fibers[value % h].append(value)
    for value in differences:
        difference_fibers[value % h].append(value)
    for fiber in (*sum_fibers.values(), *difference_fibers.values()):
        fiber.sort()

    sum_support = set(sum_fibers)
    shifted_difference_support = {
        (-b - residue) % h for residue in difference_fibers
    }
    overlap = sum_support & shifted_difference_support
    holes = set(range(h)) - (sum_support | shifted_difference_support)

    doubled_sums = {
        residue for residue, fiber in sum_fibers.items() if len(fiber) == 2
    }
    doubled_differences = {
        (-b - residue) % h
        for residue, fiber in difference_fibers.items()
        if len(fiber) == 2
    }
    if doubled_sums & doubled_differences:
        raise AssertionError("forbidden double-double carry fiber")

    carry_layers: dict[int, set[int]] = defaultdict(set)
    literal_counts: Counter[int] = Counter()
    ordered_counts: Counter[int] = Counter()
    residue_moments: Counter[int] = Counter()
    diagonal_counts: Counter[int] = Counter()
    zero_difference_weights: dict[int, int] = {}
    for total_sum in sums:
        for layer in (0, 1, 2, 3):
            difference = layer * h - b - total_sum
            if difference not in differences:
                continue
            residue = total_sum % h
            carry_layers[residue].add(layer)
            literal_counts[layer] += 1
            residue_moments[layer] += residue
            sum_weight = sum_weights[total_sum]
            ordered_counts[layer] += sum_weight * (p if difference == 0 else 1)
            if sum_weight == 1:
                diagonal_counts[layer] += 1
            if difference == 0:
                zero_difference_weights[layer] = sum_weight

    if literal_counts[0] or literal_counts[3]:
        raise AssertionError("unexpected carry outside levels 1 and 2")
    if set(carry_layers) != overlap:
        raise AssertionError("carry residues do not equal support overlap")
    allowed_profiles = ({1}, {2}, {1, 2})
    if any(layers not in allowed_profiles for layers in carry_layers.values()):
        raise AssertionError("unexpected carry-layer profile")

    split = Counter(tuple(sorted(carry_layers[residue])) for residue in overlap)
    sum_inside = doubled_sums & shifted_difference_support
    sum_outside = doubled_sums - shifted_difference_support
    difference_inside = doubled_differences & sum_support
    difference_outside = doubled_differences - sum_support

    fold_types: Counter[str] = Counter()
    weighted_sum_folds = 0
    for fiber in sum_fibers.values():
        if len(fiber) != 2:
            continue
        weights = sorted(sum_weights[value] for value in fiber)
        fold_types[f"{weights[0]}x{weights[1]}"] += 1
        weighted_sum_folds += weights[0] * weights[1]

    a = len(sums) - len(sum_support)
    c = len(differences) - len(difference_fibers)
    delta = len(sums) + len(differences) - h
    both = split[(1, 2)]
    missed_doubles = len(sum_outside) + len(difference_outside)

    # Literal lift sets, all represented in [0,h-1].
    low_sums = {value for value in sums if value < h}
    high_sums = {value - h for value in sums if value >= h}
    positive_differences = {value for value in differences if value >= 0}
    negative_differences = {value + h for value in differences if value < 0}

    def transform(residue: int) -> int:
        return (-b - residue) % h

    def transform_set(residues: set[int]) -> set[int]:
        return {transform(residue) for residue in residues}

    lp = low_sums & transform_set(positive_differences)
    ln = low_sums & transform_set(negative_differences)
    hp = high_sums & transform_set(positive_differences)
    hn = high_sums & transform_set(negative_differences)

    boundary_residue = h - 1
    boundary = {boundary_residue} if b == 2 else set()
    epsilon_p = int(boundary_residue in lp and b == 2)
    epsilon_n = int(boundary_residue in ln and b == 2)
    lp_nonboundary = lp - boundary
    ln_boundary = ln & boundary
    lp_boundary = lp & boundary

    four_m1 = len(lp_nonboundary) + len(hn) + len(ln_boundary)
    four_m2 = len(hp) + len(lp_boundary)
    j1 = sum(lp_nonboundary) + sum(hn) + sum(ln_boundary)
    j2 = sum(hp) + sum(lp_boundary)
    k1 = (
        sum(transform(residue) for residue in lp_nonboundary)
        + sum(transform(residue) for residue in hn)
        + sum(transform(residue) for residue in ln_boundary)
    )
    k2 = (
        sum(transform(residue) for residue in hp)
        + sum(transform(residue) for residue in lp_boundary)
    )
    centered_signed_moment_twice = (
        2 * (j1 - j2) - (h - 1) * (four_m1 - four_m2)
    )

    lift_law = True
    for sum_set, difference_set, high, negative in (
        (low_sums, positive_differences, 0, 0),
        (low_sums, negative_differences, 0, 1),
        (high_sums, positive_differences, 1, 0),
        (high_sums, negative_differences, 1, 1),
    ):
        for residue in sum_set & transform_set(difference_set):
            eta = int(b == 2 and residue == boundary_residue)
            layer = 1 + eta + high - negative
            total_sum = residue + high * h
            difference = transform(residue) - negative * h
            lift_law &= total_sum + difference == layer * h - b

    assertions = {
        "sum_cardinality": len(sums) == p * (p + 1) // 2,
        "difference_cardinality": len(differences) == p * (p - 1) + 1,
        "energy_identity": c == weighted_sum_folds,
        "both_identity": both == len(sum_inside) + len(difference_inside),
        "carry_count_from_split": (
            literal_counts[1] == split[(1,)] + both
            and literal_counts[2] == split[(2,)] + both
        ),
        "delta_identity": delta
        == literal_counts[1] + literal_counts[2] - len(holes) + missed_doubles,
        "four_set_sum_defect": a == len(low_sums & high_sums),
        "four_set_difference_defect": c
        == len(positive_differences & negative_differences),
        "four_set_carry_zero": not (ln - boundary) and len(ln) == epsilon_n,
        "four_set_carry_counts": (four_m1, four_m2)
        == (literal_counts[1], literal_counts[2]),
        "four_set_sum_moments": (j1, j2)
        == (residue_moments[1], residue_moments[2]),
        "four_set_residue_moment_relation": (
            j1 + k1 == (h - b) * four_m1 + h * epsilon_n
            and j2 + k2 == (h - b) * four_m2 + h * epsilon_p
        ),
        "four_set_lift_law": lift_law,
    }
    for layer in (1, 2):
        expected = (
            2 * literal_counts[layer]
            - diagonal_counts[layer]
            + (p - 1) * zero_difference_weights.get(layer, 0)
        )
        assertions[f"ordered_count_layer_{layer}"] = ordered_counts[layer] == expected
    if not all(assertions.values()):
        raise AssertionError(assertions)

    return {
        "B": values,
        "p": p,
        "h": h,
        "b": b,
        "sum_size": len(sums),
        "difference_size": len(differences),
        "a": a,
        "c": c,
        "delta": delta,
        "overlap": len(overlap),
        "double_holes": len(holes),
        "carry1_only": split[(1,)],
        "carry2_only": split[(2,)],
        "both": both,
        "M1": literal_counts[1],
        "M2": literal_counts[2],
        "Q1": ordered_counts[1],
        "Q2": ordered_counts[2],
        "J1": j1,
        "J2": j2,
        "K1": k1,
        "K2": k2,
        "centered_signed_moment_twice": centered_signed_moment_twice,
        "boundary_epsilon_P": epsilon_p,
        "boundary_epsilon_N": epsilon_n,
        "four_set_sizes": {
            "L": len(low_sums),
            "H": len(high_sums),
            "P": len(positive_differences),
            "N": len(negative_differences),
            "L_inter_TP": len(lp),
            "L_inter_TN": len(ln),
            "H_inter_TP": len(hp),
            "H_inter_TN": len(hn),
        },
        "four_set_moments": {
            "L_inter_TP": sum(lp),
            "L_inter_TN": sum(ln),
            "H_inter_TP": sum(hp),
            "H_inter_TN": sum(hn),
        },
        "diagonal_solution_counts": {
            "1": diagonal_counts[1],
            "2": diagonal_counts[2],
        },
        "zero_difference_sum_weights": {
            str(layer): weight
            for layer, weight in sorted(zero_difference_weights.items())
        },
        "sum_doubles_inside": len(sum_inside),
        "sum_doubles_outside": len(sum_outside),
        "difference_doubles_inside": len(difference_inside),
        "difference_doubles_outside": len(difference_outside),
        "sum_fold_types": dict(sorted(fold_types.items())),
        "assertions": assertions,
    }


def reflected_parameters(row: dict) -> tuple[list[int], int, int] | None:
    reflected_set = sorted(row["A"])
    size = len(reflected_set)
    sigma = int(row.get("exceptional_sum") or 0)
    multiplicity = int(row.get("exceptional_multiplicity") or 0)
    if size % 2 or sigma <= 0 or multiplicity != size // 2:
        return None
    reflected_support = set(reflected_set)
    if any(sigma - value not in reflected_support for value in reflected_set):
        return None
    lower_half = [value for value in reflected_set if 2 * value < sigma]
    if len(lower_half) != size // 2:
        return None

    top = max(lower_half)
    ruler = sorted(top - value for value in lower_half)
    gap = sigma - 2 * top
    b = 1 if gap % 2 else 2
    shift = (gap - b) // 2
    h = shift + ruler[-1] + 1
    return [shift + value for value in ruler], h, b


def exact_ratio(numerator: int, denominator: int) -> dict:
    ratio = Fraction(numerator, denominator)
    return {
        "numerator": ratio.numerator,
        "denominator": ratio.denominator,
        "decimal": float(ratio),
    }


def normalized_ranges(profiles: list[dict]) -> dict:
    metrics = {
        "overlap_over_p2": (
            lambda row: row["overlap"],
            lambda row: row["p"] ** 2,
        ),
        "signed_count_over_p2": (
            lambda row: abs(row["M1"] - row["M2"]),
            lambda row: row["p"] ** 2,
        ),
        "sum_residue_moment_over_h_p2": (
            lambda row: abs(row["J1"] - row["J2"]),
            lambda row: row["h"] * row["p"] ** 2,
        ),
        "difference_residue_moment_over_h_p2": (
            lambda row: abs(row["K1"] - row["K2"]),
            lambda row: row["h"] * row["p"] ** 2,
        ),
        "centered_sum_moment_over_h_p2": (
            lambda row: abs(row["centered_signed_moment_twice"]),
            lambda row: 2 * row["h"] * row["p"] ** 2,
        ),
    }
    result = {}
    for name, (numerator, denominator) in metrics.items():
        ranked = sorted(
            profiles,
            key=lambda row: Fraction(numerator(row), denominator(row)),
        )
        endpoints = {}
        for label, row in (("min", ranked[0]), ("max", ranked[-1])):
            endpoints[label] = {
                "sample_id": row["sample_id"],
                "p": row["p"],
                "ratio": exact_ratio(numerator(row), denominator(row)),
            }
        result[name] = endpoints
    return result


def load_source(source: Path) -> tuple[dict, list[dict]]:
    p168 = None
    large_profiles = []
    with source.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            parameters = reflected_parameters(row)
            if parameters is None:
                continue
            report = carry_profile(*parameters)
            if row.get("sample_id") == "singer-801ada713888":
                p168 = report
            if report["p"] >= 72 and report["delta"] > 0:
                large_profiles.append(
                    {
                        "sample_id": row["sample_id"],
                        "p": report["p"],
                        "h": report["h"],
                        "b": report["b"],
                        "delta": report["delta"],
                        "overlap": report["overlap"],
                        "M1": report["M1"],
                        "M2": report["M2"],
                        "J1": report["J1"],
                        "J2": report["J2"],
                        "K1": report["K1"],
                        "K2": report["K2"],
                        "centered_signed_moment_twice": report[
                            "centered_signed_moment_twice"
                        ],
                        "boundary_epsilon_P": report["boundary_epsilon_P"],
                        "boundary_epsilon_N": report["boundary_epsilon_N"],
                    }
                )
    if p168 is None:
        raise AssertionError("p=168 source row not found")
    large_profiles.sort(key=lambda row: (row["p"], row["sample_id"]))
    if len(large_profiles) != 37:
        raise AssertionError(f"expected 37 large profiles, got {len(large_profiles)}")
    return p168, large_profiles


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("problems/864/compute/p20/results/samples.jsonl"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p45/audit_signed_carry_identity.json"),
    )
    args = parser.parse_args()

    p168, large_profiles = load_source(args.source)
    twin_m2 = carry_profile([2, 4, 5], 6, 2)
    twin_m1 = carry_profile([2, 3, 5], 6, 2)
    boundary_p = carry_profile([0, 3], 4, 2)
    large_audit = {
        "filters": {"p_at_least": 72, "delta_positive": True},
        "count": len(large_profiles),
        "boundary_event_totals": {
            "epsilon_P": sum(row["boundary_epsilon_P"] for row in large_profiles),
            "epsilon_N": sum(row["boundary_epsilon_N"] for row in large_profiles),
        },
        "normalized_ranges": normalized_ranges(large_profiles),
        "profiles": large_profiles,
    }
    reports = {
        "p168": p168,
        "signed_twin_M2_heavy": twin_m2,
        "signed_twin_M1_heavy": twin_m1,
        "boundary_P_example": boundary_p,
        "large_profile_audit": large_audit,
    }
    args.output.write_text(json.dumps(reports, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "p168": {
                    key: p168[key]
                    for key in (
                        "p",
                        "h",
                        "b",
                        "delta",
                        "M1",
                        "M2",
                        "J1",
                        "J2",
                        "K1",
                        "K2",
                    )
                },
                "large_profile_count": len(large_profiles),
                "normalized_ranges": large_audit["normalized_ranges"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

