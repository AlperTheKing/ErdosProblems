#!/usr/bin/env python3
"""Exact audit of sdiam_{g-1}(G) >= g-2+ecc(G,center(G))."""
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
]

from invariants import all_pairs_dist, ecc_of_set, eccentricities, girth
from run_sweep import parse_graph6

GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


def connected_masks(n: int, adj: list[int]) -> list[int]:
    out: list[int] = []
    for mask in range(1, 1 << n):
        seen = mask & -mask
        frontier = seen
        while frontier:
            bit = frontier & -frontier
            frontier ^= bit
            u = bit.bit_length() - 1
            new = adj[u] & mask & ~seen
            seen |= new
            frontier |= new
        if seen == mask:
            out.append(mask)
    return out


def steiner_diameter(n: int, adj: list[int], k: int) -> tuple[int, int]:
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
    witness = max(best, key=best.get)
    return best[witness] - 1, witness


def audit(g6: str) -> dict | None:
    n, adj = parse_graph6(g6)
    g = girth(n, adj)
    if g < 4:
        return None
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    r = min(ecc)
    center = sum(1 << v for v in range(n) if ecc[v] == r)
    e = ecc_of_set(n, dist, center)
    sd, witness = steiner_diameter(n, adj, g - 1)
    return {
        "graph6": g6,
        "n": n,
        "g": g,
        "r": r,
        "D": max(ecc),
        "e": e,
        "sdiam": sd,
        "need": g - 2 + e,
        "slack": sd - (g - 2 + e),
        "witness": [v for v in range(n) if witness >> v & 1],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=4)
    parser.add_argument("--max-n", type=int, default=11)
    parser.add_argument("--allow-squares", action="store_true")
    args = parser.parse_args()
    flags = ["-c", "-t"] + ([] if args.allow_squares else ["-f"])
    result = {"flags": flags, "per_n": {}, "tests": 0,
              "min_slack": 10**9, "tight": [], "failures": []}
    for n in range(args.min_n, args.max_n + 1):
        proc = subprocess.run([str(GENG), *flags, "-q", str(n)],
                              check=True, capture_output=True, text=True)
        counts = {"generated": 0, "tested": 0}
        for g6 in proc.stdout.split():
            counts["generated"] += 1
            rec = audit(g6)
            if rec is None:
                continue
            counts["tested"] += 1
            result["tests"] += 1
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
