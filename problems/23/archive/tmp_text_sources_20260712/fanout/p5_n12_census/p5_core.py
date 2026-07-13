"""Exact Pattern-5 state reconstruction and finite owner-Hall checks.

This module intentionally derives every tuple-dependent object from
``(n, B, M, rows)``.  It does not consume cached active scopes, component
labels, pair counts, reservations, or switch-loss annotations.

All arithmetic is integral.  Source keys are ordered free halves
``(sourceX, sourceY, half)`` with ``sourceX != sourceY``.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from typing import Iterable


Edge = tuple[int, int]
Row = tuple[int, ...]
Source = tuple[int, int, int]


def edge(x: int, y: int) -> Edge:
    return (x, y) if x < y else (y, x)


def vertices(mask: int) -> list[int]:
    out: list[int] = []
    while mask:
        bit = mask & -mask
        out.append(bit.bit_length() - 1)
        mask ^= bit
    return out


def source_id(n: int, x: int, y: int, half: int) -> int:
    return 2 * (n * x + y) + half


def decode_source(n: int, value: int) -> Source:
    half = value & 1
    pair_id = value >> 1
    return pair_id // n, pair_id % n, half


@dataclass
class GraphContext:
    n: int
    blue: frozenset[Edge]
    bad: frozenset[Edge]
    blue_adj: tuple[frozenset[int], ...]
    sigma_pair: tuple[tuple[int, ...], ...]
    sigma_cache: dict[int, int]


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
    demanded_active_edges: set[Edge]
    active_degree: list[int]
    collision: dict[int, int]
    hit_need: dict[int, int]
    owners: tuple[int, ...]


def make_graph_context(n: int, blue: Iterable[Edge], bad: Iterable[Edge]) -> GraphContext:
    blue_set = frozenset(edge(*e) for e in blue)
    bad_set = frozenset(edge(*e) for e in bad)
    adj = [set() for _ in range(n)]
    for x, y in blue_set:
        adj[x].add(y)
        adj[y].add(x)

    signed_degree = [0] * n
    signs: dict[Edge, int] = {}
    for x, y in blue_set:
        signs[(x, y)] = 1
        signed_degree[x] += 1
        signed_degree[y] += 1
    for x, y in bad_set:
        signs[(x, y)] = -1
        signed_degree[x] -= 1
        signed_degree[y] -= 1
    sigma_pair = tuple(
        tuple(
            0 if x == y else (
                signed_degree[x] + signed_degree[y] - 2 * signs.get(edge(x, y), 0)
            )
            for y in range(n)
        )
        for x in range(n)
    )
    return GraphContext(
        n=n,
        blue=blue_set,
        bad=bad_set,
        blue_adj=tuple(frozenset(neighbors) for neighbors in adj),
        sigma_pair=sigma_pair,
        sigma_cache={0: 0},
    )


def sigma_value(ctx: GraphContext, mask: int) -> int:
    cached = ctx.sigma_cache.get(mask)
    if cached is not None:
        return cached
    blue_cut = sum(((mask >> x) ^ (mask >> y)) & 1 for x, y in ctx.blue)
    bad_cut = sum(((mask >> x) ^ (mask >> y)) & 1 for x, y in ctx.bad)
    value = blue_cut - bad_cut
    ctx.sigma_cache[mask] = value
    return value


def _components(
    n: int, edges: Iterable[Edge], allowed: set[int]
) -> tuple[list[int], list[int]]:
    adj = [[] for _ in range(n)]
    for x, y in edges:
        if x in allowed and y in allowed:
            adj[x].append(y)
            adj[y].append(x)
    comp_id = [-1] * n
    masks: list[int] = []
    for root in sorted(allowed):
        if comp_id[root] >= 0:
            continue
        cid = len(masks)
        comp_id[root] = cid
        mask = 0
        queue = deque([root])
        while queue:
            x = queue.popleft()
            mask |= 1 << x
            for y in adj[x]:
                if comp_id[y] < 0:
                    comp_id[y] = cid
                    queue.append(y)
        masks.append(mask)
    return comp_id, masks


def reconstruct_state(ctx: GraphContext, rows: Iterable[Iterable[int]]) -> TupleState:
    n = ctx.n
    normalized_rows = tuple(tuple(row) for row in rows)
    pair = [[0] * n for _ in range(n)]
    row_count = [0] * n
    selected: set[int] = set()
    support: set[Edge] = set()
    for row in normalized_rows:
        for x in row:
            if not 0 <= x < n:
                raise AssertionError(f"row vertex {x} outside 0..{n - 1}")
            row_count[x] += 1
            selected.add(x)
            for y in row:
                pair[x][y] += 1
        for x, y in zip(row, row[1:]):
            e = edge(x, y)
            if e not in ctx.blue:
                raise AssertionError(f"row step {e} is not blue")
            support.add(e)

    active_edges = {
        e for e in ctx.blue
        if e not in support and e[0] in selected and e[1] in selected
    }
    selected_comp, _ = _components(n, active_edges, selected)
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
    demanded_active_edges = {
        e for e in active_edges if selected_comp[e[0]] in active_comp_ids
    }
    active_degree = [0] * n
    for x, y in demanded_active_edges:
        active_degree[x] += 1
        active_degree[y] += 1

    collision: dict[int, int] = {}
    hit_need: dict[int, int] = {}
    for owner in sorted(active_vertices):
        collision[owner] = 2 * sum(max(0, pair[owner][y] - 1) for y in range(n))
        vertex_slack = max(0, n - 5 * row_count[owner])
        hit_need[owner] = max(0, active_degree[owner] - vertex_slack)
    owners = tuple(
        owner for owner in sorted(active_vertices)
        if collision[owner] > 0 or hit_need[owner] > 0
    )
    return TupleState(
        rows=normalized_rows,
        pair=pair,
        row_count=row_count,
        selected=selected,
        support=support,
        active_edges=active_edges,
        selected_comp=selected_comp,
        active_comp_ids=active_comp_ids,
        active_vertices=active_vertices,
        demanded_active_edges=demanded_active_edges,
        active_degree=active_degree,
        collision=collision,
        hit_need=hit_need,
        owners=owners,
    )


def _reserved(state: TupleState, x: int, y: int, half: int) -> bool:
    return (
        half == 0
        and edge(x, y) in state.demanded_active_edges
        and x in state.active_vertices
    )


def _merge_masks(*relations: dict[int, int]) -> dict[int, int]:
    out: dict[int, int] = {}
    for relation in relations:
        for source, mask in relation.items():
            out[source] = out.get(source, 0) | mask
    return out


def _base_relations(
    ctx: GraphContext, state: TupleState
) -> tuple[dict[int, int], dict[int, int]]:
    """Return P1/P3 and corrected-common-blue P2 owner masks."""
    n = ctx.n
    p13: dict[int, int] = {}
    p2: dict[int, int] = {}
    owner_index = {owner: index for index, owner in enumerate(state.owners)}
    for x in range(n):
        for y in range(n):
            if x == y or state.pair[x][y] != 0:
                continue
            sigma_pair = ctx.sigma_pair[x][y]
            mask13 = 0
            mask2 = 0
            for owner, index in owner_index.items():
                owner_bit = 1 << index
                if x == owner:
                    mask13 |= owner_bit
                if (
                    state.pair[owner][x] > 0
                    and state.pair[owner][y] > 0
                    and sigma_pair >= 0
                ):
                    mask13 |= owner_bit
                if (
                    x in ctx.blue_adj[owner]
                    and y in ctx.blue_adj[owner]
                    and sigma_pair >= 2
                ):
                    mask2 |= owner_bit
            for half in (0, 1):
                if _reserved(state, x, y, half):
                    continue
                sid = source_id(n, x, y, half)
                if mask13:
                    p13[sid] = mask13
                if mask2:
                    p2[sid] = mask2
    return p13, p2


def _boundary_masks(
    ctx: GraphContext, component_masks: list[int], boundary_vertices: set[int]
) -> list[int]:
    boundaries: list[int] = []
    for component in component_masks:
        boundary = 0
        for x in vertices(component):
            for y in ctx.blue_adj[x]:
                if y in boundary_vertices:
                    boundary |= 1 << y
        boundaries.append(boundary)
    return boundaries


def _attachment_relation(
    ctx: GraphContext,
    state: TupleState,
    *,
    allowed: set[int],
    boundary_vertices: set[int],
) -> tuple[dict[int, int], dict[str, int]]:
    """Compute strict component-attachment masks for P4 or P5.

    An owner is eligible for a component exactly when one boundary attachment
    co-occurs with the owner and lies in the same selected off-support
    component as the owner.  A source pair uses the union of its two induced
    blue components as the switch set.
    """
    n = ctx.n
    comp_id, component_masks = _components(n, ctx.blue, allowed)
    boundary_masks = _boundary_masks(ctx, component_masks, boundary_vertices)
    eligible_masks: list[int] = []
    for boundary in boundary_masks:
        owner_mask = 0
        boundary_list = vertices(boundary)
        for index, owner in enumerate(state.owners):
            if any(
                state.pair[owner][a] > 0
                and state.selected_comp[a] == state.selected_comp[owner]
                for a in boundary_list
            ):
                owner_mask |= 1 << index
        eligible_masks.append(owner_mask)

    relation: dict[int, int] = {}
    checked_switches = 0
    negative_switches = 0
    reserved_candidates = 0
    for x in sorted(allowed):
        for y in sorted(allowed):
            if x == y or state.pair[x][y] != 0:
                continue
            owner_mask = eligible_masks[comp_id[x]] & eligible_masks[comp_id[y]]
            if not owner_mask:
                continue
            switch_mask = component_masks[comp_id[x]] | component_masks[comp_id[y]]
            checked_switches += 1
            if sigma_value(ctx, switch_mask) < 0:
                negative_switches += 1
                continue
            for half in (0, 1):
                if _reserved(state, x, y, half):
                    reserved_candidates += 1
                    continue
                relation[source_id(n, x, y, half)] = owner_mask
    return relation, {
        "components": len(component_masks),
        "nonemptyBoundaries": sum(mask != 0 for mask in boundary_masks),
        "checkedSwitches": checked_switches,
        "negativeSwitches": negative_switches,
        "reservedCandidates": reserved_candidates,
    }


def relation_masks(ctx: GraphContext, state: TupleState) -> dict:
    """Build P1--P5 masks and exact source-extension statistics."""
    p13, p2 = _base_relations(ctx, state)
    p4, p4_audit = _attachment_relation(
        ctx,
        state,
        allowed=set(range(ctx.n)) - state.selected,
        boundary_vertices=state.selected,
    )
    p5, p5_audit = _attachment_relation(
        ctx,
        state,
        allowed=set(range(ctx.n)) - state.active_vertices,
        boundary_vertices=state.active_vertices,
    )
    if p5_audit["negativeSwitches"] != 0:
        raise AssertionError("P5 produced a negative-loss switch on a maximum cut")
    if p5_audit["reservedCandidates"] != 0:
        raise AssertionError("P5 quiescent endpoints reached a scoped reservation")

    before_p5 = _merge_masks(p13, p2, p4)
    five = _merge_masks(before_p5, p5)
    claude_before = p13
    claude_after = _merge_masks(p13, p5)
    new_global_keys = sum(source not in before_p5 for source in p5)
    extended_keys = sum(
        bool(mask & ~before_p5.get(source, 0)) for source, mask in p5.items()
    )
    new_owner_arcs = sum(
        (mask & ~before_p5.get(source, 0)).bit_count()
        for source, mask in p5.items()
    )
    return {
        "p13": p13,
        "p2": p2,
        "p4": p4,
        "p5": p5,
        "beforeP5": before_p5,
        "five": five,
        "claudeBefore": claude_before,
        "claudeAfter": claude_after,
        "p4Audit": p4_audit,
        "p5Audit": p5_audit,
        "p5Stats": {
            "keys": len(p5),
            "ownerArcs": sum(mask.bit_count() for mask in p5.values()),
            "newGlobalKeysVsP1P4": new_global_keys,
            "extendedKeysVsP1P4": extended_keys,
            "newOwnerArcsVsP1P4": new_owner_arcs,
        },
    }


def hall_check(
    state: TupleState, relation: dict[int, int], *, hit_scale: int
) -> dict:
    if hit_scale <= 0:
        raise ValueError("hit_scale must be positive")
    demand = [
        state.collision[owner] + hit_scale * state.hit_need[owner]
        for owner in state.owners
    ]
    if not demand:
        return {
            "full": True,
            "totalDemand": 0,
            "sourceKeys": 0,
            "minimumMargin": 0,
            "maximumDefect": 0,
            "tightShoreCount": 0,
            "worstShoreMask": 0,
            "worstOwners": [],
            "worstDemand": 0,
            "worstReach": 0,
        }

    owner_count = len(state.owners)
    full_mask = (1 << owner_count) - 1
    source_hist = [0] * (1 << owner_count)
    for mask in relation.values():
        source_hist[mask] += 1
    subset_source = source_hist[:]
    for index in range(owner_count):
        bit = 1 << index
        for mask in range(1 << owner_count):
            if mask & bit:
                subset_source[mask] += subset_source[mask ^ bit]
    demand_sum = [0] * (1 << owner_count)
    for mask in range(1, 1 << owner_count):
        bit = mask & -mask
        index = bit.bit_length() - 1
        demand_sum[mask] = demand_sum[mask ^ bit] + demand[index]

    minimum_margin: int | None = None
    worst_mask = 0
    worst_demand = 0
    worst_reach = 0
    tight_shores = 0
    for shore_mask in range(1, 1 << owner_count):
        shore_demand = demand_sum[shore_mask]
        shore_reach = len(relation) - subset_source[full_mask ^ shore_mask]
        margin = shore_reach - shore_demand
        if minimum_margin is None or margin < minimum_margin:
            minimum_margin = margin
            worst_mask = shore_mask
            worst_demand = shore_demand
            worst_reach = shore_reach
            tight_shores = int(margin == 0)
        elif margin == minimum_margin:
            tight_shores += int(margin == 0)
    assert minimum_margin is not None
    return {
        "full": minimum_margin >= 0,
        "totalDemand": sum(demand),
        "sourceKeys": len(relation),
        "minimumMargin": minimum_margin,
        "maximumDefect": max(0, -minimum_margin),
        "tightShoreCount": tight_shores,
        "worstShoreMask": worst_mask,
        "worstOwners": [
            owner for index, owner in enumerate(state.owners)
            if worst_mask & (1 << index)
        ],
        "worstDemand": worst_demand,
        "worstReach": worst_reach,
    }


def analyze_rows(
    ctx: GraphContext, rows: Iterable[Iterable[int]], *, details: bool = False
) -> dict:
    state = reconstruct_state(ctx, rows)
    one_total = sum(
        state.collision[owner] + state.hit_need[owner] for owner in state.owners
    )
    micro_total = sum(
        state.collision[owner] + 25 * state.hit_need[owner] for owner in state.owners
    )
    result = {
        "oneDemand": one_total,
        "microDemand": micro_total,
        "collisionDemand": sum(state.collision.get(owner, 0) for owner in state.owners),
        "hitNeedSlots": sum(state.hit_need.get(owner, 0) for owner in state.owners),
        "owners": list(state.owners),
        "activeVertices": len(state.active_vertices),
        "activeEdges": len(state.active_edges),
        "demandedActiveEdges": len(state.demanded_active_edges),
    }
    if not state.owners:
        empty = hall_check(state, {}, hit_scale=1)
        result.update({
            "p5Stats": {
                "keys": 0,
                "ownerArcs": 0,
                "newGlobalKeysVsP1P4": 0,
                "extendedKeysVsP1P4": 0,
                "newOwnerArcsVsP1P4": 0,
            },
            "p4Audit": {
                "components": 0,
                "nonemptyBoundaries": 0,
                "checkedSwitches": 0,
                "negativeSwitches": 0,
                "reservedCandidates": 0,
            },
            "p5Audit": {
                "components": 0,
                "nonemptyBoundaries": 0,
                "checkedSwitches": 0,
                "negativeSwitches": 0,
                "reservedCandidates": 0,
            },
            "oneClaudeBefore": empty,
            "oneClaudeAfter": empty,
            "oneBeforeP5": empty,
            "oneFive": empty,
            "microBeforeP5": empty,
            "microFive": empty,
        })
        if details:
            result["state"] = state_details(ctx, state)
        return result

    masks = relation_masks(ctx, state)
    result.update({
        "p5Stats": masks["p5Stats"],
        "p4Audit": masks["p4Audit"],
        "p5Audit": masks["p5Audit"],
        "oneClaudeBefore": hall_check(state, masks["claudeBefore"], hit_scale=1),
        "oneClaudeAfter": hall_check(state, masks["claudeAfter"], hit_scale=1),
        "oneBeforeP5": hall_check(state, masks["beforeP5"], hit_scale=1),
        "oneFive": hall_check(state, masks["five"], hit_scale=1),
        "microBeforeP5": hall_check(state, masks["beforeP5"], hit_scale=25),
        "microFive": hall_check(state, masks["five"], hit_scale=25),
    })
    if details:
        result["state"] = state_details(ctx, state)
        result["sourceCounts"] = {
            "p13": len(masks["p13"]),
            "p2": len(masks["p2"]),
            "p4": len(masks["p4"]),
            "p5": len(masks["p5"]),
            "beforeP5": len(masks["beforeP5"]),
            "five": len(masks["five"]),
        }
        result["p5Sources"] = [
            {
                "source": list(decode_source(ctx.n, source)),
                "ownerMask": mask,
                "owners": [
                    owner for index, owner in enumerate(state.owners)
                    if mask & (1 << index)
                ],
            }
            for source, mask in sorted(masks["p5"].items())
        ]
    return result


def state_details(ctx: GraphContext, state: TupleState) -> dict:
    selected_components: dict[int, list[int]] = {}
    for x in sorted(state.selected):
        selected_components.setdefault(state.selected_comp[x], []).append(x)
    return {
        "rows": [list(row) for row in state.rows],
        "selected": sorted(state.selected),
        "support": [list(e) for e in sorted(state.support)],
        "activeEdges": [list(e) for e in sorted(state.active_edges)],
        "activeVertices": sorted(state.active_vertices),
        "demandedActiveEdges": [list(e) for e in sorted(state.demanded_active_edges)],
        "selectedComponents": [
            component for _, component in sorted(selected_components.items())
        ],
        "activeComponents": [
            component for cid, component in sorted(selected_components.items())
            if cid in state.active_comp_ids
        ],
        "pair": state.pair,
        "rowCount": state.row_count,
        "collisionByOwner": {str(k): v for k, v in sorted(state.collision.items())},
        "hitNeedByOwner": {str(k): v for k, v in sorted(state.hit_need.items())},
        "blue": [list(e) for e in sorted(ctx.blue)],
        "bad": [list(e) for e in sorted(ctx.bad)],
    }


def mask_histogram(relation: dict[int, int]) -> dict[str, int]:
    return {
        str(mask): count for mask, count in sorted(Counter(relation.values()).items())
    }
