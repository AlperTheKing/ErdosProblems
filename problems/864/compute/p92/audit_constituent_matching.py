#!/usr/bin/env python3
"""Test the constituent-fold SDR proposed for the P84 triangle bound."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[4]
P46_PATH = ROOT / "problems/864/compute/p46/carry_statistics.py"
P86_DATA = ROOT / "problems/864/compute/p86/dense_loose_scan.json"

Fold = tuple[int, int, int, int]
Triangle = tuple[int, int, int]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def canonical_folds(values: tuple[int, ...], h: int) -> list[Fold]:
    sums: dict[int, tuple[int, int]] = {}
    for i, x in enumerate(values):
        for y in values[i:]:
            total = x + y
            assert total not in sums
            sums[total] = (x, y)
    return [
        (a, c, *sums[low + h])
        for low, (a, c) in sorted(sums.items())
        if low + h in sums
    ]


def loose_triangle_ids(folds: list[Fold]) -> list[Triangle]:
    ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
    assert len(ac) == len(au) == len(cu) == len(folds)

    ac_by_a: dict[int, list[tuple[int, int]]] = {}
    au_by_a: dict[int, list[tuple[int, int]]] = {}
    for (a, c), fold_id in ac.items():
        ac_by_a.setdefault(a, []).append((c, fold_id))
    for (a, u), fold_id in au.items():
        au_by_a.setdefault(a, []).append((u, fold_id))

    result: list[Triangle] = []
    for a in sorted(set(ac_by_a) & set(au_by_a)):
        for c, i0 in ac_by_a[a]:
            for u, iz in au_by_a[a]:
                ix = cu.get((c, u))
                if ix is None:
                    continue
                ids = (i0, iz, ix)
                if len(set(ids)) == 3:
                    result.append(ids)
    return result


def maximum_constituent_matching(
    adjacency: list[tuple[int, ...]], fold_count: int
) -> tuple[int, list[int]]:
    """Return a maximum matching from triangles to candidate folds."""
    fold_to_triangle = [-1] * fold_count

    def augment(triangle_id: int, seen: list[bool]) -> bool:
        for fold_id in adjacency[triangle_id]:
            if seen[fold_id]:
                continue
            seen[fold_id] = True
            previous = fold_to_triangle[fold_id]
            if previous < 0 or augment(previous, seen):
                fold_to_triangle[fold_id] = triangle_id
                return True
        return False

    size = 0
    for triangle_id in range(len(adjacency)):
        size += augment(triangle_id, [False] * fold_count)
    return size, fold_to_triangle


def hall_witness(
    adjacency: list[tuple[int, ...]], fold_to_triangle: list[int]
) -> tuple[list[int], list[int]]:
    """Recover a deficient Hall set after an unsuccessful maximum matching."""
    triangle_to_fold = {
        triangle_id: fold_id
        for fold_id, triangle_id in enumerate(fold_to_triangle)
        if triangle_id >= 0
    }
    left = {i for i in range(len(adjacency)) if i not in triangle_to_fold}
    right: set[int] = set()
    queue = list(left)
    while queue:
        triangle_id = queue.pop()
        matched_fold = triangle_to_fold.get(triangle_id)
        for fold_id in adjacency[triangle_id]:
            if fold_id == matched_fold or fold_id in right:
                continue
            right.add(fold_id)
            next_triangle = fold_to_triangle[fold_id]
            if next_triangle >= 0 and next_triangle not in left:
                left.add(next_triangle)
                queue.append(next_triangle)
    return sorted(left), sorted(right)


def hexagon_adjacency(
    folds: list[Fold], triangles: list[Triangle]
) -> list[tuple[int, ...]]:
    """Candidate targets one signed hexagon step from any phase label."""
    low_labels = [a + c for a, c, _u, _v in folds]
    result = []
    for i0, iz, ix in triangles:
        a, c, r, _s = folds[i0]
        _a, z, u, _w = folds[iz]
        x, _c, _u, _y = folds[ix]
        X, Z, R = x - a, z - c, r - u
        increments = {X, Z, R, R + X, R + Z, Z - X}
        increments |= {-value for value in increments}
        increments.add(0)
        bases = {low_labels[i0], low_labels[iz], low_labels[ix]}
        targets = {
            fold_id
            for fold_id, label in enumerate(low_labels)
            if any(label - base in increments for base in bases)
        }
        assert {i0, iz, ix} <= targets
        result.append(tuple(sorted(targets)))
    return result


def audit_row(values: Iterable[int], h: int) -> dict[str, object]:
    values = tuple(sorted(values))
    folds = canonical_folds(values, h)
    triangles = loose_triangle_ids(folds)
    constituent_adjacency = [tuple(ids) for ids in triangles]
    constituent_matching, constituent_assignment = maximum_constituent_matching(
        constituent_adjacency, len(folds)
    )
    hex_adjacency = hexagon_adjacency(folds, triangles)
    hex_matching, hex_assignment = maximum_constituent_matching(
        hex_adjacency, len(folds)
    )
    result: dict[str, object] = {
        "p": len(values),
        "h": h,
        "C_S": len(folds),
        "T_F": len(triangles),
        "constituent_matching": constituent_matching,
        "hexagon_matching": hex_matching,
    }
    if constituent_matching != len(triangles):
        left, right = hall_witness(
            constituent_adjacency, constituent_assignment
        )
        assert len(right) < len(left)
        result.update(
            {
                "B": values,
                "constituent_hall_triangles": left,
                "constituent_hall_folds": right,
                "fold_list": folds,
                "triangle_ids": triangles,
            }
        )
    if hex_matching != len(triangles):
        left, right = hall_witness(hex_adjacency, hex_assignment)
        assert len(right) < len(left)
        result.update(
            {
                "B": values,
                "hexagon_hall_triangles": left,
                "hexagon_hall_folds": right,
                "fold_list": folds,
                "triangle_ids": triangles,
                "hexagon_adjacency": hex_adjacency,
            }
        )
    return result


def archived_rows() -> list[tuple[tuple[int, ...], int]]:
    data = json.loads(P86_DATA.read_text(encoding="ascii"))
    rows: set[tuple[tuple[int, ...], int]] = set()

    def visit(value: object) -> None:
        if isinstance(value, dict):
            if "B" in value and "h" in value:
                B = value["B"]
                h = value["h"]
                if isinstance(B, list) and isinstance(h, int):
                    rows.add((tuple(B), h))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(data)
    return sorted(rows, key=lambda row: (len(row[0]), row[1], row[0]))


def exhaustive_width(max_width: int) -> dict[str, object]:
    p46 = load_module("p46_p92", P46_PATH)
    rulers = candidates = holes = triangle_rows = 0
    c84_failures = 0
    constituent_failures = 0
    hexagon_failures = 0
    first_c84_failure = None
    first_constituent_failure = None
    first_hexagon_failure = None
    max_triangles = 0
    for width in range(1, max_width + 1):
        for ruler in p46.sidon_rulers(width):
            rulers += 1
            p = len(ruler)
            baseline = (3 * p * p - p + 2) // 2
            max_gamma = baseline - width - 2
            if max_gamma < 0:
                continue
            forbidden = p46.forbidden_three_minus_one(ruler)
            reflected = tuple(sorted(width - x for x in ruler))
            for b in (1, 2):
                for gamma in range(max_gamma + 1):
                    candidates += 1
                    if 2 * width + 2 * gamma + b in forbidden:
                        continue
                    holes += 1
                    B = tuple(gamma + x for x in reflected)
                    row = audit_row(B, gamma + width + 1)
                    triangle_count = int(row["T_F"])
                    if triangle_count:
                        triangle_rows += 1
                        max_triangles = max(max_triangles, triangle_count)
                    if triangle_count > int(row["C_S"]):
                        c84_failures += 1
                        row["b"] = b
                        if first_c84_failure is None:
                            first_c84_failure = row
                    if row["constituent_matching"] != triangle_count:
                        constituent_failures += 1
                        row["b"] = b
                        if first_constituent_failure is None:
                            first_constituent_failure = row
                    if row["hexagon_matching"] != triangle_count:
                        hexagon_failures += 1
                        row["b"] = b
                        if first_hexagon_failure is None:
                            first_hexagon_failure = row
    return {
        "max_width": max_width,
        "sidon_rulers": rulers,
        "positive_defect_candidates": candidates,
        "admissible_holes": holes,
        "nonzero_triangle_rows": triangle_rows,
        "max_T_F": max_triangles,
        "T_F_gt_C_S_failures": c84_failures,
        "first_T_F_gt_C_S_failure": first_c84_failure,
        "constituent_matching_failures": constituent_failures,
        "first_constituent_matching_failure": first_constituent_failure,
        "hexagon_matching_failures": hexagon_failures,
        "first_hexagon_matching_failure": first_hexagon_failure,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    archive = archived_rows()
    archive_c84_failures = []
    archive_constituent_failures = []
    archive_hexagon_failures = []
    archive_triangle_rows = 0
    archive_max = 0
    for B, h in archive:
        row = audit_row(B, h)
        triangle_count = int(row["T_F"])
        archive_triangle_rows += triangle_count > 0
        archive_max = max(archive_max, triangle_count)
        if triangle_count > int(row["C_S"]):
            archive_c84_failures.append(row)
        if row["constituent_matching"] != triangle_count:
            archive_constituent_failures.append(row)
        if row["hexagon_matching"] != triangle_count:
            archive_hexagon_failures.append(row)

    result = {
        "claims": [
            "constituent-fold SDR",
            "global one-step signed-hexagon fold-label SDR",
            "T_F <= C_S",
        ],
        "exhaustive": exhaustive_width(args.max_width),
        "archive": {
            "records": len(archive),
            "nonzero_triangle_rows": archive_triangle_rows,
            "max_T_F": archive_max,
            "T_F_gt_C_S_failures": len(archive_c84_failures),
            "first_T_F_gt_C_S_failure": (
                archive_c84_failures[0] if archive_c84_failures else None
            ),
            "constituent_matching_failures": len(archive_constituent_failures),
            "first_constituent_matching_failure": (
                archive_constituent_failures[0]
                if archive_constituent_failures
                else None
            ),
            "hexagon_matching_failures": len(archive_hexagon_failures),
            "first_hexagon_matching_failure": (
                archive_hexagon_failures[0]
                if archive_hexagon_failures
                else None
            ),
        },
    }
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
