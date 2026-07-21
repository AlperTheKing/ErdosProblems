#!/usr/bin/env python3
"""Exact audit of a direct two-terminal construction for W144-SR.

For a root ``v`` and a second terminal ``w``, choose the remaining ``g-3``
terminals as zero-cost vertices.  If every v--w path has at least ``e``
internal vertices outside this terminal set, then every connector uses at
least ``e`` nonterminals.  This is precisely a sufficient cut-family
witness, not an asymptotic surrogate.
"""
from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [
    str(ROOT / "problems_external" / "wowii_141" / "oracle"),
    str(ROOT / "problems_external" / "wowii_144" / "oracle_exhaustive"),
]
from invariants import all_pairs_dist, eccentricities, girth
from run_sweep import parse_graph6

GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


def zero_one_distance(adjacency: list[int], start: int, target: int,
                      zero_vertices: int) -> int:
    """Minimum number of nonterminal vertices on a start--target path.

    The target itself is counted, so ``distance >= e+1`` means at least
    ``e`` internal nonterminals.
    """
    n = len(adjacency)
    distance = [n + 1] * n
    distance[start] = 0
    queue = deque([start])
    while queue:
        u = queue.popleft()
        work = adjacency[u]
        while work:
            bit = work & -work
            work ^= bit
            w = bit.bit_length() - 1
            cost = 0 if zero_vertices & bit else 1
            value = distance[u] + cost
            if value < distance[w]:
                distance[w] = value
                if cost:
                    queue.append(w)
                else:
                    queue.appendleft(w)
    return distance[target]


def witness_for(adjacency: list[int], g: int, v: int, e: int):
    vertices = range(len(adjacency))
    for w in vertices:
        if w == v:
            continue
        available = [u for u in vertices if u not in (v, w)]
        for choice in itertools.combinations(available, g - 3):
            zero = sum(1 << u for u in choice)
            if zero_one_distance(adjacency, v, w, zero) >= e + 1:
                return {"w": w, "other_terminals": choice}
    return None


def audit_one(graph6: str) -> dict | None:
    n, adjacency = parse_graph6(graph6)
    g = girth(n, adjacency)
    if g < 5:
        return None
    distances = all_pairs_dist(n, adjacency)
    eccentricity = eccentricities(n, distances)
    radius = min(eccentricity)
    center = [u for u in range(n) if eccentricity[u] == radius]
    e = max(min(distances[x][c] for c in center) for x in range(n))
    for v in range(n):
        witness = witness_for(adjacency, g, v, e)
        if witness is None:
            edges = [[u, w] for u in range(n) for w in range(u + 1, n)
                     if adjacency[u] >> w & 1]
            return {"graph6": graph6, "n": n, "g": g, "radius": radius,
                    "center": center, "e": e, "v": v, "edges": edges}
    return {"graph6": graph6, "n": n, "g": g, "e": e}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=12)
    args = parser.parse_args()
    out = {"graphs": 0, "roots": 0, "failures": [], "per_n": {}}
    for n in range(args.min_n, args.max_n + 1):
        proc = subprocess.run(
            [str(GENG), "-c", "-t", "-f", "-q", str(n)],
            check=True, capture_output=True, text=True,
        )
        tested = 0
        for graph6 in proc.stdout.split():
            rec = audit_one(graph6)
            if rec is None:
                continue
            tested += 1
            out["graphs"] += 1
            out["roots"] += rec["n"]
            if "v" in rec:
                out["failures"].append(rec)
                break
        out["per_n"][str(n)] = tested
        print(n, tested, flush=True)
        if out["failures"]:
            break
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
