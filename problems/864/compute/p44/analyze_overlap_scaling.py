#!/usr/bin/env python3
"""Exact derived statistics for the P44 modular carry profiles."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
INPUT = ROOT / "problems/864/compute/p44/carry_layer_profiles.json"
OUTPUT = ROOT / "problems/864/compute/p44/overlap_scaling_summary.json"


def ratio(num: int, den: int) -> str:
    return str(Fraction(num, den))


def enrich(row: dict[str, object]) -> dict[str, object]:
    p = int(row["p"])
    h = int(row["slot_order"])
    support_sum = int(row["sum_support_mod_h"])
    support_diff = int(row["difference_support_mod_h"])
    actual = int(row["actual_overlap"])
    one_only = int(row["carry1_only_residues"])
    two_only = int(row["carry2_only_residues"])
    both = int(row["both_positive_layers_residues"])
    layer_counts = row["literal_pair_counts_by_layer"]
    assert isinstance(layer_counts, dict)
    layer_one = int(layer_counts.get("1", 0))
    layer_two = int(layer_counts.get("2", 0))

    sum_size = p * (p + 1) // 2
    diff_size = p * (p - 1) + 1
    baseline = sum_size + diff_size
    sum_loss = sum_size - support_sum
    diff_loss = diff_size - support_diff
    delta = baseline - h
    forced = delta - sum_loss - diff_loss
    union_holes = actual - forced

    assert forced == int(row["forced_overlap"])
    assert actual == one_only + two_only + both
    assert layer_one == one_only + both
    assert layer_two == two_only + both
    assert union_holes == h - (support_sum + support_diff - actual)

    return {
        "sample_id": row["sample_id"],
        "kind": row["kind"],
        "p": p,
        "h": h,
        "max_E": int(row["max_E"]),
        "delta": delta,
        "sum_loss": sum_loss,
        "difference_loss": diff_loss,
        "forced_overlap": forced,
        "actual_overlap": actual,
        "union_holes": union_holes,
        "carry1_residues": layer_one,
        "carry2_residues": layer_two,
        "signed_carry_residue_count": layer_one - layer_two,
        "delta_over_p2": ratio(delta, p * p),
        "overlap_over_p2": ratio(actual, p * p),
        "signed_carry_over_p2": ratio(layer_one - layer_two, p * p),
        "support_loss_over_p2": ratio(sum_loss + diff_loss, p * p),
    }


def extremum(
    rows: list[dict[str, object]], field: str, largest: bool
) -> dict[str, object]:
    key = lambda row: Fraction(str(row[field]))
    return max(rows, key=key) if largest else min(rows, key=key)


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = [enrich(row) for row in payload["reports"]]
    large = [row for row in rows if int(row["p"]) >= 72]
    subcritical = [row for row in large if int(row["delta"]) > 0]
    summary = {
        "arithmetic": "integer and Fraction",
        "row_count": len(rows),
        "large_row_count": len(large),
        "large_p_cutoff": 72,
        "large_subcritical_count": len(subcritical),
        "subcritical_overlap_ratio_min": extremum(
            subcritical, "overlap_over_p2", False
        ),
        "subcritical_overlap_ratio_max": extremum(
            subcritical, "overlap_over_p2", True
        ),
        "subcritical_signed_ratio_min": extremum(
            subcritical, "signed_carry_over_p2", False
        ),
        "subcritical_signed_ratio_max": extremum(
            subcritical, "signed_carry_over_p2", True
        ),
        "large_overlap_ratio_min": extremum(
            large, "overlap_over_p2", False
        ),
        "large_overlap_ratio_max": extremum(
            large, "overlap_over_p2", True
        ),
        "large_signed_ratio_min": extremum(
            large, "signed_carry_over_p2", False
        ),
        "large_signed_ratio_max": extremum(
            large, "signed_carry_over_p2", True
        ),
        "rows": rows,
    }
    OUTPUT.write_text(
        json.dumps(summary, indent=2) + "\n", encoding="ascii"
    )
    print(
        json.dumps(
            {key: value for key, value in summary.items() if key != "rows"},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
