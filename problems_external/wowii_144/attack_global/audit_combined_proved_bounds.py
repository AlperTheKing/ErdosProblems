#!/usr/bin/env python3
"""Audit whether proved W141/W142/W143/P2 bounds already imply W144."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


def graph_girth(graph: nx.Graph) -> int | None:
    best = None
    for root in graph:
        dist = {root: 0}
        parent = {root: None}
        queue = [root]
        for u in queue:
            for v in graph[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    queue.append(v)
                elif parent[u] != v:
                    length = dist[u] + dist[v] + 1
                    if best is None or length < best:
                        best = length
    return best


def audit_graph(code: str, graph: nx.Graph) -> dict | None:
    g = graph_girth(graph)
    if g is None or g < 5:
        return None
    ecc = nx.eccentricity(graph)
    r = min(ecc.values())
    diameter = max(ecc.values())
    center = [v for v, value in ecc.items() if value == r]
    periphery = [v for v, value in ecc.items() if value == diameter]
    eta = max(nx.multi_source_dijkstra_path_length(graph, center).values())
    f = max(nx.multi_source_dijkstra_path_length(graph, periphery).values())
    degrees = sorted(dict(graph.degree()).values())
    delta2 = degrees[1]
    Delta = degrees[-1]
    target = g - 1 + eta
    bounds = {
        "cycle": g - 1,
        "P2": diameter + math.ceil(g / 2) - 1,
        "W141": g // 2 - 1 + Delta,
        "W142": math.ceil(2 * g / 3) + f,
        "W143": math.ceil((g + 1) / delta2),
        "radius_path": 2 * r - 1,
    }
    best_name, best = max(bounds.items(), key=lambda item: item[1])
    beta = graph.number_of_edges() - graph.number_of_nodes() + 1
    return {
        "graph6": code,
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "g": g,
        "r": r,
        "D": diameter,
        "eta": eta,
        "f": f,
        "Delta": Delta,
        "delta2": delta2,
        "beta": beta,
        "target": target,
        "best": best,
        "best_name": best_name,
        "deficit": target - best,
        "bounds": bounds,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=13)
    parser.add_argument("--show", type=int, default=40)
    args = parser.parse_args()
    counts = Counter()
    residual = []
    total = 0
    for n in range(args.min_n, args.max_n + 1):
        proc = subprocess.Popen(
            [str(GENG), "-ctfq", str(n)], stdout=subprocess.PIPE, text=False
        )
        assert proc.stdout is not None
        per_n = per_n_residual = 0
        for raw in proc.stdout:
            code = raw.strip()
            if not code:
                continue
            row = audit_graph(code.decode(), nx.from_graph6_bytes(code))
            if row is None:
                continue
            total += 1
            per_n += 1
            counts[(row["deficit"], row["g"], row["eta"], row["beta"])] += 1
            if row["deficit"] > 0:
                per_n_residual += 1
                if len(residual) < args.show:
                    residual.append(row)
        if proc.wait() != 0:
            raise RuntimeError("geng failed")
        print({"n": n, "checked": per_n, "residual": per_n_residual}, flush=True)
    print(json.dumps({
        "checked": total,
        "residual_examples": residual,
        "residual_count_by_key": [
            {"deficit": key[0], "g": key[1], "eta": key[2],
             "beta": key[3], "count": value}
            for key, value in sorted(counts.items()) if key[0] > 0
        ],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
