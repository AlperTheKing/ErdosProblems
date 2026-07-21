#!/usr/bin/env python3
"""Exact audit of srad_{g-1}(G) >= g-2+ecc(G,C(G))."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from test_steiner_vertex_fast import GENG, audit_one


def radius_record(graph6: str) -> dict | None:
    result = audit_one(graph6)
    if result is None:
        return None
    radius = min(r["steiner_eccentricity"] for r in result["records"])
    outer = max(r["center_distance"] for r in result["records"])
    need = result["g"] - 2 + outer
    return {"graph6": graph6, "n": result["n"], "g": result["g"],
            "steiner_radius": radius, "center_eccentricity": outer,
            "need": need, "slack": radius - need}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=13)
    parser.add_argument("--workers", type=int, default=32)
    args = parser.parse_args()
    answer = {"graphs": 0, "min_slack": 10**9, "failures": [],
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
            for rec in executor.map(radius_record, graph6s, chunksize=16):
                if rec is None:
                    continue
                tested += 1
                answer["graphs"] += 1
                answer["min_slack"] = min(answer["min_slack"], rec["slack"])
                if rec["slack"] < 0 and len(answer["failures"]) < 20:
                    answer["failures"].append(rec)
        answer["per_n"][str(n)] = {"generated": len(graph6s),
                                   "tested": tested}
        print(n, answer["per_n"][str(n)], flush=True)
        if answer["failures"]:
            break
    print(json.dumps(answer, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
