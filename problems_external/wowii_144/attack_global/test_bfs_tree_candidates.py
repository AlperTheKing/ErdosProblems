#!/usr/bin/env python3
"""Exact falsification tests for the center-rooted BFS-tree route to W144."""
from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
from collections import deque
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


def center_data(n: int, adj: list[int]) -> tuple[list[list[int]], int]:
    dist = all_pairs_dist(n, adj)
    ecc = eccentricities(n, dist)
    radius = min(ecc)
    center = sum(1 << v for v in range(n) if ecc[v] == radius)
    return dist, center


def edge_side_masks(n: int, adj: list[int]) -> list[int]:
    """One component mask of T-e for every edge of a tree T."""
    ans = []
    for u in range(n):
        for v in range(u + 1, n):
            if not (adj[u] >> v & 1):
                continue
            seen = 1 << u
            queue = deque([u])
            while queue:
                x = queue.popleft()
                nbrs = adj[x] & ~seen & ~(1 << v)
                while nbrs:
                    bit = nbrs & -nbrs
                    nbrs -= bit
                    y = bit.bit_length() - 1
                    seen |= bit
                    queue.append(y)
            ans.append(seen)
    assert len(ans) == n - 1
    return ans


def audit_tree(g6: str) -> list[dict]:
    n, adj = parse_graph6(g6)
    dist, center = center_data(n, adj)
    sides = edge_side_masks(n, adj)
    full = (1 << n) - 1
    failures = []
    for k in range(2, n + 1):
        best = [0] * n
        for vertices in itertools.combinations(range(n), k):
            mask = sum(1 << x for x in vertices)
            size = sum(bool(mask & side) and bool(mask & (full ^ side))
                       for side in sides)
            for v in vertices:
                best[v] = max(best[v], size)
        for v in range(n):
            q = dist_to_set(dist, v, center)
            need = k - 1 + min(q, n - k)
            if best[v] < need:
                failures.append({
                    "graph6": g6, "n": n, "k": k, "v": v,
                    "q": q, "e_k": best[v], "need": need,
                })
    return failures


def run_trees(max_n: int) -> dict:
    result = {"tree_tests": 0, "vertex_k_tests": 0, "failures": []}
    for n in range(2, max_n + 1):
        proc = subprocess.run(
            [str(GENG), "-c", "-q", str(n), f"{n - 1}:{n - 1}"],
            check=True, capture_output=True, text=True,
        )
        count = 0
        for g6 in proc.stdout.split():
            count += 1
            result["tree_tests"] += 1
            result["vertex_k_tests"] += n * (n - 1)
            failures = audit_tree(g6)
            result["failures"].extend(failures[:30-len(result["failures"])])
        print("trees", n, count, flush=True)
        if result["failures"]:
            break
    return result


def run_order_bound(max_n: int) -> dict:
    result = {"graph_tests": 0, "vertex_tests": 0, "min_slack": 10**9,
              "failures": []}
    for n in range(5, max_n + 1):
        proc = subprocess.run(
            [str(GENG), "-c", "-t", "-f", "-q", str(n)],
            check=True, capture_output=True, text=True,
        )
        tested = 0
        for g6 in proc.stdout.split():
            order, adj = parse_graph6(g6)
            g = girth(order, adj)
            if g < 5:
                continue
            tested += 1
            result["graph_tests"] += 1
            dist, center = center_data(order, adj)
            for v in range(order):
                q = dist_to_set(dist, v, center)
                slack = order - g - q
                result["vertex_tests"] += 1
                result["min_slack"] = min(result["min_slack"], slack)
                if slack < 0 and len(result["failures"]) < 30:
                    result["failures"].append({
                        "graph6": g6, "n": order, "g": g, "v": v,
                        "q": q, "n_minus_g": order - g,
                    })
        print("order", n, tested, flush=True)
        if result["failures"]:
            break
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["trees", "order", "both"])
    parser.add_argument("--max-n", type=int, default=11)
    args = parser.parse_args()
    answer = {}
    if args.mode in {"trees", "both"}:
        answer["trees"] = run_trees(args.max_n)
    if args.mode in {"order", "both"}:
        answer["order"] = run_order_bound(args.max_n)
    print(json.dumps(answer, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
