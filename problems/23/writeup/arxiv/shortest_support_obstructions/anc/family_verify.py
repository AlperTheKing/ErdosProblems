"""Exact verifier for the layered shortest-support Hall counterexample family.

For every t >= 1, G_t has seven independent t-classes
L,A,B,C,D,E,R, three singleton vertices u,w,v, and edges:
  L-R;
  every consecutive complete block of L-A-B-C-D-E-R;
  L-u, u-w, w-v, v-R.
The script checks the structural certificate for t=1..max_t and independently
optimizes every cut over twin-class cardinalities for t<=exact_max_t.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from itertools import product
from math import comb


def construct(t: int):
    assert t >= 1
    classes = {}
    for k, name in enumerate(("L", "A", "B", "C", "D", "E", "R")):
        classes[name] = tuple(range(k * t, (k + 1) * t))
    u, w, v = 7 * t, 7 * t + 1, 7 * t + 2

    edges = set()

    def add(x: int, y: int) -> None:
        edges.add((x, y) if x < y else (y, x))

    def complete(xs, ys) -> None:
        for x in xs:
            for y in ys:
                add(x, y)

    complete(classes["L"], classes["R"])
    names = ("L", "A", "B", "C", "D", "E", "R")
    for x, y in zip(names, names[1:]):
        complete(classes[x], classes[y])
    for x in classes["L"]:
        add(x, u)
    add(u, w)
    add(w, v)
    for y in classes["R"]:
        add(v, y)

    return classes, (u, w, v), frozenset(edges)


def edge(x: int, y: int):
    return (x, y) if x < y else (y, x)


def triangle_count(n: int, edges) -> int:
    adj = [set() for _ in range(n)]
    for x, y in edges:
        adj[x].add(y)
        adj[y].add(x)
    total = 0
    for x in range(n):
        for y in adj[x]:
            if x < y:
                total += len(adj[x] & adj[y])
    return total // 3


def packed_cycles(t: int, classes):
    L, A, B = classes["L"], classes["A"], classes["B"]
    C, D, E, R = classes["C"], classes["D"], classes["E"], classes["R"]
    out = []
    for i in range(t):
        for j in range(t):
            out.append((
                L[i], A[j], B[(i + j) % t], C[i],
                D[j], E[(i + j) % t], R[j], L[i],
            ))
    return tuple(out)


def shortest_support(s: int, target: int, blue_edges, n: int):
    adj = [set() for _ in range(n)]
    for x, y in blue_edges:
        adj[x].add(y)
        adj[y].add(x)

    def bfs(root: int):
        dist = [-1] * n
        dist[root] = 0
        queue = deque([root])
        while queue:
            x = queue.popleft()
            for y in adj[x]:
                if dist[y] < 0:
                    dist[y] = dist[x] + 1
                    queue.append(y)
        return dist

    ds, dt = bfs(s), bfs(target)
    distance = ds[target]
    support = {
        edge(x, y)
        for x, y in blue_edges
        if (
            ds[x] + 1 + dt[y] == distance
            or ds[y] + 1 + dt[x] == distance
        )
    }

    ordered = sorted(range(n), key=lambda x: ds[x])
    count = [0] * n
    count[s] = 1
    for x in ordered:
        if ds[x] < 0:
            continue
        for y in adj[x]:
            if ds[y] == ds[x] + 1:
                count[y] += count[x]
    return distance, frozenset(support), count[target]


def exact_cut_optimization(t: int, target: int):
    best = -1
    number = 0
    patterns = 0
    for xs in product(range(t + 1), repeat=7):
        web = sum(
            x * (t - y) + (t - x) * y
            for x, y in zip(xs, xs[1:])
        )
        left, right = xs[0], xs[-1]
        direct = left * (t - right) + (t - left) * right
        multiplicity = 1
        for x in xs:
            multiplicity *= comb(t, x)

        for u, w, v in product((0, 1), repeat=3):
            thin = (
                left * (1 - u) + (t - left) * u
                + (u != w) + (w != v)
                + right * (1 - v) + (t - right) * v
            )
            value = web + direct + thin
            if value > best:
                best = value
                number = multiplicity
                patterns = 1
            elif value == best:
                number += multiplicity
                patterns += 1
    assert best == target
    assert number == 2
    assert patterns == 2
    return {"best": best, "numberOfCuts": number, "countPatterns": patterns}


def verify(t: int, exact: bool):
    classes, (u, w, v), edges = construct(t)
    n = 7 * t + 3
    assert len(edges) == 7 * t * t + 2 * t + 2
    assert triangle_count(n, edges) == 0

    cycles = packed_cycles(t, classes)
    used = set()
    for cycle in cycles:
        assert len(cycle) == 8 and cycle[0] == cycle[-1]
        cycle_edges = {edge(cycle[k], cycle[k + 1]) for k in range(7)}
        assert len(cycle_edges) == 7
        assert cycle_edges <= edges
        assert used.isdisjoint(cycle_edges)
        used |= cycle_edges
    assert len(cycles) == t * t
    assert len(used) == 7 * t * t

    shore0 = set(classes["L"] + classes["B"] + classes["D"] + classes["R"] + (w,))
    bad = {e for e in edges if (e[0] in shore0) == (e[1] in shore0)}
    direct = {edge(x, y) for x in classes["L"] for y in classes["R"]}
    assert bad == direct

    maxcut = len(edges) - t * t
    assert maxcut == 6 * t * t + 2 * t + 2
    blue = edges - bad

    support_union = set()
    for x in classes["L"]:
        for y in classes["R"]:
            distance, support, paths = shortest_support(x, y, blue, n)
            assert distance == 4
            assert paths == 1
            expected = frozenset((edge(x, u), edge(u, w), edge(w, v), edge(v, y)))
            assert support == expected
            support_union |= support

    assert len(support_union) == 2 * t + 2
    result = {
        "t": t,
        "vertices": n,
        "edges": len(edges),
        "packedEdgeDisjointOddCycles": len(cycles),
        "bipartization": t * t,
        "maxcut": maxcut,
        "maximumCutsModuloComplement": 1,
        "badEdges": len(bad),
        "shortestSupportUnion": len(support_union),
        "hallDefect": t * t - (2 * t + 2),
    }
    if exact:
        result["exactTwinCountOptimization"] = exact_cut_optimization(t, maxcut)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-t", type=int, default=8)
    parser.add_argument("--exact-max-t", type=int, default=5)
    args = parser.parse_args()
    rows = [verify(t, t <= args.exact_max_t) for t in range(1, args.max_t + 1)]
    print(json.dumps(rows, sort_keys=True, indent=2))
    assert all(row["hallDefect"] > 0 for row in rows if row["t"] >= 3)
    print("PASS_LAYERED_SHORTEST_SUPPORT_FAMILY")


if __name__ == "__main__":
    main()

