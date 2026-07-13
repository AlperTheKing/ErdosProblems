#!/usr/bin/env python3
"""Exact searches for the shifted unordered-sum overlap in Problem 864.

All pair sums use i <= j, so diagonal sums are part of every model and audit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator, Sequence


# One representative of each published optimal ruler of orders 20 through 28.
# The exact search also scans the reflected representative and every translation
# that can have a nonempty h-shifted overlap.
DENSE_RULERS: tuple[tuple[int, ...], ...] = (
    (0, 1, 8, 11, 68, 77, 94, 116, 121, 156, 158, 179, 194, 208, 212,
     228, 240, 253, 259, 283),
    (0, 2, 24, 56, 77, 82, 83, 95, 129, 144, 179, 186, 195, 255, 265,
     285, 293, 296, 310, 329, 333),
    (0, 1, 9, 14, 43, 70, 106, 122, 124, 128, 159, 179, 204, 223, 253,
     263, 270, 291, 330, 341, 353, 356),
    (0, 3, 7, 17, 61, 66, 91, 99, 114, 159, 171, 199, 200, 226, 235,
     246, 277, 316, 329, 348, 350, 366, 372),
    (0, 9, 33, 37, 38, 97, 122, 129, 140, 142, 152, 191, 205, 208, 252,
     278, 286, 326, 332, 353, 368, 384, 403, 425),
    (0, 12, 29, 39, 72, 91, 146, 157, 160, 161, 166, 191, 207, 214,
     258, 290, 316, 354, 372, 394, 396, 431, 459, 467, 480),
    (0, 1, 33, 83, 104, 110, 124, 163, 185, 200, 203, 249, 251, 258,
     314, 318, 343, 356, 386, 430, 440, 456, 464, 475, 487, 492),
    (0, 3, 15, 41, 66, 95, 97, 106, 142, 152, 220, 221, 225, 242, 295,
     330, 338, 354, 382, 388, 402, 415, 486, 504, 523, 546, 553),
    (0, 3, 15, 41, 66, 95, 97, 106, 142, 152, 220, 221, 225, 242, 295,
     330, 338, 354, 382, 388, 402, 415, 486, 504, 523, 546, 553, 585),
)


def unordered_sum_map(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    out: dict[int, tuple[int, int]] = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in out:
                raise ValueError(
                    f"not Sidon including diagonals: {out[total]} and "
                    f"{(left, right)} both sum to {total}"
                )
            out[total] = (left, right)
    return out


def positive_difference_map(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    out: dict[int, tuple[int, int]] = {}
    for j, right in enumerate(values):
        for left in values[:j]:
            difference = right - left
            if difference in out:
                raise ValueError(
                    f"repeated positive difference {difference}: "
                    f"{out[difference]} and {(left, right)}"
                )
            out[difference] = (left, right)
    return out


def witness_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def audit(values_input: Iterable[int], h: int | None = None) -> dict[str, object]:
    values = tuple(sorted(int(x) for x in values_input))
    if not values or len(set(values)) != len(values) or values[0] < 0:
        raise ValueError(f"invalid nonnegative set: {values}")
    if h is None:
        h = values[-1] + 1
    if h <= 0 or values[-1] != h - 1:
        raise ValueError(f"endpoint condition fails: max(B)={values[-1]}, h={h}")

    p = len(values)
    sums = unordered_sum_map(values)
    differences = positive_difference_map(values)
    expected_sums = p * (p + 1) // 2
    expected_differences = p * (p - 1) // 2
    if len(sums) != expected_sums or len(differences) != expected_differences:
        raise AssertionError("support cardinality check failed")

    collisions: list[dict[str, object]] = []
    type_counts: Counter[str] = Counter()
    for low_sum in sorted(sums):
        high_sum = low_sum + h
        if high_sum not in sums:
            continue
        a, b = sums[low_sum]
        c, d = sums[high_sum]
        if not (a <= b < c <= d):
            raise AssertionError(("separation", a, b, c, d, h))
        central = c - b
        outer = d - a
        wrap = h - d + a
        if central + outer != h or central != wrap:
            raise AssertionError(("interval identity", a, b, c, d, h))
        if a == b and c == d:
            kind = "diagonal_diagonal"
        elif a == b:
            kind = "low_diagonal"
        elif c == d:
            kind = "high_diagonal"
        else:
            kind = "off_diagonal"
        type_counts[kind] += 1
        collisions.append(
            {
                "low_sum": low_sum,
                "low_pair": [a, b],
                "high_sum": high_sum,
                "high_pair": [c, d],
                "type": kind,
                "central_interval": [b, c],
                "outer_interval": [a, d],
                "central_length": central,
                "outer_length": outer,
                "wrap_length": wrap,
            }
        )

    c_s = len(collisions)
    bound = 2 * p - 3
    positions = {value: i for i, value in enumerate(values)}
    central_edges = [
        (positions[int(row["central_interval"][0])],
         positions[int(row["central_interval"][1])])
        for row in collisions
    ]
    if len(central_edges) != len(set(central_edges)):
        raise AssertionError("central-interval charging is not injective")
    crossing_pairs = sum(
        left1 < left2 < right1 < right2 or left2 < left1 < right2 < right1
        for edge_index, (left1, right1) in enumerate(central_edges)
        for left2, right2 in central_edges[edge_index + 1:]
    )
    central_degrees = Counter(vertex for edge in central_edges for vertex in edge)
    full_difference_labels: dict[int, tuple[int, int]] = {}
    for left in values:
        for right in values:
            full_difference_labels.setdefault(left - right, (left, right))
    hole_checks: dict[str, bool] = {}
    hole_witnesses: dict[str, list[int] | None] = {}
    for b in (1, 2):
        witness = None
        for total, (x, y) in sums.items():
            pair = full_difference_labels.get(-b - total)
            if pair is not None:
                witness = [x, y, pair[0], pair[1]]
                break
        hole_checks[str(-b)] = witness is None
        hole_witnesses[str(-b)] = witness
    report: dict[str, object] = {
        "schema_version": 1,
        "arithmetic": "integer",
        "hypotheses": {
            "B": list(values),
            "p": p,
            "h": h,
            "B_subset": [0, h - 1],
            "max_B": values[-1],
            "sidon_including_diagonals": True,
        },
        "checks": {
            "unordered_sum_support": len(sums),
            "expected_unordered_sum_support": expected_sums,
            "positive_difference_support": len(differences),
            "expected_positive_difference_support": expected_differences,
            "minus_b_not_in_3B_minus_B": hole_checks,
            "minus_b_in_3B_minus_B_witness_xyzw": hole_witnesses,
        },
        "claim": {
            "C_S": c_s,
            "two_p_minus_three": bound,
            "C_S_minus_bound": c_s - bound,
            "holds": c_s <= bound,
        },
        "collision_type_counts": dict(sorted(type_counts.items())),
        "central_interval_graph": {
            "vertices": p,
            "edges": len(central_edges),
            "all_edges_distinct": True,
            "crossing_edge_pairs_in_mark_order": crossing_pairs,
            "degree_sequence": sorted(central_degrees[i] for i in range(p)),
        },
        "collisions": collisions,
    }
    report["sha256"] = witness_digest(report)
    return report


def sidon_rulers(width: int) -> Iterator[tuple[int, ...]]:
    """Generate every subset containing 0,width with unique positive differences."""
    chosen = [0]
    used: set[int] = set()

    def new_differences(value: int) -> tuple[int, ...] | None:
        additions = tuple(value - old for old in chosen)
        if len(additions) != len(set(additions)) or any(x in used for x in additions):
            return None
        return additions

    def recurse(next_value: int) -> Iterator[tuple[int, ...]]:
        endpoint = new_differences(width)
        if endpoint is not None:
            yield tuple(chosen + [width])
        for value in range(next_value, width):
            additions = new_differences(value)
            if additions is None:
                continue
            chosen.append(value)
            used.update(additions)
            yield from recurse(value + 1)
            used.difference_update(additions)
            chosen.pop()

    yield from recurse(1)


def overlap_count_from_normalized(ruler: Sequence[int], h: int) -> int:
    sums = unordered_sum_map(ruler)
    return sum(total + h in sums for total in sums)


def scan_exhaustive(max_width: int) -> dict[str, object]:
    started = time.perf_counter()
    rulers = translations = 0
    by_width: list[dict[str, int]] = []
    smallest_failure: tuple[int, int, tuple[int, ...], int] | None = None
    maximum_slack: tuple[int, int, int, tuple[int, ...], int] | None = None
    digest = hashlib.sha256()

    for width in range(1, max_width + 1):
        width_rulers = width_translations = 0
        for ruler in sidon_rulers(width):
            rulers += 1
            width_rulers += 1
            p = len(ruler)
            sums = unordered_sum_map(ruler)
            digest.update(json.dumps(ruler, separators=(",", ":")).encode("ascii"))
            # If gamma >= width, then h=width+gamma+1 > 2*width and C_S=0.
            for gamma in range(width):
                h = width + gamma + 1
                c_s = sum(total + h in sums for total in sums)
                values = tuple(gamma + x for x in ruler)
                translations += 1
                width_translations += 1
                row = (c_s - (2 * p - 3), c_s, p, values, h)
                if maximum_slack is None or row > maximum_slack:
                    maximum_slack = row
                if row[0] > 0:
                    key = (p, h, values, c_s)
                    if smallest_failure is None or key < smallest_failure:
                        smallest_failure = key
        by_width.append(
            {
                "width": width,
                "normalized_rulers": width_rulers,
                "translations": width_translations,
            }
        )

    assert maximum_slack is not None
    return {
        "schema_version": 1,
        "arithmetic": "integer exhaustive",
        "domain": (
            f"all normalized Sidon rulers of width <= {max_width}, and all "
            "translations gamma with 0 <= gamma < width"
        ),
        "normalized_rulers": rulers,
        "translations": translations,
        "ruler_sha256": digest.hexdigest(),
        "maximum_slack": {
            "C_S_minus_bound": maximum_slack[0],
            "C_S": maximum_slack[1],
            "p": maximum_slack[2],
            "B": list(maximum_slack[3]),
            "h": maximum_slack[4],
        },
        "smallest_failure": None if smallest_failure is None else {
            "p": smallest_failure[0],
            "h": smallest_failure[1],
            "B": list(smallest_failure[2]),
            "C_S": smallest_failure[3],
        },
        "by_width": by_width,
        "elapsed_seconds": time.perf_counter() - started,
    }


def scan_dense() -> dict[str, object]:
    started = time.perf_counter()
    reports: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    for source in DENSE_RULERS:
        width = source[-1]
        for orientation, ruler in (
            ("listed", source),
            ("reflected", tuple(width - x for x in reversed(source))),
        ):
            unordered_sum_map(ruler)
            positive_difference_map(ruler)
            best: tuple[int, int, int] | None = None
            for gamma in range(width):
                h = width + gamma + 1
                c_s = overlap_count_from_normalized(ruler, h)
                row = (c_s - (2 * len(ruler) - 3), c_s, h)
                if best is None or row > best:
                    best = row
                if row[0] > 0:
                    values = tuple(gamma + x for x in ruler)
                    failures.append(audit(values, h))
            assert best is not None
            reports.append(
                {
                    "p": len(ruler),
                    "width": width,
                    "orientation": orientation,
                    "best_C_S_minus_bound": best[0],
                    "best_C_S": best[1],
                    "best_h": best[2],
                }
            )
    failures.sort(
        key=lambda row: (
            int(row["hypotheses"]["p"]),
            int(row["hypotheses"]["h"]),
            row["hypotheses"]["B"],
        )
    )
    return {
        "schema_version": 1,
        "arithmetic": "integer exact scan",
        "domain": (
            "one listed and one reflected optimal ruler of each order 20..28, "
            "with every translation capable of a nonempty overlap"
        ),
        "reports": reports,
        "failure_count": len(failures),
        "smallest_failure": failures[0] if failures else None,
        "failures": failures,
        "elapsed_seconds": time.perf_counter() - started,
    }


def cp_sat_search(
    p: int,
    h: int,
    target: int,
    seconds: float,
    workers: int,
    hint: Sequence[int] | None,
) -> dict[str, object]:
    from ortools.sat.python import cp_model

    if p < 2 or h < 2 or target < 0:
        raise ValueError("invalid CP-SAT parameters")
    model = cp_model.CpModel()
    marks = [model.new_int_var(0, h - 1, f"b_{i}") for i in range(p)]
    for left, right in zip(marks, marks[1:]):
        model.add(left < right)
    model.add(marks[-1] == h - 1)

    pair_sums = []
    for i in range(p):
        for j in range(i, p):
            total = model.new_int_var(0, 2 * h - 2, f"s_{i}_{j}")
            model.add(total == marks[i] + marks[j])
            pair_sums.append(total)
    model.add_all_different(pair_sums)

    occupied = [model.new_bool_var(f"y_{value}") for value in range(2 * h - 1)]
    for total in pair_sums:
        model.add_element(total, occupied, 1)
    model.add(sum(occupied) == len(pair_sums))

    overlaps = []
    for low in range(h - 1):
        overlap = model.new_bool_var(f"z_{low}")
        model.add(overlap <= occupied[low])
        model.add(overlap <= occupied[low + h])
        model.add(overlap >= occupied[low] + occupied[low + h] - 1)
        overlaps.append(overlap)
    model.add(sum(overlaps) >= target)
    model.maximize(sum(overlaps))

    if hint is not None:
        if len(hint) != p or sorted(hint) != list(hint) or hint[-1] != h - 1:
            raise ValueError("hint does not match p,h")
        for variable, value in zip(marks, hint):
            model.add_hint(variable, int(value))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = max(1, min(workers, 64))
    solver.parameters.random_seed = 86453
    solver.parameters.log_search_progress = False
    status = solver.solve(model)
    status_name = solver.status_name(status)
    report: dict[str, object] = {
        "schema_version": 1,
        "model": "ordered marks; AllDifferent unordered sums including diagonals",
        "p": p,
        "h": h,
        "target_C_S": target,
        "time_limit_seconds": seconds,
        "workers": max(1, min(workers, 64)),
        "status": status_name,
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        values = tuple(solver.value(x) for x in marks)
        report["witness"] = audit(values, h)
        report["objective_C_S"] = int(round(solver.objective_value))
        report["best_bound_C_S"] = int(round(solver.best_objective_bound))
    return report


def minimize_witness(
    values_input: Iterable[int], h: int | None, seconds: float, workers: int
) -> dict[str, object]:
    """Optimize every endpoint-preserving subset of one audited witness."""
    from ortools.sat.python import cp_model

    source = audit(values_input, h)
    values = tuple(int(x) for x in source["hypotheses"]["B"])
    h = int(source["hypotheses"]["h"])
    position = {value: i for i, value in enumerate(values)}
    hyperedges = [
        frozenset(position[x] for x in row["low_pair"] + row["high_pair"])
        for row in source["collisions"]
    ]
    per_size: list[dict[str, object]] = []
    smallest: dict[str, object] | None = None
    per_solve_seconds = seconds / max(1, len(values) - 1)

    for subset_size in range(2, len(values) + 1):
        model = cp_model.CpModel()
        kept = [model.new_bool_var(f"keep_{i}") for i in range(len(values))]
        model.add(kept[-1] == 1)
        model.add(sum(kept) == subset_size)
        surviving = []
        for edge_index, edge in enumerate(hyperedges):
            live = model.new_bool_var(f"live_{edge_index}")
            for vertex in edge:
                model.add(live <= kept[vertex])
            model.add(live >= sum(kept[vertex] for vertex in edge) - len(edge) + 1)
            surviving.append(live)
        model.maximize(sum(surviving))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = per_solve_seconds
        solver.parameters.num_search_workers = max(1, min(workers, 64))
        solver.parameters.random_seed = 86453 + subset_size
        status = solver.solve(model)
        row: dict[str, object] = {
            "subset_size": subset_size,
            "status": solver.status_name(status),
            "wall_time_seconds": solver.wall_time,
            "branches": solver.num_branches,
            "conflicts": solver.num_conflicts,
        }
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            subset = tuple(values[i] for i in range(len(values)) if solver.value(kept[i]))
            checked = audit(subset, h)
            row["maximum_C_S"] = checked["claim"]["C_S"]
            row["best_bound_C_S"] = int(round(solver.best_objective_bound))
            row["B"] = list(subset)
            row["violates"] = not bool(checked["claim"]["holds"])
            if row["violates"] and smallest is None and status == cp_model.OPTIMAL:
                smallest = checked
        per_size.append(row)

    return {
        "schema_version": 1,
        "arithmetic": "integer CP-SAT plus independent audit",
        "source": source,
        "subset_domain": "all subsets of source B that retain max(B)=h-1",
        "time_limit_seconds": seconds,
        "workers": max(1, min(workers, 64)),
        "per_size": per_size,
        "smallest_proved_failure": smallest,
    }


def parse_values(text: str) -> tuple[int, ...]:
    return tuple(int(token) for token in text.replace(",", " ").split())


def write_report(report: object, output: Path | None) -> None:
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output is None:
        print(encoded, end="")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="ascii")
        print(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--B", required=True, type=parse_values)
    verify_parser.add_argument("--h", type=int)
    verify_parser.add_argument("--output", type=Path)

    exhaustive_parser = subparsers.add_parser("exhaustive")
    exhaustive_parser.add_argument("--max-width", type=int, required=True)
    exhaustive_parser.add_argument("--output", type=Path)

    dense_parser = subparsers.add_parser("dense")
    dense_parser.add_argument("--output", type=Path)

    cp_parser = subparsers.add_parser("cpsat")
    cp_parser.add_argument("--p", type=int, required=True)
    cp_parser.add_argument("--h", type=int, required=True)
    cp_parser.add_argument("--target", type=int, required=True)
    cp_parser.add_argument("--seconds", type=float, default=300.0)
    cp_parser.add_argument("--workers", type=int, default=64)
    cp_parser.add_argument("--hint", type=parse_values)
    cp_parser.add_argument("--output", type=Path)

    minimize_parser = subparsers.add_parser("minimize")
    minimize_parser.add_argument("--B", required=True, type=parse_values)
    minimize_parser.add_argument("--h", type=int)
    minimize_parser.add_argument("--seconds", type=float, default=300.0)
    minimize_parser.add_argument("--workers", type=int, default=64)
    minimize_parser.add_argument("--output", type=Path)

    args = parser.parse_args()
    if args.command == "verify":
        report = audit(args.B, args.h)
    elif args.command == "exhaustive":
        report = scan_exhaustive(args.max_width)
    elif args.command == "dense":
        report = scan_dense()
    elif args.command == "cpsat":
        report = cp_sat_search(
            args.p, args.h, args.target, args.seconds, args.workers, args.hint
        )
    else:
        report = minimize_witness(args.B, args.h, args.seconds, args.workers)
    write_report(report, args.output)


if __name__ == "__main__":
    main()
