#!/usr/bin/env python3
"""Probe the direct rooted eta-minimal deletion statement for W144.

For every connected multicyclic graph of girth at least five and every
eta-realizer x, test whether a vertex v != x can be deleted so that G-v is
connected and cyclic and x remains at least eta(G) away from the new center.
The output contains a complete exact record for the first failure.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
IND2 = HERE.parent / "attack_ind2_multicycle"
sys.path.insert(0, str(IND2))
from analyze_tight_deletions import center_depth, cycle_rank, girth, records  # noqa: E402


def distances_to_set(graph: nx.Graph, source: int, targets: set[int]) -> int:
    lengths = nx.single_source_shortest_path_length(graph, source)
    return min(lengths[t] for t in targets)


def audit(min_n: int, max_n: int) -> dict:
    checked_graphs = 0
    checked_roots = 0
    first_failure = None
    first_graph_without_any_good_root = None

    for n in range(min_n, max_n + 1):
        for code, graph in records(n):
            g = girth(graph)
            if g is None or g < 5 or cycle_rank(graph) < 2:
                continue
            checked_graphs += 1
            eta, center = center_depth(graph)
            realizers = [
                x for x in sorted(graph)
                if distances_to_set(graph, x, set(center)) == eta
            ]
            root_rows = []
            graph_has_good_root = False
            for x in realizers:
                checked_roots += 1
                deletions = []
                for v in sorted(graph):
                    if v == x:
                        continue
                    subgraph = graph.copy()
                    subgraph.remove_node(v)
                    if not nx.is_connected(subgraph) or cycle_rank(subgraph) < 1:
                        continue
                    eta_h, center_h = center_depth(subgraph)
                    rooted_h = distances_to_set(subgraph, x, set(center_h))
                    deletions.append({
                        "v": v,
                        "girth": girth(subgraph),
                        "radius": nx.radius(subgraph),
                        "eta": eta_h,
                        "center": sorted(center_h),
                        "rooted_depth": rooted_h,
                        "good": rooted_h >= eta,
                    })
                good = [row for row in deletions if row["good"]]
                graph_has_good_root = graph_has_good_root or bool(good)
                root_rows.append({"x": x, "deletions": deletions})
                if not good and first_failure is None:
                    first_failure = {
                        "graph6": code.decode(),
                        "n": n,
                        "m": graph.number_of_edges(),
                        "rank": cycle_rank(graph),
                        "girth": g,
                        "radius": nx.radius(graph),
                        "eta": eta,
                        "center": sorted(center),
                        "realizers": realizers,
                        "failed_root": x,
                        "edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges()),
                        "root_rows": root_rows,
                    }
            if not graph_has_good_root and first_graph_without_any_good_root is None:
                first_graph_without_any_good_root = {
                    "graph6": code.decode(),
                    "n": n,
                    "m": graph.number_of_edges(),
                    "rank": cycle_rank(graph),
                    "girth": g,
                    "radius": nx.radius(graph),
                    "eta": eta,
                    "center": sorted(center),
                    "realizers": realizers,
                    "edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges()),
                    "root_rows": root_rows,
                }
            if first_failure is not None and first_graph_without_any_good_root is not None:
                return {
                    "checked_graphs": checked_graphs,
                    "checked_roots": checked_roots,
                    "first_failed_fixed_root": first_failure,
                    "first_graph_without_any_good_root": first_graph_without_any_good_root,
                }

    return {
        "checked_graphs": checked_graphs,
        "checked_roots": checked_roots,
        "first_failed_fixed_root": first_failure,
        "first_graph_without_any_good_root": first_graph_without_any_good_root,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=11)
    parser.add_argument("--output", type=Path, default=HERE / "rooted_eta_deletion_results.json")
    args = parser.parse_args()
    result = audit(args.min_n, args.max_n)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
