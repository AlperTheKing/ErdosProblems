#!/usr/bin/env python3
"""Exact carry-layer profiles for fully reflected Problem 864 samples."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def unordered_sum_counter(values: list[int]) -> Counter[int]:
    out: Counter[int] = Counter()
    for i, a in enumerate(values):
        for b in values[i:]:
            out[a + b] += 1
    return out


def signed_ruler_from_reflection(row: dict) -> tuple[list[int], int] | None:
    values = sorted(row["A"])
    k = len(values)
    sigma = int(row.get("exceptional_sum") or 0)
    multiplicity = int(row.get("exceptional_multiplicity") or 0)
    if k % 2 or multiplicity != k // 2 or sigma <= 0:
        return None
    if any(sigma - a not in set(values) for a in values):
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


def profile(row: dict) -> dict | None:
    data = signed_ruler_from_reflection(row)
    if data is None:
        return None
    z, gap = data
    p = len(z)
    width = z[-1]
    e = [gap + 2 * value for value in z]

    sums_e = unordered_sum_counter(e)
    if len(sums_e) != p * (p + 1) // 2:
        raise AssertionError((row["sample_id"], "E not Sidon"))
    e_set = set(e)
    pair_sum_set = set(sums_e)
    triple_hits = {
        target
        for target in e
        if any(target - a in pair_sum_set for a in e)
    }
    if triple_hits:
        raise AssertionError((row["sample_id"], "E meets 3E", sorted(triple_hits)))

    base = 1 if gap % 2 else 2
    gamma = (gap - base) // 2
    h = gamma + width + 1
    slots = [gamma + value for value in z]
    if not (min(slots) >= 0 and max(slots) == h - 1):
        raise AssertionError((row["sample_id"], "slot normalization"))

    pair_sums = sorted(unordered_sum_counter(slots))
    positive_differences = {
        slots[j] - slots[i]
        for i in range(p)
        for j in range(i + 1, p)
    }
    if len(positive_differences) != p * (p - 1) // 2:
        raise AssertionError((row["sample_id"], "difference collision"))
    differences = {0} | positive_differences | {-d for d in positive_differences}

    sum_residue_values: dict[int, list[int]] = {}
    for value in pair_sums:
        sum_residue_values.setdefault(value % h, []).append(value)
    diff_residue_values: dict[int, list[int]] = {}
    for value in differences:
        diff_residue_values.setdefault(value % h, []).append(value)

    target = -base
    overlap = set(sum_residue_values) & {
        (target - residue) % h for residue in diff_residue_values
    }
    layers = Counter()
    residue_layer_sets: dict[int, set[int]] = {}
    for residue in overlap:
        possible: set[int] = set()
        difference_residue = (target - residue) % h
        for s in sum_residue_values[residue]:
            for d in diff_residue_values[difference_residue]:
                total = s + d
                delta = total - target
                if delta % h:
                    raise AssertionError((row["sample_id"], "bad carry"))
                layer = delta // h
                possible.add(layer)
                layers[layer] += 1
        residue_layer_sets[residue] = possible
    if any(0 in possible for possible in residue_layer_sets.values()):
        raise AssertionError((row["sample_id"], "forbidden zero carry"))
    if any(not possible <= {1, 2} for possible in residue_layer_sets.values()):
        raise AssertionError((row["sample_id"], "unexpected carry layer"))

    baseline = (3 * p * p - p + 2) // 2
    support_sum = len(sum_residue_values)
    support_diff = len(diff_residue_values)
    forced_overlap = support_sum + support_diff - h
    if len(overlap) < max(0, forced_overlap):
        raise AssertionError((row["sample_id"], "overlap pigeonhole"))

    only_one = sum(possible == {1} for possible in residue_layer_sets.values())
    only_two = sum(possible == {2} for possible in residue_layer_sets.values())
    both = sum(possible == {1, 2} for possible in residue_layer_sets.values())
    return {
        "sample_id": row["sample_id"],
        "kind": row.get("kind"),
        "p": p,
        "gap": gap,
        "width": width,
        "max_E": e[-1],
        "coefficient_num": e[-1],
        "coefficient_den": p * p,
        "slot_order": h,
        "modular_threshold_slack_twice": 2 * h - (3 * p * p - p + 2),
        "sum_support_mod_h": support_sum,
        "difference_support_mod_h": support_diff,
        "baseline_support": baseline,
        "forced_overlap": forced_overlap,
        "actual_overlap": len(overlap),
        "carry1_only_residues": only_one,
        "carry2_only_residues": only_two,
        "both_positive_layers_residues": both,
        "literal_pair_counts_by_layer": {str(key): value for key, value in sorted(layers.items())},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("problems/864/compute/p20/results/samples.jsonl"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p44/carry_layer_profiles.json"),
    )
    args = parser.parse_args()
    reports = []
    with args.input.open(encoding="utf-8") as source:
        for line in source:
            result = profile(json.loads(line))
            if result is not None:
                reports.append(result)
    reports.sort(key=lambda row: (row["coefficient_num"] / row["coefficient_den"], row["p"]))
    output = {
        "arithmetic": "integer",
        "fully_reflected_count": len(reports),
        "reports": reports,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "fully_reflected_count": len(reports),
        "best": reports[:10],
    }, indent=2))


if __name__ == "__main__":
    main()