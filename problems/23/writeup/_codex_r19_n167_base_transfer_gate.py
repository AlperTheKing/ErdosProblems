"""Exact R19 base-only transfer matching gate on the locked N=167 cage.

The row choice is unique.  For every ordered vertex pair ``(x,y)``, let
``n[x,y]`` be the number of selected shortest rows containing both vertices.
A free cell ``n[x,y]=0`` supplies two half-slots.  Each collision copy beyond
the first consumes two half-slots, and each endpoint of an active internal
off-support edge consumes one hit half-slot.

The tested transfer relation has only the two sound R19 base rules:

* same-owner cancellation: a source ``(x,y)`` may pay owner ``x``;
* corrected c5Base transfer: distinct ``x,y`` have the destination owner as
  a common BLUE neighbour and

      |delta_B({x,y})| - |delta_M({x,y})| - 2 >= 0.

The final ``-2`` reserves the two destination blue edges.  No prune edge is
used.  A full integral matching is an exact positive guardrail for this cage;
it is not a proof of base-only Hall completeness on all cages.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _codex_pro_active_cycle_counterexample_verify import (  # noqa: E402
    adjacency,
    edge,
    full_support,
    verify_triangle_free,
)


Edge = tuple[int, int]
Source = tuple[int, int, int]


def build_fixture():
    w = 26
    support = {edge(i, (i + 1) % 26) for i in range(26)} | {edge(w, 0)}
    atoms = (
        {edge(i, (i + 4) % 26) for i in range(26)}
        | {edge(w, 3), edge(w, 23)}
    )
    active_vertices = [(9 * k) % 26 for k in range(13)]
    active_edges = {
        edge(active_vertices[i], active_vertices[i + 1])
        for i in range(len(active_vertices) - 1)
    }
    blue_core = support | active_edges

    blue = set(blue_core)
    next_vertex = 27
    for a, b in sorted(atoms):
        internal = list(range(next_vertex, next_vertex + 5))
        next_vertex += 5
        path = [a] + internal + [b]
        blue.update(edge(u, v) for u, v in zip(path, path[1:]))

    n_vertices = next_vertex
    assert n_vertices == 167
    verify_triangle_free(n_vertices, blue | atoms)

    blue_adj = adjacency(n_vertices, blue)
    rows: list[tuple[int, ...]] = []
    for atom in sorted(atoms):
        distance, path_count, _atom_support, vertices = full_support(
            blue, blue_adj, atom
        )
        assert distance == 4 and path_count == 1 and len(vertices) == 5
        rows.append(tuple(sorted(vertices)))

    return n_vertices, blue, atoms, active_edges, rows


def switch_counts(blue: set[Edge], bad: set[Edge], S: set[int]):
    delta_blue = sum((u in S) ^ (v in S) for u, v in blue)
    delta_bad = sum((u in S) ^ (v in S) for u, v in bad)
    return delta_blue, delta_bad


def multiplicities(n_vertices: int, rows: list[tuple[int, ...]]):
    count = [[0] * n_vertices for _ in range(n_vertices)]
    for row in rows:
        for x in row:
            for y in row:
                count[x][y] += 1
    return count


def owner_demands(count, component: set[int], active_edges: set[Edge]):
    demands: dict[int, list[tuple]] = {}
    for x in sorted(component):
        out = demands.setdefault(x, [])
        for y in sorted(component):
            for copy in range(max(0, count[x][y] - 1)):
                out.append(("collision", x, y, copy, 0))
                out.append(("collision", x, y, copy, 1))
    for u, v in sorted(active_edges):
        demands.setdefault(u, []).append(("hit", u, (u, v)))
        demands.setdefault(v, []).append(("hit", v, (u, v)))
    return {owner: rows for owner, rows in demands.items() if rows}


def source_candidates(
    owner: int,
    count,
    component: set[int],
    blue: set[Edge],
    bad: set[Edge],
    blue_adj: list[set[int]],
):
    relation: dict[Source, str] = {}

    # Same-owner sources realize the pointwise free/collision cancellation.
    for y in sorted(component):
        if count[owner][y] == 0:
            relation[(owner, y, 0)] = "sameOwner"
            relation[(owner, y, 1)] = "sameOwner"

    # Corrected common-BLUE base transfers.  Each ordered Free cell has two
    # independent half-slots, but the switch geometry is checked once.
    neighbours = sorted(blue_adj[owner] & component)
    for x in neighbours:
        for y in neighbours:
            if x == y or count[x][y] != 0:
                continue
            delta_blue, delta_bad = switch_counts(blue, bad, {x, y})
            adjusted = delta_blue - delta_bad - 2
            if adjusted < 0:
                continue
            relation.setdefault((x, y, 0), "c5Base")
            relation.setdefault((x, y, 1), "c5Base")
    return relation


def full_matching(demands, candidates):
    """Exact augmenting-path matching from demand IDs to source half-slots."""

    demand_nodes = [
        (owner, index)
        for owner in sorted(demands)
        for index in range(len(demands[owner]))
    ]
    demand_nodes.sort(key=lambda node: len(candidates[node[0]]))
    source_owner: dict[Source, tuple[int, int]] = {}
    demand_source: dict[tuple[int, int], Source] = {}

    def augment(node, seen: set[Source]):
        owner, _index = node
        for source in candidates[owner]:
            if source in seen:
                continue
            seen.add(source)
            previous = source_owner.get(source)
            if previous is None or augment(previous, seen):
                source_owner[source] = node
                demand_source[node] = source
                return True
        return False

    unmatched = []
    for node in demand_nodes:
        if not augment(node, set()):
            unmatched.append(node)
    return demand_source, unmatched


def hall_witness(demands, candidates, matching, unmatched):
    """Alternating-reachability Hall witness from unmatched demand nodes."""

    source_owner = {source: node for node, source in matching.items()}
    left = set(unmatched)
    right: set[Source] = set()
    queue = deque(unmatched)
    while queue:
        node = queue.popleft()
        owner, _index = node
        matched_source = matching.get(node)
        for source in candidates[owner]:
            if source == matched_source or source in right:
                continue
            right.add(source)
            next_node = source_owner.get(source)
            if next_node is not None and next_node not in left:
                left.add(next_node)
                queue.append(next_node)

    all_neighbours = {
        source for owner, _index in left for source in candidates[owner]
    }
    assert all_neighbours == right
    assert len(left) > len(right)
    return left, right


def main():
    n_vertices, blue, bad, active_edges, rows = build_fixture()
    count = multiplicities(n_vertices, rows)
    component = set().union(*(set(row) for row in rows))
    assert component == set(range(27))
    demands = owner_demands(count, component, active_edges)
    blue_adj = adjacency(n_vertices, blue)
    candidates = {
        owner: source_candidates(owner, count, component, blue, bad, blue_adj)
        for owner in demands
    }

    matching, unmatched = full_matching(demands, candidates)
    assert len(set(matching.values())) == len(matching)

    if unmatched:
        hall_left, hall_right = hall_witness(
            demands, candidates, matching, unmatched
        )
        left_hist = Counter(owner for owner, _index in hall_left)
        whole_owner_fibres = all(
            count == len(demands[owner]) for owner, count in left_hist.items()
        )
        assert whole_owner_fibres
        left_kind_hist = Counter(
            demands[owner][index][0] for owner, index in hall_left
        )
        right_relation_hist = Counter()
        for source in hall_right:
            kinds = {
                candidates[owner][source]
                for owner in left_hist
                if source in candidates[owner]
            }
            right_relation_hist["+".join(sorted(kinds))] += 1
        witness_payload = json.dumps({
            "left": sorted(hall_left),
            "right": sorted(hall_right),
        }, separators=(",", ":")).encode()
        print(json.dumps({
            "N": n_vertices,
            "componentN": len(component),
            "rows": len(rows),
            "activeEdges": len(active_edges),
            "totalHalfDemands": sum(map(len, demands.values())),
            "maximumMatched": len(matching),
            "unmatched": len(unmatched),
            "hallLeft": len(hall_left),
            "hallRight": len(hall_right),
            "hallDeficiency": len(hall_left) - len(hall_right),
            "hallLeftOwnerHistogram": {
                str(k): v for k, v in sorted(left_hist.items())
            },
            "hallWholeOwnerFibres": whole_owner_fibres,
            "hallLeftKindHistogram": dict(sorted(left_kind_hist.items())),
            "hallRightRelationHistogram": dict(
                sorted(right_relation_hist.items())
            ),
            "hallWitnessSHA256": hashlib.sha256(witness_payload).hexdigest(),
            "verdict": "base-only transfer relation is Hall-deficient",
        }, sort_keys=True, separators=(",", ":")))
        return

    relation_hist = Counter()
    owner_hist = {}
    records = []
    for node, source in sorted(matching.items()):
        owner, index = node
        relation = candidates[owner][source]
        relation_hist[relation] += 1
        owner_hist.setdefault(owner, Counter())[relation] += 1
        x, y, _half = source
        assert count[x][y] == 0
        if relation == "sameOwner":
            assert x == owner
        else:
            assert owner in blue_adj[x] and owner in blue_adj[y]
            delta_blue, delta_bad = switch_counts(blue, bad, {x, y})
            assert delta_blue - delta_bad - 2 >= 0
        records.append((node, demands[owner][index], source, relation))

    collision_half = sum(
        demand[0] == "collision" for owner in demands for demand in demands[owner]
    )
    hit_half = sum(
        demand[0] == "hit" for owner in demands for demand in demands[owner]
    )
    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    print(json.dumps({
        "N": n_vertices,
        "componentN": len(component),
        "rows": len(rows),
        "activeEdges": len(active_edges),
        "collisionHalfDemands": collision_half,
        "hitHalfDemands": hit_half,
        "totalHalfDemands": collision_half + hit_half,
        "matched": len(matching),
        "relationHistogram": dict(sorted(relation_hist.items())),
        "owners": {
            str(owner): dict(sorted(hist.items()))
            for owner, hist in sorted(owner_hist.items())
        },
        "minimumCandidateHalfSlots": min(map(len, candidates.values())),
        "matchingSHA256": hashlib.sha256(payload).hexdigest(),
        "verdict": "base-only transfer relation matches every obligation",
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
