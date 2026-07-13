#!/usr/bin/env python3
"""Exact adversarial search for BC108 and the arm-difference Hall gate.

The search lanes are deterministic.  Every acceptance decision uses Python
integers.  SHA-256 streams cover the complete candidate domains and all live
rows, including rows not retained in the compact JSON report.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


ROOT = Path(__file__).resolve().parents[4]
P46_PATH = ROOT / "problems/864/compute/p46/carry_statistics.py"
P86_PATH = ROOT / "problems/864/compute/p86/dense_loose_search.py"
P88_PATH = ROOT / "problems/864/compute/p88/verify_c84_order_counterexample.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def update_digest(digest: "hashlib._Hash", payload: object) -> None:
    digest.update(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("ascii"))
    digest.update(b"\n")


def unordered_sum_map(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    sums: dict[int, tuple[int, int]] = {}
    for index, left in enumerate(values):
        for right in values[index:]:
            total = left + right
            if total in sums:
                raise ValueError(("repeated sum", total, sums[total], (left, right)))
            sums[total] = (left, right)
    return sums


def positive_differences(values: Sequence[int]) -> set[int]:
    differences: set[int] = set()
    for index, right in enumerate(values):
        for left in values[:index]:
            difference = right - left
            if difference in differences:
                raise ValueError(("repeated difference", difference))
            differences.add(difference)
    return differences


def normalized(values: Iterable[int]) -> tuple[int, ...]:
    row = tuple(sorted(set(int(value) for value in values)))
    if not row:
        return ()
    return tuple(value - row[0] for value in row)


@dataclass(frozen=True)
class System:
    folds: tuple[tuple[int, int, int, int], ...]
    triangles: tuple[tuple[int, int, int], ...]
    demand: tuple[tuple[int, int], ...]
    neighbors: tuple[tuple[int, tuple[int, ...]], ...]
    positive_color_excess: int
    exposed_differences: int
    hall_matching: int


def maximum_capacitated_matching(
    demand: dict[int, int], neighbors: dict[int, set[int]]
) -> int:
    resource_owner: dict[int, tuple[int, int]] = {}

    def augment(copy: tuple[int, int], seen: set[int]) -> bool:
        color, _copy_index = copy
        for resource in sorted(neighbors[color]):
            if resource in seen:
                continue
            seen.add(resource)
            previous = resource_owner.get(resource)
            if previous is None or augment(previous, seen):
                resource_owner[resource] = copy
                return True
        return False

    for color in sorted(demand, key=lambda value: (len(neighbors[value]), value)):
        for copy_index in range(demand[color]):
            augment((color, copy_index), set())
    return len(resource_owner)


def fold_triangle_system(values: Sequence[int], h: int) -> System:
    sums = unordered_sum_map(values)
    folds = []
    for low in sorted(sums):
        high = low + h
        if high not in sums:
            continue
        a, c = sums[low]
        u, v = sums[high]
        if not a <= c < u <= v:
            raise AssertionError(("fold order", a, c, u, v, h))
        folds.append((a, c, u, v))

    ac = {(a, c): index for index, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): index for index, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): index for index, (_a, c, u, _v) in enumerate(folds)}
    if len(ac) != len(folds) or len(au) != len(folds) or len(cu) != len(folds):
        raise AssertionError("nonlinear fold shadows")

    triangles = []
    fold_count = Counter(u for _a, _c, u, _v in folds)
    triangle_count: Counter[int] = Counter()
    neighbors: dict[int, set[int]] = defaultdict(set)
    differences = positive_differences(values)
    for a, c in ac:
        for u in values:
            ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
            if None in ids or ids[0] == ids[1] == ids[2]:
                continue
            if len(set(ids)) != 3:
                raise AssertionError(("partial triangle", ids))
            base, arm_au, arm_cu = (int(value) for value in ids)
            triangles.append((base, arm_au, arm_cu))
            left, right = folds[arm_au], folds[arm_cu]
            if left[2] != right[2]:
                raise AssertionError("arm colors disagree")
            difference = abs(left[3] - right[3])
            if difference == 0 or difference not in differences:
                raise AssertionError(("arm difference", difference))
            triangle_count[u] += 1
            neighbors[u].add(difference)

    demand = {
        color: triangle_count[color] - fold_count[color]
        for color in triangle_count
        if triangle_count[color] > fold_count[color]
    }
    required = sum(demand.values())
    matching = maximum_capacitated_matching(demand, neighbors)
    exposed = len(set().union(*(neighbors.values() or [set()])))
    return System(
        tuple(folds), tuple(triangles), tuple(sorted(demand.items())),
        tuple((color, tuple(sorted(rows))) for color, rows in sorted(neighbors.items())),
        required, exposed, matching,
    )


def is_literal_hole(
    sums: Iterable[int], differences: set[int], gamma: int, b: int
) -> bool:
    return differences.isdisjoint(total + 2 * gamma + b for total in sums)


def row_record(
    base: Sequence[int], gamma: int, h: int, b: int, system: System,
    source: str, transform: str,
) -> dict[str, object]:
    values = tuple(value + gamma for value in base)
    p = len(values)
    delta = (3 * p * p - p + 2) // 2 - h
    return {
        "source": source,
        "transform": transform,
        "B": list(values),
        "p": p,
        "h": h,
        "b": b,
        "delta": delta,
        "width": values[-1] - values[0],
        "C_S": len(system.folds),
        "T_F": len(system.triangles),
        "positive_color_excess": system.positive_color_excess,
        "BC108_margin": system.positive_color_excess - p,
        "exposed_differences": system.exposed_differences,
        "difference_hall_matching": system.hall_matching,
        "difference_hall_deficit": system.positive_color_excess - system.hall_matching,
        "demand": {str(color + gamma): count for color, count in system.demand},
    }


def row_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        int(row["BC108_margin"]), int(row["difference_hall_deficit"]),
        int(row["positive_color_excess"]), int(row["T_F"]),
        -int(row["p"]), -int(row["h"]), tuple(row["B"]), int(row["b"]),
    )


class Lane:
    def __init__(self, definition: str):
        self.definition = definition
        self.counts: Counter[str] = Counter()
        self.domain_digest = hashlib.sha256()
        self.live_digest = hashlib.sha256()
        self.best: dict[str, object] | None = None
        self.first_bc_failure: dict[str, object] | None = None
        self.first_hall_failure: dict[str, object] | None = None

    def candidate(self, payload: object) -> None:
        self.counts["candidates"] += 1
        update_digest(self.domain_digest, payload)

    def live(self, row: dict[str, object]) -> None:
        self.counts["live_rows"] += 1
        self.counts["triangle_rows"] += int(row["T_F"] > 0)
        self.counts["positive_excess_rows"] += int(row["positive_color_excess"] > 0)
        compact = [
            row["source"], row["transform"], row["p"], row["h"], row["b"],
            row["delta"], row["C_S"], row["T_F"], row["positive_color_excess"],
            row["difference_hall_matching"], row["B"],
        ]
        update_digest(self.live_digest, compact)
        if self.best is None or row_key(row) > row_key(self.best):
            self.best = row
        if int(row["BC108_margin"]) > 0:
            self.counts["BC108_failures"] += 1
            self.first_bc_failure = self.first_bc_failure or row
        if int(row["difference_hall_deficit"]) > 0:
            self.counts["difference_hall_failures"] += 1
            self.first_hall_failure = self.first_hall_failure or row

    def result(self) -> dict[str, object]:
        return {
            "definition": self.definition,
            **dict(sorted(self.counts.items())),
            "domain_sha256": self.domain_digest.hexdigest(),
            "live_rows_sha256": self.live_digest.hexdigest(),
            "best_row": self.best,
            "first_BC108_failure": self.first_bc_failure,
            "first_difference_hall_failure": self.first_hall_failure,
        }


def scan_complete_widths(min_width: int, max_width: int) -> dict[str, object]:
    p46 = load("p46_p116", P46_PATH)
    lane = Lane(
        f"all endpoint-normalized integer Sidon rulers of widths {min_width}..{max_width}; "
        "all positive-defect translations; b=1,2"
    )
    for width in range(min_width, max_width + 1):
        for ruler in p46.sidon_rulers(width):
            lane.counts["bases"] += 1
            base = tuple(sorted(width - value for value in ruler))
            sums = unordered_sum_map(base)
            differences = positive_differences(base)
            p = len(base)
            baseline = (3 * p * p - p + 2) // 2
            max_gamma = baseline - width - 2
            if max_gamma < 0:
                continue
            for gamma in range(max_gamma + 1):
                h = width + gamma + 1
                system = None
                for b in (1, 2):
                    lane.candidate([width, list(ruler), gamma, b])
                    if not is_literal_hole(sums, differences, gamma, b):
                        continue
                    lane.counts["literal_holes"] += 1
                    if system is None:
                        system = fold_triangle_system(base, h)
                    row = row_record(
                        base, gamma, h, b, system, "complete-width",
                        f"width={width}; ruler={','.join(map(str, ruler))}; gamma={gamma}",
                    )
                    lane.live(row)
    return lane.result()


def archive_source(base) -> str:
    source = " | ".join(base.sources[:3])
    if len(base.sources) > 3:
        source += f" | +{len(base.sources) - 3} sources"
    return source


def scan_archive_translations(min_width: int) -> tuple[dict[str, object], list[object]]:
    p86 = load("p86_p116", P86_PATH)
    bases, manifests = p86.load_archives()
    lane = Lane(
        f"all P86 archived oriented Sidon bases of width >= {min_width}; all "
        "positive-defect folded translations; b=1,2"
    )
    for base_row in bases:
        base = base_row.values
        width = base[-1]
        if width < min_width:
            continue
        lane.counts["bases"] += 1
        sums = unordered_sum_map(base)
        differences = positive_differences(base)
        p = len(base)
        baseline = (3 * p * p - p + 2) // 2
        max_gamma = min(width - 1, baseline - width - 2)
        if max_gamma < 0:
            continue
        source = archive_source(base_row)
        for gamma in range(max_gamma + 1):
            h = width + gamma + 1
            if not any(total + h in sums for total in sums):
                continue
            system = None
            for b in (1, 2):
                lane.candidate([list(base), gamma, b])
                if not is_literal_hole(sums, differences, gamma, b):
                    continue
                lane.counts["literal_holes"] += 1
                if system is None:
                    system = fold_triangle_system(base, h)
                row = row_record(base, gamma, h, b, system, source, f"gamma={gamma}")
                lane.live(row)
    return lane.result(), manifests


def scan_archive_parity(min_width: int) -> dict[str, object]:
    p86 = load("p86_parity_p116", P86_PATH)
    bases, _manifests = p86.load_archives()
    lane = Lane(
        f"q=2 and q=3 literal-hole lifts of every folded P86 archived oriented "
        f"Sidon base of width >= {min_width} and every translation retaining positive defect"
    )
    for base_row in bases:
        base = base_row.values
        width = base[-1]
        if width < min_width:
            continue
        lane.counts["bases"] += 1
        sums = unordered_sum_map(base)
        p = len(base)
        baseline = (3 * p * p - p + 2) // 2
        max_gamma = min(width - 1, baseline - width - 2)
        source = archive_source(base_row)
        for gamma in range(max(0, max_gamma + 1)):
            source_h = width + gamma + 1
            if not any(total + source_h in sums for total in sums):
                continue
            system = None
            for q, residue in ((2, 1), (3, 2)):
                h = q * source_h
                if baseline <= h:
                    continue
                lane.candidate([q, residue, list(base), gamma])
                if system is None:
                    system = fold_triangle_system(base, source_h)
                lifted_base = tuple(q * value + residue for value in base)
                lifted_gamma = q * gamma
                row = row_record(
                    lifted_base, lifted_gamma, h, 1, system, source,
                    f"q={q}; residue={residue}; gamma={gamma}",
                )
                # Fold coordinates are scaled, but all counts and Hall cardinalities
                # are invariant; row_record only shifts labels in the demand display.
                row["B"] = [q * (value + gamma) + residue for value in base]
                row["width"] = q * width
                row["delta"] = baseline - h
                row["h"] = h
                row["demand"] = {
                    str(q * (color + gamma) + residue): count
                    for color, count in system.demand
                }
                lane.live(row)
    return lane.result()


def p88_deletion_bases() -> list[tuple[int, ...]]:
    p88 = load("p88_p116", P88_PATH)
    source = tuple(p88.B)
    orientations = (source, tuple(source[-1] - value for value in reversed(source)))
    rows: set[tuple[int, ...]] = set()
    for orientation in orientations:
        for deleted in range(len(orientation) - 1):
            row = normalized(orientation[:deleted] + orientation[deleted + 1:])
            unordered_sum_map(row)
            rows.add(row)
    return sorted(rows)


def scan_p88_deletions() -> dict[str, object]:
    lane = Lane(
        "all distinct normalized one-mark deletions of both P88 orientations, endpoint "
        "retained; every positive-defect folded translation; b=1,2"
    )
    for base in p88_deletion_bases():
        lane.counts["bases"] += 1
        width = base[-1]
        sums = unordered_sum_map(base)
        differences = positive_differences(base)
        p = len(base)
        baseline = (3 * p * p - p + 2) // 2
        max_gamma = min(width - 1, baseline - width - 2)
        for gamma in range(max(0, max_gamma + 1)):
            h = width + gamma + 1
            holes = [
                b for b in (1, 2)
                if is_literal_hole(sums, differences, gamma, b)
            ]
            for b in (1, 2):
                lane.candidate([list(base), gamma, b])
            if not holes or not any(total + h in sums for total in sums):
                continue
            system = fold_triangle_system(base, h)
            for b in holes:
                lane.counts["literal_holes"] += 1
                row = row_record(
                    base, gamma, h, b, system, "P88", "one deletion; "
                    f"base_sha256={hashlib.sha256(','.join(map(str, base)).encode('ascii')).hexdigest()}; "
                    f"gamma={gamma}",
                )
                lane.live(row)
    return lane.result()


def scan_p88_q2_insertions() -> dict[str, object]:
    p88 = load("p88_insert_p116", P88_PATH)
    base = tuple(2 * value + 1 for value in p88.B)
    h = 2 * p88.H
    lane = Lane(
        "all one-mark interior insertions into the q=2 P88 lift; all pairwise-compatible "
        "literal-hole insertions; b=1"
    )
    candidates = []
    for value in range(1, h):
        if value in base:
            continue
        lane.candidate(["single", value])
        row = tuple(sorted(base + (value,)))
        try:
            sums = unordered_sum_map(row)
            differences = positive_differences(row)
        except ValueError:
            continue
        lane.counts["Sidon_single_insertions"] += 1
        if differences.isdisjoint(total + 1 for total in sums):
            candidates.append(value)
            lane.counts["literal_hole_single_insertions"] += 1

    compatible = []
    for left_index, left in enumerate(candidates):
        for right in candidates[left_index + 1:]:
            lane.candidate(["pair", left, right])
            row = tuple(sorted(base + (left, right)))
            try:
                sums = unordered_sum_map(row)
                differences = positive_differences(row)
            except ValueError:
                continue
            if differences.isdisjoint(total + 1 for total in sums):
                compatible.append((left, right))
                lane.counts["compatible_pairs"] += 1

    adjacency: dict[int, set[int]] = {value: set() for value in candidates}
    for left, right in compatible:
        adjacency[left].add(right)
        adjacency[right].add(left)
    maximum_clique: tuple[int, ...] = ()

    def expand(clique: tuple[int, ...], available: tuple[int, ...]) -> None:
        nonlocal maximum_clique
        if len(clique) + len(available) <= len(maximum_clique):
            return
        if len(clique) > len(maximum_clique):
            maximum_clique = clique
        for index, value in enumerate(available):
            tail = tuple(
                other for other in available[index + 1:]
                if other in adjacency[value]
            )
            expand(clique + (value,), tail)

    expand((), tuple(candidates))
    lane.counts["pairwise_compatibility_clique_number"] = len(maximum_clique)
    result = lane.result()
    result.update({
        "literal_hole_single_insertion_values": candidates,
        "maximum_pairwise_compatible_set": list(maximum_clique),
        "positive_defect_minimum_p_at_h": next(
            p for p in range(1, 1000) if (3 * p * p - p + 2) // 2 > h
        ),
        "base_p": len(base),
        "h": h,
    })
    return result


def first_failure(lanes: dict[str, dict[str, object]], key: str) -> object:
    for lane in lanes.values():
        if lane.get(key) is not None:
            return lane[key]
    return None


def run(min_width: int, max_width: int) -> dict[str, object]:
    complete = scan_complete_widths(min_width, max_width)
    archive, manifests = scan_archive_translations(min_width)
    lanes = {
        "complete_widths": complete,
        "archive_translations": archive,
        "archive_parity_lifts": scan_archive_parity(min_width),
        "P88_one_deletion_translations": scan_p88_deletions(),
        "P88_q2_insertions": scan_p88_q2_insertions(),
    }


def run_one(lane_name: str, min_width: int, max_width: int) -> dict[str, object]:
    manifests = None
    if lane_name == "complete_widths":
        lane = scan_complete_widths(min_width, max_width)
    elif lane_name == "archive_translations":
        lane, manifests = scan_archive_translations(min_width)
    elif lane_name == "archive_parity_lifts":
        lane = scan_archive_parity(min_width)
    elif lane_name == "P88_one_deletion_translations":
        lane = scan_p88_deletions()
    elif lane_name == "P88_q2_insertions":
        lane = scan_p88_q2_insertions()
    else:
        raise ValueError(lane_name)
    lanes = {lane_name: lane}
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers; exact augmenting-path capacitated matching",
        "candidates": {
            "BC108": "sum_u max(t_u-n_u,0) <= p",
            "difference_Hall": "d_u copies of each color match to distinct values in D_u",
        },
        "complete_width_interval": [min_width, max_width],
        "lanes": lanes,
        "BC108_falsifier": first_failure(lanes, "first_BC108_failure"),
        "difference_Hall_falsifier": first_failure(
            lanes, "first_difference_hall_failure"
        ),
    }
    if manifests is not None:
        result["archive_manifest"] = manifests
    return result
    return {
        "schema_version": 1,
        "arithmetic": "exact Python integers; exact augmenting-path capacitated matching",
        "candidates": {
            "BC108": "sum_u max(t_u-n_u,0) <= p",
            "difference_Hall": "d_u copies of each color match to distinct values in D_u",
        },
        "complete_width_interval": [min_width, max_width],
        "archive_manifest": manifests,
        "lanes": lanes,
        "BC108_falsifier": first_failure(lanes, "first_BC108_failure"),
        "difference_Hall_falsifier": first_failure(
            lanes, "first_difference_hall_failure"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-width", type=int, default=31)
    parser.add_argument("--max-width", type=int, default=40)
    parser.add_argument(
        "--lane",
        choices=(
            "all", "complete_widths", "archive_translations",
            "archive_parity_lifts", "P88_one_deletion_translations",
            "P88_q2_insertions",
        ),
        default="all",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 31 <= args.min_width <= args.max_width:
        raise ValueError("require 31 <= min-width <= max-width")
    result = (
        run(args.min_width, args.max_width)
        if args.lane == "all"
        else run_one(args.lane, args.min_width, args.max_width)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        "output": str(args.output),
        "BC108_falsifier": result["BC108_falsifier"],
        "difference_Hall_falsifier": result["difference_Hall_falsifier"],
        "lane_counts": {
            name: {
                key: value for key, value in lane.items()
                if key in {
                    "bases", "candidates", "literal_holes", "live_rows",
                    "triangle_rows", "positive_excess_rows", "BC108_failures",
                    "difference_hall_failures", "domain_sha256", "live_rows_sha256",
                }
            }
            for name, lane in result["lanes"].items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()
