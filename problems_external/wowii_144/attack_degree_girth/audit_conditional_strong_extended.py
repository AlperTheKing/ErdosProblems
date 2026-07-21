#!/usr/bin/env python3
"""Extend the exact conditional strong-bound audit using geng -Ctfq."""

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
from audit_degree_girth_bound import maximum_induced_tree  # noqa: E402


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
    parser.add_argument("orders", type=int, nargs="+", default=[14])
    parser.add_argument("--output", type=Path, default=HERE / "conditional_strong_extended.json")
    args = parser.parse_args()
    result = {"generator": "geng -Ctfq", "orders": args.orders, "per_order": {},
              "residuals": 0, "failures": 0, "minimum_slack": None,
              "first_failure": None, "first_minimum": None}
    for n in args.orders:
        generated = retained = residuals = 0
        for code, graph in records(n):
            generated += 1
            g = girth(graph)
            if g is None or g < 5 or cycle_rank(graph) < 2:
                continue
            retained += 1
            delta = max(dict(graph.degree()).values())
            eta, center = center_depth(graph)
            diameter = nx.diameter(graph)
            if eta != delta or diameter - g // 2 >= eta:
                continue
            residuals += 1
            result["residuals"] += 1
            tree, witness = maximum_induced_tree(graph)
            slack = tree - (delta + g - 1)
            item = {"graph6": code.decode(), "n": n, "m": graph.number_of_edges(),
                    "beta": cycle_rank(graph), "girth": g, "diameter": diameter,
                    "maximum_degree": delta, "eta": eta, "center": sorted(center),
                    "tree": tree, "slack": slack, "witness": sorted(witness),
                    "edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges())}
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
