#!/usr/bin/env python3
"""Exact core for the CDC wave-1 selector adversary.

The evaluator uses Python integers only.  It constructs literal FreeHalf keys
``(source_x, source_y, half)``, gives every key unit capacity, and puts the
four oriented keys over an active undirected edge behind one capacity-two
node.  The six relation predicates are evaluated independently.

All CollisionHalf objects with one owner have the same neighbourhood under
these six predicates.  The max-flow network therefore aggregates their exact
integer demand by owner; ``enumerate_grouped_shores`` independently checks the
equivalent grouped-cap Hall inequality for every owner shore when feasible.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from typing import Iterable, Iterator, Sequence


Edge = tuple[int, int]
Row = tuple[int, int, int, int, int]
SourceKey = tuple[int, int, int]

FAMILIES = (
    "P1_sameFirst",
    "P2_commonBad",
    "P3_rowCompanion",
    "P4_strictOutsideAttachment",
    "P5_quiescentAttachment",
    "commonBlue",
)


def norm_edge(x: int, y: int) -> Edge:
    return (x, y) if x < y else (y, x)


def canonical_sha(value: object) -> str:
    import json

    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return sha256(raw).hexdigest()


@dataclass(frozen=True)
class CutGraph:
    name: str
    n: int
    blue: frozenset[Edge]
    bad: frozenset[Edge]

    @property
    def edges(self) -> frozenset[Edge]:
        return self.blue | self.bad


def adjacency(n: int, edges: Iterable[Edge]) -> tuple[frozenset[int], ...]:
    out = [set() for _ in range(n)]
    for x, y in edges:
        if not (0 <= x < y < n):
            raise ValueError((n, x, y))
        out[x].add(y)
        out[y].add(x)
    return tuple(frozenset(items) for items in out)


def graph6_encode(n: int, edges: Iterable[Edge]) -> str:
    """Encode a simple graph using the graph6 upper-triangle bit order."""
    if n < 0 or n > 258047:
        raise ValueError("only the one- and four-byte graph6 orders are used")
    edge_set = {norm_edge(*item) for item in edges}
    if n <= 62:
        header = [n]
    else:
        header = [63, (n >> 12) & 63, (n >> 6) & 63, n & 63]
    bits = [
        int((i, j) in edge_set)
        for j in range(1, n)
        for i in range(j)
    ]
    while len(bits) % 6:
        bits.append(0)
    payload = []
    for offset in range(0, len(bits), 6):
        value = 0
        for bit in bits[offset : offset + 6]:
            value = (value << 1) | bit
        payload.append(value)
    return "".join(chr(value + 63) for value in header + payload)


def graph6_decode(text: str) -> tuple[int, frozenset[Edge]]:
    values = [ord(char) - 63 for char in text.strip()]
    if not values:
        raise ValueError("empty graph6")
    if values[0] != 63:
        n = values[0]
        payload = values[1:]
    else:
        if len(values) < 4:
            raise ValueError("truncated graph6 order")
        n = (values[1] << 12) | (values[2] << 6) | values[3]
        payload = values[4:]
    bits = []
    for value in payload:
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    needed = n * (n - 1) // 2
    if len(bits) < needed:
        raise ValueError("truncated graph6 payload")
    edges = set()
    cursor = 0
    for j in range(1, n):
        for i in range(j):
            if bits[cursor]:
                edges.add((i, j))
            cursor += 1
    return n, frozenset(edges)


def recover_side(graph: CutGraph) -> tuple[int, ...]:
    """Recover the displayed cut from blue=xor1 and bad=xor0 constraints."""
    constraints = [[] for _ in range(graph.n)]
    for x, y in graph.blue:
        constraints[x].append((y, 1))
        constraints[y].append((x, 1))
    for x, y in graph.bad:
        constraints[x].append((y, 0))
        constraints[y].append((x, 0))
    side = [-1] * graph.n
    for root in range(graph.n):
        if side[root] >= 0:
            continue
        side[root] = 0
        queue = deque([root])
        while queue:
            x = queue.popleft()
            for y, parity in constraints[x]:
                value = side[x] ^ parity
                if side[y] < 0:
                    side[y] = value
                    queue.append(y)
                elif side[y] != value:
                    raise ValueError("blue/bad sets do not define a cut")
    return tuple(side)


def is_connected(n: int, edges: Iterable[Edge]) -> bool:
    if n == 0:
        return True
    adj = adjacency(n, edges)
    seen = {0}
    queue = deque([0])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                queue.append(y)
    return len(seen) == n


def triangle_count(n: int, edges: Iterable[Edge]) -> int:
    adj = adjacency(n, edges)
    return sum(
        1
        for x in range(n)
        for y in adj[x]
        if x < y
        for z in (adj[x] & adj[y])
        if y < z
    )


def cut_value(edges: Iterable[Edge], side: Sequence[int]) -> int:
    return sum(side[x] != side[y] for x, y in edges)


def maxcut_gray_exact(graph: CutGraph, *, order_limit: int = 25) -> dict:
    """Exhaust cuts modulo complement by an exact Gray-code walk."""
    if graph.n > order_limit:
        raise ValueError((graph.n, order_limit))
    adj = adjacency(graph.n, graph.edges)
    side = [0] * graph.n
    current = 0
    best = 0
    count = 1
    best_side = tuple(side)
    previous_gray = 0
    cuts = 1 << max(0, graph.n - 1)
    for index in range(1, cuts):
        gray = index ^ (index >> 1)
        changed = gray ^ previous_gray
        vertex = changed.bit_length()
        crossing_before = sum(side[vertex] != side[y] for y in adj[vertex])
        current += len(adj[vertex]) - 2 * crossing_before
        side[vertex] ^= 1
        if current > best:
            best = current
            count = 1
            best_side = tuple(side)
        elif current == best:
            count += 1
        previous_gray = gray
    return {
        "method": "exact Gray-code enumeration with vertex 0 fixed",
        "cutsChecked": cuts,
        "maximumCut": best,
        "maximumCutCountModuloComplement": count,
        "firstMaximumSide": "".join(map(str, best_side)),
    }


def shortest_rows(graph: CutGraph, source: int, target: int) -> tuple[Row, ...]:
    adj = adjacency(graph.n, graph.blue)
    distance = [-1] * graph.n
    distance[target] = 0
    queue = deque([target])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if distance[y] < 0:
                distance[y] = distance[x] + 1
                queue.append(y)
    if distance[source] != 4:
        return ()
    rows: list[Row] = []

    def visit(path: tuple[int, ...]) -> None:
        x = path[-1]
        if len(path) == 5:
            if x == target:
                rows.append(path)  # type: ignore[arg-type]
            return
        for y in sorted(adj[x]):
            if y not in path and distance[y] == distance[x] - 1:
                visit(path + (y,))

    visit((source,))
    return tuple(rows)


def complete_row_database(
    graph: CutGraph,
) -> tuple[tuple[Edge, tuple[Row, ...]], ...]:
    return tuple(
        (edge, shortest_rows(graph, *edge)) for edge in sorted(graph.bad)
    )


@dataclass
class TupleState:
    rows: tuple[Row, ...]
    pair: tuple[tuple[int, ...], ...]
    selected: frozenset[int]
    support: frozenset[Edge]
    active_edges: frozenset[Edge]
    active_component: tuple[int, ...]
    active_vertices: frozenset[int]


def reconstruct_state(graph: CutGraph, rows: Sequence[Sequence[int]]) -> TupleState:
    normalized = tuple(tuple(row) for row in rows)
    pair = [[0] * graph.n for _ in range(graph.n)]
    selected: set[int] = set()
    support: set[Edge] = set()
    for row in normalized:
        if len(row) != 5 or len(set(row)) != 5:
            raise ValueError(f"invalid row {row}")
        if norm_edge(row[0], row[4]) not in graph.bad:
            raise ValueError(f"row endpoints are not bad: {row}")
        for x in row:
            selected.add(x)
            for y in row:
                pair[x][y] += 1
        for x, y in zip(row, row[1:]):
            edge = norm_edge(x, y)
            if edge not in graph.blue:
                raise ValueError(f"non-blue row step {edge}")
            support.add(edge)
    active_edges = frozenset(
        edge
        for edge in graph.blue
        if edge not in support and edge[0] in selected and edge[1] in selected
    )
    active_adj = adjacency(graph.n, active_edges)
    component = [-1] * graph.n
    components: list[set[int]] = []
    for root in range(graph.n):
        if component[root] >= 0:
            continue
        cid = len(components)
        component[root] = cid
        members = {root}
        queue = deque([root])
        while queue:
            x = queue.popleft()
            for y in active_adj[x]:
                if component[y] < 0:
                    component[y] = cid
                    members.add(y)
                    queue.append(y)
        components.append(members)
    active_ids = {
        component[x]
        for x, y in graph.bad
        if component[x] == component[y]
    }
    active_vertices = frozenset(
        vertex
        for cid in active_ids
        for vertex in components[cid]
    )
    return TupleState(
        rows=normalized,  # type: ignore[arg-type]
        pair=tuple(tuple(row) for row in pair),
        selected=frozenset(selected),
        support=frozenset(support),
        active_edges=active_edges,
        active_component=tuple(component),
        active_vertices=active_vertices,
    )


def collision_units(state: TupleState) -> int:
    return sum(max(0, value - 1) for row in state.pair for value in row)


def collision_demand(state: TupleState) -> dict[int, int]:
    return {
        owner: amount
        for owner in range(len(state.pair))
        if (
            amount := 2
            * sum(max(0, value - 1) for value in state.pair[owner])
        )
    }


def collision_obligations(state: TupleState) -> Iterator[tuple[int, int, int, int]]:
    for owner, row in enumerate(state.pair):
        for other, count in enumerate(row):
            for copy in range(max(0, count - 1)):
                for half in (0, 1):
                    yield owner, other, copy, half


def sigma_pair(graph: CutGraph, x: int, y: int) -> int:
    switch = {x, y}
    return sum(
        1 for a, b in graph.blue if (a in switch) != (b in switch)
    ) - sum(1 for a, b in graph.bad if (a in switch) != (b in switch))


def sigma_set(graph: CutGraph, switch: frozenset[int]) -> int:
    return sum(
        1 for a, b in graph.blue if (a in switch) != (b in switch)
    ) - sum(1 for a, b in graph.bad if (a in switch) != (b in switch))


@dataclass(frozen=True)
class ComponentSystem:
    component_of: tuple[int, ...]
    components: tuple[frozenset[int], ...]
    boundaries: tuple[frozenset[int], ...]


def component_system(
    graph: CutGraph, allowed: frozenset[int], boundary_vertices: frozenset[int]
) -> ComponentSystem:
    adj = adjacency(graph.n, graph.blue)
    component_of = [-1] * graph.n
    components = []
    boundaries = []
    for root in sorted(allowed):
        if component_of[root] >= 0:
            continue
        cid = len(components)
        component_of[root] = cid
        seen = {root}
        queue = deque([root])
        while queue:
            x = queue.popleft()
            for y in adj[x]:
                if y in allowed and component_of[y] < 0:
                    component_of[y] = cid
                    seen.add(y)
                    queue.append(y)
        boundary = {
            y for x in seen for y in adj[x] if y in boundary_vertices
        }
        components.append(frozenset(seen))
        boundaries.append(frozenset(boundary))
    return ComponentSystem(
        tuple(component_of), tuple(components), tuple(boundaries)
    )


def attachment_relation(
    graph: CutGraph,
    state: TupleState,
    owners: tuple[int, ...],
    allowed: frozenset[int],
    boundary_vertices: frozenset[int],
) -> tuple[dict[SourceKey, int], dict[str, int]]:
    system = component_system(graph, allowed, boundary_vertices)
    masks = []
    for boundary in system.boundaries:
        mask = 0
        for index, owner in enumerate(owners):
            if any(
                state.pair[owner][attach] > 0
                and state.active_component[owner]
                == state.active_component[attach]
                for attach in boundary
            ):
                mask |= 1 << index
        masks.append(mask)
    relation: dict[SourceKey, int] = {}
    negative_component_pairs = 0
    for left, left_vertices in enumerate(system.components):
        for right, right_vertices in enumerate(system.components):
            mask = masks[left] & masks[right]
            if not mask:
                continue
            switch = left_vertices | right_vertices
            if sigma_set(graph, switch) < 0:
                negative_component_pairs += 1
                continue
            for x in left_vertices:
                for y in right_vertices:
                    if x == y or state.pair[x][y] != 0:
                        continue
                    relation[x, y, 0] = mask
                    relation[x, y, 1] = mask
    return relation, {
        "components": len(system.components),
        "nonemptyBoundaries": sum(bool(item) for item in system.boundaries),
        "negativeEligibleComponentPairs": negative_component_pairs,
        "ownerAttachmentActiveComponentEquality": True,
    }


def relation_families(
    graph: CutGraph, state: TupleState
) -> tuple[tuple[int, ...], dict[str, dict[SourceKey, int]], dict[str, dict]]:
    demand = collision_demand(state)
    owners = tuple(sorted(demand))
    owner_index = {owner: index for index, owner in enumerate(owners)}
    blue_adj = adjacency(graph.n, graph.blue)
    bad_adj = adjacency(graph.n, graph.bad)
    relations: dict[str, dict[SourceKey, int]] = {
        family: {} for family in FAMILIES
    }
    audit: dict[str, dict] = {family: {} for family in FAMILIES}

    def add(family: str, owner: int, x: int, y: int) -> None:
        if x == y or state.pair[x][y] != 0:
            return
        bit = 1 << owner_index[owner]
        for half in (0, 1):
            key = (x, y, half)
            relations[family][key] = relations[family].get(key, 0) | bit

    for owner in owners:
        for y in range(graph.n):
            add("P1_sameFirst", owner, owner, y)

        for x in bad_adj[owner]:
            for y in bad_adj[owner]:
                if sigma_pair(graph, x, y) >= 0:
                    add("P2_commonBad", owner, x, y)

        companions = [
            x for x in range(graph.n) if state.pair[owner][x] > 0
        ]
        for x in companions:
            for y in companions:
                if sigma_pair(graph, x, y) >= 0:
                    add("P3_rowCompanion", owner, x, y)

        for x in blue_adj[owner]:
            for y in blue_adj[owner]:
                if sigma_pair(graph, x, y) >= 2:
                    add("commonBlue", owner, x, y)

    p4, p4_audit = attachment_relation(
        graph,
        state,
        owners,
        frozenset(range(graph.n)) - state.selected,
        state.selected,
    )
    relations["P4_strictOutsideAttachment"] = p4
    audit["P4_strictOutsideAttachment"] = p4_audit

    p5, p5_audit = attachment_relation(
        graph,
        state,
        owners,
        frozenset(range(graph.n)) - state.active_vertices,
        state.active_vertices,
    )
    relations["P5_quiescentAttachment"] = p5
    audit["P5_quiescentAttachment"] = p5_audit
    return owners, relations, audit


def merge_relations(
    relations: dict[str, dict[SourceKey, int]]
) -> dict[SourceKey, int]:
    union: dict[SourceKey, int] = {}
    for family in FAMILIES:
        for key, mask in relations[family].items():
            union[key] = union.get(key, 0) | mask
    return union


@dataclass
class Arc:
    target: int
    reverse: int
    capacity: int
    initial: int


class Dinic:
    def __init__(self) -> None:
        self.graph: list[list[Arc]] = []

    def node(self) -> int:
        self.graph.append([])
        return len(self.graph) - 1

    def add(self, source: int, target: int, capacity: int) -> None:
        forward = Arc(target, len(self.graph[target]), capacity, capacity)
        reverse = Arc(source, len(self.graph[source]), 0, 0)
        self.graph[source].append(forward)
        self.graph[target].append(reverse)

    def maxflow(self, source: int, sink: int) -> int:
        total = 0
        while True:
            level = [-1] * len(self.graph)
            level[source] = 0
            queue = deque([source])
            while queue:
                x = queue.popleft()
                for arc in self.graph[x]:
                    if arc.capacity and level[arc.target] < 0:
                        level[arc.target] = level[x] + 1
                        queue.append(arc.target)
            if level[sink] < 0:
                return total
            cursor = [0] * len(self.graph)

            def send(x: int, amount: int) -> int:
                if x == sink:
                    return amount
                while cursor[x] < len(self.graph[x]):
                    arc = self.graph[x][cursor[x]]
                    if arc.capacity and level[arc.target] == level[x] + 1:
                        pushed = send(arc.target, min(amount, arc.capacity))
                        if pushed:
                            arc.capacity -= pushed
                            self.graph[arc.target][arc.reverse].capacity += pushed
                            return pushed
                    cursor[x] += 1
                return 0

            while True:
                pushed = send(source, 1 << 60)
                if not pushed:
                    break
                total += pushed

    def reachable(self, source: int) -> set[int]:
        seen = {source}
        queue = deque([source])
        while queue:
            x = queue.popleft()
            for arc in self.graph[x]:
                if arc.capacity and arc.target not in seen:
                    seen.add(arc.target)
                    queue.append(arc.target)
        return seen


def solve_literal_grouped_flow(
    graph: CutGraph,
    state: TupleState,
    owners: tuple[int, ...],
    relation: dict[SourceKey, int],
) -> dict:
    demand_map = collision_demand(state)
    network = Dinic()
    source = network.node()
    sink = network.node()
    owner_nodes = [network.node() for _ in owners]
    total_demand = sum(demand_map[owner] for owner in owners)
    for owner, node in zip(owners, owner_nodes):
        network.add(source, node, demand_map[owner])

    active_group_nodes = {
        edge: network.node() for edge in sorted(state.active_edges)
    }
    for node in active_group_nodes.values():
        network.add(node, sink, 2)

    key_nodes: dict[SourceKey, int] = {}
    infinity = total_demand + 1
    for key, mask in sorted(relation.items()):
        x, y, _half = key
        if x == y or state.pair[x][y] != 0:
            raise AssertionError(f"non-FreeHalf key in relation: {key}")
        node = network.node()
        key_nodes[key] = node
        bits = mask
        while bits:
            bit = bits & -bits
            index = bit.bit_length() - 1
            network.add(owner_nodes[index], node, infinity)
            bits ^= bit
        edge = norm_edge(x, y)
        if edge in active_group_nodes:
            network.add(node, active_group_nodes[edge], 1)
        else:
            network.add(node, sink, 1)

    maximum = network.maxflow(source, sink)
    reachable = network.reachable(source)
    mincut_owners = [
        owner for owner, node in zip(owners, owner_nodes) if node in reachable
    ]
    return {
        "totalDemand": total_demand,
        "maximumFlow": maximum,
        "defect": total_demand - maximum,
        "networkNodes": len(network.graph),
        "literalFreeHalfKeysInRelation": len(key_nodes),
        "activeEdgeGroups": len(active_group_nodes),
        "minCutOwners": mincut_owners,
    }


def grouped_shore_capacity(
    state: TupleState,
    relation: dict[SourceKey, int],
    shore_mask: int,
) -> tuple[int, list[SourceKey], dict[Edge, list[SourceKey]]]:
    direct = []
    active: dict[Edge, list[SourceKey]] = {
        edge: [] for edge in sorted(state.active_edges)
    }
    for key, owner_mask in sorted(relation.items()):
        if not (owner_mask & shore_mask):
            continue
        edge = norm_edge(key[0], key[1])
        if edge in active:
            active[edge].append(key)
        else:
            direct.append(key)
    capacity = len(direct) + sum(min(2, len(keys)) for keys in active.values())
    return capacity, direct, active


def enumerate_grouped_shores(
    state: TupleState,
    owners: tuple[int, ...],
    relation: dict[SourceKey, int],
    *,
    owner_limit: int = 22,
) -> dict:
    if len(owners) > owner_limit:
        return {"enumerated": False, "ownerCount": len(owners)}
    if not owners:
        return {
            "enumerated": True,
            "ownerCount": 0,
            "shoresChecked": 0,
            "negativeShoreCount": 0,
            "minimumShore": {
                "mask": 0,
                "owners": [],
                "demand": 0,
                "capacity": 0,
                "slack": 0,
                "directKeyCount": 0,
                "activeGroupedCapacity": 0,
                "eligibleLiteralFreeHalfKeys": [],
                "activeEligibleKeys": {},
            },
        }
    demand_map = collision_demand(state)
    minimum = None
    negative = 0
    checked = 0
    for shore in range(1, 1 << len(owners)):
        checked += 1
        shore_demand = sum(
            demand_map[owner]
            for index, owner in enumerate(owners)
            if shore & (1 << index)
        )
        capacity, direct, active = grouped_shore_capacity(
            state, relation, shore
        )
        slack = capacity - shore_demand
        record = {
            "mask": shore,
            "owners": [
                owner
                for index, owner in enumerate(owners)
                if shore & (1 << index)
            ],
            "demand": shore_demand,
            "capacity": capacity,
            "slack": slack,
            "directKeyCount": len(direct),
            "activeGroupedCapacity": sum(
                min(2, len(keys)) for keys in active.values()
            ),
            "eligibleLiteralFreeHalfKeys": [list(key) for key in direct]
            + [list(key) for keys in active.values() for key in keys],
            "activeEligibleKeys": {
                f"{edge[0]},{edge[1]}": [list(key) for key in keys]
                for edge, keys in active.items()
                if keys
            },
        }
        candidate = (slack, len(record["owners"]), shore, record)
        if minimum is None or candidate[:3] < minimum[:3]:
            minimum = candidate
        if slack < 0:
            negative += 1
    assert minimum is not None
    return {
        "enumerated": True,
        "ownerCount": len(owners),
        "shoresChecked": checked,
        "negativeShoreCount": negative,
        "minimumShore": minimum[3],
    }


def analyze_tuple(graph: CutGraph, rows: Sequence[Sequence[int]]) -> dict:
    state = reconstruct_state(graph, rows)
    owners, relations, audit = relation_families(graph, state)
    union = merge_relations(relations)
    flow = solve_literal_grouped_flow(graph, state, owners, union)
    shores = enumerate_grouped_shores(state, owners, union)
    if shores.get("enumerated"):
        expected = -shores["minimumShore"]["slack"]
        if flow["defect"] != max(0, expected):
            raise AssertionError((flow, shores["minimumShore"]))
    obligations = list(collision_obligations(state))
    if len(obligations) != flow["totalDemand"]:
        raise AssertionError("CollisionHalf enumeration/demand mismatch")
    family_stats = {
        family: {
            "literalFreeHalfKeys": len(relations[family]),
            "ownerKeyArcs": sum(mask.bit_count() for mask in relations[family].values()),
            "audit": audit[family],
        }
        for family in FAMILIES
    }
    return {
        "rows": [list(row) for row in state.rows],
        "rowSha256": canonical_sha([list(row) for row in state.rows]),
        "collisionUnits": collision_units(state),
        "collisionHalfDemand": flow["totalDemand"],
        "collisionOwners": list(owners),
        "demandByOwner": {
            str(owner): collision_demand(state)[owner] for owner in owners
        },
        "selectedVertices": sorted(state.selected),
        "activeEdges": [list(edge) for edge in sorted(state.active_edges)],
        "activeVertices": sorted(state.active_vertices),
        "actualFreeHalfCount": 2
        * sum(
            x != y and state.pair[x][y] == 0
            for x in range(graph.n)
            for y in range(graph.n)
        ),
        "familyStats": family_stats,
        "unionLiteralFreeHalfKeys": len(union),
        "flow": flow,
        "shoreAudit": shores,
        "verdict": "PASS" if flow["defect"] == 0 else "FAIL",
    }


def exhaustive_minimum_collision_tuples(
    graph: CutGraph,
    row_db: tuple[tuple[Edge, tuple[Row, ...]], ...],
    *,
    tuple_cap: int = 1_000_000,
    stop_after_first_passing_minimum: bool = False,
) -> dict:
    sizes = [len(rows) for _edge, rows in row_db]
    tuple_count = 1
    for size in sizes:
        tuple_count *= size
    if not sizes:
        tuple_count = 1
    if tuple_count > tuple_cap:
        return {
            "exhaustive": False,
            "rowFamilySizes": sizes,
            "tupleCount": tuple_count,
            "tupleCap": tuple_cap,
        }
    minimum = None
    minima: list[tuple[tuple[int, ...], tuple[Row, ...]]] = []
    collision_histogram: Counter[int] = Counter()
    for choice in product(*(range(size) for size in sizes)):
        rows = tuple(row_db[index][1][item] for index, item in enumerate(choice))
        units = collision_units(reconstruct_state(graph, rows))
        collision_histogram[units] += 1
        if minimum is None or units < minimum:
            minimum = units
            minima = [(choice, rows)]
        elif units == minimum:
            minima.append((choice, rows))
    if minimum is None:
        minimum = 0
        minima = [((), ())]
    analyzed = []
    for choice, rows in minima:
        result = analyze_tuple(graph, rows)
        analyzed.append(
            {
                "choice": list(choice),
                "defect": result["flow"]["defect"],
                "verdict": result["verdict"],
                "rowSha256": result["rowSha256"],
                "analysis": result,
            }
        )
        if stop_after_first_passing_minimum and result["verdict"] == "PASS":
            break
    return {
        "exhaustive": True,
        "rowFamilySizes": sizes,
        "tupleCount": tuple_count,
        "collisionHistogram": {
            str(key): value for key, value in sorted(collision_histogram.items())
        },
        "minimumCollisionUnits": minimum,
        "minimumTupleCount": len(minima),
        "minimumTuplesEvaluated": len(analyzed),
        "allMinimumTuplesEvaluated": len(analyzed) == len(minima),
        "passingMinimumTupleCount": sum(
            item["verdict"] == "PASS" for item in analyzed
        ),
        "failingMinimumTupleCount": sum(
            item["verdict"] == "FAIL" for item in analyzed
        ),
        "minimumTuples": analyzed,
        "selectorVerdict": (
            "PASS_SOME_MINIMUM_TUPLE"
            if any(item["verdict"] == "PASS" for item in analyzed)
            else "FAIL_ALL_MINIMUM_TUPLES"
            if len(analyzed) == len(minima)
            else "UNRESOLVED_MINIMUM_TUPLES"
        ),
    }


def n24_fixture() -> CutGraph:
    left = (0, 1, 2)
    right = (3, 4, 5)
    u, w, v = 6, 7, 8
    a_left = (9, 10, 11)
    z_left = (12, 13, 14)
    middle = (15, 16, 17)
    z_right = (18, 19, 20)
    a_right = (21, 22, 23)
    blue: set[Edge] = set()

    def link(xs: Iterable[int], ys: Iterable[int]) -> None:
        blue.update(norm_edge(x, y) for x in xs for y in ys)

    blue.update(norm_edge(x, u) for x in left)
    blue.update((norm_edge(u, w), norm_edge(w, v)))
    blue.update(norm_edge(v, y) for y in right)
    link(left, a_left)
    link(a_left, z_left)
    link(z_left, middle)
    link(middle, z_right)
    link(z_right, a_right)
    link(a_right, right)
    bad = frozenset(norm_edge(x, y) for x in left for y in right)
    return CutGraph("N24", 24, frozenset(blue), bad)


def n89_fixture() -> CutGraph:
    root, c_left, c_right = 0, 1, 2
    left = (3, 4, 5, 6)
    right = (7, 8, 9, 10, 11)
    anchor = 12
    locks = (0, 0, 0, 4, 6, 4, 5, 5, 3, 3, 3, 5)
    blue = {norm_edge(root, c_left), norm_edge(root, c_right)}
    blue.update(norm_edge(c_left, x) for x in left)
    blue.update(norm_edge(c_right, y) for y in right)
    bad = frozenset(norm_edge(x, y) for x in left for y in right)
    nxt = 13
    for owner, count in enumerate(locks):
        for _ in range(count):
            x, y = nxt, nxt + 1
            nxt += 2
            blue.update(
                (norm_edge(owner, x), norm_edge(x, y), norm_edge(y, anchor))
            )
    if nxt != 89:
        raise AssertionError(nxt)
    return CutGraph("N89", 89, frozenset(blue), bad)


def displayed_graph_checks(graph: CutGraph) -> dict:
    side = recover_side(graph)
    g6 = graph6_encode(graph.n, graph.edges)
    decoded_n, decoded_edges = graph6_decode(g6)
    row_db = complete_row_database(graph)
    return {
        "graph6": g6,
        "graph6RoundTrip": decoded_n == graph.n and decoded_edges == graph.edges,
        "order": graph.n,
        "edgeCount": len(graph.edges),
        "blueEdgeCount": len(graph.blue),
        "badEdgeCount": len(graph.bad),
        "side": "".join(map(str, side)),
        "cutValue": len(graph.blue),
        "triangleCount": triangle_count(graph.n, graph.edges),
        "graphConnected": is_connected(graph.n, graph.edges),
        "blueConnected": is_connected(graph.n, graph.blue),
        "rowFamilySizes": [len(rows) for _edge, rows in row_db],
        "allBadDistanceFour": all(rows for _edge, rows in row_db),
        "rows": [
            {
                "badEdge": list(edge),
                "rows": [list(row) for row in rows],
            }
            for edge, rows in row_db
        ],
    }


__all__ = [
    "CutGraph",
    "FAMILIES",
    "analyze_tuple",
    "canonical_sha",
    "complete_row_database",
    "displayed_graph_checks",
    "exhaustive_minimum_collision_tuples",
    "graph6_decode",
    "graph6_encode",
    "maxcut_gray_exact",
    "n24_fixture",
    "n89_fixture",
    "norm_edge",
    "recover_side",
    "reconstruct_state",
    "shortest_rows",
]
