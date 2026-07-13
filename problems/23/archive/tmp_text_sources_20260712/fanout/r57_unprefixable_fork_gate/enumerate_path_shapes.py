#!/usr/bin/env python3
"""Enumerate exact intersection shapes of two shortest length-four rows.

The rows share ordered endpoints 0 and 4.  The first row is
0-1-2-3-4.  Each internal vertex of the second row is either a distinct
internal vertex of the first row or a fresh vertex.  We retain precisely the
patterns whose union is triangle-free and whose endpoint distance is four.
"""

from __future__ import annotations

from collections import deque
from itertools import combinations, permutations
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def norm_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def graph_of(second_internal: tuple[int, int, int]):
    first = (0, 1, 2, 3, 4)
    second = (0, *second_internal, 4)
    edges = {
        norm_edge(path[i], path[i + 1])
        for path in (first, second)
        for i in range(4)
    }
    vertices = sorted(set(first) | set(second))
    adjacency = {v: set() for v in vertices}
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    return first, second, edges, adjacency


def triangle_free(adjacency: dict[int, set[int]]) -> bool:
    for u, v, w in combinations(adjacency, 3):
        if v in adjacency[u] and w in adjacency[u] and w in adjacency[v]:
            return False
    return True


def distance(adjacency: dict[int, set[int]], source: int, target: int) -> int:
    queue = deque([(source, 0)])
    seen = {source}
    while queue:
        vertex, depth = queue.popleft()
        if vertex == target:
            return depth
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, depth + 1))
    raise AssertionError("disconnected row union")


def all_patterns():
    # A cross-identification is a partial injection from the three internal
    # positions of the second row to the three internal vertices 1,2,3.
    patterns = []
    for identified_count in range(4):
        for second_positions in combinations(range(3), identified_count):
            for first_vertices in permutations((1, 2, 3), identified_count):
                assignment = dict(zip(second_positions, first_vertices))
                # Fresh labels are position-specific, so no two fresh
                # vertices are accidentally identified.
                internal = tuple(assignment.get(position, 5 + position)
                                 for position in range(3))
                first, second, edges, adjacency = graph_of(internal)
                if first == second:
                    continue
                patterns.append(
                    {
                        "secondInternal": internal,
                        "identifiedPositions": list(second_positions),
                        "identifiedVertices": list(first_vertices),
                        "edges": sorted(edges),
                        "triangleFree": triangle_free(adjacency),
                        "endpointDistance": distance(adjacency, 0, 4),
                        "vertexCount": len(adjacency),
                    }
                )
    return patterns


def main() -> int:
    patterns = all_patterns()
    accepted = [
        pattern for pattern in patterns
        if pattern["triangleFree"] and pattern["endpointDistance"] == 4
    ]
    payload = {
        "schema": "R57_TWO_SHORTEST_ROWS_SHAPE_ENUM_V1",
        "rawDistinctPatterns": len(patterns),
        "triangleFreeDistanceFourPatterns": len(accepted),
        "accepted": accepted,
    }
    result = HERE / "path_shapes.json"
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    result.write_text(encoded, encoding="utf-8")
    digest = hashlib.sha256(result.read_bytes()).hexdigest().upper()
    print(json.dumps({
        "raw": len(patterns),
        "accepted": len(accepted),
        "sha256": digest,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
