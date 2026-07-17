#!/usr/bin/env python3
"""Exact gates for arithmetic strengthenings of the C60 cut theorem.

The main diagnostic replaces the global C60 objective by a root-prefix
objective.  For a fixed ambient cutoff X and an even-root cutoff Y, only
hard roots at most Y carry source capacity and only seed-2 arcs on chains
rooted at most Y carry unit capacity.  Unlimited splitless and unary arcs
are unchanged.  A flow smaller than the number of hard roots at most Y is
an exact counterexample to root-order transport.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def factor_pairs(n: int) -> list[tuple[int, int]]:
    product = n + 1
    out: list[tuple[int, int]] = []
    a = 2
    while a * a < product:
        if product % a == 0:
            b = product // a
            if allowed(a) and allowed(b):
                out.append((a, b))
        a += 1
    return out


def hard_shape(n: int, pairs: list[tuple[int, int]]) -> bool:
    if n % 2 or not pairs:
        return False
    if (n + 1) % 3:
        return True
    parent = (n + 1) // 3
    return not (allowed(parent) and parent != 3)


def seed_root(n: int) -> int:
    while n % 2:
        n = (n + 1) // 2
    return n


@dataclass
class Edge:
    to: int
    reverse: int
    capacity: int
    initial: int


class Dinic:
    def __init__(self, size: int) -> None:
        self.graph: list[list[Edge]] = [[] for _ in range(size)]

    def add(self, u: int, v: int, capacity: int) -> None:
        if capacity <= 0:
            return
        forward = Edge(v, len(self.graph[v]), capacity, capacity)
        reverse = Edge(u, len(self.graph[u]), 0, 0)
        self.graph[u].append(forward)
        self.graph[v].append(reverse)

    def max_flow(self, source: int, sink: int, limit: int | None = None) -> int:
        total = 0
        size = len(self.graph)
        while limit is None or total < limit:
            level = [-1] * size
            level[source] = 0
            queue = deque([source])
            while queue:
                u = queue.popleft()
                for edge in self.graph[u]:
                    if edge.capacity and level[edge.to] < 0:
                        level[edge.to] = level[u] + 1
                        queue.append(edge.to)
            if level[sink] < 0:
                return total
            cursor = [0] * size

            def send(u: int, amount: int) -> int:
                if u == sink:
                    return amount
                while cursor[u] < len(self.graph[u]):
                    edge = self.graph[u][cursor[u]]
                    if edge.capacity and level[edge.to] == level[u] + 1:
                        pushed = send(edge.to, min(amount, edge.capacity))
                        if pushed:
                            edge.capacity -= pushed
                            self.graph[edge.to][edge.reverse].capacity += pushed
                            return pushed
                    cursor[u] += 1
                return 0

            while True:
                allowance = 10**18 if limit is None else limit - total
                pushed = send(source, allowance)
                if not pushed:
                    break
                total += pushed
        return total

    def reachable(self, source: int) -> set[int]:
        seen = {source}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for edge in self.graph[u]:
                if edge.capacity and edge.to not in seen:
                    seen.add(edge.to)
                    queue.append(edge.to)
        return seen

    def augment_one(self, source: int, sink: int) -> dict | None:
        """Augment one integral unit, allowing arbitrary residual rerouting."""

        parent: list[tuple[int, int] | None] = [None] * len(self.graph)
        parent[source] = (-1, -1)
        queue = deque([source])
        while queue and parent[sink] is None:
            u = queue.popleft()
            for index, edge in enumerate(self.graph[u]):
                if edge.capacity <= 0 or parent[edge.to] is not None:
                    continue
                parent[edge.to] = (u, index)
                if edge.to == sink:
                    break
                queue.append(edge.to)
        if parent[sink] is None:
            return None
        vertices = [sink]
        reverse_edges = 0
        v = sink
        while v != source:
            item = parent[v]
            if item is None:
                raise RuntimeError("broken augmenting path")
            u, index = item
            edge = self.graph[u][index]
            reverse_edges += int(edge.initial == 0)
            edge.capacity -= 1
            self.graph[v][edge.reverse].capacity += 1
            v = u
            vertices.append(v)
        vertices.reverse()
        return {"vertices": vertices, "reverse_edges": reverse_edges}


@dataclass
class ArithmeticData:
    limit: int
    values: list[int]
    pairs: dict[int, list[tuple[int, int]]]
    generated: set[int]
    holes: set[int]
    hard_holes: set[int]
    splitless: set[int]


def arithmetic_data(limit: int) -> ArithmeticData:
    values = [n for n in range(2, limit + 1) if allowed(n)]
    pairs = {n: factor_pairs(n) for n in values}
    generated: set[int] = set()
    for n in values:
        if n in (2, 3) or any(a in generated and b in generated for a, b in pairs[n]):
            generated.add(n)
    holes = set(values) - generated
    hard_holes = {n for n in holes if hard_shape(n, pairs[n])}
    splitless = {n for n in holes if n not in (2, 3) and not pairs[n]}
    return ArithmeticData(limit, values, pairs, generated, holes, hard_holes, splitless)


def root_prefix_cut(data: ArithmeticData, root_cutoff: int) -> dict:
    """Return the exact minimum cut for the root-prefix objective."""

    source, sink = data.limit + 1, data.limit + 2
    demand = {h for h in data.hard_holes if h <= root_cutoff}
    finite_seed_count = sum(
        2 * n - 1 <= data.limit and seed_root(n) <= root_cutoff
        for n in data.holes
    )
    infinity = len(demand) + finite_seed_count + 1
    flow = Dinic(data.limit + 3)
    for h in sorted(demand):
        flow.add(source, h, 1)
    for root in sorted(data.splitless):
        flow.add(source, root, infinity)
    for n in sorted(data.holes):
        for a, b in data.pairs[n]:
            if (a in data.generated) != (b in data.generated):
                flow.add(n, b if a in data.generated else a, infinity)
        child = 2 * n - 1
        if child <= data.limit and seed_root(n) <= root_cutoff:
            flow.add(n, sink if child in data.generated else child, 1)
    value = flow.max_flow(source, sink)
    reachable = flow.reachable(source)
    source_side = data.holes & reachable
    hard_inside = demand & source_side
    exits = {
        n
        for n in source_side
        if seed_root(n) <= root_cutoff
        and 2 * n - 1 <= data.limit
        and 2 * n - 1 not in source_side
    }
    if value != len(demand - source_side) + len(exits):
        raise RuntimeError("cut replay mismatch")
    for root in data.splitless:
        if root not in source_side:
            raise RuntimeError("splitless root omitted")
    for n in source_side:
        for a, b in data.pairs[n]:
            if a in data.generated and b not in source_side:
                raise RuntimeError(("unary closure", n, a, b))
            if b in data.generated and a not in source_side:
                raise RuntimeError(("unary closure", n, b, a))
    return {
        "limit": data.limit,
        "root_cutoff": root_cutoff,
        "demand": len(demand),
        "flow": value,
        "margin": value - len(demand),
        "hard_inside": sorted(hard_inside),
        "exits": sorted(exits),
        "source_side_size": len(source_side),
    }


def scan(max_limit: int, ambient_limits: list[int] | None = None) -> dict:
    if ambient_limits is None:
        ambient_limits = list(range(2, max_limit + 1))
    first_failure = None
    tight = []
    checked = 0
    for limit in ambient_limits:
        data = arithmetic_data(limit)
        roots = [n for n in data.values if n % 2 == 0]
        for root_cutoff in roots:
            row = root_prefix_cut(data, root_cutoff)
            checked += 1
            if row["margin"] < 0:
                first_failure = row
                return {
                    "checked": checked,
                    "first_failure": first_failure,
                    "tight_sample": tight[-20:],
                }
            if row["demand"] and row["margin"] == 0:
                tight.append(
                    {
                        "limit": limit,
                        "root_cutoff": root_cutoff,
                        "demand": row["demand"],
                    }
                )
    return {
        "checked": checked,
        "first_failure": first_failure,
        "tight_sample": tight[-20:],
    }


def incremental_root_scan(limit: int) -> dict:
    """Check every relevant root prefix at one ambient cutoff.

    Seed arcs are activated in increasing root order.  The maximum flow can
    only lose reserve when a hard source arc is added, so exact checks are
    needed only at hard-hole roots.
    """

    data = arithmetic_data(limit)
    source, sink = limit + 1, limit + 2
    finite_bound = len(data.hard_holes) + sum(
        2 * n - 1 <= limit for n in data.holes
    )
    infinity = finite_bound + 1
    flow = Dinic(limit + 3)
    for root in sorted(data.splitless):
        flow.add(source, root, infinity)
    for n in sorted(data.holes):
        for a, b in data.pairs[n]:
            if (a in data.generated) != (b in data.generated):
                flow.add(n, b if a in data.generated else a, infinity)

    seed_by_root: dict[int, list[tuple[int, int]]] = {}
    for n in sorted(data.holes):
        child = 2 * n - 1
        if child <= limit:
            seed_by_root.setdefault(seed_root(n), []).append(
                (n, sink if child in data.generated else child)
            )

    total_flow = 0
    demand = 0
    minimum_reserve = 10**18
    tight: list[dict] = []
    first_failure = None
    checks = 0
    augmentations: list[dict] = []
    roots = [n for n in data.values if n % 2 == 0]
    for root in roots:
        for u, v in seed_by_root.get(root, []):
            flow.add(u, v, 1)
        if root not in data.hard_holes:
            continue
        flow.add(source, root, 1)
        demand += 1
        path = flow.augment_one(source, sink) if total_flow < demand else None
        if path is not None:
            total_flow += 1
            path["root_cutoff"] = root
            augmentations.append(path)
        reserve = total_flow - demand
        minimum_reserve = min(minimum_reserve, reserve)
        checks += 1
        if reserve == 0:
            tight.append({"root_cutoff": root, "demand": demand, "flow": total_flow})
        if reserve < 0:
            first_failure = {
                "root_cutoff": root,
                "demand": demand,
                "flow": total_flow,
                "reserve": reserve,
            }
            break
    source_roots = data.splitless | data.hard_holes
    directly_healed: set[int] = set()
    for root in source_roots:
        node = root
        while 2 * node - 1 <= limit:
            child = 2 * node - 1
            if child in data.generated:
                directly_healed.add(root)
                break
            if child not in data.holes:
                raise RuntimeError(("seed chain left partition", root, child))
            node = child
    direct_count = 0
    hard_count = 0
    first_direct_failure = None
    for root in roots:
        direct_count += int(root in directly_healed)
        if root in data.hard_holes:
            hard_count += 1
            if first_direct_failure is None and direct_count < hard_count:
                first_direct_failure = {
                    "root_cutoff": root,
                    "hard_demand": hard_count,
                    "direct_sources": direct_count,
                }

    return {
        "limit": limit,
        "hard_checks": checks,
        "minimum_reserve": None if minimum_reserve == 10**18 else minimum_reserve,
        "first_failure": first_failure,
        "tight_count": len(tight),
        "tight_sample": tight[:20],
        "final_demand": demand,
        "final_flow": total_flow,
        "final_reserve": total_flow - demand,
        "reverse_augmentations": sum(p["reverse_edges"] > 0 for p in augmentations),
        "first_reverse": next((p for p in augmentations if p["reverse_edges"] > 0), None),
        "maximum_path_length": max((len(p["vertices"]) - 1 for p in augmentations), default=0),
        "maximum_path": max(augmentations, key=lambda p: len(p["vertices"]), default=None),
        "splitless_source_paths": sum(p["vertices"][1] in data.splitless for p in augmentations),
        "hard_source_paths": sum(p["vertices"][1] in data.hard_holes for p in augmentations),
        "unary_paths": sum(
            any(
                v != sink and v != 2 * u - 1
                for u, v in zip(p["vertices"][1:-1], p["vertices"][2:])
            )
            for p in augmentations
        ),
        "maximum_unary_edges": max(
            (
                sum(
                    v != sink and v != 2 * u - 1
                    for u, v in zip(p["vertices"][1:-1], p["vertices"][2:])
                )
                for p in augmentations
            ),
            default=0,
        ),
        "first_hard_source": next(
            (p for p in augmentations if p["vertices"][1] in data.hard_holes), None
        ),
        "first_unary_path": next(
            (
                p
                for p in augmentations
                if any(
                    v != sink and v != 2 * u - 1
                    for u, v in zip(p["vertices"][1:-1], p["vertices"][2:])
                )
            ),
            None,
        ),
        "diagnostic_paths": [
            p
            for p in augmentations
            if p["root_cutoff"] in {54, 74, 144, 186, 318, 362, 377, 4146, 4806}
        ],
        "path_certificate": augmentations if limit <= 500 else None,
        "directly_healed_sources": len(directly_healed),
        "first_direct_bank_failure": first_direct_failure,
    }


def direct_bank_scan(max_limit: int) -> dict:
    """Find the first ambient/root prefix where direct chains are insufficient."""

    data = arithmetic_data(max_limit)
    source_roots = data.splitless | data.hard_holes
    terminal_at: dict[int, list[int]] = {}
    terminal: dict[int, int | None] = {}
    for root in sorted(source_roots):
        node = root
        hit = None
        while 2 * node - 1 <= max_limit:
            child = 2 * node - 1
            if child in data.generated:
                hit = child
                terminal_at.setdefault(child, []).append(root)
                break
            node = child
        terminal[root] = hit

    tree = [0] * (max_limit + 2)

    def add(index: int) -> None:
        while index < len(tree):
            tree[index] += 1
            index += index & -index

    def prefix(index: int) -> int:
        total = 0
        while index:
            total += tree[index]
            index -= index & -index
        return total

    hard = sorted(data.hard_holes)
    hard_seen: list[int] = []
    hard_cursor = 0
    first_failure = None
    checks = 0
    for ambient in range(2, max_limit + 1):
        for root in terminal_at.get(ambient, []):
            add(root)
        while hard_cursor < len(hard) and hard[hard_cursor] <= ambient:
            hard_seen.append(hard[hard_cursor])
            hard_cursor += 1
        for rank, root_cutoff in enumerate(hard_seen, start=1):
            checks += 1
            available = prefix(root_cutoff)
            if available < rank:
                first_failure = {
                    "ambient": ambient,
                    "root_cutoff": root_cutoff,
                    "hard_demand": rank,
                    "direct_sources": available,
                    "direct_sources_list": sorted(
                        r
                        for r in source_roots
                        if r <= root_cutoff and terminal[r] is not None and terminal[r] <= ambient
                    ),
                    "hard_roots": hard_seen[:rank],
                }
                return {
                    "max_limit": max_limit,
                    "checks": checks,
                    "first_failure": first_failure,
                }
    return {"max_limit": max_limit, "checks": checks, "first_failure": None}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-limit", type=int, default=500)
    parser.add_argument("--ambient", nargs="*", type=int)
    parser.add_argument("--incremental-limit", type=int)
    parser.add_argument("--direct-scan-limit", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.max_limit < 2:
        raise ValueError("max-limit must be at least 2")
    if args.direct_scan_limit is not None:
        result = direct_bank_scan(args.direct_scan_limit)
    elif args.incremental_limit is not None:
        result = incremental_root_scan(args.incremental_limit)
    else:
        result = scan(args.max_limit, args.ambient or None)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
