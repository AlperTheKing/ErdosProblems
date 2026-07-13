#!/usr/bin/env python3
"""Audit whether pure overfull component cores can satisfy either literal hole."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

from component_core import canonical_folds, component_data, positive_differences, unordered_sum_map


ROOT = Path(__file__).resolve().parents[4]
P86 = ROOT / "problems/864/compute/p86/dense_loose_search.py"
P88_B = (
    0,122,163,328,351,488,499,528,553,681,837,838,920,941,1051,1070,
    1117,1322,1340,1414,1449,1520,1608,1613,1617,1715,1853,1866,1925,
    2057,2074,2153,2173,2240,2320,2380,2475,2521,2564,2596,2598,2654,
    2788,2815,2839,2901,2950,2958,3026,3070,3076,3131,3170,3184,3200,
    3212,3215,3222,3248,3285,
)


def load_p86():
    spec = importlib.util.spec_from_file_location("p86_for_p98_cores", P86)
    if spec is None or spec.loader is None:
        raise RuntimeError(P86)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def overfull_cores(values, h):
    folds = canonical_folds(values, h)
    _triangles, components = component_data(folds, values)
    return [
        tuple(sorted({mark for fold_id in component.fold_ids for mark in folds[fold_id]}))
        for component in components if component.excess > 0
    ]


def hole_free(core, b):
    sums = unordered_sum_map(core)
    differences = positive_differences(core)
    return differences.isdisjoint(total + b for total in sums)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    baseline = (3 * len(P88_B) ** 2 - len(P88_B) + 2) // 2
    p88_rows = p88_components = p88_hole_free_1 = p88_hole_free_2 = 0
    last_gamma = None
    for gamma in range(baseline - 3286):
        values = tuple(value + gamma for value in P88_B)
        cores = overfull_cores(values, 3286 + gamma)
        if not cores:
            continue
        p88_rows += 1
        p88_components += len(cores)
        last_gamma = gamma
        p88_hole_free_1 += sum(hole_free(core, 1) for core in cores)
        p88_hole_free_2 += sum(hole_free(core, 2) for core in cores)

    p86 = load_p86()
    bases, _manifest = p86.load_archives()
    archive_bases = archive_components = archive_hole_free_1 = archive_hole_free_2 = 0
    for base in bases:
        values = base.values
        p = len(values)
        h = values[-1] + 1
        if (3 * p * p - p + 2) // 2 <= h:
            continue
        cores = overfull_cores(values, h)
        if not cores:
            continue
        archive_bases += 1
        archive_components += len(cores)
        archive_hole_free_1 += sum(hole_free(core, 1) for core in cores)
        archive_hole_free_2 += sum(hole_free(core, 2) for core in cores)

    result = {
        "arithmetic": "exact Python integers",
        "p88_positive_defect_translations": baseline - 3286,
        "p88_overfull_rows": p88_rows,
        "p88_overfull_components": p88_components,
        "p88_last_overfull_gamma": last_gamma,
        "p88_core_hole_free_b1": p88_hole_free_1,
        "p88_core_hole_free_b2": p88_hole_free_2,
        "archive_oriented_bases": len(bases),
        "archive_positive_defect_endpoint_bases_with_overfull_component": archive_bases,
        "archive_overfull_components": archive_components,
        "archive_core_hole_free_b1": archive_hole_free_1,
        "archive_core_hole_free_b2": archive_hole_free_2,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
