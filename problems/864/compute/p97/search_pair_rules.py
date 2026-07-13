#!/usr/bin/env python3
"""Search order-equivariant triangle-to-pair rules on exact archived rows."""

from __future__ import annotations

import importlib.util
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p93 = load("p93_rules", ROOT / "problems/864/compute/p93/audit_triangle_components.py")


def triangle_types(folds, triangles, key):
    out = []
    for triangle in triangles:
        ds = [key(folds[i]) for i in triangle]
        if len(set(ds)) != 3:
            raise AssertionError((triangle, ds))
        order = tuple(sorted(range(3), key=ds.__getitem__))
        out.append((triangle, order))
    return out


def maximum_excess(vertex_count, typed, rule, type_ids):
    parent = list(range(vertex_count))
    counts = [[1, 0] for _ in range(vertex_count)]

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        x, y = find(x), find(y)
        if x != y:
            parent[y] = x

    selected = []
    pairs = ((0, 1), (1, 2), (0, 2))
    for triangle, order in typed:
        left_rank, right_rank = pairs[rule[type_ids[order]]]
        edge = (triangle[order[left_rank]], triangle[order[right_rank]])
        selected.append(edge)
        union(*edge)
    component = {}
    for vertex in range(vertex_count):
        component.setdefault(find(vertex), [0, 0])[0] += 1
    for left, _right in selected:
        component[find(left)][1] += 1
    return max((edges - vertices for vertices, edges in component.values()), default=0)


def main() -> None:
    audit = json.loads((ROOT / "problems/864/compute/p97/prefix_audit.json").read_text())
    rows = [audit["max_component_excess_row"], audit["max_color_prefix_excess_row"]]
    systems = {"inner_length": [], "phase_label": []}
    orders = list(itertools.permutations(range(3)))
    type_ids = {order: i for i, order in enumerate(orders)}
    for row in rows:
        folds, triangles = p93.fold_triangle_system(row["B"], row["h"])
        systems["inner_length"].append((folds, triangle_types(folds, triangles, lambda f: f[2] - f[1])))
        systems["phase_label"].append((folds, triangle_types(folds, triangles, lambda f: f[0] + f[1])))
    survivor_sets = {}
    for name, system_rows in systems.items():
        survivors = []
        for rule in itertools.product(range(3), repeat=6):
            excesses = [maximum_excess(len(folds), typed, rule, type_ids) for folds, typed in system_rows]
            if max(excesses, default=0) <= 0:
                survivors.append({"rule": rule, "excesses": excesses})
        survivor_sets[name] = survivors
    print(json.dumps({
        "pair_choices": {"0": "min-median", "1": "median-max", "2": "min-max"},
        "order_types": orders,
        "tested_rules": 3**6,
        "survivors": survivor_sets,
    }, indent=2))


if __name__ == "__main__":
    main()
