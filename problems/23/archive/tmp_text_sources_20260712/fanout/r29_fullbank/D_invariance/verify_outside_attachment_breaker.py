"""Exact R23 outsideAttachment breaker for restricted-pool invariance."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
TRAFFIC = frozenset(range(55))


def load() -> tuple[object, dict]:
    spec = importlib.util.spec_from_file_location("r29_incidence", LEAD)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module, module.build()


def analyze(data: dict, rows: tuple[tuple[int, ...], ...]) -> dict:
    n = data["n"]
    adj = [[] for _ in range(n)]
    for u, v in data["blue"]:
        adj[u].append(v)
        adj[v].append(u)
    selected = {v for row in rows for v in row}
    support = {
        (u, v) if u < v else (v, u)
        for row in rows for u, v in zip(row, row[1:])
    }
    active_edges = {
        e for e in data["blue"]
        if e[0] in selected and e[1] in selected and e not in support
    }
    active_adj = [[] for _ in range(n)]
    for u, v in active_edges:
        active_adj[u].append(v)
        active_adj[v].append(u)
    hub_component = {0}
    todo = deque([0])
    while todo:
        u = todo.popleft()
        for v in active_adj[u]:
            if v not in hub_component:
                hub_component.add(v)
                todo.append(v)
    hub_blue_boundary = {
        e for e in data["blue"]
        if (e[0] in hub_component) != (e[1] in hub_component)
    }
    outside = set(range(n)) - selected
    pair = Counter()
    for row in rows:
        for x in row:
            for y in row:
                pair[x, y] += 1

    component: dict[int, int] = {}
    components: list[set[int]] = []
    for root in sorted(outside):
        if root in component:
            continue
        seen = {root}
        todo = deque([root])
        while todo:
            u = todo.popleft()
            for v in adj[u]:
                if v in outside and v not in seen:
                    seen.add(v)
                    todo.append(v)
        cid = len(components)
        for v in seen:
            component[v] = cid
        components.append(seen)

    attachments = [
        {v for u in comp for v in adj[u] if v in selected}
        for comp in components
    ]
    # All three hubs have the same fixed row-companion set TRAFFIC.
    eligible = {
        x for x in outside
        if attachments[component[x]] & TRAFFIC
    }
    free_pairs = [
        (x, y) for x in sorted(eligible) for y in sorted(eligible)
        if x != y and pair[x, y] == 0
    ]
    assert free_pairs
    x, y = free_pairs[0]
    witness = {
        "source": [x, y],
        "attachment_x": min(attachments[component[x]] & TRAFFIC),
        "attachment_y": min(attachments[component[y]] & TRAFFIC),
        "owner_companion_set": [0, 54],
        "pair_multiplicity": pair[x, y],
    }
    return {
        "selected_vertices": len(selected),
        "outside_vertices": len(outside),
        "outside_components": len(components),
        "outside_attachment_eligible_vertices": len(eligible),
        "ordered_free_pairs": len(free_pairs),
        "outside_attachment_half_sources": 2 * len(free_pairs),
        "hub_active_component_vertices": len(hub_component),
        "hub_blue_boundary_edges": len(hub_blue_boundary),
        "anchor_row_load": sum(55 in row for row in rows),
        "witness": witness,
    }


def main() -> None:
    module, data = load()
    start = data["selectorStart"]
    rows = [tuple(row) for row in data["rows"]]
    for i, meta in enumerate(data["selectorMeta"]):
        rows[start + i] = tuple(meta["anchorRow"])
    all_anchor_rows = tuple(rows)
    all_anchor = analyze(data, all_anchor_rows)

    adj = module.adjacency(data["n"], data["blue"])
    family = module.shortest_rows(adj, *data["atoms"][start])
    local = min(row for row in family if 55 not in row)
    anchor = tuple(data["selectorMeta"][0]["anchorRow"])
    rows[start] = local
    one_local = analyze(data, tuple(rows))

    assert all_anchor["outside_attachment_half_sources"] == 912600
    assert one_local["outside_attachment_half_sources"] == 909900
    assert all_anchor["outside_attachment_half_sources"] - one_local["outside_attachment_half_sources"] == 2700
    support = lambda row: {
        (u, v) if u < v else (v, u) for u, v in zip(row, row[1:])
    }
    removed_support = sorted(support(anchor) - support(local))
    added_support = sorted(support(local) - support(anchor))
    assert (removed_support, added_support) == (
        [(55, 59), (55, 735)], [(59, 732), (732, 735)])
    result = {
        "arithmetic": "integers only",
        "relation": "R23 outsideAttachment for hub shore {0,1,2}",
        "all_anchor": all_anchor,
        "one_local_selector_index": 0,
        "one_local_row": list(local),
        "replaced_anchor_row": list(anchor),
        "removed_row_support": removed_support,
        "added_row_support": added_support,
        "one_local": one_local,
        "half_source_change": -2700,
        "restricted_pool": 19925,
        "all_anchor_restricted_plus_outside": 19925 + 912600,
        "one_local_restricted_plus_outside": 19925 + 909900,
        "incidence_source_sha256": hashlib.sha256(LEAD.read_bytes()).hexdigest(),
    }
    output = HERE / "outside_attachment_breaker_result.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
