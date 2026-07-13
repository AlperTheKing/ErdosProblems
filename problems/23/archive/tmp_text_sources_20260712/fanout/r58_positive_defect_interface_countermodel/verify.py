#!/usr/bin/env python3
"""Standalone exact replay of the R58 compiled-interface countermodel.

The replay owns only this directory and uses only the Python standard library.
It checks the fixed 16-vertex graph, all 2^9 row tuples, the exact six-family
grouped soft-cap flow, a forced optimum using both fork halves, and the full
residual unit-core closure. Signed cut arithmetic uses fractions.Fraction;
network capacities and cardinalities are exact integers.

Default mode verifies that REPORT.md and result.json are byte-for-byte the
deterministic outputs. Pass --write only to refresh those two files.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from dataclasses import dataclass
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "result.json"
REPORT_PATH = HERE / "REPORT.md"

Edge = tuple[int, int]
Row = tuple[int, ...]
Choice = tuple[int, ...]
Obligation = tuple[int, int, int, int]
SourceKey = tuple[int, int, int]

N = 16
ATOM_COPIES = 9
CORE_NAMES = ("s", "t", "a1", "a2", "a3", "b1", "b2", "b3")
CORE = {name: index for index, name in enumerate(CORE_NAMES)}
LEAF = {name: index + 8 for index, name in enumerate(CORE_NAMES)}
VERTEX_NAMES = CORE_NAMES + tuple(name + "'" for name in CORE_NAMES)

LEFT_ROW: Row = tuple(CORE[name] for name in ("s", "a1", "a2", "a3", "t"))
RIGHT_ROW: Row = tuple(CORE[name] for name in ("s", "b1", "b2", "b3", "t"))
FORK_LEFT = CORE["a1"]
FORK_RIGHT = CORE["b1"]
CURRENT_CHOICE: Choice = (0, 0, 0, 0, 1, 1, 1, 1, 1)

FAMILY_ORDER = (
    "P1_sameFirst",
    "P2_commonBad",
    "P3_rowCompanion",
    "P4_outsideAttachment",
    "P5_quiescentAttachment",
    "commonBlue",
)


def norm_edge(left: int, right: int) -> Edge:
    return (left, right) if left < right else (right, left)


PATH_BLUE = frozenset(
    norm_edge(left, right)
    for row in (LEFT_ROW, RIGHT_ROW)
    for left, right in zip(row, row[1:])
)
PENDANT_BLUE = frozenset(
    norm_edge(CORE[name], LEAF[name]) for name in CORE_NAMES
)
BASE_BLUE = PATH_BLUE | PENDANT_BLUE
BASE_BAD = frozenset({norm_edge(CORE["s"], CORE["t"])})
BASE_EDGES = BASE_BLUE | BASE_BAD
BASE_SHORE = frozenset(
    {CORE[name] for name in ("s", "t", "a2", "b2")}
    | {
        LEAF[name]
        for name in CORE_NAMES
        if name not in {"s", "t", "a2", "b2"}
    }
)


def canonical_json_bytes(value: object, *, pretty: bool) -> bytes:
    if pretty:
        text = json.dumps(value, indent=2, sort_keys=True)
    else:
        text = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return (text + "\n").encode("ascii")


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def digest_json(value: object) -> str:
    return digest_bytes(canonical_json_bytes(value, pretty=False).rstrip(b"\n"))


def digest_path(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def fraction_record(value: Fraction) -> dict:
    return {
        "denominator": value.denominator,
        "numerator": value.numerator,
        "text": str(value),
    }


def edge_record(edge: Edge) -> list[str]:
    return [VERTEX_NAMES[edge[0]], VERTEX_NAMES[edge[1]]]


def row_record(row: Row) -> list[str]:
    return [VERTEX_NAMES[vertex] for vertex in row]


def mask_of(vertices: Iterable[int]) -> int:
    return sum(1 << vertex for vertex in vertices)


def crosses(edge: Edge, mask: int) -> bool:
    return bool(((mask >> edge[0]) ^ (mask >> edge[1])) & 1)


def adjacency(edges: Iterable[Edge]) -> tuple[tuple[int, ...], ...]:
    output = [set() for _ in range(N)]
    for left, right in edges:
        output[left].add(right)
        output[right].add(left)
    return tuple(tuple(sorted(items)) for items in output)


def connected(edges: Iterable[Edge]) -> bool:
    adj = adjacency(edges)
    seen = {0}
    queue = deque([0])
    while queue:
        vertex = queue.popleft()
        for neighbor in adj[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return len(seen) == N


def triangle_count(edges: Iterable[Edge]) -> int:
    adj = tuple(set(items) for items in adjacency(edges))
    return sum(
        1
        for left in range(N)
        for middle in range(left + 1, N)
        for right in range(middle + 1, N)
        if middle in adj[left] and right in adj[left] and right in adj[middle]
    )


def distances(edges: Iterable[Edge], source: int) -> tuple[int, ...]:
    adj = adjacency(edges)
    distance = [-1] * N
    distance[source] = 0
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for neighbor in adj[vertex]:
            if distance[neighbor] < 0:
                distance[neighbor] = distance[vertex] + 1
                queue.append(neighbor)
    return tuple(distance)


def shortest_rows(edges: Iterable[Edge], source: int, target: int) -> tuple[Row, ...]:
    edge_set = frozenset(edges)
    adj = adjacency(edge_set)
    from_source = distances(edge_set, source)
    from_target = distances(edge_set, target)
    length = from_source[target]
    output: list[Row] = []

    def visit(path: list[int]) -> None:
        vertex = path[-1]
        if vertex == target:
            output.append(tuple(path))
            return
        for neighbor in adj[vertex]:
            if neighbor in path:
                continue
            if from_source[neighbor] != from_source[vertex] + 1:
                continue
            if from_source[neighbor] + from_target[neighbor] != length:
                continue
            path.append(neighbor)
            visit(path)
            path.pop()

    visit([source])
    return tuple(output)


def gamma_for_cut(mask: int) -> int | None:
    blue = frozenset(edge for edge in BASE_EDGES if crosses(edge, mask))
    if not connected(blue):
        return None
    total = 0
    for left, right in BASE_EDGES - blue:
        distance = distances(blue, left)[right]
        if distance < 0:
            return None
        total += (distance + 1) ** 2
    return total


def graph_cut_audit() -> dict:
    best = -1
    best_masks: list[int] = []
    for mask in range(1 << N):
        if mask & 1:
            continue
        value = sum(crosses(edge, mask) for edge in BASE_EDGES)
        if value > best:
            best = value
            best_masks = [mask]
        elif value == best:
            best_masks.append(mask)
    gammas = [gamma_for_cut(mask) for mask in best_masks]
    connected_gammas = [value for value in gammas if value is not None]
    shown = mask_of(BASE_SHORE)
    if shown & 1:
        shown ^= (1 << N) - 1
    shown_value = sum(crosses(edge, shown) for edge in BASE_EDGES)
    shown_gamma = gamma_for_cut(shown)
    return {
        "connectedMaximumCutOrbits": len(connected_gammas),
        "displayedGamma": shown_gamma,
        "displayedIsGammaMinimal": shown_gamma == min(connected_gammas),
        "displayedIsMaximum": shown_value == best,
        "displayedValue": shown_value,
        "maximum": best,
        "maximumCutOrbits": len(best_masks),
        "minimumConnectedMaximumGamma": min(connected_gammas),
        "normalizedCuts": 1 << (N - 1),
    }


@dataclass
class GraphContext:
    n: int
    blue: frozenset[Edge]
    bad: frozenset[Edge]
    blue_adj: tuple[frozenset[int], ...]
    bad_adj: tuple[frozenset[int], ...]
    sigma_pair: tuple[tuple[Fraction, ...], ...]
    edge_sign: dict[Edge, Fraction]
    sigma_cache: dict[int, Fraction]

    def sigma(self, mask: int) -> Fraction:
        cached = self.sigma_cache.get(mask)
        if cached is not None:
            return cached
        value = sum(
            (
                sign
                for (left, right), sign in self.edge_sign.items()
                if bool(mask & (1 << left)) != bool(mask & (1 << right))
            ),
            Fraction(0),
        )
        self.sigma_cache[mask] = value
        return value


def make_graph_context() -> GraphContext:
    blue_adj = [set() for _ in range(N)]
    bad_adj = [set() for _ in range(N)]
    signed_degree = [Fraction(0) for _ in range(N)]
    edge_sign: dict[Edge, Fraction] = {}
    for left, right in sorted(BASE_BLUE):
        blue_adj[left].add(right)
        blue_adj[right].add(left)
        signed_degree[left] += 1
        signed_degree[right] += 1
        edge_sign[(left, right)] = Fraction(1)
    for left, right in sorted(BASE_BAD):
        bad_adj[left].add(right)
        bad_adj[right].add(left)
        signed_degree[left] -= 1
        signed_degree[right] -= 1
        edge_sign[(left, right)] = Fraction(-1)
    sigma_pair = tuple(
        tuple(
            Fraction(0)
            if left == right
            else signed_degree[left]
            + signed_degree[right]
            - 2 * edge_sign.get(norm_edge(left, right), Fraction(0))
            for right in range(N)
        )
        for left in range(N)
    )
    return GraphContext(
        n=N,
        blue=BASE_BLUE,
        bad=BASE_BAD,
        blue_adj=tuple(frozenset(items) for items in blue_adj),
        bad_adj=tuple(frozenset(items) for items in bad_adj),
        sigma_pair=sigma_pair,
        edge_sign=edge_sign,
        sigma_cache={0: Fraction(0)},
    )


def signed_cut_audit(ctx: GraphContext) -> dict:
    losses = [ctx.sigma(mask) for mask in range(1 << N)]
    if any(value < 0 for value in losses):
        raise AssertionError("displayed maximum cut has negative switch loss")
    row_union = tuple(sorted(set(LEFT_ROW) | set(RIGHT_ROW)))
    masks = [
        mask_of(
            row_union[index]
            for index in range(len(row_union))
            if small & (1 << index)
        )
        for small in range(1 << len(row_union))
    ]
    minimum_margin: Fraction | None = None
    identity_checks = 0
    for left_mask in masks:
        for right_mask in masks:
            left_only = left_mask & ~right_mask
            right_only = right_mask & ~left_mask
            opposite = sum(
                (
                    sign
                    for edge, sign in ctx.edge_sign.items()
                    if (
                        bool(left_only & (1 << edge[0]))
                        and bool(right_only & (1 << edge[1]))
                    )
                    or (
                        bool(left_only & (1 << edge[1]))
                        and bool(right_only & (1 << edge[0]))
                    )
                ),
                Fraction(0),
            )
            margin = ctx.sigma(left_mask) + ctx.sigma(right_mask) - 2 * opposite
            corner = ctx.sigma(left_mask & right_mask) + ctx.sigma(left_mask | right_mask)
            if margin != corner:
                raise AssertionError("four-corner identity failed")
            identity_checks += 1
            if minimum_margin is None or margin < minimum_margin:
                minimum_margin = margin
    if minimum_margin is None or minimum_margin != 0:
        raise AssertionError("unexpected four-corner minimum")

    boundary_histogram: Counter[int] = Counter()
    for mask in masks:
        support = sum(crosses(edge, mask) for edge in PATH_BLUE)
        active = 0
        outside = sum(crosses(edge, mask) for edge in PENDANT_BLUE)
        blue = sum(crosses(edge, mask) for edge in BASE_BLUE)
        bad = sum(crosses(edge, mask) for edge in BASE_BAD)
        if blue != support + active + outside:
            raise AssertionError("selected-support boundary decomposition failed")
        if Fraction(blue - bad) != ctx.sigma(mask):
            raise AssertionError("signed boundary count mismatch")
        boundary_histogram[outside] += 1

    denominators = {value.denominator for value in losses}
    denominators.add(minimum_margin.denominator)
    return {
        "allDenominatorsOne": denominators == {1},
        "arithmetic": "fractions.Fraction",
        "fourCornerIdentityChecks": identity_checks,
        "minimumFourCornerMargin": fraction_record(minimum_margin),
        "minimumSwitchLoss": fraction_record(min(losses)),
        "nonnegativeSwitchMasks": sum(value >= 0 for value in losses),
        "outsideBoundaryHistogramOnRowUnionMasks": {
            str(key): value for key, value in sorted(boundary_histogram.items())
        },
        "rowUnionMaskPairs": len(masks) ** 2,
        "rowUnionMasks": len(masks),
        "switchMasks": len(losses),
    }


@dataclass
class TupleState:
    rows: tuple[Row, ...]
    pair: list[list[int]]
    row_count: list[int]
    selected: set[int]
    support: set[Edge]
    active_edges: set[Edge]
    selected_comp: list[int]
    active_comp_ids: set[int]
    active_vertices: set[int]


def components(
    edges: Iterable[Edge], allowed: set[int]
) -> tuple[list[int], list[list[int]], list[int]]:
    adj = [[] for _ in range(N)]
    for left, right in sorted(edges):
        if left in allowed and right in allowed:
            adj[left].append(right)
            adj[right].append(left)
    comp_id = [-1] * N
    output: list[list[int]] = []
    masks: list[int] = []
    for root in sorted(allowed):
        if comp_id[root] >= 0:
            continue
        index = len(output)
        comp_id[root] = index
        queue = deque([root])
        vertices: list[int] = []
        mask = 0
        while queue:
            vertex = queue.popleft()
            vertices.append(vertex)
            mask |= 1 << vertex
            for neighbor in adj[vertex]:
                if comp_id[neighbor] < 0:
                    comp_id[neighbor] = index
                    queue.append(neighbor)
        output.append(vertices)
        masks.append(mask)
    return comp_id, output, masks


def reconstruct_state(rows: Iterable[Row]) -> TupleState:
    normalized = tuple(rows)
    pair = [[0] * N for _ in range(N)]
    row_count = [0] * N
    selected: set[int] = set()
    support: set[Edge] = set()
    for row in normalized:
        if len(row) != 5 or len(set(row)) != 5:
            raise AssertionError("row is not five distinct vertices")
        if norm_edge(row[0], row[-1]) not in BASE_BAD:
            raise AssertionError("row endpoints do not form the graph bad edge")
        for vertex in row:
            row_count[vertex] += 1
            selected.add(vertex)
            for other in row:
                pair[vertex][other] += 1
        for left, right in zip(row, row[1:]):
            edge = norm_edge(left, right)
            if edge not in BASE_BLUE:
                raise AssertionError("row step is not blue")
            support.add(edge)
    active_edges = {
        edge
        for edge in BASE_BLUE
        if edge not in support and edge[0] in selected and edge[1] in selected
    }
    selected_comp, _component_list, _masks = components(active_edges, selected)
    active_comp_ids = {
        selected_comp[left]
        for left, right in BASE_BAD
        if left in selected
        and right in selected
        and selected_comp[left] == selected_comp[right]
    }
    active_vertices = {
        vertex for vertex in selected if selected_comp[vertex] in active_comp_ids
    }
    return TupleState(
        rows=normalized,
        pair=pair,
        row_count=row_count,
        selected=selected,
        support=support,
        active_edges=active_edges,
        selected_comp=selected_comp,
        active_comp_ids=active_comp_ids,
        active_vertices=active_vertices,
    )


def global_demands(state: TupleState) -> tuple[tuple[int, ...], tuple[int, ...]]:
    amounts = tuple(
        2 * sum(max(0, state.pair[owner][other] - 1) for other in range(N))
        for owner in range(N)
    )
    owners = tuple(owner for owner, amount in enumerate(amounts) if amount)
    return owners, tuple(amounts[owner] for owner in owners)


def collision_obligations(state: TupleState, owner: int):
    for other in range(N):
        for copy in range(max(0, state.pair[owner][other] - 1)):
            for half in (0, 1):
                yield (owner, other, copy, half)


def add_owner_mask(target: dict[int, int], base: int, owner_bit: int) -> None:
    target[base] = target.get(base, 0) | owner_bit


def p1_relation(
    _ctx: GraphContext, state: TupleState, owners: tuple[int, ...]
) -> dict[int, int]:
    relation: dict[int, int] = {}
    for index, owner in enumerate(owners):
        bit = 1 << index
        for other in range(N):
            if other != owner and state.pair[owner][other] == 0:
                add_owner_mask(relation, N * owner + other, bit)
    return relation


def p2_relation(
    ctx: GraphContext, state: TupleState, owners: tuple[int, ...]
) -> dict[int, int]:
    relation: dict[int, int] = {}
    for index, owner in enumerate(owners):
        bit = 1 << index
        neighbors = sorted(ctx.bad_adj[owner])
        for left in neighbors:
            for right in neighbors:
                if (
                    left != right
                    and state.pair[left][right] == 0
                    and ctx.sigma_pair[left][right] >= 0
                ):
                    add_owner_mask(relation, N * left + right, bit)
    return relation


def p3_relation(
    ctx: GraphContext, state: TupleState, owners: tuple[int, ...]
) -> dict[int, int]:
    relation: dict[int, int] = {}
    for index, owner in enumerate(owners):
        bit = 1 << index
        companions = [vertex for vertex in range(N) if state.pair[owner][vertex] > 0]
        for left in companions:
            for right in companions:
                if (
                    left != right
                    and state.pair[left][right] == 0
                    and ctx.sigma_pair[left][right] >= 0
                ):
                    add_owner_mask(relation, N * left + right, bit)
    return relation


def common_blue_relation(
    ctx: GraphContext, state: TupleState, owners: tuple[int, ...]
) -> dict[int, int]:
    relation: dict[int, int] = {}
    for index, owner in enumerate(owners):
        bit = 1 << index
        neighbors = sorted(ctx.blue_adj[owner])
        for left in neighbors:
            for right in neighbors:
                if (
                    left != right
                    and state.pair[left][right] == 0
                    and ctx.sigma_pair[left][right] >= 2
                ):
                    add_owner_mask(relation, N * left + right, bit)
    return relation


def attachment_relation(
    ctx: GraphContext,
    state: TupleState,
    owners: tuple[int, ...],
    *,
    allowed: set[int],
    boundary_vertices: set[int],
    require_active_component: bool,
) -> dict[int, int]:
    if not owners or not allowed or not boundary_vertices:
        return {}
    comp_id, component_list, component_masks = components(ctx.blue, allowed)
    del comp_id
    boundaries: list[set[int]] = []
    for component in component_list:
        boundary: set[int] = set()
        for vertex in component:
            boundary.update(
                neighbor
                for neighbor in ctx.blue_adj[vertex]
                if neighbor in boundary_vertices
            )
        boundaries.append(boundary)
    eligible_masks: list[int] = []
    for boundary in boundaries:
        owner_mask = 0
        for index, owner in enumerate(owners):
            owner_component = state.selected_comp[owner]
            if any(
                state.pair[owner][attachment] > 0
                and (
                    not require_active_component
                    or state.selected_comp[attachment] == owner_component
                )
                for attachment in boundary
            ):
                owner_mask |= 1 << index
        eligible_masks.append(owner_mask)

    relation: dict[int, int] = {}
    for left_index, left_vertices in enumerate(component_list):
        left_mask = eligible_masks[left_index]
        if not left_mask:
            continue
        for right_index, right_vertices in enumerate(component_list):
            owner_mask = left_mask & eligible_masks[right_index]
            if not owner_mask:
                continue
            switch = component_masks[left_index] | component_masks[right_index]
            if ctx.sigma(switch) < 0:
                continue
            for left in left_vertices:
                for right in right_vertices:
                    if left != right and state.pair[left][right] == 0:
                        add_owner_mask(relation, N * left + right, owner_mask)
    return relation


def p4_relation(
    ctx: GraphContext, state: TupleState, owners: tuple[int, ...]
) -> dict[int, int]:
    return attachment_relation(
        ctx,
        state,
        owners,
        allowed=set(range(N)) - state.selected,
        boundary_vertices=set(state.selected),
        require_active_component=False,
    )


def p5_relation(
    ctx: GraphContext, state: TupleState, owners: tuple[int, ...]
) -> dict[int, int]:
    return attachment_relation(
        ctx,
        state,
        owners,
        allowed=set(range(N)) - state.active_vertices,
        boundary_vertices=set(state.active_vertices),
        require_active_component=True,
    )


FAMILY_BUILDERS = {
    "P1_sameFirst": p1_relation,
    "P2_commonBad": p2_relation,
    "P3_rowCompanion": p3_relation,
    "P4_outsideAttachment": p4_relation,
    "P5_quiescentAttachment": p5_relation,
    "commonBlue": common_blue_relation,
}


def merge_relation(target: dict[int, int], source: dict[int, int]) -> None:
    for base, owners in source.items():
        target[base] = target.get(base, 0) | owners


@dataclass
class Arc:
    to: int
    rev: int
    cap: int
    initial: int


class Dinic:
    def __init__(self) -> None:
        self.graph: list[list[Arc]] = []

    def node(self) -> int:
        self.graph.append([])
        return len(self.graph) - 1

    def add_edge(self, source: int, target: int, capacity: int) -> Arc:
        if capacity < 0:
            raise ValueError(capacity)
        forward = Arc(target, len(self.graph[target]), capacity, capacity)
        reverse = Arc(source, len(self.graph[source]), 0, 0)
        self.graph[source].append(forward)
        self.graph[target].append(reverse)
        return forward

    def max_flow(self, source: int, sink: int) -> int:
        total = 0
        while True:
            level = [-1] * len(self.graph)
            level[source] = 0
            queue = deque([source])
            while queue:
                vertex = queue.popleft()
                for arc in self.graph[vertex]:
                    if arc.cap and level[arc.to] < 0:
                        level[arc.to] = level[vertex] + 1
                        queue.append(arc.to)
            if level[sink] < 0:
                return total
            cursor = [0] * len(self.graph)

            def send(vertex: int, amount: int) -> int:
                if vertex == sink:
                    return amount
                while cursor[vertex] < len(self.graph[vertex]):
                    arc = self.graph[vertex][cursor[vertex]]
                    if arc.cap and level[arc.to] == level[vertex] + 1:
                        pushed = send(arc.to, min(amount, arc.cap))
                        if pushed:
                            arc.cap -= pushed
                            self.graph[arc.to][arc.rev].cap += pushed
                            return pushed
                    cursor[vertex] += 1
                return 0

            while True:
                pushed = send(source, 1 << 60)
                if not pushed:
                    break
                total += pushed


def solve_grouped_flow(
    owners: tuple[int, ...],
    demand: tuple[int, ...],
    relation: dict[int, int],
    active_edges: Iterable[Edge],
) -> dict:
    active = tuple(sorted(set(active_edges)))
    active_base: dict[int, Edge] = {}
    for left, right in active:
        active_base[N * left + right] = (left, right)
        active_base[N * right + left] = (left, right)

    direct_counts: Counter[int] = Counter()
    edge_pools: dict[Edge, dict[int, int]] = {}
    for base, mask in relation.items():
        if not mask:
            continue
        edge = active_base.get(base)
        if edge is None:
            direct_counts[mask] += 2
        else:
            edge_pools.setdefault(edge, {})[mask] = (
                edge_pools.setdefault(edge, {}).get(mask, 0) + 2
            )

    network = Dinic()
    source = network.node()
    sink = network.node()
    owner_nodes = [network.node() for _ in owners]
    for node, amount in zip(owner_nodes, demand):
        network.add_edge(source, node, amount)
    infinity = sum(demand)

    def add_pool(mask: int, capacity: int, target: int) -> None:
        node = network.node()
        bits = mask
        while bits:
            bit = bits & -bits
            index = bit.bit_length() - 1
            network.add_edge(owner_nodes[index], node, infinity)
            bits ^= bit
        network.add_edge(node, target, capacity)

    for mask, capacity in sorted(direct_counts.items()):
        add_pool(mask, capacity, sink)
    for edge in active:
        group = network.node()
        network.add_edge(group, sink, 2)
        for mask, capacity in sorted(edge_pools.get(edge, {}).items()):
            add_pool(mask, capacity, group)

    maximum = network.max_flow(source, sink)
    total = sum(demand)
    return {
        "activeEdgeGroups": len(active),
        "defect": total - maximum,
        "directMaskPools": len(direct_counts),
        "maximumFlow": maximum,
        "networkNodes": len(network.graph),
        "totalDemand": total,
    }


@dataclass
class ExactModel:
    rows: tuple[Row, ...]
    state: TupleState
    owners: tuple[int, ...]
    demand: tuple[int, ...]
    relation: dict[int, int]
    flow: dict
    collision_units: int

    @property
    def defect(self) -> int:
        return self.flow["defect"]


def exact_model(ctx: GraphContext, rows: Iterable[Row]) -> ExactModel:
    normalized = tuple(rows)
    state = reconstruct_state(normalized)
    owners, demand = global_demands(state)
    relation: dict[int, int] = {}
    for family in FAMILY_ORDER:
        merge_relation(relation, FAMILY_BUILDERS[family](ctx, state, owners))
    flow = solve_grouped_flow(owners, demand, relation, state.active_edges)
    if flow["maximumFlow"] + flow["defect"] != flow["totalDemand"]:
        raise AssertionError("flow accounting failed")
    if flow["totalDemand"] % 2:
        raise AssertionError("CollisionHalf demand is not even")
    return ExactModel(
        rows=normalized,
        state=state,
        owners=owners,
        demand=demand,
        relation=relation,
        flow=flow,
        collision_units=flow["totalDemand"] // 2,
    )


def lower_bound_circulation(node_count: int, specs):
    network = Dinic()
    for _ in range(node_count + 2):
        network.node()
    super_source = node_count
    super_sink = node_count + 1
    balance = [0] * node_count
    records = []
    for source, target, lower, upper, label in specs:
        if not 0 <= lower <= upper:
            raise AssertionError((source, target, lower, upper, label))
        arc = network.add_edge(source, target, upper - lower)
        balance[source] -= lower
        balance[target] += lower
        records.append((arc, lower, label))
    required = 0
    for vertex, amount in enumerate(balance):
        if amount > 0:
            network.add_edge(super_source, vertex, amount)
            required += amount
        elif amount < 0:
            network.add_edge(vertex, super_sink, -amount)
    if network.max_flow(super_source, super_sink) != required:
        return None
    return [
        (label, lower + (arc.initial - arc.cap))
        for arc, lower, label in records
    ]


def forced_divergence_feasible(model: ExactModel) -> bool:
    base = N * FORK_LEFT + FORK_RIGHT
    if not model.relation.get(base, 0) or model.flow["maximumFlow"] < 2:
        return False
    if model.state.pair[FORK_LEFT][FORK_RIGHT] != 0:
        return False

    source = 0
    sink = 1
    next_node = 2
    owner_nodes: dict[int, int] = {}
    for owner in model.owners:
        owner_nodes[owner] = next_node
        next_node += 1
    active_nodes: dict[Edge, int] = {}
    for edge in sorted(model.state.active_edges):
        active_nodes[edge] = next_node
        next_node += 1
    pool_nodes: dict[int, int] = {}
    for ordered_base in sorted(model.relation):
        pool_nodes[ordered_base] = next_node
        next_node += 1

    infinity = max(1, sum(model.demand))
    specs = []
    for owner, amount in zip(model.owners, model.demand):
        specs.append((source, owner_nodes[owner], 0, amount, ("source-owner", owner)))
    for ordered_base, mask in sorted(model.relation.items()):
        left, right = divmod(ordered_base, N)
        pool = pool_nodes[ordered_base]
        bits = mask
        while bits:
            bit = bits & -bits
            owner = model.owners[bit.bit_length() - 1]
            specs.append(
                (owner_nodes[owner], pool, 0, infinity, ("owner-pool", owner, ordered_base))
            )
            bits ^= bit
        edge = norm_edge(left, right)
        target = active_nodes[edge] if edge in active_nodes else sink
        lower = 2 if ordered_base == base else 0
        specs.append((pool, target, lower, 2, ("pool-out", ordered_base)))
    for edge, group in sorted(active_nodes.items()):
        specs.append((group, sink, 0, 2, ("active-cap", edge)))
    specs.append(
        (sink, source, model.flow["maximumFlow"], model.flow["maximumFlow"], ("fixed-optimum",))
    )
    return lower_bound_circulation(next_node, specs) is not None


def explicit_forced_flow(model: ExactModel) -> dict:
    obligations = tuple(
        obligation
        for owner in model.owners
        for obligation in collision_obligations(model.state, owner)
    )
    keys = tuple(
        (ordered_base // N, ordered_base % N, half)
        for ordered_base in sorted(model.relation)
        for half in (0, 1)
    )
    owner_index = {owner: index for index, owner in enumerate(model.owners)}
    active_edges = frozenset(model.state.active_edges)

    source = 0
    sink = 1
    next_node = 2
    obligation_node: dict[Obligation, int] = {}
    for obligation in obligations:
        obligation_node[obligation] = next_node
        next_node += 1
    key_node: dict[SourceKey, int] = {}
    for key in keys:
        key_node[key] = next_node
        next_node += 1
    group_node: dict[Edge, int] = {}
    for edge in sorted(active_edges):
        group_node[edge] = next_node
        next_node += 1

    forced = {
        (FORK_LEFT, FORK_RIGHT, 0),
        (FORK_LEFT, FORK_RIGHT, 1),
    }
    specs = []
    for obligation in obligations:
        specs.append((source, obligation_node[obligation], 0, 1, ("source-obligation", obligation)))
        bit = 1 << owner_index[obligation[0]]
        for key in keys:
            ordered_base = N * key[0] + key[1]
            if model.relation.get(ordered_base, 0) & bit:
                specs.append(
                    (
                        obligation_node[obligation],
                        key_node[key],
                        0,
                        1,
                        ("obligation-key", obligation, key),
                    )
                )
    for key in keys:
        edge = norm_edge(key[0], key[1])
        target = group_node[edge] if edge in active_edges else sink
        specs.append((key_node[key], target, int(key in forced), 1, ("key-out", key)))
    for edge, node in sorted(group_node.items()):
        specs.append((node, sink, 0, 2, ("group-out", edge)))
    specs.append(
        (sink, source, model.flow["maximumFlow"], model.flow["maximumFlow"], ("fixed-optimum",))
    )
    flows = lower_bound_circulation(next_node, specs)
    if flows is None:
        raise AssertionError("both divergence halves cannot be forced in an optimum")
    assignment = {
        label[1]: label[2]
        for label, amount in flows
        if label[0] == "obligation-key" and amount == 1
    }
    if len(assignment) != model.flow["maximumFlow"]:
        raise AssertionError("forced assignment has wrong cardinality")
    if len(set(assignment.values())) != len(assignment):
        raise AssertionError("forced assignment reuses a literal key")
    if not forced <= set(assignment.values()):
        raise AssertionError("forced divergence keys are absent")
    active_load = Counter(
        norm_edge(*key[:2])
        for key in assignment.values()
        if norm_edge(*key[:2]) in active_edges
    )
    if any(load > 2 for load in active_load.values()):
        raise AssertionError("active-edge grouped capacity exceeded")
    return {
        "activeEdges": active_edges,
        "assignment": assignment,
        "keys": keys,
        "obligations": obligations,
    }


def residual_unit_core(model: ExactModel, explicit: dict) -> tuple[dict, dict]:
    obligations: tuple[Obligation, ...] = explicit["obligations"]
    keys: tuple[SourceKey, ...] = explicit["keys"]
    assignment: dict[Obligation, SourceKey] = explicit["assignment"]
    active_edges: frozenset[Edge] = explicit["activeEdges"]
    matched_by_key = {key: obligation for obligation, key in assignment.items()}
    unmatched = tuple(sorted(set(obligations) - set(assignment)))
    if not unmatched:
        raise AssertionError("positive core requested from a total flow")
    root = unmatched[0]
    owner_index = {owner: index for index, owner in enumerate(model.owners)}
    residual: dict[tuple, set[tuple]] = {}

    def arc(source_node: tuple, target_node: tuple) -> None:
        residual.setdefault(source_node, set()).add(target_node)

    for obligation in obligations:
        owner_bit = 1 << owner_index[obligation[0]]
        for key in keys:
            ordered_base = N * key[0] + key[1]
            if not (model.relation.get(ordered_base, 0) & owner_bit):
                continue
            if assignment.get(obligation) == key:
                arc(("k", key), ("o", obligation))
            else:
                arc(("o", obligation), ("k", key))
    for key in keys:
        edge = norm_edge(*key[:2])
        target = ("g", edge) if edge in active_edges else ("t", None)
        if key in matched_by_key:
            arc(target, ("k", key))
        else:
            arc(("k", key), target)
    for edge in active_edges:
        load = sum(norm_edge(*key[:2]) == edge for key in assignment.values())
        if load < 2:
            arc(("g", edge), ("t", None))
        if load:
            arc(("t", None), ("g", edge))

    reached = {("o", root)}
    queue = deque(reached)
    while queue:
        node = queue.popleft()
        for neighbor in residual.get(node, ()):
            if neighbor not in reached:
                reached.add(neighbor)
                queue.append(neighbor)
    if ("t", None) in reached:
        raise AssertionError("maximum flow has an augmenting residual path")
    reached_obligations = {value for kind, value in reached if kind == "o"}
    reached_keys = {value for kind, value in reached if kind == "k"}
    direct_capacity = sum(
        norm_edge(*key[:2]) not in active_edges for key in reached_keys
    )
    active_counts = Counter(
        norm_edge(*key[:2])
        for key in reached_keys
        if norm_edge(*key[:2]) in active_edges
    )
    grouped_capacity = direct_capacity + sum(min(2, count) for count in active_counts.values())
    forced_keys = (
        (FORK_LEFT, FORK_RIGHT, 0),
        (FORK_LEFT, FORK_RIGHT, 1),
    )
    successors = tuple(matched_by_key[key] for key in forced_keys)
    residual_closed = all(
        neighbor in reached
        for node in reached
        for neighbor in residual.get(node, ())
    )
    raw = {
        "activeReachedGroupCounts": {
            f"{edge[0]},{edge[1]}": count
            for edge, count in sorted(active_counts.items())
        },
        "bothHalvesMatched": True,
        "directReachedCapacity": direct_capacity,
        "forkKeysReached": all(key in reached_keys for key in forced_keys),
        "globalDefect": model.defect,
        "leastUnmatchedRoot": list(root),
        "noSimultaneous": True,
        "obligationCount": len(reached_obligations),
        "positiveUnitDefect": len(reached_obligations) == grouped_capacity + 1,
        "rawReachedSourceKeys": len(reached_keys),
        "residualSinkUnreachable": True,
        "sourceCapacity": grouped_capacity,
        "successorObligations": [list(obligation) for obligation in successors],
        "successorSinkClosed": residual_closed,
        "successorsInUnitCore": all(
            obligation in reached_obligations for obligation in successors
        ),
    }
    owners = sorted({obligation[0] for obligation in reached_obligations})
    owner_set = set(owners)
    selected_load = sum(5 * model.state.pair[owner][owner] for owner in owners)
    internal_active = sum(
        left in owner_set and right in owner_set
        for left, right in model.state.active_edges
    )
    shore_zero = sum(
        model.state.pair[owner][other] == 0
        for owner in owners
        for other in range(N)
    )
    shore_collision = sum(
        max(0, model.state.pair[owner][other] - 1)
        for owner in owners
        for other in range(N)
    )
    detail = {
        "forkKeys": [list(key) for key in forced_keys],
        "ownerSet": owners,
        "ownerSetLabels": [VERTEX_NAMES[owner] for owner in owners],
        "overload": {
            "internalActive": internal_active,
            "leftNCardA": N * len(owners),
            "p1GroupedCapacity": 2 * (shore_zero - internal_active),
            "p1GroupedDemand": 2 * shore_collision,
            "shoreCollision": shore_collision,
            "shoreSelectedLoad": selected_load,
            "shoreZero": shore_zero,
            "strict": N * len(owners) < selected_load + internal_active,
            "rightLoadPlusInternal": selected_load + internal_active,
        },
        "reachedObligations": len(reached_obligations),
        "reachedSourceKeys": len(reached_keys),
        "unmatchedGlobalObligations": len(unmatched),
    }
    if shore_collision + N * len(owners) != selected_load + shore_zero:
        raise AssertionError("owner-shore overload identity failed")
    return raw, detail


def choice_rows(choice: Choice) -> tuple[Row, ...]:
    return tuple((LEFT_ROW, RIGHT_ROW)[value] for value in choice)


def census(ctx: GraphContext) -> tuple[dict, dict[Choice, ExactModel]]:
    records = []
    models: dict[Choice, ExactModel] = {}
    saturable: dict[Choice, bool] = {}
    for choice in product((0, 1), repeat=ATOM_COPIES):
        model = exact_model(ctx, choice_rows(choice))
        models[choice] = model
        saturable[choice] = forced_divergence_feasible(model)
    collision_minimum = min(model.collision_units for model in models.values())
    defect_minimum = min(
        model.defect
        for model in models.values()
        if model.collision_units == collision_minimum
    )
    histogram: Counter[tuple[int, int]] = Counter()
    for choice in sorted(models):
        model = models[choice]
        lex_minimal = (
            model.collision_units == collision_minimum
            and model.defect == defect_minimum
        )
        histogram[(model.collision_units, model.defect)] += 1
        records.append(
            {
                "choice": list(choice),
                "choiceCode": "".join(str(value) for value in choice),
                "collisionUnits": model.collision_units,
                "defect": model.defect,
                "forkBothHalvesSaturable": saturable[choice],
                "lexMinimal": lex_minimal,
                "leftRows": choice.count(0),
                "rightRows": choice.count(1),
            }
        )
    lex_records = [record for record in records if record["lexMinimal"]]
    summary = {
        "bothHalvesSaturableLexStates": sum(
            record["forkBothHalvesSaturable"] for record in lex_records
        ),
        "collisionMinimum": collision_minimum,
        "defectMinimumOnCollisionFace": defect_minimum,
        "firstDivergenceFreeLexStates": len(lex_records),
        "lexFaceStates": len(lex_records),
        "metricHistogram": {
            f"{collision},{defect}": count
            for (collision, defect), count in sorted(histogram.items())
        },
        "positivePayloadLexStates": sum(record["defect"] > 0 for record in lex_records),
        "rotorCandidateLexStates": sum(
            record["defect"] > 0 and record["forkBothHalvesSaturable"]
            for record in lex_records
        ),
        "rowTuples": len(records),
    }
    expected = {
        "bothHalvesSaturableLexStates": 420,
        "collisionMinimum": 179,
        "defectMinimumOnCollisionFace": 50,
        "firstDivergenceFreeLexStates": 420,
        "lexFaceStates": 420,
        "metricHistogram": {
            "179,106": 18,
            "179,50": 420,
            "179,76": 72,
            "200,50": 2,
        },
        "positivePayloadLexStates": 420,
        "rotorCandidateLexStates": 420,
        "rowTuples": 512,
    }
    if summary != expected:
        raise AssertionError((summary, expected))
    return {"records": records, "summary": summary}, models


def replacement_audit(
    census_payload: dict, models: dict[Choice, ExactModel]
) -> dict:
    current = models[CURRENT_CHOICE]
    records_by_choice = {
        tuple(record["choice"]): record for record in census_payload["records"]
    }
    replacements = []
    for index in range(ATOM_COPIES):
        changed = list(CURRENT_CHOICE)
        before = changed[index]
        changed[index] = 1 - changed[index]
        replacement = tuple(changed)
        record = records_by_choice[replacement]
        replacements.append(
            {
                "atom": index,
                "choice": list(replacement),
                "collisionDelta": record["collisionUnits"] - current.collision_units,
                "collisionUnits": record["collisionUnits"],
                "defect": record["defect"],
                "defectDelta": record["defect"] - current.defect,
                "direction": "P_to_Q" if before == 0 else "Q_to_P",
            }
        )
    if any(item["collisionDelta"] < 0 or item["defectDelta"] < 0 for item in replacements):
        raise AssertionError("one-row replacement lowers collision or defect")
    classes = {}
    for direction in ("P_to_Q", "Q_to_P"):
        selected = [item for item in replacements if item["direction"] == direction]
        classes[direction] = {
            "atoms": [item["atom"] for item in selected],
            "count": len(selected),
            "metrics": sorted({(item["collisionUnits"], item["defect"]) for item in selected}),
        }
        classes[direction]["metrics"] = [list(value) for value in classes[direction]["metrics"]]
    return {
        "allPreserveLexMetric": all(
            item["collisionDelta"] == 0 and item["defectDelta"] == 0
            for item in replacements
        ),
        "classes": classes,
        "currentChoice": list(CURRENT_CHOICE),
        "currentMetric": [current.collision_units, current.defect],
        "replacements": replacements,
    }


def input_payload() -> dict:
    rows = shortest_rows(BASE_BLUE, CORE["s"], CORE["t"])
    if set(rows) != {LEFT_ROW, RIGHT_ROW}:
        raise AssertionError("complete shortest-row family changed")
    if triangle_count(BASE_EDGES) != 0 or not connected(BASE_BLUE):
        raise AssertionError("graph structural check failed")
    return {
        "atomCopies": ATOM_COPIES,
        "badEdge": edge_record(next(iter(BASE_BAD))),
        "badKeysNodup": False,
        "blueConnected": True,
        "blueEdges": [edge_record(edge) for edge in sorted(BASE_BLUE)],
        "checkedDuplicateAtoms": True,
        "completeShortestRowsForEachCopy": [row_record(row) for row in rows],
        "cutShore": [VERTEX_NAMES[vertex] for vertex in sorted(BASE_SHORE)],
        "edges": len(BASE_EDGES),
        "graphBadEdges": len(BASE_BAD),
        "listedBadAtoms": ATOM_COPIES,
        "triangleCount": 0,
        "vertices": N,
    }


def build_payload() -> dict:
    ctx = make_graph_context()
    cuts = graph_cut_audit()
    fractions = signed_cut_audit(ctx)
    census_payload, models = census(ctx)
    current = models[CURRENT_CHOICE]
    explicit = explicit_forced_flow(current)
    core, core_detail = residual_unit_core(current, explicit)
    replacements = replacement_audit(census_payload, models)

    relation_record = [[base, mask] for base, mask in sorted(current.relation.items())]
    assignment_record = [
        [list(obligation), list(key)]
        for obligation, key in sorted(explicit["assignment"].items())
    ]
    if len(relation_record) != 154 or len(assignment_record) != 308:
        raise AssertionError("current-state relation or forced flow cardinality changed")
    if core["obligationCount"] != 293 or core["sourceCapacity"] != 292:
        raise AssertionError("forced residual core cardinality changed")
    if core_detail["overload"]["leftNCardA"] != 112:
        raise AssertionError("owner set changed")
    if core_detail["overload"]["rightLoadPlusInternal"] != 200:
        raise AssertionError("owner overload changed")

    artifact_digests = {
        "censusSha256": digest_json(census_payload["records"]),
        "forcedAssignmentSha256": digest_json(assignment_record),
        "relationSha256": digest_json(relation_record),
        "unitCoreSha256": digest_json(core),
        "verifyPySha256": digest_path(Path(__file__).resolve()),
    }
    return {
        "artifactDigests": artifact_digests,
        "arithmetic": {
            "cutAndSignedBoundary": "fractions.Fraction",
            "floatingPointUsed": False,
            "flowAndCardinality": "Python exact integers",
        },
        "census": census_payload,
        "currentState": {
            "activeEdges": len(current.state.active_edges),
            "choice": list(CURRENT_CHOICE),
            "collisionUnits": current.collision_units,
            "defect": current.defect,
            "demandByOwner": {
                VERTEX_NAMES[owner]: amount
                for owner, amount in zip(current.owners, current.demand)
            },
            "forcedAssignmentCardinality": len(assignment_record),
            "maximumFlow": current.flow["maximumFlow"],
            "orderedRelationBases": len(relation_record),
            "selectedSupportEdges": len(current.state.support),
            "totalDemand": current.flow["totalDemand"],
        },
        "forcedResidualCore": core,
        "forcedResidualCoreDetail": core_detail,
        "graphCutAudit": cuts,
        "inputs": input_payload(),
        "oneRowReplacementAudit": replacements,
        "schema": "R58_POSITIVE_DEFECT_COMPILED_INTERFACE_COUNTERMODEL_V1",
        "scope": {
            "counterexampleTo": (
                "the compiled AllBadsChecked/GlobalSoftCapTrace interface bridge "
                "from owner overload plus a saturated same-atom fork to boundary "
                "overweight or lex descent"
            ),
            "notCounterexampleTo": (
                "a production theorem explicitly assuming "
                "CompleteShortestRowDB.badKeys_nodup"
            ),
            "reason": (
                "nine checked BadEdgeData atoms share the one graph bad edge; "
                "row multiplicity survives pairCount while graph boundaries use sets"
            ),
        },
        "signedCutAudit": fractions,
        "status": "PASS_R58_POSITIVE_DEFECT_INTERFACE_COUNTERMODEL",
    }


def report_text(payload: dict, result_sha: str) -> str:
    summary = payload["census"]["summary"]
    current = payload["currentState"]
    core = payload["forcedResidualCore"]
    detail = payload["forcedResidualCoreDetail"]
    overload = detail["overload"]
    replacements = payload["oneRowReplacementAudit"]
    digests = payload["artifactDigests"]
    signed = payload["signedCutAudit"]
    return f"""# R58 positive-defect compiled-interface countermodel

