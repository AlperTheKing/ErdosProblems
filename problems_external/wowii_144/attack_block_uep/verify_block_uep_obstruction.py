#!/usr/bin/env python3
"""Verify the exact block/UEP obstruction records used in the audit."""

from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
IND2 = HERE.parent / "attack_ind2_multicycle"
sys.path.insert(0, str(IND2))
from analyze_tight_deletions import center_depth, cycle_rank, girth  # noqa: E402


def new_center_fiber(graph: nx.Graph, v: int, old_center: set[int]) -> set[int]:
    subgraph = graph.copy()
    subgraph.remove_node(v)
    _, new_center = center_depth(subgraph)
    return set(new_center) - old_center


def verify_two_block_record() -> None:
    graph = nx.from_graph6_bytes(b"J??CAAoR@U?")
    eta, center_frozen = center_depth(graph)
    center = set(center_frozen)
    eccentricity = nx.eccentricity(graph)
    radius = min(eccentricity.values())
    assert len(graph) == 11
    assert graph.number_of_edges() == 12
    assert girth(graph) == 5
    assert cycle_rank(graph) == 2
    assert radius == eta == 3
    assert center == {10}
    assert set(nx.articulation_points(graph)) == {8, 9, 10}

    expected = {
        3: {4, 7},
        5: {2, 6},
    }
    for v, expected_fiber in expected.items():
        subgraph = graph.copy()
        subgraph.remove_node(v)
        new_eta, _ = center_depth(subgraph)
        new_radius = min(nx.eccentricity(subgraph).values())
        fiber = new_center_fiber(graph, v, center)
        assert new_radius == radius
        assert new_eta == eta - 1
        assert fiber == expected_fiber
        for u in fiber:
            distances = nx.single_source_shortest_path_length(graph, u)
            farthest = {x for x, value in distances.items() if value == max(distances.values())}
            assert max(distances.values()) == radius + 1
            assert farthest == {v}

    assert expected[3].isdisjoint(expected[5])

    good_nonperipheral = []
    distance = dict(nx.all_pairs_shortest_path_length(graph))
    for v in graph:
        subgraph = graph.copy()
        subgraph.remove_node(v)
        if not nx.is_connected(subgraph) or cycle_rank(subgraph) < 1:
            continue
        new_eta, _ = center_depth(subgraph)
        peripheral = any(distance[c][v] == radius for c in center)
        if new_eta >= eta and not peripheral:
            good_nonperipheral.append(v)
    assert good_nonperipheral == [0, 1, 2, 4, 6, 7]


def verify_distance_shortcut_record() -> None:
    graph = nx.from_graph6_bytes(("I??ED" + chr(96) + "KI_").encode())
    eta, center_frozen = center_depth(graph)
    center = set(center_frozen)
    eccentricity = nx.eccentricity(graph)
    radius = min(eccentricity.values())
    distance = dict(nx.all_pairs_shortest_path_length(graph))
    realizers = {
        x for x in graph if min(distance[x][c] for c in center) == eta
    }
    assert len(graph) == 10
    assert girth(graph) == 5
    assert cycle_rank(graph) == 2
    assert radius == eta == 3
    assert center == {6, 9}
    assert realizers == {3, 5}

    candidates = []
    for v in graph:
        subgraph = graph.copy()
        subgraph.remove_node(v)
        if not nx.is_connected(subgraph) or cycle_rank(subgraph) < 1:
            continue
        new_radius = min(nx.eccentricity(subgraph).values())
        if new_radius <= radius:
            candidates.append(v)
            assert all(
                distance[x][v] >= radius - eta + 2
                for x in realizers - {v}
            )
    assert candidates == [0, 1, 2, 3, 4, 5]


def main() -> None:
    verify_two_block_record()
    verify_distance_shortcut_record()
    print("verified block/UEP obstruction records")


if __name__ == "__main__":
    main()
