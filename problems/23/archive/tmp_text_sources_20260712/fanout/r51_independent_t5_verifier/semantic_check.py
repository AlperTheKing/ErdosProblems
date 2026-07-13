#!/usr/bin/env python3
"""Direct graph-semantic checker for rooted t=5 support edge sets."""

from __future__ import annotations

from collections import deque


V, M, A, B = 0, 1, 2, 3
X, Y = 0, 1


def check_support(
    left_n: int,
    right_n: int,
    edges: list[list[int]] | list[tuple[int, int]],
    require_connected: bool,
) -> dict:
    edge_set = {(int(u), int(r)) for u, r in edges}
    if len(edge_set) != len(edges):
        raise AssertionError("duplicate support edge")
    if any(not (0 <= u < left_n and 0 <= r < right_n) for u, r in edge_set):
        raise AssertionError("support edge outside shore range")

    mandatory = {(A, X), (V, X), (M, X), (V, Y), (M, Y), (B, Y)}
    if not mandatory <= edge_set:
        raise AssertionError("mandatory rooted row edge missing")
    if len(edge_set) != 24:
        raise AssertionError("support does not have 24 edges")

    n = left_n + right_n
    adj = [set() for _ in range(n)]
    for u, r in edge_set:
        z = left_n + r
        adj[u].add(z)
        adj[z].add(u)
    if len(adj[V]) != 5 or len(adj[M]) != 5:
        raise AssertionError("root owner degree is not five")
    if any(not neighbours for neighbours in adj):
        raise AssertionError("isolated support vertex")

    def distances(source: int) -> list[int | None]:
        out: list[int | None] = [None] * n
        out[source] = 0
        queue = deque([source])
        while queue:
            z = queue.popleft()
            assert out[z] is not None
            for w in adj[z]:
                if out[w] is None:
                    out[w] = out[z] + 1
                    queue.append(w)
        return out

    all_dist = [distances(z) for z in range(n)]
    connected = all(d is not None for d in all_dist[V])
    if require_connected and not connected:
        raise AssertionError("support is disconnected")

    if all_dist[A][B] != 4:
        raise AssertionError("rooted bad pair A,B is not at distance four")
    v_d4 = sum(all_dist[V][u] == 4 for u in range(left_n) if u != V)
    m_d4 = sum(all_dist[M][u] == 4 for u in range(left_n) if u != M)
    if v_d4 < 5 or m_d4 < 5:
        raise AssertionError("root owner has fewer than five distance-four atoms")

    total_d4 = 0
    for shore in (range(left_n), range(left_n, n)):
        vertices = list(shore)
        for i, u in enumerate(vertices):
            for w in vertices[i + 1 :]:
                total_d4 += all_dist[u][w] == 4
    if total_d4 < 25:
        raise AssertionError("fewer than 25 same-shore distance-four atoms")

    return {
        "edgeCount": len(edge_set),
        "connected": connected,
        "rootDegrees": [len(adj[V]), len(adj[M])],
        "rootDistanceFourCounts": [v_d4, m_d4],
        "totalDistanceFourAtoms": total_d4,
    }
