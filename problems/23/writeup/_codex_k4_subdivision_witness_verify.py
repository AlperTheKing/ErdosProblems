"""Independent exact verifier for the first K4-subdivision obstruction."""

from __future__ import annotations

import json
from collections import deque


G6 = "Mo_Gj@?CH??@?@C?_"
DEMANDS = (
    (0, 3), (0, 12), (1, 6), (1, 11), (1, 13), (2, 6),
    (2, 9), (2, 13), (3, 7), (3, 10), (4, 9), (4, 11),
    (4, 13), (5, 7), (5, 8), (5, 10), (5, 12),
)


def decode_graph6(encoded: str) -> tuple[int, tuple[tuple[int, int], ...]]:
    values = [ord(char) - 63 for char in encoded]
    n = values[0]
    bits = []
    for value in values[1:]:
        bits.extend((value >> bit) & 1 for bit in range(5, -1, -1))
    edges = []
    index = 0
    for v in range(1, n):
        for u in range(v):
            if bits[index]:
                edges.append((u, v))
            index += 1
    return n, tuple(edges)


def distances(n: int, edges: tuple[tuple[int, int], ...], start: int) -> list[int]:
    adjacency = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
    distance = [-1] * n
    distance[start] = 0
    queue = deque([start])
    while queue:
        u = queue.popleft()
        for v in adjacency[u]:
            if distance[v] < 0:
                distance[v] = distance[u] + 1
                queue.append(v)
    return distance


def main() -> None:
    n, edges = decode_graph6(G6)
    edge_index = {edge: index for index, edge in enumerate(edges)}
    all_distances = [distances(n, edges, u) for u in range(n)]

    supports = []
    for u, v in DEMANDS:
        assert all_distances[u][v] == 4
        support = set()
        for x, y in edges:
            if (all_distances[u][x] + 1 + all_distances[y][v] == 4 or
                    all_distances[u][y] + 1 + all_distances[x][v] == 4):
                support.add(edge_index[(x, y)])
        supports.append(support)

    demand_adjacency = [set() for _ in range(n)]
    for u, v in DEMANDS:
        assert v not in demand_adjacency[u]
        assert not (demand_adjacency[u] & demand_adjacency[v])
        demand_adjacency[u].add(v)
        demand_adjacency[v].add(u)

    multiplicities = [sum(index in support for support in supports)
                      for index in range(len(edges))]
    assert len(edges) == 16
    assert len(DEMANDS) == len(edges) + 1 == 17
    assert min(multiplicities) >= 2
    assert set().union(*supports) == set(range(len(edges)))

    degrees = [0] * n
    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        degrees[u] += 1
        degrees[v] += 1
        adjacency[u].add(v)
        adjacency[v].add(u)
    assert sorted(vertex for vertex, degree in enumerate(degrees) if degree == 3) == [0, 1, 2, 3]
    assert all(degree in (2, 3) for degree in degrees)

    branch_vertices = {0, 1, 2, 3}
    contracted_paths: dict[tuple[int, int], frozenset[tuple[int, int]]] = {}
    for start in sorted(branch_vertices):
        for first in sorted(adjacency[start]):
            previous, current = start, first
            path_edges = {tuple(sorted((previous, current)))}
            while current not in branch_vertices:
                choices = adjacency[current] - {previous}
                assert len(choices) == 1
                following = next(iter(choices))
                previous, current = current, following
                edge = tuple(sorted((previous, current)))
                assert edge not in path_edges
                path_edges.add(edge)
            if start < current:
                key = (start, current)
                assert key not in contracted_paths
                contracted_paths[key] = frozenset(path_edges)

    expected_branch_edges = set(
        (u, v) for u in range(4) for v in range(u + 1, 4)
    )
    assert set(contracted_paths) == expected_branch_edges
    all_path_edges = set().union(*contracted_paths.values())
    assert all_path_edges == set(edges)
    assert sum(len(path) for path in contracted_paths.values()) == len(edges)

    print(json.dumps({
        "g6": G6,
        "vertices": n,
        "supplyEdges": len(edges),
        "atoms": len(DEMANDS),
        "allAtomDistances": 4,
        "demandTriangleFree": True,
        "supportUnionAllEdges": True,
        "minimumSupplyMultiplicity": min(multiplicities),
        "maximumSupplyMultiplicity": max(multiplicities),
        "branchVertices": sorted(branch_vertices),
        "contractedBranchEdges": sorted(contracted_paths),
        "k4Subdivision": True,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
