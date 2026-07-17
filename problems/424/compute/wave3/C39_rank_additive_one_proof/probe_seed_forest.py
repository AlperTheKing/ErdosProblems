#!/usr/bin/env python3
"""Exact seed-2/seed-3 forest audit for C39.

Every allowed hole is either a structural root (splitless or hard), an odd
seed-2 child of a smaller hole, or a 3-easy seed-3 child of a smaller hole.
This script verifies that decomposition and tests whether healed seed-2
edges from splitless-root components already pay all hard roots.
"""

from __future__ import annotations

import argparse
import json
from array import array
from collections import Counter, defaultdict
from pathlib import Path

from probe_multiplier_targets import (
    INF, allowed, hard_shape, pairs_for, spf_sieve,
)


def structural_parent(n: int) -> tuple[int, str] | None:
    if n > 3 and n % 2:
        return (n + 1) // 2, "T2"
    if n % 2 == 0 and (n + 1) % 3 == 0:
        q = (n + 1) // 3
        if allowed(q) and q != 3:
            return q, "T3"
    return None


def structural_root(n: int) -> int:
    while True:
        parent = structural_parent(n)
        if parent is None:
            return n
        n = parent[0]


def greedy_unmatched(
    hard: list[tuple[int, int]],
    targets: list[tuple[int, int, int, int]],
    target_filter,
) -> list[dict]:
    available: list[list[tuple[int, int, int, int]]] = [[] for _ in range(64)]
    pos = 0
    unmatched = []
    for source, source_rank in hard:
        while pos < len(targets) and targets[pos][0] <= source:
            target = targets[pos]
            if target_filter(target):
                available[target[2]].append(target)
            pos += 1
        chosen = None
        for r in range(source_rank, -1, -1):
            if available[r]:
                chosen = available[r].pop()
                break
        if chosen is None:
            unmatched.append({"source": source, "rank": source_rank})
    return unmatched


