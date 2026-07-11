"""Exact structural census of active-scoped monotone one-row descents.

This refines ``_codex_r23_outside_attachment_census_gate.py``.  For every
active-scoped Hall failure it chooses the lexicographically least one-row
replacement with nonincreasing global collision units and strictly fewer
active edges, then records the old active-component geometry, the canonical
deficient owner shore, and the exact score deltas.  All arithmetic is
integral and all graph predicates are recomputed from the literal rows.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from itertools import product

from _codex_r19_global_base_census import dec, graph6_for_orders, loads, multiplicities
from _codex_r20_two_row_exchange_gate import obligation_score, shortest_row_families
from _codex_r23_outside_attachment_full_obligation_gate import edge, full_owner_flow


def row_structure(n, blue, bad, rows):
    selected = {v for row in rows for v in row}
    support = {edge(x, y) for row in rows for x, y in zip(row, row[1:])}
    active = {e for e in blue if e[0] in selected and e[1] in selected and e not in support}
    adj = {v: set() for v in selected}
    for x, y in active:
        adj[x].add(y)
        adj[y].add(x)
    components = []
    component_of = {}
    for root in sorted(selected):
        if root in component_of:
            continue
        cid = len(components)
        vertices = set()
        queue = deque([root])
        component_of[root] = cid
        while queue:
            x = queue.popleft()
            vertices.add(x)
            for y in adj[x]:
                if y not in component_of:
                    component_of[y] = cid
                    queue.append(y)
        components.append(vertices)
    active_component_ids = {
        component_of[x]
        for x, y in bad
        if x in selected and y in selected and component_of[x] == component_of[y]
    }
    active_components = [components[cid] for cid in sorted(active_component_ids)]
    return {
        "selected": selected,
        "support": support,
        "active": active,
        "adj": adj,
        "componentOf": component_of,
        "components": components,
        "activeComponentIds": active_component_ids,
        "activeComponents": active_components,
    }


def collision_units(n, rows):
    count = multiplicities(n, rows)
    return sum(max(0, count[x][y] - 1) for x in range(n) for y in range(n))


def active_distance(structure, source, target):
    queue = deque([(source, 0)])
    seen = {source}
    while queue:
        x, distance = queue.popleft()
        if x == target:
            return distance
        for y in structure["adj"].get(x, ()):
            if y not in seen:
                seen.add(y)
                queue.append((y, distance + 1))
    return None


def analyze_graph(g6):
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    if info is None:
        return {"status": "skipNoCut", "order": n}
    if any(length != 5 for length in info["ell"].values()):
        return {"status": "skipNotAll5", "order": n}
    families = shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    hist = Counter()
    failures = 0
    for choice in product(*(range(size) for size in sizes)):
        rows = tuple(families[i][choice[i]] for i in range(len(choice)))
        old_flow = full_owner_flow(
            n, set(info["Bset"]), set(info["Mset"]), rows, g6,
            require_full=False, quiet=True, scope="active", include_outside=False,
        )
        if old_flow["full"]:
            continue
        failures += 1
        old_structure = row_structure(n, set(info["Bset"]), set(info["Mset"]), rows)
        old_collision = collision_units(n, rows)
        old_active = len(old_structure["active"])
        old_score = 2 * (old_collision + old_active)
        candidates = []
        existential = Counter()
        shore = set(old_flow["deficientOwners"])
        for index, family in enumerate(families):
            for replacement, new_row in enumerate(family):
                if replacement == choice[index]:
                    continue
                new_rows = rows[:index] + (new_row,) + rows[index + 1:]
                new_structure = row_structure(
                    n, set(info["Bset"]), set(info["Mset"]), new_rows
                )
                new_collision = collision_units(n, new_rows)
                new_active = len(new_structure["active"])
                if new_collision > old_collision or new_active >= old_active:
                    continue
                bad_edge = tuple(info["M"][index])
                replacement_edges = {edge(x, y) for x, y in zip(new_row, new_row[1:])}
                cid = old_structure["componentOf"].get(bad_edge[0])
                component = (
                    old_structure["components"][cid]
                    if cid is not None and old_structure["componentOf"].get(bad_edge[1]) == cid
                    else set()
                )
                all_in_component = set(new_row) <= component
                active_count = len(replacement_edges & old_structure["active"])
                support_count = len(replacement_edges & old_structure["support"])
                existential["badEndpointInShore"] |= bool(set(bad_edge) & shore)
                existential["oldRowMeetsShore"] |= bool(set(rows[index]) & shore)
                existential["newRowMeetsShore"] |= bool(set(new_row) & shore)
                existential["allNewVerticesInOldActiveComponent"] |= all_in_component
                candidates.append((
                    2 * (new_collision + new_active), index, replacement,
                    new_collision, new_active, new_structure, component,
                    active_count, support_count, active_distance(
                        old_structure, bad_edge[0], bad_edge[1]
                    ), bad_edge, new_row, all_in_component,
                ))
        assert candidates, (g6, choice, old_flow)
        candidate = min(
            candidates,
            key=lambda item: (
                not item[13],
                len(item[5]["activeComponents"]) != 0,
                item[0], item[1], item[2],
            ),
        )
        (new_score, index, replacement, new_collision, new_active, new_structure,
         component, active_count, support_count, distance, bad_edge, new_row,
         all_in_component) = candidate
        assert all_in_component
        component_edges = sum(
            x in component and y in component for x, y in old_structure["active"]
        )
        witness_bads = sum(
            x in component and y in component for x, y in info["Mset"]
        )
        hist[f"fail.activeComponents={old_flow['activeComponents']}"] += 1
        hist[f"fail.deficiency={old_flow['deficiency']}"] += 1
        hist[f"fail.deficientOwners={len(shore)}"] += 1
        hist[f"fail.badEdges={len(info['M'])}"] += 1
        hist[f"component.shape={len(component)}v,{component_edges}e,{witness_bads}b"] += 1
        hist[f"descent.deltaCollision={new_collision - old_collision}"] += 1
        hist[f"descent.deltaActive={new_active - old_active}"] += 1
        hist[f"descent.deltaScore={new_score - old_score}"] += 1
        hist[f"descent.activeDistance={distance}"] += 1
        hist[f"descent.replacementEdges={active_count}A+{support_count}S"] += 1
        hist[f"descent.newActiveComponents={len(new_structure['activeComponents'])}"] += 1
        hist[f"descent.badEndpointShoreCount={len(set(bad_edge) & shore)}"] += 1
        hist[f"descent.oldRowShoreCount={len(set(rows[index]) & shore)}"] += 1
        hist[f"descent.newRowShoreCount={len(set(new_row) & shore)}"] += 1
        hist[f"exists.badEndpointInShore={bool(existential['badEndpointInShore'])}"] += 1
        hist[f"exists.oldRowMeetsShore={bool(existential['oldRowMeetsShore'])}"] += 1
        hist[f"exists.newRowMeetsShore={bool(existential['newRowMeetsShore'])}"] += 1
        hist[
            "exists.allNewVerticesInOldActiveComponent="
            f"{bool(existential['allNewVerticesInOldActiveComponent'])}"
        ] += 1
    return {"status": "eligible", "order": n, "failures": failures, "hist": dict(hist)}


def positive(value):
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-order", type=positive, default=10)
    parser.add_argument("--max-order", type=positive, default=11)
    parser.add_argument("--workers", type=positive, default=min(48, os.cpu_count() or 1))
    args = parser.parse_args()
    if args.workers > 64:
        parser.error("--workers must not exceed 64")
    graph6, generated = graph6_for_orders(args.min_order, args.max_order)
    total = Counter()
    status = Counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(analyze_graph, graph6, chunksize=16):
            status[result["status"]] += 1
            if result["status"] != "eligible":
                continue
            total["failures"] += result["failures"]
            total.update(result["hist"])
    print(json.dumps({
        "orders": [args.min_order, args.max_order],
        "workers": args.workers,
        "generatedGraphs": generated,
        "status": dict(status),
        "result": dict(sorted(total.items())),
    }, sort_keys=True, separators=(",", ":")))
    assert total["failures"] == total["exists.allNewVerticesInOldActiveComponent=True"]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