## Verdict

The 16-vertex R57 graph with nine checked copies of its sole `s-t` bad atom is
an exact countermodel to the compiled-interface bridge.  The selected tuple
uses four left rows and five right rows.  It is lex-minimal, has positive exact
grouped defect, saturates both first-divergence halves in an optimum, and has a
positive residual unit core.  No graph-only mask pair is four-corner
overweight, and neither class of one-row replacement lowers collision or
defect.

This is not a counterexample to a theorem explicitly assuming
`CompleteShortestRowDB.badKeys_nodup`: all nine listed atoms have the same one
graph bad-edge key.

## One-command replay

From `E:\\Projects\\ErdosProblems`:

```powershell
python -B tmp/fanout/r58_positive_defect_interface_countermodel/verify.py
```

Default mode rebuilds every check in memory and verifies `result.json` and
`REPORT.md` byte-for-byte.  `--write` is the explicit deterministic refresh
mode and writes only those two files in this directory.

## Exact arithmetic

- Signed cut engine: `fractions.Fraction`; floating point used: `false`.
- Switch masks checked: {signed['switchMasks']}.
- Row-union mask pairs checked: {signed['rowUnionMaskPairs']}.
- Four-corner identities checked: {signed['fourCornerIdentityChecks']}.
- Minimum switch loss: {signed['minimumSwitchLoss']['text']}.
- Minimum four-corner margin: {signed['minimumFourCornerMargin']['text']}.
- All observed Fraction denominators equal one: `{str(signed['allDenominatorsOne']).lower()}`.

