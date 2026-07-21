#!/usr/bin/env python3
"""Fast exact superset-DP audit of the vertex-specific Steiner bound."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [
    str(ROOT / "problems_external" / "wowii_141" / "oracle"),
    str(ROOT / "problems_external" / "wowii_144" / "oracle_exhaustive"),
]
from invariants import all_pairs_dist, dist_to_set, eccentricities, girth
from run_sweep import parse_graph6

GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


def is_connected(mask: int, adjacency: list[int]) -> bool:
    if not mask:
        return False
    seen = mask & -mask
    frontier = seen
    while frontier:
        neighbors = 0
        work = frontier
        while work:
            bit = work & -work
            neighbors |= adjacency[bit.bit_length() - 1]
            work ^= bit
        frontier = neighbors & mask & ~seen
        seen |= frontier
    return seen == mask


def audit_one(graph6: str) -> dict | None:
    n, adjacency = parse_graph6(graph6)
    g = girth(n, adjacency)
    if g < 5:
        return None
    k = g - 1
    limit = 1 << n
    best_superset = [n + 1] * limit
    for mask in range(1, limit):
        if is_connected(mask, adjacency):
            best_superset[mask] = mask.bit_count()
    for bit_index in range(n):
        bit = 1 << bit_index
        for mask in range(limit):
            if not mask & bit:
                value = best_superset[mask | bit]
                if value < best_superset[mask]:
                    best_superset[mask] = value

    steiner_ecc = [0] * n
    witnesses = [0] * n
    for mask in range(limit):
        if mask.bit_count() != k:
            continue
        value = best_superset[mask] - 1
        work = mask
        while work:
            bit = work & -work
            v = bit.bit_length() - 1
            if value > steiner_ecc[v]:
                steiner_ecc[v] = value
                witnesses[v] = mask
            work ^= bit

    distances = all_pairs_dist(n, adjacency)
    eccentricity = eccentricities(n, distances)
    radius = min(eccentricity)
    center = sum(1 << v for v in range(n) if eccentricity[v] == radius)
    records = []
    for v in range(n):
        center_distance = dist_to_set(distances, v, center)
        need = k - 1 + center_distance
        records.append({
            "graph6": graph6, "n": n, "g": g, "v": v,
            "center_distance": center_distance,
            "steiner_eccentricity": steiner_ecc[v], "need": need,
            "slack": steiner_ecc[v] - need,
            "witness": [u for u in range(n) if witnesses[v] >> u & 1],
        })
    return {"graph6": graph6, "n": n, "g": g, "records": records}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=12)
    parser.add_argument("--max-n", type=int, default=12)
    parser.add_argument("--workers", type=int, default=32)
    args = parser.parse_args()
    summary = {"per_n": {}, "graphs": 0, "vertices": 0,
               "min_slack": 10**9, "failures": [], "tight": []}
    for n in range(args.min_n, args.max_n + 1):
        proc = subprocess.run(
            [str(GENG), "-c", "-t", "-f", "-q", str(n)],
            check=True, capture_output=True, text=True,
        )
        graph6s = proc.stdout.split()
        tested = vertices = 0
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=args.workers) as executor:
            results = executor.map(audit_one, graph6s, chunksize=16)
            for result in results:
                if result is None:
                    continue
                tested += 1
                summary["graphs"] += 1
                for record in result["records"]:
                    vertices += 1
                    summary["vertices"] += 1
                    summary["min_slack"] = min(
                        summary["min_slack"], record["slack"])
                    if record["slack"] < 0 and len(summary["failures"]) < 20:
                        summary["failures"].append(record)
                    if record["slack"] == 0 and len(summary["tight"]) < 20:
                        summary["tight"].append(record)
        summary["per_n"][str(n)] = {
            "generated": len(graph6s), "tested": tested,
            "vertex_tests": vertices,
        }
        print(n, summary["per_n"][str(n)], flush=True)
        if summary["failures"]:
            break
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
