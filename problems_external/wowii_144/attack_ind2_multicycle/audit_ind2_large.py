#!/usr/bin/env python3
"""Reproducible large-order falsification audit for W144-IND2.

The exact lemma tested is: every connected graph G of girth at least five and
cycle rank at least two has a vertex v such that H=G-v is connected and
cyclic and phi(H) >= phi(G), where phi(X)=girth(X)+eta(X) and eta is the
maximum distance from a vertex to the center set.

This script deliberately computes every invariant from the graph itself.  It
does not use the W144 target inequality or an induced-tree oracle.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, deque
from pathlib import Path

import networkx as nx


def graph6(graph: nx.Graph) -> str:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(graph, header=False).decode().strip()


def cycle_rank(graph: nx.Graph) -> int:
    return graph.number_of_edges() - graph.number_of_nodes() + 1


def girth(graph: nx.Graph) -> int | None:
    """Exact undirected girth by BFS from every source."""
    best = graph.number_of_nodes() + 1
    for source in graph:
        distance = {source: 0}
        parent = {source: None}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            if 2 * distance[u] + 1 >= best:
                continue
            for v in graph[u]:
                if v not in distance:
                    distance[v] = distance[u] + 1
                    parent[v] = u
                    queue.append(v)
                elif parent[u] != v:
                    best = min(best, distance[u] + distance[v] + 1)
    return None if best == graph.number_of_nodes() + 1 else best


def center_depth(graph: nx.Graph) -> tuple[int, list[int], int]:
    """Return eta, center, and radius, all exactly."""
    eccentricity = nx.eccentricity(graph)
    radius = min(eccentricity.values())
    center = sorted(v for v, value in eccentricity.items() if value == radius)
    distances = nx.multi_source_dijkstra_path_length(graph, center)
    return max(distances.values()), center, radius


def deletion_table(graph: nx.Graph) -> tuple[dict, list[dict]]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    g = girth(graph)
    if g is None:
        raise ValueError("graph is acyclic")
    eta, center, radius = center_depth(graph)
    base = {
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "rank": cycle_rank(graph),
        "girth": g,
        "eta": eta,
        "radius": radius,
        "center": center,
        "phi": g + eta,
        "graph6": graph6(graph),
        "edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges()),
    }
    rows = []
    for v in graph:
        h = graph.copy()
        h.remove_node(v)
        connected = nx.is_connected(h)
        rank_h = cycle_rank(h) if connected else None
        row = {
            "v": v,
            "degree": graph.degree[v],
            "connected": connected,
            "rank": rank_h,
            "admissible": bool(connected and rank_h is not None and rank_h >= 1),
        }
        if row["admissible"]:
            gh = girth(h)
            assert gh is not None
            etah, centerh, radiush = center_depth(h)
            row.update(
                girth=gh,
                eta=etah,
                radius=radiush,
                center=centerh,
                phi=gh + etah,
                slack=gh + etah - (g + eta),
            )
        rows.append(row)
    return base, rows


def path_with_new_vertices(
    graph: nx.Graph, u: int, v: int, length: int, next_vertex: int
) -> int:
    assert length >= 1
    previous = u
    for _ in range(length - 1):
        graph.add_edge(previous, next_vertex)
        previous = next_vertex
        next_vertex += 1
    graph.add_edge(previous, v)
    return next_vertex


def theta(a: int, b: int, c: int) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from([0, 1])
    next_vertex = 2
    for length in (a, b, c):
        next_vertex = path_with_new_vertices(graph, 0, 1, length, next_vertex)
    return graph


def handcuff(g1: int, g2: int, bridge_length: int) -> nx.Graph:
    graph = nx.cycle_graph(g1)
    offset = g1
    second = nx.relabel_nodes(nx.cycle_graph(g2), lambda x: x + offset)
    graph = nx.compose(graph, second)
    if bridge_length == 0:
        graph = nx.contracted_nodes(graph, 0, offset, self_loops=False)
        return nx.convert_node_labels_to_integers(graph)
    next_vertex = g1 + g2
    path_with_new_vertices(graph, 0, offset, bridge_length, next_vertex)
    return graph


def cycle_with_ear(g: int, separation: int, ear_length: int) -> nx.Graph:
    graph = nx.cycle_graph(g)
    path_with_new_vertices(graph, 0, separation % g, ear_length, g)
    return graph


def attach_tail(graph: nx.Graph, root: int, length: int) -> nx.Graph:
    graph = graph.copy()
    previous = root
    next_vertex = max(graph, default=-1) + 1
    for _ in range(length):
        graph.add_edge(previous, next_vertex)
        previous = next_vertex
        next_vertex += 1
    return graph


def attach_two_tails(
    graph: nx.Graph, root1: int, length1: int, root2: int, length2: int
) -> nx.Graph:
    return attach_tail(attach_tail(graph, root1, length1), root2, length2)


def deterministic_families() -> list[tuple[str, nx.Graph]]:
    records: list[tuple[str, nx.Graph]] = []

    for a in range(2, 11):
        for b in range(a, 12):
            for c in range(b, 13):
                if a + b < 5:
                    continue
                core = theta(a, b, c)
                for tail in range(0, 9):
                    graph = attach_tail(core, 0, tail)
                    if 14 <= len(graph) <= 40:
                        records.append((f"theta({a},{b},{c})+tail({tail})", graph))
                for tail in range(1, 6):
                    graph = attach_two_tails(core, 0, tail, 1, tail + 1)
                    if 14 <= len(graph) <= 40:
                        records.append((f"theta({a},{b},{c})+2tails({tail},{tail+1})", graph))

    for g1 in range(5, 13):
        for g2 in range(5, 13):
            for bridge in range(0, 8):
                core = handcuff(g1, g2, bridge)
                roots = [0, min(g1, len(core) - 1)]
                for tail in range(0, 9):
                    graph = attach_tail(core, roots[0], tail)
                    if 14 <= len(graph) <= 40:
                        records.append(
                            (f"handcuff({g1},{g2},{bridge})+tail({tail})", graph)
                        )
                for t1 in range(1, 5):
                    graph = attach_two_tails(core, roots[0], t1, roots[1], t1 + 2)
                    if 14 <= len(graph) <= 40:
                        records.append(
                            (f"handcuff({g1},{g2},{bridge})+2tails({t1},{t1+2})", graph)
                        )

    for g in range(5, 18):
        for separation in range(2, g - 1):
            for ear_length in range(3, 13):
                core = cycle_with_ear(g, separation, ear_length)
                core_girth = girth(core)
                if core_girth is None or core_girth < 5:
                    continue
                for tail in range(0, 9):
                    graph = attach_tail(core, 0, tail)
                    if 14 <= len(graph) <= 40:
                        records.append(
                            (f"ear({g},{separation},{ear_length})+tail({tail})", graph)
                        )
                graph = attach_two_tails(core, 0, 3, separation, 5)
                if 14 <= len(graph) <= 40:
                    records.append(
                        (f"ear({g},{separation},{ear_length})+2tails(3,5)", graph)
                    )

    # Deduplicate isomorphic encodings only at graph6 level; the named families
    # intentionally retain distinct labelings when their attachment data differ.
    seen: set[str] = set()
    unique: list[tuple[str, nx.Graph]] = []
    for name, graph in records:
        code = graph6(graph)
        if code not in seen:
            seen.add(code)
            unique.append((name, graph))
    return unique


def random_ear_graph(rng: random.Random, n: int) -> nx.Graph:
    g = rng.randint(5, min(12, n - 4))
    graph = nx.cycle_graph(g)
    target_rank = rng.randint(2, min(7, 1 + (n - g) // 3))
    while cycle_rank(graph) < target_rank and len(graph) + 2 <= n:
        u, v = rng.sample(list(graph), 2)
        old_distance = nx.shortest_path_length(graph, u, v)
        min_length = max(2, 5 - old_distance)
        max_length = min(8, n - len(graph) + 1)
        if min_length > max_length:
            continue
        length = rng.randint(min_length, max_length)
        candidate = graph.copy()
        path_with_new_vertices(candidate, u, v, length, max(candidate) + 1)
        if girth(candidate) is not None and girth(candidate) >= 5:
            graph = candidate
    while len(graph) < n:
        parent = rng.choice(list(graph))
        graph.add_edge(parent, max(graph) + 1)
    return graph


def random_tree_plus_edges(rng: random.Random, n: int) -> nx.Graph:
    graph = nx.random_labeled_tree(n, seed=rng.randrange(1 << 32))
    target_rank = rng.randint(2, min(8, n // 4))
    attempts = 0
    while cycle_rank(graph) < target_rank and attempts < 20 * n:
        attempts += 1
        u, v = rng.sample(list(graph), 2)
        if graph.has_edge(u, v) or nx.shortest_path_length(graph, u, v) < 4:
            continue
        graph.add_edge(u, v)
        if girth(graph) is None or girth(graph) < 5:
            graph.remove_edge(u, v)
    if cycle_rank(graph) < 2:
        return random_ear_graph(rng, n)
    return graph


def random_subdivided_core(rng: random.Random, n: int) -> nx.Graph:
    while True:
        core_n = rng.randint(4, min(9, max(4, n // 3)))
        base = nx.gnp_random_graph(
            core_n, rng.uniform(0.28, 0.62), seed=rng.randrange(1 << 32)
        )
        if nx.is_connected(base) and cycle_rank(base) >= 2:
            break
    graph = nx.Graph()
    graph.add_nodes_from(base)
    next_vertex = core_n
    edges = list(base.edges())
    # Subdivide each edge at least once.  If triangles remain as 6-cycles this
    # gives a high-girth sparse core while preserving cycle rank.
    for index, (u, v) in enumerate(edges):
        remaining_edges = len(edges) - index
        spare = n - next_vertex - remaining_edges
        subdivisions = 1 + (rng.randrange(min(3, spare + 1)) if spare > 0 else 0)
        next_vertex = path_with_new_vertices(
            graph, u, v, subdivisions + 1, next_vertex
        )
    if len(graph) > n:
        return random_ear_graph(rng, n)
    while len(graph) < n:
        parent = rng.choice(list(graph))
        graph.add_edge(parent, max(graph) + 1)
    if girth(graph) is None or girth(graph) < 5:
        return random_ear_graph(rng, n)
    return graph


def run_graph(name: str, graph: nx.Graph) -> tuple[dict, list[dict], int]:
    if not nx.is_connected(graph):
        raise AssertionError((name, "disconnected"))
    g = girth(graph)
    if g is None or g < 5 or cycle_rank(graph) < 2:
        raise AssertionError((name, g, cycle_rank(graph)))
    base, rows = deletion_table(graph)
    admissible = [row for row in rows if row["admissible"]]
    if not admissible:
        raise AssertionError((name, "no admissible deletion"))
    best = max(row["slack"] for row in admissible)
    return base, rows, best


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=14420260718)
    parser.add_argument("--random-trials", type=int, default=3000)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("audit_ind2_large_results.json"),
    )
    args = parser.parse_args()

    counts = Counter()
    best_slack_counts = Counter()
    minimum_best = 10**9
    tight_examples: list[dict] = []

    def consume(name: str, graph: nx.Graph, corpus: str) -> dict | None:
        nonlocal minimum_best
        base, rows, best = run_graph(name, graph)
        counts[corpus] += 1
        best_slack_counts[best] += 1
        minimum_best = min(minimum_best, best)
        if best == 0 and len(tight_examples) < 24:
            tight_examples.append(
                {
                    "name": name,
                    "corpus": corpus,
                    "graph6": base["graph6"],
                    "n": base["n"],
                    "girth": base["girth"],
                    "eta": base["eta"],
                    "rank": base["rank"],
                    "winning_vertices": [
                        row["v"]
                        for row in rows
                        if row["admissible"] and row["slack"] == 0
                    ],
                }
            )
        if best < 0:
            return {
                "name": name,
                "corpus": corpus,
                "base": base,
                "deletions": rows,
                "best_slack": best,
            }
        return None

    counterexample = None
    for name, graph in deterministic_families():
        counterexample = consume(name, graph, "deterministic")
        if counterexample is not None:
            break

    rng = random.Random(args.seed)
    generators = (random_ear_graph, random_tree_plus_edges, random_subdivided_core)
    if counterexample is None:
        for trial in range(args.random_trials):
            n = rng.randint(14, 40)
            generator = generators[trial % len(generators)]
            graph = generator(rng, n)
            counterexample = consume(
                f"{generator.__name__}(seed={args.seed},trial={trial},n={n})",
                graph,
                "random",
            )
            if counterexample is not None:
                break

    result = {
        "lemma": "exists admissible v with phi(G-v)>=phi(G)",
        "phi": "girth + maximum distance to center set",
        "seed": args.seed,
        "requested_random_trials": args.random_trials,
        "counts": dict(counts),
        "minimum_best_slack": minimum_best,
        "best_slack_counts": {str(k): v for k, v in sorted(best_slack_counts.items())},
        "tight_examples": tight_examples,
        "counterexample": counterexample,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if counterexample is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
