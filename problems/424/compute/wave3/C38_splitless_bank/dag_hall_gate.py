#!/usr/bin/env python3
"""Exact critical-DAG Hall gates for the C38 splitless bank lane."""

from __future__ import annotations

import argparse
import json
import sys
from array import array
from collections import deque
from dataclasses import dataclass
from pathlib import Path

INF = 65535


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def spf_sieve(limit: int) -> array:
    spf = array("I", range(limit + 1))
    for p in range(2, int(limit**0.5) + 1):
        if spf[p] != p:
            continue
        for multiple in range(p * p, limit + 1, p):
            if spf[multiple] == multiple:
                spf[multiple] = p
    return spf


def divisors(n: int, spf: array) -> list[int]:
    values = [1]
    while n > 1:
        p = spf[n]
        old_size = len(values)
        power = 1
        while n % p == 0:
            n //= p
            power *= p
            values.extend(values[i] * power for i in range(old_size))
    return values


def pairs_for(n: int, spf: array) -> list[tuple[int, int]]:
    product = n + 1
    return [
        (a, product // a)
        for a in divisors(product, spf)
        if 2 <= a < product // a
        and allowed(a)
        and allowed(product // a)
    ]


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    q = (n + 1) // 3
    return not (allowed(q) and q != 3)


@dataclass(frozen=True)
class Source:
    value: int
    rank: int
    critical_roots: frozenset[int]
    all_lower_roots: frozenset[int]


@dataclass(frozen=True)
class Target:
    kind: str
    coordinate: int
    value: int
    rank: int
    critical_roots: frozenset[int]
    all_lower_roots: frozenset[int]


class Dinic:
    def __init__(self, node_count: int) -> None:
        self.graph: list[list[list[int]]] = [[] for _ in range(node_count)]

    def add_edge(self, source: int, target: int, capacity: int) -> None:
        forward = [target, len(self.graph[target]), capacity, capacity]
        reverse = [source, len(self.graph[source]), 0, 0]
        self.graph[source].append(forward)
        self.graph[target].append(reverse)

    def flow(self, source: int, sink: int, limit: int) -> int:
        total = 0
        while total < limit:
            level = [-1] * len(self.graph)
            level[source] = 0
            queue = deque((source,))
            while queue:
                node = queue.popleft()
                for target, _, capacity, _ in self.graph[node]:
                    if capacity and level[target] < 0:
                        level[target] = level[node] + 1
                        queue.append(target)
            if level[sink] < 0:
                break
            cursor = [0] * len(self.graph)

            def send(node: int, pushed: int) -> int:
                if node == sink:
                    return pushed
                while cursor[node] < len(self.graph[node]):
                    edge_id = cursor[node]
                    target, reverse_id, capacity, _ = self.graph[node][edge_id]
                    if capacity and level[target] == level[node] + 1:
                        sent = send(target, min(pushed, capacity))
                        if sent:
                            self.graph[node][edge_id][2] -= sent
                            self.graph[target][reverse_id][2] += sent
                            return sent
                    cursor[node] += 1
                return 0

            sent = send(source, limit - total)
            if not sent:
                break
            total += sent
        return total

    def reachable(self, source: int) -> set[int]:
        seen = {source}
        queue = deque((source,))
        while queue:
            node = queue.popleft()
            for target, _, capacity, _ in self.graph[node]:
                if capacity and target not in seen:
                    seen.add(target)
                    queue.append(target)
        return seen

    def cut_capacity(self, reachable: set[int]) -> int:
        return sum(
            original
            for source in reachable
            for target, _, _, original in self.graph[source]
            if target not in reachable
        )


def build(limit: int) -> tuple[list[Source], list[Target], dict[str, int]]:
    spf = spf_sieve(limit + 1)
    member = bytearray(limit + 1)
    rank = array("H", [INF]) * (limit + 1)
    member[2] = member[3] = 1
    critical_roots: list[frozenset[int]] = [frozenset() for _ in range(limit + 1)]
    all_lower_roots: list[frozenset[int]] = [frozenset() for _ in range(limit + 1)]
    sources: list[Source] = []
    targets: list[Target] = []
    splitless = holes = generated = 0

    for n in range(4, limit + 1):
        if not allowed(n):
            continue
        pairs = pairs_for(n, spf)
        if any(member[a] and member[b] for a, b in pairs):
            member[n] = 1
            generated += 1
            if n % 2:
                q = (n + 1) // 2
                if not member[q]:
                    targets.append(Target(
                        "Q", n, q, rank[q],
                        critical_roots[q], all_lower_roots[q],
                    ))
            continue

        holes += 1
        if not pairs:
            rank[n] = 0
            critical_roots[n] = frozenset((n,))
            all_lower_roots[n] = frozenset((n,))
            targets.append(Target(
                "E", n, n, 0, critical_roots[n], all_lower_roots[n]
            ))
            splitless += 1
        else:
            pair_blocks = [
                min(rank[q] for q in (a, b) if not member[q])
                for a, b in pairs
            ]
            blocking = max(pair_blocks)
            rank[n] = blocking + 1
            critical_children = {
                q
                for (a, b), pair_block in zip(pairs, pair_blocks)
                if pair_block == blocking
                for q in (a, b)
                if not member[q] and rank[q] == blocking
            }
            lower_children = {
                q
                for a, b in pairs
                for q in (a, b)
                if not member[q] and rank[q] < rank[n]
            }
            if not critical_children or not lower_children:
                raise AssertionError(("missing descent", n, rank[n]))
            critical_roots[n] = frozenset().union(
                *(critical_roots[q] for q in critical_children)
            )
            all_lower_roots[n] = frozenset().union(
                *(all_lower_roots[q] for q in lower_children)
            )

        if hard_shape(n, pairs):
            sources.append(Source(
                n, rank[n], critical_roots[n], all_lower_roots[n]
            ))

    return sources, targets, {
        "generated_nonseeds": generated,
        "holes": holes,
        "splitless": splitless,
        "hard": len(sources),
        "healed": sum(target.kind == "Q" for target in targets),
        "maximum_rank": max((source.rank for source in sources), default=0),
        "maximum_critical_root_count": max(
            (len(source.critical_roots) for source in sources), default=0
        ),
        "maximum_all_lower_root_count": max(
            (len(source.all_lower_roots) for source in sources), default=0
        ),
    }


def hall_gate(
    sources: list[Source],
    targets: list[Target],
    root_field: str,
    include_healed: bool,
    rank_offset: int | None,
    bank_capacity: int = 1,
) -> dict:
    if bank_capacity < 1:
        raise ValueError("bank_capacity must be positive")
    root_targets: dict[int, list[int]] = {}
    slot_target: list[int] = []
    slot_copy: list[int] = []
    for target_id, target in enumerate(targets):
        if target.kind == "Q" and not include_healed:
            continue
        copies = bank_capacity if target.kind == "E" else 1
        for copy in range(copies):
            slot_id = len(slot_target)
            slot_target.append(target_id)
            slot_copy.append(copy)
            for root in getattr(target, root_field):
                root_targets.setdefault(root, []).append(slot_id)

    target_owner = [-1] * len(slot_target)
    matched = 0

    def augment(
        source_id: int,
        cutoff: int,
        seen_sources: set[int],
        seen_targets: set[int],
    ) -> bool:
        if source_id in seen_sources:
            return False
        seen_sources.add(source_id)
        source = sources[source_id]
        for root in getattr(source, root_field):
            for slot_id in root_targets.get(root, ()):
                target = targets[slot_target[slot_id]]
                if target.coordinate > cutoff:
                    break
                if rank_offset is not None and target.rank > source.rank + rank_offset:
                    continue
                if slot_id in seen_targets:
                    continue
                seen_targets.add(slot_id)
                owner = target_owner[slot_id]
                if owner < 0 or augment(owner, cutoff, seen_sources, seen_targets):
                    target_owner[slot_id] = source_id
                    return True
        return False

    first_failure = None
    for source_id, source in enumerate(sources):
        seen_sources: set[int] = set()
        seen_targets: set[int] = set()
        if augment(source_id, source.value, seen_sources, seen_targets):
            matched += 1
            continue
        first_failure = {
            "X": source.value,
            "source_rank": source.rank,
            "left_size": len(seen_sources),
            "neighbor_size": len(seen_targets),
            "deficit": len(seen_sources) - len(seen_targets),
            "left": sorted(sources[s].value for s in seen_sources),
            "neighbors": [
                {
                    "kind": targets[t].kind,
                    "coordinate": targets[t].coordinate,
                    "value": targets[t].value,
                    "rank": targets[t].rank,
                    "copy": slot_copy[slot],
                }
                for slot in sorted(seen_targets, key=lambda slot: (
                    targets[slot_target[slot]].coordinate,
                    targets[slot_target[slot]].kind,
                    targets[slot_target[slot]].value,
                    slot_copy[slot],
                ))
                for t in (slot_target[slot],)
            ],
        }
        break

    return {
        "root_relation": root_field,
        "targets": "E+Q" if include_healed else "E",
        "rank_offset": rank_offset,
        "bank_capacity": bank_capacity,
        "matched_before_failure": matched,
        "passed": first_failure is None,
        "first_failure": first_failure,
    }


def dinic_gate(
    sources: list[Source],
    targets: list[Target],
    bank_capacity: int,
) -> dict:
    """Incremental exact max flow on H -> leaf -> (E or Q)."""
    if bank_capacity < 1:
        raise ValueError("bank_capacity must be positive")
    root_values = sorted(target.value for target in targets if target.kind == "E")
    root_id = {value: index for index, value in enumerate(root_values)}

    super_source = 0
    sink = 1
    root_offset = 2
    source_offset = root_offset + len(root_values)
    target_offset = source_offset + len(sources)
    flow = Dinic(target_offset + len(targets))

    target_cursor = 0
    active_targets = 0
    matched = 0
    first_failure = None
    for source_id, source in enumerate(sources):
        while (
            target_cursor < len(targets)
            and targets[target_cursor].coordinate <= source.value
        ):
            target = targets[target_cursor]
            target_node = target_offset + target_cursor
            capacity = bank_capacity if target.kind == "E" else 1
            for root in target.all_lower_roots:
                flow.add_edge(root_offset + root_id[root], target_node, capacity)
            flow.add_edge(target_node, sink, capacity)
            target_cursor += 1
            active_targets += 1

        source_node = source_offset + source_id
        flow.add_edge(super_source, source_node, 1)
        for root in source.all_lower_roots:
            flow.add_edge(source_node, root_offset + root_id[root], 1)

        if flow.flow(super_source, sink, 1) == 1:
            matched += 1
            continue

        reachable = flow.reachable(super_source)
        left_ids = [
            index for index in range(source_id + 1)
            if source_offset + index in reachable
        ]
        reachable_roots = frozenset().union(*(
            sources[index].all_lower_roots for index in left_ids
        ))
        neighbor_ids = [
            index for index in range(active_targets)
            if targets[index].all_lower_roots & reachable_roots
        ]
        neighbor_capacity = sum(
            bank_capacity if targets[index].kind == "E" else 1
            for index in neighbor_ids
        )
        cut_capacity = flow.cut_capacity(reachable)
        if cut_capacity != matched:
            raise AssertionError(("min-cut mismatch", cut_capacity, matched))
        first_failure = {
            "X": source.value,
            "source_rank": source.rank,
            "left_size": len(left_ids),
            "neighbor_vertices": len(neighbor_ids),
            "neighbor_capacity": neighbor_capacity,
            "flow_value": matched,
            "min_cut_capacity": cut_capacity,
            "flow_deficit": source_id + 1 - matched,
            "residual_reachable_roots": sum(
                root_offset + index in reachable
                for index in range(len(root_values))
            ),
            "residual_reachable_targets": sum(
                target_offset + index in reachable
                for index in range(active_targets)
            ),
            "left_prefix": [sources[index].value for index in left_ids[:200]],
            "neighbors_prefix": [
                {
                    "kind": targets[index].kind,
                    "coordinate": targets[index].coordinate,
                    "value": targets[index].value,
                    "rank": targets[index].rank,
                    "capacity": (
                        bank_capacity if targets[index].kind == "E" else 1
                    ),
                }
                for index in neighbor_ids[:200]
            ],
        }
        break

    return {
        "root_relation": "all_lower_roots",
        "targets": "E+Q",
        "rank_offset": None,
        "bank_capacity": bank_capacity,
        "engine": "incremental_tripartite_dinic",
        "matched_before_failure": matched,
        "passed": first_failure is None,
        "first_failure": first_failure,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("expanded", "dinic"), default="expanded")
    parser.add_argument("--capacities", default="1,2,3,4,8")
    args = parser.parse_args()
    if args.limit < 100:
        raise ValueError("limit must be at least 100")

    sources, targets, counts = build(args.limit)
    sys.setrecursionlimit(max(10_000, 2 * len(sources) + 100))
    capacities = tuple(int(value) for value in args.capacities.split(","))
    gates = []
    if args.mode == "dinic":
        gates.extend(dinic_gate(sources, targets, capacity) for capacity in capacities)
    else:
        for root_field in ("critical_roots", "all_lower_roots"):
            gates.append(hall_gate(sources, targets, root_field, False, None))
            gates.append(hall_gate(sources, targets, root_field, True, None))
            gates.append(hall_gate(sources, targets, root_field, True, 0))
            gates.append(hall_gate(sources, targets, root_field, True, 1))
        for bank_capacity in capacities:
            if bank_capacity == 1:
                continue
            gates.append(hall_gate(
                sources, targets, "all_lower_roots", True, None, bank_capacity
            ))

    result = {
        "schema_version": 1,
        "limit": args.limit,
        "mode": args.mode,
        "critical_relation": (
            "follow every missing endpoint of rank r-1 in a factor pair "
            "attaining the death-rank maximum"
        ),
        "all_lower_relation": (
            "follow every missing endpoint of lower rank in every factor pair"
        ),
        "shared_leaf_edge": (
            "a hard source and E/Q target are adjacent when their obstruction "
            "shadows share a splitless leaf"
        ),
        "counts": counts,
        "gates": gates,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "limit": args.limit,
        "counts": counts,
        "gates": [
            {
                "root_relation": gate["root_relation"],
                "targets": gate["targets"],
                "rank_offset": gate["rank_offset"],
                "bank_capacity": gate["bank_capacity"],
                "passed": gate["passed"],
                "first_X": (
                    None if gate["first_failure"] is None
                    else gate["first_failure"]["X"]
                ),
            }
            for gate in gates
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
