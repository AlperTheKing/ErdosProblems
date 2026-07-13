"""Independent exact reconstruction and coordinated-trade probe for R29."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, deque
from pathlib import Path


def edge(u: int, v: int) -> tuple[int, int]:
    assert u != v
    return (u, v) if u < v else (v, u)


def adjacency(n: int, edges: set[tuple[int, int]]) -> list[list[int]]:
    out = [set() for _ in range(n)]
    for u, v in edges:
        assert v not in out[u]
        out[u].add(v)
        out[v].add(u)
    return [sorted(xs) for xs in out]


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


def shortest_rows(
    adj: list[list[int]], source: int, target: int
) -> tuple[tuple[int, ...], ...]:
    dist, count = bfs(adj, source)
    assert dist[target] == 4
    rows = []

    def visit(path: list[int]) -> None:
        u = path[-1]
        if u == target:
            rows.append(tuple(path))
            return
        for v in adj[u]:
            if dist[v] == dist[u] + 1 and dist[v] <= 4:
                visit(path + [v])

    # Filter at the end because a distance-increasing path need not end at target.
    visit([source])
    rows = [row for row in rows if row[-1] == target and len(row) == 5]
    assert len(rows) == count[target]
    return tuple(sorted(rows))


def add_circuit(
    blue: set[tuple[int, int]],
    bad: set[tuple[int, int]],
    side: list[int],
    offset: int,
) -> tuple[int, list[tuple[int, int]]]:
    w = 26
    support = {edge(i, (i + 1) % 26) for i in range(26)} | {edge(w, 0)}
    atoms = sorted(
        {edge(i, (i + 4) % 26) for i in range(26)}
        | {edge(w, 3), edge(w, 23)}
    )
    active_vertices = [(9 * k) % 26 for k in range(13)]
    active = {
        edge(active_vertices[i], active_vertices[i + 1])
        for i in range(12)
    }
    while len(side) < offset:
        raise AssertionError("noncontiguous circuit offset")
    side.extend([i % 2 for i in range(26)] + [1])
    blue.update(edge(offset + u, offset + v) for u, v in support | active)
    bad.update(edge(offset + u, offset + v) for u, v in atoms)
    next_vertex = offset + 27
    for a, b in atoms:
        internal = list(range(next_vertex, next_vertex + 5))
        next_vertex += 5
        for step in range(1, 6):
            side.append(side[offset + a] ^ (step % 2))
        path = [offset + a] + internal + [offset + b]
        blue.update(edge(u, v) for u, v in zip(path, path[1:]))
    assert next_vertex == offset + 167
    return next_vertex, [edge(offset + u, offset + v) for u, v in atoms]


def locked_double_star_maxcut() -> tuple[int, int]:
    """Enumerate the advertised 16*27^2 endpoint/count quotient."""
    t = 26
    best = -1
    achievers = 0
    for core in range(16):
        r = (core >> 0) & 1
        c_l = (core >> 1) & 1
        c_r = (core >> 2) & 1
        anchor = (core >> 3) & 1
        for left_one in range(t + 1):
            for right_one in range(t + 1):
                value = (r != c_l) + (r != c_r)
                value += left_one * (1 != c_l) + (t - left_one) * (0 != c_l)
                value += right_one * (1 != c_r) + (t - right_one) * (0 != c_r)
                value += left_one * (t - right_one) + (t - left_one) * right_one
                opposite = (
                    (left_one if anchor == 0 else t - left_one)
                    + (right_one if anchor == 0 else t - right_one)
                )
                value += t * (3 * opposite + 2 * (2 * t - opposite))
                if value > best:
                    best, achievers = value, 1
                elif value == best:
                    achievers += 1
    return best, achievers


def build() -> dict:
    r, c_l, c_r = 0, 1, 2
    left = list(range(3, 29))
    right = list(range(29, 55))
    anchor = 55
    side = [0, 1, 1] + [0] * 52 + [1]
    blue = {edge(r, c_l), edge(r, c_r)}
    blue.update(edge(c_l, v) for v in left)
    blue.update(edge(c_r, v) for v in right)
    bad = {edge(u, v) for u in left for v in right}
    traffic_rows = [(u, c_l, r, c_r, v) for u in left for v in right]

    arms_by_region: list[list[tuple[int, int, int]]] = []
    next_vertex = 56
    for region in (left, right):
        arms = []
        for leaf in region:
            for _ in range(26):
                x, y = next_vertex, next_vertex + 1
                next_vertex += 2
                side.extend([1, 0])
                blue.update({edge(leaf, x), edge(x, y), edge(y, anchor)})
                arms.append((leaf, x, y))
        assert len(arms) == 676
        arms_by_region.append(arms)
    assert next_vertex == 2760

    q_l, q_r = 2760, 2761
    side.extend([0, 0])
    selector_rows = []
    selector_atoms = []
    selector_meta = []
    d_x_to_leaf = {}
    d_leaves_by_region = []
    for region_id, (q, arms) in enumerate(zip((q_l, q_r), arms_by_region)):
        first, second = arms[:338], arms[338:]
        assert len({leaf for leaf, _, _ in first}) == 13
        assert len({leaf for leaf, _, _ in second}) == 13
        d_leaves_by_region.append(sorted({leaf for leaf, _, _ in second}))
        d_x_to_leaf.update({x: leaf for leaf, x, _ in second})
        for j in range(338):
            _, x_f, _ = first[j]
            _, _, y_f_next = first[(j + 1) % 338]
            _, x_d, _ = second[j]
            _, _, y_d_next = second[(j + 1) % 338]
            displayed_row = (q, x_f, y_f_next, x_d, y_d_next)
            atom = edge(q, y_d_next)
            blue.update(
                edge(u, v)
                for u, v in zip(displayed_row, displayed_row[1:])
            )
            bad.add(atom)
            selector_rows.append(tuple(reversed(displayed_row)))
            selector_atoms.append(atom)
            selector_meta.append({
                "region": region_id,
                "j": j,
                "q": q,
                "xF": x_f,
                "yF": y_f_next,
                "xD": x_d,
                "yD": y_d_next,
                "anchorRow": (y_d_next, anchor, y_f_next, x_f, q),
            })

    circuit_offset = 2762
    next_vertex, circuit_atoms = add_circuit(
        blue, bad, side, circuit_offset
    )
    assert next_vertex == 2929
    z_l, z_r = next_vertex, next_vertex + 1
    next_vertex += 2
    side.extend([0, 0])
    midpoint = circuit_offset + 2
    cable = {
        edge(r, anchor), edge(anchor, midpoint),
        edge(c_l, z_l), edge(z_l, anchor),
        edge(c_r, z_r), edge(z_r, anchor),
    }
    blue.update(cable)

    seed_atoms = []
    seed_rows = []
    for seed in (anchor, z_l, z_r):
        internal = list(range(next_vertex, next_vertex + 4))
        next_vertex += 4
        for step in range(1, 5):
            side.append(side[seed] ^ (step % 2))
        row = tuple([seed] + internal)
        atom = edge(seed, internal[-1])
        blue.update(edge(u, v) for u, v in zip(row, row[1:]))
        bad.add(atom)
        seed_atoms.append(atom)
        seed_rows.append(row)
    n = next_vertex
    assert n == 2943 and len(side) == n

    graph = blue | bad
    assert len(blue) == 7039
    assert len(bad) == 1383
    assert len(graph) == 8422
    assert blue.isdisjoint(bad)
    assert all(side[u] != side[v] for u, v in blue)
    assert all(side[u] == side[v] for u, v in bad)

    adj_graph = adjacency(n, graph)
    assert all(not (set(adj_graph[u]) & set(adj_graph[v])) for u, v in graph)
    adj_blue = adjacency(n, blue)
    seen = {0}
    todo = deque([0])
    while todo:
        u = todo.popleft()
        for v in adj_blue[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    assert len(seen) == n

    circuit_rows = []
    for atom in circuit_atoms:
        rows = shortest_rows(adj_blue, *atom)
        assert len(rows) == 1
        circuit_rows.append(rows[0])
    rows = tuple(traffic_rows + selector_rows + circuit_rows + seed_rows)
    atoms = tuple(
        sorted(edge(u, v) for u in left for v in right)
        + selector_atoms + circuit_atoms + seed_atoms
    )
    assert len(rows) == len(atoms) == 1383
    for atom, row in zip(atoms, rows):
        assert edge(row[0], row[-1]) == atom
        assert all(edge(u, v) in blue for u, v in zip(row, row[1:]))

    return {
        "n": n,
        "blue": blue,
        "bad": bad,
        "graph": graph,
        "side": side,
        "rows": rows,
        "atoms": atoms,
        "selectorMeta": selector_meta,
        "selectorStart": len(traffic_rows),
        "selectorStop": len(traffic_rows) + len(selector_rows),
        "dXToLeaf": d_x_to_leaf,
        "dLeavesByRegion": d_leaves_by_region,
        "classMax": [4110, 2704, 12, 207, 6],
    }


def scoped_state(data: dict, rows: tuple[tuple[int, ...], ...]) -> dict:
    n = data["n"]
    counts = Counter()
    row_count = [0] * n
    support = set()
    for row in rows:
        for x in row:
            row_count[x] += 1
            for y in row:
                counts[x, y] += 1
        support.update(edge(u, v) for u, v in zip(row, row[1:]))
    selected = {x for row in rows for x in row}
    active = {
        e for e in data["blue"]
        if e[0] in selected and e[1] in selected and e not in support
    }
    parent = {v: v for v in selected}

    def find(v: int) -> int:
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    def union(u: int, v: int) -> None:
        u, v = find(u), find(v)
        if u != v:
            parent[max(u, v)] = min(u, v)

    for u, v in active:
        union(u, v)
    roots = {
        find(u) for u, v in data["bad"]
        if u in selected and v in selected and find(u) == find(v)
    }
    active_vertices = {v for v in selected if find(v) in roots}
    demanded_active = {e for e in active if find(e[0]) in roots}
    degree = [0] * n
    for u, v in demanded_active:
        degree[u] += 1
        degree[v] += 1
    collision = {}
    hitneed = {}
    for v in sorted(active_vertices):
        collision[v] = 2 * sum(
            multiplicity - 1
            for (x, _), multiplicity in counts.items()
            if x == v and multiplicity >= 2
        )
        hitneed[v] = max(0, degree[v] - max(0, n - 5 * row_count[v]))
    return {
        "selected": selected,
        "activeVertices": active_vertices,
        "activeEdges": active,
        "demandedActive": demanded_active,
        "collision": collision,
        "hitNeed": hitneed,
        "collisionTotal": sum(collision.values()),
        "hitNeedTotal": sum(hitneed.values()),
        "score": sum(collision.values()) + sum(hitneed.values()),
    }


def canonical_bytes(data: dict) -> bytes:
    payload = {
        "n": data["n"],
        "blue": [list(e) for e in sorted(data["blue"])],
        "bad": [list(e) for e in sorted(data["bad"])],
        "rows": [list(row) for row in data["rows"]],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def main() -> None:
    data = build()
    assert sum(data["classMax"]) == 7039
    locked_max, locked_achievers = locked_double_star_maxcut()
    assert locked_max == 4110
    adj_blue = adjacency(data["n"], data["blue"])
    hist = Counter()
    gamma = 0
    selector_count = 0
    for atom in data["atoms"]:
        dist, path_count = bfs(adj_blue, atom[0])
        assert dist[atom[1]] == 4
        hist[path_count[atom[1]]] += 1
        gamma += 25
        if path_count[atom[1]] == 680:
            selector_count += 1
    assert gamma == 34575
    assert hist == Counter({1: 707, 680: 676})
    assert selector_count == 676

    # Exhaustively classify the 459,680 selector rows.  An anchor row contains
    # vertex 55; every other row contains exactly one D-arm x vertex.
    family_shapes = Counter()
    local_touch = [Counter(), Counter()]
    for atom, meta in zip(
        data["atoms"][data["selectorStart"]:data["selectorStop"]],
        data["selectorMeta"],
    ):
        family = shortest_rows(adj_blue, *atom)
        anchors = [row for row in family if 55 in row]
        locals_ = [row for row in family if 55 not in row]
        assert len(anchors) == 676 and len(locals_) == 4
        assert meta["anchorRow"] in anchors
        touched = set()
        for row in locals_:
            xds = [v for v in row if v in data["dXToLeaf"]]
            assert len(xds) == 1
            touched.add(data["dXToLeaf"][xds[0]])
        for leaf in touched:
            local_touch[meta["region"]][leaf] += 1
        family_shapes[len(anchors), len(locals_)] += 1
    assert family_shapes == Counter({(676, 4): 676})
    assert all(
        set(touches.values()) == {27} and len(touches) == 13
        for touches in local_touch
    )

    baseline = scoped_state(data, data["rows"])
    assert baseline["score"] == 30811

    anchor_rows = list(data["rows"])
    for i, meta in enumerate(data["selectorMeta"]):
        anchor_rows[data["selectorStart"] + i] = meta["anchorRow"]
    anchor_state = scoped_state(data, tuple(anchor_rows))

    # Global lower bound.  Let L_s be the number of local rows on side s.
    # At most 27 local families can touch one D leaf, so at least ceil(L_s/27)
    # D leaves are active, each retaining its fixed traffic collision score 200.
    # Vertex 55 contributes its self and q_L/q_R collision fibres exactly as
    # encoded below.  Hubs plus the rigid circuit contribute the fixed 20411.
    lower_bounds = {}
    minimum_lower = None
    minimizers = []
    for local_l in range(339):
        for local_r in range(339):
            anchor_l, anchor_r = 338 - local_l, 338 - local_r
            anchor_total = anchor_l + anchor_r
            collision_55 = 2 * (
                anchor_total
                + max(0, anchor_l - 1)
                + max(0, anchor_r - 1)
            )
            active_d_leaves = (
                (local_l + 26) // 27 + (local_r + 26) // 27
            )
            bound = 20411 + collision_55 + 200 * active_d_leaves
            if local_l == 0 and local_r == 0:
                bound += 4  # exact cable HitNeed at the overloaded anchor
            if minimum_lower is None or bound < minimum_lower:
                minimum_lower = bound
                minimizers = [(local_l, local_r)]
            elif bound == minimum_lower:
                minimizers.append((local_l, local_r))
            lower_bounds[local_l, local_r] = bound
    assert minimum_lower == 23115
    assert minimizers == [(0, 0)]
    assert anchor_state["score"] == minimum_lower

    raw = canonical_bytes(data)
    payload = {
        "counts": {
            "n": data["n"],
            "edges": len(data["graph"]),
            "blue": len(data["blue"]),
            "bad": len(data["bad"]),
            "maxCut": sum(data["classMax"]),
            "gamma": gamma,
            "rowHistogram": dict(sorted(hist.items())),
            "hammingOneReplacements": 676 * 679,
            "lockedQuotientCases": 16 * 27 * 27,
            "lockedQuotientAchievers": locked_achievers,
        },
        "baseline": {
            "score": baseline["score"],
            "collision": baseline["collisionTotal"],
            "hitNeed": baseline["hitNeedTotal"],
            "activeVertices": len(baseline["activeVertices"]),
            "positiveOwners": {
                str(v): baseline["collision"].get(v, 0)
                + baseline["hitNeed"].get(v, 0)
                for v in sorted(baseline["activeVertices"])
                if baseline["collision"].get(v, 0)
                + baseline["hitNeed"].get(v, 0) > 0
            },
        },
        "allAnchorTrade": {
            "changedRows": 676,
            "score": anchor_state["score"],
            "delta": anchor_state["score"] - baseline["score"],
            "collision": anchor_state["collisionTotal"],
            "hitNeed": anchor_state["hitNeedTotal"],
            "activeVertices": len(anchor_state["activeVertices"]),
            "positiveOwners": {
                str(v): anchor_state["collision"].get(v, 0)
                + anchor_state["hitNeed"].get(v, 0)
                for v in sorted(anchor_state["activeVertices"])
                if anchor_state["collision"].get(v, 0)
                + anchor_state["hitNeed"].get(v, 0) > 0
            },
        },
        "globalSelectorLandscape": {
            "minimum": minimum_lower,
            "minimizingLocalCounts": [list(x) for x in minimizers],
            "minimizingSupportPatternsPerSide": 2,
            "atomAssignmentsPerSupportPatternPerSide": str(math.factorial(338)),
            "rowTupleMinimizers": str(4 * math.factorial(338) ** 2),
            "familyShape": {
                "families": family_shapes[676, 4],
                "anchorRowsPerFamily": 676,
                "localRowsPerFamily": 4,
            },
            "maxLocalFamiliesTouchingOneDLeaf": 27,
            "hubsDeactivate": False,
            "trafficLeavesActiveAtMinimum": 0,
        },
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    out = Path(__file__).with_name("lead_result.json")
    out.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
