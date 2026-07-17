#!/usr/bin/env python3
"""Attach exact log-power threshold certificates to a C104 raw census."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


EXPONENTS = ((11, 20, ".55"), (3, 5, ".60"), (13, 20, ".65"))
SERIES_TERMS = 24


def fraction_json(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def fraction_from_json(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def ln_ratio_bounds(numerator: int, denominator: int, terms: int) -> tuple[Fraction, Fraction]:
    if numerator < denominator or denominator <= 0:
        raise ValueError("ratio must be at least one")
    z = Fraction(numerator - denominator, numerator + denominator)
    if not 0 <= z <= Fraction(1, 3):
        raise AssertionError(("range reduction failed", numerator, denominator, z))
    partial = Fraction()
    power = z
    z_squared = z * z
    for j in range(terms):
        partial += power / (2 * j + 1)
        power *= z_squared
    lower = 2 * partial
    if z == 0:
        return lower, lower
    remainder_upper = 2 * power / ((2 * terms + 1) * (1 - z_squared))
    return lower, lower + remainder_upper


def ln_integer_bounds(n: int, terms: int = SERIES_TERMS) -> tuple[Fraction, Fraction]:
    if n < 1:
        raise ValueError("n must be positive")
    if n == 1:
        return Fraction(), Fraction()
    shift = n.bit_length() - 1
    power_two = 1 << shift
    ln2_lower, ln2_upper = ln_ratio_bounds(2, 1, terms)
    tail_lower, tail_upper = ln_ratio_bounds(n, power_two, terms)
    return shift * ln2_lower + tail_lower, shift * ln2_upper + tail_upper


def certified_log_power_floor(n: int, p: int, q: int) -> dict:
    lower, upper = ln_integer_bounds(n)
    lower_power = lower**p
    upper_power = upper**p
    d = 0
    while Fraction((d + 1) ** q) <= lower_power:
        d += 1
    lower_margin = lower_power - Fraction(d**q)
    upper_margin = Fraction((d + 1) ** q) - upper_power
    if lower_margin < 0 or upper_margin <= 0:
        raise AssertionError(("threshold not certified", n, p, q, d))
    return {
        "D": d,
        "statement": f"D=floor((ln X)^({p}/{q}))",
        "ln_lower": fraction_json(lower),
        "ln_upper": fraction_json(upper),
        "lower_comparison_verified": True,
        "upper_comparison_verified": True,
        "comparisons": [
            "D^q <= ln_lower^p",
            "ln_upper^p < (D+1)^q",
        ],
        "series_terms": SERIES_TERMS,
        "series_remainder_rule": "2*z^(2T+1)/((2T+1)*(1-z^2)) after power update",
    }


def endpoint_bin_statistics(row: dict, d: int) -> dict:
    prefix = 0
    maximum_bin = Fraction()
    maximum_prefix = Fraction()
    maximum_bin_j = None
    maximum_prefix_j = None
    for item in row["dyadic_bins"]:
        j = item["j"]
        count = item["count"]
        bin_ratio = Fraction(d * count, 1 << j)
        if bin_ratio > maximum_bin:
            maximum_bin = bin_ratio
            maximum_bin_j = j
        prefix += count
        prefix_ratio = Fraction(d * prefix, 1 << (j + 1))
        if prefix_ratio > maximum_prefix:
            maximum_prefix = prefix_ratio
            maximum_prefix_j = j
    return {
        "occupied_bins": len(row["dyadic_bins"]),
        "maximum_D_times_bin_count_over_2j": fraction_json(maximum_bin),
        "maximum_bin_j": maximum_bin_j,
        "maximum_D_times_prefix_count_over_2j1": fraction_json(maximum_prefix),
        "maximum_prefix_j": maximum_prefix_j,
        "finite_dyadic_mass_bound_if_bin_inequality_used": fraction_json(
            Fraction(len(row["dyadic_bins"]), d)
        ),
    }


def process(raw_path: Path) -> dict:
    raw_bytes = raw_path.read_bytes()
    raw = json.loads(raw_bytes)
    scale = raw["fixed_point"]["scale"]
    limit = raw["limit"]
    exponent_rows = []
    previous: dict[str, tuple[int, Fraction]] = {}
    first_certified_increase: dict[str, dict | None] = {
        label: None for _, _, label in EXPONENTS
    }

    for checkpoint in raw["checkpoints"]:
        x = checkpoint["X"]
        rows = {row["k"]: row for row in checkpoint["thresholds"]}
        all_hard_row = rows[1]
        all_hard_lower = fraction_from_json(all_hard_row["reciprocal_interval"]["lower"])
        all_hard_upper = fraction_from_json(all_hard_row["reciprocal_interval"]["upper"])
        per_exponent = []
        for p, q, label in EXPONENTS:
            certificate = certified_log_power_floor(x, p, q)
            d = certificate["D"]
            if d < 1 or d + 1 not in rows:
                raise AssertionError(("threshold outside raw table", x, label, d))
            row = rows[d + 1]
            sigma_lower = fraction_from_json(row["reciprocal_interval"]["lower"])
            sigma_upper = fraction_from_json(row["reciprocal_interval"]["upper"])
            normalized_lower = sigma_lower / d
            normalized_upper = sigma_upper / d
            power_normalized_lower = sigma_lower / (d + 1)
            power_normalized_upper = sigma_upper / d
            all_power_lower = all_hard_lower / (d + 1)
            all_power_upper = all_hard_upper / d
            prior = previous.get(label)
            if (
                prior is not None
                and prior[1] > 0
                and normalized_lower > 0
                and first_certified_increase[label] is None
                and normalized_lower > prior[1]
            ):
                first_certified_increase[label] = {
                    "previous_X": prior[0],
                    "current_X": x,
                    "current_lower": fraction_json(normalized_lower),
                    "previous_upper": fraction_json(prior[1]),
                }
            if normalized_upper > 0:
                previous[label] = (x, normalized_upper)
            per_exponent.append(
                {
                    "exponent": label,
                    "p": p,
                    "q": q,
                    "threshold_certificate": certificate,
                    "selected_k": d + 1,
                    "hard_sources": row["hard_sources"],
                    "reducible_root_count": row["root_count"],
                    "Sigma_D_interval": row["reciprocal_interval"],
                    "Sigma_D_over_D_interval": {
                        "lower": fraction_json(normalized_lower),
                        "upper": fraction_json(normalized_upper),
                    },
                    "Sigma_D_over_log_power_interval": {
                        "lower": fraction_json(power_normalized_lower),
                        "upper": fraction_json(power_normalized_upper),
                        "reason": "D <= (ln X)^c < D+1",
                    },
                    "all_hard_reducible_mass_over_log_power_interval": {
                        "lower": fraction_json(all_power_lower),
                        "upper": fraction_json(all_power_upper),
                    },
                    "endpoint_dyadic_statistics": endpoint_bin_statistics(row, d),
                    "dyadic_bins": row["dyadic_bins"],
                }
            )
        exponent_rows.append(
            {
                "X": x,
                "all_hard_reducible_root_count": all_hard_row["root_count"],
                "all_hard_reducible_mass_interval": all_hard_row["reciprocal_interval"],
                "exponents": per_exponent,
            }
        )

    endpoint_thresholds = {
        row["D"]: row for row in raw["checkpoints"][-1]["thresholds"]
    }
    linear_survivors = []
    linear_nonvacuous_survivors = []
    prefix_survivors = []
    stronger_failures = []
    for item in raw["candidate_inequality_failures"]:
        if item["D_times_bin_count_le_2j"] is None:
            linear_survivors.append(item["D"])
            if endpoint_thresholds[item["D"]]["root_count"]:
                linear_nonvacuous_survivors.append(item["D"])
        if item["D_times_prefix_count_le_2j1"] is None:
            prefix_survivors.append(item["D"])
        if item["D2_times_bin_count_le_2j"] is not None:
            stronger_failures.append(
                {"D": item["D"], "first_failure": item["D2_times_bin_count_le_2j"]}
            )

    return {
        "schema": "C104-thresholded-reducible-root-report-v1",
        "raw_file": raw_path.name,
        "raw_sha256": hashlib.sha256(raw_bytes).hexdigest().upper(),
        "limit": limit,
        "exact_acceptance": True,
        "fixed_point_scale": scale,
        "finite_evidence_only": True,
        "thresholded_checkpoints": exponent_rows,
        "monotonicity_test": {
            "candidate": "Sigma_D(X)/D is nonincreasing at the listed geometric cutoffs",
            "first_certified_increase_by_exponent": first_certified_increase,
        },
        "candidate_basin_inequalities": {
            "survived_through_limit": {
                "statement": "D*count_j(R_{X,D}) <= 2^j for every dyadic denominator bin",
                "D_values": linear_survivors,
                "nonvacuous_endpoint_D_values": linear_nonvacuous_survivors,
                "eventwise_scan_through_X": limit,
            },
            "prefix_capacity_survived_through_limit": {
                "statement": "D*count({r:r-1<2^(j+1)}) <= 2^(j+1)",
                "D_values": prefix_survivors,
                "eventwise_scan_through_X": limit,
            },
            "stronger_quadratic_first_failures": {
                "statement": "D^2*count_j(R_{X,D}) <= 2^j",
                "rows": stronger_failures,
            },
            "raw_failure_table": raw["candidate_inequality_failures"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = process(args.raw)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_text(payload, encoding="ascii")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "limit": result["limit"],
                "raw_sha256": result["raw_sha256"],
                "linear_bin_D_survivors": result["candidate_basin_inequalities"]
                ["survived_through_limit"]["D_values"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
