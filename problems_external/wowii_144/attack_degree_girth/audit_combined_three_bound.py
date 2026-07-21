#!/usr/bin/env python3
"""Exact audit of the registered W144-COMB three-bound cover."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"
IND2 = HERE.parent / "attack_ind2_multicycle"
sys.path.insert(0, str(IND2))
from analyze_tight_deletions import center_depth, cycle_rank, girth  # noqa: E402


def records(order: int):
    run = subprocess.Popen([str(GENG), "-Ctfq", str(order)], stdout=subprocess.PIPE)
    assert run.stdout is not None
    for line in run.stdout:
        code = line.strip()
        if code:
            yield code, nx.from_graph6_bytes(code)
    if run.wait() != 0:
        raise RuntimeError("geng failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=14)
    parser.add_argument("--output", type=Path, default=HERE / "combined_three_bound_audit.json")
    args = parser.parse_args()
    result = {
        "statement": "eta <= max(Delta-1, diameter-floor(girth/2), n-girth-beta+1)",
        "generator": "geng -Ctfq", "max_n": args.max_n, "per_order": {},
        "graphs": 0, "residuals": 0, "failures": 0, "minimum_slack": None,
        "first_minimum": None, "first_failure": None,
    }
    for n in range(5, args.max_n + 1):
        generated = retained = residuals = 0
        for code, graph in records(n):
            generated += 1
            g = girth(graph)
            beta = cycle_rank(graph)
            if g is None or g < 5 or beta < 2:
                continue
            retained += 1
            result["graphs"] += 1
            eta, center = center_depth(graph)
            delta = max(dict(graph.degree()).values())
            diameter = nx.diameter(graph)
            degree_term = delta - 1
            diameter_term = diameter - g // 2
            rank_term = n - g - beta + 1
            slack = max(degree_term, diameter_term, rank_term) - eta
            residual = eta >= delta and eta > diameter_term
            if residual:
                residuals += 1
                result["residuals"] += 1
            item = {
                "graph6": code.decode(), "n": n, "m": graph.number_of_edges(),
                "beta": beta, "girth": g, "diameter": diameter,
                "maximum_degree": delta, "eta": eta, "center": sorted(center),
                "degree_term": degree_term, "diameter_term": diameter_term,
                "rank_term": rank_term, "slack": slack,
                "residual_rank_slack": n - g + 1 - eta - beta,
                "edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges()),
            }
            if result["minimum_slack"] is None or slack < result["minimum_slack"]:
                result["minimum_slack"] = slack
                result["first_minimum"] = item
            if slack < 0:
                result["failures"] += 1
                if result["first_failure"] is None:
                    result["first_failure"] = item
        result["per_order"][n] = {"generated": generated, "retained": retained,
                                  "residuals": residuals}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
