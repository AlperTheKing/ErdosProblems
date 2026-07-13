#!/usr/bin/env python3
"""Independent audit of the shortest-support Hall counterexample family.

This file intentionally imports no project modules and does not read the
original verifier.  It reconstructs G_t directly from the theorem statement.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, deque
from math import comb
from pathlib import Path


CLASS_ORDER = ("L", "A", "B", "C", "D", "E", "R")
CHAIN_BLOCKS = tuple(zip(CLASS_ORDER, CLASS_ORDER[1:]))


def vertex(cls: str, index: int) -> str:
    return f"{cls}{index}"


def edge(x: str, y: str) -> tuple[str, str]:
    assert x != y
    return (x, y) if x < y else (y, x)


def build_graph(t: int) -> tuple[tuple[str, ...], frozenset[tuple[str, str]]]:
    assert t >= 1
    vertices = [vertex(cls, i) for cls in CLASS_ORDER for i in range(t)]
    vertices.extend(("u", "w", "v"))
    edges: set[tuple[str, str]] = set()

    for left, right in CHAIN_BLOCKS:
        for i in range(t):
            for j in range(t):
                edges.add(edge(vertex(left, i), vertex(right, j)))
    for i in range(t):
        for j in range(t):
            edges.add(edge(vertex("L", i), vertex("R", j)))
    for i in range(t):
        edges.add(edge(vertex("L", i), "u"))
        edges.add(edge("v", vertex("R", i)))
    edges.add(edge("u", "w"))
    edges.add(edge("w", "v"))
    return tuple(vertices), frozenset(edges)


def adjacency(vertices: tuple[str, ...], edges: frozenset[tuple[str, str]]):
    adj = {x: set() for x in vertices}
    for x, y in edges:
        adj[x].add(y)
        adj[y].add(x)
    return adj


def triangle_count(vertices, edges) -> int:
    adj = adjacency(vertices, edges)
    count = 0
    for i, x in enumerate(vertices):
        for j in range(i + 1, len(vertices)):
            y = vertices[j]
            if y not in adj[x]:
                continue
            for z in vertices[j + 1 :]:
                count += int(z in adj[x] and z in adj[y])
    return count


def canonical_side(x: str) -> int:
    if x in ("u", "v"):
        return 1
    if x == "w":
        return 0
    return 0 if x[0] in ("L", "B", "D", "R") else 1


def bad_edges_for_sides(edges, side) -> frozenset[tuple[str, str]]:
    return frozenset((x, y) for x, y in edges if side[x] == side[y])


def packed_cycles(t: int):
    for i in range(t):
        for j in range(t):
            yield (
                vertex("L", i),
                vertex("A", j),
                vertex("B", (i + j) % t),
                vertex("C", i),
                vertex("D", j),
                vertex("E", (i + j) % t),
                vertex("R", j),
            )


def cycle_edges(cycle: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    return tuple(edge(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle)))


def check_packing(t: int, graph_edges) -> dict:
    usage: Counter[tuple[str, str]] = Counter()
    cycles = list(packed_cycles(t))
    for cyc in cycles:
        assert len(cyc) == 7 and len(set(cyc)) == 7
        for e in cycle_edges(cyc):
            assert e in graph_edges
            usage[e] += 1

    wide_edges = {
        e
        for e in graph_edges
        if e not in {edge("u", "w"), edge("w", "v")}
        and "u" not in e
        and "v" not in e
        and "w" not in e
    }
    thin_edges = set(graph_edges) - wide_edges
    collisions = {e: k for e, k in usage.items() if k != 1}
    assert not collisions
    assert set(usage) == wide_edges
    assert all(usage[e] == 0 for e in thin_edges)
    assert len(cycles) == t * t
    assert len(usage) == 7 * t * t
    return {
        "cycles": len(cycles),
        "packed_edges": len(usage),
        "wide_edges": len(wide_edges),
        "thin_edges_outside_packing": len(thin_edges),
        "edge_collisions": 0,
    }


def connected(vertices, edges) -> bool:
    adj = adjacency(vertices, edges)
    seen = {vertices[0]}
    todo = [vertices[0]]
    while todo:
        x = todo.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                todo.append(y)
    return len(seen) == len(vertices)


def shortest_path_data(vertices, edges, start: str, target: str):
    adj = adjacency(vertices, edges)
    dist = {start: 0}
    ways = {start: 1}
    predecessors: dict[str, list[str]] = {start: []}
    queue = deque([start])
    while queue:
        x = queue.popleft()
        for y in sorted(adj[x]):
            nd = dist[x] + 1
            if y not in dist:
                dist[y] = nd
                ways[y] = ways[x]
                predecessors[y] = [x]
                queue.append(y)
            elif dist[y] == nd:
                ways[y] += ways[x]
                predecessors[y].append(x)
    assert target in dist

    paths: list[tuple[str, ...]] = []

    def recover(x: str, suffix: tuple[str, ...]):
        if x == start:
            paths.append((start,) + suffix)
            return
        for p in predecessors[x]:
            recover(p, (x,) + suffix)

    recover(target, ())
    assert len(paths) == ways[target]
    return dist[target], ways[target], tuple(paths)


def check_shortest_supports(t: int, vertices, edges) -> dict:
    sides = {x: canonical_side(x) for x in vertices}
    bad = bad_edges_for_sides(edges, sides)
    expected_bad = {
        edge(vertex("L", i), vertex("R", j))
        for i in range(t)
        for j in range(t)
    }
    assert bad == expected_bad
    blue = frozenset(set(edges) - set(bad))
    assert connected(vertices, blue)

    support: set[tuple[str, str]] = set()
    unique_paths = []
    for i in range(t):
        for j in range(t):
            start, target = vertex("L", i), vertex("R", j)
            distance, ways, paths = shortest_path_data(vertices, blue, start, target)
            expected = (start, "u", "w", "v", target)
            assert distance == 4
            assert ways == 1
            assert paths == (expected,)
            unique_paths.append(paths[0])
            support.update(edge(paths[0][k], paths[0][k + 1]) for k in range(4))
    assert len(support) == 2 * t + 2
    return {
        "canonical_bad_edges": len(bad),
        "blue_connected": True,
        "shortest_distance": 4,
        "shortest_path_count_per_bad_edge": 1,
        "support_edges": len(support),
        "hall_defect": t * t - (2 * t + 2),
    }


def full_cut_audit(t: int, vertices, edges) -> dict:
    index = {x: i for i, x in enumerate(vertices)}
    encoded_edges = tuple((index[x], index[y]) for x, y in edges)
    best = len(edges) + 1
    minimizers: list[int] = []
    cycle_edge_indices = [tuple((index[x], index[y]) for x, y in cycle_edges(cyc)) for cyc in packed_cycles(t)]
    for mask in range(1 << len(vertices)):
        bad = sum(((mask >> x) & 1) == ((mask >> y) & 1) for x, y in encoded_edges)
        if bad < best:
            best = bad
            minimizers = [mask]
        elif bad == best:
            minimizers.append(mask)
        # Independently enforce the packing lower bound for every coloring.
        for cyc_edges in cycle_edge_indices:
            assert any(((mask >> x) & 1) == ((mask >> y) & 1) for x, y in cyc_edges)
    assert best == t * t
    assert len(minimizers) == 2
    assert minimizers[1] == ((1 << len(vertices)) - 1) ^ minimizers[0]
    return {
        "cuts_checked": 1 << len(vertices),
        "minimum_bad_edges": best,
        "minimizing_cuts": len(minimizers),
        "minimum_cut_orbits_mod_complement": 1,
    }


def complete_bipartite_bad(t: int, x: int, y: int) -> int:
    return x * y + (t - x) * (t - y)


def star_bad(t: int, class_ones: int, singleton_side: int) -> int:
    return class_ones if singleton_side else t - class_ones


def orbit_bad_count(t: int, counts: tuple[int, ...], bits: tuple[int, int, int]) -> int:
    by_class = dict(zip(CLASS_ORDER, counts))
    u, w, v = bits
    bad = 0
    for left, right in CHAIN_BLOCKS:
        bad += complete_bipartite_bad(t, by_class[left], by_class[right])
    bad += complete_bipartite_bad(t, by_class["L"], by_class["R"])
    bad += star_bad(t, by_class["L"], u)
    bad += int(u == w) + int(w == v)
    bad += star_bad(t, by_class["R"], v)
    return bad


def orbit_cut_audit(t: int) -> dict:
    best = 7 * t * t + 2 * t + 3
    best_states = []
    assignment_total = 0
    minimizing_assignment_total = 0
    orbit_count = 0
    for counts in itertools.product(range(t + 1), repeat=7):
        multiplicity = 1
        for k in counts:
            multiplicity *= comb(t, k)
        for bits in itertools.product((0, 1), repeat=3):
            orbit_count += 1
            assignment_total += multiplicity
            bad = orbit_bad_count(t, counts, bits)
            if bad < best:
                best = bad
                best_states = [(counts, bits, multiplicity)]
                minimizing_assignment_total = multiplicity
            elif bad == best:
                best_states.append((counts, bits, multiplicity))
                minimizing_assignment_total += multiplicity
    assert orbit_count == (t + 1) ** 7 * 8
    assert assignment_total == 1 << (7 * t + 3)
    assert best == t * t
    assert len(best_states) == 2
    assert minimizing_assignment_total == 2
    a_counts, a_bits, _ = best_states[0]
    b_counts, b_bits, _ = best_states[1]
    assert b_counts == tuple(t - x for x in a_counts)
    assert b_bits == tuple(1 - x for x in a_bits)
    return {
        "cut_orbits_checked": orbit_count,
        "represented_labeled_cuts": assignment_total,
        "minimum_bad_edges": best,
        "minimizing_orbits": len(best_states),
        "minimizing_labeled_cuts": minimizing_assignment_total,
        "minimum_cut_orbits_mod_complement": 1,
    }


def audit_t(t: int) -> dict:
    vertices, edges = build_graph(t)
    assert len(vertices) == 7 * t + 3
    assert len(edges) == 7 * t * t + 2 * t + 2
    assert triangle_count(vertices, edges) == 0
    result = {
        "t": t,
        "vertices": len(vertices),
        "edges": len(edges),
        "triangles": 0,
        "packing": check_packing(t, edges),
        "shortest_support": check_shortest_supports(t, vertices, edges),
    }
    if t in (1, 2):
        result["full_cut_audit"] = full_cut_audit(t, vertices, edges)
    if t in (3, 4):
        result["orbit_cut_audit"] = orbit_cut_audit(t)
    return result


def canonical_json(data) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structural-max-t", type=int, default=8)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    assert args.structural_max_t >= 4

    results = [audit_t(t) for t in range(1, args.structural_max_t + 1)]
    payload = {
        "verdict": "PASS",
        "independence": "standard library only; no project verifier imports",
        "structural_t_range": [1, args.structural_max_t],
        "full_cut_t": [1, 2],
        "orbit_cut_t": [3, 4],
        "results": results,
    }
    encoded = canonical_json(payload)
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_bytes(encoded)
    print(encoded.decode("utf-8"), end="")
    print("RESULT_SHA256=" + hashlib.sha256(encoded).hexdigest().upper())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
