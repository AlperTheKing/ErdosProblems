#!/usr/bin/env python3
"""Exact carry-level residue moments for fully reflected samples."""

from __future__ import annotations

import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
INPUT = ROOT / "problems/864/compute/p20/results/samples.jsonl"
OUTPUT = ROOT / "problems/864/compute/p44/weighted_carry_moments.json"


def unordered_sums(values: list[int]) -> list[int]:
    return [a + b for i, a in enumerate(values) for b in values[i:]]


def reflected_data(row: dict[str, object]) -> tuple[list[int], int] | None:
    values = sorted(int(x) for x in row["A"])
    k = len(values)
    sigma = int(row.get("exceptional_sum") or 0)
    multiplicity = int(row.get("exceptional_multiplicity") or 0)
    value_set = set(values)
    if k % 2 or sigma <= 0 or multiplicity != k // 2:
        return None
    if any(sigma - a not in value_set for a in values):
        return None
    lower = [a for a in values if 2 * a < sigma]
    if len(lower) != k // 2:
        return None
    top = max(lower)
    z = sorted(top - a for a in lower)
    gap = sigma - 2 * top
    if gap <= 0:
        return None
    return z, gap


def ratio(num: int, den: int) -> str:
    return str(Fraction(num, den))


def moment_profile(row: dict[str, object]) -> dict[str, object] | None:
    parsed = reflected_data(row)
    if parsed is None:
        return None
    z, gap = parsed
    p = len(z)
    width = z[-1]
    b = 1 if gap % 2 else 2
    gamma = (gap - b) // 2
    h = gamma + width + 1
    slots = [gamma + value for value in z]
    sums = unordered_sums(slots)
    assert len(sums) == len(set(sums))
    differences = {
        x - y
        for x in slots
        for y in slots
    }
    assert len(differences) == p * (p - 1) + 1

    levels: dict[str, dict[str, object]] = {}
    for level in (0, 1, 2):
        target = level * h - b
        solutions = [(s, target - s) for s in sums if target - s in differences]
        residues = [s % h for s, _ in solutions]
        if level == 0:
            assert not solutions
        else:
            assert len(residues) == len(set(residues))
        centered = [2 * residue - (h - b) for residue in residues]
        levels[str(level)] = {
            "count": len(solutions),
            "sum_sum_coordinate": sum(s for s, _ in solutions),
            "sum_difference_coordinate": sum(d for _, d in solutions),
            "sum_residue": sum(residues),
            "sum_centered_residue": sum(centered),
            "sum_abs_centered_residue": sum(abs(value) for value in centered),
            "sum_square_centered_residue": sum(value * value for value in centered),
        }

    count1 = int(levels["1"]["count"])
    count2 = int(levels["2"]["count"])
    signed_count = count1 - count2
    residue_moment = int(levels["1"]["sum_residue"]) - int(
        levels["2"]["sum_residue"]
    )
    centered_moment = int(levels["1"]["sum_centered_residue"]) - int(
        levels["2"]["sum_centered_residue"]
    )
    baseline = (3 * p * p - p + 2) // 2
    delta = baseline - h

    return {
        "sample_id": row["sample_id"],
        "kind": row.get("kind"),
        "p": p,
        "b": b,
        "h": h,
        "max_E": b + 2 * (h - 1),
        "delta": delta,
        "levels": levels,
        "signed_count": signed_count,
        "signed_residue_moment": residue_moment,
        "signed_centered_moment": centered_moment,
        "signed_count_over_p2": ratio(signed_count, p * p),
        "signed_residue_moment_over_hp2": ratio(
            residue_moment, h * p * p
        ),
        "signed_centered_moment_over_hp2": ratio(
            centered_moment, h * p * p
        ),
    }


def extrema(
    rows: list[dict[str, object]], field: str
) -> dict[str, dict[str, object]]:
    key = lambda row: Fraction(str(row[field]))
    return {"minimum": min(rows, key=key), "maximum": max(rows, key=key)}


def main() -> None:
    reports = []
    for line in INPUT.read_text(encoding="utf-8").splitlines():
        result = moment_profile(json.loads(line))
        if result is not None:
            reports.append(result)
    reports.sort(key=lambda row: (int(row["p"]), str(row["sample_id"])))
    subcritical = [
        row for row in reports if int(row["p"]) >= 72 and int(row["delta"]) > 0
    ]
    summary = {
        "arithmetic": "integer and Fraction",
        "report_count": len(reports),
        "large_subcritical_count": len(subcritical),
        "signed_count_extrema": extrema(
            subcritical, "signed_count_over_p2"
        ),
        "signed_residue_moment_extrema": extrema(
            subcritical, "signed_residue_moment_over_hp2"
        ),
        "signed_centered_moment_extrema": extrema(
            subcritical, "signed_centered_moment_over_hp2"
        ),
        "reports": reports,
    }
    OUTPUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {key: value for key, value in summary.items() if key != "reports"},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()