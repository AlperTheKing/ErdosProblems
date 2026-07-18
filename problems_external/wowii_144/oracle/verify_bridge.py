#!/usr/bin/env python3
"""Independent verification of the bridge-claim counterexamples found by
bridge_tests.py, using ONLY plain networkx primitives (no code reuse from
invariants.py): nx.from_graph6_bytes, nx.eccentricity, nx.shortest_path_length,
full nx.simple_cycles (no length bound), brute-force induced-tree search.

Prints a human-readable certificate for each counterexample and writes
verify_bridge_report.json.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "verify_bridge_report.json"


def load(g6: str) -> nx.Graph:
    return nx.from_graph6_bytes(g6.encode())


def center_data(G: nx.Graph):
    ecc = nx.eccentricity(G)
    radius = min(ecc.values())
    center = sorted(v for v in G if ecc[v] == radius)
    dist = dict(nx.all_pairs_shortest_path_length(G))
    if len(center) == len(G):
        ecc_center = 0
    else:
        ecc_center = max(min(dist[v][c] for c in center)
                         for v in G if v not in center)
    return ecc, radius, center, dist, ecc_center


def all_shortest_cycles(G: nx.Graph):
    """ALL simple cycles, unbounded, then keep the minimum length."""
    cycles = [c for c in nx.simple_cycles(G)]
    if not cycles:
        return 0, []
    g = min(len(c) for c in cycles)
    return g, sorted({frozenset(c) for c in cycles if len(c) == g}, key=sorted)


def tree_number(G: nx.Graph) -> int:
    best = 1
    nodes = list(G)
    for k in range(len(nodes), 0, -1):
        if k <= best:
            break
        for S in combinations(nodes, k):
            H = G.subgraph(S)
            if nx.is_connected(H) and H.number_of_edges() == k - 1:
                best = k
                break
        if best == k:
            break
    return best


def verify_q1(g6: str) -> dict:
    G = load(g6)
    ecc, radius, center, dist, ecc_center = center_data(G)
    g, cycles = all_shortest_cycles(G)
    per_cycle = []
    overall = -1
    for K in cycles:
        mx = max(min(dist[x][k] for k in K) for x in G)
        per_cycle.append({"cycle": sorted(K), "max_x_dist": mx})
        overall = max(overall, mx)
    t = tree_number(G)
    rec = {
        "graph6": g6, "n": len(G), "edges": sorted(map(sorted, G.edges())),
        "girth": g, "num_shortest_cycles": len(cycles),
        "per_cycle_max_dist": per_cycle,
        "radius": radius, "center": center, "ecc_center": ecc_center,
        "max_K_max_x": overall,
        "q1_holds_here": overall >= ecc_center,
        "tree": t,
        "c144_lhs": g - 1 + ecc_center,
        "c144_holds_here": g - 1 + ecc_center <= t,
    }
    return rec


def verify_q2(g6: str, v: int) -> dict:
    G = load(g6)
    ecc, radius, center, dist, ecc_center = center_data(G)
    dvc = min(dist[v][c] for c in center)
    rec = {
        "graph6": g6, "n": len(G), "edges": sorted(map(sorted, G.edges())),
        "vertex": v, "eccent_v": ecc[v], "radius": radius, "center": center,
        "dist_v_center": dvc,
        "q2_holds_here": ecc[v] >= radius + dvc,
    }
    return rec


def verify_q4(g6: str) -> dict:
    G = load(g6)
    ecc, radius, center, dist, ecc_center = center_data(G)
    diam = max(ecc.values())
    t = tree_number(G)
    per_path = []
    for u, v in combinations(sorted(G), 2):
        if dist[u][v] != diam:
            continue
        for P in nx.all_shortest_paths(G, u, v):
            mx = max(min(dist[x][w] for w in P) for x in G)
            per_path.append({"path": list(P), "max_x_dist": mx,
                             "lhs": len(P) + mx})
    best_lhs = min(p["lhs"] for p in per_path)
    rec = {
        "graph6": g6, "n": len(G), "edges": sorted(map(sorted, G.edges())),
        "tree": t, "diam": diam,
        "diametral_geodesics": per_path,
        "min_over_P_lhs": best_lhs,
        "q4_exists_holds_here": best_lhs <= t,
    }
    return rec


def main() -> None:
    report = {
        # Q1 smallest CE (n=6) + a families CE (slack -2) + adversarial (slack -3)
        "q1": [verify_q1("EQKo"),
               verify_q1("KhCGKE??GO?@"),
               verify_q1("XhCGGC@_K??@?@??_?G_???C??G??G??CA?????G???_??@???@")],
        # Q2 smallest CE (n=7, vertex 0) + a second n=7 CE + adversarial slack -3
        "q2": [verify_q2("FMoG_", 0),
               verify_q2("FhELO", 1),
               verify_q2("XhCGGC@_K??@?@??_?G_???C??G??G??CA?????G???_??@???@", 7)],
        # Q4 smallest CE (triangle, n=3) + slack -2 witness
        "q4": [verify_q4("Bw"), verify_q4("E@dW")],
    }
    ok = (all(not r["q1_holds_here"] and r["c144_holds_here"]
              for r in report["q1"])
          and all(not r["q2_holds_here"] for r in report["q2"])
          and all(not r["q4_exists_holds_here"] for r in report["q4"]))
    report["all_counterexamples_confirmed"] = ok
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
