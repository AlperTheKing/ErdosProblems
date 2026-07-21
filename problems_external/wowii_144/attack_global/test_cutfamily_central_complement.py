#!/usr/bin/env python3
"""Test minimum-center-distance complements for the exact W144-S cut family."""
from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [
    str(ROOT / "problems_external" / "wowii_141" / "oracle"),
    str(ROOT / "problems_external" / "wowii_144" / "oracle_exhaustive"),
    str(ROOT / "problems_external" / "wowii_144" / "attack_global"),
]
from invariants import all_pairs_dist, eccentricities, girth
from run_sweep import parse_graph6
from test_cutfamily_exchange import b_values
from test_steiner_vertex_fast import GENG


def audit_one(graph6: str) -> dict | None:
    n, adjacency = parse_graph6(graph6)
    g = girth(n, adjacency)
    if g < 5:
        return None
    k, p = g - 1, n - g + 1
    dist = all_pairs_dist(n, adjacency)
    ecc = eccentricities(n, dist)
    r = min(ecc)
    center = [u for u in range(n) if ecc[u] == r]
    dc = [min(dist[x][c] for c in center) for x in range(n)]
    e = max(dc)
    values = b_values(n, adjacency, k)
    for v in range(n):
        available = [u for u in range(n) if u != v]
        min_weight = min(sum(dc[u] for u in choice)
                         for choice in itertools.combinations(available, p))
        best = -1
        candidates = 0
        for choice in itertools.combinations(available, p):
            if sum(dc[u] for u in choice) != min_weight:
                continue
            candidates += 1
            x = sum(1 << u for u in choice)
            best = max(best, values[x])
        if best < e:
            edges = [[u, w] for u in range(n) for w in range(u + 1, n)
                     if adjacency[u] >> w & 1]
            return {"graph6": graph6, "n": n, "g": g, "radius": r,
                    "center": center, "center_distance": dc, "e": e,
                    "v": v, "p": p, "min_weight": min_weight,
                    "candidates": candidates, "best_b": best,
                    "edges": edges}
    return {"n": n}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=11)
    args = parser.parse_args()
    checked = 0
    for n in range(5, args.max_n + 1):
        proc = subprocess.run([str(GENG), "-c", "-t", "-f", "-q", str(n)],
                              check=True, capture_output=True, text=True)
        for graph6 in proc.stdout.split():
            rec = audit_one(graph6)
            if rec is None:
                continue
            checked += 1
            if "v" in rec:
                print(json.dumps({"graphs": checked, "failure": rec},
                                 indent=2, sort_keys=True))
                return
        print(n, checked, flush=True)
    print(json.dumps({"graphs": checked, "failure": None}, indent=2))


if __name__ == "__main__":
    main()
