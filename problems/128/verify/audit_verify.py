#!/usr/bin/env python3
"""Independent exact verifier for an Erdos Problem 128 n=20 certificate."""

from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

N = 20
HALF_SIZE = 10
REQUIRED_HALF_EDGES = 9
EXPECTED_TRIPLES = 1140
EXPECTED_HALF_SETS = 184756


class AdjacencyError(ValueError):
    pass


def _coerce_rows(raw: Any) -> list[Any]:
    if isinstance(raw, dict) and ("adjacency" in raw or "adjacency_list" in raw):
        raw = raw.get("adjacency", raw.get("adjacency_list"))
    if isinstance(raw, dict):
        converted: dict[int, Any] = {}
        for key, value in raw.items():
            if isinstance(key, bool):
                raise AdjacencyError("Boolean vertex label is forbidden")
            try:
                vertex = int(key)
            except (TypeError, ValueError) as exc:
                raise AdjacencyError(f"Invalid vertex label: {key!r}") from exc
            if str(vertex) != str(key) and not isinstance(key, int):
                raise AdjacencyError(f"Non-canonical vertex label: {key!r}")
            if vertex in converted:
                raise AdjacencyError(f"Duplicate vertex row: {vertex}")
            converted[vertex] = value
        if set(converted) != set(range(N)):
            raise AdjacencyError("Rows must be labelled by every integer 0..19")
        return [converted[v] for v in range(N)]
    if not isinstance(raw, list) or len(raw) != N:
        raise AdjacencyError("Adjacency must contain exactly 20 rows")
    return raw


def normalize_adjacency(raw: Any) -> tuple[frozenset[int], ...]:
    rows = _coerce_rows(raw)
    adjacency: list[frozenset[int]] = []
    for vertex, row in enumerate(rows):
        if not isinstance(row, (list, tuple, set, frozenset)):
            raise AdjacencyError(f"Row {vertex} is not a neighbour sequence")
        neighbours: list[int] = []
        for item in row:
            if isinstance(item, bool) or not isinstance(item, int):
                raise AdjacencyError(f"Row {vertex} has non-integer neighbour {item!r}")
            if not 0 <= item < N:
                raise AdjacencyError(f"Row {vertex} has out-of-range neighbour {item}")
            neighbours.append(item)
        if len(neighbours) != len(set(neighbours)):
            raise AdjacencyError(f"Row {vertex} contains a duplicate neighbour")
        if vertex in neighbours:
            raise AdjacencyError(f"Loop at vertex {vertex}")
        adjacency.append(frozenset(neighbours))
    for u in range(N):
        for v in adjacency[u]:
            if u not in adjacency[v]:
                raise AdjacencyError(f"Asymmetric edge declaration {u}-{v}")
    return tuple(adjacency)


def _parse_plain(text: str) -> list[list[int]]:
    rows: dict[int, list[int]] = {}
    for line_number, original in enumerate(text.splitlines(), start=1):
        line = original.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            raise AdjacencyError(f"Line {line_number} has no ':' separator")
        left, right = line.split(":", 1)
        try:
            vertex = int(left.strip())
        except ValueError as exc:
            raise AdjacencyError(f"Line {line_number} has invalid vertex label") from exc
        if vertex in rows:
            raise AdjacencyError(f"Duplicate row for vertex {vertex}")
        rows[vertex] = [int(token) for token in re.findall(r"-?\d+", right)]
    return _coerce_rows(rows)


def load_adjacency(path: Path) -> tuple[frozenset[int], ...]:
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if not stripped:
        raise AdjacencyError("Input file is empty")
    if stripped[0] in "[{":
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise AdjacencyError(f"Invalid JSON: {exc}") from exc
    else:
        raw = _parse_plain(text)
    return normalize_adjacency(raw)


def canonical_sha256(adjacency: Sequence[Iterable[int]]) -> str:
    payload = json.dumps(
        [sorted(row) for row in adjacency], separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def audit(adjacency: Sequence[frozenset[int]]) -> dict[str, Any]:
    if len(adjacency) != N:
        raise AdjacencyError("Internal audit input does not have 20 rows")
    edge_count = sum(len(row) for row in adjacency) // 2

    triangle_count = 0
    first_triangles: list[list[int]] = []
    triple_count = 0
    for a, b, c in itertools.combinations(range(N), 3):
        triple_count += 1
        if b in adjacency[a] and c in adjacency[a] and c in adjacency[b]:
            triangle_count += 1
            if len(first_triangles) < 8:
                first_triangles.append([a, b, c])

    histogram: Counter[int] = Counter()
    minimum = 46
    maximum = -1
    minimizers: list[list[int]] = []
    violating_half_sets = 0
    half_set_count = 0
    for chosen in itertools.combinations(range(N), HALF_SIZE):
        half_set_count += 1
        induced_edges = 0
        for i in range(HALF_SIZE):
            u = chosen[i]
            for j in range(i + 1, HALF_SIZE):
                if chosen[j] in adjacency[u]:
                    induced_edges += 1
        histogram[induced_edges] += 1
        if induced_edges < REQUIRED_HALF_EDGES:
            violating_half_sets += 1
        if induced_edges < minimum:
            minimum = induced_edges
            minimizers = [list(chosen)]
        elif induced_edges == minimum and len(minimizers) < 8:
            minimizers.append(list(chosen))
        maximum = max(maximum, induced_edges)

    if triple_count != EXPECTED_TRIPLES:
        raise AssertionError(f"Enumerated {triple_count} triples, expected 1140")
    if half_set_count != EXPECTED_HALF_SETS:
        raise AssertionError(f"Enumerated {half_set_count} half-sets, expected 184756")

    triangle_free = triangle_count == 0
    half_condition = minimum >= REQUIRED_HALF_EDGES
    return {
        "n": N,
        "edge_count": edge_count,
        "triangle_triples_checked": triple_count,
        "triangle_count": triangle_count,
        "first_triangles": first_triangles,
        "triangle_free": triangle_free,
        "half_sets_checked": half_set_count,
        "minimum_half_edges": minimum,
        "maximum_half_edges": maximum,
        "violating_half_sets_below_9": violating_half_sets,
        "first_minimizing_half_sets": minimizers,
        "half_edge_histogram": {str(k): histogram[k] for k in sorted(histogram)},
        "half_condition_at_least_9": half_condition,
        "certificate_sha256": canonical_sha256(adjacency),
        "passes_problem_128_n20": triangle_free and half_condition,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit a JSON or 'v: neighbours' adjacency list on vertices 0..19."
    )
    parser.add_argument("adjacency_list", type=Path)
    args = parser.parse_args(argv)
    try:
        result = audit(load_adjacency(args.adjacency_list))
    except (AdjacencyError, OSError) as exc:
        print(json.dumps({"input_valid": False, "error": str(exc)}))
        return 2
    result["input_valid"] = True
    result["verifier_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["passes_problem_128_n20"] else 1


if __name__ == "__main__":
    sys.exit(main())
