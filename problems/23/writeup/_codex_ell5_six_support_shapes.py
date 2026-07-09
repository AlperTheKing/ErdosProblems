"""Exact six-support shape gate for the T7 no-six-support hinge.

A full ell=5 geodesic support of cardinality 6 contains two distinct simple
length-4 geodesics between the same endpoints whose edge-union already has
cardinality 6 (by the compiled T6 union lower bound).  This script enumerates
all such two-geodesic union shapes on labelled vertices and checks the property
needed by the size-seven obstruction bridge:

  no distance-four endpoint pair has a full shortest-geodesic support of
  cardinality 4 contained in that same six-edge support.

The enumeration is labelled but finite/exact; canonicalization is unnecessary
for soundness because every labelled overlap pattern is checked.  The summary
also reports the number of distinct edge-set shapes encountered.
"""

from __future__ import annotations

import json
from collections import deque
from itertools import combinations, product
from pathlib import Path


def norm_edge(a: int, b: int) -> tuple[int, int]:
    if a == b:
        raise ValueError("loop")
    return (a, b) if a < b else (b, a)


def path_edges(path: tuple[int, ...] | list[int]) -> frozenset[tuple[int, int]]:
    return frozenset(norm_edge(path[i], path[i + 1]) for i in range(len(path) - 1))


def shortest_simple_paths(adj: dict[int, set[int]], u: int, v: int) -> tuple[int | None, list[list[int]]]:
    q: deque[tuple[int, list[int]]] = deque([(u, [u])])
    best: int | None = None
    out: list[list[int]] = []
    while q:
        x, path = q.popleft()
        d = len(path) - 1
        if best is not None and d > best:
            continue
        if x == v:
            best = d
            out.append(path)
            continue
        for y in sorted(adj[x]):
            if y in path:
                continue
            nd = d + 1
            if best is not None and nd > best:
                continue
            q.append((y, path + [y]))
    return best, out


def is_bipartite(vertices: set[int], edges: frozenset[tuple[int, int]]) -> bool:
    adj = {v: set() for v in vertices}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    color: dict[int, int] = {}
    for s in sorted(vertices):
        if s in color:
            continue
        color[s] = 0
        stack = [s]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in color:
                    color[y] = 1 - color[x]
                    stack.append(y)
                elif color[y] == color[x]:
                    return False
    return True


def analyze_shape(edges: frozenset[tuple[int, int]]) -> dict:
    vertices = set()
    for a, b in edges:
        vertices.add(a)
        vertices.add(b)
    adj = {v: set() for v in vertices}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    dist4 = []
    bad_four = []
    for u, v in combinations(sorted(vertices), 2):
        d, paths = shortest_simple_paths(adj, u, v)
        if d != 4:
            continue
        supp = frozenset().union(*(path_edges(p) for p in paths))
        rec = {
            "pair": [u, v],
            "support_size": len(supp),
            "support": [list(e) for e in sorted(supp)],
            "path_count": len(paths),
        }
        dist4.append(rec)
        if len(supp) == 4 and supp <= edges:
            bad_four.append(rec)
    return {"dist4": dist4, "bad_four": bad_four}


def main() -> int:
    base = (0, 1, 2, 3, 4)
    base_edges = path_edges(base)
    labels = range(8)
    checked_labelled = 0
    accepted_labelled = 0
    shapes: dict[tuple[tuple[int, int], ...], dict] = {}
    failures = []

    for middle in product(labels, repeat=3):
        q = (0,) + middle + (4,)
        if len(set(q)) != 5:
            continue
        q_edges = path_edges(q)
        if q_edges == base_edges:
            continue
        union = frozenset(base_edges | q_edges)
        if len(union) != 6:
            continue
        checked_labelled += 1
        vertices = {x for e in union for x in e}
        if not is_bipartite(vertices, union):
            continue
        accepted_labelled += 1
        key = tuple(sorted(union))
        if key not in shapes:
            analysis = analyze_shape(union)
            shapes[key] = {
                "edges": [list(e) for e in key],
                "analysis": analysis,
            }
            if analysis["bad_four"]:
                failures.append(shapes[key])

    summary = {
        "checked_labelled_unions": checked_labelled,
        "accepted_bipartite_labelled_unions": accepted_labelled,
        "distinct_labelled_edge_sets": len(shapes),
        "failure_count": len(failures),
        "failures": failures,
        "shapes": list(shapes.values()),
    }
    out = Path("tmp/codex_ell5_six_support_shapes.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in summary if k not in {"shapes", "failures"}}, indent=2))
    print(f"wrote {out}")
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
