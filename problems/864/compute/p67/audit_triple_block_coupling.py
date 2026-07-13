"""Exact probes for cross-column coupling of actual equal-three-sum blocks.

The balanced blocks are the type-111 and type-3 representations from P51.
For two distinct sum columns, their block-intersection multigraph has one
edge for each common mark.  All arithmetic and all graph statistics here are
integer exact.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from itertools import combinations, combinations_with_replacement
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[4]
P864 = ROOT / "problems" / "864"
BOSE_Q128 = P864 / "compute" / "p37" / "bose_q128_sample.jsonl"
OUT = Path(__file__).with_name("audit_results.json")


Block = tuple[int, ...]


def pair_sums(values: tuple[int, ...]) -> set[int]:
    return {a + b for i, a in enumerate(values) for b in values[i:]}


def positive_differences(values: tuple[int, ...]) -> set[int]:
    return {b - a for i, a in enumerate(values) for b in values[i + 1 :]}


def is_sidon(values: tuple[int, ...]) -> bool:
    return len(pair_sums(values)) == len(values) * (len(values) + 1) // 2


def is_valid_pair(values: tuple[int, ...], gap: int) -> bool:
    differences = positive_differences(values)
    return differences.isdisjoint({gap + s for s in pair_sums(values)})


def balanced_columns(
    values: tuple[int, ...], cutoff: int
) -> dict[int, tuple[Block, ...]]:
    low = tuple(value for value in values if value <= cutoff)
    columns: dict[int, list[Block]] = defaultdict(list)
    for triple in combinations_with_replacement(low, 3):
        total = sum(triple)
        if total <= cutoff and len(set(triple)) in (1, 3):
            columns[total].append(triple)

    result: dict[int, tuple[Block, ...]] = {}
    for total, blocks in columns.items():
        supports = [set(block) for block in blocks]
        for left, right in combinations(supports, 2):
            assert left.isdisjoint(right), (values, total, blocks)
        result[total] = tuple(blocks)
    return dict(sorted(result.items()))


def graph_components(
    qx: int, qy: int, incidences: list[tuple[int, int, int]]
) -> tuple[int, int]:
    """Return (active vertices, connected components) in the simple graph."""
    adjacency: list[set[int]] = [set() for _ in range(qx + qy)]
    for left, right, multiplicity in incidences:
        assert multiplicity > 0
        u, v = left, qx + right
        adjacency[u].add(v)
        adjacency[v].add(u)
    active = {vertex for vertex, neighbors in enumerate(adjacency) if neighbors}
    components = 0
    unseen = set(active)
    while unseen:
        components += 1
        start = unseen.pop()
        queue = deque([start])
        while queue:
            vertex = queue.popleft()
            for neighbor in adjacency[vertex]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
    return len(active), components


def pair_profile(
    x: int, left: tuple[Block, ...], y: int, right: tuple[Block, ...]
) -> dict[str, object]:
    assert x != y
    incidences: list[tuple[int, int, int]] = []
    common_marks: set[int] = set()
    for i, a in enumerate(left):
        sa = set(a)
        for j, b in enumerate(right):
            intersection = sa.intersection(b)
            if intersection:
                multiplicity = len(intersection)
                assert multiplicity <= 2, (x, a, y, b)
                incidences.append((i, j, multiplicity))
                common_marks.update(intersection)

    edges = len(common_marks)
    simple_edges = len(incidences)
    double_edges = sum(multiplicity - 1 for _, _, multiplicity in incidences)
    active_vertices, components = graph_components(len(left), len(right), incidences)
    cycle_rank = simple_edges - active_vertices + components
    return {
        "x": x,
        "y": y,
        "left_blocks": len(left),
        "right_blocks": len(right),
        "common_marks": sorted(common_marks),
        "edges": edges,
        "simple_edges": simple_edges,
        "double_edges": double_edges,
        "active_vertices": active_vertices,
        "components": components,
        "cycle_rank": cycle_rank,
        "vertex_excess": edges - len(left) - len(right),
        "incidences": incidences,
        "left": [list(block) for block in left],
        "right": [list(block) for block in right],
    }


def audit_case(
    name: str, values: tuple[int, ...], gap: int
) -> dict[str, object]:
    assert is_sidon(values), name
    assert is_valid_pair(values, gap), name
    cutoff = values[-1] - gap
    columns = balanced_columns(values, cutoff)
    profiles = [
        pair_profile(x, columns[x], y, columns[y])
        for x, y in combinations(columns, 2)
    ]
    double_failures = [row for row in profiles if int(row["double_edges"]) > 1]
    plus_one_failures = [
        row for row in profiles if int(row["vertex_excess"]) > 1
    ]
    pseudoforest_failures = [
        row for row in profiles if int(row["cycle_rank"]) > int(row["components"])
    ]
    return {
        "name": name,
        "p": len(values),
        "W": values[-1],
        "G": gap,
        "K": cutoff,
        "columns": len(columns),
        "column_pairs": len(profiles),
        "balanced_blocks": sum(len(blocks) for blocks in columns.values()),
        "balanced_incidence": sum(
            len(set(block)) for blocks in columns.values() for block in blocks
        ),
        "maximum_common_marks": max(
            (int(row["edges"]) for row in profiles), default=0
        ),
        "maximum_vertex_excess": max(
            (int(row["vertex_excess"]) for row in profiles), default=0
        ),
        "maximum_cycle_rank": max(
            (int(row["cycle_rank"]) for row in profiles), default=0
        ),
        "maximum_double_edges": max(
            (int(row["double_edges"]) for row in profiles), default=0
        ),
        "double_edge_failures": len(double_failures),
        "plus_one_failures": len(plus_one_failures),
        "pseudoforest_failures": len(pseudoforest_failures),
        "largest_excess_profile": max(
            profiles,
            key=lambda row: (
                int(row["vertex_excess"]),
                int(row["edges"]),
                -int(row["x"]),
                -int(row["y"]),
            ),
            default=None,
        ),
    }


def endpoint_sidon_rulers(width: int) -> Iterable[tuple[int, ...]]:
    interior = range(1, width)
    for size in range(0, width - 1):
        for middle in combinations(interior, size):
            values = (0, *middle, width)
            if is_sidon(values):
                yield values


def exhaustive_small(max_width: int) -> dict[str, object]:
    rulers = 0
    valid_pairs = 0
    column_pairs = 0
    plus_one_failures = 0
    pseudoforest_failures = 0
    double_failures = 0
    maximum_excess = -10**9
    maximum_cycle_rank = 0
    extremal: dict[str, object] | None = None
    for width in range(1, max_width + 1):
        for values in endpoint_sidon_rulers(width):
            rulers += 1
            for gap in range(1, width):
                if not is_valid_pair(values, gap):
                    continue
                valid_pairs += 1
                record = audit_case("exhaustive", values, gap)
                column_pairs += int(record["column_pairs"])
                plus_one_failures += int(record["plus_one_failures"])
                pseudoforest_failures += int(record["pseudoforest_failures"])
                double_failures += int(record["double_edge_failures"])
                maximum_cycle_rank = max(
                    maximum_cycle_rank, int(record["maximum_cycle_rank"])
                )
                profile = record["largest_excess_profile"]
                if profile is not None and int(profile["vertex_excess"]) > maximum_excess:
                    maximum_excess = int(profile["vertex_excess"])
                    extremal = {
                        "Z": list(values),
                        "G": gap,
                        "K": width - gap,
                        **profile,
                    }
    return {
        "max_width": max_width,
        "endpoint_sidon_rulers": rulers,
        "valid_pairs": valid_pairs,
        "column_pairs": column_pairs,
        "maximum_vertex_excess": maximum_excess if extremal else 0,
        "maximum_cycle_rank": maximum_cycle_rank,
        "double_edge_failures": double_failures,
        "plus_one_failures": plus_one_failures,
        "pseudoforest_failures": pseudoforest_failures,
        "largest_excess_profile": extremal,
    }


def load_q128() -> tuple[tuple[int, ...], int]:
    record = json.loads(BOSE_Q128.read_text(encoding="ascii").splitlines()[0])
    candidate = record["best_candidate"]
    reflected = tuple(int(value) for value in candidate["points"])
    width = int(candidate["span"])
    center = int(candidate["candidate_center"])
    values = tuple(sorted(width - value for value in reflected))
    return values, center - 2 * width


def audit_all(max_width: int) -> dict[str, object]:
    p59_values = (0, 7, 9, 12, 20, 26, 30, 58)
    q128_values, q128_gap = load_q128()
    result = {
        "exact_arithmetic": "integers",
        "candidate": (
            "For actual balanced block partitions at distinct sums x,y, "
            "|B_x intersect B_y| <= q_x+q_y+1"
        ),
        "exhaustive": exhaustive_small(max_width),
        "p59": audit_case("p59", p59_values, 15),
        "q128": audit_case("q128", q128_values, q128_gap),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=18)
    args = parser.parse_args()
    result = audit_all(args.max_width)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