def audit(limit: int) -> dict:
    spf = spf_sieve(limit + 1)
    member = bytearray(limit + 1)
    rank = array("H", [INF]) * (limit + 1)
    member[2] = member[3] = 1
    pairs: list[list[tuple[int, int]]] = [[] for _ in range(limit + 1)]
    hard = []
    targets = []
    decomposition_failures = []

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs[n] = pairs_for(n, spf)
        if any(member[a] and member[b] for a, b in pairs[n]):
            member[n] = 1
            if n % 2:
                q = (n + 1) // 2
                if allowed(q) and not member[q]:
                    targets.append((n, q, rank[q], structural_root(q)))
            continue
        if not pairs[n]:
            rank[n] = 0
        else:
            rank[n] = 1 + max(
                min(rank[x] for x in (a, b) if not member[x])
                for a, b in pairs[n]
            )
        parent = structural_parent(n)
        if parent is None:
            if not (not pairs[n] or hard_shape(n, pairs[n])):
                decomposition_failures.append({"n": n, "reason": "bad root"})
        else:
            p, kind = parent
            if member[p] or rank[p] >= rank[n]:
                decomposition_failures.append({
                    "n": n, "parent": p, "kind": kind,
                    "parent_member": bool(member[p]),
                    "parent_rank": rank[p], "rank": rank[n],
                })
        if hard_shape(n, pairs[n]):
            hard.append((n, rank[n]))

    root_kind = {}
    for root in {target[3] for target in targets}:
        root_pairs = pairs[root]
        root_kind[root] = "splitless" if not root_pairs else (
            "hard_hole" if not member[root] else "hard_generated"
        )

    component_counts = defaultdict(lambda: {"targets": 0, "min_child": None,
                                             "min_rank": None, "max_rank": None})
    for child, _, target_rank, root in targets:
        row = component_counts[root]
        row["targets"] += 1
        row["min_child"] = child if row["min_child"] is None else min(row["min_child"], child)
        row["min_rank"] = target_rank if row["min_rank"] is None else min(row["min_rank"], target_rank)
        row["max_rank"] = target_rank if row["max_rank"] is None else max(row["max_rank"], target_rank)

    unmatched_all = greedy_unmatched(hard, targets, lambda _: True)
    unmatched_splitless_all = greedy_unmatched(
        hard, targets, lambda t: root_kind[t[3]] == "splitless"
    )
    first_per_splitless = set()
    for target in targets:
        if root_kind[target[3]] == "splitless" and target[3] not in first_per_splitless:
            first_per_splitless.add(target[3])
    unmatched_splitless_first = greedy_unmatched(
        hard, targets,
        lambda t: root_kind[t[3]] == "splitless"
        and component_counts[t[3]]["min_child"] == t[0],
    )
    unmatched_first_all = greedy_unmatched(
        hard, targets,
        lambda t: component_counts[t[3]]["min_child"] == t[0],
    )
    ordinal_by_child = {}
    seen_in_component = defaultdict(int)
    for target in targets:
        seen_in_component[target[3]] += 1
        ordinal_by_child[target[0]] = seen_in_component[target[3]]
    first_k_component_unmatched = {}
    for cap in (1, 2, 3, 4, 8):
        misses = greedy_unmatched(
            hard, targets, lambda t, cap=cap: ordinal_by_child[t[0]] <= cap,
        )
        first_k_component_unmatched[str(cap)] = {
            "count": len(misses), "prefix": misses[:20],
        }

    own_component = []
    target_by_root = defaultdict(list)
    for target in targets:
        target_by_root[target[3]].append(target)
    for source, source_rank in hard:
        hits = [
            {"child": child, "rank": target_rank}
            for child, _, target_rank, root in target_by_root.get(source, [])
            if child <= source and target_rank <= source_rank
        ]
        if hits:
            own_component.append({"source": source, "rank": source_rank, "hits": hits})

    kind_histogram = Counter(root_kind[target[3]] for target in targets)
    component_histogram = Counter(root_kind[root] for root in component_counts)
    return {
        "schema_version": 1,
        "limit": limit,
        "hard_count": len(hard),
        "target_count": len(targets),
        "decomposition_failures": decomposition_failures[:20],
        "target_event_root_kind_histogram": dict(kind_histogram),
        "target_component_root_kind_histogram": dict(component_histogram),
        "all_target_greedy_unmatched": unmatched_all[:20],
        "all_target_greedy_unmatched_count": len(unmatched_all),
        "splitless_component_greedy_unmatched": unmatched_splitless_all[:20],
        "splitless_component_greedy_unmatched_count": len(unmatched_splitless_all),
        "first_splitless_boundary_greedy_unmatched": unmatched_splitless_first[:20],
        "first_splitless_boundary_greedy_unmatched_count": len(unmatched_splitless_first),
        "first_boundary_each_component_greedy_unmatched": unmatched_first_all[:20],
        "first_boundary_each_component_greedy_unmatched_count": len(unmatched_first_all),
        "first_k_boundaries_each_component": first_k_component_unmatched,
        "hard_sources_paid_by_own_component_before_arrival": own_component[:20],
        "hard_sources_paid_by_own_component_count": len(own_component),
        "multi_target_components": [
            {"root": root, "kind": root_kind[root], **row}
            for root, row in sorted(component_counts.items()) if row["targets"] > 1
        ][:50],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = audit(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        key: payload[key] for key in (
            "limit", "hard_count", "target_count", "decomposition_failures",
            "target_event_root_kind_histogram",
            "all_target_greedy_unmatched_count",
            "splitless_component_greedy_unmatched_count",
            "first_splitless_boundary_greedy_unmatched_count",
            "first_boundary_each_component_greedy_unmatched_count",
            "first_k_boundaries_each_component",
            "hard_sources_paid_by_own_component_count",
        )
    }, indent=2))


if __name__ == "__main__":
    main()
