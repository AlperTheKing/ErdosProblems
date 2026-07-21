#!/usr/bin/env python3
"""Exact graph-atlas falsification test for WOWII / Graffiti.pc Conjecture 143."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "atlas_results.json"


def exact_girth(graph: nx.Graph) -> int:
    best = graph.number_of_nodes() + 1
    for u, v in list(graph.edges()):
        graph.remove_edge(u, v)
        try:
            distance = nx.shortest_path_length(graph, u, v)
        except nx.NetworkXNoPath:
            distance = None
        graph.add_edge(u, v)
        if distance is not None:
            best = min(best, distance + 1)
    if best == graph.number_of_nodes() + 1:
        raise ValueError("exact_girth called on an acyclic graph")
    return best


def exact_largest_induced_tree_order(graph: nx.Graph) -> tuple[int, tuple[int, ...]]:
    vertices = tuple(sorted(graph.nodes()))
    for size in range(len(vertices), 0, -1):
        for subset in itertools.combinations(vertices, size):
            induced = graph.subgraph(subset)
            if nx.is_tree(induced):
                return size, subset
    raise AssertionError("every nonempty graph has a one-vertex induced tree")


def graph6(graph: nx.Graph) -> str:
    ordered = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(ordered, header=False).decode("ascii").strip()


def main() -> None:
    atlas = nx.graph_atlas_g()
    records: list[dict[str, object]] = []
    equality: list[str] = []
    leaf_equality: list[str] = []
    violations: list[dict[str, object]] = []
    leaf_violations: list[dict[str, object]] = []

    connected_count = 0
    cyclic_count = 0
    delta_one_count = 0
    delta_ge_two_count = 0
    leaf_case_count = 0
    min_slack: int | None = None
    min_leaf_slack: int | None = None

    for atlas_index, graph in enumerate(atlas):
        n = graph.number_of_nodes()
        if n == 0 or not nx.is_connected(graph):
            continue
        connected_count += 1
        if nx.is_tree(graph):
            continue
        cyclic_count += 1

        degrees = sorted(dict(graph.degree()).values())
        if len(degrees) < 2 or degrees[0] == 0:
            raise AssertionError("connected cyclic atlas graph has invalid degree sequence")
        delta_two = degrees[1]
        if delta_two == 1:
            delta_one_count += 1
        elif delta_two >= 2:
            delta_ge_two_count += 1
        else:
            raise AssertionError("second-smallest degree must be positive")

        girth = exact_girth(graph)
        tree_order, tree_witness = exact_largest_induced_tree_order(graph)
        slack = tree_order * delta_two - (girth + 1)
        min_slack = slack if min_slack is None else min(min_slack, slack)
        leaves = sum(degree == 1 for degree in degrees)

        record: dict[str, object] = {
            "atlas_index": atlas_index,
            "graph6": graph6(graph),
            "n": n,
            "m": graph.number_of_edges(),
            "degrees": degrees,
            "delta_two": delta_two,
            "girth": girth,
            "tree_order": tree_order,
            "tree_witness": list(tree_witness),
            "leaves": leaves,
            "slack": slack,
        }
        records.append(record)

        if slack == 0:
            equality.append(record["graph6"])
        if slack < 0:
            violations.append(record)

        if leaves >= 2:
            leaf_case_count += 1
            leaf_slack = tree_order - (girth + 1)
            record["leaf_lemma_slack"] = leaf_slack
            min_leaf_slack = (
                leaf_slack if min_leaf_slack is None else min(min_leaf_slack, leaf_slack)
            )
            if leaf_slack == 0:
                leaf_equality.append(record["graph6"])
            if leaf_slack < 0:
                leaf_violations.append(record)

    payload = {
        "test": "WOWII_Graffiti_pc_Conjecture_143",
        "atlas_total": len(atlas),
        "connected_graphs": connected_count,
        "connected_cyclic_graphs": cyclic_count,
        "delta_two_eq_one": delta_one_count,
        "delta_two_ge_two": delta_ge_two_count,
        "two_leaf_cases": leaf_case_count,
        "minimum_main_slack": min_slack,
        "minimum_leaf_lemma_slack": min_leaf_slack,
        "main_equality_count": len(equality),
        "leaf_equality_count": len(leaf_equality),
        "violations": violations,
        "leaf_violations": leaf_violations,
        "main_equality_graph6": equality,
        "leaf_equality_graph6": leaf_equality,
        "records": records,
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    digest = hashlib.sha256(encoded).hexdigest().upper()

    summary = {
        key: payload[key]
        for key in (
            "atlas_total",
            "connected_graphs",
            "connected_cyclic_graphs",
            "delta_two_eq_one",
            "delta_two_ge_two",
            "two_leaf_cases",
            "minimum_main_slack",
            "minimum_leaf_lemma_slack",
            "main_equality_count",
            "leaf_equality_count",
        )
    }
    summary["violations"] = len(violations)
    summary["leaf_violations"] = len(leaf_violations)
    summary["output_sha256"] = digest
    print(json.dumps(summary, indent=2, sort_keys=True))

    if violations or leaf_violations:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
