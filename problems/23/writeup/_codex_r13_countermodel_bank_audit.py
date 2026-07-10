"""Exact audit of GPT-Pro R13's 13-vertex Horn countermodel.

The graph/max-cut/D1 claims are checked exactly.  We then recompute the
canonical selected ell=5 core from the unique shortest P4 row and evaluate the
existing half-block cover.  This distinguishes an abstract full-row wall from
the actual cage boundary/own-Door semantics.
"""

from __future__ import annotations

import hashlib
import json
from collections import deque
from fractions import Fraction


NAMES = ("x", "a", "b", "c", "y", "r1", "r2", "u", "v", "r3", "xo", "yo", "bo")
ID = {name: i for i, name in enumerate(NAMES)}


def edge(a: str, b: str) -> tuple[int, int]:
    u, v = ID[a], ID[b]
    return (u, v) if u < v else (v, u)


P4 = ("x", "a", "b", "c", "y")
P6 = ("x", "r1", "r2", "u", "v", "r3", "y")
BLUE = {
    *(edge(P4[i], P4[i + 1]) for i in range(4)),
    *(edge(P6[i], P6[i + 1]) for i in range(6)),
    edge("x", "xo"), edge("y", "yo"), edge("b", "bo"),
}
BAD = {edge("x", "y")}
EDGES = BLUE | BAD
CORE = {ID[x] for x in P4}
SHORT = {edge(P4[i], P4[i + 1]) for i in range(4)}


def adjacency(edges):
    adj = [set() for _ in NAMES]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def bfs(adj, source):
    dist = [-1] * len(adj)
    dist[source] = 0
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


def main():
    full_adj = adjacency(EDGES)
    assert all(not (full_adj[u] & full_adj[v]) for u, v in EDGES)

    cut_values = []
    for mask in range(1 << len(NAMES)):
        cut_values.append(sum(((mask >> u) ^ (mask >> v)) & 1 for u, v in EDGES))
    assert max(cut_values) == 13

    blue_adj = adjacency(BLUE)
    x, y = ID["x"], ID["y"]
    assert bfs(blue_adj, x)[y] == 4

    # Exact D1 over the 10 non-leaf wall vertices.
    wall_vertices = [ID[name] for name in NAMES[:10]]
    p6_edges = [edge(P6[i], P6[i + 1]) for i in range(6)]
    d1_slacks = []
    for mask in range(1 << len(wall_vertices)):
        shore = {wall_vertices[i] for i in range(len(wall_vertices)) if (mask >> i) & 1}
        atom_cross = int((x in shore) ^ (y in shore))
        port_cross = sum(int((u in shore) ^ (v in shore)) for u, v in p6_edges)
        slack = Fraction(port_cross - atom_cross, 13)
        assert slack >= 0
        d1_slacks.append(slack)

    # Canonical singleton/block loads for the actual P4 support core.
    loads = {}
    for e in BLUE - SHORT:
        u, v = e
        count = int(u in CORE) + int(v in CORE)
        loads[e] = Fraction(count, 2)
    positive = {e: q for e, q in loads.items() if q > 0}
    boundary = {e for e in BLUE if (e[0] in CORE) ^ (e[1] in CORE)}
    internal = {e for e in BLUE - SHORT if e[0] in CORE and e[1] in CORE}
    assert not internal
    assert set(positive) == boundary
    assert all(q == Fraction(1, 2) for q in positive.values())

    # Of Pro's six P6 gamma coordinates, only the two terminal P6 edges are
    # actual core-boundary exits.  Unit own Doors already overpay alpha.
    p6_boundary = [e for e in p6_edges if e in boundary]
    assert len(p6_boundary) == 2
    alpha = Fraction(1, 13)
    actual_door_penalty = len(p6_boundary) * Fraction(1, 13)
    strict_gap_upper = alpha - actual_door_penalty
    assert strict_gap_upper < 0

    payload = "".join(
        f"{NAMES[u]} {NAMES[v]} {positive[(u, v)]}\n" for u, v in sorted(positive)
    )
    print(json.dumps({
        "vertices": len(NAMES),
        "edges": len(EDGES),
        "triangleFree": True,
        "maxCut": max(cut_values),
        "distanceXY": 4,
        "d1RowsChecked": len(d1_slacks),
        "minD1Slack": str(min(d1_slacks)),
        "canonicalCoreVertices": sorted(NAMES[v] for v in CORE),
        "canonicalShortEdges": len(SHORT),
        "internalOffSupport": [],
        "positiveBoundaryLoads": {
            f"{NAMES[u]}-{NAMES[v]}": str(q) for (u, v), q in sorted(positive.items())
        },
        "p6Coordinates": len(p6_edges),
        "p6ActualBoundaryCoordinates": [f"{NAMES[u]}-{NAMES[v]}" for u, v in p6_boundary],
        "strictGapClaimWithZeroCaps": "1/13",
        "strictGapUpperWithActualUnitOwnDoors": str(strict_gap_upper),
        "boundaryLoadSHA256": hashlib.sha256(payload.encode("ascii")).hexdigest(),
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
