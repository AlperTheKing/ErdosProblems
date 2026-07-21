"""Deterministic randomized falsification search for the W144-IND2 lemma."""

from __future__ import annotations

import argparse
import random

import networkx as nx

from analyze_tight_deletions import center_depth, cycle_rank, girth


def subdivided_core(rng: random.Random) -> nx.Graph:
    while True:
        order = rng.randint(4, 12)
        probability = rng.uniform(0.2, 0.55)
        base = nx.gnp_random_graph(order, probability, seed=rng.randrange(1 << 30))
        if nx.is_connected(base) and cycle_rank(base) >= 2:
            break
    graph = nx.Graph()
    graph.add_nodes_from(base)
    next_vertex = order
    for u, v in base.edges():
        # One subdivision makes every inherited cycle at least twice as long.
        # A second subdivision is added randomly to vary ear lengths.
        count = 1 + (rng.random() < 0.3)
        previous = u
        for _ in range(count):
            graph.add_edge(previous, next_vertex)
            previous = next_vertex
            next_vertex += 1
        graph.add_edge(previous, v)
    return graph


def attach_tree(graph: nx.Graph, rng: random.Random) -> None:
    next_vertex = len(graph)
    for _ in range(rng.randint(0, 12)):
        parent = rng.choice(list(graph))
        graph.add_edge(parent, next_vertex)
        next_vertex += 1


def evaluate(graph: nx.Graph):
    g = girth(graph)
    assert g is not None and g >= 6
    e, center = center_depth(graph)
    phi = g + e
    deletion_data = []
    for v in graph:
        h = graph.copy()
        h.remove_node(v)
        if not nx.is_connected(h) or cycle_rank(h) < 1:
            continue
        gh = girth(h)
        assert gh is not None
        eh, center_h = center_depth(h)
        deletion_data.append((v, graph.degree[v], gh, eh, gh + eh - phi, sorted(center_h)))
    return phi, e, sorted(center), deletion_data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=144)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    minimum = 10**9
    tight = 0
    for trial in range(args.trials):
        graph = subdivided_core(rng)
        attach_tree(graph, rng)
        phi, e, center, data = evaluate(graph)
        best = max(item[4] for item in data)
        minimum = min(minimum, best)
        tight += best == 0
        if best < 0:
            print("COUNTEREXAMPLE", trial, nx.to_graph6_bytes(graph, header=False).strip().decode())
            print("n", len(graph), "m", graph.number_of_edges(), "phi", phi, "e", e, "center", center)
            print("deletions", data)
            return
    print("PASS", args.trials, "MIN_BEST_SLACK", minimum, "TIGHT", tight)


if __name__ == "__main__":
    main()