## Full row-tuple census

All `{summary['rowTuples']}` choices in `{{P,Q}}^9` are listed in
`result.json`.

| Quantity | Exact value |
|---|---:|
| Collision minimum | {summary['collisionMinimum']} |
| Defect minimum on the collision face | {summary['defectMinimumOnCollisionFace']} |
| Lex-minimal tuples | {summary['lexFaceStates']} |
| Positive lex payloads | {summary['positivePayloadLexStates']} |
| Lex tuples with both fork halves saturable | {summary['bothHalvesSaturableLexStates']} |

Metric histogram: `{json.dumps(summary['metricHistogram'], sort_keys=True)}`.

## Selected state and forced core

- Choice: `{current['choice']}`.
- Collision/defect: `({current['collisionUnits']}, {current['defect']})`.
- Total demand / maximum flow: `{current['totalDemand']} / {current['maximumFlow']}`.
- Ordered relation bases: `{current['orderedRelationBases']}`.
- Forced assignment cardinality: `{current['forcedAssignmentCardinality']}`.
- Residual root: `{core['leastUnmatchedRoot']}`.
- Unit core: `|O_K|={core['obligationCount']}`, `cap(S_K)={core['sourceCapacity']}`.
- Fork halves reached and matched: `{str(core['forkKeysReached'] and core['bothHalvesMatched']).lower()}`.
- Successors lie in the core and the residual sink is unreachable:
  `{str(core['successorsInUnitCore'] and core['residualSinkUnreachable']).lower()}`.

