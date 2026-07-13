#!/usr/bin/env python3
"""Exhaust ordered linear triple systems and test component sparsity."""

from __future__ import annotations

import argparse
import json


def triangles(edges: tuple[tuple[int, int, int], ...]) -> list[tuple[int, int, int]]:
    ac = {(a, c): i for i, (a, c, _u) in enumerate(edges)}
    au = {(a, u): i for i, (a, _c, u) in enumerate(edges)}
    cu = {(c, u): i for i, (_a, c, u) in enumerate(edges)}
    out = []
    for a, c in ac:
        for u in range(c + 1, max((e[2] for e in edges), default=c) + 1):
            ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
            if None not in ids and len(set(ids)) == 3:
                out.append(ids)
    return out


def maximum_component_excess(edge_count: int, ts: list[tuple[int, int, int]]) -> int:
    parent = list(range(edge_count))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        x, y = find(x), find(y)
        if x != y:
            parent[y] = x

    for t in ts:
        union(t[0], t[1])
        union(t[0], t[2])
    counts: dict[int, list[int]] = {}
    for i in range(edge_count):
        counts.setdefault(find(i), [0, 0])[0] += 1
    for t in ts:
        counts[find(t[0])][1] += 1
    return max((ne - nv for nv, ne in counts.values()), default=0)


def search(n: int) -> dict[str, object]:
    candidates = [(a, c, u) for u in range(n) for c in range(u) for a in range(c + 1)]
    used_ac: set[tuple[int, int]] = set()
    used_au: set[tuple[int, int]] = set()
    used_cu: set[tuple[int, int]] = set()
    chosen: list[tuple[int, int, int]] = []
    systems = 0
    best = (-10**9, None)

    def visit(index: int) -> None:
        nonlocal systems, best
        if index == len(candidates):
            systems += 1
            edge_tuple = tuple(chosen)
            ts = triangles(edge_tuple)
            excess = maximum_component_excess(len(edge_tuple), ts)
            if excess > best[0]:
                best = (excess, {"edges": edge_tuple, "triangles": ts})
            return
        visit(index + 1)
        a, c, u = candidates[index]
        if (a, c) in used_ac or (a, u) in used_au or (c, u) in used_cu:
            return
        used_ac.add((a, c)); used_au.add((a, u)); used_cu.add((c, u))
        chosen.append((a, c, u))
        visit(index + 1)
        chosen.pop()
        used_ac.remove((a, c)); used_au.remove((a, u)); used_cu.remove((c, u))

    visit(0)
    return {"n": n, "systems": systems, "maximum_component_excess": best[0], "witness": best[1]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(search(args.n), indent=2))


if __name__ == "__main__":
    main()
