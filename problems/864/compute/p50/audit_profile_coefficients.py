#!/usr/bin/env python3
"""Exact coefficient gates on the stored P20 profile corpus."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter
from math import gcd
from pathlib import Path


COEFFICIENTS = {
    "2": (1, 8),
    "17/8": (2, 17),
    "13/6": (3, 26),
    "9/4": (1, 9),
}


def prescribed(n: int, h: int) -> bool:
    return h**3 >= n * n and (h - 1) ** 3 < n * n


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def update_required_coefficient(
    current: dict | None, record: dict, fixed: int, unit: int
) -> dict | None:
    if unit <= 0:
        return current
    numerator = max(0, fixed)
    denominator = 4 * unit
    if current is not None:
        old_numerator = int(current["required_numerator"])
        old_denominator = int(current["required_denominator"])
        if numerator * old_denominator <= old_numerator * denominator:
            return current
    common = gcd(numerator, denominator)
    return {
        **record,
        "required_coefficient": f"{numerator // common}/{denominator // common}",
        "required_numerator": numerator,
        "required_denominator": denominator,
    }


def update_residual_ratio(
    current: dict | None, record: dict, residual: int, rescue: int
) -> dict:
    if residual <= 0 or rescue < 0:
        raise AssertionError("invalid sharp residual ratio")
    if current is not None:
        old_residual = int(current["residual_numerator"])
        old_rescue = int(current["rescue_denominator"])
        if old_rescue == 0:
            return current
        if rescue != 0 and residual * old_rescue <= old_residual * rescue:
            return current
    ratio = "infinity"
    if rescue:
        common = gcd(residual, rescue)
        ratio = f"{residual // common}/{rescue // common}"
    return {
        **record,
        "residual_to_rescue_ratio": ratio,
        "residual_numerator": residual,
        "rescue_denominator": rescue,
    }


def audit(path: Path, all_scales: bool = False) -> dict:
    input_sha256 = sha256(path)
    profile_count = canonical_count = eligible_count = high_support_count = 0
    failure_counts = {name: 0 for name in COEFFICIENTS}
    residual_failure_counts = {name: 0 for name in COEFFICIENTS}
    first_failure = {name: None for name in COEFFICIENTS}
    maximum_margin = {name: None for name in COEFFICIENTS}
    residual_maximum_margin = {name: None for name in COEFFICIENTS}
    coverage_counts = Counter()
    covered_lg33_failures = Counter()
    maximum_envelope_margin = {
        "linear_4Z_le_3N": None,
        "simple": None,
        "sharp": None,
    }
    first_remaining = {
        "linear_4Z_le_3N": None,
        "simple": None,
        "sharp": None,
    }
    minimum_rhs_over_sharp = None
    minimum_sharp_over_simple = None
    maximum_required_coefficient = None
    residual_maximum_required_coefficient = None
    maximum_residual_ratio = None

    with gzip.open(path, "rt", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            row = json.loads(line)
            profile_count += 1
            n = int(row["N"])
            h = int(row["H"])
            is_prescribed = prescribed(n, h)
            if is_prescribed:
                canonical_count += 1
            if not all_scales and not is_prescribed:
                continue
            eligible_count += 1
            m = int(row["M"])
            if 3 * m < 2 * n:
                continue
            high_support_count += 1
            k = int(row["size"])
            z = int(row["Z"])
            g = n + h - 1 - m
            lhs = 8 * n * z
            rhs = (
                12 * h * h * g
                - 3 * h**3
                + 12 * h * h
                + 9 * n * (k - 1) * h
            )
            simple_envelope = 6 * n * n + (12 * h * h - 9 * n) * g
            sharp_envelope = (
                9 * n * (n - 1)
                - 3 * h**3
                + 12 * h * h
                + (12 * h * h - 9 * n) * g
            )
            rhs_over_sharp = rhs - sharp_envelope
            sharp_over_simple = sharp_envelope - simple_envelope
            if rhs_over_sharp != 9 * n * (k * h - m):
                raise AssertionError(
                    f"sharp-envelope identity failed at line {line_number}"
                )
            if not all_scales and sharp_over_simple <= 0:
                raise AssertionError(
                    f"simple envelope was not strict at line {line_number}"
                )

            base_record = {
                "line": line_number,
                "sample_id": row["sample_id"],
                "N": n,
                "H": h,
                "k": k,
                "M_H": m,
                "G_H": g,
                "D_H": int(row["duplicate_weight"]),
                "Q_H": int(row["missing_weight"]),
                "Z_H": z,
                "lg33_margin": lhs - rhs,
            }
            for name, margin in {
                "linear_4Z_le_3N": 4 * z - 3 * n,
                "simple": lhs - simple_envelope,
                "sharp": lhs - sharp_envelope,
            }.items():
                record = {**base_record, "margin": margin}
                old = maximum_envelope_margin[name]
                if old is None or margin > old["margin"]:
                    maximum_envelope_margin[name] = record
                if margin <= 0:
                    coverage_counts[name] += 1
                    if lhs > rhs:
                        covered_lg33_failures[name] += 1
                elif first_remaining[name] is None:
                    first_remaining[name] = record

            if (
                minimum_rhs_over_sharp is None
                or rhs_over_sharp < minimum_rhs_over_sharp["margin"]
            ):
                minimum_rhs_over_sharp = {**base_record, "margin": rhs_over_sharp}
            if (
                minimum_sharp_over_simple is None
                or sharp_over_simple < minimum_sharp_over_simple["margin"]
            ):
                minimum_sharp_over_simple = {**base_record, "margin": sharp_over_simple}
            if lhs > sharp_envelope:
                maximum_residual_ratio = update_residual_ratio(
                    maximum_residual_ratio,
                    base_record,
                    lhs - sharp_envelope,
                    rhs_over_sharp,
                )

            fixed = 8 * n * z - 12 * h * h * g + 3 * h**3 - 12 * h * h
            unit = n * (k - 1) * h
            maximum_required_coefficient = update_required_coefficient(
                maximum_required_coefficient, base_record, fixed, unit
            )
            if lhs > sharp_envelope:
                residual_maximum_required_coefficient = update_required_coefficient(
                    residual_maximum_required_coefficient, base_record, fixed, unit
                )
            for name, (multiplier, coefficient) in COEFFICIENTS.items():
                margin = multiplier * fixed - coefficient * unit
                record = {**base_record, "margin": margin}
                if maximum_margin[name] is None or margin > maximum_margin[name]["margin"]:
                    maximum_margin[name] = record
                if margin > 0:
                    failure_counts[name] += 1
                    if first_failure[name] is None:
                        first_failure[name] = record
                if lhs > sharp_envelope:
                    if (
                        residual_maximum_margin[name] is None
                        or margin > residual_maximum_margin[name]["margin"]
                    ):
                        residual_maximum_margin[name] = record
                    if margin > 0:
                        residual_failure_counts[name] += 1

    if sha256(path) != input_sha256:
        raise RuntimeError("profile corpus changed during audit")
    return {
        "arithmetic": "integer",
        "input": str(path).replace("\\", "/"),
        "input_sha256": input_sha256,
        "scope": "all_scales" if all_scales else "prescribed_H",
        "profile_count": profile_count,
        "canonical_count": canonical_count,
        "eligible_profile_count": eligible_count,
        "high_support_count": high_support_count,
        "linear_condition_is_proved_subcase": not all_scales,
        "subcase_coverage_counts": {
            name: coverage_counts[name]
            for name in ("linear_4Z_le_3N", "simple", "sharp")
        },
        "subcase_remaining_counts": {
            name: high_support_count - coverage_counts[name]
            for name in ("linear_4Z_le_3N", "simple", "sharp")
        },
        "covered_lg33_failure_counts": {
            name: covered_lg33_failures[name]
            for name in ("linear_4Z_le_3N", "simple", "sharp")
        },
        "maximum_subcase_margins": maximum_envelope_margin,
        "first_remaining": first_remaining,
        "minimum_rhs_over_sharp_envelope": minimum_rhs_over_sharp,
        "minimum_sharp_over_simple_envelope": minimum_sharp_over_simple,
        "maximum_required_coefficient": maximum_required_coefficient,
        "sharp_residual_maximum_required_coefficient": (
            residual_maximum_required_coefficient
        ),
        "maximum_sharp_residual_to_rescue_ratio": maximum_residual_ratio,
        "failure_counts": failure_counts,
        "sharp_residual_failure_counts": residual_failure_counts,
        "first_failure": first_failure,
        "maximum_margin": maximum_margin,
        "sharp_residual_maximum_margin": residual_maximum_margin,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("problems/864/compute/p20/results/profiles.jsonl.gz"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p50/profile_coefficient_gates.json"),
    )
    parser.add_argument(
        "--all-scales",
        action="store_true",
        help="evaluate every H row, not only H=ceil(N^(2/3))",
    )
    args = parser.parse_args()
    result = audit(args.input, args.all_scales)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "profile_count": result["profile_count"],
                "canonical_count": result["canonical_count"],
                "eligible_profile_count": result["eligible_profile_count"],
                "scope": result["scope"],
                "subcase_remaining_counts": result["subcase_remaining_counts"],
                "failure_counts": result["failure_counts"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
