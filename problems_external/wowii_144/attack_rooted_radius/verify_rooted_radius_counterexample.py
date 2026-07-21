#!/usr/bin/env python3
"""Verify the exact obstruction to a fixed-root radius-critical proof of W144-MIN."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
CODE = "G?`e_w"
ROOT = 1


def cycle_rank(graph: nx.Graph) -> int:
    return graph.number_of_edges() - graph.number_of_nodes() + 1


def girth(graph: nx.Graph) -> int:
    return min(len(cycle) for cycle in nx.cycle_basis(graph))


def center_depth(graph: nx.Graph) -> tuple[int, list[int]]:
    center = sorted(nx.center(graph))
    eta = max(
        min(nx.shortest_path_length(graph, vertex, central) for central in center)
        for vertex in graph
    )
    return eta, center


def rooted_depth(graph: nx.Graph, root: int) -> int:
    return min(nx.shortest_path_length(graph, root, central) for central in nx.center(graph))


def connected_cyclic_rows(graph: nx.Graph, root: int) -> list[dict]:
    vertices = sorted(graph)
    rows = []
    for size in range(3, len(vertices) + 1):
        for subset_tuple in itertools.combinations(vertices, size):
            subset = set(subset_tuple)
            if root not in subset:
                continue
            subgraph = graph.subgraph(subset).copy()
            if not nx.is_connected(subgraph) or cycle_rank(subgraph) < 1:
                continue
            eta, center = center_depth(subgraph)
            rows.append(
                {
                    "vertices": sorted(subset),
                    "n": len(subset),
                    "m": subgraph.number_of_edges(),
                    "rank": cycle_rank(subgraph),
                    "radius": nx.radius(subgraph),
                    "center": center,
                    "eta": eta,
                    "rooted_depth": rooted_depth(subgraph, root),
                }
            )
    return rows


def main() -> None:
    graph = nx.from_graph6_bytes(CODE.encode())
    expected_edges = {
        (0, 4), (0, 6), (1, 5), (1, 6), (2, 5),
        (3, 6), (3, 7), (4, 7), (5, 7),
    }
    assert {tuple(sorted(edge)) for edge in graph.edges()} == expected_edges
    assert nx.is_connected(graph)
    assert (graph.number_of_nodes(), graph.number_of_edges(), cycle_rank(graph)) == (8, 9, 2)
    assert girth(graph) == 5
    eta, center = center_depth(graph)
    assert nx.radius(graph) == 2 and center == [7] and eta == 2
    assert rooted_depth(graph, ROOT) == eta

    rows = connected_cyclic_rows(graph, ROOT)
    feasible = [row for row in rows if row["rooted_depth"] >= eta]
    assert len(rows) == 11
    assert feasible == [row for row in rows if row["vertices"] == list(range(8))]
    assert feasible[0]["rank"] == 2

    path = graph.subgraph({0, 1, 4, 6}).copy()
    assert nx.is_tree(path) and nx.radius(path) == 2 and ROOT in path
    for vertex in path:
        proper = path.copy()
        proper.remove_node(vertex)
        if proper and nx.is_connected(proper):
            assert nx.radius(proper) < 2

    cycle = graph.subgraph({1, 3, 5, 6, 7}).copy()
    assert cycle_rank(cycle) == 1 and girth(cycle) == 5
    assert nx.radius(cycle) == 2 and set(nx.center(cycle)) == set(cycle)
    cycle_eta, _ = center_depth(cycle)
    assert cycle_eta == 0 and rooted_depth(cycle, ROOT) == 0

    result = {
        "graph6": CODE,
        "root": ROOT,
        "ambient": {
            "n": 8,
            "m": 9,
            "rank": 2,
            "girth": 5,
            "radius": 2,
            "center": center,
            "eta": eta,
            "edges": sorted([list(edge) for edge in expected_edges]),
        },
        "connected_cyclic_induced_subgraphs_containing_root": rows,
        "rooted_depth_feasible_subgraphs": feasible,
        "minimal_radius_path": sorted(path),
        "radius_preserving_cycle": {
            "vertices": sorted(cycle),
            "radius": nx.radius(cycle),
            "center": sorted(nx.center(cycle)),
            "eta": cycle_eta,
            "rooted_depth": rooted_depth(cycle, ROOT),
        },
    }
    output = HERE / "rooted_radius_counterexample.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
