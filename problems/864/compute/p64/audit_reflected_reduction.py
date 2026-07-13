#!/usr/bin/env python3
"""Exact audit of the reflected Sidon specialization of LG33."""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

from audit_residual_bridges import metrics


ROOT = Path(__file__).resolve().parents[4]
SAMPLES = ROOT / "problems/864/compute/p20/results/samples.jsonl"
BOSE128 = ROOT / "problems/864/compute/p37/bose_q128_sample.jsonl"
HARD_SAMPLE_ID = "ruzsa-9ab2ac138632"


def pair_sums(values: tuple[int, ...]) -> set[int]:
    return {
        values[i] + values[j]
        for j in range(len(values))
        for i in range(j + 1)
    }


def positive_differences(values: tuple[int, ...]) -> set[int]:
    return {
        values[j] - values[i]
        for j in range(1, len(values))
        for i in range(j)
    }


def is_sidon(values: tuple[int, ...]) -> bool:
    sums = [
        values[i] + values[j]
        for j in range(len(values))
        for i in range(j + 1)
    ]
    return len(sums) == len(set(sums))


def reflected_record(base: tuple[int, ...], center: int, label: str) -> dict:
    if base[0] != 0:
        raise ValueError("base must start at zero")
    width = base[-1]
    if center <= 2 * width:
        raise ValueError("reflected blocks are not disjoint")
    if not is_sidon(base):
        raise ValueError("base is not Sidon")
    sums = pair_sums(base)
    differences = positive_differences(base)
    if center in {left + right for left in sums for right in differences}:
        raise ValueError("center is not a literal sum-plus-difference hole")

    reflected = tuple(sorted(base + tuple(center - value for value in base)))
    row = metrics(reflected, center + 1)
    h = row["H"]
    gap = center - 2 * width
    internal_gaps = tuple(base[i + 1] - base[i] for i in range(len(base) - 1))
    excess = sum(max(0, value - h) for value in internal_gaps)
    d_base = sum(h - value for value in differences if value < h)
    separated = gap >= h

    result = {
        "label": label,
        "p": len(base),
        "W": width,
        "center": center,
        "N": center + 1,
        "H": h,
        "central_gap": gap,
        "internal_excess_E": excess,
        "D_base": d_base,
        "lg33_margin": row["lg33_margin"],
        "edge_bridge_margin": row["edge_bridge_margin"],
        "touch_bridge_margin": row["touch_bridge_margin"],
        "separated": separated,
    }
    if separated:
        expected_g = gap - h + 2 * excess
        expected_s = 2 * ((len(base) - 1) * h - width + excess)
        expected_z = 2 * d_base - h * (h - 1) // 2
        if row["G_H"] != expected_g:
            raise AssertionError("reflected ambient-hole identity failed")
        if row["S_H"] != expected_s:
            raise AssertionError("reflected short-gap identity failed")
        if row["Z_H"] != expected_z:
            raise AssertionError("reflected centered-difference identity failed")
        if row["adjacent_duplicate_weight"] != row["S_H"]:
            raise AssertionError("separated reflected edge bridge is not LG33")
        slack_formula = (
            -16 * row["N"] * d_base
            - 15 * h**3
            + 4 * row["N"] * h * h
            + 12 * h * h * gap
            + 24 * h * h * excess
            + 12 * h * h
            + 18 * h * row["N"] * len(base)
            - 13 * h * row["N"]
        )
        if slack_formula != -row["lg33_margin"]:
            raise AssertionError("reflected LG33 reduction failed")
        result["lg33_slack_formula"] = slack_formula
        result["exact_gap_bound_lhs"] = 12 * h * h * (gap + 2 * excess)
        result["exact_gap_bound_rhs"] = (
            16 * row["N"] * d_base
            + 15 * h**3
            - 4 * row["N"] * h * h
            - 12 * h * h
            - 18 * h * row["N"] * len(base)
            + 13 * h * row["N"]
        )
    return result


def small_holes(max_width: int) -> dict:
    rulers = holes = separated = failures = 0
    maximum_margin = None
    for width in range(1, max_width + 1):
        for middle_size in range(width):
            for middle in combinations(range(1, width), middle_size):
                base = (0, *middle, width)
                if not is_sidon(base):
                    continue
                rulers += 1
                sums = pair_sums(base)
                differences = positive_differences(base)
                forbidden = {left + right for left in sums for right in differences}
                for center in range(2 * width + 1, 3 * width):
                    if center in forbidden:
                        continue
                    holes += 1
                    row = reflected_record(base, center, "small")
                    separated += int(row["separated"])
                    failures += int(row["lg33_margin"] > 0)
                    if maximum_margin is None or row["lg33_margin"] > maximum_margin["lg33_margin"]:
                        maximum_margin = {**row, "B": list(base)}
    return {
        "max_width": max_width,
        "sidon_rulers": rulers,
        "literal_holes": holes,
        "separated_rows": separated,
        "lg33_failures": failures,
        "maximum_lg33_margin": maximum_margin,
    }


def hard_record() -> dict:
    sample = None
    with SAMPLES.open(encoding="utf-8") as source:
        for line in source:
            row = json.loads(line)
            if row["sample_id"] == HARD_SAMPLE_ID:
                sample = row
                break
    if sample is None:
        raise RuntimeError("hard P20 sample not found")
    shift = min(sample["A"])
    center = int(sample["exceptional_sum"]) - 2 * shift
    normalized = tuple(int(value) - shift for value in sample["A"])
    base = tuple(value for value in normalized if 2 * value < center)
    if tuple(sorted(base + tuple(center - value for value in base))) != normalized:
        raise AssertionError("hard sample is not fully reflected")
    return reflected_record(base, center, HARD_SAMPLE_ID)


def bose_record() -> dict:
    stored = json.loads(BOSE128.read_text(encoding="utf-8").splitlines()[0])
    best = stored["best_candidate"]
    base = tuple(int(value) for value in best["points"])
    center = int(best["candidate_center"])
    return reflected_record(base, center, "bose-q128")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=18)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "problems/864/compute/p64/reflected_reduction.json",
    )
    args = parser.parse_args()
    report = {
        "arithmetic": "integer",
        "small_holes": small_holes(args.max_width),
        "hard_P20": hard_record(),
        "bose_q128": bose_record(),
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "small_holes": report["small_holes"],
                "hard_P20": report["hard_P20"],
                "bose_q128": report["bose_q128"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