The core owner set is `{detail['ownerSetLabels']}` and satisfies

```text
N*|A| = {overload['leftNCardA']}
shoreSelectedLoad(A) + internalActive(A) = {overload['rightLoadPlusInternal']}
2*shoreCollision(A) = {overload['p1GroupedDemand']}
p1GroupedCapacity(A) = {overload['p1GroupedCapacity']}
```

## One-row replacements

- Four `P_to_Q` replacements have metric
  `{replacements['classes']['P_to_Q']['metrics'][0]}`.
- Five `Q_to_P` replacements have metric
  `{replacements['classes']['Q_to_P']['metrics'][0]}`.
- Every one-coordinate replacement preserves `(collision, defect)`:
  `{str(replacements['allPreserveLexMetric']).lower()}`.

## SHA-256

```text
verify.py            {digests['verifyPySha256']}
result.json          {result_sha}
census records       {digests['censusSha256']}
relation             {digests['relationSha256']}
forced assignment    {digests['forcedAssignmentSha256']}
unit core            {digests['unitCoreSha256']}
```
"""


def expected_outputs() -> tuple[dict, bytes, bytes]:
    payload = build_payload()
    result_bytes = canonical_json_bytes(payload, pretty=True)
    report_bytes = report_text(payload, digest_bytes(result_bytes)).encode("ascii")
    return payload, result_bytes, report_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="refresh result.json and REPORT.md deterministically in this directory",
    )
    args = parser.parse_args()

    payload, result_bytes, report_bytes = expected_outputs()
    if args.write:
        RESULT_PATH.write_bytes(result_bytes)
        REPORT_PATH.write_bytes(report_bytes)
    else:
        if not RESULT_PATH.exists() or RESULT_PATH.read_bytes() != result_bytes:
            raise SystemExit("FAIL: result.json is missing or differs; run with --write to refresh")
        if not REPORT_PATH.exists() or REPORT_PATH.read_bytes() != report_bytes:
            raise SystemExit("FAIL: REPORT.md is missing or differs; run with --write to refresh")

    output = {
        "mode": "write" if args.write else "check",
        "reportSha256": digest_bytes(report_bytes),
        "resultSha256": digest_bytes(result_bytes),
        "status": payload["status"],
        "verifySha256": payload["artifactDigests"]["verifyPySha256"],
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
