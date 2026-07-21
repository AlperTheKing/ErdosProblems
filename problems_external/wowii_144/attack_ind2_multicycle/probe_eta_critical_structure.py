#!/usr/bin/env python3
"""Finite probe for direct structural criteria behind W144-IND2."""

from __future__ import annotations

import argparse
from collections import Counter

import networkx as nx

from analyze_tight_deletions import center_depth, cycle_rank, girth, records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=10)
    args = parser.parse_args()
    totals = Counter()
    first_fail = {}
    for n in range(5, args.max_n + 1):
        for code, graph in records(n):
            g = girth(graph)
            if g is None or g < 5 or cycle_rank(graph) < 2:
                continue
            totals["graphs"] += 1
            eta, center = center_depth(graph)
            distance = nx.multi_source_dijkstra_path_length(graph, center)
            realizers = {v for v, value in distance.items() if value == eta}
            articulation = set(nx.articulation_points(graph))
            preserving = []
            good = []
            for v in graph:
                if v in articulation:
                    continue
                h = graph.copy()
                h.remove_node(v)
                if cycle_rank(h) < 1 or girth(h) != g:
                    continue
                etah, _ = center_depth(h)
                preserving.append((v, etah - eta))
                if etah >= eta:
                    good.append(v)
            assert good
            candidates = {
                "outside_center_realizers": [
                    v
                    for v, _ in preserving
                    if v not in center and v not in realizers
                ],
                "noncenter": [v for v, _ in preserving if v not in center],
                "nonrealizer": [v for v, _ in preserving if v not in realizers],
                "leaf": [v for v, _ in preserving if graph.degree[v] == 1],
                "core": [
                    v for v, _ in preserving if v in nx.k_core(graph, 2)
                ],
            }
            for label, vertices in candidates.items():
                if not vertices:
                    continue
                totals[label + "_applicable"] += 1
                if any(v in good for v in vertices):
                    totals[label + "_works"] += 1
                elif label not in first_fail:
                    first_fail[label] = {
                        "graph6": code.decode(),
                        "n": n,
                        "g": g,
                        "eta": eta,
                        "center": sorted(center),
                        "realizers": sorted(realizers),
                        "candidates": vertices,
                        "preserving": preserving,
                        "good": good,
                        "degrees": dict(graph.degree()),
                    }
    print("TOTALS", dict(sorted(totals.items())))
    print("FIRST_FAIL", first_fail)


if __name__ == "__main__":
    main()
