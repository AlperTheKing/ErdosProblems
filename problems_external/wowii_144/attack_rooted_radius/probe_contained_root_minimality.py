#!/usr/bin/env python3
"""Find a multicyclic eta-minimal induced subgraph forced to contain a root."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
IND2 = HERE.parent / "attack_ind2_multicycle"
sys.path.insert(0, str(IND2))
from analyze_tight_deletions import center_depth, cycle_rank, girth, records  # noqa: E402


def distance_to_set(graph: nx.Graph, source: int, targets: set[int]) -> int:
    lengths = nx.single_source_shortest_path_length(graph, source)
    return min(lengths[t] for t in targets)


def graph_failure(graph: nx.Graph, eta: int, realizers: list[int]) -> dict | None:
    vertices = sorted(graph)
    minimal: dict[int, list[frozenset[int]]] = {x: [] for x in realizers}
    for size in range(3, len(vertices) + 1):
        for subset_tuple in itertools.combinations(vertices, size):
            subset = frozenset(subset_tuple)
            roots_here = [x for x in realizers if x in subset]
            if not roots_here:
                continue
            subgraph = graph.subgraph(subset).copy()
            if subgraph.number_of_edges() < subgraph.number_of_nodes():
                continue
            if not nx.is_connected(subgraph):
                continue
            eta_h, center_h = center_depth(subgraph)
            if eta_h < eta:
                continue
            rank_h = cycle_rank(subgraph)
            for root in roots_here:
                if any(old < subset for old in minimal[root]):
                    continue
                if rank_h >= 2:
                    return {
                        "root": root,
                        "vertices": sorted(subset),
                        "n": len(subset),
                        "m": subgraph.number_of_edges(),
                        "rank": rank_h,
                        "girth": girth(subgraph),
                        "radius": nx.radius(subgraph),
                        "eta": eta_h,
                        "center": sorted(center_h),
                    }
                minimal[root].append(subset)
    return None


def audit(min_n: int, max_n: int) -> dict:
    total = 0
    per_order: dict[str, int] = {}
    failure = None
    for n in range(min_n, max_n + 1):
        checked = 0
        for code, graph in records(n):
            g = girth(graph)
            if g is None or g < 5 or cycle_rank(graph) < 2:
                continue
            checked += 1
            total += 1
            eta, center = center_depth(graph)
            realizers = [
                x for x in sorted(graph)
                if distance_to_set(graph, x, set(center)) == eta
            ]
            witness = graph_failure(graph, eta, realizers)
            if witness is not None:
                failure = {
                    "graph6": code.decode(),
                    "ambient_n": n,
                    "ambient_m": graph.number_of_edges(),
                    "ambient_rank": cycle_rank(graph),
                    "ambient_girth": g,
                    "ambient_radius": nx.radius(graph),
                    "ambient_eta": eta,
                    "ambient_center": sorted(center),
                    "ambient_realizers": realizers,
                    "ambient_edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges()),
                    "minimal_subgraph": witness,
                }
                break
        per_order[str(n)] = checked
        if failure is not None:
            break
    return {"min_n": min_n, "max_n": max_n, "total_checked": total, "per_order": per_order, "failure": failure}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--output", type=Path, default=HERE / "contained_root_minimality_results.json")
    args = parser.parse_args()
    result = audit(args.min_n, args.max_n)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["failure"] is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
