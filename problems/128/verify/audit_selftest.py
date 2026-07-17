#!/usr/bin/env python3
"""Exact self-tests for audit_verify.py using known non-certificates."""

from __future__ import annotations
import json
from audit_verify import (
    AdjacencyError,
    EXPECTED_HALF_SETS,
    EXPECTED_TRIPLES,
    audit,
    normalize_adjacency,
)


def graph_from_edges(edges: set[tuple[int, int]]) -> tuple[frozenset[int], ...]:
    rows = [[] for _ in range(20)]
    for u, v in edges:
        rows[u].append(v)
        rows[v].append(u)
    return normalize_adjacency(rows)


def complete_graph() -> tuple[frozenset[int], ...]:
    return graph_from_edges({(u, v) for u in range(20) for v in range(u + 1, 20)})


def c5_blowup_4() -> tuple[frozenset[int], ...]:
    edges: set[tuple[int, int]] = set()
    parts = [list(range(4 * i, 4 * i + 4)) for i in range(5)]
    for i in range(5):
        for u in parts[i]:
            for v in parts[(i + 1) % 5]:
                edges.add(tuple(sorted((u, v))))
    return graph_from_edges(edges)


def petersen_blowup_2() -> tuple[frozenset[int], ...]:
    base_edges: set[tuple[int, int]] = set()
    for i in range(5):
        base_edges.add(tuple(sorted((i, (i + 1) % 5))))
        base_edges.add(tuple(sorted((5 + i, 5 + (i + 2) % 5))))
        base_edges.add((i, 5 + i))
    edges: set[tuple[int, int]] = set()
    for u, v in base_edges:
        for copy_u in (2 * u, 2 * u + 1):
            for copy_v in (2 * v, 2 * v + 1):
                edges.add(tuple(sorted((copy_u, copy_v))))
    return graph_from_edges(edges)


def check_case(name, adjacency, *, edges, triangles, minimum, maximum):
    result = audit(adjacency)
    assert result["edge_count"] == edges
    assert result["triangle_count"] == triangles
    assert result["minimum_half_edges"] == minimum
    assert result["maximum_half_edges"] == maximum
    assert result["triangle_triples_checked"] == EXPECTED_TRIPLES
    assert result["half_sets_checked"] == EXPECTED_HALF_SETS
    assert result["passes_problem_128_n20"] is False
    return {
        "case": name,
        "edge_count": result["edge_count"],
        "triangle_count": result["triangle_count"],
        "minimum_half_edges": result["minimum_half_edges"],
        "maximum_half_edges": result["maximum_half_edges"],
        "violating_half_sets_below_9": result["violating_half_sets_below_9"],
        "certificate_sha256": result["certificate_sha256"],
        "expected_noncertificate": "PASS",
    }


def main() -> None:
    reports = [
        check_case(
            "empty", normalize_adjacency([[] for _ in range(20)]),
            edges=0, triangles=0, minimum=0, maximum=0,
        ),
        check_case(
            "complete", complete_graph(),
            edges=190, triangles=1140, minimum=45, maximum=45,
        ),
        check_case(
            "C5_blowup_4", c5_blowup_4(),
            edges=80, triangles=0, minimum=8, maximum=24,
        ),
        check_case(
            "Petersen_blowup_2", petersen_blowup_2(),
            edges=60, triangles=0, minimum=8, maximum=20,
        ),
    ]

    asymmetric = [[] for _ in range(20)]
    asymmetric[0] = [1]
    try:
        normalize_adjacency(asymmetric)
    except AdjacencyError:
        reports.append({"case": "asymmetric_input", "parser_rejection": "PASS"})
    else:
        raise AssertionError("Asymmetric input was accepted")

    for report in reports:
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    print(json.dumps({
        "selftest": "PASS",
        "cases": len(reports),
        "triples_per_graph": EXPECTED_TRIPLES,
        "half_sets_per_graph": EXPECTED_HALF_SETS,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

