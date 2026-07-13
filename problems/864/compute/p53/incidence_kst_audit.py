#!/usr/bin/env python3
"""Exact audit of the direct KST graphs for the fold-repair residual."""

from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Iterable


BOSE_Z = (0, 7, 37, 48, 52, 68, 76, 101, 110, 111, 123, 161, 167,
          188, 190, 193, 207)
BOSE_GAMMA = 80
BOSE_B = tuple(BOSE_GAMMA + x for x in BOSE_Z)
BOSE_H = 288
BOSE_B_PARAMETER = 2


def sum_map(values: tuple[int, ...]) -> dict[int, tuple[int, int]]:
    out: dict[int, tuple[int, int]] = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in out:
                raise AssertionError(("sum collision", total, out[total], (left, right)))
            out[total] = (left, right)
    return out


def difference_map(values: tuple[int, ...]) -> dict[int, tuple[int, int] | None]:
    out: dict[int, tuple[int, int] | None] = {0: None}
    for left in values:
        for right in values:
            if left == right:
                continue
            difference = left - right
            if difference in out:
                raise AssertionError(("difference collision", difference))
            out[difference] = (left, right)
    return out


def modular_defect(support: Iterable[int], h: int) -> int:
    values = set(support)
    return len(values) - len({x % h for x in values})


