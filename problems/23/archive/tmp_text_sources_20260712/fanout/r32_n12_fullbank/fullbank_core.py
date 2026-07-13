"""Exact R32 collision/full-bank gate core.

The graph, cut, row, P1/P3, and P5 predicates are reconstructed by the pinned
``p5_n12_census`` implementation.  This module changes the accounting:

* collision halves use only P1/P3/P5 FreeHalf keys;
* common-blue is an optional terminal bundle whose two owner edges are
  reserved exclusively, with every FreeHalf on a reserved edge deducted;
* both half bits of one ordered pair may be used only in one active component;
* residual HitNeed incidences use distinct demanded-active-edge Doors of raw
  capacity 25.  Vertex slack pays first; no capacity is inferred for prune.

All arithmetic and optimization are integer/set operations.  The constrained
search is exhaustive: ordinary max flow supplies a Hall shore; any successful
common-blue extension must add a new neighbor to that shore.  Base-component
conflicts branch over every component in which that ordered base can occur.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P5_DIR = HERE.parent / "p5_n12_census"
sys.path.insert(0, str(P5_DIR))

import p5_core as p5  # noqa: E402


Edge = tuple[int, int]


def canonical_sha(value) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def decode_source(n: int, source: int) -> tuple[int, int, int]:
    half = source & 1
    pair_id = source >> 1
    return pair_id // n, pair_id % n, half


def source_base(source: int) -> int:
    return source >> 1


def source_edge(n: int, source: int) -> Edge:
    x, y, _ = decode_source(n, source)
    return p5.edge(x, y)


class Dinic:
    """Small deterministic integral max-flow implementation."""

    def __init__(self, size: int):
        self.graph: list[list[list[int]]] = [[] for _ in range(size)]

    def add_edge(self, u: int, v: int, cap: int) -> int:
        if cap < 0:
            raise ValueError("negative capacity")
        forward = [v, cap, len(self.graph[v]), cap]
        reverse = [u, 0, len(self.graph[u]), 0]
        self.graph[u].append(forward)
        self.graph[v].append(reverse)
        return len(self.graph[u]) - 1

    def max_flow(self, source: int, sink: int) -> int:
        total = 0
        size = len(self.graph)
        while True:
            level = [-1] * size
            level[source] = 0
            queue = deque([source])
            while queue:
                u = queue.popleft()
                for v, cap, _rev, _original in self.graph[u]:
                    if cap and level[v] < 0:
                        level[v] = level[u] + 1
                        queue.append(v)
            if level[sink] < 0:
                break
            cursor = [0] * size

            def send(u: int, amount: int) -> int:
                if u == sink:
                    return amount
                while cursor[u] < len(self.graph[u]):
                    index = cursor[u]
                    edge = self.graph[u][index]
                    v, cap, rev, _original = edge
                    if cap and level[v] == level[u] + 1:
                        pushed = send(v, min(amount, cap))
                        if pushed:
                            edge[1] -= pushed
                            self.graph[v][rev][1] += pushed
                            return pushed
                    cursor[u] += 1
                return 0

            while True:
                pushed = send(source, 1 << 60)
                if not pushed:
                    break
                total += pushed
        return total

    def reachable(self, source: int) -> set[int]:
        seen = {source}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v, cap, _rev, _original in self.graph[u]:
                if cap and v not in seen:
                    seen.add(v)
                    queue.append(v)
        return seen


@dataclass(frozen=True)
class FlowResult:
    value: int
    assignment: tuple[tuple[int, int], ...]
    reachable_owner_mask: int
    witness_demand: int
    witness_reach: int


def owner_source_flow(
    demand: tuple[int, ...], relation: dict[int, int]
) -> FlowResult:
    """Maximum b-matching; relation values are owner bitmasks."""

    owner_count = len(demand)
    sources = tuple(sorted(source for source, mask in relation.items() if mask))
    source_pos = {source: index for index, source in enumerate(sources)}
    source_node = 1 + owner_count
    sink = source_node + len(sources)
    network = Dinic(sink + 1)
    for index, amount in enumerate(demand):
        network.add_edge(0, 1 + index, amount)
    arc_refs: list[tuple[int, int, int, int]] = []
    for owner_index in range(owner_count):
        owner_bit = 1 << owner_index
        owner_node = 1 + owner_index
        for source in sources:
            if relation[source] & owner_bit:
                arc_index = network.add_edge(
                    owner_node, source_node + source_pos[source], 1
                )
                arc_refs.append((owner_index, source, owner_node, arc_index))
    for index in range(len(sources)):
        network.add_edge(source_node + index, sink, 1)
    value = network.max_flow(0, sink)
    assignment = tuple(
        sorted(
            (source, owner_index)
            for owner_index, source, owner_node, arc_index in arc_refs
            if network.graph[owner_node][arc_index][1] == 0
        )
    )
    reachable = network.reachable(0)
    shore_mask = sum(
        1 << index
        for index in range(owner_count)
        if 1 + index in reachable
    )
    if value == sum(demand):
        shore_mask = 0
        witness_demand = 0
        witness_reach = 0
    else:
        witness_demand = sum(
            amount
            for index, amount in enumerate(demand)
            if shore_mask & (1 << index)
        )
        witness_reach = sum(
            bool(mask & shore_mask) for mask in relation.values()
        )
        if witness_demand <= witness_reach:
            raise AssertionError("residual shore is not Hall-deficient")
    return FlowResult(
        value=value,
        assignment=assignment,
        reachable_owner_mask=shore_mask,
        witness_demand=witness_demand,
        witness_reach=witness_reach,
    )


@dataclass(frozen=True)
class CommonTerminal:
    index: int
    owner_index: int
    owner: int
    source_x: int
    source_y: int
    sources: tuple[int, ...]
    reserve_edges: tuple[Edge, Edge]
    reserve_mask: int


@dataclass(frozen=True)
class CollisionResult:
    exact: bool
    demand: int
    matched: int
    defect: int
    assignment: tuple[tuple[int, int], ...]
    selected_terminals: tuple[int, ...]
    base_labels: tuple[tuple[int, int], ...]
    search_nodes: int
    raw_source_count: int
    final_source_count: int
    deducted_raw_keys: tuple[int, ...]
    witness_owner_mask: int
    witness_demand: int
    witness_reach: int


def _merge_relations(*relations: dict[int, int]) -> dict[int, int]:
    merged: dict[int, int] = {}
    for relation in relations:
        for source, mask in relation.items():
            merged[source] = merged.get(source, 0) | mask
    return merged


def collision_owners(state: p5.TupleState) -> tuple[int, ...]:
    return tuple(
        owner for owner in sorted(state.active_vertices)
        if state.collision.get(owner, 0) > 0
    )


def project_masks(
    state: p5.TupleState,
    relation: dict[int, int],
    owners: tuple[int, ...],
) -> dict[int, int]:
    old_index = {owner: index for index, owner in enumerate(state.owners)}
    out: dict[int, int] = {}
    for source, old_mask in relation.items():
        mask = 0
        for index, owner in enumerate(owners):
            prior = old_index.get(owner)
            if prior is not None and old_mask & (1 << prior):
                mask |= 1 << index
        if mask:
            out[source] = mask
    return out


def raw_relation(
    ctx: p5.GraphContext,
    state: p5.TupleState,
    owners: tuple[int, ...],
) -> tuple[dict[int, int], dict]:
    masks = p5.relation_masks(ctx, state)
    relation = project_masks(
        state, _merge_relations(masks["p13"], masks["p5"]), owners
    )
    return relation, masks


def _scoped_reserved(
    state: p5.TupleState, x: int, y: int, half: int
) -> bool:
    return (
        half == 0
        and p5.edge(x, y) in state.demanded_active_edges
        and x in state.active_vertices
    )


def common_terminals(
    ctx: p5.GraphContext,
    state: p5.TupleState,
    owners: tuple[int, ...],
    raw: dict[int, int],
) -> tuple[CommonTerminal, ...]:
    edge_ids = {edge: index for index, edge in enumerate(sorted(ctx.blue))}
    records: list[tuple[int, int, int, tuple[int, ...], tuple[Edge, Edge], int]] = []
    for owner_index, owner in enumerate(owners):
        owner_bit = 1 << owner_index
        neighbors = sorted(ctx.blue_adj[owner])
        for left in range(len(neighbors)):
            x = neighbors[left]
            for y in neighbors[left + 1 :]:
                if state.pair[x][y] != 0 or ctx.sigma_pair[x][y] < 2:
                    continue
                reserved = (p5.edge(x, owner), p5.edge(y, owner))
                if reserved[0] == reserved[1]:
                    raise AssertionError("common terminal has repeated reserve edge")
                reserve_mask = (1 << edge_ids[reserved[0]]) | (
                    1 << edge_ids[reserved[1]]
                )
                for source_x, source_y in ((x, y), (y, x)):
                    sources = tuple(
                        p5.source_id(ctx.n, source_x, source_y, half)
                        for half in (0, 1)
                        if not _scoped_reserved(
                            state, source_x, source_y, half
                        )
                    )
                    # A terminal with no genuinely new owner arc can only
                    # reserve/deduct capacity, so it is never needed.
                    if not any(not (raw.get(source, 0) & owner_bit) for source in sources):
                        continue
                    records.append(
                        (
                            owner_index,
                            source_x,
                            source_y,
                            sources,
                            reserved,
                            reserve_mask,
                        )
                    )
    records.sort()
    return tuple(
        CommonTerminal(
            index=index,
            owner_index=record[0],
            owner=owners[record[0]],
            source_x=record[1],
            source_y=record[2],
            sources=record[3],
            reserve_edges=record[4],
            reserve_mask=record[5],
        )
        for index, record in enumerate(records)
    )


def _selected_ids(bits: int) -> Iterable[int]:
    while bits:
        bit = bits & -bits
        yield bit.bit_length() - 1
        bits ^= bit


def coherent_collision_match(
    ctx: p5.GraphContext,
    state: p5.TupleState,
    owners: tuple[int, ...],
    raw: dict[int, int],
    terminals: tuple[CommonTerminal, ...],
) -> CollisionResult:
    demand_by_owner = tuple(state.collision[owner] for owner in owners)
    total_demand = sum(demand_by_owner)
    if total_demand == 0:
        return CollisionResult(
            exact=True,
            demand=0,
            matched=0,
            defect=0,
            assignment=(),
            selected_terminals=(),
            base_labels=(),
            search_nodes=1,
            raw_source_count=len(raw),
            final_source_count=len(raw),
            deducted_raw_keys=(),
            witness_owner_mask=0,
            witness_demand=0,
            witness_reach=0,
        )

    owner_components = tuple(state.selected_comp[owner] for owner in owners)
    base_possible: dict[int, set[int]] = {}
    for source, mask in raw.items():
        base = source_base(source)
        for index, component in enumerate(owner_components):
            if mask & (1 << index):
                base_possible.setdefault(base, set()).add(component)
    for terminal in terminals:
        component = owner_components[terminal.owner_index]
        for source in terminal.sources:
            base_possible.setdefault(source_base(source), set()).add(component)

    memo: dict[tuple[int, tuple[tuple[int, int], ...]], int] = {}
    nodes = 0
    best: tuple[FlowResult, int, tuple[tuple[int, int], ...], dict[int, int], int] | None = None
    found_full = False

    def relation_for(
        selected: int, labels: tuple[tuple[int, int], ...]
    ) -> tuple[dict[int, int], int, tuple[int, ...]]:
        label_map = dict(labels)
        reserve_mask = 0
        for terminal_index in _selected_ids(selected):
            reserve_mask |= terminals[terminal_index].reserve_mask
        reserved_edges = {
            edge
            for index, edge in enumerate(sorted(ctx.blue))
            if reserve_mask & (1 << index)
        }
        deducted = tuple(
            sorted(
                source for source in raw
                if source_edge(ctx.n, source) in reserved_edges
            )
        )
        relation = {
            source: mask for source, mask in raw.items()
            if source_edge(ctx.n, source) not in reserved_edges
        }
        for terminal_index in _selected_ids(selected):
            terminal = terminals[terminal_index]
            owner_bit = 1 << terminal.owner_index
            for source in terminal.sources:
                if source_edge(ctx.n, source) not in reserved_edges:
                    relation[source] = relation.get(source, 0) | owner_bit
        for source in tuple(relation):
            label = label_map.get(source_base(source))
            if label is None:
                continue
            mask = relation[source]
            filtered = sum(
                1 << index
                for index, component in enumerate(owner_components)
                if component == label and mask & (1 << index)
            )
            if filtered:
                relation[source] = filtered
            else:
                del relation[source]
        return relation, reserve_mask, deducted

    def first_coherence_conflict(
        assignment: tuple[tuple[int, int], ...]
    ) -> int | None:
        seen: dict[int, int] = {}
        for source, owner_index in assignment:
            base = source_base(source)
            component = owner_components[owner_index]
            previous = seen.setdefault(base, component)
            if previous != component:
                return base
        return None

    def visit(selected: int, labels: tuple[tuple[int, int], ...]) -> None:
        nonlocal nodes, best, found_full
        if found_full:
            return
        key = (selected, labels)
        if key in memo:
            return
        nodes += 1
        relation, used_reserve_mask, deducted = relation_for(selected, labels)
        flow = owner_source_flow(demand_by_owner, relation)
        memo[key] = flow.value
        conflict = first_coherence_conflict(flow.assignment)
        if conflict is not None:
            current = dict(labels)
            if conflict in current:
                raise AssertionError("labeled base produced a component conflict")
            for component in sorted(base_possible[conflict]):
                updated = tuple(sorted((*labels, (conflict, component))))
                visit(selected, updated)
            return
        if best is None or flow.value > best[0].value:
            best = (flow, selected, labels, relation, len(deducted))
        if flow.value == total_demand:
            best = (flow, selected, labels, relation, len(deducted))
            found_full = True
            return

        shore = flow.reachable_owner_mask
        candidates: list[tuple[int, int, int]] = []
        label_map = dict(labels)
        for terminal in terminals:
            terminal_bit = 1 << terminal.index
            if selected & terminal_bit or used_reserve_mask & terminal.reserve_mask:
                continue
            owner_bit = 1 << terminal.owner_index
            if not (shore & owner_bit):
                continue
            owner_component = owner_components[terminal.owner_index]
            expansion = 0
            for source in terminal.sources:
                label = label_map.get(source_base(source))
                if label is not None and label != owner_component:
                    continue
                # Another selected terminal may reserve this source edge.
                edge_id = source_edge(ctx.n, source)
                edge_index = sorted(ctx.blue).index(edge_id) if edge_id in ctx.blue else -1
                if edge_index >= 0 and used_reserve_mask & (1 << edge_index):
                    continue
                if not (relation.get(source, 0) & shore):
                    expansion += 1
            if expansion:
                candidates.append((-expansion, terminal.index, terminal.reserve_mask))
        for _negative_expansion, terminal_index, _mask in sorted(candidates):
            visit(selected | (1 << terminal_index), labels)

    visit(0, ())
    if best is None:
        raise AssertionError("collision search produced no root result")
    flow, selected, labels, final_relation, _deducted_count = best

    # Drop activated common terminals that the final assignment does not use.
    relation_unlabeled, reserve_mask, _ = relation_for(selected, labels)
    label_map = dict(labels)
    used_terminal_ids: set[int] = set()
    for source, owner_index in flow.assignment:
        raw_mask = raw.get(source, 0)
        label = label_map.get(source_base(source))
        if label is not None:
            raw_mask &= sum(
                1 << i
                for i, component in enumerate(owner_components)
                if component == label
            )
        source_is_reserved = False
        source_pair = source_edge(ctx.n, source)
        for terminal_index in _selected_ids(selected):
            if source_pair in terminals[terminal_index].reserve_edges:
                source_is_reserved = True
                break
        if raw_mask & (1 << owner_index) and not source_is_reserved:
            continue
        providers = [
            terminal_index
            for terminal_index in _selected_ids(selected)
            if terminals[terminal_index].owner_index == owner_index
            and source in terminals[terminal_index].sources
        ]
        if not providers:
            raise AssertionError("matched non-raw arc has no selected common terminal")
        used_terminal_ids.add(min(providers))
    used_selected = sum(1 << index for index in used_terminal_ids)
    final_relation, _used_reserve, deducted = relation_for(used_selected, labels)
    for source, owner_index in flow.assignment:
        if not (final_relation.get(source, 0) & (1 << owner_index)):
            raise AssertionError("terminal minimization invalidated assignment")

    # Exact final certificate checks.
    if len({source for source, _owner in flow.assignment}) != len(flow.assignment):
        raise AssertionError("FreeHalf source spent twice")
    used_edges: set[Edge] = set()
    for terminal_index in sorted(used_terminal_ids):
        terminal = terminals[terminal_index]
        if used_edges.intersection(terminal.reserve_edges):
            raise AssertionError("common-blue reservation edge reused")
        used_edges.update(terminal.reserve_edges)
    if any(source_edge(ctx.n, source) in used_edges for source, _ in flow.assignment):
        raise AssertionError("matching spends a FreeHalf deducted by a reservation")
    base_component: dict[int, int] = {}
    for source, owner_index in flow.assignment:
        base = source_base(source)
        component = owner_components[owner_index]
        if base in base_component and base_component[base] != component:
            raise AssertionError("base key crosses active components")
        base_component[base] = component

    return CollisionResult(
        exact=True,
        demand=total_demand,
        matched=flow.value,
        defect=total_demand - flow.value,
        assignment=flow.assignment,
        selected_terminals=tuple(sorted(used_terminal_ids)),
        base_labels=labels,
        search_nodes=nodes,
        raw_source_count=len(raw),
        final_source_count=len(final_relation),
        deducted_raw_keys=deducted,
        witness_owner_mask=flow.reachable_owner_mask,
        witness_demand=flow.witness_demand,
        witness_reach=flow.witness_reach,
    )


@dataclass(frozen=True)
class DoorResult:
    exact: bool
    demand_slots: int
    matched_slots: int
    defect_slots: int
    assignment: tuple[tuple[Edge, int], ...]
    vertex_slack: tuple[tuple[int, int], ...]
    slack_paid_incidences: int
    witness_owners: tuple[int, ...]
    witness_demand: int
    witness_reach: int


def door_match(state: p5.TupleState, n: int) -> DoorResult:
    owners = tuple(
        owner for owner in sorted(state.active_vertices)
        if state.hit_need.get(owner, 0) > 0
    )
    demand = tuple(state.hit_need[owner] for owner in owners)
    edges = tuple(sorted(state.demanded_active_edges))
    edge_id = {edge: index for index, edge in enumerate(edges)}
    relation: dict[int, int] = {}
    for index, owner in enumerate(owners):
        for edge in edges:
            if owner in edge:
                relation[edge_id[edge]] = relation.get(edge_id[edge], 0) | (1 << index)
    flow = owner_source_flow(demand, relation)
    assignment = tuple(
        sorted((edges[source], owners[owner_index]) for source, owner_index in flow.assignment)
    )
    if len({edge for edge, _owner in assignment}) != len(assignment):
        raise AssertionError("Door key spent twice")
    for edge, owner in assignment:
        if edge not in state.demanded_active_edges or owner not in edge:
            raise AssertionError("illegal Door incidence")
    vertex_slack = tuple(
        (owner, max(0, n - 5 * state.row_count[owner]))
        for owner in sorted(state.active_vertices)
    )
    paid = sum(
        state.active_degree[owner] - state.hit_need.get(owner, 0)
        for owner in state.active_vertices
    )
    witness_mask = flow.reachable_owner_mask
    return DoorResult(
        exact=True,
        demand_slots=sum(demand),
        matched_slots=flow.value,
        defect_slots=sum(demand) - flow.value,
        assignment=assignment,
        vertex_slack=vertex_slack,
        slack_paid_incidences=paid,
        witness_owners=tuple(
            owner for index, owner in enumerate(owners)
            if witness_mask & (1 << index)
        ),
        witness_demand=flow.witness_demand,
        witness_reach=flow.witness_reach,
    )


def collision_obligations(
    state: p5.TupleState, owners: tuple[int, ...]
) -> dict[int, list[tuple[int, int, int, int]]]:
    out: dict[int, list[tuple[int, int, int, int]]] = {}
    for owner in owners:
        obligations = []
        for other in range(len(state.pair)):
            for copy in range(max(0, state.pair[owner][other] - 1)):
                for half in (0, 1):
                    obligations.append((owner, other, copy, half))
        if len(obligations) != state.collision[owner]:
            raise AssertionError("collision obligation cardinality mismatch")
        out[owner] = obligations
    return out


def analyze_fullbank(
    ctx: p5.GraphContext,
    rows: Iterable[Iterable[int]],
    *,
    details: bool = False,
) -> dict:
    state = p5.reconstruct_state(ctx, rows)
    owners = collision_owners(state)
    raw, masks = raw_relation(ctx, state, owners)
    terminals = common_terminals(ctx, state, owners, raw)
    collision = coherent_collision_match(ctx, state, owners, raw, terminals)
    doors = door_match(state, ctx.n)
    full = collision.defect == 0 and doors.defect_slots == 0
    result = {
        "full": full,
        "collisionDemand": collision.demand,
        "collisionMatched": collision.matched,
        "collisionDefect": collision.defect,
        "hitNeedSlots": doors.demand_slots,
        "doorMatchedSlots": doors.matched_slots,
        "doorDefectSlots": doors.defect_slots,
        "microDemand": collision.demand + 25 * doors.demand_slots,
        "microMatched": collision.matched + 25 * doors.matched_slots,
        "microDefect": collision.defect + 25 * doors.defect_slots,
        "owners": list(owners),
        "allDemandOwners": list(state.owners),
        "activeVertices": len(state.active_vertices),
        "activeEdges": len(state.active_edges),
        "demandedActiveEdges": len(state.demanded_active_edges),
        "rawSourceKeys": collision.raw_source_count,
        "finalSourceKeys": collision.final_source_count,
        "commonCandidates": len(terminals),
        "commonUsed": len(collision.selected_terminals),
        "rawKeysDeducted": len(collision.deducted_raw_keys),
        "coherenceLabels": len(collision.base_labels),
        "collisionSearchNodes": collision.search_nodes,
        "vertexSlackPaidIncidences": doors.slack_paid_incidences,
        "doorRawCapacity": 25 * doors.matched_slots,
        "pruneCheckedCapacity": 0,
        "p5Keys": len(masks["p5"]),
        "p5OwnerArcs": sum(mask.bit_count() for mask in masks["p5"].values()),
    }
    if details:
        obligation_by_owner = collision_obligations(state, owners)
        assigned_by_owner: dict[int, list[int]] = {owner: [] for owner in owners}
        for source, owner_index in collision.assignment:
            assigned_by_owner[owners[owner_index]].append(source)
        assignment_records = []
        for owner in owners:
            obligations = obligation_by_owner[owner]
            sources = sorted(assigned_by_owner[owner])
            for obligation, source in zip(obligations, sources):
                assignment_records.append(
                    {
                        "obligation": list(obligation),
                        "source": list(decode_source(ctx.n, source)),
                    }
                )
        result["state"] = p5.state_details(ctx, state)
        result["collisionAssignment"] = assignment_records
        result["selectedCommonTerminals"] = [
            {
                "owner": terminals[index].owner,
                "source": [terminals[index].source_x, terminals[index].source_y],
                "halves": [
                    list(decode_source(ctx.n, source))
                    for source in terminals[index].sources
                ],
                "reserveEdges": [list(edge) for edge in terminals[index].reserve_edges],
            }
            for index in collision.selected_terminals
        ]
        result["deductedRawKeys"] = [
            list(decode_source(ctx.n, source))
            for source in collision.deducted_raw_keys
        ]
        result["baseLabels"] = [list(item) for item in collision.base_labels]
        result["collisionWitness"] = {
            "owners": [
                owner for index, owner in enumerate(owners)
                if collision.witness_owner_mask & (1 << index)
            ],
            "demand": collision.witness_demand,
            "reach": collision.witness_reach,
        }
        result["doorAssignment"] = [
            {
                "owner": owner,
                "edge": list(edge),
                "copies": 25,
            }
            for edge, owner in doors.assignment
        ]
        result["vertexSlack"] = [
            {"owner": owner, "capacity": capacity}
            for owner, capacity in doors.vertex_slack
        ]
        result["doorWitness"] = {
            "owners": list(doors.witness_owners),
            "demand": doors.witness_demand,
            "reach": doors.witness_reach,
        }
    return result
