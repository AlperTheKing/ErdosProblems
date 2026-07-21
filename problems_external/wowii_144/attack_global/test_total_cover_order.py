#!/usr/bin/env python3
"""Exact audit of the direct total-off-cycle cover bound for W144.

For each connected graph of girth at least five, each shortest cycle K, and
each maximum-height realizer x of ecc(G,C) relative to K, this tests the
window W about every nearest anchor m, including the wrap correction:

    |W| <= sum_H |E_H cap W|,
    sum_H |E_H cap W| + max(0,2(e-h)-g) <= 2 (n-g-h).

Here h=d(x,K), and E_H consists of cycle vertices having an r+1-distant
witness in the component H of G-K.  The first inequality is also checked
directly; the second is the proposed load-bearing order-cover lemma.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
W141 = HERE.parent.parent / "wowii_141" / "oracle"
W144O = HERE.parent / "oracle"
sys.path[:0] = [str(W141), str(W144O)]

from bridge_tests import shortest_cycles  # noqa: E402
from invariants import (all_pairs_dist, dist_to_set, eccentricities, girth,
                        nx_to_bitadj)  # noqa: E402
from test_steiner_vertex_fast import GENG  # noqa: E402


def audit_one(g6: str) -> dict | None:
    G = nx.from_graph6_bytes(g6.encode())
    G = nx.convert_node_labels_to_integers(G)
    n, adj = nx_to_bitadj(G)
    g = girth(n, adj)
    if g < 5:
        return None
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    r = min(ecc)
    center = [v for v in range(n) if ecc[v] == r]
    e = max(min(dist[v][c] for c in center) for v in range(n))
    if e == 0:
        return {"g6": g6, "n": n, "g": g, "cases": 0,
                "min_cover_slack": None, "min_window_slack": None,
                "failures": []}
    realizers = [v for v in range(n)
                 if min(dist[v][c] for c in center) == e]
    cases = 0
    min_cover_slack = 10**9
    min_window_slack = 10**9
    failures = []
    for K in shortest_cycles(G, g):
        kset = set(K)
        heights = {x: min(dist[x][a] for a in K) for x in realizers}
        max_h = max(heights.values())
        q = n - g
        comps = [set(H) for H in nx.connected_components(
            G.subgraph(set(G) - kset))]
        for x in realizers:
            if heights[x] != max_h:
                continue
            h = max_h
            if h >= e:
                continue
            delta = e - h
            anchors = [m for m in K if dist[x][m] == h]
            for m in anchors:
                W = [a for a in K if dist[a][m] <= delta - 1]
                correction = max(0, 2 * delta - g)
                if correction == 0:
                    assert len(W) == 2 * delta - 1
                else:
                    assert len(W) == g
                covsum = 0
                uncovered = []
                for sig in W:
                    covered = False
                    for H in comps:
                        if max((dist[sig][y] for y in H), default=-1) >= r + 1:
                            covered = True
                    if not covered:
                        uncovered.append(sig)
                for H in comps:
                    covsum += sum(
                        max((dist[sig][y] for y in H), default=-1) >= r + 1
                        for sig in W)
                cases += 1
                window_slack = covsum - len(W)
                cover_slack = 2 * (q - h) - covsum - correction
                min_window_slack = min(min_window_slack, window_slack)
                min_cover_slack = min(min_cover_slack, cover_slack)
                if uncovered or cover_slack < 0:
                    failures.append({
                        "graph6": g6, "n": n, "g": g, "r": r, "e": e,
                        "K": sorted(K), "x": x, "h": h, "m": m,
                        "delta": delta, "q": q, "W": W,
                        "correction": correction,
                        "covsum": covsum, "uncovered": uncovered,
                        "cover_slack": cover_slack,
                    })
    return {"g6": g6, "n": n, "g": g, "cases": cases,
            "min_cover_slack": None if cases == 0 else min_cover_slack,
            "min_window_slack": None if cases == 0 else min_window_slack,
            "failures": failures[:2]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=12)
    parser.add_argument("--workers", type=int, default=24)
    args = parser.parse_args()
    out = {"graphs": 0, "cases": 0, "min_cover_slack": 10**9,
           "min_window_slack": 10**9, "failures": [], "per_n": {}}
    for n in range(args.min_n, args.max_n + 1):
        proc = subprocess.run([str(GENG), "-c", "-t", "-f", "-q", str(n)],
                              check=True, capture_output=True, text=True)
        g6s = proc.stdout.split()
        tested = 0
        if args.workers == 1:
            records = map(audit_one, g6s)
        else:
            executor = concurrent.futures.ProcessPoolExecutor(
                max_workers=args.workers)
            records = executor.map(audit_one, g6s, chunksize=32)
        try:
            for rec in records:
                if rec is None:
                    continue
                tested += 1
                out["graphs"] += 1
                out["cases"] += rec["cases"]
                if rec["min_cover_slack"] is not None:
                    out["min_cover_slack"] = min(
                        out["min_cover_slack"], rec["min_cover_slack"])
                    out["min_window_slack"] = min(
                        out["min_window_slack"], rec["min_window_slack"])
                if rec["failures"] and len(out["failures"]) < 20:
                    out["failures"].extend(rec["failures"])
        finally:
            if args.workers != 1:
                executor.shutdown()
        out["per_n"][str(n)] = {"generated": len(g6s), "tested": tested}
        print(n, out["per_n"][str(n)], flush=True)
        if out["failures"]:
            break
    if out["cases"] == 0:
        out["min_cover_slack"] = None
        out["min_window_slack"] = None
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
