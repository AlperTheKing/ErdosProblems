#!/usr/bin/env python3
"""Exact-test canonical death-rank pair choices on complete C34 skeletons."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
C34 = HERE.parent / "C34_image_dual_core"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(C34))

from ground_core_lp import grounded_core, solve  # noqa: E402
from lp_probe import admissible_pairs, allowed, hard_shape  # noqa: E402
from scan_complete_gate_rule import exact_audit  # noqa: E402


INDEXED = re.compile(r"^(and_lo|and_l|and_r|or_lo)_(\d+)_(\d+)$")


def rank_data(limit: int):
    values = [value for value in range(2, limit + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    ground = grounded_core(values, pairs)
    infinity = limit + 1
    death = {}
    generation = {2: 0, 3: 0}
    for value in values:
        if value in ground:
            death[value] = infinity
            candidates = [
                1 + max(generation[left], generation[right])
                for left, right in pairs[value]
                if left in generation and right in generation
            ]
            if value not in generation and candidates:
                generation[value] = min(candidates)
        elif not pairs[value]:
            death[value] = 1
        else:
            death[value] = 1 + max(
                min(death[left], death[right]) for left, right in pairs[value]
            )
    return pairs, ground, death, generation, infinity


def canonical_rows(limit: int, selected_names: set[str]) -> tuple[set[str], dict]:
    pairs, ground, death, generation, infinity = rank_data(limit)
    boundary = {name for name in selected_names if name.startswith("q_lower_")}
    indexed = defaultdict(set)
    upper_nodes = set()
    for name in selected_names:
        if name.startswith("or_hi_"):
            upper_nodes.add(int(name.rsplit("_", 1)[1]))
            continue
        match = INDEXED.match(name)
        if match:
            kind, node, pair_index = match.groups()
            indexed[int(node), int(pair_index)].add(kind)

    lower_counts = defaultdict(int)
    original_lower = set()
    for (node, pair_index), kinds in indexed.items():
        if "and_lo" in kinds and "or_lo" in kinds:
            lower_counts[node] += 1
            original_lower.add((node, pair_index))

    kept = set(boundary)
    canonical_lower = set()
    for node, count in lower_counts.items():
        def lower_key(pair_index: int):
            left, right = pairs[node][pair_index]
            survival = min(death[left], death[right])
            if survival == infinity:
                generation_cost = max(generation[left], generation[right])
            else:
                generation_cost = limit + 1
            return (-survival, generation_cost, pair_index)

        chosen = sorted(range(len(pairs[node])), key=lower_key)[:count]
        for pair_index in chosen:
            kept.add(f"and_lo_{node}_{pair_index}")
            kept.add(f"or_lo_{node}_{pair_index}")
            canonical_lower.add((node, pair_index))

    canonical_upper = {}
    complete_upper_nodes = []
    for node in sorted(upper_nodes):
        if any(
            len([kind for kind in ("and_l", "and_r") if kind in indexed[node, pair_index]]) != 1
            for pair_index in range(len(pairs[node]))
        ):
            continue
        kept.add(f"or_hi_{node}")
        choices = []
        for pair_index, pair in enumerate(pairs[node]):
            def parent_key(parent: int):
                generation_rank = generation.get(parent, limit + 1)
                return (death[parent], generation_rank, parent)

            selected_parent = min(pair, key=parent_key)
            side = "and_l" if selected_parent == pair[0] else "and_r"
            kept.add(f"{side}_{node}_{pair_index}")
            choices.append(selected_parent)
        canonical_upper[node] = choices
        complete_upper_nodes.append(node)

    original_upper = {}
    for node in complete_upper_nodes:
        choices = []
        for pair_index, pair in enumerate(pairs[node]):
            kinds = indexed[node, pair_index]
            choices.append(pair[0] if "and_l" in kinds else pair[1])
        original_upper[node] = choices

    return kept, {
        "changed_lower_gate_count": len(original_lower ^ canonical_lower) // 2,
        "changed_upper_parent_count": sum(
            old != new
            for node in canonical_upper
            for old, new in zip(original_upper[node], canonical_upper[node])
        ),
        "lower_changes": [
            {
                "node": node,
                "original": sorted(pair for n, pair in original_lower if n == node),
                "canonical": sorted(pair for n, pair in canonical_lower if n == node),
            }
            for node in sorted({n for n, _ in original_lower ^ canonical_lower})
        ],
        "upper_changes": [
            {"node": node, "original": original_upper[node], "canonical": canonical_upper[node]}
            for node in canonical_upper
            if original_upper[node] != canonical_upper[node]
        ],
    }


def test_cutoff(limit: int) -> dict:
    source = solve(limit, True)
    selected = {
        row["name"]
        for row in source["active_rows"]
        if abs(row["dual"]) >= 1e-8
    }
    kept, changes = canonical_rows(limit, selected)
    audit = exact_audit(limit, kept)
    return {"limit": limit, **audit, **changes}


def hard_cutoffs(stop: int) -> list[int]:
    return [
        value
        for value in range(4, stop + 1)
        if allowed(value) and hard_shape(value, admissible_pairs(value))
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = []
    for cutoff in hard_cutoffs(args.stop):
        result = test_cutoff(cutoff)
        results.append(result)
        if not result["passes"]:
            break
    payload = {
        "schema_version": 1,
        "stop": args.stop,
        "tested": len(results),
        "all_pass": all(result["passes"] for result in results),
        "first_failure": next((result for result in results if not result["passes"]), None),
        "changed_lower_cutoffs": sum(result["changed_lower_gate_count"] > 0 for result in results),
        "changed_upper_cutoffs": sum(result["changed_upper_parent_count"] > 0 for result in results),
        "results": results,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({key: payload[key] for key in payload if key != "results"}))


if __name__ == "__main__":
    main()
