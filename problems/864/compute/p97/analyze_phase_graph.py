#!/usr/bin/env python3
"""Compare loose triangles with cliques in the fold phase graph."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p75 = load("p75_phase_graph", ROOT / "problems/864/compute/p75/verify_hard_fold_counterexample.py")
p88 = load("p88_phase_graph", ROOT / "problems/864/compute/p88/verify_c84_order_counterexample.py")
p93 = load("p93_phase_graph", ROOT / "problems/864/compute/p93/audit_triangle_components.py")


def score(values, h, b):
    folds, triangles = p93.fold_triangle_system(values, h)
    differences = {right - left for left in values for right in values if left < right}
    labels = [a + c + b for a, c, _u, _v in folds]
    adjacency = [set() for _ in folds]
    for i in range(len(folds)):
        for j in range(i + 1, len(folds)):
            if abs(labels[i] - labels[j]) in differences:
                adjacency[i].add(j); adjacency[j].add(i)
    cliques = []
    for i in range(len(folds)):
        for j in adjacency[i]:
            if i < j:
                for k in adjacency[i] & adjacency[j]:
                    if j < k:
                        cliques.append((i, j, k))
    loose_sets = {tuple(sorted(t)) for t in triangles}
    clique_sets = set(cliques)
    folds_by_color = {}
    triangles_by_color = {}
    for i, fold in enumerate(folds):
        folds_by_color[fold[2]] = folds_by_color.get(fold[2], 0) + 1
    for _base, au, cu in triangles:
        color = folds[au][2]
        assert folds[cu][2] == color
        triangles_by_color[color] = triangles_by_color.get(color, 0) + 1
    color_rows = sorted(
        ((triangles_by_color.get(u, 0) - count, u, count, triangles_by_color.get(u, 0))
         for u, count in folds_by_color.items()), reverse=True,
    )
    return {
        "folds": len(folds), "loose_triangles": len(triangles),
        "phase_graph_edges": sum(map(len, adjacency)) // 2,
        "phase_graph_cliques": len(cliques),
        "loose_not_clique": len(loose_sets - clique_sets),
        "clique_not_loose": len(clique_sets - loose_sets),
        "maximum_color_excess": color_rows[0] if color_rows else None,
        "colors_with_excess": sum(row[0] > 0 for row in color_rows),
    }


def main():
    audit = json.loads((ROOT / "problems/864/compute/p97/prefix_audit.json").read_text())
    tight = audit["max_component_excess_row"]
    print(json.dumps({
        "P75": score(p75.B, p75.h, p75.b),
        "P88_b1": score(p88.B, p88.H, 1),
        "tight": score(tuple(tight["B"]), tight["h"], tight["b"]),
    }, indent=2))


if __name__ == "__main__":
    main()
