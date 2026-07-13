#!/usr/bin/env python3
"""Independent exact verification of retained P116 rows and witnesses."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, deque
from pathlib import Path
from typing import Sequence


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_sidon(values: Sequence[int]):
    sums = {}
    positive_differences = {}
    for index, left in enumerate(values):
        for right in values[index:]:
            total = left + right
            if total in sums:
                raise AssertionError(("sum collision", total, sums[total], (left, right)))
            sums[total] = (left, right)
        for right in values[index + 1:]:
            difference = right - left
            if difference in positive_differences:
                raise AssertionError(
                    ("difference collision", difference, positive_differences[difference], (left, right))
                )
            positive_differences[difference] = (left, right)
    return sums, positive_differences


def maximum_flow(demand: dict[int, int], neighbors: dict[int, set[int]]) -> int:
    colors = sorted(demand)
    resources = sorted(set().union(*(neighbors.values() or [set()])))
    source = 0
    color_offset = 1
    resource_offset = color_offset + len(colors)
    sink = resource_offset + len(resources)
    graph: list[dict[int, int]] = [dict() for _ in range(sink + 1)]

    def edge(left: int, right: int, capacity: int) -> None:
        graph[left][right] = graph[left].get(right, 0) + capacity
        graph[right].setdefault(left, 0)

    color_id = {color: color_offset + index for index, color in enumerate(colors)}
    resource_id = {
        resource: resource_offset + index for index, resource in enumerate(resources)
    }
    for color in colors:
        edge(source, color_id[color], demand[color])
        for resource in sorted(neighbors[color]):
            edge(color_id[color], resource_id[resource], 1)
    for resource in resources:
        edge(resource_id[resource], sink, 1)

    total = 0
    while True:
        parent = [-1] * len(graph)
        parent[source] = source
        queue = deque([source])
        while queue and parent[sink] < 0:
            left = queue.popleft()
            for right, capacity in graph[left].items():
                if capacity > 0 and parent[right] < 0:
                    parent[right] = left
                    queue.append(right)
        if parent[sink] < 0:
            return total
        amount = 10**9
        right = sink
        while right != source:
            left = parent[right]
            amount = min(amount, graph[left][right])
            right = left
        right = sink
        while right != source:
            left = parent[right]
            graph[left][right] -= amount
            graph[right][left] = graph[right].get(left, 0) + amount
            right = left
        total += amount


def audit(values_input: Sequence[int], h: int, b: int) -> dict[str, int | bool]:
    values = tuple(sorted(int(value) for value in values_input))
    if len(values) != len(set(values)) or values[-1] != h - 1:
        raise AssertionError(("endpoint", values[-1], h))
    sums, differences = verify_sidon(values)
    literal_hole = all(total + b not in differences for total in sums)

    folds = []
    for total in sorted(sums):
        if total + h not in sums:
            continue
        a, c = sums[total]
        u, v = sums[total + h]
        if not a <= c < u <= v:
            raise AssertionError(("fold order", a, c, u, v))
        folds.append((a, c, u, v))

    fold_by_ac = {(row[0], row[1]): index for index, row in enumerate(folds)}
    fold_by_au = {(row[0], row[2]): index for index, row in enumerate(folds)}
    fold_by_cu = {(row[1], row[2]): index for index, row in enumerate(folds)}
    fold_count = Counter(row[2] for row in folds)
    triangle_count: Counter[int] = Counter()
    neighbors: dict[int, set[int]] = {}
    triangle_total = 0
    for a, c in sorted(fold_by_ac):
        for u in values:
            base = fold_by_ac.get((a, c))
            left = fold_by_au.get((a, u))
            right = fold_by_cu.get((c, u))
            if base is None or left is None or right is None:
                continue
            if base == left == right:
                continue
            if len({base, left, right}) != 3:
                raise AssertionError(("partial triangle", base, left, right))
            if folds[left][2] != folds[right][2]:
                raise AssertionError("arm colors")
            difference = abs(folds[left][3] - folds[right][3])
            if difference == 0 or difference not in differences:
                raise AssertionError(("arm difference", difference))
            triangle_total += 1
            triangle_count[u] += 1
            neighbors.setdefault(u, set()).add(difference)

    demand = {
        color: triangle_count[color] - fold_count[color]
        for color in triangle_count
        if triangle_count[color] > fold_count[color]
    }
    excess = sum(demand.values())
    matching = maximum_flow(demand, neighbors)
    p = len(values)
    return {
        "p": p,
        "h": h,
        "b": b,
        "delta": (3 * p * p - p + 2) // 2 - h,
        "literal_hole": literal_hole,
        "C_S": len(folds),
        "T_F": triangle_total,
        "positive_color_excess": excess,
        "BC108_margin": excess - p,
        "difference_hall_matching": matching,
        "difference_hall_deficit": excess - matching,
    }


def compare(row: dict[str, object]) -> dict[str, int | bool]:
    fresh = audit(row["B"], int(row["h"]), int(row["b"]))
    for key in (
        "p", "h", "b", "delta", "C_S", "T_F", "positive_color_excess",
        "BC108_margin", "difference_hall_matching", "difference_hall_deficit",
    ):
        if key in row and fresh[key] != row[key]:
            raise AssertionError((key, fresh[key], row[key]))
    if not fresh["literal_hole"] or int(fresh["delta"]) <= 0:
        raise AssertionError(("not live", fresh))
    if "sha256" in row:
        digest = hashlib.sha256(
            ",".join(map(str, row["B"])).encode("ascii")
        ).hexdigest()
        if digest != row["sha256"]:
            raise AssertionError((digest, row["sha256"]))
    return fresh


def retained_rows(payload: dict[str, object]):
    lanes = payload.get("lanes", {})
    if isinstance(lanes, dict):
        for lane in lanes.values():
            if not isinstance(lane, dict):
                continue
            for key in (
                "best_row", "first_BC108_failure", "first_difference_hall_failure"
            ):
                row = lane.get(key)
                if isinstance(row, dict):
                    yield f"lane/{key}", row
    for key in ("BC108_falsifier", "difference_Hall_falsifier", "smallest_witness"):
        row = payload.get(key)
        if isinstance(row, dict):
            yield key, row
    results = payload.get("results", [])
    if isinstance(results, list):
        for index, result in enumerate(results):
            if not isinstance(result, dict):
                continue
            for key in ("witness", "minimum_p_witness"):
                row = result.get(key)
                if isinstance(row, dict):
                    yield f"results/{index}/{key}", row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = []
    for path in args.inputs:
        payload = json.loads(path.read_text(encoding="ascii"))
        checked = 0
        row_digest = hashlib.sha256()
        seen = set()
        for label, row in retained_rows(payload):
            identity = (tuple(row["B"]), int(row["h"]), int(row["b"]))
            if identity in seen:
                continue
            seen.add(identity)
            fresh = compare(row)
            row_digest.update(
                json.dumps([label, row["B"], fresh], sort_keys=True).encode("ascii")
            )
            row_digest.update(b"\n")
            checked += 1
        records.append({
            "input": str(path),
            "input_sha256": sha256_file(path),
            "distinct_retained_rows_checked": checked,
            "verified_rows_sha256": row_digest.hexdigest(),
        })
    result = {
        "schema_version": 1,
        "arithmetic": "independent exact Python integers and Edmonds-Karp max flow",
        "status": "PASS",
        "inputs": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
