#!/usr/bin/env python3
"""Exact audit of matching loose triangles to folds or difference labels."""

from __future__ import annotations

import argparse
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


p46 = load("p46_p113", ROOT / "problems/864/compute/p46/carry_statistics.py")
p103 = load("p103_p113", ROOT / "problems/864/compute/p103/audit_relation_matroid.py")


def maximum_matching(neighbors: list[list[int]]) -> int:
    owner: dict[int, int] = {}

    def augment(left: int, seen: set[int]) -> bool:
        for right in neighbors[left]:
            if right in seen:
                continue
            seen.add(right)
            if right not in owner or augment(owner[right], seen):
                owner[right] = left
                return True
        return False

    return sum(augment(left, set()) for left in range(len(neighbors)))


def audit_row(B: tuple[int, ...], h: int) -> dict[str, int]:
    folds, triangles = p103.fold_system(B, h)
    differences = sorted({right - left for left in B for right in B if left < right})
    difference_id = {difference: index for index, difference in enumerate(differences)}
    C = len(folds)
    neighbors = []
    difference_neighbors = []
    for f0, fz, fx in triangles:
        q = [folds[index][0] + folds[index][1] for index in (f0, fz, fx)]
        labels = {
            difference_id[abs(q[0] - q[1])],
            difference_id[abs(q[0] - q[2])],
            difference_id[abs(q[1] - q[2])],
        }
        difference_neighbors.append(sorted(labels))
        neighbors.append(sorted({f0, fz, fx} | {C + label for label in labels}))
    return {
        "C_S": C,
        "T_F": len(triangles),
        "difference_resources": len(differences),
        "difference_matching": maximum_matching(difference_neighbors),
        "matching": maximum_matching(neighbors),
    }


def empty_summary() -> dict[str, object]:
    return {
        "rows": 0,
        "triangle_rows": 0,
        "difference_only_failures": 0,
        "failures": 0,
        "first_difference_only_failure": None,
        "first_failure": None,
    }


def consume(summary: dict[str, object], B: tuple[int, ...], h: int, witness: dict[str, object]) -> None:
    summary["rows"] += 1
    row = audit_row(B, h)
    if not row["T_F"]:
        return
    summary["triangle_rows"] += 1
    if row["difference_matching"] < row["T_F"]:
        summary["difference_only_failures"] += 1
        if summary["first_difference_only_failure"] is None:
            summary["first_difference_only_failure"] = {**witness, **row, "B": B, "h": h}
    if row["matching"] < row["T_F"]:
        summary["failures"] += 1
        if summary["first_failure"] is None:
            summary["first_failure"] = {**witness, **row, "B": B, "h": h}


def scan_width(max_width: int) -> dict[str, object]:
    summary = empty_summary()
    for width in range(1, max_width + 1):
        for ruler in p46.sidon_rulers(width):
            reflected = tuple(sorted(width - x for x in ruler))
            for gamma in range(width):
                B = tuple(gamma + x for x in reflected)
                h = gamma + width + 1
                consume(summary, B, h, {"width": width, "gamma": gamma})
    return summary


def scan_p88() -> dict[str, object]:
    summary = empty_summary()
    for gamma in range(2085):
        B = tuple(x + gamma for x in p103.P88)
        consume(summary, B, 3286 + gamma, {"source": "P88", "gamma": gamma})
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "candidate": "match every loose triangle to a supporting fold or one of its three represented difference lengths",
        "consequence": "T_F <= C_S + binom(p,2) = O(p^2)",
        "width_scan": scan_width(args.max_width),
        "P88_scan": scan_p88(),
    }
    rendered = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="ascii")
    print(rendered)


if __name__ == "__main__":
    main()
