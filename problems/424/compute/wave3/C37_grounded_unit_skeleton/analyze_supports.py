#!/usr/bin/env python3
"""Normalize and compare the nine exact C34 grounded dual supports."""

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
from lp_probe import admissible_pairs, allowed, hard_shape  # noqa: E402


ENDPOINTS = (54, 74, 186, 362, 500, 1000, 2000, 5000, 10000)
ROW_RE = re.compile(
    r"^(?P<kind>and_lo|and_l|and_r|or_lo)_(?P<node>\d+)_(?P<pair>\d+)$"
)


def chain_coordinate(value: int) -> tuple[int, int]:
    depth = 0
    while value % 2 == 1:
        value = (value + 1) // 2
        depth += 1
    return value, depth


def ground_data(limit: int) -> tuple[set[int], dict[int, int], dict[int, int]]:
    values = [value for value in range(2, limit + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    ground = grounded_core(values, pairs)
    rank = {2: 0, 3: 0}
    canonical_pair: dict[int, int] = {}
    for value in values:
        candidates = []
        for pair_index, (left, right) in enumerate(pairs[value]):
            if left in rank and right in rank:
                candidates.append(
                    (
                        max(rank[left], rank[right]),
                        rank[left] + rank[right],
                        pair_index,
                    )
                )
        if candidates:
            _, _, pair_index = min(candidates)
            left, right = pairs[value][pair_index]
            rank[value] = 1 + max(rank[left], rank[right])
            canonical_pair[value] = pair_index
    assert set(rank) == ground
    return ground, rank, canonical_pair


def parse_certificate(limit: int) -> dict:
    path = C34 / f"ground_dual_{limit}.json"
    source = json.loads(path.read_text(encoding="ascii"))
    rows = source["row_duals"]
    selected = defaultdict(lambda: defaultdict(set))
    boundary = set()
    for name, multiplier in rows.items():
        assert multiplier == "-1", (limit, name, multiplier)
        if name.startswith("q_lower_"):
            boundary.add(int(name.rsplit("_", 1)[1]))
            continue
        if name.startswith("or_hi_"):
            selected[int(name.rsplit("_", 1)[1])]["or_hi"].add(-1)
            continue
        match = ROW_RE.match(name)
        if match:
            selected[int(match.group("node"))][match.group("kind")].add(
                int(match.group("pair"))
            )
            continue
        raise AssertionError((limit, name))

    pairs = {value: admissible_pairs(value) for value in range(2, limit + 1)}
    lower_complete = {}
    lower_incomplete = {}
    upper_rows = {}
    for node, kinds in selected.items():
        complete = kinds["and_lo"] & kinds["or_lo"]
        incomplete = kinds["and_lo"] ^ kinds["or_lo"]
        if complete:
            lower_complete[node] = sorted(complete)
        if incomplete:
            lower_incomplete[node] = {
                kind: sorted(kinds[kind]) for kind in ("and_lo", "or_lo")
                if kinds[kind]
            }
        if kinds["or_hi"] or kinds["and_l"] or kinds["and_r"]:
            upper_rows[node] = {
                "or_hi": bool(kinds["or_hi"]),
                "and_l": sorted(kinds["and_l"]),
                "and_r": sorted(kinds["and_r"]),
            }

    ground, rank, canonical_pair = ground_data(limit)

    def node_record(node: int, indices: list[int]) -> dict:
        root, depth = chain_coordinate(node)
        return {
            "node": node,
            "chain_root": root,
            "chain_depth": depth,
            "pairs": [
                {
                    "index": index,
                    "parents": list(pairs[node][index]),
                    "ground_parents": [parent in ground for parent in pairs[node][index]],
                    "parent_ranks": [rank.get(parent) for parent in pairs[node][index]],
                    "canonical_ground_pair": canonical_pair.get(node) == index,
                }
                for index in indices
            ],
        }

    return {
        "limit": limit,
        "objective": int(source["dual_objective"]),
        "hard_count": sum(
            hard_shape(value, admissible_pairs(value))
            for value in range(2, limit + 1)
            if allowed(value)
        ),
        "boundary": sorted(boundary),
        "boundary_coordinates": [
            {"child": child, "parent": (child + 1) // 2,
             "chain_root": chain_coordinate(child)[0],
             "chain_depth": chain_coordinate(child)[1]}
            for child in sorted(boundary)
        ],
        "lower_complete": [
            node_record(node, indices) for node, indices in sorted(lower_complete.items())
        ],
        "lower_incomplete": lower_incomplete,
        "upper_rows": upper_rows,
        "bounds": {
            "lower": source["lower_bound_duals"],
            "upper": source["upper_bound_duals"],
        },
    }


def restricted_signature(certificate: dict, cutoff: int) -> dict:
    return {
        "boundary": [x for x in certificate["boundary"] if x <= cutoff],
        "lower": {
            row["node"]: [pair["index"] for pair in row["pairs"]]
            for row in certificate["lower_complete"] if row["node"] <= cutoff
        },
        "upper": {
            node: data for node, data in certificate["upper_rows"].items()
            if int(node) <= cutoff
        },
    }


def compare(certificates: list[dict]) -> list[dict]:
    comparisons = []
    for previous, current in zip(certificates, certificates[1:]):
        cutoff = previous["limit"]
        old = restricted_signature(previous, cutoff)
        new = restricted_signature(current, cutoff)
        comparisons.append(
            {
                "from": previous["limit"],
                "to": current["limit"],
                "boundary_removed": sorted(set(old["boundary"]) - set(new["boundary"])),
                "boundary_added_below_old_cutoff": sorted(
                    set(new["boundary"]) - set(old["boundary"])
                ),
                "lower_pair_conflicts": [
                    {
                        "node": node,
                        "old": old["lower"].get(node),
                        "new": new["lower"].get(node),
                    }
                    for node in sorted(set(old["lower"]) | set(new["lower"]))
                    if old["lower"].get(node) != new["lower"].get(node)
                ],
                "upper_conflicts": [
                    {
                        "node": node,
                        "old": old["upper"].get(node),
                        "new": new["upper"].get(node),
                    }
                    for node in sorted(set(old["upper"]) | set(new["upper"]))
                    if old["upper"].get(node) != new["upper"].get(node)
                ],
            }
        )
    return comparisons


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    certificates = [parse_certificate(limit) for limit in ENDPOINTS]
    payload = {
        "schema_version": 1,
        "endpoints": certificates,
        "adjacent_restriction_comparisons": compare(certificates),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            [
                {
                    "limit": item["limit"],
                    "boundary": len(item["boundary"]),
                    "lower_complete": len(item["lower_complete"]),
                    "lower_incomplete": len(item["lower_incomplete"]),
                    "upper": len(item["upper_rows"]),
                }
                for item in certificates
            ]
        )
    )


if __name__ == "__main__":
    main()
