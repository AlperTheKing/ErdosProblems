#!/usr/bin/env python3
"""Test a sufficient two-endpoint terminal construction for the VE lemma."""
from __future__ import annotations

import itertools
import subprocess
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [
    str(ROOT / "problems_external" / "wowii_141" / "oracle"),
    str(ROOT / "problems_external" / "wowii_144" / "oracle_exhaustive"),
]
from invariants import all_pairs_dist, dist_to_set, eccentricities, girth
from run_sweep import parse_graph6

GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


def zero_one_distance(adjacency: list[int], start: int, target: int,
                      zero_vertices: int) -> int:
    n = len(adjacency)
    distance = [n + 1] * n
    distance[start] = 0
    queue = deque([start])
    while queue:
        u = queue.popleft()
        work = adjacency[u]
        while work:
            bit = work & -work
            w = bit.bit_length() - 1
            cost = 0 if zero_vertices & bit else 1
            value = distance[u] + cost
            if value < distance[w]:
                distance[w] = value
                if cost:
                    queue.append(w)
                else:
                    queue.appendleft(w)
            work ^= bit
    return distance[target]


def witness_for(adjacency: list[int], g: int, v: int, target_value: int):
    vertices = range(len(adjacency))
    for w in vertices:
        if w == v:
            continue
        available = [u for u in vertices if u not in (v, w)]
        for choice in itertools.combinations(available, g - 3):
            mask = sum(1 << u for u in choice)
            if zero_one_distance(adjacency, v, w, mask) >= target_value:
                return w, choice
    return None


def main() -> None:
    graphs = vertices = 0
    for n in range(5, 12):
        proc = subprocess.run(
            [str(GENG), "-c", "-t", "-f", "-q", str(n)],
            check=True, capture_output=True, text=True,
        )
        for graph6 in proc.stdout.split():
            order, adjacency = parse_graph6(graph6)
            g = girth(order, adjacency)
            if g < 5:
                continue
            graphs += 1
            distances = all_pairs_dist(order, adjacency)
            eccentricity = eccentricities(order, distances)
            radius = min(eccentricity)
            center = sum(1 << u for u in range(order)
                         if eccentricity[u] == radius)
            for v in range(order):
                vertices += 1
                t = dist_to_set(distances, v, center)
                witness = witness_for(adjacency, g, v, t + 1)
                if witness is None:
                    print({"failure": graph6, "n": order, "g": g,
                           "v": v, "center_distance": t,
                           "graphs": graphs, "vertices": vertices})
                    return
    print({"graphs": graphs, "vertices": vertices, "failures": 0})


if __name__ == "__main__":
    main()
