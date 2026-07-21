#!/usr/bin/env python3
"""Verify the beta=3 counterexample to the corrected W144 metric split."""

from __future__ import annotations

import itertools

import networkx as nx


CODE = "NhCGGE@?O?_@O@G???g"
EXPECTED_ADJACENCY = {
    0: [1, 8],
    1: [0, 2, 12],
    2: [1, 3, 13],
    3: [2, 4],
    4: [3, 5],
    5: [4, 6],
    6: [5, 7],
    7: [6, 8, 9],
    8: [0, 7],
    9: [7, 10],
    10: [9, 11],
    11: [10, 12, 14],
    12: [1, 11],
    13: [2, 14],
    14: [11, 13],
}


def cycle_rank(graph: nx.Graph) -> int:
    return graph.number_of_edges() - graph.number_of_nodes() + 1


def center_data(graph: nx.Graph) -> tuple[int, set[int], int, set[int]]:
    eccentricity = nx.eccentricity(graph)
    radius = min(eccentricity.values())
    center = {v for v, value in eccentricity.items() if value == radius}
    distances = nx.multi_source_dijkstra_path_length(graph, center)
    eta = max(distances.values())
    realizers = {v for v, value in distances.items() if value == eta}
    return radius, center, eta, realizers


def maximum_induced_tree(graph: nx.Graph) -> tuple[int, tuple[int, ...]]:
    vertices = sorted(graph)
    for size in range(len(vertices), 0, -1):
        for subset in itertools.combinations(vertices, size):
            induced = graph.subgraph(subset)
            if induced.number_of_edges() == size - 1 and nx.is_connected(induced):
                return size, subset
    raise AssertionError("nonempty graph has no induced tree")


def main() -> None:
    graph = nx.from_graph6_bytes(CODE.encode())
    assert {v: sorted(graph[v]) for v in graph} == EXPECTED_ADJACENCY
    assert nx.is_biconnected(graph)
    assert (len(graph), graph.number_of_edges(), cycle_rank(graph)) == (15, 17, 3)

    girth = nx.girth(graph)
    diameter = nx.diameter(graph)
    maximum_degree = max(dict(graph.degree()).values())
    radius, center, eta, realizers = center_data(graph)
    assert (girth, diameter, maximum_degree) == (6, 5, 3)
    assert (radius, center, eta, realizers) == (4, {0, 1}, 4, {5})
    metric_rhs = max(maximum_degree, diameter - girth // 2)
    assert metric_rhs == 3 < eta

    tree, witness = maximum_induced_tree(graph)
    target = girth - 1 + eta
    assert tree == 13 and target == 9
    assert witness == (0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 13, 14)

    eta_good = []
    phi_good = []
    deletion_rows = []
    for vertex in sorted(graph):
        reduced = graph.copy()
        reduced.remove_node(vertex)
        assert nx.is_connected(reduced) and cycle_rank(reduced) >= 1
        reduced_girth = nx.girth(reduced)
        reduced_radius, reduced_center, reduced_eta, _ = center_data(reduced)
        if reduced_eta >= eta:
            eta_good.append(vertex)
        if reduced_girth + reduced_eta >= girth + eta:
            phi_good.append(vertex)
        deletion_rows.append(
            (vertex, cycle_rank(reduced), reduced_girth, reduced_radius,
             reduced_eta, tuple(sorted(reduced_center)))
        )
    assert eta_good == [2, 4, 6, 7, 10, 11]
    assert phi_good == [1, 2, 4, 6, 7, 10, 11, 13, 14]

    row2 = next(row for row in deletion_rows if row[0] == 2)
    assert row2[:5] == (2, 1, 8, 5, 4)
    print(
        "PASS",
        {
            "graph6": CODE,
            "beta": 3,
            "girth": girth,
            "diameter": diameter,
            "Delta": maximum_degree,
            "center": sorted(center),
            "eta": eta,
            "metric_rhs": metric_rhs,
            "tree": tree,
            "W144_target": target,
            "eta_good_deletions": eta_good,
            "phi_good_deletions": phi_good,
            "unicyclic_good_deletion": row2,
        },
    )


if __name__ == "__main__":
    main()
