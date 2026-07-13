#!/usr/bin/env python3
"""Integer audit for the P50 centered-LG33 subcase."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from math import gcd
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_WITNESS = ROOT / "problems/864/compute/p36/admissible_bridge_obstruction.json"


def prescribed_h(n: int) -> int:
    lo, hi = 1, n
    while lo < hi:
        mid = (lo + hi) // 2
        if mid**3 >= n * n:
            hi = mid
        else:
            lo = mid + 1
    return lo


def sum_counts(points: tuple[int, ...]) -> Counter[int]:
    result: Counter[int] = Counter()
    for j, right in enumerate(points):
        for left in points[: j + 1]:
            result[left + right] += 1
    return result


def classify_sum_fibers(points: tuple[int, ...]) -> tuple[bool, int | None]:
    repeated = [value for value, count in sum_counts(points).items() if count >= 2]
    return len(repeated) <= 1, repeated[0] if len(repeated) == 1 else None


def difference_reps(points: tuple[int, ...]) -> dict[int, list[tuple[int, int]]]:
    result: dict[int, list[tuple[int, int]]] = {}
    for j in range(1, len(points)):
        for i in range(j):
            result.setdefault(points[j] - points[i], []).append((points[j], points[i]))
    return result


def metrics(points: tuple[int, ...], n: int, sigma: int | None = None) -> dict:
    admissible, actual_sigma = classify_sum_fibers(points)
    if not admissible:
        raise ValueError("nonadmissible input")
    if sigma != actual_sigma:
        sigma = actual_sigma

    h = prescribed_h(n)
    k = len(points)
    reps = difference_reps(points)
    duplicate_count = 0
    for difference, edges in reps.items():
        if len(edges) > 2:
            raise AssertionError(f"nu({difference}) > 2")
        if len(edges) != 2:
            continue
        duplicate_count += 1
        if sigma is None:
            raise AssertionError("duplicate difference without exceptional sum")
        (r1, l1), (r2, l2) = edges
        if r1 + l2 != sigma or r2 + l1 != sigma:
            raise AssertionError("reflection involution failed")

    gaps = [right - left for left, right in zip(points, points[1:])]
    m = h + sum(min(gap, h) for gap in gaps)
    endpoint_slack = points[0] + (n - 1 - points[-1])
    g = endpoint_slack + sum(max(0, gap - h) for gap in gaps)
    if g != n + h - 1 - m:
        raise AssertionError("gap identity failed")
    short_gap_slack = sum(max(0, h - gap) for gap in gaps)
    if short_gap_slack != (k - 1) * h + g - (n - 1):
        raise AssertionError("short-gap identity failed")
    if short_gap_slack != k * h - m:
        raise AssertionError("support-defect identity failed")

    d_weight = sum(
        h - difference
        for difference, edges in reps.items()
        if difference < h and len(edges) == 2
    )
    q_weight = sum(
        h - difference for difference in range(1, h) if difference not in reps
    )
    z = d_weight - q_weight
    w = sum(
        (h - difference) * len(edges)
        for difference, edges in reps.items()
        if difference < h
    )
    if z != w - h * (h - 1) // 2:
        raise AssertionError("centered D-Q identity failed")

    lhs = 8 * n * z
    rhs = 12 * h * h * g - 3 * h**3 + 12 * h * h + 9 * n * (k - 1) * h
    simple_envelope = 6 * n * n + (12 * h * h - 9 * n) * g
    sharp_envelope = (
        9 * n * (n - 1)
        - 3 * h**3
        + 12 * h * h
        + (12 * h * h - 9 * n) * g
    )
    if rhs - sharp_envelope != 9 * n * short_gap_slack:
        raise AssertionError("sharp-envelope identity failed")
    if sharp_envelope <= simple_envelope:
        raise AssertionError("prescribed-scale base envelope was not strict")
    fixed = 8 * n * z - 12 * h * h * g + 3 * h**3 - 12 * h * h
    unit = n * (k - 1) * h
    return {
        "A": list(points),
        "N": n,
        "H": h,
        "k": k,
        "M_H": m,
        "G_H": g,
        "short_gap_slack": short_gap_slack,
        "D_H": d_weight,
        "Q_H": q_weight,
        "Z_H": z,
        "exceptional_sum": sigma,
        "duplicate_distance_count": duplicate_count,
        "lg33_rhs": rhs,
        "lg33_margin": lhs - rhs,
        "simple_envelope": simple_envelope,
        "sharp_envelope": sharp_envelope,
        "simple_envelope_margin": lhs - simple_envelope,
        "sharp_envelope_margin": lhs - sharp_envelope,
        "rhs_over_sharp_envelope": rhs - sharp_envelope,
        "sharp_over_simple_envelope": sharp_envelope - simple_envelope,
        "rhs_envelope_margin": rhs - simple_envelope,
        "coefficient_2_margin": fixed - 8 * unit,
        "coefficient_17_8_margin": 2 * fixed - 17 * unit,
        "coefficient_13_6_margin": 3 * fixed - 26 * unit,
    }


def endpoint_sets(n: int):
    if n == 1:
        yield (0,)
        return
    for mask in range(1 << (n - 2)):
        yield (0,) + tuple(
            value
            for value in range(1, n - 1)
            if mask & (1 << (value - 1))
        ) + (n - 1,)


def keep_extreme(current: dict | None, row: dict, key: str, maximum: bool) -> dict:
    if current is None:
        return row
    if (row[key] > current[key]) == maximum and row[key] != current[key]:
        return row
    return current


def keep_residual_ratio(current: dict | None, row: dict) -> dict:
    numerator = row["sharp_envelope_margin"]
    denominator = row["rhs_over_sharp_envelope"]
    if numerator <= 0 or denominator < 0:
        raise AssertionError("invalid sharp residual ratio")
    if current is not None:
        old_numerator = current["residual_numerator"]
        old_denominator = current["rescue_denominator"]
        if old_denominator == 0:
            return current
        if (
            denominator != 0
            and numerator * old_denominator <= old_numerator * denominator
        ):
            return current
    if denominator == 0:
        ratio = "infinity"
    else:
        common = gcd(numerator, denominator)
        ratio = f"{numerator // common}/{denominator // common}"
    return {
        **row,
        "residual_to_rescue_ratio": ratio,
        "residual_numerator": numerator,
        "rescue_denominator": denominator,
    }


def exhaustive(max_n: int) -> dict:
    checked = high_support = lg33_failures = envelope_failures = 0
    subcase_count = subcase_failures = 0
    simple_envelope_count = simple_envelope_failures = 0
    sharp_envelope_count = sharp_envelope_failures = 0
    linear_remaining_by_n: Counter[int] = Counter()
    sharp_remaining_by_n: Counter[int] = Counter()
    minimum_envelope = None
    minimum_sharp_proof_margin = None
    minimum_base_improvement = None
    maximum_residual_ratio = None
    maximum = {
        "lg33": None,
        "simple_envelope": None,
        "sharp_envelope": None,
        "coefficient_2": None,
        "coefficient_17_8": None,
        "coefficient_13_6": None,
    }
    keys = {
        "lg33": "lg33_margin",
        "simple_envelope": "simple_envelope_margin",
        "sharp_envelope": "sharp_envelope_margin",
        "coefficient_2": "coefficient_2_margin",
        "coefficient_17_8": "coefficient_17_8_margin",
        "coefficient_13_6": "coefficient_13_6_margin",
    }
    remaining_maximum = {
        name: None
        for name in (
            "lg33",
            "coefficient_2",
            "coefficient_17_8",
            "coefficient_13_6",
        )
    }

    for n in range(1, max_n + 1):
        for points in endpoint_sets(n):
            admissible, sigma = classify_sum_fibers(points)
            if not admissible:
                continue
            row = metrics(points, n, sigma)
            checked += 1
            minimum_envelope = keep_extreme(
                minimum_envelope, row, "rhs_envelope_margin", False
            )
            minimum_sharp_proof_margin = keep_extreme(
                minimum_sharp_proof_margin, row, "rhs_over_sharp_envelope", False
            )
            minimum_base_improvement = keep_extreme(
                minimum_base_improvement, row, "sharp_over_simple_envelope", False
            )
            for name, key in keys.items():
                maximum[name] = keep_extreme(maximum[name], row, key, True)
            if row["rhs_envelope_margin"] < 0:
                envelope_failures += 1
            if 3 * row["M_H"] < 2 * n:
                continue
            high_support += 1
            if row["lg33_margin"] > 0:
                lg33_failures += 1
            if 4 * row["Z_H"] <= 3 * n:
                subcase_count += 1
                if row["lg33_margin"] > 0:
                    subcase_failures += 1
            else:
                linear_remaining_by_n[n] += 1
            if row["simple_envelope_margin"] <= 0:
                simple_envelope_count += 1
                if row["lg33_margin"] > 0:
                    simple_envelope_failures += 1
            if row["sharp_envelope_margin"] <= 0:
                sharp_envelope_count += 1
                if row["lg33_margin"] > 0:
                    sharp_envelope_failures += 1
            else:
                sharp_remaining_by_n[n] += 1
                maximum_residual_ratio = keep_residual_ratio(
                    maximum_residual_ratio, row
                )
                for name, key in {
                    "lg33": "lg33_margin",
                    "coefficient_2": "coefficient_2_margin",
                    "coefficient_17_8": "coefficient_17_8_margin",
                    "coefficient_13_6": "coefficient_13_6_margin",
                }.items():
                    remaining_maximum[name] = keep_extreme(
                        remaining_maximum[name], row, key, True
                    )

    return {
        "max_N": max_n,
        "admissible_sets_checked": checked,
        "high_support_sets_checked": high_support,
        "lg33_failure_count": lg33_failures,
        "rhs_envelope_failure_count": envelope_failures,
        "linear_subcase_condition": "4*Z_H <= 3*N",
        "linear_subcase_count": subcase_count,
        "linear_subcase_failure_count": subcase_failures,
        "linear_remaining_count": high_support - subcase_count,
        "linear_remaining_by_N": dict(sorted(linear_remaining_by_n.items())),
        "simple_envelope_condition": (
            "8*N*Z_H <= 6*N^2 + (12*H^2-9*N)*G_H"
        ),
        "simple_envelope_subcase_count": simple_envelope_count,
        "simple_envelope_subcase_failure_count": simple_envelope_failures,
        "sharp_envelope_condition": (
            "8*N*Z_H <= 9*N*(N-1)-3*H^3+12*H^2 "
            "+ (12*H^2-9*N)*G_H"
        ),
        "sharp_envelope_subcase_count": sharp_envelope_count,
        "sharp_envelope_subcase_failure_count": sharp_envelope_failures,
        "sharp_envelope_remaining_count": high_support - sharp_envelope_count,
        "sharp_envelope_remaining_by_N": dict(sorted(sharp_remaining_by_n.items())),
        "minimum_rhs_envelope": minimum_envelope,
        "minimum_rhs_over_sharp_envelope": minimum_sharp_proof_margin,
        "minimum_sharp_over_simple_envelope": minimum_base_improvement,
        "maximum_sharp_residual_to_rescue_ratio": maximum_residual_ratio,
        "maximum_margins": maximum,
        "sharp_remaining_maximum_margins": remaining_maximum,
    }


def recheck_witness(path: Path) -> dict:
    stored = json.loads(path.read_text(encoding="utf-8"))
    points = tuple(int(value) - 1 for value in stored["A"])
    row = metrics(points, int(stored["N"]))
    expected = {
        "H": stored["H"],
        "k": stored["k"],
        "M_H": stored["M_H"],
        "G_H": stored["ambient_holes"],
        "D_H": stored["D_H"],
        "Q_H": stored["Q_H"],
        "Z_H": stored["Z_H"],
    }
    for key, value in expected.items():
        if row[key] != int(value):
            raise AssertionError(f"stored witness mismatch for {key}")
    row["source"] = str(path.relative_to(ROOT)).replace("\\", "/")
    row["falsifies_coefficient_2"] = row["coefficient_2_margin"] > 0
    row["falsifies_coefficient_17_8"] = row["coefficient_17_8_margin"] > 0
    row["falsifies_coefficient_13_6"] = row["coefficient_13_6_margin"] > 0
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=22)
    parser.add_argument("--witness", type=Path, default=DEFAULT_WITNESS)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p50/audit_results.json"),
    )
    args = parser.parse_args()
    result = {
        "arithmetic": "integer",
        "exhaustive": exhaustive(args.max_n),
        "stored_admissible_falsifier": recheck_witness(args.witness),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "admissible_sets_checked": result["exhaustive"][
                    "admissible_sets_checked"
                ],
                "high_support_sets_checked": result["exhaustive"][
                    "high_support_sets_checked"
                ],
                "lg33_failure_count": result["exhaustive"]["lg33_failure_count"],
                "rhs_envelope_failure_count": result["exhaustive"][
                    "rhs_envelope_failure_count"
                ],
                "linear_remaining_count": result["exhaustive"][
                    "linear_remaining_count"
                ],
                "sharp_envelope_remaining_count": result["exhaustive"][
                    "sharp_envelope_remaining_count"
                ],
                "stored_coefficient_2_margin": result[
                    "stored_admissible_falsifier"
                ]["coefficient_2_margin"],
                "stored_coefficient_17_8_margin": result[
                    "stored_admissible_falsifier"
                ]["coefficient_17_8_margin"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
