#!/usr/bin/env python3
"""Exact audit of e_{g-1}(v) >= g-2+d(v,Center(G))."""
from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [
    str(HERE),
    str(ROOT / "problems_external" / "wowii_141" / "oracle"),
    str(ROOT / "problems_external" / "wowii_144" / "oracle_exhaustive"),
]
from invariants import (all_pairs_dist, dist_to_set, eccentricities, girth)
from run_sweep import parse_graph6
from test_steiner_metric import connected_masks

GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


def audit(g6: str) -> list[dict]:
    n, adj = parse_graph6(g6)
    g = girth(n, adj)
    if g < 5:
        return []
    k = g - 1
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    radius = min(ecc)
    center = sum(1 << v for v in range(n) if ecc[v] == radius)
    best = {sum(1 << v for v in S): n + 1
            for S in itertools.combinations(range(n), k)}
    for mask in connected_masks(n, adj):
        size = mask.bit_count()
        if size < k:
            continue
        vertices = [v for v in range(n) if mask >> v & 1]
        for S in itertools.combinations(vertices, k):
            smask = sum(1 << v for v in S)
            if size < best[smask]:
                best[smask] = size
    records = []
    for v in range(n):
        eligible = [(size - 1, smask) for smask, size in best.items()
                    if smask >> v & 1]
        steiner_ecc, witness = max(eligible)
        dc = dist_to_set(dist, v, center)
        need = g - 2 + dc
        records.append({
            "graph6": g6, "n": n, "g": g, "v": v,
            "distance_to_center": dc,
            "steiner_eccentricity": steiner_ecc,
            "need": need, "slack": steiner_ecc - need,
            "witness": [u for u in range(n) if witness >> u & 1],
        })
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=11)
    args = parser.parse_args()
    result = {"per_n": {}, "graph_tests": 0, "vertex_tests": 0,
              "min_slack": 10**9, "tight": [], "failures": []}
    for n in range(args.min_n, args.max_n + 1):
        proc = subprocess.run([str(GENG), "-c", "-t", "-f", "-q", str(n)],
                              check=True, capture_output=True, text=True)
        counts = {"generated": 0, "tested": 0, "vertex_tests": 0}
        for g6 in proc.stdout.split():
            counts["generated"] += 1
            records = audit(g6)
            if not records:
                continue
            counts["tested"] += 1
            counts["vertex_tests"] += len(records)
            result["graph_tests"] += 1
            result["vertex_tests"] += len(records)
            for rec in records:
                result["min_slack"] = min(result["min_slack"], rec["slack"])
                if rec["slack"] == 0 and len(result["tight"]) < 30:
                    result["tight"].append(rec)
                if rec["slack"] < 0 and len(result["failures"]) < 30:
                    result["failures"].append(rec)
        result["per_n"][str(n)] = counts
        print(n, counts, flush=True)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
