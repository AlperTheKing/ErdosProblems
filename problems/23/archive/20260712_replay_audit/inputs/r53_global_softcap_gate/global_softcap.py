#!/usr/bin/env python3
"""Exact evaluator for the corrected global R53 soft-cap model.

The left side is every global ``CollisionHalf``.  The right side is made only
from literal ``FreeHalf`` triples ``(sourceX, sourceY, half)``.  Each key has
capacity one.  The four keys over every active undirected edge share capacity
two.  The resulting layered network is integral, so integer max flow computes
the exact rational optimum as well.

No active-only demand, fixed reservation, raw physical key, floating point, or
``native_decide`` analogue occurs here.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from typing import Callable, Iterable


Edge = tuple[int, int]
Row = tuple[int, ...]
SourceKey = tuple[int, int, int]

FAMILY_ORDER = (
    "P1_sameFirst",
    "P2_commonBad",
    "P3_rowCompanion",
    "P4_outsideAttachment",
    "P5_quiescentAttachment",
    "commonBlue",
)

# Cheap local relations are evaluated first.  Once a subset has defect zero,
# monotonicity proves that the full six-family union also has exact defect zero.
EVALUATION_ORDER = (
    "P1_sameFirst",
    "P2_commonBad",
    "P3_rowCompanion",
    "commonBlue",
    "P4_outsideAttachment",
    "P5_quiescentAttachment",
)

RELATION_PROVENANCE = {
    "P1_sameFirst": {
        "data": "reconstructed",
        "status": "compiled eligibility",
        "predicate": "sourceX = owner",
    },
    "P2_commonBad": {
        "data": "reconstructed",
        "status": "archival Python relation; no named production Lean disjunct",
        "predicate": (
            "sourceX and sourceY are distinct bad neighbours of owner and "
            "sigma({sourceX,sourceY}) >= 0"
        ),
    },
    "P3_rowCompanion": {
        "data": "reconstructed",
        "status": "compiled eligibility",
        "predicate": (
            "pair(owner,sourceX)>0, pair(owner,sourceY)>0, and "
            "sigma({sourceX,sourceY}) >= 0"
        ),
    },
    "P4_outsideAttachment": {
        "data": "reconstructed",
        "status": (
            "coherence-free R23 semantics; caller-supplied in production Lean"
        ),
        "predicate": (
            "selected-complement component attachment; no owner/source "
            "active-component equality after coherence is dropped"
        ),
    },
    "P5_quiescentAttachment": {
        "data": "reconstructed",
        "status": "archival exact semantics; caller-supplied in production Lean",
        "predicate": "quiescent B[V\\A] component attachment",
    },
    "commonBlue": {
        "data": "reconstructed",
        "status": "compiled terminal predicate; matching consumer absent",
        "predicate": (
            "sourceX and sourceY are blue neighbours of owner and "
            "sigma({sourceX,sourceY}) >= 2"
        ),
    },
}


def norm_edge(x: int, y: int) -> Edge:
    return (x, y) if x < y else (y, x)


def vertices(mask: int) -> list[int]:
    out: list[int] = []
    while mask:
        bit = mask & -mask
        out.append(bit.bit_length() - 1)
        mask ^= bit
    return out


@dataclass
class GraphContext:
    n: int
    blue: frozenset[Edge]
    bad: frozenset[Edge]
    blue_adj: tuple[frozenset[int], ...]
    bad_adj: tuple[frozenset[int], ...]
    sigma_pair: tuple[tuple[int, ...], ...]
    edge_sign: dict[Edge, int]
    sigma_cache: dict[int, int]

    def sigma(self, mask: int) -> int:
        cached = self.sigma_cache.get(mask)
        if cached is not None:
            return cached
        value = sum(
            sign
            for (x, y), sign in self.edge_sign.items()
            if bool(mask & (1 << x)) != bool(mask & (1 << y))
        )
        self.sigma_cache[mask] = value
        return value


def make_graph_context(
    n: int, blue: Iterable[Edge], bad: Iterable[Edge]
) -> GraphContext:
    blue_set = frozenset(norm_edge(*item) for item in blue)
    bad_set = frozenset(norm_edge(*item) for item in bad)
    if blue_set & bad_set:
        raise ValueError("blue and bad edge sets overlap")
    blue_adj = [set() for _ in range(n)]
    bad_adj = [set() for _ in range(n)]
    signed_degree = [0] * n
    edge_sign: dict[Edge, int] = {}
    for x, y in blue_set:
        if not (0 <= x < y < n):
            raise ValueError((n, x, y))
        blue_adj[x].add(y)
        blue_adj[y].add(x)
        signed_degree[x] += 1
        signed_degree[y] += 1
        edge_sign[(x, y)] = 1
    for x, y in bad_set:
        if not (0 <= x < y < n):
            raise ValueError((n, x, y))
        bad_adj[x].add(y)
        bad_adj[y].add(x)
        signed_degree[x] -= 1
        signed_degree[y] -= 1
        edge_sign[(x, y)] = -1
    sigma_pair = tuple(
        tuple(
            0
            if x == y
            else signed_degree[x]
            + signed_degree[y]
            - 2 * edge_sign.get(norm_edge(x, y), 0)
            for y in range(n)
        )
        for x in range(n)
    )
    return GraphContext(
        n=n,
        blue=blue_set,
        bad=bad_set,
        blue_adj=tuple(frozenset(items) for items in blue_adj),
        bad_adj=tuple(frozenset(items) for items in bad_adj),
        sigma_pair=sigma_pair,
        edge_sign=edge_sign,
        sigma_cache={0: 0},
    )


def _components(
    n: int, edges: Iterable[Edge], allowed: set[int]
) -> tuple[list[int], list[list[int]], list[int]]:
    adjacency = [[] for _ in range(n)]
    for x, y in edges:
        if x in allowed and y in allowed:
            adjacency[x].append(y)
            adjacency[y].append(x)
    comp_id = [-1] * n
    components: list[list[int]] = []
    masks: list[int] = []
    for root in sorted(allowed):
        if comp_id[root] >= 0:
            continue
        cid = len(components)
        comp_id[root] = cid
        queue = deque([root])
        component: list[int] = []
        mask = 0
        while queue:
            x = queue.popleft()
            component.append(x)
            mask |= 1 << x
            for y in adjacency[x]:
                if comp_id[y] < 0:
                    comp_id[y] = cid
                    queue.append(y)
        components.append(component)
        masks.append(mask)
    return comp_id, components, masks


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


def reconstruct_state(ctx: GraphContext, rows: Iterable[Iterable[int]]) -> TupleState:
    normalized = tuple(tuple(row) for row in rows)
    pair = [[0] * ctx.n for _ in range(ctx.n)]
    row_count = [0] * ctx.n
    selected: set[int] = set()
    support: set[Edge] = set()
    for row in normalized:
        if len(row) != 5 or len(set(row)) != 5:
            raise ValueError(f"not a five-distinct-vertex row: {row}")
        if not all(0 <= x < ctx.n for x in row):
            raise ValueError(f"row vertex outside graph: {row}")
        if norm_edge(row[0], row[-1]) not in ctx.bad:
            raise ValueError(f"row endpoints are not a bad edge: {row}")
        for x in row:
            row_count[x] += 1
            selected.add(x)
            for y in row:
                pair[x][y] += 1
        for x, y in zip(row, row[1:]):
            item = norm_edge(x, y)
            if item not in ctx.blue:
                raise ValueError(f"row step is not blue: {item}")
            support.add(item)
    active_edges = {
        item
        for item in ctx.blue
        if item not in support and item[0] in selected and item[1] in selected
    }
    selected_comp, _components_list, _masks = _components(
        ctx.n, active_edges, selected
    )
    active_comp_ids = {
        selected_comp[x]
        for x, y in ctx.bad
        if x in selected
        and y in selected
        and selected_comp[x] == selected_comp[y]
    }
    active_vertices = {
        x for x in selected if selected_comp[x] in active_comp_ids
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
        2 * sum(max(0, state.pair[x][y] - 1) for y in range(len(state.pair)))
        for x in range(len(state.pair))
    )
    owners = tuple(x for x, amount in enumerate(amounts) if amount)
    return owners, tuple(amounts[x] for x in owners)


def collision_obligations(state: TupleState, owner: int):
    for other in range(len(state.pair)):
        for copy in range(max(0, state.pair[owner][other] - 1)):
            for half in (0, 1):
                yield (owner, other, copy, half)


def _add_mask(target: dict[int, int], base: int, owner_bit: int) -> None:
    target[base] = target.get(base, 0) | owner_bit


def _p1(
    ctx: GraphContext, state: TupleState, owners: tuple[int, ...]
) -> tuple[dict[int, int], dict]:
    relation: dict[int, int] = {}
    for index, owner in enumerate(owners):
        bit = 1 << index
        for y in range(ctx.n):
            if y != owner and state.pair[owner][y] == 0:
                _add_mask(relation, ctx.n * owner + y, bit)
    return relation, {}


def _p2_common_bad(
    ctx: GraphContext, state: TupleState, owners: tuple[int, ...]
) -> tuple[dict[int, int], dict]:
    relation: dict[int, int] = {}
    for index, owner in enumerate(owners):
        bit = 1 << index
        neighbors = sorted(ctx.bad_adj[owner])
        for x in neighbors:
            for y in neighbors:
                if (
                    x != y
                    and state.pair[x][y] == 0
                    and ctx.sigma_pair[x][y] >= 0
                ):
                    _add_mask(relation, ctx.n * x + y, bit)
    return relation, {}


def _p3(
    ctx: GraphContext, state: TupleState, owners: tuple[int, ...]
) -> tuple[dict[int, int], dict]:
    relation: dict[int, int] = {}
    for index, owner in enumerate(owners):
        bit = 1 << index
        companions = [x for x in range(ctx.n) if state.pair[owner][x] > 0]
        for x in companions:
            for y in companions:
                if (
                    x != y
                    and state.pair[x][y] == 0
                    and ctx.sigma_pair[x][y] >= 0
                ):
                    _add_mask(relation, ctx.n * x + y, bit)
    return relation, {}


def _common_blue(
    ctx: GraphContext, state: TupleState, owners: tuple[int, ...]
) -> tuple[dict[int, int], dict]:
    relation: dict[int, int] = {}
    for index, owner in enumerate(owners):
        bit = 1 << index
        neighbors = sorted(ctx.blue_adj[owner])
        for x in neighbors:
            for y in neighbors:
                if (
                    x != y
                    and state.pair[x][y] == 0
                    and ctx.sigma_pair[x][y] >= 2
                ):
                    _add_mask(relation, ctx.n * x + y, bit)
    return relation, {}


def _attachment(
    ctx: GraphContext,
    state: TupleState,
    owners: tuple[int, ...],
    *,
    allowed: set[int],
    boundary_vertices: set[int],
    require_active_component: bool,
) -> tuple[dict[int, int], dict]:
    if not owners or not allowed or not boundary_vertices:
        return {}, {
            "components": len(allowed),
            "nonemptyBoundaries": 0,
            "checkedOrderedBases": 0,
            "negativeOrderedBases": 0,
        }
    comp_id, components, component_masks = _components(ctx.n, ctx.blue, allowed)
    boundaries: list[set[int]] = []
    for component in components:
        boundary: set[int] = set()
        for x in component:
            boundary.update(y for y in ctx.blue_adj[x] if y in boundary_vertices)
        boundaries.append(boundary)
    eligible_masks: list[int] = []
    for boundary in boundaries:
        mask = 0
        for index, owner in enumerate(owners):
            owner_component = state.selected_comp[owner]
            if any(
                state.pair[owner][a] > 0
                and (
                    not require_active_component
                    or state.selected_comp[a] == owner_component
                )
                for a in boundary
            ):
                mask |= 1 << index
        eligible_masks.append(mask)

    relation: dict[int, int] = {}
    checked = 0
    negative = 0
    for left_id, left_vertices in enumerate(components):
        left_mask = eligible_masks[left_id]
        if not left_mask:
            continue
        for right_id, right_vertices in enumerate(components):
            owner_mask = left_mask & eligible_masks[right_id]
            if not owner_mask:
                continue
            switch_mask = component_masks[left_id] | component_masks[right_id]
            switch_nonnegative = ctx.sigma(switch_mask) >= 0
            for x in left_vertices:
                for y in right_vertices:
                    if x == y or state.pair[x][y] != 0:
                        continue
                    checked += 1
                    if not switch_nonnegative:
                        negative += 1
                        continue
                    _add_mask(relation, ctx.n * x + y, owner_mask)
    return relation, {
        "components": len(components),
        "nonemptyBoundaries": sum(bool(item) for item in boundaries),
        "checkedOrderedBases": checked,
        "negativeOrderedBases": negative,
        "componentEqualityRequired": require_active_component,
    }


def _p4(
    ctx: GraphContext, state: TupleState, owners: tuple[int, ...]
) -> tuple[dict[int, int], dict]:
    return _attachment(
        ctx,
        state,
        owners,
        allowed=set(range(ctx.n)) - state.selected,
        boundary_vertices=set(state.selected),
        require_active_component=False,
    )


def _p5(
    ctx: GraphContext, state: TupleState, owners: tuple[int, ...]
) -> tuple[dict[int, int], dict]:
    return _attachment(
        ctx,
        state,
        owners,
        allowed=set(range(ctx.n)) - state.active_vertices,
        boundary_vertices=set(state.active_vertices),
        require_active_component=True,
    )


FAMILY_BUILDERS: dict[
    str,
    Callable[
        [GraphContext, TupleState, tuple[int, ...]], tuple[dict[int, int], dict]
    ],
] = {
    "P1_sameFirst": _p1,
    "P2_commonBad": _p2_common_bad,
    "P3_rowCompanion": _p3,
    "P4_outsideAttachment": _p4,
    "P5_quiescentAttachment": _p5,
    "commonBlue": _common_blue,
}


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
                x = queue.popleft()
                for arc in self.graph[x]:
                    if arc.cap and level[arc.to] < 0:
                        level[arc.to] = level[x] + 1
                        queue.append(arc.to)
            if level[sink] < 0:
                return total
            cursor = [0] * len(self.graph)

            def send(x: int, amount: int) -> int:
                if x == sink:
                    return amount
                while cursor[x] < len(self.graph[x]):
                    arc = self.graph[x][cursor[x]]
                    if arc.cap and level[arc.to] == level[x] + 1:
                        pushed = send(arc.to, min(amount, arc.cap))
                        if pushed:
                            arc.cap -= pushed
                            self.graph[arc.to][arc.rev].cap += pushed
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
                if arc.cap and arc.to not in seen:
                    seen.add(arc.to)
                    queue.append(arc.to)
        return seen


def _used(arc: Arc) -> int:
    return arc.initial - arc.cap


def solve_grouped_flow(
    n: int,
    owners: tuple[int, ...],
    demand: tuple[int, ...],
    base_masks: dict[int, int],
    active_edges: Iterable[Edge],
    *,
    extract_assignment: bool = False,
) -> tuple[dict, dict[int, list[SourceKey]]]:
    if len(owners) != len(demand):
        raise ValueError("owner/demand length mismatch")
    active = tuple(sorted(set(active_edges)))
    active_base: dict[int, Edge] = {}
    for x, y in active:
        active_base[n * x + y] = (x, y)
        active_base[n * y + x] = (x, y)

    direct_counts: Counter[int] = Counter()
    direct_bases: dict[int, list[int]] = {}
    edge_pools: dict[Edge, dict[int, list[SourceKey]]] = {}
    for base, mask in base_masks.items():
        if not mask:
            continue
        x, y = divmod(base, n)
        if x == y:
            raise AssertionError("relation contains a diagonal source")
        edge = active_base.get(base)
        if edge is None:
            direct_counts[mask] += 2
            if extract_assignment:
                direct_bases.setdefault(mask, []).append(base)
        else:
            edge_pools.setdefault(edge, {}).setdefault(mask, []).extend(
                ((x, y, 0), (x, y, 1))
            )

    network = Dinic()
    source = network.node()
    sink = network.node()
    owner_nodes = [network.node() for _ in owners]
    for node, amount in zip(owner_nodes, demand):
        network.add_edge(source, node, amount)
    infinity = sum(demand)
    pool_records: list[dict] = []

    def add_pool(mask: int, capacity: int, keys, target: int) -> None:
        node = network.node()
        owner_arcs: list[tuple[int, Arc]] = []
        bits = mask
        while bits:
            bit = bits & -bits
            index = bit.bit_length() - 1
            owner_arcs.append(
                (index, network.add_edge(owner_nodes[index], node, infinity))
            )
            bits ^= bit
        network.add_edge(node, target, capacity)
        pool_records.append(
            {
                "mask": mask,
                "capacity": capacity,
                "keys": keys,
                "ownerArcs": owner_arcs,
            }
        )

    for mask, capacity in sorted(direct_counts.items()):
        keys = None
        if extract_assignment:
            keys = [
                (base // n, base % n, half)
                for base in sorted(direct_bases[mask])
                for half in (0, 1)
            ]
        add_pool(mask, capacity, keys, sink)

    for edge in active:
        group = network.node()
        network.add_edge(group, sink, 2)
        for mask, keys in sorted(edge_pools.get(edge, {}).items()):
            add_pool(mask, len(keys), sorted(keys) if extract_assignment else None, group)

    maximum = network.max_flow(source, sink)
    reachable = network.reachable(source)
    witness_indices = [
        index for index, node in enumerate(owner_nodes) if node in reachable
    ]
    witness_owners = [owners[index] for index in witness_indices]
    shore_mask = sum(1 << index for index in witness_indices)
    shore_demand = sum(demand[index] for index in witness_indices)
    direct_shore_capacity = sum(
        2
        for base, mask in base_masks.items()
        if base not in active_base and mask & shore_mask
    )
    active_shore_capacity = 0
    for x, y in active:
        eligible_keys = 2 * bool(base_masks.get(n * x + y, 0) & shore_mask)
        eligible_keys += 2 * bool(base_masks.get(n * y + x, 0) & shore_mask)
        active_shore_capacity += min(2, eligible_keys)
    shore_capacity = direct_shore_capacity + active_shore_capacity
    assigned: dict[int, list[SourceKey]] = {owner: [] for owner in owners}
    if extract_assignment:
        for pool in pool_records:
            keys = pool["keys"]
            assert keys is not None
            cursor = 0
            for owner_index, arc in pool["ownerArcs"]:
                amount = _used(arc)
                if amount:
                    assigned[owners[owner_index]].extend(keys[cursor : cursor + amount])
                    cursor += amount
            if cursor > pool["capacity"]:
                raise AssertionError("pool over capacity")
    total_demand = sum(demand)
    return (
        {
            "maximumFlow": maximum,
            "defect": total_demand - maximum,
            "totalDemand": total_demand,
            "networkNodes": len(network.graph),
            "directMaskPools": len(direct_counts),
            "activeEdgeGroups": len(active),
            "activeRelationPools": sum(len(items) for items in edge_pools.values()),
            "minCutSourceOwners": witness_owners,
            "minCutSourceOwnerDemand": shore_demand,
            "minCutShoreDirectCapacity": direct_shore_capacity,
            "minCutShoreActiveCapacity": active_shore_capacity,
            "minCutShoreCapacity": shore_capacity,
            "minCutShoreDefect": shore_demand - shore_capacity,
        },
        assigned,
    )


def _relation_stats(relation: dict[int, int], audit: dict) -> dict:
    return {
        "orderedFreeBases": len(relation),
        "freeHalfKeys": 2 * len(relation),
        "ownerBaseArcs": sum(mask.bit_count() for mask in relation.values()),
        "ownerHalfArcs": 2 * sum(mask.bit_count() for mask in relation.values()),
        "audit": audit,
    }


def _merge_relation(target: dict[int, int], source: dict[int, int]) -> None:
    for base, mask in source.items():
        target[base] = target.get(base, 0) | mask


def analyze_global(
    ctx: GraphContext,
    rows: Iterable[Iterable[int]],
    *,
    extract_certificate: bool = False,
    enumerate_after_zero: bool = False,
) -> tuple[dict, dict | None]:
    state = reconstruct_state(ctx, rows)
    owners, demand = global_demands(state)
    nonfree_active = [
        [x, y, state.pair[x][y], state.pair[y][x]]
        for x, y in sorted(state.active_edges)
        if state.pair[x][y] != 0 or state.pair[y][x] != 0
    ]
    incidence = sum(sum(row) for row in state.pair)
    if incidence != 25 * len(state.rows):
        raise AssertionError((incidence, 25 * len(state.rows)))
    free_ordered_distinct = sum(
        x != y and state.pair[x][y] == 0
        for x in range(ctx.n)
        for y in range(ctx.n)
    )
    free_mass = sum(
        state.pair[x][y] == 0
        for x in range(ctx.n)
        for y in range(ctx.n)
    )
    active_demand = sum(
        amount for owner, amount in zip(owners, demand) if owner in state.active_vertices
    )
    summary = {
        "schema": "R53_GLOBAL_FREEHALF_SOFTCAP_EVALUATION_V1",
        "model": {
            "demand": "all global CollisionHalf identities",
            "sink": "actual FreeHalf(sourceX,sourceY,half)",
            "keyCapacity": 1,
            "activeEdgeAggregateCapacity": 2,
            "cappedEdgeScope": "all activeEdges",
            "fixedReservations": False,
            "arithmetic": "Python integers; integral layered max flow",
            "relations": list(FAMILY_ORDER),
        },
        "state": {
            "order": ctx.n,
            "rows": len(state.rows),
            "selectedVertices": len(state.selected),
            "activeVertices": len(state.active_vertices),
            "activeEdges": len(state.active_edges),
            "activeEdgeFourFreeHalfBlocks": len(state.active_edges) - len(nonfree_active),
            "nonfreeActiveEdges": nonfree_active,
            "globalCollisionOwners": len(owners),
            "globalCollisionHalfDemand": sum(demand),
            "activeOnlyCollisionHalfDemand": active_demand,
            "inactiveCollisionHalfDemand": sum(demand) - active_demand,
            "demandByOwner": {
                str(owner): amount for owner, amount in zip(owners, demand)
            },
            "actualFreeHalfCount": 2 * free_ordered_distinct,
            "freeMassIncludingDiagonal": free_mass,
            "incidence": incidence,
            "residual": ctx.n * ctx.n - 25 * len(state.rows),
        },
        "relationProvenance": RELATION_PROVENANCE,
        "familyStats": {},
        "stages": [],
        "evaluatedFamilies": [],
        "notEnumeratedFamilies": [],
    }
    if nonfree_active:
        summary["verdict"] = "INVALID_ACTIVE_EDGE_NOT_FOUR_FREEHALVES"
        summary["minimumDefect"] = None
        return summary, None

    union: dict[int, int] = {}
    family_relations: dict[str, dict[int, int]] = {}
    last_flow = {
        "maximumFlow": 0,
        "defect": sum(demand),
        "totalDemand": sum(demand),
        "minCutSourceOwners": list(owners),
    }
    assigned: dict[int, list[SourceKey]] = {owner: [] for owner in owners}
    if not owners:
        summary["minimumDefect"] = 0
        summary["verdict"] = "PASS_ZERO_GLOBAL_DEMAND"
        summary["notEnumeratedFamilies"] = list(FAMILY_ORDER)
        return summary, {
            "schema": "R53_GLOBAL_FREEHALF_ASSIGNMENT_V1",
            "assignments": [],
            "checks": {
                "allGlobalDemandAssigned": True,
                "actualFreeHalfSinks": True,
                "unitKeyCapacity": True,
                "activeEdgeCapacityTwo": True,
                "eligible": True,
            },
        } if extract_certificate else None

    zero_reached = False
    for family in EVALUATION_ORDER:
        if zero_reached and not enumerate_after_zero:
            continue
        relation, audit = FAMILY_BUILDERS[family](ctx, state, owners)
        family_relations[family] = relation
        summary["familyStats"][family] = _relation_stats(relation, audit)
        _merge_relation(union, relation)
        summary["evaluatedFamilies"].append(family)
        last_flow, assigned = solve_grouped_flow(
            ctx.n,
            owners,
            demand,
            union,
            state.active_edges,
            extract_assignment=extract_certificate,
        )
        summary["stages"].append(
            {
                "afterAdding": family,
                "unionOrderedFreeBases": len(union),
                "unionFreeHalfKeys": 2 * len(union),
                **last_flow,
            }
        )
        zero_reached = last_flow["defect"] == 0

    summary["notEnumeratedFamilies"] = [
        family for family in FAMILY_ORDER if family not in summary["evaluatedFamilies"]
    ]
    summary["minimumDefect"] = last_flow["defect"]
    summary["maximumFlow"] = last_flow["maximumFlow"]
    summary["minCutSourceOwners"] = last_flow["minCutSourceOwners"]
    summary["fullUnionExactReason"] = (
        "zero on an evaluated subrelation; adding remaining families cannot lower zero"
        if zero_reached and summary["notEnumeratedFamilies"]
        else "all six families explicitly enumerated"
        if not summary["notEnumeratedFamilies"]
        else "not applicable"
    )
    summary["verdict"] = "PASS" if last_flow["defect"] == 0 else "FAIL"

    certificate = None
    if extract_certificate:
        source_keys = [key for keys in assigned.values() for key in keys]
        source_counts = Counter(source_keys)
        active_load: Counter[Edge] = Counter()
        records = []
        all_eligible = True
        for owner in owners:
            obligations = list(collision_obligations(state, owner))
            sources = sorted(assigned[owner])
            for obligation, key in zip(obligations, sources):
                x, y, half = key
                bit = 1 << owners.index(owner)
                base = ctx.n * x + y
                families = [
                    family
                    for family, relation in family_relations.items()
                    if relation.get(base, 0) & bit
                ]
                all_eligible &= bool(families)
                edge = norm_edge(x, y)
                if edge in state.active_edges:
                    active_load[edge] += 1
                records.append(
                    {
                        "obligation": list(obligation),
                        "source": [x, y, half],
                        "families": families,
                    }
                )
        checks = {
            "allGlobalDemandAssigned": len(records) == sum(demand),
            "actualFreeHalfSinks": all(
                x != y and state.pair[x][y] == 0 for x, y, _half in source_keys
            ),
            "unitKeyCapacity": all(value <= 1 for value in source_counts.values()),
            "activeEdgeCapacityTwo": all(value <= 2 for value in active_load.values()),
            "eligible": all_eligible,
        }
        certificate = {
            "schema": "R53_GLOBAL_FREEHALF_ASSIGNMENT_V1",
            "model": summary["model"],
            "checks": checks,
            "activeEdgeLoads": {
                f"{x},{y}": active_load[(x, y)] for x, y in sorted(active_load)
            },
            "assignments": records,
        }
    return summary, certificate


def self_check() -> dict:
    owners = (0,)
    demand = (3,)
    masks = {1: 1, 2: 1}  # (0,1) and (1,0), two halves each.
    grouped, _ = solve_grouped_flow(2, owners, demand, masks, [(0, 1)])
    direct, _ = solve_grouped_flow(2, owners, demand, masks, [])
    inactive, _ = solve_grouped_flow(2, (0, 1), (0, 1), {}, [])
    checks = {
        "aggregateCapBinds": grouped["maximumFlow"] == 2
        and grouped["defect"] == 1,
        "unitKeysWithoutGroupCarryThree": direct["maximumFlow"] == 3,
        "activeOnlyZeroWouldMissGlobalDemand": inactive["defect"] == 1,
        "rawKeyGuardrailArithmetic": (
            4 * 4 - 25 == -9 and 2 * 9 <= 4 * 3 * 2
        ),
    }
    if not all(checks.values()):
        raise AssertionError(checks)
    return checks


__all__ = [
    "FAMILY_ORDER",
    "RELATION_PROVENANCE",
    "analyze_global",
    "make_graph_context",
    "norm_edge",
    "self_check",
    "solve_grouped_flow",
]
