"""Exact gluing guardrail for the global active-scoped owner flow.

Two copies of the order-10 scoped Hall failure are joined by a three-edge
blue path whose internal vertices lie outside every selected row.  Although
each copy fails alone, cross-component free-pair sources heal the combined
owner flow exactly.  Thus naive disjoint gluing is not a counterexample to the
global absorbing-row implication.
"""

from __future__ import annotations

import json
from collections import deque

from _codex_r19_global_base_census import dec, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_outside_attachment_full_obligation_gate import (
    active_scoped_obligation_score,
    full_owner_flow,
)


BASE_GRAPH6 = "I?`fBO]]?"
BASE_CHOICE = (1, 1, 1)
SHIFT = 10
N = 22


def norm_edge(x, y):
    return (x, y) if x < y else (y, x)


def shifted_edge(edge, shift):
    return norm_edge(edge[0] + shift, edge[1] + shift)


def shifted_row(row, shift):
    return tuple(x + shift for x in row)


def adjacency(edges):
    out = [set() for _ in range(N)]
    for x, y in edges:
        out[x].add(y)
        out[y].add(x)
    return out


def all_shortest_paths(edges, source, target):
    adj = adjacency(edges)
    distance = [None] * N
    distance[source] = 0
    queue = deque([source])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if distance[y] is None:
                distance[y] = distance[x] + 1
                queue.append(y)
    assert distance[target] is not None
    paths = []

    def visit(path):
        x = path[-1]
        if x == target:
            paths.append(tuple(path))
            return
        for y in sorted(adj[x]):
            if distance[y] == distance[x] + 1 and distance[y] <= distance[target]:
                visit(path + [y])

    visit([source])
    return paths


def connected(edges):
    adj = adjacency(edges)
    seen = {0}
    queue = deque([0])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                queue.append(y)
    return len(seen) == N


def triangle_free(edges):
    adj = adjacency(edges)
    return not any(
        y in adj[x]
        for x in range(N)
        for y in adj[x]
        for z in adj[x] & adj[y]
        if z != x and z != y
    )


def max_cut_size(n, edges):
    best = 0
    for mask in range(1 << (n - 1)):
        cut = sum(
            (((mask >> (x - 1)) & 1) if x else 0)
            != (((mask >> (y - 1)) & 1) if y else 0)
            for x, y in edges
        )
        best = max(best, cut)
    return best


def main() -> int:
    base_n, base_edges = dec(BASE_GRAPH6)
    assert base_n == SHIFT
    info = loads(base_n, base_edges)
    assert info is not None
    families = shortest_row_families(info)
    first_rows = tuple(
        families[i][BASE_CHOICE[i]] for i in range(len(BASE_CHOICE))
    )
    second_rows = tuple(shifted_row(row, SHIFT) for row in first_rows)
    rows = first_rows + second_rows

    blue = set(info["Bset"])
    blue |= {shifted_edge(edge, SHIFT) for edge in info["Bset"]}
    blue |= {(0, 20), (20, 21), (11, 21)}
    bad = set(info["Mset"])
    bad |= {shifted_edge(edge, SHIFT) for edge in info["Mset"]}
    graph = blue | bad

    assert connected(blue)
    assert triangle_free(graph)
    assert max_cut_size(base_n, set(info["Bset"]) | set(info["Mset"])) == len(info["Bset"])
    assert len(blue) == 2 * len(info["Bset"]) + 3
    # Each base component contributes at most its base maximum, and the joining
    # path contributes at most three, so the displayed cut is globally maximum.

    complete_rows = []
    for shift in (0, SHIFT):
        for edge, family in zip(info["M"], families):
            shifted_bad = shifted_edge(edge, shift)
            actual = set(all_shortest_paths(blue, *shifted_bad))
            expected = {shifted_row(row, shift) for row in family}
            assert actual == expected
            complete_rows.append(tuple(sorted(actual)))

    score = active_scoped_obligation_score(N, blue, bad, rows)
    flow = full_owner_flow(
        N, blue, bad, rows, "glued-N22",
        require_full=False, quiet=True, scope="active", include_outside=False,
    )

    replacements = []
    for index, family in enumerate(complete_rows):
        old_row = rows[index]
        for replacement_row in family:
            if replacement_row == old_row:
                continue
            new_rows = rows[:index] + (replacement_row,) + rows[index + 1:]
            new_score = active_scoped_obligation_score(N, blue, bad, new_rows)
            new_flow = full_owner_flow(
                N, blue, bad, new_rows, "glued-N22",
                require_full=False, quiet=True, scope="active",
                include_outside=False,
            )
            replacements.append({
                "index": index,
                "row": list(replacement_row),
                "score": new_score,
                "activeComponents": new_flow["activeComponents"],
                "full": new_flow["full"],
            })

    assert score == 32
    assert flow["full"] and flow["deficiency"] == 0
    assert flow["activeComponents"] == 2
    assert min(row["score"] for row in replacements) == 16
    assert any(row["score"] < score for row in replacements)
    assert min(row["activeComponents"] for row in replacements) == 1
    assert not any(row["activeComponents"] == 0 for row in replacements)

    payload = {
        "order": N,
        "baseGraph6": BASE_GRAPH6,
        "baseChoice": list(BASE_CHOICE),
        "blueEdges": len(blue),
        "badEdges": len(bad),
        "completeRowFamilySizes": [len(family) for family in complete_rows],
        "oldScore": score,
        "oldFlow": flow,
        "bestReplacementScore": min(row["score"] for row in replacements),
        "bestReplacementActiveComponents": min(
            row["activeComponents"] for row in replacements
        ),
        "descendingReplacements": [
            row for row in replacements if row["score"] < score
        ],
        "verdict": "GLUED_LOCAL_FAILURES_GLOBAL_SCOPED_HALL_FEASIBLE",
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
