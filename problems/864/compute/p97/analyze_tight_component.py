#!/usr/bin/env python3
"""Summarize role and phase structure of the archived tight component."""

from __future__ import annotations

import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p93 = load("p93_p97", ROOT / "problems/864/compute/p93/audit_triangle_components.py")


def main() -> None:
    audit = json.loads((ROOT / "problems/864/compute/p97/prefix_audit.json").read_text())
    row = audit["max_component_excess_row"]
    folds, triangles = p93.fold_triangle_system(row["B"], row["h"])
    components = p93.component_rows(folds, triangles)
    component = max(components, key=lambda x: (x["excess"], x["triangles"]))
    fold_ids = set(component["fold_ids"])
    triangle_ids = component["triangle_ids"]
    roles = {"base": Counter(), "au": Counter(), "cu": Counter()}
    phases = Counter()
    color_arcs = Counter()
    difference_arcs = Counter()
    extreme_edges = []
    for tid in triangle_ids:
        base, au, cu = triangles[tid]
        roles["base"][base] += 1
        roles["au"][au] += 1
        roles["cu"][cu] += 1
        a, c, r, _s = folds[base]
        aa, _z, u, _w = folds[au]
        _x, cc, uu, _y = folds[cu]
        assert (aa, cc, uu) == (a, c, u)
        x, y, z = c - a, u - c, u - a
        assert x + y == z
        phases[(r > u, folds[cu][0] > a, folds[au][1] > c)] += 1
        color_arcs[(u, r)] += 1
        difference_arcs[(x, y, z)] += 1
        ds = {fold_id: folds[fold_id][2] - folds[fold_id][1] for fold_id in (base, au, cu)}
        ordered = sorted(ds, key=ds.get)
        extreme_edges.append((ordered[0], ordered[2]))

    parent = {fold_id: fold_id for fold_id in fold_ids}
    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x: int, y: int) -> None:
        x, y = find(x), find(y)
        if x != y:
            parent[y] = x
    for left, right in extreme_edges:
        union(left, right)
    extreme_components = defaultdict(lambda: [0, 0])
    for fold_id in fold_ids:
        extreme_components[find(fold_id)][0] += 1
    for left, _right in extreme_edges:
        extreme_components[find(left)][1] += 1
    role_summary = {}
    for name, counts in roles.items():
        role_summary[name] = {
            "used_folds": len(counts),
            "maximum_multiplicity": max(counts.values(), default=0),
            "multiplicity_histogram": dict(sorted(Counter(counts.values()).items())),
        }
    a_values = {folds[i][0] for i in fold_ids}
    c_values = {folds[i][1] for i in fold_ids}
    u_values = {folds[i][2] for i in fold_ids}
    v_values = {folds[i][3] for i in fold_ids}
    ordered_folds = sorted(fold_ids, key=lambda i: folds[i][2] - folds[i][1])
    positions = {fold_id: pos for pos, fold_id in enumerate(ordered_folds)}
    partition_crossings = {}
    for role, coordinate in (("A", 0), ("C", 1), ("U", 2)):
        blocks = defaultdict(list)
        for fold_id in ordered_folds:
            blocks[folds[fold_id][coordinate]].append(positions[fold_id])
        crossing_count = 0
        values = list(blocks)
        for i, left_value in enumerate(values):
            left = blocks[left_value]
            for right_value in values[i + 1:]:
                right = blocks[right_value]
                merged = sorted((x, 0) for x in left) + sorted((x, 1) for x in right)
                labels = [label for _pos, label in sorted(merged)]
                compressed = [label for j, label in enumerate(labels) if j == 0 or label != labels[j - 1]]
                if len(compressed) >= 4:
                    crossing_count += 1
        partition_crossings[role] = crossing_count
    print(json.dumps({
        "folds": len(fold_ids),
        "triangles": len(triangle_ids),
        "role_summary": role_summary,
        "sign_chambers_R_X_Z": {str(k): v for k, v in sorted(phases.items())},
        "distinct_color_arcs": len(color_arcs),
        "maximum_color_arc_multiplicity": max(color_arcs.values(), default=0),
        "distinct_difference_triples": len(difference_arcs),
        "maximum_difference_triple_multiplicity": max(difference_arcs.values(), default=0),
        "extreme_graph_maximum_excess": max((e - v for v, e in extreme_components.values()), default=0),
        "extreme_graph_component_histogram": {
            str(key): value
            for key, value in sorted(Counter((v, e) for v, e in extreme_components.values()).items())
        },
        "coordinate_class_counts": {
            "A": len(a_values), "C": len(c_values),
            "U": len(u_values), "V": len(v_values),
            "ACU_total": len(a_values) + len(c_values) + len(u_values),
        },
        "shadow_cycle_rank": 3 * len(fold_ids) - (len(a_values) + len(c_values) + len(u_values)) + 1,
        "partition_crossing_block_pairs": partition_crossings,
    }, indent=2))


if __name__ == "__main__":
    main()
