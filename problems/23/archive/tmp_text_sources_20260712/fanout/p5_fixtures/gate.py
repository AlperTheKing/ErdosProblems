"""Independent exact Pattern-5 fixture gate for the R30 transfer relation.

This gate reconstructs the literal FreeHalf keys, scoped reservations, owner
demands, P1--P4 availability, and Pattern-5 quiescent-component availability.
It uses integers only.  The owner-shore reduction is exact because all demand
objects with the same owner have the same source neighbourhood.

The full semantic P5 pool and the checked certificate pool are kept separate.
For N=2943 the checked pool is exactly the 28 R30 keys, so the claimed
zero-slack certificate is tested without silently adding other eligible keys.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BIT_COUNT = tuple(i.bit_count() for i in range(256))
BYTE_BITS = tuple(tuple(j for j in range(8) if i & (1 << j)) for i in range(256))

Edge = tuple[int, int]
Row = tuple[int, int, int, int, int]


def edge(x: int, y: int) -> Edge:
    return (x, y) if x < y else (y, x)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class Fixture:
    name: str
    n: int
    blue: frozenset[Edge]
    bad: frozenset[Edge]
    atoms: tuple[Edge, ...]
    rows: tuple[Row, ...]
    metadata: dict


class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> None:
        x, y = self.find(x), self.find(y)
        if x != y:
            self.parent[max(x, y)] = min(x, y)


def adjacency(n: int, edges: Iterable[Edge]) -> list[set[int]]:
    out = [set() for _ in range(n)]
    for x, y in edges:
        out[x].add(y)
        out[y].add(x)
    return out


def build_24() -> Fixture:
    left = (0, 1, 2)
    right = (3, 4, 5)
    u, w, v = 6, 7, 8
    a_l = (9, 10, 11)
    z_l = (12, 13, 14)
    middle = (15, 16, 17)
    z_r = (18, 19, 20)
    a_r = (21, 22, 23)
    blue: set[Edge] = set()

    def link(xs, ys):
        blue.update(edge(x, y) for x in xs for y in ys)

    blue.update(edge(x, u) for x in left)
    blue.update((edge(u, w), edge(w, v)))
    blue.update(edge(v, y) for y in right)
    link(left, a_l)
    link(a_l, z_l)
    link(z_l, middle)
    link(middle, z_r)
    link(z_r, a_r)
    link(a_r, right)
    atoms = tuple(edge(x, y) for x in left for y in right)
    rows = tuple((x, u, w, v, y) for x in left for y in right)
    return Fixture("24", 24, frozenset(blue), frozenset(atoms), atoms, rows,
                   {"constructor": "independent R1 double-star/web reconstruction"})


def build_167_or_175(order: int) -> Fixture:
    if order not in (167, 175):
        raise ValueError(order)
    blue: set[Edge] = {edge(i, (i + 1) % 26) for i in range(26)}
    blue.add(edge(26, 0))
    atom_list = [edge(i, (i + 4) % 26) for i in range(26)]
    atom_list.extend((edge(26, 3), edge(26, 23)))
    rows: list[Row] = [tuple((i + j) % 26 for j in range(5)) for i in range(26)]
    rows.extend(((26, 0, 1, 2, 3), (26, 0, 25, 24, 23)))
    internal_path = [0]
    for _ in range(12):
        internal_path.append((internal_path[-1] + 9) % 26)
    blue.update(edge(x, y) for x, y in zip(internal_path, internal_path[1:]))
    nxt = 27
    for x, y in atom_list:
        private = list(range(nxt, nxt + 5))
        nxt += 5
        chain = [x, *private, y]
        blue.update(edge(a, b) for a, b in zip(chain, chain[1:]))
    assert nxt == 167
    if order == 175:
        x, y, z = 167, 168, 169
        blue.update((edge(x, 0), edge(9, y), edge(y, z)))
        atom_list.append(edge(x, z))
        rows.append((x, 0, 9, y, z))
        private = list(range(170, 175))
        chain = [x, *private, z]
        blue.update(edge(a, b) for a, b in zip(chain, chain[1:]))
        nxt = 175
    return Fixture(str(order), nxt, frozenset(blue), frozenset(atom_list),
                   tuple(atom_list), tuple(rows),
                   {"constructor": f"independent R15/R18 N={order} reconstruction"})


def build_311() -> Fixture:
    blue: set[Edge] = {edge(i, (i + 1) % 26) for i in range(26)}
    blue.add(edge(26, 0))
    atoms = [edge(i, (i + 4) % 26) for i in range(26)]
    atoms.extend((edge(26, 3), edge(26, 23)))
    rows: list[Row] = [tuple((i + j) % 26 for j in range(5)) for i in range(26)]
    rows.extend(((26, 0, 1, 2, 3), (26, 0, 25, 24, 23)))
    path = [0]
    for _ in range(12):
        path.append((path[-1] + 9) % 26)
    blue.update(edge(x, y) for x, y in zip(path, path[1:]))
    nxt = 27
    for x, y in atoms[:28]:
        private = list(range(nxt, nxt + 5))
        nxt += 5
        chain = [x, *private, y]
        blue.update(edge(a, b) for a, b in zip(chain, chain[1:]))
    owner = 9
    p0 = tuple(range(nxt, nxt + 8)); nxt += 8
    p1 = tuple(range(nxt, nxt + 64)); nxt += 64
    p3 = tuple(range(nxt, nxt + 64)); nxt += 64
    p4 = tuple(range(nxt, nxt + 8)); nxt += 8
    blue.update(edge(x, y) for x in p0 for y in p1)
    blue.update(edge(y, owner) for y in p1)
    blue.update(edge(owner, y) for y in p3)
    blue.update(edge(x, y) for x in p3 for y in p4)
    attachment_oriented = [(x, y) for x in p4 for y in p0]
    attachment_atoms = [edge(x, y) for x, y in attachment_oriented]
    atoms.extend(attachment_atoms)
    rows.extend((x, p3[0], owner, p1[0], y) for x, y in attachment_oriented)
    assert nxt == 311
    return Fixture("311", nxt, frozenset(blue), frozenset(atoms), tuple(atoms),
                   tuple(rows), {"constructor": "independent R20 lex-row reconstruction"})


def build_89() -> Fixture:
    root, c_l, c_r = 0, 1, 2
    left = (3, 4, 5, 6)
    right = (7, 8, 9, 10, 11)
    anchor = 12
    locks = (0, 0, 0, 4, 6, 4, 5, 5, 3, 3, 3, 5)
    blue = {edge(root, c_l), edge(root, c_r)}
    blue.update(edge(c_l, x) for x in left)
    blue.update(edge(c_r, y) for y in right)
    atoms = tuple(edge(x, y) for x in left for y in right)
    rows = tuple((x, c_l, root, c_r, y) for x in left for y in right)
    nxt = 13
    for owner, count in enumerate(locks):
        for _ in range(count):
            x, y = nxt, nxt + 1
            nxt += 2
            blue.update((edge(owner, x), edge(x, y), edge(y, anchor)))
    assert nxt == 89
    return Fixture("89", nxt, frozenset(blue), frozenset(atoms), atoms, rows,
                   {"constructor": "independent R22 reconstruction"})


def lex_shortest_row(adj: list[set[int]], source: int, target: int) -> Row:
    dist = [-1] * len(adj)
    dist[target] = 0
    queue = deque([target])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1
                queue.append(y)
    if dist[source] != 4:
        raise AssertionError((source, target, dist[source]))
    row = [source]
    while row[-1] != target:
        x = row[-1]
        row.append(min(y for y in adj[x] if dist[y] == dist[x] - 1))
    if len(row) != 5:
        raise AssertionError(row)
    return tuple(row)  # type: ignore[return-value]


def build_3892() -> Fixture:
    path = ROOT / "problems/23/writeup/_codex_endpointflow_3892_counterexample.py"
    module = load_module("p5_fixture_3892", path)
    side, edges, blue, bad, _locks, nxt = module.build_locked_core()
    blowups = {}
    for owner in module.ATTACHMENTS:
        nxt, parts, _cycles = module.add_c5_blowup(
            side, edges, blue, bad, nxt, owner
        )
        blowups[owner] = parts
    assert nxt == 3892
    adj = adjacency(nxt, blue)
    core_bad = tuple(sorted(module.CORE_BAD))
    atoms: list[Edge] = list(core_bad)
    rows: list[Row] = [lex_shortest_row(adj, x, y) for x, y in core_bad]
    for owner in module.ATTACHMENTS:
        parts = blowups[owner]
        for a4 in parts[4]:
            for a0 in parts[0]:
                atom = edge(a4, a0)
                atoms.append(atom)
                rows.append((a4, min(parts[3]), owner, min(parts[1]), a0))
    assert len(atoms) == len(bad) == 1581
    return Fixture("3892", nxt, frozenset(blue), frozenset(bad), tuple(atoms),
                   tuple(rows), {
                       "constructor": str(path.relative_to(ROOT)),
                       "constructor_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                       "row_choice": "lexicographic core and lexicographic blow-up middles",
                   })


def build_2943() -> Fixture:
    path = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
    module = load_module("p5_fixture_2943", path)
    data = module.build()
    rows = list(tuple(row) for row in data["rows"])
    start = data["selectorStart"]
    for j, meta in enumerate(data["selectorMeta"]):
        rows[start + j] = tuple(meta["anchorRow"])
    assert len(rows) == len(data["atoms"]) == len(data["bad"]) == 1383
    return Fixture("2943", data["n"], frozenset(data["blue"]),
                   frozenset(data["bad"]), tuple(map(lambda e: edge(*e), data["atoms"])),
                   tuple(rows), {
                       "constructor": str(path.relative_to(ROOT)),
                       "constructor_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                       "row_choice": "all-anchor selector tuple",
                       "selector_range": [data["selectorStart"], data["selectorStop"]],
                   })


def validate_fixture(fixture: Fixture) -> dict:
    if fixture.blue & fixture.bad:
        raise AssertionError("blue/bad overlap")
    if len(fixture.atoms) != len(fixture.rows):
        raise AssertionError("atom/row length")
    if Counter(fixture.atoms) != Counter(fixture.bad):
        raise AssertionError("rows do not cover each bad edge exactly once")
    for atom, row in zip(fixture.atoms, fixture.rows):
        if len(row) != 5 or len(set(row)) != 5:
            raise AssertionError((atom, row))
        if edge(row[0], row[-1]) != atom:
            raise AssertionError((atom, row))
        if any(edge(x, y) not in fixture.blue for x, y in zip(row, row[1:])):
            raise AssertionError((atom, row, "nonblue step"))
    return {
        "n": fixture.n,
        "blue_edges": len(fixture.blue),
        "bad_edges": len(fixture.bad),
        "rows": len(fixture.rows),
        "all_rows_distinct_vertices": True,
        "all_rows_blue_length4": True,
        "all_bad_edges_covered_once": True,
    }


@dataclass
class ComponentSystem:
    excluded: frozenset[int]
    comp_id: list[int]
    components: list[tuple[int, ...]]
    boundaries: list[frozenset[int]]
    losses: list[int]
    cross_signed: Counter

    def union_loss(self, left: int, right: int) -> int:
        if left == right:
            return self.losses[left]
        key = edge(left, right)
        return self.losses[left] + self.losses[right] - 2 * self.cross_signed[key]


def component_system(
    n: int,
    blue: frozenset[Edge],
    bad: frozenset[Edge],
    adj: list[set[int]],
    signed_degree: list[int],
    excluded: set[int],
) -> ComponentSystem:
    comp_id = [-1] * n
    components: list[tuple[int, ...]] = []
    boundaries: list[frozenset[int]] = []
    for root in range(n):
        if root in excluded or comp_id[root] >= 0:
            continue
        cid = len(components)
        comp_id[root] = cid
        vertices = []
        boundary = set()
        queue = deque([root])
        while queue:
            x = queue.popleft()
            vertices.append(x)
            for y in adj[x]:
                if y in excluded:
                    boundary.add(y)
                elif comp_id[y] < 0:
                    comp_id[y] = cid
                    queue.append(y)
        components.append(tuple(sorted(vertices)))
        boundaries.append(frozenset(boundary))

    internal_signed = [0] * len(components)
    cross_signed: Counter = Counter()
    for sign, edges in ((1, blue), (-1, bad)):
        for x, y in edges:
            cx, cy = comp_id[x], comp_id[y]
            if cx >= 0 and cy >= 0:
                if cx == cy:
                    internal_signed[cx] += sign
                else:
                    cross_signed[edge(cx, cy)] += sign
    losses = [
        sum(signed_degree[x] for x in component) - 2 * internal_signed[cid]
        for cid, component in enumerate(components)
    ]
    return ComponentSystem(frozenset(excluded), comp_id, components,
                           boundaries, losses, cross_signed)


def bitset_size(n: int) -> int:
    return (2 * n * n + 7) // 8


def source_index(n: int, x: int, y: int, half: int) -> int:
    return 2 * (x * n + y) + half


def has_bit(bits: bytearray | bytes, index: int) -> bool:
    return bool(bits[index >> 3] & (1 << (index & 7)))


def clear_bit(bits: bytearray, index: int) -> None:
    bits[index >> 3] &= ~(1 << (index & 7)) & 255


def set_pair(bits: bytearray, n: int, x: int, y: int) -> int:
    base = source_index(n, x, y, 0)
    byte_index = base >> 3
    mask = 3 << (base & 7)
    new = mask & (~bits[byte_index] & 255)
    bits[byte_index] |= mask
    return BIT_COUNT[new]


def set_key(bits: bytearray, n: int, x: int, y: int, half: int) -> int:
    index = source_index(n, x, y, half)
    byte_index = index >> 3
    mask = 1 << (index & 7)
    new = not (bits[byte_index] & mask)
    bits[byte_index] |= mask
    return int(new)


def count_bits(bits: bytearray | bytes) -> int:
    return sum(BIT_COUNT[x] for x in bits)


def or_delta(target: bytearray, source: bytearray | bytes) -> int:
    added = 0
    for i, value in enumerate(source):
        new = value & (~target[i] & 255)
        added += BIT_COUNT[new]
        target[i] |= value
    return added


def new_against(left: bytearray | bytes, right: bytearray | bytes) -> int:
    return sum(BIT_COUNT[x & (~y & 255)] for x, y in zip(left, right))


def bitset_sha(bits: bytearray | bytes) -> str:
    return hashlib.sha256(bits).hexdigest()


def relation_for_components(
    n: int,
    pair: list[Counter],
    system: ComponentSystem,
    eligible: tuple[int, ...],
) -> tuple[bytearray, dict]:
    bits = bytearray(bitset_size(n))
    checked_pairs = 0
    min_loss = None
    for left in eligible:
        for right in eligible:
            loss = system.union_loss(left, right)
            checked_pairs += 1
            min_loss = loss if min_loss is None else min(min_loss, loss)
            if loss < 0:
                continue
            for x in system.components[left]:
                for y in system.components[right]:
                    if x != y and pair[x].get(y, 0) == 0:
                        set_pair(bits, n, x, y)
    return bits, {
        "eligible_components": len(eligible),
        "eligible_vertices": sum(len(system.components[c]) for c in eligible),
        "component_pairs_checked": checked_pairs,
        "minimum_switch_loss": min_loss,
        "negative_component_pairs": sum(
            system.union_loss(i, j) < 0 for i in eligible for j in eligible
        ),
    }


def owner_mask_histogram(
    old: list[bytearray],
    extra: list[bytearray] | None = None,
) -> Counter:
    if not old:
        return Counter()
    length = len(old[0])
    hist: Counter = Counter()
    for offset in range(length):
        values = []
        union = 0
        for i, bits in enumerate(old):
            value = bits[offset]
            if extra is not None:
                value |= extra[i][offset]
            values.append(value)
            union |= value
        for bit in BYTE_BITS[union]:
            mask = 0
            flag = 1 << bit
            for owner_index, value in enumerate(values):
                if value & flag:
                    mask |= 1 << owner_index
            hist[mask] += 1
    return hist


def dinic(node_count: int, source: int, sink: int, arcs) -> tuple[int, set[int]]:
    graph = [[] for _ in range(node_count)]

    def add(x: int, y: int, capacity: int) -> None:
        graph[x].append([y, capacity, len(graph[y])])
        graph[y].append([x, 0, len(graph[x]) - 1])

    for x, y, capacity in arcs:
        add(x, y, capacity)
    flow = 0
    while True:
        level = [-1] * node_count
        level[source] = 0
        queue = deque([source])
        while queue:
            x = queue.popleft()
            for y, capacity, _ in graph[x]:
                if capacity > 0 and level[y] < 0:
                    level[y] = level[x] + 1
                    queue.append(y)
        if level[sink] < 0:
            reachable = {source}
            queue = deque([source])
            while queue:
                x = queue.popleft()
                for y, capacity, _ in graph[x]:
                    if capacity > 0 and y not in reachable:
                        reachable.add(y)
                        queue.append(y)
            return flow, reachable
        cursor = [0] * node_count

        def send(x: int, amount: int) -> int:
            if x == sink:
                return amount
            while cursor[x] < len(graph[x]):
                item = graph[x][cursor[x]]
                y, capacity, reverse = item
                if capacity > 0 and level[y] == level[x] + 1:
                    pushed = send(y, min(amount, capacity))
                    if pushed:
                        item[1] -= pushed
                        graph[y][reverse][1] += pushed
                        return pushed
                cursor[x] += 1
            return 0

        while True:
            pushed = send(source, 1 << 62)
            if not pushed:
                break
            flow += pushed


def hall_gate(
    label: str,
    owners: list[int],
    demand: dict[int, int],
    hist: Counter,
) -> tuple[dict, list[dict]]:
    owner_count = len(owners)
    total_demand = sum(demand[x] for x in owners)
    masks = sorted(mask for mask, count in hist.items() if mask and count)
    source = 0
    owner_base = 1
    mask_base = owner_base + owner_count
    sink = mask_base + len(masks)
    inf = total_demand + 1
    arcs = [(source, owner_base + i, demand[owner]) for i, owner in enumerate(owners)]
    for i in range(owner_count):
        for j, mask in enumerate(masks):
            if mask & (1 << i):
                arcs.append((owner_base + i, mask_base + j, inf))
    arcs.extend((mask_base + j, sink, hist[mask]) for j, mask in enumerate(masks))
    flow, reachable = dinic(sink + 1, source, sink, arcs)
    mincut_owners = [owners[i] for i in range(owner_count) if owner_base + i in reachable]

    rows = []
    exhaustive = owner_count <= 22
    minimum_slack = None
    zero_masks = []
    negative_masks = []
    shore_sha = None
    if exhaustive:
        size = 1 << owner_count
        subset_hist = [0] * size
        for mask, count in hist.items():
            subset_hist[mask] += count
        for bit in range(owner_count):
            step = 1 << bit
            for mask in range(size):
                if mask & step:
                    subset_hist[mask] += subset_hist[mask ^ step]
        demand_sum = [0] * size
        for mask in range(1, size):
            low = mask & -mask
            i = low.bit_length() - 1
            demand_sum[mask] = demand_sum[mask ^ low] + demand[owners[i]]
        full = size - 1
        payload = hashlib.sha256()
        total_sources = sum(hist.values())
        for shore in range(1, size):
            reach = total_sources - subset_hist[full ^ shore]
            slack = reach - demand_sum[shore]
            record = {
                "mask": shore,
                "owners": [owners[i] for i in range(owner_count) if shore & (1 << i)],
                "demand": demand_sum[shore],
                "reach": reach,
                "slack": slack,
            }
            rows.append(record)
            payload.update((json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode())
            minimum_slack = slack if minimum_slack is None else min(minimum_slack, slack)
            if slack == 0:
                zero_masks.append(shore)
            if slack < 0:
                negative_masks.append(shore)
        shore_sha = payload.hexdigest()
    result = {
        "label": label,
        "owners": owners,
        "owner_count": owner_count,
        "demand_by_owner": {str(x): demand[x] for x in owners},
        "total_demand": total_demand,
        "source_owner_masks": {str(mask): hist[mask] for mask in masks},
        "distinct_reachable_sources": sum(hist.values()),
        "max_flow": flow,
        "full": flow == total_demand,
        "mincut_owners": mincut_owners,
        "all_owner_shores_enumerated": exhaustive,
        "owner_shores_checked": (1 << owner_count) - 1 if exhaustive else None,
        "minimum_shore_slack": minimum_slack,
        "zero_slack_masks": zero_masks,
        "negative_shore_masks": negative_masks,
        "shore_table_sha256": shore_sha,
    }
    return result, rows


def write_shores(label: str, rows: list[dict]) -> str | None:
    if not rows:
        return None
    path = OUT / f"shores_{label}.jsonl"
    with path.open("w", encoding="ascii", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    return str(path.relative_to(ROOT))


def analyze(fixture: Fixture, scope: str = "active") -> dict:
    structural = validate_fixture(fixture)
    n = fixture.n
    adj = adjacency(n, fixture.blue)
    bad_adj = adjacency(n, fixture.bad)
    pair: list[Counter] = [Counter() for _ in range(n)]
    selected_vertices_set = set()
    support: set[Edge] = set()
    for row in fixture.rows:
        selected_vertices_set.update(row)
        support.update(edge(x, y) for x, y in zip(row, row[1:]))
        for x in row:
            pair[x].update(row)

    active_edges = {
        e for e in fixture.blue
        if e[0] in selected_vertices_set and e[1] in selected_vertices_set and e not in support
    }
    dsu = DSU(n)
    for x, y in active_edges:
        dsu.union(x, y)
    active_roots = {
        dsu.find(x) for x, y in fixture.bad
        if x in selected_vertices_set and y in selected_vertices_set and dsu.find(x) == dsu.find(y)
    }
    active_scope = {x for x in selected_vertices_set if dsu.find(x) in active_roots}
    scoped_edges = {e for e in active_edges if dsu.find(e[0]) in active_roots}
    if scope == "active":
        owner_scope = active_scope
        demand_edges = scoped_edges
        strict_components = True
    elif scope == "legacy_all":
        owner_scope = set(range(n))
        demand_edges = active_edges
        strict_components = False
    else:
        raise ValueError(scope)

    degree = Counter()
    for x, y in demand_edges:
        degree[x] += 1
        degree[y] += 1
    collision = {
        x: 2 * sum(max(0, count - 1) for count in pair[x].values())
        for x in owner_scope
    }
    hit_need = {
        x: max(0, degree[x] - max(0, n - 5 * pair[x].get(x, 0)))
        for x in owner_scope
    }
    demand = {
        x: collision[x] + hit_need[x]
        for x in owner_scope if collision[x] + hit_need[x] > 0
    }
    owners = sorted(demand)

    signed_degree = [0] * n
    edge_sign = {}
    for x, y in fixture.blue:
        signed_degree[x] += 1
        signed_degree[y] += 1
        edge_sign[(x, y)] = 1
    for x, y in fixture.bad:
        signed_degree[x] -= 1
        signed_degree[y] -= 1
        edge_sign[(x, y)] = -1

    p4_system = component_system(
        n, fixture.blue, fixture.bad, adj, signed_degree, selected_vertices_set
    )
    p5_system = component_system(
        n, fixture.blue, fixture.bad, adj, signed_degree, active_scope
    )

    reservation_indices = []
    for x, y in demand_edges:
        if pair[x].get(y, 0) != 0:
            raise AssertionError((fixture.name, "active edge not free", x, y))
        reservation_indices.extend((source_index(n, x, y, 0), source_index(n, y, x, 0)))
    if len(reservation_indices) != len(set(reservation_indices)):
        raise AssertionError("duplicate reservation key")

    p4_cache = {}
    p5_cache = {}
    old_by_owner: list[bytearray] = []
    p5_by_owner: list[bytearray] = []
    owner_records = {}

    def eligible_components(system: ComponentSystem, owner: int) -> tuple[tuple[int, ...], dict]:
        ids = []
        witnesses = {}
        owner_root = dsu.find(owner) if owner in active_scope else None
        for cid, boundary in enumerate(system.boundaries):
            if strict_components:
                hits = sorted(
                    a for a in boundary
                    if a in active_scope and dsu.find(a) == owner_root and pair[owner].get(a, 0) > 0
                )
            else:
                hits = sorted(a for a in boundary if pair[owner].get(a, 0) > 0)
            if hits:
                ids.append(cid)
                witnesses[str(cid)] = hits[0]
        return tuple(ids), witnesses

    for owner in owners:
        old = bytearray(bitset_size(n))
        additions = {}

        added = 0
        for y in range(n):
            if y != owner and pair[owner].get(y, 0) == 0:
                added += set_pair(old, n, owner, y)
        additions["P1_sameFirst"] = added

        added = 0
        for x in sorted(bad_adj[owner]):
            for y in sorted(bad_adj[owner]):
                if x == y or pair[x].get(y, 0) != 0:
                    continue
                e = edge(x, y)
                loss = signed_degree[x] + signed_degree[y] - 2 * edge_sign.get(e, 0)
                if loss >= 0:
                    added += set_pair(old, n, x, y)
        additions["P2_commonBad_new"] = added

        added = 0
        companions = sorted(x for x, count in pair[owner].items() if count > 0)
        for x in companions:
            for y in companions:
                if x == y or pair[x].get(y, 0) != 0:
                    continue
                e = edge(x, y)
                loss = signed_degree[x] + signed_degree[y] - 2 * edge_sign.get(e, 0)
                if loss >= 0:
                    added += set_pair(old, n, x, y)
        additions["P3_rowCompanion_new"] = added

        p4_ids, p4_witnesses = eligible_components(p4_system, owner)
        if p4_ids not in p4_cache:
            p4_cache[p4_ids] = relation_for_components(n, pair, p4_system, p4_ids)
        p4_bits, p4_stats = p4_cache[p4_ids]
        additions["P4_outsideAttachment_new"] = or_delta(old, p4_bits)

        raw_old_count = count_bits(old)
        reservation_overlap = sum(has_bit(old, index) for index in reservation_indices)
        for index in reservation_indices:
            clear_bit(old, index)
        old_count = count_bits(old)
        if raw_old_count - old_count != reservation_overlap:
            raise AssertionError("reservation subtraction")

        p5_ids, p5_witnesses = eligible_components(p5_system, owner)
        if p5_ids not in p5_cache:
            p5_cache[p5_ids] = relation_for_components(n, pair, p5_system, p5_ids)
        p5_bits, p5_stats = p5_cache[p5_ids]
        p5_reserved = sum(has_bit(p5_bits, index) for index in reservation_indices)
        if p5_reserved:
            raise AssertionError((fixture.name, owner, "P5 reserved overlap", p5_reserved))

        owner_records[str(owner)] = {
            "collision": collision[owner],
            "hit_need": hit_need[owner],
            "demand": demand[owner],
            "pattern_additions_raw": additions,
            "old_raw_keys": raw_old_count,
            "old_reserved_keys_removed": reservation_overlap,
            "old_available_keys": old_count,
            "old_available_bitset_sha256": bitset_sha(old),
            "P4": {**p4_stats, "boundary_witness_by_component": p4_witnesses},
            "P5": {
                **p5_stats,
                "boundary_witness_by_component": p5_witnesses,
                "semantic_keys": count_bits(p5_bits),
                "new_vs_old_available": new_against(p5_bits, old),
                "reserved_overlap": p5_reserved,
                "bitset_sha256": bitset_sha(p5_bits),
            },
        }
        old_by_owner.append(old)
        p5_by_owner.append(p5_bits)

    old_hist = owner_mask_histogram(old_by_owner)
    old_hall, old_shores = hall_gate(f"{fixture.name}_{scope}_old", owners, demand, old_hist)
    old_shore_path = write_shores(f"{fixture.name}_{scope}_old", old_shores)

    semantic_hist = owner_mask_histogram(old_by_owner, p5_by_owner)
    semantic_hall, semantic_shores = hall_gate(
        f"{fixture.name}_{scope}_semantic_p5", owners, demand, semantic_hist
    )
    semantic_shore_path = write_shores(
        f"{fixture.name}_{scope}_semantic_p5", semantic_shores
    )

    selected_extra = [bytearray(bitset_size(n)) for _ in owners]
    selected_keys = []
    selected_key_global_old_owners = {}
    certificate_mode = "P1-P4 only; no P5 key needed"
    if fixture.name == "2943" and scope == "active":
        hub_indices = [owners.index(owner) for owner in (0, 1, 2)]
        for x in range(56, 84, 2):
            for half in (0, 1):
                key = (3, x, half)
                index = source_index(n, *key)
                if any(not has_bit(p5_by_owner[i], index) for i in hub_indices):
                    raise AssertionError(("2943 P5 ineligible", key))
                if any(has_bit(old_by_owner[i], index) for i in hub_indices):
                    raise AssertionError(("2943 P5 not new", key))
                if index in reservation_indices:
                    raise AssertionError(("2943 P5 reserved", key))
                old_owners = [
                    owner for i, owner in enumerate(owners)
                    if has_bit(old_by_owner[i], index)
                ]
                if old_owners:
                    selected_key_global_old_owners[str(key)] = old_owners
                for i in hub_indices:
                    set_key(selected_extra[i], n, *key)
                selected_keys.append(list(key))
        certificate_mode = "exact R30 28-key P5 supplement"
    elif not old_hall["full"]:
        if not semantic_hall["full"]:
            certificate_mode = "no passing P5 certificate exists in the full semantic pool"
        else:
            selected_extra = [bytearray(bits) for bits in p5_by_owner]
            certificate_mode = "full semantic P5 pool (nonminimal fallback)"

    cert_hist = owner_mask_histogram(old_by_owner, selected_extra)
    cert_hall, cert_shores = hall_gate(
        f"{fixture.name}_{scope}_certificate", owners, demand, cert_hist
    )
    cert_shore_path = write_shores(
        f"{fixture.name}_{scope}_certificate", cert_shores
    )

    special = None
    if fixture.name == "2943" and scope == "active":
        leaf = 3
        cid = p5_system.comp_id[leaf]
        component = set(p5_system.components[cid])
        xs = list(range(56, 84, 2))
        boundary = sorted(p5_system.boundaries[cid])
        bcut = sum((x in component) != (y in component) for x, y in fixture.blue)
        mcut = sum((x in component) != (y in component) for x, y in fixture.bad)
        special = {
            "leaf": leaf,
            "component_id": cid,
            "component_size": len(component),
            "boundary": boundary,
            "blue_boundary": bcut,
            "bad_boundary": mcut,
            "loss": bcut - mcut,
            "lock_vertices": xs,
            "all_lock_vertices_in_component": all(x in component for x in xs),
            "all_pairs_free": all(pair[leaf].get(x, 0) == 0 for x in xs),
            "selected_keys": selected_keys,
            "selected_key_count": len(selected_keys),
            "selected_keys_sha256": hashlib.sha256(
                json.dumps(selected_keys, separators=(",", ":")).encode()
            ).hexdigest(),
            "all_selected_keys_new_for_hub_shore": True,
            "globally_new_selected_key_count": len(selected_keys) - len(selected_key_global_old_owners),
            "selected_key_global_old_owners": selected_key_global_old_owners,
            "all_selected_keys_unreserved": True,
            "all_three_hub_owner_arcs": True,
            "hub_shores": {
                "old": next(row for row in old_shores if row["mask"] == 7),
                "semantic_p5": next(row for row in semantic_shores if row["mask"] == 7),
                "certificate": next(row for row in cert_shores if row["mask"] == 7),
            },
        }

    return {
        "fixture": fixture.name,
        "scope": scope,
        "integer_only": True,
        "workers": 1,
        "metadata": fixture.metadata,
        "structural": structural,
        "selected_vertices": len(selected_vertices_set),
        "selected_support_edges": len(support),
        "active_edges_all": len(active_edges),
        "active_components": len(active_roots),
        "active_scope_vertices": len(active_scope),
        "active_scoped_edges": len(scoped_edges),
        "reservation_key_count": len(reservation_indices),
        "reservation_keys_sha256": hashlib.sha256(
            b"".join(index.to_bytes(8, "little") for index in sorted(reservation_indices))
        ).hexdigest(),
        "owners": owners,
        "owner_records": owner_records,
        "p4_component_count": len(p4_system.components),
        "p5_quiescent_component_count": len(p5_system.components),
        "old_relation": {**old_hall, "shore_file": old_shore_path},
        "semantic_p5_relation": {**semantic_hall, "shore_file": semantic_shore_path},
        "checked_certificate": {
            **cert_hall,
            "mode": certificate_mode,
            "selected_p5_keys": selected_keys,
            "shore_file": cert_shore_path,
        },
        "special_2943": special,
    }


BUILDERS = {
    "24": build_24,
    "167": lambda: build_167_or_175(167),
    "175": lambda: build_167_or_175(175),
    "311": build_311,
    "3892": build_3892,
    "89": build_89,
    "2943": build_2943,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", choices=tuple(BUILDERS), action="append")
    parser.add_argument("--legacy-small", action="store_true")
    args = parser.parse_args()
    names = args.fixture or ["2943", "24", "167", "175", "311", "3892", "89"]
    results = []
    for name in names:
        print(f"BUILD {name}", flush=True)
        fixture = BUILDERS[name]()
        print(f"GATE {name} active", flush=True)
        result = analyze(fixture, "active")
        results.append(result)
        cert = result["checked_certificate"]
        print(
            f"RESULT {name} active demand={cert['total_demand']} "
            f"flow={cert['max_flow']} minSlack={cert['minimum_shore_slack']} "
            f"full={cert['full']}",
            flush=True,
        )
        if args.legacy_small and name in ("24", "89"):
            print(f"GATE {name} legacy_all", flush=True)
            legacy = analyze(fixture, "legacy_all")
            results.append(legacy)
            cert = legacy["checked_certificate"]
            print(
                f"RESULT {name} legacy_all demand={cert['total_demand']} "
                f"flow={cert['max_flow']} minSlack={cert['minimum_shore_slack']} "
                f"full={cert['full']}",
                flush=True,
            )
    payload = {
        "schema": "p5-fixture-regate-v1",
        "integer_only": True,
        "native_decide": False,
        "sorry": False,
        "workers": 1,
        "gate_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "fixtures": results,
    }
    result_path = OUT / "result.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(f"WROTE {result_path}")
    return 0 if all(item["checked_certificate"]["full"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
