"""Exact gate for the R29 cage with every y--55 arm edge 3-subdivided.

All arithmetic is integer.  The max-cut proof is the exact restriction/extension
identity: a private length-3 path with old endpoints u,v has optimum
2 + [u and v are separated].
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
FULLBANK_GATE = ROOT / "tmp/fanout/r29_fullbank_gate/verify.py"


def edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def load_lead():
    spec = importlib.util.spec_from_file_location("r29_lead", LEAD)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_fullbank_gate():
    spec = importlib.util.spec_from_file_location("r29_fullbank", FULLBANK_GATE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def adjacency(n: int, edges: set[tuple[int, int]]) -> list[list[int]]:
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    for row in adj:
        row.sort()
    return adj


def bfs(adj: list[list[int]], source: int) -> tuple[list[int], list[int]]:
    dist = [-1] * len(adj)
    count = [0] * len(adj)
    dist[source] = 0
    count[source] = 1
    todo = deque([source])
    while todo:
        u = todo.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                count[v] = count[u]
                todo.append(v)
            elif dist[v] == dist[u] + 1:
                count[v] += count[u]
    return dist, count


def shortest_rows(adj: list[list[int]], source: int, target: int):
    ds, _ = bfs(adj, source)
    dt, _ = bfs(adj, target)
    assert ds[target] == 4
    rows: list[tuple[int, ...]] = []

    def visit(path: list[int]) -> None:
        u = path[-1]
        if len(path) == 5:
            if u == target:
                rows.append(tuple(path))
            return
        for v in adj[u]:
            if ds[v] == ds[u] + 1 and ds[v] + dt[v] == 4:
                visit(path + [v])

    visit([source])
    return tuple(sorted(rows))


def triangle_free(n: int, graph: set[tuple[int, int]]) -> bool:
    adj = [set() for _ in range(n)]
    for u, v in graph:
        adj[u].add(v)
        adj[v].add(u)
    return all(not (adj[u] & adj[v]) for u, v in graph)


def connected(n: int, graph: set[tuple[int, int]]) -> bool:
    adj = adjacency(n, graph)
    seen = {0}
    todo = deque([0])
    while todo:
        u = todo.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return len(seen) == n


def cut_value(edges: set[tuple[int, int]], side: list[int]) -> int:
    return sum(side[u] != side[v] for u, v in edges)


def build_subdivision():
    lead = load_lead()
    old = lead.build()
    data = dict(old)
    data["blue"] = set(old["blue"])
    data["bad"] = set(old["bad"])
    data["side"] = list(old["side"])

    arm_y = sorted(
        v for u, v in data["blue"]
        if u == 55 and 56 <= v < 2760 and v % 2 == 1
    )
    assert len(arm_y) == 1352
    removed = {edge(55, y) for y in arm_y}
    assert removed <= data["blue"]
    data["blue"] -= removed

    replacements = []
    next_vertex = old["n"]
    for y in arm_y:
        a, b = next_vertex, next_vertex + 1
        next_vertex += 2
        data["side"].extend([1 - data["side"][y], data["side"][y]])
        path = (y, a, b, 55)
        path_edges = {edge(x, z) for x, z in zip(path, path[1:])}
        data["blue"].update(path_edges)
        replacements.append((y, a, b, 55))

    data["n"] = next_vertex
    data["graph"] = data["blue"] | data["bad"]
    data["removedArmEdges"] = removed
    data["replacementPaths"] = tuple(replacements)
    assert data["n"] == 5647
    assert len(data["side"]) == data["n"]
    assert len(data["blue"]) == 7039 - 1352 + 3 * 1352 == 9743
    assert len(data["bad"]) == 1383
    return lead, old, data


def main() -> None:
    lead, old, data = build_subdivision()
    fullbank = load_fullbank_gate()
    n = data["n"]

    # Exact structural checks.
    assert data["blue"].isdisjoint(data["bad"])
    assert all(data["side"][u] != data["side"][v] for u, v in data["blue"])
    assert all(data["side"][u] == data["side"][v] for u, v in data["bad"])
    assert triangle_free(n, data["graph"])
    assert connected(n, data["blue"])

    # Exact max-cut certificate.  For fixed old endpoint colors, each private
    # 3-path contributes at most 2 plus the old edge indicator.  Restricting a
    # new cut therefore loses at most the constant 2 per path.
    old_maxcut = sum(old["classMax"])
    constant = 2 * len(data["replacementPaths"])
    maxcut_upper = old_maxcut + constant
    displayed = cut_value(data["graph"], data["side"])
    assert old_maxcut == 7039 and constant == 2704
    assert displayed == maxcut_upper == 9743

    # All old bad edges retain distance four; count every shortest family.
    adj_blue = adjacency(n, data["blue"])
    family_hist = Counter()
    gamma = 0
    selector_families: list[tuple[tuple[int, ...], ...]] = []
    selector_begin = data["selectorStart"]
    selector_end = data["selectorStop"]
    for index, atom in enumerate(data["atoms"]):
        dist, count = bfs(adj_blue, atom[0])
        assert dist[atom[1]] == 4
        family_hist[count[atom[1]]] += 1
        gamma += 25
        if selector_begin <= index < selector_end:
            rows = shortest_rows(adj_blue, *atom)
            assert len(rows) == count[atom[1]]
            selector_families.append(rows)
    assert family_hist == Counter({1: 707, 4: 676})
    assert gamma == 34575

    # Every selector family has exactly the four former local rows.  Record
    # the finite variation relevant to hub P1/P3: no local row contains an old
    # traffic vertex 0..55, so hub companions and all companion-pair counts are
    # independent of all 4^676 choices.
    local_shape = Counter()
    local_union_sizes = Counter()
    local_support_sizes = Counter()
    for rows in selector_families:
        assert len(rows) == 4
        assert all(55 not in row for row in rows)
        assert all(not (set(row) & set(range(56))) for row in rows)
        local_shape[tuple(sorted(len(set(row)) for row in rows))] += 1
        local_union_sizes[len(set().union(*(set(row) for row in rows)))] += 1
        local_support_sizes[len({
            edge(u, v) for row in rows for u, v in zip(row, row[1:])
        })] += 1

    # Baseline is one legal local tuple.  The hub collision fibres are fixed
    # for every local tuple by the preceding disjointness check.
    baseline = lead.scoped_state(data, data["rows"])
    hub_collision = {v: baseline["collision"][v] for v in (0, 1, 2)}
    hub_hit = {v: baseline["hitNeed"][v] for v in (0, 1, 2)}
    assert hub_collision == {0: 6650, 1: 6650, 2: 6650}
    # N increased while all hub row counts/degrees stayed fixed, so endpoint
    # HitNeed vanishes in the subdivided graph.
    assert hub_hit == {0: 0, 1: 0, 2: 0}

    # Recompute the literal production source pool.  New private vertices are
    # absent from every possible local selector row, so each gives both
    # same-first halves (owner,newVertex,h) to each hub, universally over all
    # 4^676 local tuples.  The baseline reconstruction below also checks the
    # complete P1/P3 union, including reservation deductions.
    state = fullbank.rebuild_scope(data, data["rows"])
    staged = fullbank.staged_sources(data, state)["stages"]
    p1 = fullbank.aggregate_masks([staged["sameFirst"]])
    p13 = fullbank.aggregate_masks([
        staged["sameFirst"], staged["commonBad"], staged["rowCompanion"]
    ])
    demand_by_owner = hub_collision
    _, p1_cuts = fullbank.hall_cuts(demand_by_owner, p1)
    _, p13_cuts = fullbank.hall_cuts(demand_by_owner, p13)
    p1_full = p1_cuts[7]
    p13_full = p13_cuts[7]
    assert p1_full["demand"] == 19950
    assert p1_full["reach"] >= p1_full["demand"]
    assert p13_full["reach"] >= p13_full["demand"]

    old_private_start = old["n"]
    expected_new_keys = {
        (owner, vertex, half)
        for owner in (0, 1, 2)
        for vertex in range(old_private_start, n)
        for half in (0, 1)
    }
    assert expected_new_keys <= set(staged["sameFirst"])
    assert len(expected_new_keys) == 16224

    canonical = {
        "n": n,
        "blue": [list(e) for e in sorted(data["blue"])],
        "bad": [list(e) for e in sorted(data["bad"])],
    }
    canonical_bytes = json.dumps(
        canonical, sort_keys=True, separators=(",", ":")
    ).encode()
    result = {
        "schema": "R33_SUBDIVIDED_ANCHOR_CAGE_V1",
        "construction": {
            "oldN": old["n"],
            "newN": n,
            "replacedEdges": len(data["replacementPaths"]),
            "newPrivateVertices": n - old["n"],
            "blueEdges": len(data["blue"]),
            "badEdges": len(data["bad"]),
            "totalEdges": len(data["graph"]),
        },
        "checks": {
            "triangleFree": True,
            "blueConnected": True,
            "displayedCut": displayed,
            "maxCutUpper": maxcut_upper,
            "oldMaxCut": old_maxcut,
            "subdivisionConstant": constant,
            "gamma": gamma,
            "rowHistogram": dict(sorted(family_hist.items())),
            "selectorFamilies": len(selector_families),
            "selectorRowsEach": 4,
        },
        "localFamilyAudit": {
            "rowVertexCardinalityShape": {
                str(k): v for k, v in sorted(local_shape.items())
            },
            "familyVertexUnionSizes": dict(sorted(local_union_sizes.items())),
            "familySupportUnionSizes": dict(sorted(local_support_sizes.items())),
            "allRowsAvoidOldTrafficVertices0to55": True,
            "hubCompanionPairCountsTupleInvariant": True,
        },
        "baselineHub": {
            "collision": hub_collision,
            "hitNeed": hub_hit,
            "collisionShoreDemand": sum(hub_collision.values()),
            "newPrivateSameFirstKeys": len(expected_new_keys),
            "p1FullShore": p1_full,
            "p1p3FullShore": p13_full,
            "candidateRejected": True,
            "rejection": "P1 same-first sources alone make the hub collision shore feasible",
        },
        "sha256": {
            "oldConstructor": hashlib.sha256(LEAD.read_bytes()).hexdigest(),
            "canonicalGraph": hashlib.sha256(canonical_bytes).hexdigest(),
            "script": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
