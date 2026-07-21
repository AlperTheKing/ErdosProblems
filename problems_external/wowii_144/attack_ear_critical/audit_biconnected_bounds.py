#!/usr/bin/env python3
"""Audit P2 and W141 bounds on the exact biconnected W144 corpus."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
IND2 = HERE.parent / "attack_ind2_multicycle"
sys.path.insert(0, str(IND2))
from analyze_tight_deletions import center_depth, cycle_rank, girth, records  # noqa: E402


def row(code: bytes, graph: nx.Graph, g: int, eta: int) -> dict:
    diameter = nx.diameter(graph)
    maximum_degree = max(dict(graph.degree()).values())
    target = g - 1 + eta
    p2 = diameter + (g + 1) // 2 - 1
    w141 = maximum_degree + g // 2 - 1
    strong141 = maximum_degree + g - 3
    return {
        "graph6": code.decode(),
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "beta": cycle_rank(graph),
        "girth": g,
        "diameter": diameter,
        "eta": eta,
        "maximum_degree": maximum_degree,
        "target": target,
        "p2": p2,
        "target_minus_p2": target - p2,
        "w141": w141,
        "target_minus_w141": target - w141,
        "strong141": strong141,
        "target_minus_strong141": target - strong141,
        "edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=13)
    parser.add_argument("--show", type=int, default=20)
    parser.add_argument("--output", type=Path, default=HERE / "biconnected_bound_audit.json")
    args = parser.parse_args()
    totals = Counter()
    first: dict[str, list[dict]] = {
        "p2_residual": [],
        "p2_and_w141_residual": [],
        "p2_and_strong141_residual": [],
    }
    worst: dict[str, dict | None] = {key: None for key in first}
    for n in range(5, args.max_n + 1):
        for code, graph in records(n):
            g = girth(graph)
            if g is None or g < 5 or cycle_rank(graph) < 2 or not nx.is_biconnected(graph):
                continue
            totals["graphs"] += 1
            eta, _ = center_depth(graph)
            item = row(code, graph, g, eta)
            conditions = {
                "p2_residual": item["target_minus_p2"] > 0,
                "p2_and_w141_residual": item["target_minus_p2"] > 0
                and item["target_minus_w141"] > 0,
                "p2_and_strong141_residual": item["target_minus_p2"] > 0
                and item["target_minus_strong141"] > 0,
            }
            for label, applies in conditions.items():
                if not applies:
                    continue
                totals[label] += 1
                if len(first[label]) < args.show:
                    first[label].append(item)
                score_key = (
                    "target_minus_p2"
                    if label == "p2_residual"
                    else "target_minus_w141"
                    if label == "p2_and_w141_residual"
                    else "target_minus_strong141"
                )
                if worst[label] is None or item[score_key] > worst[label][score_key]:
                    worst[label] = item
    result = {
        "max_n": args.max_n,
        "totals": dict(totals),
        "first": first,
        "worst": worst,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"totals": result["totals"], "first": {k: v[:1] for k, v in first.items()}}, indent=2))


if __name__ == "__main__":
    main()
