#!/usr/bin/env python3
"""Audit t(G) >= Delta+g-1 on the exact eta=Delta metric residual."""

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
from audit_degree_girth_bound import maximum_induced_tree  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=13)
    parser.add_argument("--output", type=Path, default=HERE / "conditional_strong_audit.json")
    args = parser.parse_args()
    total = residual = failures = 0
    per_order: dict[int, int] = {}
    first_residual = first_failure = minimum = None
    min_slack = None
    for n in range(5, args.max_n + 1):
        per_order[n] = 0
        for code, graph in records(n):
            g = girth(graph)
            if g is None or g < 5 or cycle_rank(graph) < 2 or not nx.is_biconnected(graph):
                continue
            total += 1
            delta = max(dict(graph.degree()).values())
            eta, center = center_depth(graph)
            diameter = nx.diameter(graph)
            if eta != delta or diameter - g // 2 >= eta:
                continue
            residual += 1
            per_order[n] += 1
            tree, witness = maximum_induced_tree(graph)
            slack = tree - (delta + g - 1)
            item = {
                "graph6": code.decode(), "n": n, "m": graph.number_of_edges(),
                "girth": g, "diameter": diameter, "maximum_degree": delta,
                "eta": eta, "center": sorted(center), "tree": tree,
                "slack": slack, "witness": sorted(witness),
                "edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges()),
            }
            if first_residual is None:
                first_residual = item
            if min_slack is None or slack < min_slack:
                min_slack, minimum = slack, item
            if slack < 0:
                failures += 1
                if first_failure is None:
                    first_failure = item
    result = {
        "scope": "biconnected multicyclic girth>=5; eta=Delta and diameter-floor(girth/2)<eta",
        "max_n": args.max_n, "total_base_graphs": total, "residual_graphs": residual,
        "per_order": per_order, "failures": failures, "minimum_slack": min_slack,
        "first_residual": first_residual, "first_minimum": minimum,
        "first_failure": first_failure,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
