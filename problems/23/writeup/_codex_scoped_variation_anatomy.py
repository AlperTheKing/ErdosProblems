"""Exact anatomy of the active-scoped one-row variation frontier.

The default fixture is the first order-10 Hall failure.  The script separates
collision and HitNeed score changes, records the deficient owner shore, and
counts its exact ordered free-half source neighborhood.  It is diagnostic:
all graph and score arithmetic is integral and uses the same definitions as
the exhaustive census gates.
"""

from __future__ import annotations

import argparse
import json

from _codex_r19_global_base_census import dec, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_outside_attachment_full_obligation_gate import (
    dinic,
    edge,
    full_owner_flow,
)


def scoped_state(n, blue, bad, rows):
    counts = {}
    row_count = [0] * n
    support = set()
    for row in rows:
        for x in row:
            row_count[x] += 1
            for y in row:
                counts[(x, y)] = counts.get((x, y), 0) + 1
        support.update(edge(x, y) for x, y in zip(row, row[1:]))

    selected = {x for row in rows for x in row}
    active = {
        e for e in blue
        if e[0] in selected and e[1] in selected and e not in support
    }
    parent = {v: v for v in selected}

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    def union(x, y):
        x, y = find(x), find(y)
        if x != y:
            parent[max(x, y)] = min(x, y)

    for x, y in active:
        union(x, y)
    active_roots = {
        find(x) for x, y in bad
        if x in selected and y in selected and find(x) == find(y)
    }
    active_vertices = {v for v in selected if find(v) in active_roots}
    demanded_active = {e for e in active if find(e[0]) in active_roots}
    active_degree = [0] * n
    for x, y in demanded_active:
        active_degree[x] += 1
        active_degree[y] += 1

    collision = {
        v: 2 * sum(
            multiplicity - 1
            for (x, _), multiplicity in counts.items()
            if x == v and multiplicity >= 2
        )
        for v in sorted(active_vertices)
    }
    raw_collision = {
        v: 2 * sum(
            multiplicity - 1
            for (x, _), multiplicity in counts.items()
            if x == v and multiplicity >= 2
        )
        for v in range(n)
    }
    hitneed = {
        v: max(0, active_degree[v] - max(0, n - 5 * row_count[v]))
        for v in sorted(active_vertices)
    }
    demand = {v: collision[v] + hitneed[v] for v in sorted(active_vertices)}
    return {
        "counts": counts,
        "rowCount": row_count,
        "support": support,
        "active": active,
        "activeVertices": active_vertices,
        "activeComponent": {v: find(v) for v in active_vertices},
        "demandedActive": demanded_active,
        "collision": collision,
        "rawCollision": raw_collision,
        "hitNeed": hitneed,
        "demand": demand,
        "collisionTotal": sum(collision.values()),
        "rawCollisionTotal": sum(raw_collision.values()),
        "hitNeedTotal": sum(hitneed.values()),
        "score": sum(demand.values()),
    }


def owner_shore_source_count(n, blue, bad, state, owners):
    counts = state["counts"]
    owners = set(owners)

    def loss(vertices):
        vertices = set(vertices)
        return (
            sum((x in vertices) != (y in vertices) for x, y in blue)
            - sum((x in vertices) != (y in vertices) for x, y in bad)
        )

    cells = set()
    by_owner = {}
    for owner in owners:
        eligible = set()
        for y in range(n):
            if y != owner and counts.get((owner, y), 0) == 0:
                eligible.add((owner, y))
        companions = [
            x for x in range(n)
            if x != owner and counts.get((owner, x), 0) > 0
        ]
        for x in companions:
            for y in companions:
                if x != y and counts.get((x, y), 0) == 0:
                    if loss({x, y}) >= 0:
                        eligible.add((x, y))
        by_owner[owner] = eligible
        cells.update(eligible)

    halves = 0
    capacities = {}
    for x, y in cells:
        capacity = 1 if edge(x, y) in state["demandedActive"] else 2
        capacities[(x, y)] = capacity
        halves += capacity
    return halves, by_owner, capacities


def summarize_state(state):
    return {
        "score": state["score"],
        "collisionTotal": state["collisionTotal"],
        "rawCollisionTotal": state["rawCollisionTotal"],
        "hitNeedTotal": state["hitNeedTotal"],
        "collisionByOwner": state["collision"],
        "hitNeedByOwner": state["hitNeed"],
        "demandByOwner": state["demand"],
        "activeEdges": [list(e) for e in sorted(state["active"])],
        "demandedActiveEdges": [list(e) for e in sorted(state["demandedActive"])],
        "activeVertices": sorted(state["activeVertices"]),
        "activeComponent": state["activeComponent"],
    }


