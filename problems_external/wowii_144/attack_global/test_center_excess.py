#!/usr/bin/env python3
"""Falsifier-first audit of d(v,Center(G)) <= |V(G)|-girth(G)."""
from __future__ import annotations

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


def main() -> None:
    graph_tests = vertex_tests = 0
    worst = None
    failures = []
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
            graph_tests += 1
            distances = all_pairs_dist(order, adjacency)
            eccentricity = eccentricities(order, distances)
            radius = min(eccentricity)
            center = sum(1 << v for v in range(order) if eccentricity[v] == radius)
            for v in range(order):
                vertex_tests += 1
                value = dist_to_set(distances, v, center)
                slack = order - g - value
                record = (slack, graph6, order, g, v, value)
                if worst is None or record < worst:
                    worst = record
                if slack < 0:
                    failures.append(record)
                    print("FAIL", record)
                    return
    print({"graphs": graph_tests, "vertices": vertex_tests,
           "failures": len(failures), "minimum": worst})


if __name__ == "__main__":
    main()
