#!/usr/bin/env python3
"""Independent zero-exit verifier for the exact ear-route counterexamples."""

from __future__ import annotations

import networkx as nx

from audit_terminal_ears import deletion_row, invariants
from test_max_tree_geodesic_boundary import audit_graph


def graph(code: str) -> nx.Graph:
    return nx.from_graph6_bytes(code.encode())


def verify_max_tree() -> None:
    g = graph("I?ABAaIBO")
    old = invariants(g)
    assert g.number_of_nodes() == 10
    assert g.number_of_edges() == 11
    assert nx.girth(g) == 5
    assert old["center"] == {1, 4, 6, 7}
    assert old["eta"] == 2
    assert old["realizers"] == {0, 5}
    success, detail = audit_graph(b"I?ABAaIBO", g)
    assert not success
    assert detail["best_overlap"] == 2
    assert len(detail["choices"]) == 4
    assert all(choice["maximum_order"] == 9 for choice in detail["choices"])
    assert all(choice["maximum_tree_count"] == 1 for choice in detail["choices"])


def verify_degree_two() -> None:
    g = graph("I?`acgwg_")
    old = invariants(g)
    assert nx.is_biconnected(g)
    assert g.number_of_nodes() == 10
    assert g.number_of_edges() == 14
    assert nx.girth(g) == 5
    assert old["radius"] == 2
    assert old["eta"] == 2
    assert old["center"] == {2, 3, 7, 9}
    degree_two = {v for v in g if g.degree[v] == 2}
    assert degree_two == {1, 4}
    rows = {v: deletion_row(g, old, v) for v in g}
    assert all(rows[v]["delta_eta"] == -1 for v in degree_two)
    assert all(rows[v]["delta_eta"] == 0 for v in set(g) - degree_two)


def verify_neighbor_exchange() -> None:
    g = graph("H?`@F_]")
    old = invariants(g)
    assert nx.is_biconnected(g)
    assert g.number_of_nodes() == 9
    assert g.number_of_edges() == 11
    assert nx.girth(g) == 5
    assert old["radius"] == 2
    assert old["eta"] == 1
    assert old["center"] == {3, 7, 8}
    assert set(g[3]) == {7, 8}
    row = deletion_row(g, old, 3)
    assert row is not None and row["delta_eta"] == -1 and row["delta_radius"] == 1
    for v in (7, 8):
        subgraph = g.copy()
        subgraph.remove_node(v)
        assert subgraph.number_of_edges() - subgraph.number_of_nodes() + 1 == 0


def main() -> None:
    verify_max_tree()
    verify_degree_two()
    verify_neighbor_exchange()
    print("verified max-tree, degree-two, and neighbor-exchange counterexamples")


if __name__ == "__main__":
    main()
