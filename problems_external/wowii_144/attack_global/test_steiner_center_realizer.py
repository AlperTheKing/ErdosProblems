#!/usr/bin/env python3
"""Test the W144-only Steiner-center split on outer center realizers."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [
    str(HERE),
    str(ROOT / "problems_external" / "wowii_141" / "oracle"),
]
from invariants import all_pairs_dist, dist_to_set
from test_steiner_vertex_fast import GENG, audit_one, parse_graph6


def audit_realizers(graph6: str) -> dict | None:
    result = audit_one(graph6)
    if result is None:
        return None
    n, adjacency = parse_graph6(graph6)
    dist = all_pairs_dist(n, adjacency)
    e_k = [0] * n
    center_distance = [0] * n
    for record in result["records"]:
        v = record["v"]
        e_k[v] = record["steiner_eccentricity"]
        center_distance[v] = record["center_distance"]
    r_k = min(e_k)
    c_k = sum(1 << v for v in range(n) if e_k[v] == r_k)
    outer = max(center_distance)
    realizers = [v for v in range(n) if center_distance[v] == outer]
    data = []
    for v in realizers:
        d_ck = dist_to_set(dist, v, c_k)
        slack_a = e_k[v] - (r_k + d_ck)
        slack_b = d_ck + r_k - (result["g"] - 2) - outer
        data.append({"v": v, "e_k": e_k[v], "R_k": r_k,
                     "d_C": outer, "d_Ck": d_ck,
                     "slack_A": slack_a, "slack_B": slack_b})
    return {"graph6": graph6, "n": n, "g": result["g"],
            "realizers": data,
            "some_A": any(x["slack_A"] >= 0 for x in data),
            "some_A_and_B": any(x["slack_A"] >= 0 and x["slack_B"] >= 0
                                for x in data)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=13)
    parser.add_argument("--workers", type=int, default=32)
    args = parser.parse_args()
    summary = {"graphs": 0, "failures_A": [], "failures_A_and_B": [],
               "per_n": {}}
    for n in range(args.min_n, args.max_n + 1):
        proc = subprocess.run(
            [str(GENG), "-c", "-t", "-f", "-q", str(n)],
            check=True, capture_output=True, text=True,
        )
        graph6s = proc.stdout.split()
        tested = 0
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=args.workers) as executor:
            for rec in executor.map(audit_realizers, graph6s, chunksize=16):
                if rec is None:
                    continue
                tested += 1
                summary["graphs"] += 1
                if not rec["some_A"] and len(summary["failures_A"]) < 20:
                    summary["failures_A"].append(rec)
                if (not rec["some_A_and_B"] and
                        len(summary["failures_A_and_B"]) < 20):
                    summary["failures_A_and_B"].append(rec)
        summary["per_n"][str(n)] = {"generated": len(graph6s),
                                    "tested": tested}
        print(n, summary["per_n"][str(n)], flush=True)
        if summary["failures_A"]:
            break
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
