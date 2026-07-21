#!/usr/bin/env python3
"""Test one-swap ascent for the exact complement objective b(X)."""
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
from test_steiner_vertex_fast import GENG, is_connected


def b_values(n: int, adjacency: list[int], k: int) -> dict[int, int]:
    limit = 1 << n
    best_superset = [n + 1] * limit
    for mask in range(1, limit):
        if is_connected(mask, adjacency):
            best_superset[mask] = mask.bit_count()
    for bit_index in range(n):
        bit = 1 << bit_index
        for mask in range(limit):
            if not mask & bit:
                best_superset[mask] = min(best_superset[mask],
                                           best_superset[mask | bit])
    full = limit - 1
    return {x: best_superset[full ^ x] - k for x in range(limit)
            if x.bit_count() == n - k}


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
    e = max(min(dist[x][c] for c in center) for x in range(n))
    values = b_values(n, adjacency, k)
    for v in range(n):
        allowed = {x: value for x, value in values.items() if not x >> v & 1}
        assert max(allowed.values()) >= e
        for x, value in allowed.items():
            if value >= e:
                continue
            outside = ((1 << n) - 1) ^ x
            outside &= ~(1 << v)
            ascent = False
            work_x = x
            while work_x and not ascent:
                a = work_x & -work_x
                work_x ^= a
                work_s = outside
                while work_s:
                    s = work_s & -work_s
                    work_s ^= s
                    if allowed[(x ^ a) | s] > value:
                        ascent = True
                        break
            if not ascent:
                edges = [[u, w] for u in range(n) for w in range(u + 1, n)
                         if adjacency[u] >> w & 1]
                return {"graph6": graph6, "n": n, "g": g, "radius": r,
                        "center": center, "e": e, "v": v,
                        "X": [u for u in range(n) if x >> u & 1],
                        "b": value, "edges": edges}
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
            if "X" in rec:
                print(json.dumps({"graphs": checked, "failure": rec},
                                 indent=2, sort_keys=True))
                return
        print(n, checked, flush=True)
    print(json.dumps({"graphs": checked, "failure": None}, indent=2))


if __name__ == "__main__":
    main()
