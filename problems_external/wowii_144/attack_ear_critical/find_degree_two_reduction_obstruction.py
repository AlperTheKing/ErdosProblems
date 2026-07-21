#!/usr/bin/env python3
"""Find the first obstruction to a last-ear/degree-two eta deletion rule."""

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


def deletion_row(graph: nx.Graph, eta: int, v: int) -> dict:
    subgraph = graph.copy()
    subgraph.remove_node(v)
    eta_h, center_h = center_depth(subgraph)
    return {
        "v": v,
        "degree": graph.degree[v],
        "radius": nx.radius(subgraph),
        "eta": eta_h,
        "delta_eta": eta_h - eta,
        "center": sorted(center_h),
        "girth": girth(subgraph),
        "beta": cycle_rank(subgraph),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=13)
    parser.add_argument(
        "--output", type=Path, default=HERE / "degree_two_reduction_obstruction.json"
    )
    args = parser.parse_args()
    checked = 0
    applicable = 0
    first_failure = None
    for n in range(5, args.max_n + 1):
        for code, graph in records(n):
            g = girth(graph)
            if (
                g is None
                or g < 5
                or cycle_rank(graph) < 3
                or not nx.is_biconnected(graph)
            ):
                continue
            checked += 1
            degree_two = sorted(v for v in graph if graph.degree[v] == 2)
            if not degree_two:
                continue
            applicable += 1
            eta, center = center_depth(graph)
            rows = [deletion_row(graph, eta, v) for v in sorted(graph)]
            low_rows = [row for row in rows if row["degree"] == 2]
            if max(row["delta_eta"] for row in low_rows) >= 0:
                continue
            good = [row for row in rows if row["delta_eta"] >= 0]
            first_failure = {
                "graph6": code.decode(),
                "n": n,
                "m": graph.number_of_edges(),
                "beta": cycle_rank(graph),
                "girth": g,
                "radius": nx.radius(graph),
                "eta": eta,
                "center": sorted(center),
                "degree_sequence": sorted(dict(graph.degree()).values()),
                "edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges()),
                "degree_two_deletions": low_rows,
                "eta_good_deletions": good,
            }
            break
        if first_failure is not None:
            break
    result = {
        "statement": "some degree-two vertex has eta(G-v)>=eta(G) in every biconnected beta>=3 graph",
        "max_n": args.max_n,
        "checked_before_failure": checked,
        "applicable_before_failure": applicable,
        "first_failure": first_failure,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if first_failure is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
