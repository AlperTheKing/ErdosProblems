#!/usr/bin/env python3
"""Find eta-deletion obstructions without the girth-at-least-five hypothesis."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
IND2 = HERE.parent / "attack_ind2_multicycle"
sys.path.insert(0, str(IND2))
from analyze_tight_deletions import GENG, center_depth, cycle_rank, girth  # noqa: E402


def records(order: int):
    process = subprocess.Popen(
        [str(GENG), "-Cq", str(order)], stdout=subprocess.PIPE, text=False
    )
    assert process.stdout is not None
    for line in process.stdout:
        code = line.strip()
        if code:
            yield code, nx.from_graph6_bytes(code)
    if process.wait() != 0:
        raise RuntimeError("geng failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--show", type=int, default=30)
    parser.add_argument("--output", type=Path, default=HERE / "short_girth_obstructions.json")
    args = parser.parse_args()
    totals: dict[str, int] = {}
    failures = []
    for n in range(3, args.max_n + 1):
        for code, graph in records(n):
            if cycle_rank(graph) < 2 or not nx.is_biconnected(graph):
                continue
            g = girth(graph)
            eta, center = center_depth(graph)
            deltas = []
            for v in sorted(graph):
                subgraph = graph.copy()
                subgraph.remove_node(v)
                if not nx.is_connected(subgraph) or cycle_rank(subgraph) < 1:
                    continue
                eta_h, center_h = center_depth(subgraph)
                deltas.append(
                    {
                        "v": v,
                        "degree": graph.degree[v],
                        "eta": eta_h,
                        "delta_eta": eta_h - eta,
                        "center": sorted(center_h),
                    }
                )
            if not deltas:
                continue
            key = f"girth_{g}"
            totals[key] = totals.get(key, 0) + 1
            if max(row["delta_eta"] for row in deltas) < 0:
                totals[key + "_failures"] = totals.get(key + "_failures", 0) + 1
                if len(failures) < args.show:
                    failures.append(
                        {
                            "graph6": code.decode(),
                            "n": n,
                            "m": graph.number_of_edges(),
                            "beta": cycle_rank(graph),
                            "girth": g,
                            "radius": nx.radius(graph),
                            "eta": eta,
                            "center": sorted(center),
                            "edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges()),
                            "deletions": deltas,
                        }
                    )
    result = {"max_n": args.max_n, "totals": totals, "failures": failures}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(totals, indent=2))
    print(f"recorded_failures={len(failures)}")


if __name__ == "__main__":
    main()
