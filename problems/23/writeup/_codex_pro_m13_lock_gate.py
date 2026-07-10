"""Exact audit of GPT-5.6-Pro's 58-vertex m=13 lock extension.

The lock does make the displayed cut globally maximum, but the official
vertex-slack capacity uses ambient N=58, not core size 13.  This script checks
both claims with integer/Fraction arithmetic.
"""

from fractions import Fraction as F
from collections import deque


CORE_N = 13
SUPPORT = [
    (0, 9), (1, 9), (2, 10), (3, 10), (0, 11), (4, 11),
    (5, 11), (0, 12), (2, 12), (6, 12), (7, 12), (8, 12),
]
INTERNAL = (1, 10)
BAD = [
    (1, 4), (1, 5), (2, 4), (2, 5), (3, 6), (3, 7), (3, 8),
    (4, 6), (4, 7), (4, 8), (5, 6), (5, 7), (5, 8),
]
Q = (1, 1, 2, 2, 5, 4, 2, 3, 2)


def crossed(edge, mask):
    u, v = edge
    return ((mask >> u) ^ (mask >> v)) & 1


def build():
    anchor = CORE_N
    next_vertex = anchor + 1
    blue = list(SUPPORT) + [INTERNAL]
    paths = []
    for v, count in enumerate(Q):
        for _ in range(count):
            x, y = next_vertex, next_vertex + 1
            next_vertex += 2
            path = ((v, x), (x, y), (y, anchor))
            paths.append(path)
            blue.extend(path)
    n = next_vertex
    side = [0] * n
    for v in (9, 10, 11, 12, anchor):
        side[v] = 1
    for path in paths:
        _, x = path[0]
        _, y = path[1]
        side[x], side[y] = 1, 0
    return n, blue, list(BAD), side, paths


def bfs(adj, source):
    dist = [-1] * len(adj)
    dist[source] = 0
    queue = deque([source])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1
                queue.append(y)
    return dist


def main():
    n, blue, bad, side, paths = build()
    edges = blue + bad
    adj = [set() for _ in range(n)]
    blue_adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for u, v in blue:
        blue_adj[u].add(v)
        blue_adj[v].add(u)

    triangle_free = all(not (adj[u] & adj[v]) for u, v in edges)
    displayed_cut = sum(side[u] != side[v] for u, v in edges)
    displayed_bad = len(edges) - displayed_cut

    best_lock_gap = -10**9
    best_mask = 0
    for mask in range(1 << CORE_N):
        core_gain = sum(crossed(e, mask) for e in bad)
        core_gain -= sum(crossed(e, mask) for e in SUPPORT + [INTERNAL])
        lock_loss = sum(Q[v] for v in range(9) if (mask >> v) & 1)
        gap = core_gain - lock_loss
        if gap > best_lock_gap:
            best_lock_gap, best_mask = gap, mask

    distances = [bfs(blue_adj, v) for v in range(CORE_N)]
    ell5 = all(distances[u][v] == 4 for u, v in bad)
    internal_used = False
    for u, v in bad:
        du, dv = distances[u], distances[v]
        a, b = INTERNAL
        internal_used |= (du[a] + 1 + dv[b] == 4 or du[b] + 1 + dv[a] == 4)

    rows_through_10 = 0
    for u, v in bad:
        if distances[u][10] + distances[10][v] == 4:
            rows_through_10 += 1
    t10 = 5 * rows_through_10
    official_cap = max(F(0), F(n - t10))
    internal_load = F(1, 2)

    result = {
        "N": n,
        "edges": len(edges),
        "blue": len(blue),
        "bad": len(bad),
        "displayedCut": displayed_cut,
        "displayedBad": displayed_bad,
        "triangleFree": triangle_free,
        "allCoreBadEll5": ell5,
        "internalEdgeOnShortestRow": internal_used,
        "maxCoreGainMinusLockLoss": best_lock_gap,
        "maximizingCoreMask": best_mask,
        "displayedCutIsGlobalMaximum": best_lock_gap == 0,
        "T10": t10,
        "coreSize": CORE_N,
        "officialAmbientVertexSlackCap10": str(official_cap),
        "internalLoad10": str(internal_load),
        "officialMargin10": str(official_cap - internal_load),
        "incorrectCoreSizeMargin10": str(max(F(0), F(CORE_N - t10)) - internal_load),
    }
    print(result)
    assert n == 58 and len(edges) == 92
    assert triangle_free and ell5 and not internal_used
    assert displayed_cut == 79 and displayed_bad == 13 and best_lock_gap == 0
    assert official_cap - internal_load == F(85, 2)


if __name__ == "__main__":
    main()