def graph_statistics(edges: set[tuple[int, int]], vertices: tuple[int, ...]) -> dict[str, object]:
    left_neighbors = {x: set() for x in vertices}
    right_neighbors = {x: set() for x in vertices}
    for left, right in edges:
        left_neighbors[left].add(right)
        right_neighbors[right].add(left)

    codegrees = []
    for i, first in enumerate(vertices):
        for second in vertices[i + 1:]:
            common = sorted(left_neighbors[first] & left_neighbors[second])
            codegrees.append((len(common), first, second, common))
    codegrees.sort(reverse=True)

    def wedges(neighbors: dict[int, set[int]]) -> int:
        return sum(len(row) * (len(row) - 1) // 2 for row in neighbors.values())

    return {
        "edges": len(edges),
        "left_degrees": sorted(len(row) for row in left_neighbors.values()),
        "right_degrees": sorted(len(row) for row in right_neighbors.values()),
        "left_wedges": wedges(left_neighbors),
        "right_wedges": wedges(right_neighbors),
        "maximum_left_codegree": codegrees[0][0] if codegrees else 0,
        "left_pairs_with_codegree_at_least_two": sum(row[0] >= 2 for row in codegrees),
        "K22_witness": None if not codegrees or codegrees[0][0] < 2 else {
            "left_vertices": [codegrees[0][1], codegrees[0][2]],
            "common_right_vertices": codegrees[0][3],
        },
    }


def maximum_c4_free_subgraph(
    edges: set[tuple[int, int]], vertices: tuple[int, ...]
) -> dict[str, object]:
    from ortools.sat.python import cp_model

    ordered_edges = sorted(edges)
    edge_index = {edge: i for i, edge in enumerate(ordered_edges)}
    neighbors = {left: set() for left in vertices}
    for left, right in ordered_edges:
        neighbors[left].add(right)
    cycles: set[tuple[int, int, int, int]] = set()
    for i, first in enumerate(vertices):
        for second in vertices[i + 1:]:
            common = sorted(neighbors[first] & neighbors[second])
            for right1, right2 in combinations(common, 2):
                cycles.add(tuple(sorted((
                    edge_index[(first, right1)], edge_index[(first, right2)],
                    edge_index[(second, right1)], edge_index[(second, right2)],
                ))))

    model = cp_model.CpModel()
    kept = [model.new_bool_var(f"edge_{i}") for i in range(len(ordered_edges))]
    for cycle in cycles:
        model.add(sum(kept[i] for i in cycle) <= 3)
    model.maximize(sum(kept))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 64
    solver.parameters.max_time_in_seconds = 120
    status = solver.solve(model)
    if status != cp_model.OPTIMAL:
        raise AssertionError(("C4-free optimization not proved", solver.status_name(status)))
    maximum = int(round(solver.objective_value))
    return {
        "C4_count": len(cycles),
        "status": solver.status_name(status),
        "maximum_edges": maximum,
        "minimum_edge_deletions": len(ordered_edges) - maximum,
        "wall_time_seconds": solver.wall_time,
    }


def projection_statistics(
    relations: list[tuple[int, int, int, int]], vertices: tuple[int, ...]
) -> dict[str, object]:
    projections = {
        "sum_low__difference_left": (0, 2),
        "sum_low__difference_right": (0, 3),
        "sum_high__difference_left": (1, 2),
        "sum_high__difference_right": (1, 3),
        "sum_pair": (0, 1),
        "difference_pair": (2, 3),
    }
    out: dict[str, object] = {}
    for name, (left_index, right_index) in projections.items():
        projected = [(row[left_index], row[right_index]) for row in relations]
        multiplicities = Counter(projected)
        stats = graph_statistics(set(projected), vertices)
        stats["relations"] = len(relations)
        stats["duplicate_relations"] = len(relations) - len(multiplicities)
        stats["maximum_edge_multiplicity"] = max(multiplicities.values(), default=0)
        stats["is_injective"] = len(relations) == len(multiplicities)
        out[name] = stats
    return out


def audit() -> dict[str, object]:
    values = BOSE_B
    p = len(values)
    h = BOSE_H
    b = BOSE_B_PARAMETER
    sums = sum_map(values)
    differences = difference_map(values)
    c_s = modular_defect(sums, h)
    c_d = modular_defect(differences, h)
    baseline = (3 * p * p - p + 2) // 2
    delta = baseline - h
    residual = max(delta - 5 * (c_s + c_d), 0)
    hole = all(-b - total not in differences for total in sums)
    if not hole:
        raise AssertionError("Bose profile does not satisfy the required hole")

    sum_residues = {total % h for total in sums}
    translated_difference_residues = {(-b - d) % h for d in differences}
    overlap = sum_residues & translated_difference_residues
    missed_both = h - len(sum_residues | translated_difference_residues)

    carries: dict[str, object] = {}
    support_total = 0
    for carry in (1, 2):
        target = carry * h - b
        relations: list[tuple[int, int, int, int]] = []
        support_pairs = 0
        zero_difference_active = target in sums
        for difference, pair in differences.items():
            total = target - difference
            if total not in sums:
                continue
            support_pairs += 1
            if difference != 0:
                assert pair is not None
                relations.append((*sums[total], *pair))
        support_total += support_pairs

        expanded_edges = {
            (left, right)
            for left in values
            for right in values
            if target - (left - right) in sums
        }
        nonzero_edges = {(left, right) for left, right in expanded_edges if left != right}
        expanded_stats = graph_statistics(expanded_edges, values)
        expanded_stats["maximum_C4_free_subgraph"] = maximum_c4_free_subgraph(
            expanded_edges, values
        )
        carries[str(carry)] = {
            "target": target,
            "support_pairs_Uk": support_pairs,
            "zero_difference_active": zero_difference_active,
            "expanded_difference_edge_graph": expanded_stats,
            "nonzero_difference_edge_graph": graph_statistics(nonzero_edges, values),
            "endpoint_projection_graphs_nonzero": projection_statistics(relations, values),
        }

    if delta != len(overlap) + c_s + c_d - missed_both:
        raise AssertionError("defect identity failed")
    if delta != support_total - missed_both:
        raise AssertionError("collision-free support identity failed")

    # A short literal K_2,2 is easier to referee than the maximum-codegree one.
    target = h - b
    explicit_left = (80, 87)
    explicit_right = (128, 132)
    explicit_edges = []
    for left in explicit_left:
        for right in explicit_right:
            total = target - (left - right)
            if total not in sums:
                raise AssertionError("explicit K22 edge absent")
            explicit_edges.append(
                {
                    "left": left,
                    "right": right,
                    "difference": left - right,
                    "complementary_sum": total,
                    "sum_pair": list(sums[total]),
                }
            )

    return {
        "schema_version": 1,
        "arithmetic": "exact integers",
        "profile": {
            "Z": list(BOSE_Z),
            "gamma": BOSE_GAMMA,
            "B": list(values),
            "p": p,
            "h": h,
            "b": b,
            "sidon_including_diagonals": len(sums) == p * (p + 1) // 2,
            "minus_b_not_in_3B_minus_B": hole,
        },
        "fold_repair": {
            "delta": delta,
            "C_S": c_s,
            "C_D": c_d,
            "residual": residual,
            "residual_squared": residual * residual,
            "four_p_cubed": 4 * p**3,
            "ratio_numerator": residual * residual,
            "ratio_denominator": p**3,
            "modular_overlap_I": len(overlap),
            "missed_both_H0": missed_both,
            "U1_plus_U2": support_total,
        },
        "carry_graphs": carries,
        "explicit_carry1_K22": {
            "left_vertices": list(explicit_left),
            "right_vertices": list(explicit_right),
            "edges": explicit_edges,
        },
        "verdict": (
            "The direct difference-edge carry graph and every fixed obvious "
            "endpoint projection fail the codegree-one/C4-free KST premise, "
            "already when C_S=C_D=0."
        ),
    }


def main() -> None:
    output = Path("problems/864/compute/p53/kst_bose_p17_audit.json")
    report = audit()
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(output)


if __name__ == "__main__":
    main()
