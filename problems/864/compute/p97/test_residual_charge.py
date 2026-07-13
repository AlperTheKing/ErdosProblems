#!/usr/bin/env python3
"""Test component excess against occupied fold residual endpoints."""

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


p88 = load("p88_residual", ROOT / "problems/864/compute/p88/verify_c84_order_counterexample.py")
p93 = load("p93_residual", ROOT / "problems/864/compute/p93/audit_triangle_components.py")


def score(values, h, b):
    value_set = set(values)
    differences = {right - left for left in values for right in values if left < right}
    folds, triangles = p93.fold_triangle_system(values, h)
    rows = p93.component_rows(folds, triangles)
    out = []
    for row in rows:
        residual_incidences = []
        residual_labels = set()
        bad_folds = set()
        represented_fold_labels = set()
        represented_fold_label_folds = 0
        for fold_id in row["fold_ids"]:
            a, c, u, v = folds[fold_id]
            label = a + c + b
            if label in differences:
                represented_fold_labels.add(label)
                represented_fold_label_folds += 1
            for residual in (h - b - v, h - b - u):
                if residual in value_set:
                    residual_incidences.append((fold_id, residual))
                    residual_labels.add(residual)
                    bad_folds.add(fold_id)
        out.append({
            "folds": row["folds"], "triangles": row["triangles"],
            "excess": row["excess"],
            "occupied_residual_incidences": len(residual_incidences),
            "occupied_residual_labels": len(residual_labels),
            "bad_folds": len(bad_folds),
            "represented_fold_label_folds": represented_fold_label_folds,
            "represented_fold_labels": len(represented_fold_labels),
        })
    return sorted(out, key=lambda x: (x["excess"], x["triangles"]), reverse=True)


def main():
    print(json.dumps({
        "P88_b1": score(p88.B, p88.H, 1)[:5],
        "P88_b2": score(p88.B, p88.H, 2)[:5],
    }, indent=2))


if __name__ == "__main__":
    main()
