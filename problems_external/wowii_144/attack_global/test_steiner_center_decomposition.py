#!/usr/bin/env python3
"""Exact audit of two Steiner-center inequalities whose sum implies W144-VE."""
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
from invariants import all_pairs_dist, dist_to_set, eccentricities, girth
from run_sweep import parse_graph6

GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


def connected(mask: int, adj: list[int]) -> bool:
    seen = mask & -mask
    frontier = seen
    while frontier:
        bit = frontier & -frontier
        frontier ^= bit
        u = bit.bit_length() - 1
        new = adj[u] & mask & ~seen
        seen |= new
        frontier |= new
    return seen == mask


def steiner_distances(n: int, adj: list[int], k: int) -> list[int]:
    """Return d_G(S) for every mask, using a superset minimum transform."""
    inf = n + 1
    best = [inf] * (1 << n)
    for mask in range(1, 1 << n):
        if connected(mask, adj):
            best[mask] = mask.bit_count()
    for bit in range(n):
        step = 1 << bit
        for mask in range(1 << n):
            if not mask & step and best[mask | step] < best[mask]:
                best[mask] = best[mask | step]
    return [x - 1 if x <= n else inf for x in best]


def audit(g6: str) -> dict | None:
    n, adj = parse_graph6(g6)
    g = girth(n, adj)
    if g < 5:
        return None
    k = g - 1
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    radius = min(ecc)
    center = sum(1 << v for v in range(n) if ecc[v] == radius)
    sd = steiner_distances(n, adj, k)
    e_k = [max(sd[sum(1 << x for x in S)]
               for S in itertools.combinations(range(n), k) if v in S)
           for v in range(n)]
    r_k = min(e_k)
    c_k = sum(1 << v for v in range(n) if e_k[v] == r_k)
    failures_a = []
    failures_b = []
    failures_ve = []
    for v in range(n):
        d_ck = dist_to_set(dist, v, c_k)
        d_c = dist_to_set(dist, v, center)
        slack_a = e_k[v] - (r_k + d_ck)
        slack_b = d_ck + r_k - (k - 1) - d_c
        slack_ve = e_k[v] - (k - 1 + d_c)
        base = {"v": v, "d_C": d_c, "d_Ck": d_ck,
                "e_k": e_k[v], "R_k": r_k}
        if slack_a < 0:
            failures_a.append(base | {"slack": slack_a})
        if slack_b < 0:
            failures_b.append(base | {"slack": slack_b})
        if slack_ve < 0:
            failures_ve.append(base | {"slack": slack_ve})
    return {"graph6": g6, "n": n, "g": g,
            "failures_A": failures_a, "failures_B": failures_b,
            "failures_VE": failures_ve}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=11)
    args = parser.parse_args()
    result = {"graphs": 0, "vertices": 0, "failures_A": [],
              "failures_B": [], "failures_VE": [], "per_n": {}}
    for n in range(args.min_n, args.max_n + 1):
        proc = subprocess.run(
            [str(GENG), "-c", "-t", "-f", "-q", str(n)],
            check=True, capture_output=True, text=True,
        )
        generated = tested = 0
        for g6 in proc.stdout.split():
            generated += 1
            rec = audit(g6)
            if rec is None:
                continue
            tested += 1
            result["graphs"] += 1
            result["vertices"] += rec["n"]
            for key in ["failures_A", "failures_B", "failures_VE"]:
                if rec[key] and len(result[key]) < 30:
                    result[key].append({
                        "graph6": g6, "n": rec["n"], "g": rec["g"],
                        "instances": rec[key],
                    })
        result["per_n"][str(n)] = {"generated": generated, "tested": tested}
        print(n, result["per_n"][str(n)], flush=True)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
