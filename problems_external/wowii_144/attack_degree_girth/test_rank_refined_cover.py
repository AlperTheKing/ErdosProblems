#!/usr/bin/env python3
"""Test the rank-refined version of the proved total-cover argument.

On the W144-COMB residual, put kappa=beta-1.  The tested load-bearing
strengthening is obtained by replacing q-h by q-h-kappa in the total-cover
upper bound.  Its exact bridge is e<=q-kappa, i.e. the rank term in W144-COMB.
"""

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
W141 = HERE.parent.parent / "wowii_141" / "oracle"
W144O = HERE.parent / "oracle"
sys.path[:0] = [str(W141), str(W144O)]
from bridge_tests import shortest_cycles  # noqa: E402
from invariants import all_pairs_dist, eccentricities, girth, nx_to_bitadj  # noqa: E402


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
    parser.add_argument("--max-n", type=int, default=13)
    parser.add_argument("--output", type=Path, default=HERE / "rank_refined_cover_audit.json")
    args = parser.parse_args()
    out = {"max_n": args.max_n, "residual_graphs": 0, "cases": 0,
           "direct_cases": 0, "minimum_slack": None, "failures": []}
    for n in range(5, args.max_n + 1):
        for code, graph in records(n):
            n0, adjacency = nx_to_bitadj(graph)
            g = girth(n0, adjacency)
            beta = graph.number_of_edges() - n + 1
            if g < 5 or beta < 2:
                continue
            dist = all_pairs_dist(n0, adjacency)
            eccentricity = eccentricities(n0, dist)
            radius = min(eccentricity)
            center = [v for v in range(n) if eccentricity[v] == radius]
            eta = max(min(dist[v][c] for c in center) for v in range(n))
            delta = max(dict(graph.degree()).values())
            diameter = max(eccentricity)
            if eta < delta or eta <= diameter - g // 2:
                continue
            out["residual_graphs"] += 1
            realizers = [v for v in range(n)
                         if min(dist[v][c] for c in center) == eta]
            q = n - g
            kappa = beta - 1
            for cycle in shortest_cycles(graph, g):
                components = [set(component) for component in nx.connected_components(
                    graph.subgraph(set(graph) - set(cycle)))]
                for x in realizers:
                    h = min(dist[x][a] for a in cycle)
                    if h >= eta:
                        slack = q - h - kappa
                        out["direct_cases"] += 1
                        out["cases"] += 1
                        out["minimum_slack"] = slack if out["minimum_slack"] is None else min(out["minimum_slack"], slack)
                        if slack < 0 and len(out["failures"]) < 20:
                            out["failures"].append({"graph6": code.decode(), "kind": "direct", "n": n,
                                "girth": g, "beta": beta, "eta": eta, "Delta": delta,
                                "diameter": diameter, "cycle": sorted(cycle), "x": x, "h": h,
                                "q": q, "kappa": kappa, "slack": slack})
                        continue
                    d = eta - h
                    for anchor in cycle:
                        if dist[x][anchor] != h:
                            continue
                        window = [a for a in cycle if dist[a][anchor] <= d - 1]
                        correction = max(0, 2 * d - g)
                        cover_sum = 0
                        for component in components:
                            cover_sum += sum(max((dist[a][y] for y in component), default=-1) >= radius + 1 for a in window)
                        slack = 2 * (q - h - kappa) - cover_sum - correction
                        out["cases"] += 1
                        out["minimum_slack"] = slack if out["minimum_slack"] is None else min(out["minimum_slack"], slack)
                        if slack < 0 and len(out["failures"]) < 20:
                            out["failures"].append({"graph6": code.decode(), "kind": "cover", "n": n,
                                "girth": g, "beta": beta, "eta": eta, "Delta": delta,
                                "diameter": diameter, "cycle": sorted(cycle), "x": x, "h": h,
                                "anchor": anchor, "q": q, "kappa": kappa, "window": window,
                                "cover_sum": cover_sum, "correction": correction, "slack": slack})
        if out["failures"]:
            break
    args.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
