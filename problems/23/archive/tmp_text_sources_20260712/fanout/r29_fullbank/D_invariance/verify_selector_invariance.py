"""Exact support-signature proof for the R29 hub-shore invariance.

This enumerates the 680 rows in each selector family, not selector tuples.
All arithmetic and all acceptance checks are integral.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
HUBS = (0, 1, 2)
TRAFFIC = frozenset(range(55))
LEFT = frozenset(range(3, 29))
RIGHT = frozenset(range(29, 55))


def edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_incidence() -> dict:
    spec = importlib.util.spec_from_file_location("r29_incidence", LEAD)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.build()


def adjacency(n: int, edges: set[tuple[int, int]]) -> list[list[int]]:
    out = [[] for _ in range(n)]
    for u, v in edges:
        out[u].append(v)
        out[v].append(u)
    for row in out:
        row.sort()
    return out


def distances(adj: list[list[int]], source: int) -> list[int]:
    dist = [-1] * len(adj)
    dist[source] = 0
    todo = deque([source])
    while todo:
        u = todo.popleft()
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                todo.append(v)
    return dist


def shortest_rows(adj: list[list[int]], source: int, target: int) -> tuple[tuple[int, ...], ...]:
    ds = distances(adj, source)
    dt = distances(adj, target)
    assert ds[target] == 4
    rows: list[tuple[int, ...]] = []

    def visit(path: tuple[int, ...]) -> None:
        u = path[-1]
        if u == target:
            rows.append(path)
            return
        for v in adj[u]:
            if ds[v] == ds[u] + 1 and ds[v] + dt[v] == 4:
                visit(path + (v,))

    visit((source,))
    return tuple(rows)


def fixed_pair_counts(rows: tuple[tuple[int, ...], ...], start: int, stop: int) -> Counter:
    pair = Counter()
    for i, row in enumerate(rows):
        if start <= i < stop:
            continue
        for x in row:
            for y in row:
                pair[x, y] += 1
    return pair


def path_in(adjacency_sets: list[set[int]], source: int, target: int) -> list[int]:
    parent: dict[int, int | None] = {source: None}
    todo = deque([source])
    while todo:
        u = todo.popleft()
        if u == target:
            break
        for v in sorted(adjacency_sets[u]):
            if v not in parent:
                parent[v] = u
                todo.append(v)
    assert target in parent
    out = []
    u: int | None = target
    while u is not None:
        out.append(u)
        u = parent[u]
    return list(reversed(out))


def main() -> None:
    data = load_incidence()
    n = data["n"]
    blue = set(data["blue"])
    bad = set(data["bad"])
    rows = tuple(tuple(row) for row in data["rows"])
    atoms = tuple(data["atoms"])
    start, stop = data["selectorStart"], data["selectorStop"]
    assert n == 2943 and stop - start == 676

    adj_blue = adjacency(n, blue)
    possible_selector_support: set[tuple[int, int]] = set()
    selector_vertices: set[int] = set()
    family_hist = Counter()
    family_partition_hist = Counter()
    selector_traffic_intersections = Counter()
    for atom in atoms[start:stop]:
        family = shortest_rows(adj_blue, *atom)
        family_hist[len(family)] += 1
        anchors = 0
        locals_ = 0
        for row in family:
            selector_vertices.update(row)
            selector_traffic_intersections[len(set(row) & TRAFFIC)] += 1
            anchors += 55 in row
            locals_ += 55 not in row
            possible_selector_support.update(edge(u, v) for u, v in zip(row, row[1:]))
        family_partition_hist[anchors, locals_] += 1

    fixed_rows = tuple(row for i, row in enumerate(rows) if not start <= i < stop)
    fixed_vertices = {x for row in fixed_rows for x in row}
    fixed_support = {edge(u, v) for row in fixed_rows for u, v in zip(row, row[1:])}
    assert family_hist == Counter({680: 676})
    assert family_partition_hist == Counter({(676, 4): 676})
    assert selector_traffic_intersections == Counter({0: 676 * 680})

    # These edges are selected and active for every selector tuple.
    guaranteed_active = {
        e for e in blue
        if e not in fixed_support
        and e not in possible_selector_support
        and e[0] in fixed_vertices
        and e[1] in fixed_vertices
    }
    guaranteed_adj = [set() for _ in range(n)]
    for u, v in guaranteed_active:
        guaranteed_adj[u].add(v)
        guaranteed_adj[v].add(u)
    component = {0}
    todo = deque([0])
    while todo:
        u = todo.popleft()
        for v in guaranteed_adj[u]:
            if v not in component:
                component.add(v)
                todo.append(v)
    active_bad_witnesses = sorted(e for e in bad if e[0] in component and e[1] in component)
    assert active_bad_witnesses == [(2762, 2766)]
    assert all(hub in component for hub in HUBS)

    pair = fixed_pair_counts(rows, start, stop)
    # Selector rows miss TRAFFIC, so these are the pair counts for every tuple.
    companions = {hub: {y for y in range(n) if pair[hub, y] > 0} for hub in HUBS}
    assert all(companions[hub] == set(TRAFFIC) for hub in HUBS)
    assert all(sum(pair[hub, y] - 1 for y in companions[hub]) == 3325 for hub in HUBS)
    fixed_row_load = {hub: pair[hub, hub] for hub in HUBS}
    assert fixed_row_load == {0: 676, 1: 676, 2: 676}

    # Selector choices cannot touch hub-incident edges.  Fixed rows support all
    # but one such edge at each hub, and the remaining edge is guaranteed active.
    hub_active_neighbors = {}
    for hub in HUBS:
        incident = {e for e in blue if hub in e}
        assert not (incident & possible_selector_support)
        active = {
            (v if u == hub else u)
            for u, v in incident
            if edge(u, v) not in fixed_support
        }
        hub_active_neighbors[hub] = sorted(active)
    assert hub_active_neighbors == {0: [55], 1: [2929], 2: [2930]}

    collision = 2 * (3 * 675 + 52 * 25)
    hit_need = max(0, 1 - max(0, n - 5 * 676))
    demand_per_hub = collision + hit_need
    demand = len(HUBS) * demand_per_hub
    assert (collision, hit_need, demand_per_hub, demand) == (6650, 1, 6651, 19953)

    # Same-owner/same-first sources: two ordered FreeHalf bits for every y
    # outside the 55 companions, minus the fixed reserved active-edge half.
    same_owner_per_hub = 2 * (n - len(TRAFFIC)) - 1
    same_owner = len(HUBS) * same_owner_per_hub
    assert (same_owner_per_hub, same_owner) == (5775, 17325)

    signed_degree = Counter()
    sign = {}
    for e in blue:
        sign[e] = 1
        signed_degree[e[0]] += 1
        signed_degree[e[1]] += 1
    for e in bad:
        sign[e] = -1
        signed_degree[e[0]] -= 1
        signed_degree[e[1]] -= 1
    companion_pairs = []
    for x in TRAFFIC:
        for y in TRAFFIC:
            if x == y or pair[x, y] != 0:
                continue
            sigma2 = signed_degree[x] + signed_degree[y] - 2 * sign.get(edge(x, y), 0)
            assert sigma2 >= 0
            companion_pairs.append((x, y))
    expected_pairs = {(x, y) for side in (LEFT, RIGHT) for x in side for y in side if x != y}
    assert set(companion_pairs) == expected_pairs
    row_companion = 2 * len(companion_pairs)
    reach = same_owner + row_companion
    assert (len(companion_pairs), row_companion, reach, demand - reach) == (1300, 2600, 19925, 28)

    bad_witness = active_bad_witnesses[0]
    result = {
        "arithmetic": "integers only",
        "tuple_space": "680^676",
        "selector_families_checked": 676,
        "rows_per_family_checked": 680,
        "selector_rows_checked": 676 * 680,
        "selector_family_partition": {"anchor": 676, "local": 4},
        "possible_selector_support_edges": len(possible_selector_support),
        "fixed_support_edges": len(fixed_support),
        "fixed_selected_vertices": len(fixed_vertices),
        "guaranteed_active_edges": len(guaranteed_active),
        "guaranteed_hub_component_vertices": len(component),
        "active_bad_witness": list(bad_witness),
        "paths_from_hub_0": [
            path_in(guaranteed_adj, 0, bad_witness[0]),
            path_in(guaranteed_adj, 0, bad_witness[1]),
        ],
        "hub_active_neighbors": {str(k): v for k, v in hub_active_neighbors.items()},
        "hub_companion_set": [0, 54],
        "hub_row_load": 676,
        "collision_per_hub": collision,
        "hit_need_per_hub": hit_need,
        "demand_per_hub": demand_per_hub,
        "shore_demand": demand,
        "same_owner_per_hub": same_owner_per_hub,
        "same_owner_pool": same_owner,
        "row_companion_ordered_pairs": len(companion_pairs),
        "row_companion_pool": row_companion,
        "reachable_union": reach,
        "defect": demand - reach,
        "incidence_source_sha256": sha256(LEAD),
    }
    output = HERE / "selector_invariance_result.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
