"""Independent exact replay of the 2943 Pattern-5 row-preservation audit."""

from __future__ import annotations

import importlib.util
from collections import Counter, defaultdict, deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def norm(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def main() -> None:
    lead = load("r29_lead_preservation", LEAD)
    data = lead.build()
    n = data["n"]
    blue = {norm(*edge) for edge in data["blue"]}
    bad = {norm(*edge) for edge in data["bad"]}
    rows = [tuple(row) for row in data["rows"]]
    start = data["selectorStart"]
    for j in range(data["selectorStop"] - start):
        rows[start + j] = tuple(data["selectorMeta"][j]["anchorRow"])

    pair = Counter()
    selected = set()
    support_occurrences = []
    support = set()
    for row in rows:
        selected.update(row)
        for x in row:
            for y in row:
                pair[x, y] += 1
        for x, y in zip(row, row[1:]):
            edge = norm(x, y)
            support_occurrences.append(edge)
            support.add(edge)

    active_edges = {
        edge for edge in blue
        if edge not in support and edge[0] in selected and edge[1] in selected
    }
    active_adj = defaultdict(set)
    for u, v in active_edges:
        active_adj[u].add(v)
        active_adj[v].add(u)

    component = {}
    for root in sorted(selected):
        if root in component:
            continue
        seen = {root}
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v in active_adj[u]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        for v in seen:
            component[v] = root
    active_roots = {
        component[u] for u, v in bad
        if u in component and v in component and component[u] == component[v]
    }
    active_vertices = {v for v in selected if component[v] in active_roots}

    blue_adj = defaultdict(set)
    for u, v in blue:
        blue_adj[u].add(v)
        blue_adj[v].add(u)
    quiet_component = {}
    quiet_sets = []
    for root in range(n):
        if root in active_vertices or root in quiet_component:
            continue
        cid = len(quiet_sets)
        seen = {root}
        quiet_component[root] = cid
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v in blue_adj[u]:
                if v not in active_vertices and v not in quiet_component:
                    quiet_component[v] = cid
                    seen.add(v)
                    queue.append(v)
        quiet_sets.append(seen)

    K = quiet_sets[quiet_component[3]]
    boundary = {
        v for u in K for v in blue_adj[u] if v in active_vertices
    }
    crossing_rows = [row for row in rows if set(row) & K and set(row) - K]
    crossing_support_occurrences = sum(
        (u in K) != (v in K) for u, v in support_occurrences
    )
    crossing_bad = sum((u in K) != (v in K) for u, v in bad)
    crossing_blue = sum((u in K) != (v in K) for u, v in blue)

    assert len(K) == 1379
    assert boundary == {1, 55}
    assert pair[3, 56] == 0
    assert 3 not in active_vertices and 56 not in active_vertices
    assert crossing_blue == 702
    assert crossing_bad == 676
    assert crossing_blue - crossing_bad == 26
    assert len(crossing_rows) == 1014
    assert crossing_support_occurrences == 1352
    assert crossing_rows[0] == (3, 1, 0, 2, 29)

    print({
        "n": n,
        "activeVertices": len(active_vertices),
        "K": len(K),
        "boundary": sorted(boundary),
        "crossingRows": len(crossing_rows),
        "crossingSupportOccurrences": crossing_support_occurrences,
        "crossingBad": crossing_bad,
        "crossingBlue": crossing_blue,
        "sigma": crossing_blue - crossing_bad,
        "firstCrossingRow": crossing_rows[0],
    })


if __name__ == "__main__":
    main()
