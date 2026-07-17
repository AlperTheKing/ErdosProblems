#!/usr/bin/env python3
"""Exact incremental max-flow/min-cut gate for the C90 ordered bank.

At every ambient hard-hole cutoff X, the arithmetic network contains all
splitless and hard source arcs, unary arcs, and seed edges whose endpoints
are at most X.  The network is monotone in X, so one exact residual flow can
be extended and audited at every hard arrival.

The saved output contains every hard-cutoff value and every tight min-cut.
Replay rebuilds the integer network from scratch and compares the full object.
No floating-point arithmetic is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import deque
from dataclasses import dataclass
from pathlib import Path


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def factor_pairs(n: int) -> tuple[tuple[int, int], ...]:
    product = n + 1
    result: list[tuple[int, int]] = []
    for a in range(2, math.isqrt(product) + 1):
        if product % a:
            continue
        b = product // a
        if a < b and allowed(a) and allowed(b):
            result.append((a, b))
    return tuple(result)


def hard_shape(n: int, pairs: tuple[tuple[int, int], ...]) -> bool:
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


class Dinic:
    def __init__(self, vertices: int) -> None:
        self.graph: list[list[Edge]] = [[] for _ in range(vertices)]

    def add(self, source: int, target: int, capacity: int) -> None:
        if capacity < 0:
            raise RuntimeError("negative capacity")
        forward = Edge(target, len(self.graph[target]), capacity)
        reverse = Edge(source, len(self.graph[source]), 0)
        self.graph[source].append(forward)
        self.graph[target].append(reverse)

    def max_flow(self, source: int, sink: int) -> int:
        total = 0
        vertices = len(self.graph)
        while True:
            level = [-1] * vertices
            level[source] = 0
            queue: deque[int] = deque([source])
            while queue:
                u = queue.popleft()
                for edge in self.graph[u]:
                    if edge.capacity > 0 and level[edge.to] < 0:
                        level[edge.to] = level[u] + 1
                        queue.append(edge.to)
            if level[sink] < 0:
                return total
            cursor = [0] * vertices

            def send(u: int, amount: int) -> int:
                if u == sink:
                    return amount
                while cursor[u] < len(self.graph[u]):
                    index = cursor[u]
                    edge = self.graph[u][index]
                    if edge.capacity > 0 and level[edge.to] == level[u] + 1:
                        pushed = send(edge.to, min(amount, edge.capacity))
                        if pushed:
                            edge.capacity -= pushed
                            self.graph[edge.to][edge.reverse].capacity += pushed
                            return pushed
                    cursor[u] += 1
                return 0

            while True:
                pushed = send(source, 10**18)
                if not pushed:
                    break
                total += pushed

    def reachable(self, source: int) -> set[int]:
        seen = {source}
        queue: deque[int] = deque([source])
        while queue:
            u = queue.popleft()
            for edge in self.graph[u]:
                if edge.capacity > 0 and edge.to not in seen:
                    seen.add(edge.to)
                    queue.append(edge.to)
        return seen


@dataclass(frozen=True)
class Arithmetic:
    limit: int
    values: tuple[int, ...]
    pairs: dict[int, tuple[tuple[int, int], ...]]
    generated: frozenset[int]
    holes: frozenset[int]
    hard_holes: frozenset[int]
    splitless: frozenset[int]
    unary: dict[int, tuple[tuple[int, int], ...]]


def arithmetic(limit: int) -> Arithmetic:
    values = tuple(n for n in range(2, limit + 1) if allowed(n))
    pairs = {n: factor_pairs(n) for n in values}
    generated: set[int] = set()
    for n in values:
        if n in (2, 3) or any(a in generated and b in generated for a, b in pairs[n]):
            generated.add(n)
    holes = set(values) - generated
    hard_holes = {n for n in holes if hard_shape(n, pairs[n])}
    splitless = {n for n in holes if not pairs[n]}
    unary: dict[int, tuple[tuple[int, int], ...]] = {}
    for n in holes:
        arcs: list[tuple[int, int]] = []
        for a, b in pairs[n]:
            if (a in generated) != (b in generated):
                arcs.append((b if a in generated else a, a if a in generated else b))
        unary[n] = tuple(sorted(arcs))  # (hole target, generated factor)
    return Arithmetic(
        limit,
        values,
        pairs,
        frozenset(generated),
        frozenset(holes),
        frozenset(hard_holes),
        frozenset(splitless),
        unary,
    )


def cut_certificate(
    data: Arithmetic,
    cutoff: int,
    reachable: set[int],
    demand: int,
    flow_value: int,
) -> dict:
    source_side = {n for n in data.holes if n <= cutoff and n in reachable}
    splitless = {n for n in data.splitless if n <= cutoff}
    if not splitless <= source_side:
        missing = sorted(splitless - source_side)[:20]
        raise RuntimeError(f"infinite splitless arc crosses min-cut: {missing}")
    for n in source_side:
        for target, witness in data.unary.get(n, ()):
            if target <= cutoff and target not in source_side:
                raise RuntimeError(
                    f"infinite unary arc crosses min-cut: {n}->{target} via {witness}"
                )
    hard = {n for n in data.hard_holes if n <= cutoff}
    hard_inside = hard & source_side
    hard_outside = hard - source_side
    exits: list[tuple[int, int]] = []
    for parent in sorted(source_side):
        child = 2 * parent - 1
        if child > cutoff:
            continue
        if child in data.generated or child not in source_side:
            exits.append((parent, child))
    capacity = len(hard_outside) + len(exits)
    if capacity != flow_value:
        raise RuntimeError(
            f"min-cut replay mismatch at {cutoff}: {capacity} != {flow_value}"
        )
    nonhard_inside = source_side - hard_inside
    subadditivity_violations: list[tuple[int, int, int]] = []
    for n in sorted(source_side):
        for a, b in data.pairs[n]:
            if a not in source_side and b not in source_side:
                subadditivity_violations.append((n, a, b))
    hard_shapes = {
        n for n in data.values if n <= cutoff and hard_shape(n, data.pairs[n])
    }
    selected_hard_shapes = hard_shapes & source_side
    c79_excess = len(selected_hard_shapes) - len(exits)
    selected_roots = {seed_root(n) for n in source_side}
    exiting_roots = {seed_root(parent) for parent, _child in exits}
    if len(exiting_roots) != len(exits):
        raise RuntimeError("two seed exits occur on one selected chain")
    if not exiting_roots <= selected_roots:
        raise RuntimeError("seed exit has no selected root")
    terminal_roots = selected_roots - exiting_roots
    selected_hard_roots = selected_roots & hard_inside
    selected_nonhard_roots = selected_roots - selected_hard_roots
    if len(exits) != len(selected_roots) - len(terminal_roots):
        raise RuntimeError("seed-chain balance identity failed")
    return {
        "cutoff": cutoff,
        "demand": demand,
        "flow": flow_value,
        "capacity": capacity,
        "source_side_size": len(source_side),
        "hard_inside": sorted(hard_inside),
        "hard_outside": sorted(hard_outside),
        "nonhard_inside": sorted(nonhard_inside),
        "seed_exits": [[a, b] for a, b in exits],
        "unary_closed": True,
        "splitless_contained": True,
        "subadditivity_violations": [list(row) for row in subadditivity_violations],
        "selected_hard_shapes": len(selected_hard_shapes),
        "c79_hard_minus_boundary": c79_excess,
        "selected_roots": len(selected_roots),
        "selected_hard_roots": len(selected_hard_roots),
        "selected_nonhard_roots": len(selected_nonhard_roots),
        "terminal_roots": len(terminal_roots),
        "ordered_bank_defect": len(terminal_roots) - len(selected_nonhard_roots),
    }


def scan(limit: int) -> dict:
    data = arithmetic(limit)
    source, sink = limit + 1, limit + 2
    finite_seed = sum(2 * n - 1 <= limit for n in data.holes)
    infinity = len(data.hard_holes) + finite_seed + 1
    flow = Dinic(limit + 3)
    value = 0
    demand = 0
    rows: list[dict] = []
    tight_rows: list[dict] = []
    failure_rows: list[dict] = []
    first_failure: dict | None = None

    for n in range(2, limit + 1):
        if n in data.holes:
            if n in data.splitless:
                flow.add(source, n, infinity)
            if n in data.hard_holes:
                flow.add(source, n, 1)
            for target, _witness in data.unary.get(n, ()):
                flow.add(n, target, infinity)

        if n % 2 == 1:
            parent = (n + 1) // 2
            if parent in data.holes:
                if n in data.generated:
                    flow.add(parent, sink, 1)
                elif n in data.holes:
                    flow.add(parent, n, 1)

        if n not in data.hard_holes:
            continue
        demand += 1
        value += flow.max_flow(source, sink)
        margin = value - demand
        if margin < 0 or margin == 0:
            cut = cut_certificate(data, n, flow.reachable(source), demand, value)
        else:
            cut = None
        rows.append({"cutoff": n, "demand": demand, "flow": value, "margin": margin})
        if margin == 0 and cut is not None:
            tight_rows.append(
                {
                    "cutoff": n,
                    "demand": demand,
                    "flow": value,
                    "source_side_size": cut["source_side_size"],
                    "hard_inside": len(cut["hard_inside"]),
                    "seed_exits": len(cut["seed_exits"]),
                }
            )
        if margin < 0:
            if cut is None:
                raise RuntimeError("failure has no min-cut")
            failure_rows.append(
                {
                    "cutoff": n,
                    "demand": demand,
                    "flow": value,
                    "margin": margin,
                    "source_side_size": cut["source_side_size"],
                    "hard_inside": len(cut["hard_inside"]),
                    "seed_exits": len(cut["seed_exits"]),
                }
            )
            if first_failure is None:
                first_failure = cut

    digest_payload = json.dumps(rows, separators=(",", ":"), sort_keys=True).encode("ascii")
    return {
        "schema_version": 1,
        "limit": limit,
        "allowed_values": len(data.values),
        "generated_values": len(data.generated),
        "holes": len(data.holes),
        "hard_holes": len(data.hard_holes),
        "splitless_holes": len(data.splitless),
        "infinity": infinity,
        "checked_hard_cutoffs": len(rows),
        "first_failure": first_failure,
        "tight_cut_count": len(tight_rows),
        "failure_cutoff_count": len(failure_rows),
        "minimum_margin": min((row["margin"] for row in rows), default=0),
        "maximum_margin": max((row["margin"] for row in rows), default=0),
        "rows_sha256": hashlib.sha256(digest_payload).hexdigest().upper(),
        "rows": rows,
        "tight_rows": tight_rows,
        "failure_rows": failure_rows,
    }


def verify(saved: dict) -> dict:
    rebuilt = scan(int(saved["limit"]))
    if rebuilt != saved:
        keys = sorted(set(rebuilt) | set(saved))
        differing = [key for key in keys if rebuilt.get(key) != saved.get(key)]
        raise RuntimeError(f"saved scan differs from exact replay: {differing}")
    return {
        "limit": rebuilt["limit"],
        "checked_hard_cutoffs": rebuilt["checked_hard_cutoffs"],
        "first_failure": rebuilt["first_failure"],
        "tight_cut_count": rebuilt["tight_cut_count"],
        "failure_cutoff_count": rebuilt["failure_cutoff_count"],
        "minimum_margin": rebuilt["minimum_margin"],
        "maximum_margin": rebuilt["maximum_margin"],
        "rows_sha256": rebuilt["rows_sha256"],
        "exact_replay": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--generate", type=int)
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.generate is not None:
        if args.output is None:
            parser.error("--generate requires --output")
        result = scan(args.generate)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(verify(result))
    else:
        saved = json.loads(args.verify.read_text(encoding="utf-8"))
        print(verify(saved))


if __name__ == "__main__":
    main()
