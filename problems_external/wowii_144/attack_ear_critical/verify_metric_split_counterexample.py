#!/usr/bin/env python3
"""Independent verifier for the W144-MET counterexample Theta(1,7,8)."""

from __future__ import annotations

import networkx as nx


PATHS = (
    (0, 1),
    (0, 2, 3, 4, 5, 6, 7, 1),
    (0, 8, 9, 10, 11, 12, 13, 14, 1),
)
EXPECTED_GRAPH6 = "NpCGIE??G?_@?@??g?G"


def build_graph() -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(15))
    for path in PATHS:
        graph.add_edges_from(zip(path, path[1:]))
    return graph


def main() -> None:
    graph = build_graph()
    assert nx.is_connected(graph)
    assert nx.is_biconnected(graph)
    assert nx.number_connected_components(graph) == 1
    assert graph.number_of_nodes() == 15
    assert graph.number_of_edges() == 16
    assert nx.to_graph6_bytes(graph, header=False).decode().strip() == EXPECTED_GRAPH6

    girth = nx.girth(graph)
    diameter = nx.diameter(graph)
    maximum_degree = max(dict(graph.degree()).values())
    eccentricity = nx.eccentricity(graph)
    radius = min(eccentricity.values())
    center = {v for v, value in eccentricity.items() if value == radius}
    center_distance = nx.multi_source_dijkstra_path_length(graph, center)
    eta = max(center_distance.values())
    right_hand_side = max(maximum_degree, diameter - girth // 2)

    assert girth == 8
    assert diameter == 7
    assert maximum_degree == 3
    assert radius == 4
    assert center == {0, 1}
    assert eta == 4
    assert {v for v, value in center_distance.items() if value == eta} == {11}
    assert right_hand_side == 3
    assert eta > right_hand_side

    print(
        "PASS",
        {
            "graph6": EXPECTED_GRAPH6,
            "girth": girth,
            "diameter": diameter,
            "Delta": maximum_degree,
            "radius": radius,
            "center": sorted(center),
            "eta": eta,
            "rhs": right_hand_side,
        },
    )


if __name__ == "__main__":
    main()