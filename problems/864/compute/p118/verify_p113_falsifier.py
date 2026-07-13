#!/usr/bin/env python3
"""Independent exact verifier for retained P118 endpoint fold systems.

This file deliberately does not import the search implementation.  It uses
Dinic max flow instead of Hopcroft--Karp and reconstructs folds and loose
triangles directly from unordered sum pairs.
"""

from __future__ import annotations

import argparse
from collections import deque
from hashlib import sha256
import json
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_INPUT = ROOT / "problems/864/compute/p118/p113_falsifier_search.json"
DEFAULT_OUTPUT = ROOT / "problems/864/compute/p118/verification.json"


def digest(values: Sequence[int]) -> str:
    return sha256(",".join(map(str, values)).encode("ascii")).hexdigest()


class Dinic:
    def __init__(self, size: int):
        self.graph: list[list[list[int]]] = [[] for _ in range(size)]

    def add(self, left: int, right: int, capacity: int) -> None:
        forward = [right, capacity, len(self.graph[right])]
        backward = [left, 0, len(self.graph[left])]
        self.graph[left].append(forward)
        self.graph[right].append(backward)

    def flow(self, source: int, sink: int) -> int:
        total = 0
        while True:
            level = [-1] * len(self.graph)
            level[source] = 0
            queue = deque([source])
            while queue:
                vertex = queue.popleft()
                for target, capacity, _reverse in self.graph[vertex]:
                    if capacity and level[target] < 0:
                        level[target] = level[vertex] + 1
                        queue.append(target)
            if level[sink] < 0:
                return total
            cursor = [0] * len(self.graph)

            def send(vertex: int, amount: int) -> int:
                if vertex == sink:
                    return amount
                while cursor[vertex] < len(self.graph[vertex]):
                    edge = self.graph[vertex][cursor[vertex]]
                    target, capacity, reverse = edge
                    if capacity and level[target] == level[vertex] + 1:
                        pushed = send(target, min(amount, capacity))
                        if pushed:
                            edge[1] -= pushed
                            self.graph[target][reverse][1] += pushed
                            return pushed
                    cursor[vertex] += 1
                return 0

            while True:
                pushed = send(source, 1 << 30)
                if not pushed:
                    break
                total += pushed


def max_matching(neighbors: list[list[int]], right_count: int) -> int:
    left_count = len(neighbors)
    source = left_count + right_count
    sink = source + 1
    network = Dinic(sink + 1)
    for left in range(left_count):
        network.add(source, left, 1)
        for right in neighbors[left]:
            network.add(left, left_count + right, 1)
    for right in range(right_count):
        network.add(left_count + right, sink, 1)
    return network.flow(source, sink)


def reconstruct(values: list[int], h: int) -> dict[str, object]:
    if values != sorted(set(values)) or values[0] < 0 or values[-1] != h - 1:
        raise AssertionError("endpoint normalization")
    sums: dict[int, tuple[int, int]] = {}
    differences: dict[int, tuple[int, int]] = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in sums:
                raise AssertionError(("sum collision", total))
            sums[total] = (left, right)
        for right in values[i + 1:]:
            difference = right - left
            if difference in differences:
                raise AssertionError(("difference collision", difference))
            differences[difference] = (left, right)
    folds = []
    for low in sorted(sums):
        if low + h not in sums:
            continue
        a, c = sums[low]
        u, v = sums[low + h]
        if not a <= c < u <= v:
            raise AssertionError(("fold order", a, c, u, v))
        folds.append((a, c, u, v))
    ac = {(fold[0], fold[1]): index for index, fold in enumerate(folds)}
    au = {(fold[0], fold[2]): index for index, fold in enumerate(folds)}
    cu = {(fold[1], fold[2]): index for index, fold in enumerate(folds)}
    triangles = []
    for a, c in ac:
        for aa, u in au:
            if aa != a or (c, u) not in cu:
                continue
            triangle = (ac[a, c], au[a, u], cu[c, u])
            if len(set(triangle)) == 3:
                triangles.append(triangle)
    labels = sorted(differences)
    label_id = {label: index for index, label in enumerate(labels)}
    full = []
    diff_only = []
    support_only = []
    for triangle in triangles:
        phases = [folds[index][0] + folds[index][1] for index in triangle]
        ds = sorted({label_id[abs(phases[i] - phases[j])] for i in range(3) for j in range(i)})
        support = sorted(set(triangle))
        support_only.append(support)
        diff_only.append(ds)
        full.append(support + [len(folds) + label for label in ds])
    return {
        "sha256": digest(values),
        "C_S": len(folds),
        "T_F": len(triangles),
        "matching": max_matching(full, len(folds) + len(labels)),
        "difference_matching": max_matching(diff_only, len(labels)),
        "support_matching": max_matching(support_only, len(folds)),
        "full_neighbors": full,
    }


def verify_row(row: dict[str, object]) -> None:
    values = [int(x) for x in row["B"]]
    fresh = reconstruct(values, int(row["h"]))
    expected = {
        "sha256": row["sha256"],
        "C_S": int(row["C_S"]),
        "T_F": int(row["T_F"]),
        "matching": int(row["matching"]),
        "difference_matching": int(row["difference_matching"]),
        "support_matching": int(row["support_matching"]),
    }
    for key, value in expected.items():
        if fresh[key] != value:
            raise AssertionError((key, fresh[key], value, row["source"]))
    if int(row["hall_deficiency"]) != fresh["T_F"] - fresh["matching"]:
        raise AssertionError("deficiency mismatch")
    witness = row.get("hall_witness")
    if witness:
        left = [int(x) for x in witness["triangle_ids"]]
        neighborhood = {right for triangle in left for right in fresh["full_neighbors"][triangle]}
        if neighborhood != {int(x) for x in witness["resource_ids"]}:
            raise AssertionError("Hall witness neighborhood mismatch")
        if len(left) <= len(neighborhood):
            raise AssertionError("Hall witness is not deficient")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.input = args.input.resolve()
    args.output = args.output.resolve()
    payload = json.loads(args.input.read_text(encoding="ascii"))
    unique: dict[str, dict[str, object]] = {}
    for section_name in ("exhaustive", "costas", "cpsat"):
        for section in payload[section_name]:
            for row in section.get("best", []):
                unique[str(row["sha256"])] = row
    for row in payload["global"]["best"]:
        unique[str(row["sha256"])] = row
    for row in unique.values():
        verify_row(row)
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "matching_algorithm": "independent Dinic max flow",
        "input": str(args.input.relative_to(ROOT)),
        "input_sha256": sha256(args.input.read_bytes()).hexdigest(),
        "retained_rows_checked": len(unique),
        "falsifiers_checked": sum(int(row["hall_deficiency"] > 0) for row in unique.values()),
        "status": "PASS",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
