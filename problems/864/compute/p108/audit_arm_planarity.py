#!/usr/bin/env python3
"""Exact construction and combinatorial planarity audit of arm graphs."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p108 = load("sweep_planar_p108", ROOT / "problems/864/compute/p108/audit_sweep_saturation.py")
p106 = p108.p106


def planarity_score(values: tuple[int, ...], h: int, b: int) -> dict[str, object]:
    folds, triangles, _intervals, _slots, _differences = p106.residual_system(values, h, b)
    vertices: dict[int, set[int]] = defaultdict(set)
    directed: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for fold_id, (_a, _c, u, _v) in enumerate(folds):
        vertices[u].add(fold_id)
    for _base, arm_au, arm_cu in triangles:
        u = folds[arm_au][2]
        if folds[arm_cu][2] != u:
            raise AssertionError("arm colors disagree")
        directed[u].append((arm_au, arm_cu))
    rows = []
    failures = 0
    for u, arcs in directed.items():
        graph = nx.Graph()
        graph.add_nodes_from(vertices[u])
        graph.add_edges_from(arcs)
        planar, certificate = nx.check_planarity(graph, counterexample=True)
        if not planar:
            failures += 1
        pair_counts = Counter(tuple(sorted(edge)) for edge in arcs)
        rows.append({
            "u": u,
            "vertices": graph.number_of_nodes(),
            "directed_arcs": len(arcs),
            "simple_edges": graph.number_of_edges(),
            "digons": sum(value == 2 for value in pair_counts.values()),
            "planar": planar,
            "kuratowski_nodes": [] if planar else sorted(certificate.nodes()),
            "kuratowski_edges": [] if planar else sorted(
                [sorted(edge) for edge in certificate.edges()]
            ),
        })
    base = p108.score(values, h, b)
    return {
        key: base[key]
        for key in ("p", "h", "b", "delta", "C_S", "T_F", "V_b", "literal_hole")
    } | {
        "active_colors": len(rows),
        "nonplanar_colors": failures,
        "maximum_directed_minus_6n": max(
            (row["directed_arcs"] - 6 * row["vertices"] for row in rows),
            default=0,
        ),
        "worst_color": max(
            rows,
            key=lambda row: (row["directed_arcs"] - 3 * row["vertices"], row["directed_arcs"]),
            default=None,
        ),
        "nonplanar_rows": [row for row in rows if not row["planar"]],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "schema_version": 1,
        "arithmetic": "exact graph construction; NetworkX Boyer-Myrvold planarity",
        "rows": {
            name: planarity_score(*row)
            for name, row in p108.mandatory_rows().items()
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
