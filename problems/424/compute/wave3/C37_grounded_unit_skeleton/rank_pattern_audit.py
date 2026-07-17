#!/usr/bin/env python3
"""Test chain and rank-based selection rules on the nine C34 supports."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
C34 = HERE.parent / "C34_image_dual_core"
sys.path.insert(0, str(C34))

from ground_core_lp import grounded_core  # noqa: E402
from lp_probe import admissible_pairs, allowed  # noqa: E402


ENDPOINTS = (54, 74, 186, 362, 500, 1000, 2000, 5000, 10000)
INDEXED = re.compile(r"^(and_lo|and_l|and_r|or_lo)_(\d+)_(\d+)$")


def chain_coordinate(value: int) -> tuple[int, int]:
    depth = 0
    while value % 2:
        value = (value + 1) // 2
        depth += 1
    return value, depth


def ranks(limit: int, values: list[int], pairs: dict[int, list[tuple[int, int]]], ground: set[int]):
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
    assert set(death) == set(values)
    assert set(generation) == ground
    return death, generation, infinity


def support(limit: int) -> dict:
    values = [value for value in range(2, limit + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    ground = grounded_core(values, pairs)
    death, generation, infinity = ranks(limit, values, pairs, ground)
    cert = json.loads((C34 / f"ground_dual_{limit}.json").read_text(encoding="ascii"))
    rows = defaultdict(lambda: defaultdict(set))
    boundary = set()
    for name in cert["row_duals"]:
        if name.startswith("q_lower_"):
            boundary.add(int(name.rsplit("_", 1)[1]))
        elif name.startswith("or_hi_"):
            rows[int(name.rsplit("_", 1)[1])]["or_hi"].add(0)
        else:
            match = INDEXED.match(name)
            if match:
                kind, node, pair_index = match.groups()
                rows[int(node)][kind].add(int(pair_index))

    lower = sorted(
        (node, pair_index)
        for node, kinds in rows.items()
        for pair_index in kinds["and_lo"] & kinds["or_lo"]
    )
    upper = {}
    for node, kinds in rows.items():
        if not kinds["or_hi"]:
            continue
        choices = []
        for pair_index in range(len(pairs[node])):
            sides = []
            if pair_index in kinds["and_l"]:
                sides.append(0)
            if pair_index in kinds["and_r"]:
                sides.append(1)
            if len(sides) != 1:
                choices = []
                break
            choices.append(sides[0])
        if choices:
            upper[node] = choices

    lower_records = []
    for node, pair_index in lower:
        pair = pairs[node][pair_index]
        survival = min(death[parent] for parent in pair)
        all_survivals = [min(death[parent] for parent in item) for item in pairs[node]]
        ground_pair = all(parent in ground for parent in pair)
        ground_scores = [
            (max(generation[parent] for parent in item), index)
            for index, item in enumerate(pairs[node])
            if all(parent in ground for parent in item)
        ]
        lower_records.append(
            {
                "node": node,
                "pair_index": pair_index,
                "parents": list(pair),
                "parent_death_ranks": [
                    "inf" if death[parent] == infinity else death[parent] for parent in pair
                ],
                "max_survival_pair": survival == max(all_survivals),
                "ground_pair": ground_pair,
                "minimum_generation_ground_pair": bool(ground_pair and ground_scores)
                and (max(generation[parent] for parent in pair), pair_index)
                == min(ground_scores),
            }
        )

    upper_records = []
    for node, choices in sorted(upper.items()):
        for pair_index, side in enumerate(choices):
            pair = pairs[node][pair_index]
            selected_parent = pair[side]
            other_parent = pair[1 - side]
            upper_records.append(
                {
                    "node": node,
                    "pair_index": pair_index,
                    "pair": list(pair),
                    "selected_parent": selected_parent,
                    "selected_death_rank": "inf" if death[selected_parent] == infinity else death[selected_parent],
                    "other_death_rank": "inf" if death[other_parent] == infinity else death[other_parent],
                    "earliest_death_parent": death[selected_parent] <= death[other_parent],
                }
            )

    chain_depths = defaultdict(list)
    for child in boundary:
        root, depth = chain_coordinate(child)
        chain_depths[root].append(depth)
    interval_count = 0
    noncontiguous = []
    for root, depths in sorted(chain_depths.items()):
        depths.sort()
        intervals = 1 + sum(right != left + 1 for left, right in zip(depths, depths[1:]))
        interval_count += intervals
        if intervals > 1:
            noncontiguous.append({"root": root, "depths": depths, "intervals": intervals})

    return {
        "limit": limit,
        "boundary": sorted(boundary),
        "boundary_chain_count": len(chain_depths),
        "boundary_interval_count": interval_count,
        "noncontiguous_boundary_chains": noncontiguous,
        "lower": lower_records,
        "upper": upper_records,
    }


def first_pair_conflict(items: list[dict], key: str) -> dict | None:
    seen = {}
    for item in items:
        by_node = defaultdict(set)
        for record in item[key]:
            signature = record["pair_index"]
            if key == "upper":
                signature = (record["pair_index"], record["selected_parent"])
            by_node[record["node"]].add(signature)
        for node, signature in sorted(by_node.items()):
            if node in seen and seen[node][1] != signature:
                return {
                    "node": node,
                    "first_limit": seen[node][0],
                    "first_selection": sorted(seen[node][1]),
                    "second_limit": item["limit"],
                    "second_selection": sorted(signature),
                }
            seen[node] = (item["limit"], signature)
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    items = [support(limit) for limit in ENDPOINTS]
    summaries = []
    for item in items:
        lower = item["lower"]
        upper = item["upper"]
        summaries.append(
            {
                "limit": item["limit"],
                "boundary_chain_count": item["boundary_chain_count"],
                "boundary_interval_count": item["boundary_interval_count"],
                "noncontiguous_chain_count": len(item["noncontiguous_boundary_chains"]),
                "lower_count": len(lower),
                "lower_max_survival_count": sum(r["max_survival_pair"] for r in lower),
                "lower_ground_pair_count": sum(r["ground_pair"] for r in lower),
                "lower_min_generation_count": sum(r["minimum_generation_ground_pair"] for r in lower),
                "upper_choice_count": len(upper),
                "upper_earliest_death_count": sum(r["earliest_death_parent"] for r in upper),
            }
        )

    prefix_conflicts = []
    for old, new in zip(items, items[1:]):
        cutoff = old["limit"]
        removed = sorted(set(old["boundary"]) - {x for x in new["boundary"] if x <= cutoff})
        added = sorted({x for x in new["boundary"] if x <= cutoff} - set(old["boundary"]))
        if removed or added:
            prefix_conflicts.append(
                {"from": cutoff, "to": new["limit"], "removed": removed, "added": added}
            )

    payload = {
        "schema_version": 1,
        "summaries": summaries,
        "first_boundary_prefix_conflict": prefix_conflicts[0] if prefix_conflicts else None,
        "all_boundary_prefix_conflicts": prefix_conflicts,
        "first_lower_pair_conflict": first_pair_conflict(items, "lower"),
        "first_upper_parent_conflict": first_pair_conflict(items, "upper"),
        "first_lower_max_survival_counterexample": next(
            (
                {"limit": item["limit"], **record}
                for item in items for record in item["lower"]
                if not record["max_survival_pair"]
            ),
            None,
        ),
        "first_upper_earliest_death_counterexample": next(
            (
                {"limit": item["limit"], **record}
                for item in items for record in item["upper"]
                if not record["earliest_death_parent"]
            ),
            None,
        ),
        "supports": items,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({key: payload[key] for key in payload if key != "supports"}))


if __name__ == "__main__":
    main()
