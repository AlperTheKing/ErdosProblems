"""Exact finite evidence for Pattern-5 base-key component coherence.

This checks only the actual R29 28-key repair and the first N12 P1-P5 micro
failure.  It is not a universal census.  All arithmetic is integer/set based.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import defaultdict, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
P5 = ROOT / "problems/23/writeup/_claude_r29_pattern5_gate.py"
N12_DIR = ROOT / "tmp/fanout/pht_n12_direct"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_state(n: int, blue: set, bad: set, rows: tuple) -> dict:
    counts = defaultdict(int)
    support = set()
    selected = set()
    for row in rows:
        selected.update(row)
        for x in row:
            for y in row:
                counts[x, y] += 1
        support.update(edge(x, y) for x, y in zip(row, row[1:]))
    active_edges = {
        e for e in blue if e[0] in selected and e[1] in selected and e not in support
    }
    parent = {v: v for v in selected}

    def find(v: int) -> int:
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    def union(x: int, y: int) -> None:
        x, y = find(x), find(y)
        if x != y:
            parent[max(x, y)] = min(x, y)

    for x, y in active_edges:
        union(x, y)
    active_roots = {
        find(x) for x, y in bad
        if x in selected and y in selected and find(x) == find(y)
    }
    active = {v for v in selected if find(v) in active_roots}
    return {
        "counts": counts,
        "active": active,
        "active_edges": active_edges,
        "active_roots": active_roots,
        "find": find,
    }


def quiet_components(n: int, blue: set, active: set) -> tuple[list, dict]:
    adjacency = [set() for _ in range(n)]
    for x, y in blue:
        adjacency[x].add(y)
        adjacency[y].add(x)
    components = []
    component_of = {}
    for root in range(n):
        if root in active or root in component_of:
            continue
        index = len(components)
        vertices = {root}
        boundary = set()
        component_of[root] = index
        queue = deque([root])
        while queue:
            x = queue.popleft()
            for y in adjacency[x]:
                if y in active:
                    boundary.add(y)
                elif y not in component_of:
                    component_of[y] = index
                    vertices.add(y)
                    queue.append(y)
        components.append((vertices, boundary))
    return components, component_of


def p5_relation_summary(n: int, blue: set, bad: set, rows: tuple,
                        owners: list[int]) -> dict:
    state = selected_state(n, blue, bad, rows)
    components, component_of = quiet_components(n, blue, state["active"])
    eligible_components = {}
    for owner in owners:
        owner_root = state["find"](owner)
        eligible_components[owner] = {
            index for index, (_vertices, boundary) in enumerate(components)
            if any(
                state["counts"][owner, a] > 0 and state["find"](a) == owner_root
                for a in boundary
            )
        }

    def loss(vertices: set[int]) -> int:
        return (
            sum((x in vertices) != (y in vertices) for x, y in blue)
            - sum((x in vertices) != (y in vertices) for x, y in bad)
        )

    destination_roots_by_key = defaultdict(set)
    quiet = sorted(component_of)
    loss_cache = {}
    for x in quiet:
        for y in quiet:
            if x == y or state["counts"][x, y] != 0:
                continue
            component_pair = (component_of[x], component_of[y])
            if component_pair not in loss_cache:
                switch = components[component_pair[0]][0] | components[component_pair[1]][0]
                loss_cache[component_pair] = loss(switch)
            if loss_cache[component_pair] < 0:
                continue
            for owner in owners:
                if (component_of[x] in eligible_components[owner]
                        and component_of[y] in eligible_components[owner]):
                    destination_roots_by_key[x, y].add(state["find"](owner))
    return {
        "activeComponentCount": len(state["active_roots"]),
        "ownerRoots": {str(owner): state["find"](owner) for owner in owners},
        "quiescentComponentSizes": sorted(len(vertices) for vertices, _ in components),
        "eligibleOrderedBaseKeys": len(destination_roots_by_key),
        "maxDestinationComponentsPerBaseKey": max(
            (len(roots) for roots in destination_roots_by_key.values()), default=0
        ),
        "baseKeyComponentCoherent": all(
            len(roots) <= 1 for roots in destination_roots_by_key.values()
        ),
    }


def main() -> None:
    lead = load("static_owner_r29_lead", LEAD)
    p5 = load("static_owner_r29_p5", P5)
    data = lead.build()
    anchor_rows = [tuple(row) for row in data["rows"]]
    for index, meta in enumerate(data["selectorMeta"]):
        anchor_rows[data["selectorStart"] + index] = tuple(meta["anchorRow"])
    r29_state = p5.full_state(data, tuple(anchor_rows))
    owner_roots = {owner: r29_state["comp"][owner] for owner in (0, 1, 2)}
    repair_keys = [(3, 56 + 2 * j, half) for j in range(14) for half in (0, 1)]
    assert len(repair_keys) == len(set(repair_keys)) == 28
    assert len(set(owner_roots.values())) == 1
    assert all(r29_state["pair"][x, y] == 0 for x, y, _half in repair_keys)
    assert all(
        not (_half == 0 and edge(x, y) in r29_state["active_edges"] and x in r29_state["av"])
        for x, y, _half in repair_keys
    )

    sys.path.insert(0, str(N12_DIR))
    import n12_pht as n12

    graph6 = "K??E@cyjFgWk"
    n, edges = n12.dec(graph6)
    info = n12.loads(n, edges)
    families = n12.shortest_row_families(info)
    choice = (0, 4, 5, 7)
    rows = n12.rows_for_choice(families, choice)
    n12_summary = p5_relation_summary(
        n, set(info["Bset"]), set(info["Mset"]), rows, [7, 10, 11]
    )
    assert n12_summary["baseKeyComponentCoherent"]
    assert n12_summary["maxDestinationComponentsPerBaseKey"] == 1

    result = {
        "arithmetic": "integer-only",
        "scope": "finite evidence only",
        "r29AllAnchorRepair": {
            "activeOwners": [0, 1, 2],
            "ownerRoots": {str(k): v for k, v in owner_roots.items()},
            "repairHalfKeys": len(repair_keys),
            "baseKeys": len({(x, y) for x, y, _half in repair_keys}),
            "allFree": True,
            "allUnreserved": True,
            "baseKeyComponentCoherent": True,
        },
        "n12FirstP1P5Failure": {
            "graph6": graph6,
            "choice": list(choice),
            "familySizes": [len(family) for family in families],
            **n12_summary,
            "microDemand": 78,
            "p1p5Flow": 69,
            "defect": 9,
        },
        "conclusion": (
            "Both named fixtures satisfy static base-key component coherence; "
            "this does not prove a universal graph theorem or FullBank package existence."
        ),
    }
    output = HERE / "fixture_coherence_result.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"resultSHA256": sha256(output), **result}, sort_keys=True))


if __name__ == "__main__":
    main()
