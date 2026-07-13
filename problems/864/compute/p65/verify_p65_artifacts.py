#!/usr/bin/env python3
"""Independent exact checks for the P65 finite results and graph obstruction."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SEARCH = ROOT / "problems/864/compute/p65/search_hole_restricted_folds.py"


def load_search():
    spec = importlib.util.spec_from_file_location("p65_verify_search", SEARCH)
    if spec is None or spec.loader is None:
        raise RuntimeError(SEARCH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def outer_edges(values: tuple[int, ...], h: int) -> set[tuple[int, int]]:
    sums = {}
    for i, x in enumerate(values):
        for y in values[i:]:
            if x + y in sums:
                raise AssertionError(("not Sidon", x + y))
            sums[x + y] = (x, y)
    edges = set()
    for low, low_pair in sums.items():
        high_pair = sums.get(low + h)
        if high_pair is not None:
            edge = (low_pair[0], high_pair[1])
            if edge in edges:
                raise AssertionError(("outer edge repeated", edge))
            edges.add(edge)
    return edges


def degeneracy(vertices: tuple[int, ...], edges: set[tuple[int, int]]) -> int:
    adjacency = {v: set() for v in vertices}
    for x, y in edges:
        adjacency[x].add(y)
        adjacency[y].add(x)
    remaining = set(vertices)
    answer = 0
    while remaining:
        v = min(remaining, key=lambda x: (len(adjacency[x] & remaining), x))
        answer = max(answer, len(adjacency[v] & remaining))
        remaining.remove(v)
    return answer


def main() -> None:
    search = load_search()
    width45 = json.loads((
        ROOT / "problems/864/compute/p65/hole_restricted_folds_width45.json"
    ).read_text(encoding="ascii"))
    ex = width45["exhaustive"]
    assert ex["rulers"] == 745733
    assert ex["hole_translations"] == 9953261
    assert ex["failure_count"] == 0
    assert ex["ruler_stream_sha256"] == (
        "772e239cc1a5d1a02f7f2d9a63f5e53fab579cb472834c14446d3bd97e2e9e53"
    )

    p20 = json.loads((
        ROOT / "problems/864/compute/p65/p20_hole_fold_audit.json"
    ).read_text(encoding="ascii"))
    assert p20["source_rulers"] == 133
    assert p20["admissible_translations"] == 165225
    assert p20["failure_count"] == 0

    parent = json.loads((
        ROOT / "problems/864/compute/p65/parent_subset_optimization.json"
    ).read_text(encoding="ascii"))
    assert parent["unresolved_count"] == 0
    assert parent["falsifier_count"] == 0
    assert parent["maximum_objective"] == -18

    dense = json.loads((
        ROOT / "problems/864/compute/p65/dense_subset_optimization.json"
    ).read_text(encoding="ascii"))
    assert dense["unresolved_count"] == 0
    assert dense["falsifier_count"] == 0
    assert dense["maximum_objective"] == -16

    # This exact conditioned example kills the tempting stronger C_S <= p-1.
    strongest = max(
        (row for row in parent["rows"] if row["status"] == "OPTIMAL"),
        key=lambda row: row["objective_C_S_minus_2p"],
    )["audit"]
    independent = search.fold_rows(
        tuple(x - strongest["gamma"] for x in strongest["B"]),
        strongest["gamma"], strongest["b"],
    )
    assert independent == strongest
    assert strongest["p"] == 19 and strongest["C_S"] == 20
    assert strongest["hole"] and strongest["delta"] > 0

    # Exact real hole instance whose outer collision graph contains K_{3,3}.
    carry = json.loads((
        ROOT / "problems/864/compute/p46/carry_statistics.json"
    ).read_text(encoding="ascii"))
    row = next(
        r for r in carry["p20"]["reports"]
        if r["source_id"] == "singer-e82f2d6a63ca"
    )
    values = tuple(int(x) for x in row["B"])
    h, b = int(row["h"]), int(row["b"])
    assert h == values[-1] + 1 and b == 1
    assert search.hole_holds(values, b)
    edges = outer_edges(values, h)
    assert len(edges) == int(row["sum_collision_residues"]) == 256
    assert all(2 * (y - x) >= h for x, y in edges)
    assert degeneracy(values, edges) == 6
    left = (7469, 7994, 8476)
    right = (27235, 27527, 28303)
    assert all((x, y) in edges for x in left for y in right)

    unrestricted = json.loads((
        ROOT / "problems/864/compute/p65/unrestricted_p25_H493_b1_target48.json"
    ).read_text(encoding="ascii"))
    assert unrestricted["status"] == "UNKNOWN"
    assert unrestricted["target_C_S"] == 48

    print(json.dumps({
        "width45_rulers": ex["rulers"],
        "width45_hole_translations": ex["hole_translations"],
        "p20_hole_translations": p20["admissible_translations"],
        "parent_max_objective": parent["maximum_objective"],
        "dense_max_objective": dense["maximum_objective"],
        "stronger_bound_falsifier": {
            "p": strongest["p"], "C_S": strongest["C_S"],
            "h": strongest["h"], "b": strongest["b"],
        },
        "outer_graph_K33": {"left": left, "right": right},
        "outer_graph_degeneracy": degeneracy(values, edges),
        "unrestricted_status": unrestricted["status"],
    }, indent=2))


if __name__ == "__main__":
    main()
