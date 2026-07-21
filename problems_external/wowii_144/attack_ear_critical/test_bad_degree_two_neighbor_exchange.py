#!/usr/bin/env python3
"""Test the direct neighbor exchange for a bad degree-two deletion."""

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


def row(graph: nx.Graph, eta: int, v: int) -> dict | None:
    subgraph = graph.copy()
    subgraph.remove_node(v)
    if not nx.is_connected(subgraph) or cycle_rank(subgraph) < 1:
        return None
    eta_h, center_h = center_depth(subgraph)
    return {
        "v": v,
        "degree": graph.degree[v],
        "eta": eta_h,
        "delta_eta": eta_h - eta,
        "radius": nx.radius(subgraph),
        "center": sorted(center_h),
        "girth": girth(subgraph),
        "beta": cycle_rank(subgraph),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=13)
    parser.add_argument("--min-beta", type=int, default=2)
    parser.add_argument(
        "--output", type=Path, default=HERE / "bad_degree_two_neighbor_exchange.json"
    )
    args = parser.parse_args()
    graphs = 0
    bad_degree_two = 0
    first_failure = None
    for n in range(5, args.max_n + 1):
        for code, graph in records(n):
            g = girth(graph)
            if (
                g is None
                or g < 5
                or cycle_rank(graph) < args.min_beta
                or not nx.is_biconnected(graph)
            ):
                continue
            graphs += 1
            eta, center = center_depth(graph)
            rows = {v: row(graph, eta, v) for v in sorted(graph)}
            for v in sorted(graph):
                if graph.degree[v] != 2 or rows[v]["delta_eta"] >= 0:
                    continue
                bad_degree_two += 1
                neighbors = sorted(graph[v])
                if any(
                    rows[u] is not None and rows[u]["delta_eta"] >= 0
                    for u in neighbors
                ):
                    continue
                first_failure = {
                    "graph6": code.decode(),
                    "n": n,
                    "m": graph.number_of_edges(),
                    "beta": cycle_rank(graph),
                    "girth": g,
                    "radius": nx.radius(graph),
                    "eta": eta,
                    "center": sorted(center),
                    "bad_vertex": v,
                    "bad_row": rows[v],
                    "neighbors": neighbors,
                    "neighbor_rows": {str(u): rows[u] for u in neighbors},
                    "edges": sorted([min(a, b), max(a, b)] for a, b in graph.edges()),
                }
                break
            if first_failure is not None:
                break
        if first_failure is not None:
            break
    result = {
        "statement": "every bad degree-two deletion has an eta-good admissible neighbor",
        "max_n": args.max_n,
        "min_beta": args.min_beta,
        "graphs_checked_before_failure": graphs,
        "bad_degree_two_checked_before_failure": bad_degree_two,
        "first_failure": first_failure,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if first_failure is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
