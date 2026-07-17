#!/usr/bin/env python3
"""Exact capacity-one falsifier and root-pool audit for C85.

The graph has a hard hole h on the left and an even seed-chain root r on the
right whenever some missing endpoint of an admissible factor pair of h lies
on r's seed-2 chain.  The script scans high-pair hard holes in increasing
order, maintains an exact maximum matching, and emits the first Hall witness.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
C67_PATH = ROOT / "problems/424/fanout/wave5/C67_weak_scb.py"


def load_c67():
    spec = importlib.util.spec_from_file_location("c67_weak_scb", C67_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {C67_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def witness_roots(h: int, data: dict) -> list[int]:
    holes: set[int] = data["holes"]
    root_of: dict[int, int] = data["root_of"]
    out = set()
    for a, b in data["pairs"][h]:
        found = False
        for p in (a, b):
            if p not in holes:
                continue
            found = True
            if p % 2 != 1:
                raise RuntimeError(("even endpoint of odd product", h, p))
            u = (p + 1) // 2
            if u not in holes:
                raise RuntimeError(("missing endpoint has nonmissing parent", h, p, u))
            out.add(root_of[u])
        if not found:
            raise RuntimeError(("hard hole has an unblocked pair", h, a, b))
    return sorted(out)


def augment(h: int, adjacency: dict[int, list[int]], match_right: dict[int, int], seen: set[int]) -> bool:
    for root in adjacency[h]:
        if root in seen:
            continue
        seen.add(root)
        if root not in match_right or augment(match_right[root], adjacency, match_right, seen):
            match_right[root] = h
            return True
    return False


def hall_witness(unmatched: list[int], adjacency: dict[int, list[int]], match_right: dict[int, int]) -> tuple[list[int], list[int]]:
    match_left = {h: root for root, h in match_right.items()}
    left_seen = set(unmatched)
    right_seen: set[int] = set()
    queue = deque(unmatched)
    while queue:
        h = queue.popleft()
        for root in adjacency[h]:
            if match_left.get(h) == root or root in right_seen:
                continue
            right_seen.add(root)
            mate = match_right.get(root)
            if mate is not None and mate not in left_seen:
                left_seen.add(mate)
                queue.append(mate)
    neighborhood = {root for h in left_seen for root in adjacency[h]}
    if neighborhood != right_seen:
        raise RuntimeError("alternating Hall neighborhood mismatch")
    if len(left_seen) <= len(neighborhood):
        raise RuntimeError("extracted set is not Hall deficient")
    return sorted(left_seen), sorted(neighborhood)


def chain_nodes(root: int, holes: set[int], limit: int) -> list[int]:
    nodes = []
    value = 2 * root - 1
    while value <= limit and value in holes:
        nodes.append(value)
        value = 2 * value - 1
    return nodes


def root_incidence_budget(root: int, holes: set[int], limit: int) -> int:
    top = limit + 1
    return sum(top // p for p in chain_nodes(root, holes, top))


def audit(limit: int, min_pairs: int) -> dict:
    if min_pairs < 1:
        raise ValueError("min_pairs must be positive")
    c67 = load_c67()
    data = c67.build_arithmetic(limit)
    left = sorted(h for h in data["hard"] if len(data["pairs"][h]) >= min_pairs)
    adjacency = {h: witness_roots(h, data) for h in left}
    if any(not adjacency[h] for h in left):
        raise RuntimeError("a high-pair hard hole has no witness root")

    sys.setrecursionlimit(max(10000, 4 * len(left) + 100))
    match_right: dict[int, int] = {}
    first_failure = None
    for index, h in enumerate(left, start=1):
        if augment(h, adjacency, match_right, set()):
            continue
        witness_left, witness_right = hall_witness([h], adjacency, match_right)
        first_failure = {
            "cutoff": h,
            "source_index": index,
            "matched_before_failure": len(match_right),
            "failed_source": h,
            "failed_source_pair_count": len(data["pairs"][h]),
            "failed_source_roots": adjacency[h],
            "hall_left": witness_left,
            "hall_right": witness_right,
            "hall_left_size": len(witness_left),
            "hall_right_size": len(witness_right),
            "hall_deficiency": len(witness_left) - len(witness_right),
        }
        break

    result = {
        "limit": limit,
        "minimum_pair_count": min_pairs,
        "high_pair_source_count": len(left),
        "first_capacity_one_failure": first_failure,
    }

    if first_failure is not None:
        cutoff = first_failure["cutoff"]
        # Recompute the right-closed witness at its literal cutoff.  Every
        # listed source and neighbor is already at most cutoff, so this also
        # verifies that the failure is not caused by later arithmetic data.
        if max(first_failure["hall_left"]) != cutoff:
            raise RuntimeError("first failure is not anchored by its new source")
        recomputed = {
            root
            for h in first_failure["hall_left"]
            for root in witness_roots(h, data)
        }
        if recomputed != set(first_failure["hall_right"]):
            raise RuntimeError("Hall neighborhood replay failed")
        if any(len(data["pairs"][h]) < min_pairs for h in first_failure["hall_left"]):
            raise RuntimeError("Hall witness contains a low-pair source")

        D = min_pairs - 1
        exact_budgets = {
            root: root_incidence_budget(root, data["holes"], cutoff)
            for root in first_failure["hall_right"]
        }
        capacities = {
            root: (budget + D) // (D + 1)
            for root, budget in exact_budgets.items()
        }
        result["corrected_pool_at_failure"] = {
            "D": D,
            "exact_root_incidence_budget_sum": sum(exact_budgets.values()),
            "capacitated_root_slot_sum": sum(capacities.values()),
            "maximum_single_root_capacity": max(capacities.values()),
            "capacity_covers_hall_left": sum(capacities.values()) >= len(first_failure["hall_left"]),
        }

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--min-pairs", type=int, default=6)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.limit, args.min_pairs)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
