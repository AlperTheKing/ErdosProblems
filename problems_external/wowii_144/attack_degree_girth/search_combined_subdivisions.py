#!/usr/bin/env python3
"""Falsifier-first W144-COMB search on subdivided 2-connected cores."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
IND2 = HERE.parent / "attack_ind2_multicycle"
sys.path.insert(0, str(IND2))
from analyze_tight_deletions import center_depth, cycle_rank, girth  # noqa: E402


def subdivide(core: nx.Graph, lengths: list[int]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(core.nodes())
    next_vertex = core.number_of_nodes()
    for (u, v), length in zip(sorted(core.edges()), lengths, strict=True):
        previous = u
        for _ in range(length - 1):
            graph.add_edge(previous, next_vertex)
            previous = next_vertex
            next_vertex += 1
        graph.add_edge(previous, v)
    return graph


def item(graph: nx.Graph, label: str, lengths: list[int]) -> dict | None:
    g = girth(graph)
    if g is None or g < 5:
        return None
    n = graph.number_of_nodes()
    beta = cycle_rank(graph)
    eta, center = center_depth(graph)
    delta = max(dict(graph.degree()).values())
    diameter = nx.diameter(graph)
    terms = [delta - 1, diameter - g // 2, n - g - beta + 1]
    return {"core": label, "lengths": lengths, "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
            "n": n, "m": graph.number_of_edges(), "girth": g, "beta": beta,
            "diameter": diameter, "maximum_degree": delta, "eta": eta,
            "center": sorted(center), "terms": terms, "slack": max(terms) - eta}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=14420260718)
    parser.add_argument("--max-length", type=int, default=10)
    parser.add_argument("--output", type=Path, default=HERE / "combined_subdivision_search.json")
    args = parser.parse_args()
    rng = random.Random(args.seed)
    cores: list[tuple[str, nx.Graph]] = []
    for i, graph in enumerate(nx.graph_atlas_g()):
        if 4 <= len(graph) <= 7 and nx.is_connected(graph) and nx.is_biconnected(graph) \
                and min(dict(graph.degree()).values()) >= 3:
            cores.append((f"atlas_{i}", nx.convert_node_labels_to_integers(graph)))
    cores.extend([("petersen", nx.petersen_graph()), ("heawood", nx.heawood_graph()),
                  ("cube", nx.cubical_graph()), ("K5", nx.complete_graph(5)),
                  ("K44", nx.complete_bipartite_graph(4, 4))])
    result = {"seed": args.seed, "samples": 0, "eligible": 0, "cores": len(cores),
              "minimum_slack": None, "first_minimum": None, "first_failure": None}
    for trial in range(args.samples):
        label, core = rng.choice(cores)
        lengths = [rng.randint(1, args.max_length) for _ in core.edges()]
        graph = subdivide(core, lengths)
        record = item(graph, label, lengths)
        result["samples"] += 1
        if record is None:
            continue
        result["eligible"] += 1
        if result["minimum_slack"] is None or record["slack"] < result["minimum_slack"]:
            result["minimum_slack"] = record["slack"]
            result["first_minimum"] = record
        if record["slack"] < 0:
            result["first_failure"] = record
            break
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
