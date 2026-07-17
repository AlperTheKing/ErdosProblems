#!/usr/bin/env python3
"""Independent exhaustive NetworkX oracle for WOWII Conjecture 143.

This implementation deliberately uses only the statement in PROOF_PLAN.md.  It
does not import or depend on the pre-existing atlas checker.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import platform
import time
import tracemalloc
from collections import Counter, deque
from pathlib import Path
from typing import Any

import networkx as nx


OUTPUT_PATH = Path(__file__).with_name("atlas_independent_results.json")


def graph6_certificate(graph: nx.Graph) -> str:
    """Return a deterministic compact certificate for an atlas graph."""

    return nx.to_graph6_bytes(graph, header=False).decode("ascii").strip()


def exact_girth(graph: nx.Graph) -> int:
    """Compute girth by deleting each edge logically and running BFS.

    For an edge uv, any u-v path avoiding uv closes with uv to form a cycle.
    Minimizing this quantity over all edges gives the shortest cycle exactly.
    """

    best = graph.number_of_nodes() + 1
    adjacency = {vertex: tuple(graph.neighbors(vertex)) for vertex in graph}

    for source, target in graph.edges():
        distance = {source: 0}
        queue: deque[int] = deque([source])

        while queue:
            vertex = queue.popleft()
            next_distance = distance[vertex] + 1
            if next_distance + 1 >= best:
                continue

            for neighbor in adjacency[vertex]:
                if (vertex == source and neighbor == target) or (
                    vertex == target and neighbor == source
                ):
                    continue
                if neighbor in distance:
                    continue
                distance[neighbor] = next_distance
                if neighbor == target:
                    best = min(best, next_distance + 1)
                    queue.clear()
                    break
                queue.append(neighbor)

    if best == graph.number_of_nodes() + 1:
        raise ValueError("exact_girth called on an acyclic graph")
    return best


def induced_tree_orders(
    graph: nx.Graph, leaves: tuple[int, ...]
) -> tuple[int, int, dict[tuple[int, int], int]]:
    """Exhaust all nonempty vertex subsets and record induced-tree maxima.

    Returns the global maximum order, the number of maximizing subsets, and
    the maximum order among induced trees containing each pair of leaves.
    """

    vertices = tuple(sorted(graph.nodes()))
    leaf_pairs = tuple(itertools.combinations(leaves, 2))
    pair_maximum = {pair: 0 for pair in leaf_pairs}
    maximum_order = 0
    maximizing_subset_count = 0

    for mask in range(1, 1 << len(vertices)):
        chosen = tuple(
            vertices[position]
            for position in range(len(vertices))
            if mask & (1 << position)
        )
        induced = graph.subgraph(chosen)
        order = len(chosen)

        # A finite nonempty simple graph is a tree iff it is connected and has
        # exactly |V|-1 edges.  Both conditions are checked independently.
        if induced.number_of_edges() != order - 1 or not nx.is_connected(induced):
            continue

        if order > maximum_order:
            maximum_order = order
            maximizing_subset_count = 1
        elif order == maximum_order:
            maximizing_subset_count += 1

        chosen_set = set(chosen)
        for pair in leaf_pairs:
            if pair[0] in chosen_set and pair[1] in chosen_set:
                pair_maximum[pair] = max(pair_maximum[pair], order)

    return maximum_order, maximizing_subset_count, pair_maximum


def basic_record(index: int, graph: nx.Graph) -> dict[str, Any]:
    order = graph.number_of_nodes()
    size = graph.number_of_edges()
    connected = order > 0 and nx.is_connected(graph)
    return {
        "atlas_index": index,
        "connected": connected,
        "graph6": graph6_certificate(graph),
        "order": order,
        "size": size,
    }


def audit_atlas() -> dict[str, Any]:
    atlas = nx.graph_atlas_g()
    records: list[dict[str, Any]] = []
    order_counts: Counter[int] = Counter()
    connected_count = 0
    connected_tree_count = 0
    connected_cyclic_count = 0
    main_violations: list[dict[str, Any]] = []
    main_equalities: list[dict[str, Any]] = []
    two_leaf_violations: list[dict[str, Any]] = []
    two_leaf_equalities: list[dict[str, Any]] = []
    pairwise_violations: list[dict[str, Any]] = []
    pairwise_pairs_checked = 0
    main_minimum_slack: int | None = None
    two_leaf_minimum_slack: int | None = None
    pairwise_minimum_slack: int | None = None

    for index, graph in enumerate(atlas):
        record = basic_record(index, graph)
        order = record["order"]
        size = record["size"]
        connected = record["connected"]
        order_counts[order] += 1

        if not connected:
            record["target_domain"] = False
            records.append(record)
            continue

        connected_count += 1
        if size == order - 1:
            connected_tree_count += 1
            record["target_domain"] = False
            record["tree"] = True
            records.append(record)
            continue

        connected_cyclic_count += 1
        degrees = sorted(degree for _, degree in graph.degree())
        leaves = tuple(sorted(vertex for vertex, degree in graph.degree() if degree == 1))
        girth = exact_girth(graph)
        tree_order, maximizing_count, pair_maximum = induced_tree_orders(graph, leaves)
        second_smallest_degree = degrees[1]
        lhs = tree_order * second_smallest_degree
        rhs = girth + 1
        main_slack = lhs - rhs
        main_minimum_slack = (
            main_slack
            if main_minimum_slack is None
            else min(main_minimum_slack, main_slack)
        )

        record.update(
            {
                "degrees": degrees,
                "girth": girth,
                "induced_tree_maximizer_count": maximizing_count,
                "largest_induced_tree_order": tree_order,
                "leaf_count": len(leaves),
                "leaves": list(leaves),
                "main_lhs": lhs,
                "main_rhs": rhs,
                "main_slack": main_slack,
                "second_smallest_degree": second_smallest_degree,
                "target_domain": True,
                "tree": False,
            }
        )

        main_witness = {
            "atlas_index": index,
            "graph6": record["graph6"],
            "girth": girth,
            "largest_induced_tree_order": tree_order,
            "second_smallest_degree": second_smallest_degree,
            "slack": main_slack,
        }
        if main_slack < 0:
            main_violations.append(main_witness)
        elif main_slack == 0:
            main_equalities.append(main_witness)

        if len(leaves) >= 2:
            lemma_slack = tree_order - rhs
            two_leaf_minimum_slack = (
                lemma_slack
                if two_leaf_minimum_slack is None
                else min(two_leaf_minimum_slack, lemma_slack)
            )
            record["two_leaf_lemma_slack"] = lemma_slack

            lemma_witness = {
                "atlas_index": index,
                "graph6": record["graph6"],
                "girth": girth,
                "largest_induced_tree_order": tree_order,
                "slack": lemma_slack,
            }
            if lemma_slack < 0:
                two_leaf_violations.append(lemma_witness)
            elif lemma_slack == 0:
                two_leaf_equalities.append(lemma_witness)

            pair_rows = []
            for pair in sorted(pair_maximum):
                pairwise_pairs_checked += 1
                pair_order = pair_maximum[pair]
                pair_slack = pair_order - rhs
                pairwise_minimum_slack = (
                    pair_slack
                    if pairwise_minimum_slack is None
                    else min(pairwise_minimum_slack, pair_slack)
                )
                pair_row = {
                    "leaves": list(pair),
                    "maximum_induced_tree_order_containing_pair": pair_order,
                    "slack": pair_slack,
                }
                pair_rows.append(pair_row)
                if pair_slack < 0:
                    pairwise_violations.append(
                        {
                            "atlas_index": index,
                            "graph6": record["graph6"],
                            **pair_row,
                        }
                    )
            record["leaf_pair_checks"] = pair_rows
        else:
            record["two_leaf_lemma_slack"] = None

        records.append(record)

    return {
        "metadata": {
            "algorithm": {
                "girth": "BFS between endpoints with the tested edge excluded",
                "induced_tree": "all nonempty vertex subsets; connected and |E|=|V|-1",
                "leaf_pair_strengthening": "same exhaustive subsets, separately for every leaf pair",
            },
            "networkx_version": nx.__version__,
            "python_version": platform.python_version(),
            "schema": "wowii-143-independent-atlas-v1",
        },
        "summary": {
            "atlas_graph_count": len(atlas),
            "connected_count": connected_count,
            "connected_cyclic_count": connected_cyclic_count,
            "connected_tree_count": connected_tree_count,
            "main_equality_count": len(main_equalities),
            "main_equality_witnesses": main_equalities,
            "main_minimum_slack": main_minimum_slack,
            "main_violation_count": len(main_violations),
            "main_violations": main_violations,
            "order_counts": {str(key): order_counts[key] for key in sorted(order_counts)},
            "pairwise_leaf_pair_minimum_slack": pairwise_minimum_slack,
            "pairwise_leaf_pairs_checked": pairwise_pairs_checked,
            "pairwise_leaf_violation_count": len(pairwise_violations),
            "pairwise_leaf_violations": pairwise_violations,
            "two_leaf_equality_count": len(two_leaf_equalities),
            "two_leaf_equality_witnesses": two_leaf_equalities,
            "two_leaf_graph_count": sum(
                1
                for record in records
                if record.get("target_domain") and record.get("leaf_count", 0) >= 2
            ),
            "two_leaf_minimum_slack": two_leaf_minimum_slack,
            "two_leaf_violation_count": len(two_leaf_violations),
            "two_leaf_violations": two_leaf_violations,
        },
        "graphs": records,
    }


def main() -> None:
    tracemalloc.start()
    started = time.perf_counter()
    results = audit_atlas()
    elapsed_seconds = time.perf_counter() - started
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    results["metadata"]["elapsed_seconds"] = round(elapsed_seconds, 6)
    results["metadata"]["peak_traced_python_bytes"] = peak_bytes
    serialized = (json.dumps(results, indent=2, sort_keys=True) + "\n").encode("utf-8")
    OUTPUT_PATH.write_bytes(serialized)

    summary = results["summary"]
    print(f"output={OUTPUT_PATH}")
    print(f"sha256={hashlib.sha256(serialized).hexdigest()}")
    print(f"atlas_graph_count={summary['atlas_graph_count']}")
    print(f"connected_cyclic_count={summary['connected_cyclic_count']}")
    print(f"main_violation_count={summary['main_violation_count']}")
    print(f"main_minimum_slack={summary['main_minimum_slack']}")
    print(f"main_equality_count={summary['main_equality_count']}")
    print(f"two_leaf_graph_count={summary['two_leaf_graph_count']}")
    print(f"two_leaf_violation_count={summary['two_leaf_violation_count']}")
    print(f"two_leaf_minimum_slack={summary['two_leaf_minimum_slack']}")
    print(f"pairwise_leaf_pairs_checked={summary['pairwise_leaf_pairs_checked']}")
    print(f"pairwise_leaf_violation_count={summary['pairwise_leaf_violation_count']}")
    print(f"pairwise_leaf_pair_minimum_slack={summary['pairwise_leaf_pair_minimum_slack']}")
    print(f"elapsed_seconds={elapsed_seconds:.6f}")
    print(f"peak_traced_python_bytes={peak_bytes}")


if __name__ == "__main__":
    main()
