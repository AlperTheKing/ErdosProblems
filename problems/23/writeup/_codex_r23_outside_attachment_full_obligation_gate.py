"""Corrected R23 outside-attachment gate with the full owner obligations.

The original R23 fixture gate checks collision halves but does not reserve the
half-zero orientations of active off-support edges and does not add the
residual endpoint ``HitNeed`` obligations.  Those omissions are harmless on
the 89-vertex cage (its active set is empty), but they matter to the claimed
311 full-transfer verdict.

This companion gate uses the owner-aggregate form of the exact relation:

* owner demand = collision halves + HitNeed;
* a free ordered active-edge cell has capacity one, every other free cell two;
* same-owner, row-companion, and R23 outside-attachment eligibility;
* exact max-cut switch loss is recomputed for every used pattern-4 component
  pair (nonnegative automatically on these certified maximum cuts).

All arithmetic and max flow are integral exact.
"""

from __future__ import annotations

from collections import deque


def edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def dinic(node_count: int, source: int, sink: int, arcs):
    graph = [[] for _ in range(node_count)]

    def add(u, v, cap):
        graph[u].append([v, cap, len(graph[v])])
        graph[v].append([u, 0, len(graph[u]) - 1])

    for u, v, cap in arcs:
        add(u, v, cap)
    flow = 0
    while True:
        level = [-1] * node_count
        level[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v, cap, _ in graph[u]:
                if cap > 0 and level[v] < 0:
                    level[v] = level[u] + 1
                    queue.append(v)
        if level[sink] < 0:
            reachable = {source}
            queue = deque([source])
            while queue:
                u = queue.popleft()
                for v, cap, _ in graph[u]:
                    if cap > 0 and v not in reachable:
                        reachable.add(v)
                        queue.append(v)
            return flow, reachable
        cursor = [0] * node_count

        def send(u, amount):
            if u == sink:
                return amount
            while cursor[u] < len(graph[u]):
                item = graph[u][cursor[u]]
                v, cap, reverse = item
                if cap > 0 and level[v] == level[u] + 1:
                    pushed = send(v, min(amount, cap))
                    if pushed:
                        item[1] -= pushed
                        graph[v][reverse][1] += pushed
                        return pushed
                cursor[u] += 1
            return 0

        while True:
            pushed = send(source, 1 << 60)
            if not pushed:
                break
            flow += pushed


def full_owner_flow(
    n_vertices, blue, bad, rows, label, *, require_full=True, quiet=False,
    scope="all", include_outside=True
):
    counts = {}
    row_count = [0] * n_vertices
    selected_support = set()
    for row in rows:
        for x in row:
            row_count[x] += 1
            for y in row:
                counts[(x, y)] = counts.get((x, y), 0) + 1
        selected_support.update(edge(x, y) for x, y in zip(row, row[1:]))
    selected = {x for row in rows for x in row}
    active = {
        e for e in blue
        if e[0] in selected and e[1] in selected and e not in selected_support
    }

    # Components of the internal off-support graph.  A component is active
    # exactly when it contains both endpoints of a selected bad atom.  The
    # canonical block cover collapses every other component, making all of its
    # internal loads identically zero before transfer Hall is invoked.
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
    demanded_active = {
        e for e in active if find(e[0]) in active_roots
    }
    if scope not in {"all", "active"}:
        raise ValueError(f"unknown scope: {scope}")
    owner_scope = set(range(n_vertices)) if scope == "all" else active_vertices
    reserved_active = active if scope == "all" else demanded_active

    active_degree = [0] * n_vertices
    for x, y in reserved_active:
        active_degree[x] += 1
        active_degree[y] += 1

    collision = {
        v: 2 * sum(
            multiplicity - 1
            for (x, _), multiplicity in counts.items()
            if x == v and multiplicity >= 2
        )
        for v in owner_scope
    }
    tload = [5 * row_count[v] for v in range(n_vertices)]
    hitneed = {
        v: max(0, active_degree[v] - max(0, n_vertices - tload[v]))
        for v in owner_scope
    }
    demand = {
        v: collision[v] + hitneed[v]
        for v in owner_scope
        if collision[v] + hitneed[v] > 0
    }
    owners = sorted(demand)

    blue_adj = [set() for _ in range(n_vertices)]
    for x, y in blue:
        blue_adj[x].add(y)
        blue_adj[y].add(x)

    # Components of the blue graph induced outside the selected row union.
    component_id = [-1] * n_vertices
    components = []
    attachments = []
    for root in range(n_vertices):
        if root in selected or component_id[root] >= 0:
            continue
        cid = len(components)
        vertices = set()
        attachment = set()
        component_id[root] = cid
        queue = deque([root])
        while queue:
            x = queue.popleft()
            vertices.add(x)
            for y in blue_adj[x]:
                if y in selected:
                    attachment.add(y)
                elif component_id[y] < 0:
                    component_id[y] = cid
                    queue.append(y)
        components.append(vertices)
        attachments.append(attachment)

    eligible_outside = {}
    for owner in owners:
        eligible = set()
        for cid, component in enumerate(components):
            if any(counts.get((owner, a), 0) > 0 for a in attachments[cid]):
                eligible.update(component)
        eligible_outside[owner] = eligible

    def loss(vertices):
        return (
            sum((x in vertices) != (y in vertices) for x, y in blue)
            - sum((x in vertices) != (y in vertices) for x, y in bad)
        )

    # Cells are created lazily.  Capacity one exactly implements the reserved
    # half-zero orientation on an active edge; all other cells have two halves.
    cell_id = {}
    cell_capacity = {}

    def get_cell(x, y):
        key = (x, y)
        if key not in cell_id:
            cell_id[key] = len(cell_id)
            cell_capacity[key] = 1 if edge(x, y) in reserved_active else 2
        return cell_id[key]

    owner_cell_arcs = set()
    for owner_index, owner in enumerate(owners):
        # Same-owner sources.
        for y in range(n_vertices):
            if y != owner and counts.get((owner, y), 0) == 0:
                owner_cell_arcs.add((owner_index, get_cell(owner, y)))

        # Row-companion sources.  Positive co-occurrence is the exact semantic
        # relation; commonBad is already a subcase.
        companions = [
            x for x in range(n_vertices)
            if x != owner and counts.get((owner, x), 0) > 0
        ]
        for x in companions:
            for y in companions:
                if x != y and counts.get((x, y), 0) == 0 and loss({x, y}) >= 0:
                    owner_cell_arcs.add((owner_index, get_cell(x, y)))

        # Outside-component attachment sources.  These cells are never active.
        if include_outside:
            outside = sorted(eligible_outside[owner])
            loss_cache = {}
            for x in outside:
                for y in outside:
                    if x == y:
                        continue
                    pair = (component_id[x], component_id[y])
                    if pair not in loss_cache:
                        loss_cache[pair] = loss(
                            components[pair[0]] | components[pair[1]]
                        ) >= 0
                    if loss_cache[pair]:
                        owner_cell_arcs.add((owner_index, get_cell(x, y)))

    source, sink = 0, 1
    owner_base = 2
    cell_base = owner_base + len(owners)
    inverse_cell = {value: key for key, value in cell_id.items()}
    # Owner-to-cell capacity may safely equal the cell capacity; the cell sink
    # arc enforces global no-double-spend across owners.
    arcs = [
        (source, owner_base + i, demand[owner])
        for i, owner in enumerate(owners)
    ] + [
        (owner_base + i, cell_base + j, cell_capacity[inverse_cell[j]])
        for i, j in owner_cell_arcs
    ]
    arcs.extend(
        (cell_base + j, sink, cell_capacity[inverse_cell[j]])
        for j in range(len(cell_id))
    )

    total = sum(demand.values())
    maximum, reachable = dinic(cell_base + len(cell_id), source, sink, arcs)
    deficient_owners = [
        owner for i, owner in enumerate(owners)
        if owner_base + i in reachable
    ] if maximum < total else []
    record = {
        "label": label,
        "scope": scope,
        "includeOutside": include_outside,
        "owners": len(owners),
        "activeEdges": len(active),
        "activeComponents": len(active_roots),
        "activeVertices": len(active_vertices),
        "demandedActiveEdges": len(demanded_active),
        "collisionDemand": sum(collision.values()),
        "hitNeed": sum(hitneed.values()),
        "totalDemand": total,
        "cells": len(cell_id),
        "maxFlow": maximum,
        "deficiency": total - maximum,
        "deficientOwners": deficient_owners,
        "full": maximum == total,
        "eligibleOutsideByOwner": {
            str(v): len(eligible_outside[v]) for v in owners
            if eligible_outside[v]
        },
    }
    if not quiet:
        print(record)
    if require_full:
        assert maximum == total
    return record


def build_89():
    r, c_l, c_r = 0, 1, 2
    left = [3, 4, 5, 6]
    right = [7, 8, 9, 10, 11]
    anchor = 12
    locks = [0, 0, 0, 4, 6, 4, 5, 5, 3, 3, 3, 5]
    blue = {edge(r, c_l), edge(r, c_r)}
    blue.update(edge(c_l, x) for x in left)
    blue.update(edge(c_r, y) for y in right)
    bad = {edge(x, y) for x in left for y in right}
    nxt = 13
    for v, count in enumerate(locks):
        for _ in range(count):
            x, y = nxt, nxt + 1
            nxt += 2
            blue.update((edge(v, x), edge(x, y), edge(y, anchor)))
    rows = [(x, c_l, r, c_r, y) for x in left for y in right]
    assert nxt == 89
    return nxt, blue, bad, rows


def build_311():
    blue = set()
    bad = []
    for i in range(26):
        blue.add(edge(i, (i + 1) % 26))
    blue.add(edge(26, 0))
    for i in range(26):
        bad.append(edge(i, (i + 4) % 26))
    bad.extend((edge(26, 3), edge(26, 23)))
    path = [0]
    for _ in range(12):
        path.append((path[-1] + 9) % 26)
    blue.update(edge(x, y) for x, y in zip(path, path[1:]))
    nxt = 27
    for x, y in bad[:28]:
        internal = list(range(nxt, nxt + 5))
        nxt += 5
        chain = [x] + internal + [y]
        blue.update(edge(u, v) for u, v in zip(chain, chain[1:]))
    owner = 9
    p0 = list(range(nxt, nxt + 8)); nxt += 8
    p1 = list(range(nxt, nxt + 64)); nxt += 64
    p3 = list(range(nxt, nxt + 64)); nxt += 64
    p4 = list(range(nxt, nxt + 8)); nxt += 8
    blue.update(edge(x, y) for x in p0 for y in p1)
    blue.update(edge(y, owner) for y in p1)
    blue.update(edge(owner, y) for y in p3)
    blue.update(edge(x, y) for x in p3 for y in p4)
    attachment_bad = [edge(x, y) for x in p4 for y in p0]
    bad.extend(attachment_bad)
    rows = [tuple((i + step) % 26 for step in range(5)) for i in range(26)]
    rows.extend(((26, 0, 1, 2, 3), (26, 0, 25, 24, 23)))
    rows.extend((x, p3[0], owner, p1[0], y) for x, y in attachment_bad)
    assert nxt == 311
    return nxt, blue, set(bad), rows


def main():
    record89 = full_owner_flow(*build_89(), "89", scope="all")
    assert record89["activeEdges"] == 0 and record89["hitNeed"] == 0
    record311 = full_owner_flow(*build_311(), "311", scope="all")
    assert record311["activeEdges"] > 0 and record311["hitNeed"] > 0
    print("VERDICT: R23 outsideAttachment passes the corrected full owner obligations")


if __name__ == "__main__":
    main()