def component_transport_flow(
    old,
    owner_set,
    by_owner,
    capacities,
    alternatives,
    old_row,
    alternative_rows,
):
    """Aggregate component-aware injection into the old transport target."""
    alternative_count = len(alternatives)
    old_shore_demand = sum(old["demand"].get(v, 0) for v in owner_set)
    old_outside_demand = old["score"] - old_shore_demand

    groups = []
    for alternative_id, new in enumerate(alternatives):
        for owner, amount in new["demand"].items():
            if amount:
                groups.append((alternative_id, owner, amount, new))

    cells = sorted(capacities)
    source = 0
    outside = 1
    group_base = 2
    cell_base = group_base + len(groups)
    sink = cell_base + len(cells)
    arcs = [(source, group_base + j, amount) for j, (_, _, amount, _) in enumerate(groups)]
    arcs.append((outside, sink, alternative_count * old_outside_demand))
    cell_index = {cell: j for j, cell in enumerate(cells)}
    touched_groups = 0
    touched_demand = 0
    inherited_only_groups = 0
    inherited_only_demand = 0
    unanchored_groups = 0
    unanchored_demand = 0
    for cell, capacity in capacities.items():
        arcs.append((cell_base + cell_index[cell], sink, alternative_count * capacity))

    for j, (alternative_id, owner, amount, new) in enumerate(groups):
        node = group_base + j
        arcs.append((node, outside, amount))
        component = new["activeComponent"].get(owner)
        new_component_vertices = {
            v for v, cid in new["activeComponent"].items()
            if cid == component
        }
        inherited_anchors = {
            a for a in owner_set
            if any(
                old["activeComponent"].get(v) ==
                  old["activeComponent"].get(a)
                for v in new_component_vertices
            )
        }
        changed_row_vertices = set(old_row) | set(alternative_rows[alternative_id])
        touches_changed_rows = bool(new_component_vertices & changed_row_vertices)
        anchors = set(inherited_anchors)
        if touches_changed_rows:
            anchors.update(owner_set)
            touched_groups += 1
            touched_demand += amount
        elif inherited_anchors:
            inherited_only_groups += 1
            inherited_only_demand += amount
        else:
            unanchored_groups += 1
            unanchored_demand += amount
        eligible = set().union(*(by_owner[a] for a in anchors)) if anchors else set()
        for cell in eligible:
            if cell in cell_index:
                arcs.append((node, cell_base + cell_index[cell], amount))

    total = sum(amount for _, _, amount, _ in groups)
    maximum, _ = dinic(sink + 1, source, sink, arcs)
    return {
        "demand": total,
        "flow": maximum,
        "gap": total - maximum,
        "outsideCapacity": alternative_count * old_outside_demand,
        "sourceCapacity": alternative_count * sum(capacities.values()),
        "groups": len(groups),
        "touchedGroups": touched_groups,
        "touchedDemand": touched_demand,
        "inheritedOnlyGroups": inherited_only_groups,
        "inheritedOnlyDemand": inherited_only_demand,
        "unanchoredGroups": unanchored_groups,
        "unanchoredDemand": unanchored_demand,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--g6", default="I?`fBO]]?")
    parser.add_argument("--choice", default="1,1,1")
    args = parser.parse_args()

    n, graph_edges = dec(args.g6)
    info = loads(n, graph_edges)
    if info is None or any(length != 5 for length in info["ell"].values()):
        raise SystemExit("fixture is not an all-length-five accepted cut")
    blue, bad = set(info["Bset"]), set(info["Mset"])
    families = shortest_row_families(info)
    choice = tuple(int(x) for x in args.choice.split(","))
    if len(choice) != len(families):
        raise SystemExit("choice length does not match bad-edge families")
    rows = tuple(families[i][choice[i]] for i in range(len(choice)))
    old = scoped_state(n, blue, bad, rows)
    flow = full_owner_flow(
        n, blue, bad, rows, args.g6, require_full=False, quiet=True,
        scope="active", include_outside=False,
    )
    owners = flow["deficientOwners"]
    owner_set = set(owners)
    source_count, by_owner, capacities = owner_shore_source_count(
        n, blue, bad, old, owners
    )
    demand_count = sum(old["demand"].get(v, 0) for v in owners)

    by_coordinate = []
    total_delta = 0
    collision_delta = 0
    raw_collision_delta = 0
    hitneed_delta = 0
    alternatives = 0
    for index, family in enumerate(families):
        coordinate = {
            "index": index,
            "oldRow": list(rows[index]),
            "alternatives": [],
            "deltaSum": 0,
            "collisionDeltaSum": 0,
            "rawCollisionDeltaSum": 0,
            "fixedOldScopeCollisionDeltaSum": 0,
            "newScopeMinusFixedOldScopeSum": 0,
            "shoreCollisionDeltaSum": 0,
            "outsideShoreCollisionDeltaSum": 0,
            "hitNeedDeltaSum": 0,
        }
        coordinate_states = []
        coordinate_rows = []
        for replacement, replacement_row in enumerate(family):
            if replacement == choice[index]:
                continue
            new_rows = rows[:index] + (replacement_row,) + rows[index + 1:]
            new = scoped_state(n, blue, bad, new_rows)
            coordinate_states.append(new)
            coordinate_rows.append(replacement_row)
            delta = new["score"] - old["score"]
            cdelta = new["collisionTotal"] - old["collisionTotal"]
            raw_cdelta = (
                new["rawCollisionTotal"] - old["rawCollisionTotal"]
            )
            fixed_old_scope_collision = sum(
                new["rawCollision"].get(v, 0)
                for v in old["activeVertices"]
            )
            fixed_old_scope_delta = (
                fixed_old_scope_collision - old["collisionTotal"]
            )
            old_shore_collision = sum(
                old["collision"].get(v, 0) for v in owner_set
            )
            new_shore_collision = sum(
                new["collision"].get(v, 0) for v in owner_set
            )
            shore_collision_delta = new_shore_collision - old_shore_collision
            outside_shore_collision_delta = cdelta - shore_collision_delta
            hdelta = new["hitNeedTotal"] - old["hitNeedTotal"]
            coordinate["alternatives"].append({
                "replacement": replacement,
                "row": list(replacement_row),
                "delta": delta,
                "collisionDelta": cdelta,
                "rawCollisionDelta": raw_cdelta,
                "fixedOldScopeCollision": fixed_old_scope_collision,
                "fixedOldScopeCollisionDelta": fixed_old_scope_delta,
                "newScopeMinusFixedOldScope":
                    new["collisionTotal"] - fixed_old_scope_collision,
                "shoreCollisionDelta": shore_collision_delta,
                "outsideShoreCollisionDelta": outside_shore_collision_delta,
                "hitNeedDelta": hdelta,
                "new": summarize_state(new),
            })
            coordinate["deltaSum"] += delta
            coordinate["collisionDeltaSum"] += cdelta
            coordinate["rawCollisionDeltaSum"] += raw_cdelta
            coordinate["fixedOldScopeCollisionDeltaSum"] += (
                fixed_old_scope_delta
            )
            coordinate["newScopeMinusFixedOldScopeSum"] += (
                new["collisionTotal"] - fixed_old_scope_collision
            )
            coordinate["shoreCollisionDeltaSum"] += shore_collision_delta
            coordinate["outsideShoreCollisionDeltaSum"] += (
                outside_shore_collision_delta
            )
            coordinate["hitNeedDeltaSum"] += hdelta
            total_delta += delta
            collision_delta += cdelta
            raw_collision_delta += raw_cdelta
            hitneed_delta += hdelta
            alternatives += 1
        coordinate["componentTransport"] = component_transport_flow(
            old,
            owner_set,
            by_owner,
            capacities,
            coordinate_states,
            rows[index],
            coordinate_rows,
        )
        by_coordinate.append(coordinate)

    result = {
        "g6": args.g6,
        "choice": list(choice),
        "familySizes": [len(family) for family in families],
        "rows": [list(row) for row in rows],
        "old": summarize_state(old),
        "flow": flow,
        "deficientOwnerShore": owners,
        "ownerDemand": demand_count,
        "ownerSourceHalves": source_count,
        "ownerDefect": demand_count - source_count,
        "eligibleCellsByOwner": {
            str(v): [list(cell) for cell in sorted(by_owner[v])]
            for v in owners
        },
        "sourceCellCapacity": {
            f"{x},{y}": capacity
            for (x, y), capacity in sorted(capacities.items())
        },
        "alternativeCount": alternatives,
        "variation": total_delta,
        "collisionVariation": collision_delta,
        "rawCollisionVariation": raw_collision_delta,
        "hitNeedVariation": hitneed_delta,
        "coordinates": by_coordinate,
    }
    assert old["score"] == flow["totalDemand"]
    assert demand_count - source_count == flow["deficiency"]
    assert total_delta == collision_delta + hitneed_delta
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
