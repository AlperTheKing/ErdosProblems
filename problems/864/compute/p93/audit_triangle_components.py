#!/usr/bin/env python3
"""Exact component audit for the P93 strengthening of C84."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "problems/864/compute/p86"))
import dense_loose_search as p86


def fold_triangle_system(
    values: Sequence[int], h: int,
) -> tuple[list[tuple[int, int, int, int]], list[tuple[int, int, int]]]:
    folds, _ = p86.fold_edges(values, h)
    ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
    triangles = []
    for a, c in ac:
        for u in values:
            ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
            if None in ids or ids[0] == ids[1] == ids[2]:
                continue
            if len(set(ids)) != 3:
                raise AssertionError(("linearity", ids))
            triangles.append(ids)
    return folds, triangles


def component_rows(
    folds: Sequence[tuple[int, int, int, int]],
    triangles: Sequence[tuple[int, int, int]],
) -> list[dict[str, object]]:
    incident: list[set[int]] = [set() for _ in folds]
    for triangle_id, triangle in enumerate(triangles):
        for fold_id in triangle:
            incident[fold_id].add(triangle_id)

    rows = []
    seen: set[int] = set()
    for start in range(len(folds)):
        if start in seen:
            continue
        vertices = {start}
        edges: set[int] = set()
        stack = [start]
        seen.add(start)
        while stack:
            fold_id = stack.pop()
            for triangle_id in incident[fold_id]:
                edges.add(triangle_id)
                for neighbor in triangles[triangle_id]:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        vertices.add(neighbor)
                        stack.append(neighbor)

        active_vertices = set(vertices)
        active_edges = set(edges)
        while True:
            degree = {fold_id: 0 for fold_id in active_vertices}
            for triangle_id in active_edges:
                for fold_id in triangles[triangle_id]:
                    degree[fold_id] += 1
            low = {fold_id for fold_id, value in degree.items() if value <= 1}
            if not low:
                break
            active_vertices -= low
            active_edges = {
                triangle_id
                for triangle_id in active_edges
                if not low.intersection(triangles[triangle_id])
            }

        rows.append(
            {
                "fold_ids": sorted(vertices),
                "triangle_ids": sorted(edges),
                "folds": len(vertices),
                "triangles": len(edges),
                "excess": len(edges) - len(vertices),
                "two_core_folds": len(active_vertices),
                "two_core_triangles": len(active_edges),
                "two_core_excess": len(active_edges) - len(active_vertices),
            }
        )
    return rows


def score(values: Sequence[int], h: int, b: int) -> dict[str, object]:
    folds, triangles = fold_triangle_system(values, h)
    components = component_rows(folds, triangles)
    worst = max(components, key=lambda row: (row["excess"], row["triangles"]))
    core = max(
        components,
        key=lambda row: (row["two_core_excess"], row["two_core_triangles"]),
    )
    fold_count_by_u: dict[int, int] = {}
    triangle_count_by_u: dict[int, int] = {}
    for _a, _c, u, _v in folds:
        fold_count_by_u[u] = fold_count_by_u.get(u, 0) + 1
    for _middle, arm_au, arm_cu in triangles:
        u = folds[arm_au][2]
        if folds[arm_cu][2] != u:
            raise AssertionError(("shared color", arm_au, arm_cu))
        triangle_count_by_u[u] = triangle_count_by_u.get(u, 0) + 1
    prefix = 0
    max_prefix = None
    max_prefix_u = None
    for u in sorted(fold_count_by_u.keys() | triangle_count_by_u.keys()):
        prefix += triangle_count_by_u.get(u, 0) - fold_count_by_u.get(u, 0)
        if max_prefix is None or prefix > max_prefix:
            max_prefix = prefix
            max_prefix_u = u
    return {
        "B": list(values),
        "p": len(values),
        "h": h,
        "b": b,
        "delta": (3 * len(values) ** 2 - len(values) + 2) // 2 - h,
        "C_S": len(folds),
        "T_F": len(triangles),
        "component_count": len(components),
        "max_component": worst,
        "max_two_core": core,
        "max_color_prefix_excess": max_prefix,
        "max_color_prefix_u": max_prefix_u,
    }


def translation_worker(values: Sequence[int]) -> dict[str, object]:
    z = tuple(values)
    p, width = len(z), z[-1]
    baseline = (3 * p * p - p + 2) // 2
    max_gamma = min(width - 1, baseline - width - 2)
    if max_gamma < 0:
        return {
            "holes": 0, "failures": 0, "prefix_failures": 0,
            "best": None, "core": None, "prefix": None,
        }
    sum_mask, difference_mask = p86.masks_for_ruler(z)
    holes = failures = prefix_failures = 0
    best = core = prefix_best = None
    for gamma in range(max_gamma + 1):
        h = width + gamma + 1
        if (sum_mask & (sum_mask >> h)).bit_count() == 0:
            continue
        for b in (1, 2):
            if ((sum_mask << (2 * gamma + b)) & difference_mask) != 0:
                continue
            holes += 1
            row = score(tuple(x + gamma for x in z), h, b)
            excess = int(row["max_component"]["excess"])
            if excess > 0:
                failures += 1
            prefix_excess = int(row["max_color_prefix_excess"])
            if prefix_excess > 0:
                prefix_failures += 1
            key = (excess, int(row["max_component"]["triangles"]))
            if best is None or key > best[0]:
                best = (key, row)
            core_key = (
                int(row["max_two_core"]["two_core_excess"]),
                int(row["max_two_core"]["two_core_triangles"]),
            )
            if core is None or core_key > core[0]:
                core = (core_key, row)
            prefix_key = (prefix_excess, int(row["T_F"]))
            if prefix_best is None or prefix_key > prefix_best[0]:
                prefix_best = (prefix_key, row)
    return {
        "holes": holes,
        "failures": failures,
        "prefix_failures": prefix_failures,
        "best": best[1] if best else None,
        "core": core[1] if core else None,
        "prefix": prefix_best[1] if prefix_best else None,
    }


def best(rows: Sequence[dict[str, object]], field: str, component: str) -> object:
    candidates = [row[field] for row in rows if row[field] is not None]
    return max(
        candidates,
        key=lambda row: (
            int(row[component][
                "excess" if component == "max_component" else "two_core_excess"
            ]),
            int(row[component][
                "triangles" if component == "max_component" else "two_core_triangles"
            ]),
        ),
        default=None,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "problems/864/compute/p93/triangle_components.json",
    )
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        raise ValueError("workers must be in [1,64]")
    bases, _ = p86.load_archives()
    payloads = [base.values for base in bases]
    if args.workers == 1:
        rows = [translation_worker(values) for values in payloads]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows = list(pool.map(translation_worker, payloads, chunksize=1))
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "bases": len(bases),
        "literal_holes": sum(int(row["holes"]) for row in rows),
        "component_failures": sum(int(row["failures"]) for row in rows),
        "color_prefix_failures": sum(
            int(row["prefix_failures"]) for row in rows
        ),
        "max_component_excess_row": best(rows, "best", "max_component"),
        "max_two_core_excess_row": best(rows, "core", "max_two_core"),
        "max_color_prefix_excess_row": max(
            (row["prefix"] for row in rows if row["prefix"] is not None),
            key=lambda row: (row["max_color_prefix_excess"], row["T_F"]),
            default=None,
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
