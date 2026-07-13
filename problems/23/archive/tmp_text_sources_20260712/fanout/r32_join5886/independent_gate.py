"""Independent exact gate for the doubled R29 cage.

This file deliberately does not import the candidate constructor, its doubled
falsifier, or either Pattern-5 gate.  It rebuilds the graph from the explicit
five-class R29 specification and checks every claim with integer arithmetic.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
OFFSET = 2943

ORIGINAL_DIR = (
    ROOT / "tmp/fanout/common_blue_universal/pattern5_static_token"
)
ORIGINAL_MANIFEST = ORIGINAL_DIR / "MANIFEST.sha256"
ORIGINAL_RESULT = ORIGINAL_DIR / "doubled_cage_result.json"
LEAD_RESULT = ROOT / "tmp/fanout/r29_gate/lead/lead_result.json"


def edge(u: int, v: int) -> tuple[int, int]:
    assert u != v
    return (u, v) if u < v else (v, u)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def json_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("ascii")


def audit_manifest(path: Path) -> dict[str, object]:
    entries: dict[str, str] = {}
    actual: dict[str, str] = {}
    for raw_line in path.read_text(encoding="ascii").splitlines():
        if not raw_line.strip():
            continue
        digest, name = raw_line.split(maxsplit=1)
        entries[name] = digest.lower()
        actual[name] = sha256_file(path.parent / name)
    mismatches = {
        name: {"expected": entries[name], "actual": actual[name]}
        for name in entries
        if entries[name] != actual[name]
    }
    assert not mismatches, mismatches
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "manifestSHA256": sha256_file(path),
        "entries": len(entries),
        "allEntriesMatch": True,
        "files": actual,
    }


class CageBuilder:
    """Standalone reconstruction with an explicit edge-class ledger."""

    def __init__(self) -> None:
        self.blue: set[tuple[int, int]] = set()
        self.bad: set[tuple[int, int]] = set()
        self.classes: dict[str, set[tuple[int, int]]] = {
            name: set()
            for name in ("traffic", "selectors", "seeds", "circuit", "cable")
        }

    def add(self, color: str, cls: str, u: int, v: int) -> tuple[int, int]:
        e = edge(u, v)
        assert e not in self.blue and e not in self.bad
        assert e not in self.classes[cls]
        if color == "blue":
            self.blue.add(e)
        else:
            assert color == "bad"
            self.bad.add(e)
        self.classes[cls].add(e)
        return e


def adjacency(n: int, edges: set[tuple[int, int]]) -> list[set[int]]:
    out = [set() for _ in range(n)]
    for u, v in edges:
        assert v not in out[u]
        out[u].add(v)
        out[v].add(u)
    return out


def bfs_distances(adj: list[set[int]], source: int) -> list[int]:
    dist = [-1] * len(adj)
    dist[source] = 0
    todo = deque([source])
    while todo:
        u = todo.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                todo.append(v)
    return dist


def unique_shortest_row(
    adj: list[set[int]], source: int, target: int
) -> tuple[int, ...]:
    dist_source = bfs_distances(adj, source)
    dist_target = bfs_distances(adj, target)
    assert dist_source[target] == 4
    rows: list[tuple[int, ...]] = []

    def visit(path: tuple[int, ...]) -> None:
        u = path[-1]
        if u == target:
            rows.append(path)
            return
        for v in sorted(adj[u]):
            if (
                dist_source[v] == dist_source[u] + 1
                and dist_source[v] + dist_target[v] == 4
            ):
                visit(path + (v,))

    visit((source,))
    assert len(rows) == 1 and len(rows[0]) == 5
    return rows[0]


def reconstruct_base() -> dict[str, object]:
    b = CageBuilder()
    r, c_left, c_right, anchor = 0, 1, 2, 55
    left = list(range(3, 29))
    right = list(range(29, 55))
    side = [0, 1, 1] + [0] * 52 + [1]

    b.add("blue", "traffic", r, c_left)
    b.add("blue", "traffic", r, c_right)
    for leaf in left:
        b.add("blue", "traffic", c_left, leaf)
    for leaf in right:
        b.add("blue", "traffic", c_right, leaf)
    traffic_rows = []
    traffic_atoms = []
    for u in left:
        for v in right:
            b.add("bad", "traffic", u, v)
            traffic_atoms.append(edge(u, v))
            traffic_rows.append((u, c_left, r, c_right, v))

    arms_by_region: list[list[tuple[int, int, int]]] = []
    next_vertex = 56
    for region in (left, right):
        arms = []
        for leaf in region:
            for _ in range(26):
                x, y = next_vertex, next_vertex + 1
                next_vertex += 2
                side.extend((1, 0))
                b.add("blue", "traffic", leaf, x)
                b.add("blue", "traffic", x, y)
                b.add("blue", "traffic", y, anchor)
                arms.append((leaf, x, y))
        assert len(arms) == 676
        arms_by_region.append(arms)
    assert next_vertex == 2760

    q_left, q_right = 2760, 2761
    side.extend((0, 0))
    selector_rows = []
    selector_anchor_rows = []
    selector_atoms = []
    selector_cycles: list[set[tuple[int, int]]] = []
    for q, arms in zip((q_left, q_right), arms_by_region):
        first, second = arms[:338], arms[338:]
        assert len({leaf for leaf, _x, _y in first}) == 13
        assert len({leaf for leaf, _x, _y in second}) == 13
        for j in range(338):
            _leaf_f, x_f, _y_f = first[j]
            _leaf_fn, _x_fn, y_f_next = first[(j + 1) % 338]
            _leaf_d, x_d, _y_d = second[j]
            _leaf_dn, _x_dn, y_d_next = second[(j + 1) % 338]
            displayed = (q, x_f, y_f_next, x_d, y_d_next)
            cycle = set()
            for u, v in zip(displayed, displayed[1:]):
                cycle.add(b.add("blue", "selectors", u, v))
            cycle.add(b.add("bad", "selectors", q, y_d_next))
            assert len(cycle) == 5 and len(set(displayed)) == 5
            selector_cycles.append(cycle)
            selector_rows.append(tuple(reversed(displayed)))
            selector_anchor_rows.append(
                (y_d_next, anchor, y_f_next, x_f, q)
            )
            selector_atoms.append(edge(q, y_d_next))

    circuit_offset = 2762
    w = 26
    support = {edge(i, (i + 1) % 26) for i in range(26)} | {edge(w, 0)}
    circuit_atoms_local = sorted(
        {edge(i, (i + 4) % 26) for i in range(26)}
        | {edge(w, 3), edge(w, 23)}
    )
    active_vertices = [(9 * k) % 26 for k in range(13)]
    active_core = {
        edge(active_vertices[i], active_vertices[i + 1])
        for i in range(12)
    }
    side.extend([i % 2 for i in range(26)] + [1])
    for u, v in sorted(support | active_core):
        b.add("blue", "circuit", circuit_offset + u, circuit_offset + v)
    circuit_core = {
        edge(circuit_offset + u, circuit_offset + v)
        for u, v in support | active_core
    }
    assert len(circuit_core) == 39

    circuit_atoms = []
    circuit_cycles: list[set[tuple[int, int]]] = []
    next_vertex = circuit_offset + 27
    for u_local, v_local in circuit_atoms_local:
        u, v = circuit_offset + u_local, circuit_offset + v_local
        atom = b.add("bad", "circuit", u, v)
        circuit_atoms.append(atom)
        internal = list(range(next_vertex, next_vertex + 5))
        next_vertex += 5
        for step in range(1, 6):
            side.append(side[u] ^ (step % 2))
        path = [u] + internal + [v]
        cycle = {atom}
        for x, y in zip(path, path[1:]):
            cycle.add(b.add("blue", "circuit", x, y))
        assert len(cycle) == 7 and len(set(path)) == 7
        circuit_cycles.append(cycle)
    assert next_vertex == 2929

    z_left, z_right = 2929, 2930
    next_vertex += 2
    side.extend((0, 0))
    midpoint = circuit_offset + 2
    for u, v in (
        (r, anchor),
        (anchor, midpoint),
        (c_left, z_left),
        (z_left, anchor),
        (c_right, z_right),
        (z_right, anchor),
    ):
        b.add("blue", "cable", u, v)

    seed_rows = []
    seed_atoms = []
    seed_cycles: list[set[tuple[int, int]]] = []
    for seed in (anchor, z_left, z_right):
        internal = list(range(next_vertex, next_vertex + 4))
        next_vertex += 4
        for step in range(1, 5):
            side.append(side[seed] ^ (step % 2))
        row = tuple([seed] + internal)
        cycle = set()
        for u, v in zip(row, row[1:]):
            cycle.add(b.add("blue", "seeds", u, v))
        atom = b.add("bad", "seeds", seed, internal[-1])
        cycle.add(atom)
        assert len(cycle) == 5 and len(set(row)) == 5
        seed_rows.append(row)
        seed_atoms.append(atom)
        seed_cycles.append(cycle)
    assert next_vertex == OFFSET and len(side) == OFFSET

    graph = b.blue | b.bad
    assert len(b.blue) == 7039
    assert len(b.bad) == 1383
    assert len(graph) == 8422
    assert b.blue.isdisjoint(b.bad)
    assert set().union(*b.classes.values()) == graph
    assert sum(map(len, b.classes.values())) == len(graph)
    assert {name: len(es) for name, es in b.classes.items()} == {
        "traffic": 4786,
        "selectors": 3380,
        "seeds": 15,
        "circuit": 235,
        "cable": 6,
    }
    assert all(side[u] != side[v] for u, v in b.blue)
    assert all(side[u] == side[v] for u, v in b.bad)

    adj_blue = adjacency(OFFSET, b.blue)
    circuit_rows = [
        unique_shortest_row(adj_blue, *atom) for atom in circuit_atoms
    ]
    default_rows = tuple(
        traffic_rows + selector_rows + circuit_rows + seed_rows
    )
    anchor_rows = tuple(
        traffic_rows + selector_anchor_rows + circuit_rows + seed_rows
    )
    atoms = tuple(
        traffic_atoms + selector_atoms + circuit_atoms + seed_atoms
    )
    assert len(default_rows) == len(anchor_rows) == len(atoms) == 1383
    for atom, row in zip(atoms, anchor_rows):
        assert edge(row[0], row[-1]) == atom
        assert len(row) == len(set(row)) == 5
        assert all(edge(u, v) in b.blue for u, v in zip(row, row[1:]))

    return {
        "n": OFFSET,
        "blue": b.blue,
        "bad": b.bad,
        "graph": graph,
        "side": tuple(side),
        "classes": b.classes,
        "selectorCycles": selector_cycles,
        "seedCycles": seed_cycles,
        "circuitCycles": circuit_cycles,
        "circuitCore": circuit_core,
        "defaultRows": default_rows,
        "anchorRows": anchor_rows,
        "atoms": atoms,
    }


def disjoint_cycle_union(
    cycles: list[set[tuple[int, int]]], expected: set[tuple[int, int]]
) -> None:
    seen: set[tuple[int, int]] = set()
    for cycle in cycles:
        assert seen.isdisjoint(cycle)
        seen.update(cycle)
    assert seen == expected


def traffic_quotient_certificate() -> dict[str, object]:
    t = 26
    best = -1
    achievers = []
    cases = 0
    for core in range(16):
        r = (core >> 0) & 1
        c_left = (core >> 1) & 1
        c_right = (core >> 2) & 1
        anchor = (core >> 3) & 1
        for left_one in range(t + 1):
            for right_one in range(t + 1):
                cases += 1
                value = int(r != c_left) + int(r != c_right)
                value += left_one * int(1 != c_left)
                value += (t - left_one) * int(0 != c_left)
                value += right_one * int(1 != c_right)
                value += (t - right_one) * int(0 != c_right)
                value += left_one * (t - right_one)
                value += (t - left_one) * right_one
                opposite = (
                    (left_one if anchor == 0 else t - left_one)
                    + (right_one if anchor == 0 else t - right_one)
                )
                value += t * (3 * opposite + 2 * (2 * t - opposite))
                witness = [r, c_left, c_right, anchor, left_one, right_one]
                if value > best:
                    best = value
                    achievers = [witness]
                elif value == best:
                    achievers.append(witness)
    assert cases == 11664 and best == 4110 and len(achievers) == 2
    return {"cases": cases, "maximum": best, "maximizers": achievers}


def maxcut_certificate(base: dict[str, object]) -> dict[str, object]:
    classes = base["classes"]
    assert isinstance(classes, dict)
    selectors = base["selectorCycles"]
    seeds = base["seedCycles"]
    circuit_cycles = base["circuitCycles"]
    circuit_core = base["circuitCore"]
    assert isinstance(selectors, list)
    assert isinstance(seeds, list)
    assert isinstance(circuit_cycles, list)
    assert isinstance(circuit_core, set)
    disjoint_cycle_union(selectors, classes["selectors"])
    disjoint_cycle_union(seeds, classes["seeds"])
    cycle_edges = set().union(*circuit_cycles)
    assert cycle_edges.isdisjoint(circuit_core)
    assert cycle_edges | circuit_core == classes["circuit"]

    quotient = traffic_quotient_certificate()
    upper = {
        "traffic": quotient["maximum"],
        "selectors": 4 * len(selectors),
        "seeds": 4 * len(seeds),
        "circuit": len(circuit_core) + 6 * len(circuit_cycles),
        "cable": len(classes["cable"]),
    }
    assert upper == {
        "traffic": 4110,
        "selectors": 2704,
        "seeds": 12,
        "circuit": 207,
        "cable": 6,
    }
    side = base["side"]
    attaining = {
        name: sum(side[u] != side[v] for u, v in es)
        for name, es in classes.items()
    }
    assert attaining == upper
    assert sum(upper.values()) == 7039
    return {
        "classEdgeCounts": {name: len(es) for name, es in classes.items()},
        "classUpperBounds": upper,
        "attainingClassCounts": attaining,
        "trafficQuotient": quotient,
        "baseUpper": 7039,
        "baseAttaining": 7039,
        "joinBridgeUpper": 1,
        "doubledUpper": 14079,
        "doubledAttaining": 14079,
    }


def shifted(edges: set[tuple[int, int]], delta: int) -> set[tuple[int, int]]:
    return {(u + delta, v + delta) for u, v in edges}


def shifted_rows(
    rows: tuple[tuple[int, ...], ...], delta: int
) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(v + delta for v in row) for row in rows)


def reconstruct_join(base: dict[str, object]) -> dict[str, object]:
    bridge = edge(3, OFFSET + 3)
    blue = set(base["blue"]) | shifted(base["blue"], OFFSET) | {bridge}
    bad = set(base["bad"]) | shifted(base["bad"], OFFSET)
    rows = tuple(base["anchorRows"]) + shifted_rows(base["anchorRows"], OFFSET)
    side = tuple(base["side"]) + tuple(1 - bit for bit in base["side"])
    return {
        "n": 2 * OFFSET,
        "blue": blue,
        "bad": bad,
        "graph": blue | bad,
        "rows": rows,
        "side": side,
        "bridge": bridge,
    }


class DSU:
    def __init__(self, vertices: set[int]) -> None:
        self.parent = {v: v for v in vertices}

    def find(self, v: int) -> int:
        root = v
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[v] != v:
            v, self.parent[v] = self.parent[v], root
        return root

    def union(self, u: int, v: int) -> None:
        ru, rv = self.find(u), self.find(v)
        if ru != rv:
            self.parent[max(ru, rv)] = min(ru, rv)


def selected_state(data: dict[str, object]) -> dict[str, object]:
    n = data["n"]
    rows = data["rows"]
    blue = data["blue"]
    bad = data["bad"]
    assert isinstance(n, int)
    pair: Counter[tuple[int, int]] = Counter()
    load: Counter[int] = Counter()
    support: set[tuple[int, int]] = set()
    selected: set[int] = set()
    for row in rows:
        assert len(row) == len(set(row)) == 5
        for x in row:
            selected.add(x)
            load[x] += 1
        for x in row:
            for y in row:
                pair[x, y] += 1
        support.update(edge(x, y) for x, y in zip(row, row[1:]))
    active_edges = {
        e for e in blue
        if e not in support and e[0] in selected and e[1] in selected
    }
    dsu = DSU(selected)
    for u, v in sorted(active_edges):
        dsu.union(u, v)
    component = {v: dsu.find(v) for v in selected}
    active_roots = {
        component[u]
        for u, v in bad
        if u in component and v in component and component[u] == component[v]
    }
    active = {v for v in selected if component[v] in active_roots}
    active_degree: Counter[int] = Counter()
    for u, v in active_edges:
        if component[u] in active_roots:
            active_degree[u] += 1
            active_degree[v] += 1
    pair_excess: Counter[int] = Counter()
    for (x, _y), count in pair.items():
        pair_excess[x] += max(0, count - 1)
    collision = {v: 2 * pair_excess[v] for v in active}
    hit_need = {
        v: max(0, active_degree[v] - max(0, n - 5 * load[v]))
        for v in active
    }
    return {
        "n": n,
        "pair": pair,
        "load": load,
        "support": support,
        "selected": selected,
        "activeEdges": active_edges,
        "component": component,
        "activeRoots": active_roots,
        "active": active,
        "activeDegree": active_degree,
        "collision": collision,
        "hitNeed": hit_need,
    }


def quiet_components(
    n: int, blue: set[tuple[int, int]], active: set[int]
) -> dict[str, object]:
    adj = adjacency(n, blue)
    component_of: dict[int, int] = {}
    vertices_by_root: dict[int, set[int]] = {}
    boundary_by_root: dict[int, set[int]] = {}
    for start in range(n):
        if start in active or start in component_of:
            continue
        vertices = {start}
        boundary: set[int] = set()
        component_of[start] = start
        todo = deque([start])
        while todo:
            u = todo.popleft()
            for v in adj[u]:
                if v in active:
                    boundary.add(v)
                elif v not in component_of:
                    component_of[v] = start
                    vertices.add(v)
                    todo.append(v)
        vertices_by_root[start] = vertices
        boundary_by_root[start] = boundary
    return {
        "componentOf": component_of,
        "vertices": vertices_by_root,
        "boundary": boundary_by_root,
    }


def signed_data(
    n: int, blue: set[tuple[int, int]], bad: set[tuple[int, int]]
) -> tuple[Counter[int], dict[tuple[int, int], int]]:
    degree: Counter[int] = Counter()
    sign: dict[tuple[int, int], int] = {}
    for e in blue:
        sign[e] = 1
        degree[e[0]] += 1
        degree[e[1]] += 1
    for e in bad:
        sign[e] = -1
        degree[e[0]] -= 1
        degree[e[1]] -= 1
    return degree, sign


def old_source_masks(
    data: dict[str, object],
    state: dict[str, object],
    owners: tuple[int, int, int],
    vertex_domain: range,
) -> dict[tuple[int, int, int], int]:
    pair = state["pair"]
    active_edges = state["activeEdges"]
    active = state["active"]
    degree, sign = signed_data(data["n"], data["blue"], data["bad"])
    masks: dict[tuple[int, int, int], int] = {}
    domain = tuple(vertex_domain)
    for owner_index, owner in enumerate(owners):
        owner_bit = 1 << owner_index
        for y in domain:
            if y == owner or pair[owner, y] != 0:
                continue
            for half in (0, 1):
                if not (
                    half == 0
                    and edge(owner, y) in active_edges
                    and owner in active
                ):
                    key = (owner, y, half)
                    masks[key] = masks.get(key, 0) | owner_bit
        companions = [x for x in domain if pair[owner, x] > 0]
        for x in companions:
            for y in companions:
                if x == y or pair[x, y] != 0:
                    continue
                e = edge(x, y)
                if degree[x] + degree[y] - 2 * sign.get(e, 0) < 0:
                    continue
                for half in (0, 1):
                    if not (
                        half == 0 and e in active_edges and x in active
                    ):
                        key = (x, y, half)
                        masks[key] = masks.get(key, 0) | owner_bit
    return masks


class Dinic:
    def __init__(self, n: int) -> None:
        self.graph: list[list[list[int]]] = [[] for _ in range(n)]

    def add_edge(self, u: int, v: int, capacity: int) -> int:
        forward = [v, len(self.graph[v]), capacity]
        backward = [u, len(self.graph[u]), 0]
        self.graph[u].append(forward)
        self.graph[v].append(backward)
        return len(self.graph[u]) - 1

    def max_flow(self, source: int, sink: int) -> int:
        total = 0
        n = len(self.graph)
        while True:
            level = [-1] * n
            level[source] = 0
            todo = deque([source])
            while todo:
                u = todo.popleft()
                for v, _rev, cap in self.graph[u]:
                    if cap > 0 and level[v] < 0:
                        level[v] = level[u] + 1
                        todo.append(v)
            if level[sink] < 0:
                return total
            cursor = [0] * n

            def send(u: int, amount: int) -> int:
                if u == sink:
                    return amount
                while cursor[u] < len(self.graph[u]):
                    i = cursor[u]
                    v, rev, cap = self.graph[u][i]
                    if cap > 0 and level[v] == level[u] + 1:
                        pushed = send(v, min(amount, cap))
                        if pushed:
                            self.graph[u][i][2] -= pushed
                            self.graph[v][rev][2] += pushed
                            return pushed
                    cursor[u] += 1
                return 0

            while True:
                pushed = send(source, 10**18)
                if not pushed:
                    break
                total += pushed


def hall_cuts(
    demands: tuple[int, int, int], masks: dict[tuple[int, int, int], int]
) -> list[dict[str, int]]:
    out = []
    for shore in range(1, 8):
        demand = sum(demands[i] for i in range(3) if shore & (1 << i))
        reach = sum(1 for mask in masks.values() if mask & shore)
        out.append(
            {"shoreMask": shore, "demand": demand, "reach": reach,
             "slack": reach - demand}
        )
    return out


def exact_matching(
    owners: tuple[int, int, int],
    demands: tuple[int, int, int],
    masks: dict[tuple[int, int, int], int],
    component_root: int,
) -> tuple[list[tuple[int, int, int, int, int]], int]:
    keys = sorted(masks)
    source = 0
    key_start = 1
    owner_start = key_start + len(keys)
    sink = owner_start + 3
    flow = Dinic(sink + 1)
    owner_arcs: dict[tuple[int, int], int] = {}
    for key_index, key in enumerate(keys):
        node = key_start + key_index
        flow.add_edge(source, node, 1)
        for owner_index in range(3):
            if masks[key] & (1 << owner_index):
                arc = flow.add_edge(node, owner_start + owner_index, 1)
                owner_arcs[key_index, owner_index] = arc
    for owner_index, demand in enumerate(demands):
        flow.add_edge(owner_start + owner_index, sink, demand)
    value = flow.max_flow(source, sink)
    assignments = []
    for key_index, key in enumerate(keys):
        node = key_start + key_index
        used = []
        for owner_index in range(3):
            arc = owner_arcs.get((key_index, owner_index))
            if arc is not None and flow.graph[node][arc][2] == 0:
                used.append(owner_index)
        assert len(used) <= 1
        if used:
            assignments.append((*key, owners[used[0]], component_root))
    assert len(assignments) == value
    return assignments, value


def canonical_graph_hash(
    n: int,
    blue: set[tuple[int, int]],
    bad: set[tuple[int, int]],
    rows: tuple[tuple[int, ...], ...],
) -> str:
    return sha256_bytes(json_bytes({
        "n": n,
        "blue": [list(e) for e in sorted(blue)],
        "bad": [list(e) for e in sorted(bad)],
        "rows": [list(row) for row in rows],
    }))


def main() -> None:
    manifest_audit = audit_manifest(ORIGINAL_MANIFEST)
    base = reconstruct_base()
    lead_result = json.loads(LEAD_RESULT.read_text(encoding="ascii"))
    base_default_hash = canonical_graph_hash(
        base["n"], base["blue"], base["bad"], base["defaultRows"]
    )
    assert base_default_hash == lead_result["sha256"]
    cut_certificate = maxcut_certificate(base)

    joined = reconstruct_join(base)
    n = joined["n"]
    blue = joined["blue"]
    bad = joined["bad"]
    graph = joined["graph"]
    side = joined["side"]
    assert n == 5886
    assert len(blue) == 14079
    assert len(bad) == 2766
    assert len(graph) == 16845
    assert blue.isdisjoint(bad)
    assert sum(side[u] != side[v] for u, v in graph) == 14079
    assert all(side[u] != side[v] for u, v in blue)
    assert all(side[u] == side[v] for u, v in bad)

    graph_adj = adjacency(n, graph)
    triangle_witness = next(
        (
            (u, v, min(graph_adj[u] & graph_adj[v]))
            for u, v in sorted(graph)
            if graph_adj[u] & graph_adj[v]
        ),
        None,
    )
    assert triangle_witness is None
    blue_adj = adjacency(n, blue)
    connected_vertices = {0}
    todo = deque([0])
    while todo:
        u = todo.popleft()
        for v in blue_adj[u]:
            if v not in connected_vertices:
                connected_vertices.add(v)
                todo.append(v)
    assert len(connected_vertices) == n

    distance_histogram: Counter[int] = Counter()
    for u, v in sorted(bad):
        distance_histogram[bfs_distances(blue_adj, u)[v]] += 1
    assert distance_histogram == {4: 2766}
    gamma = sum((distance + 1) ** 2 * count
                for distance, count in distance_histogram.items())
    assert gamma == 69150

    base_state_data = {
        "n": base["n"],
        "blue": base["blue"],
        "bad": base["bad"],
        "rows": base["anchorRows"],
    }
    base_state = selected_state(base_state_data)
    joined_state = selected_state(joined)
    assert len(base_state["active"]) == 19
    assert len(joined_state["active"]) == 38
    assert joined_state["activeRoots"] == {0, OFFSET}
    owners_left = (0, 1, 2)
    owners_right = tuple(v + OFFSET for v in owners_left)
    assert all(joined_state["component"][v] == 0 for v in owners_left)
    assert all(joined_state["component"][v] == OFFSET for v in owners_right)

    quiet = quiet_components(n, blue, joined_state["active"])
    quiet_root = quiet["componentOf"][3]
    assert quiet["componentOf"][OFFSET + 3] == quiet_root
    quiet_vertices = quiet["vertices"][quiet_root]
    quiet_boundary = quiet["boundary"][quiet_root]
    assert len(quiet_vertices) == 2758
    assert quiet_boundary == {1, 55, OFFSET + 1, OFFSET + 55}
    switch_blue = sum((u in quiet_vertices) != (v in quiet_vertices)
                      for u, v in blue)
    switch_bad = sum((u in quiet_vertices) != (v in quiet_vertices)
                     for u, v in bad)
    assert (switch_blue, switch_bad, switch_blue - switch_bad) == (1404, 1352, 52)

    def p5_witness(source: tuple[int, int], owner: int) -> tuple[int, int] | None:
        x, y = source
        if x == y or joined_state["pair"][x, y] != 0:
            return None
        if x in joined_state["active"] or y in joined_state["active"]:
            return None
        root_x = quiet["componentOf"][x]
        root_y = quiet["componentOf"][y]
        owner_root = joined_state["component"].get(owner)
        if owner_root not in joined_state["activeRoots"]:
            return None
        attach_x = [
            a for a in quiet["boundary"][root_x]
            if joined_state["pair"][owner, a] > 0
            and joined_state["component"].get(a) == owner_root
        ]
        attach_y = [
            a for a in quiet["boundary"][root_y]
            if joined_state["pair"][owner, a] > 0
            and joined_state["component"].get(a) == owner_root
        ]
        if not attach_x or not attach_y:
            return None
        return min(attach_x), min(attach_y)

    shared_base_key = (3, 56)
    eligible = {
        owner: p5_witness(shared_base_key, owner)
        for owner in owners_left + owners_right
    }
    assert all(witness is not None for witness in eligible.values())
    eligible_roots = {
        joined_state["component"][owner] for owner in eligible
    }
    assert eligible_roots == {0, OFFSET}
    assert joined_state["pair"][shared_base_key] == 0
    assert shared_base_key[0] not in joined_state["active"]
    assert shared_base_key[1] not in joined_state["active"]
    split_assignment = [
        [3, 56, 0, 0, 0],
        [3, 56, 1, OFFSET, OFFSET],
    ]
    assert split_assignment[0][:2] == split_assignment[1][:2]
    assert split_assignment[0][2] != split_assignment[1][2]
    assert split_assignment[0][4] != split_assignment[1][4]

    base_old_masks = old_source_masks(
        base_state_data, base_state, owners_left, range(OFFSET)
    )
    assert len(base_old_masks) == 19925
    old_histogram = Counter(base_old_masks.values())
    assert old_histogram == {1: 5775, 2: 5775, 4: 5775, 7: 2600}
    collision_demands = tuple(base_state["collision"][v] for v in owners_left)
    base_profile_demands = tuple(
        base_state["collision"][v] + base_state["hitNeed"][v]
        for v in owners_left
    )
    joined_left_demands = tuple(
        joined_state["collision"][v] for v in owners_left
    )
    joined_right_demands = tuple(
        joined_state["collision"][v] for v in owners_right
    )
    assert collision_demands == (6650, 6650, 6650)
    assert base_profile_demands == (6651, 6651, 6651)
    assert joined_left_demands == joined_right_demands == collision_demands
    assert tuple(base_state["hitNeed"][v] for v in owners_left) == (1, 1, 1)
    assert tuple(joined_state["hitNeed"][v] for v in owners_left) == (0, 0, 0)
    assert tuple(joined_state["hitNeed"][v] for v in owners_right) == (0, 0, 0)

    global_left_masks = old_source_masks(
        joined, joined_state, owners_left, range(OFFSET)
    )
    global_right_masks_raw = old_source_masks(
        joined, joined_state, owners_right, range(OFFSET, 2 * OFFSET)
    )
    for key, mask in base_old_masks.items():
        assert global_left_masks.get(key, 0) & mask == mask
    shifted_old_masks = {
        (x + OFFSET, y + OFFSET, half): mask
        for (x, y, half), mask in base_old_masks.items()
    }
    for key, mask in shifted_old_masks.items():
        assert global_right_masks_raw.get(key, 0) & mask == mask

    p5_left = {
        (3, 56 + 2 * j, half): 7
        for j in range(14) for half in (0, 1)
    }
    p5_right = {
        (x + OFFSET, y + OFFSET, half): mask
        for (x, y, half), mask in p5_left.items()
    }
    assert len(p5_left) == len(p5_right) == 28
    assert set(p5_left).isdisjoint(base_old_masks)
    assert set(p5_right).isdisjoint(shifted_old_masks)
    for x, y, _half in p5_left:
        assert all(p5_witness((x, y), owner) is not None
                   for owner in owners_left + owners_right)
    for x, y, _half in p5_right:
        assert all(p5_witness((x, y), owner) is not None
                   for owner in owners_left + owners_right)

    repaired_left = dict(base_old_masks)
    repaired_left.update(p5_left)
    repaired_right = dict(shifted_old_masks)
    repaired_right.update(p5_right)
    assert len(repaired_left) == len(repaired_right) == sum(base_profile_demands)
    before_cuts = hall_cuts(collision_demands, base_old_masks)
    after_left_cuts = hall_cuts(collision_demands, repaired_left)
    after_right_cuts = hall_cuts(collision_demands, repaired_right)
    assert min(cut["slack"] for cut in before_cuts) == -25
    assert [cut for cut in before_cuts if cut["slack"] < 0] == [{
        "shoreMask": 7, "demand": 19950, "reach": 19925, "slack": -25
    }]
    assert min(cut["slack"] for cut in after_left_cuts) == 3
    assert after_left_cuts == after_right_cuts

    left_assignment, left_flow = exact_matching(
        owners_left, collision_demands, repaired_left, 0
    )
    right_assignment, right_flow = exact_matching(
        owners_right, collision_demands, repaired_right, OFFSET
    )
    assert left_flow == right_flow == 19950
    assignments = sorted(left_assignment + right_assignment)
    assert len(assignments) == 39900
    full_keys = {(x, y, half) for x, y, half, _owner, _root in assignments}
    assert len(full_keys) == len(assignments)
    roots_by_base: dict[tuple[int, int], set[int]] = defaultdict(set)
    for x, y, _half, _owner, root in assignments:
        roots_by_base[x, y].add(root)
    assert all(len(roots) == 1 for roots in roots_by_base.values())
    p5_used_left = sum(
        (x, y, half) in p5_left for x, y, half, _o, _r in assignments
    )
    p5_used_right = sum(
        (x, y, half) in p5_right for x, y, half, _o, _r in assignments
    )
    assert p5_used_left >= 25 and p5_used_right >= 25

    stress_left_assignment, stress_left_flow = exact_matching(
        owners_left, base_profile_demands, repaired_left, 0
    )
    stress_right_assignment, stress_right_flow = exact_matching(
        owners_right, base_profile_demands, repaired_right, OFFSET
    )
    assert stress_left_flow == stress_right_flow == 19953
    stress_roots_by_base: dict[tuple[int, int], set[int]] = defaultdict(set)
    for x, y, _half, _owner, root in (
        stress_left_assignment + stress_right_assignment
    ):
        stress_roots_by_base[x, y].add(root)
    assert all(len(roots) == 1 for roots in stress_roots_by_base.values())

    assignment_payload = {
        "schema": "R32_JOIN5886_COHERENT_ASSIGNMENT_V1",
        "arithmetic": "integer-only",
        "columns": ["sourceX", "sourceY", "half", "owner", "componentRoot"],
        "assignments": [list(item) for item in assignments],
    }
    assignment_path = HERE / "coherent_assignment.json"
    assignment_path.write_text(
        json.dumps(assignment_payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    assignment_sha = sha256_file(assignment_path)

    joined_hash = canonical_graph_hash(n, blue, bad, joined["rows"])
    original_result = json.loads(ORIGINAL_RESULT.read_text(encoding="ascii"))
    assert original_result["graph"]["n"] == n
    assert original_result["graph"]["edges"] == len(graph)
    assert original_result["graph"]["blue"] == len(blue)
    assert original_result["graph"]["bad"] == len(bad)
    assert original_result["graph"]["gamma"] == gamma
    assert original_result["pattern5"]["sourceBaseKey"] == list(shared_base_key)
    assert original_result["pattern5"]["eligibleDestinationRoots"] == [0, OFFSET]

    input_paths = {
        "doubledCageFalsifier": ORIGINAL_DIR / "doubled_cage_falsifier.py",
        "doubledCageResult": ORIGINAL_RESULT,
        "baseBuilder": ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py",
        "baseLeadResult": LEAD_RESULT,
        "baseMaxCutCertificate": ROOT / "tmp/fanout/r29_gate/d03/retry2/certificate.json",
        "pattern5PythonGate": ROOT / "problems/23/writeup/_claude_r29_pattern5_gate.py",
        "checkedPattern5Lean": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/CheckedQuiescentAttachmentBaseTerminal.lean",
        "residualTokenizationLean": ROOT / "problems/23/lean/Erdos23Delta0/ResidualSourceTokenization.lean",
        "staticOwnershipLean": ORIGINAL_DIR / "StaticOwnership.lean",
    }
    input_hashes = {
        name: {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(path),
        }
        for name, path in input_paths.items()
    }

    result = {
        "schema": "R32_JOIN5886_INDEPENDENT_EXACT_GATE_V1",
        "arithmetic": "integer-only",
        "independence": {
            "importsCandidateDoubledScript": False,
            "importsR29Builder": False,
            "importsClaudePattern5Gate": False,
            "constructor": "standalone five-edge-class reconstruction",
            "baseCanonicalSHA256": base_default_hash,
            "baseCanonicalMatchesR29Lead": True,
            "joinedAllAnchorCanonicalSHA256": joined_hash,
        },
        "inputIntegrity": {
            "originalManifest": manifest_audit,
            "inputs": input_hashes,
        },
        "graph": {
            "n": n,
            "edges": len(graph),
            "blue": len(blue),
            "bad": len(bad),
            "bridge": list(joined["bridge"]),
            "triangleFree": True,
            "blueConnected": True,
            "badBlueDistanceHistogram": {
                str(k): v for k, v in sorted(distance_histogram.items())
            },
            "gamma": gamma,
        },
        "maxCut": cut_certificate,
        "selectedState": {
            "rows": len(joined["rows"]),
            "activeVertices": len(joined_state["active"]),
            "activeComponentRoots": sorted(joined_state["activeRoots"]),
            "ownerComponents": {
                str(owner): joined_state["component"][owner]
                for owner in owners_left + owners_right
            },
        },
        "pattern5SharedKey": {
            "sourceBaseKey": list(shared_base_key),
            "pairCount": joined_state["pair"][shared_base_key],
            "sourceVerticesQuiescent": True,
            "bothHalvesUnreserved": True,
            "quiescentComponentSize": len(quiet_vertices),
            "boundary": sorted(quiet_boundary),
            "switchBlueBoundary": switch_blue,
            "switchBadBoundary": switch_bad,
            "switchLoss": switch_blue - switch_bad,
            "eligibleOwners": {
                str(owner): {
                    "componentRoot": joined_state["component"][owner],
                    "attachX": eligible[owner][0],
                    "attachY": eligible[owner][1],
                }
                for owner in eligible
            },
            "eligibleDestinationRoots": sorted(eligible_roots),
        },
        "relationLevelUniqueness": {
            "holds": False,
            "counterexampleAssignments": split_assignment,
            "reason": "one ordered-pair base key is P5-eligible in roots 0 and 2943",
        },
        "coherenceConstrainedRepair": {
            "holds": True,
            "method": "copy-local old relation plus 14 local P5 base keys per root",
            "obligationClass": "collision debits (FreeHalf-only in R32)",
            "perComponentDemand": sum(collision_demands),
            "perOwnerDemand": list(collision_demands),
            "joinedHitNeedPerOwner": [0, 0, 0],
            "oldSourceKeysPerComponent": len(base_old_masks),
            "oldMaskHistogram": {str(k): v for k, v in sorted(old_histogram.items())},
            "oldHallCuts": before_cuts,
            "p5HalfKeysPerComponent": 28,
            "repairedHallCuts": after_left_cuts,
            "exactFlowPerComponent": [left_flow, right_flow],
            "combinedAssignments": len(assignments),
            "p5KeysUsedPerComponent": [p5_used_left, p5_used_right],
            "fullKeyInjective": True,
            "baseKeyComponentCoherent": True,
            "assignmentFile": assignment_path.name,
            "assignmentSHA256": assignment_sha,
            "base2943CombinedCollisionHitStress": {
                "perOwnerDemand": list(base_profile_demands),
                "exactFlowPerComponent": [stress_left_flow, stress_right_flow],
                "baseKeyComponentCoherent": True,
                "note": "auxiliary stress profile; joined hit need is zero at N=5886",
            },
        },
        "verdicts": {
            "structuralAndExactNumericGate": "PASS",
            "relationBaseComponentUnique": "FALSIFIED",
            "coherenceConstrainedPerComponentRepair": "PASS",
            "mainTheoremClaimed": False,
        },
    }
    result_path = HERE / "result.json"
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    log_lines = [
        "PASS integer-only independent reconstruction",
        "PASS original manifest entries 7/7",
        "PASS triangle-free and connected blue graph n=5886 edges=16845",
        "PASS exact MaxCut upper=attaining=14079",
        "PASS bad blue distances {4:2766} Gamma=69150",
        "PASS shared P5 base key (3,56) eligible in roots 0 and 2943",
        "PASS RelationBaseComponentUnique falsified by split halves",
        "PASS coherent collision flows 19950+19950 assignments=39900 defect=0+0",
        "PASS auxiliary 2943 collision+hit stress flows 19953+19953",
        f"RESULT_SHA256 {sha256_file(result_path)}",
        f"ASSIGNMENT_SHA256 {assignment_sha}",
    ]
    (HERE / "gate.log").write_text("\n".join(log_lines) + "\n", encoding="ascii")
    print("\n".join(log_lines))


if __name__ == "__main__":
    main()
