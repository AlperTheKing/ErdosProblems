"""Exact R29 audit of the API-licensed common-blue c5Base terminal.

All arithmetic is integral.  The output gives a minimum 28-FreeHalf absorber
for the all-anchor owner shore and an explicit deterministic injective flow.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
EXPECTED_CANONICAL_SHA256 = (
    "fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f"
)
OWNERS = (0, 1, 2)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def load_incidence() -> tuple[object, dict]:
    spec = importlib.util.spec_from_file_location("r29_lead", LEAD)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    data = module.build()
    assert sha256_bytes(module.canonical_bytes(data)) == EXPECTED_CANONICAL_SHA256
    return module, data


def all_anchor_rows(data: dict) -> tuple[tuple[int, ...], ...]:
    rows = list(data["rows"])
    for j, meta in enumerate(data["selectorMeta"]):
        rows[data["selectorStart"] + j] = tuple(meta["anchorRow"])
    return tuple(rows)


def selected_state(data: dict, rows: tuple[tuple[int, ...], ...]) -> dict:
    pair = Counter()
    row_count = Counter()
    support: set[tuple[int, int]] = set()
    selected: set[int] = set()
    for row in rows:
        selected.update(row)
        row_count.update(row)
        pair.update((x, y) for x in row for y in row)
        support.update(edge(x, y) for x, y in zip(row, row[1:]))

    active_edges = {
        e for e in data["blue"]
        if e not in support and e[0] in selected and e[1] in selected
    }
    adj: dict[int, set[int]] = defaultdict(set)
    for u, v in active_edges:
        adj[u].add(v)
        adj[v].add(u)
    component: dict[int, int] = {}
    components: list[set[int]] = []
    for root in sorted(selected):
        if root in component:
            continue
        seen = {root}
        todo = deque([root])
        while todo:
            u = todo.popleft()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    todo.append(v)
        cid = len(components)
        components.append(seen)
        for v in seen:
            component[v] = cid
    bad_components = {
        component[u] for u, v in data["bad"]
        if u in component and v in component and component[u] == component[v]
    }
    active_vertices = {
        v for v in selected if component[v] in bad_components
    }
    demanded_active_edges = {
        e for e in active_edges if e[0] in active_vertices
    }
    active_degree = Counter()
    for u, v in demanded_active_edges:
        active_degree[u] += 1
        active_degree[v] += 1
    collision = {
        v: 2 * sum(max(0, pair[v, y] - 1) for y in range(data["n"]))
        for v in active_vertices
    }
    hit_need = {
        v: max(
            0,
            active_degree[v] - max(0, data["n"] - 5 * row_count[v]),
        )
        for v in active_vertices
    }
    return {
        "pair": pair,
        "row_count": row_count,
        "support": support,
        "selected": selected,
        "active_edges": active_edges,
        "active_vertices": active_vertices,
        "demanded_active_edges": demanded_active_edges,
        "collision": collision,
        "hit_need": hit_need,
    }


def cut_data(data: dict) -> tuple[Counter, dict[tuple[int, int], int], dict[int, set[int]]]:
    signed_degree = Counter()
    sign: dict[tuple[int, int], int] = {}
    blue_neighbors: dict[int, set[int]] = defaultdict(set)
    for u, v in data["blue"]:
        sign[(u, v)] = 1
        signed_degree[u] += 1
        signed_degree[v] += 1
        blue_neighbors[u].add(v)
        blue_neighbors[v].add(u)
    for u, v in data["bad"]:
        sign[(u, v)] = -1
        signed_degree[u] -= 1
        signed_degree[v] -= 1
    return signed_degree, sign, blue_neighbors


def sigma_pair(
    x: int,
    y: int,
    signed_degree: Counter,
    sign: dict[tuple[int, int], int],
) -> int:
    """Exact dB({x,y}) - dM({x,y})."""
    return signed_degree[x] + signed_degree[y] - 2 * sign.get(edge(x, y), 0)


def current_source_masks(data: dict, state: dict) -> dict[tuple[int, int, int], int]:
    pair = state["pair"]
    active_edges = state["active_edges"]
    active_vertices = state["active_vertices"]
    signed_degree, sign, _ = cut_data(data)
    companions = {
        owner: {x for x in range(data["n"]) if pair[owner, x] > 0}
        for owner in OWNERS
    }
    masks: dict[tuple[int, int, int], int] = {}
    for owner in OWNERS:
        for y in range(data["n"]):
            if y == owner or pair[owner, y] != 0:
                continue
            for half in (0, 1):
                reserved = (
                    half == 0
                    and edge(owner, y) in active_edges
                    and owner in active_vertices
                )
                if not reserved:
                    key = (owner, y, half)
                    masks[key] = masks.get(key, 0) | (1 << owner)
        for x in companions[owner]:
            for y in companions[owner]:
                if x == y or pair[x, y] != 0:
                    continue
                if sigma_pair(x, y, signed_degree, sign) < 0:
                    continue
                for half in (0, 1):
                    reserved = (
                        half == 0
                        and edge(x, y) in active_edges
                        and x in active_vertices
                    )
                    if not reserved:
                        key = (x, y, half)
                        masks[key] = masks.get(key, 0) | (1 << owner)
    return masks


def c5base_source_masks(data: dict, state: dict) -> tuple[dict, list[dict]]:
    """Enumerate CheckedC5BaseTransfer.Valid plus FreeHalf/unreserved fields."""
    pair = state["pair"]
    active_edges = state["active_edges"]
    active_vertices = state["active_vertices"]
    signed_degree, sign, blue_neighbors = cut_data(data)
    masks: dict[tuple[int, int, int], int] = {}
    terminals: list[dict] = []
    for owner in OWNERS:
        for x in sorted(blue_neighbors[owner]):
            for y in sorted(blue_neighbors[owner]):
                if x == y or pair[x, y] != 0:
                    continue
                sigma = sigma_pair(x, y, signed_degree, sign)
                if sigma < 2:
                    continue
                for half in (0, 1):
                    if (
                        half == 0
                        and edge(x, y) in active_edges
                        and x in active_vertices
                    ):
                        continue
                    key = (x, y, half)
                    masks[key] = masks.get(key, 0) | (1 << owner)
                    terminals.append({
                        "owner": owner,
                        "source": list(key),
                        "dBMinusDM": sigma,
                        "adjustedSurplus": sigma - 2,
                    })
    return masks, terminals


def owner_cuts(masks: dict[tuple[int, int, int], int], demand: dict[int, int]) -> list[dict]:
    cuts = []
    for shore_mask in range(8):
        shore = [o for o in OWNERS if shore_mask & (1 << o)]
        d = sum(demand[o] for o in shore)
        reach = sum(1 for mask in masks.values() if mask & shore_mask)
        cuts.append({
            "shoreMask": shore_mask,
            "shore": shore,
            "demand": d,
            "reach": reach,
            "margin": reach - d,
        })
    return cuts


def main() -> None:
    module, data = load_incidence()
    rows = all_anchor_rows(data)
    state = selected_state(data, rows)
    demand = {
        o: state["collision"].get(o, 0) + state["hit_need"].get(o, 0)
        for o in OWNERS
    }
    assert demand == {0: 6651, 1: 6651, 2: 6651}

    base = current_source_masks(data, state)
    assert len(base) == 19925
    base_cuts = owner_cuts(base, demand)
    assert base_cuts[7] == {
        "shoreMask": 7,
        "shore": [0, 1, 2],
        "demand": 19953,
        "reach": 19925,
        "margin": -28,
    }

    c5_masks, terminals = c5base_source_masks(data, state)
    combined_all = dict(base)
    for key, mask in c5_masks.items():
        combined_all[key] = combined_all.get(key, 0) | mask
    new_keys = {key for key in combined_all if key not in base}
    upgraded_keys = {
        key for key in base if combined_all.get(key, base[key]) != base[key]
    }
    assert len(c5_masks) == 2824
    assert len(new_keys) == 216
    assert len(upgraded_keys) == 8
    assert all(cut["margin"] >= 0 for cut in owner_cuts(combined_all, demand))

    # Minimum absorber: fourteen common-blue pairs, both FreeHalf bits each.
    absorber_keys = [(x, 2930, half) for x in range(29, 43) for half in (0, 1)]
    assert len(absorber_keys) == 28 and len(set(absorber_keys)) == 28
    signed_degree, sign, blue_neighbors = cut_data(data)
    for x, y, half in absorber_keys:
        assert x in blue_neighbors[2] and y in blue_neighbors[2]
        assert x != y and state["pair"][x, y] == 0
        assert sigma_pair(x, y, signed_degree, sign) == 3
        assert edge(x, y) not in state["active_edges"]
        assert (x, y, half) not in base
        assert c5_masks[x, y, half] & (1 << 2)

    repaired = dict(base)
    for key in absorber_keys:
        repaired[key] = repaired.get(key, 0) | (1 << 2)
    repaired_cuts = owner_cuts(repaired, demand)
    assert all(cut["margin"] >= 0 for cut in repaired_cuts)
    assert repaired_cuts[7]["margin"] == 0

    # Deterministic complete assignment.  It uses every repaired source once.
    by_mask: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for key, mask in repaired.items():
        by_mask[mask].append(key)
    for keys in by_mask.values():
        keys.sort()
    assert {mask: len(keys) for mask, keys in by_mask.items()} == {
        1: 5775,
        2: 5775,
        4: 5803,
        7: 2600,
    }
    assignment: list[tuple[tuple[int, int, int], int]] = []
    assignment.extend((key, 0) for key in by_mask[1])
    assignment.extend((key, 1) for key in by_mask[2])
    assignment.extend((key, 2) for key in by_mask[4])
    assignment.extend((key, 0) for key in by_mask[7][:876])
    assignment.extend((key, 1) for key in by_mask[7][876:1752])
    assignment.extend((key, 2) for key in by_mask[7][1752:])
    assert len(assignment) == 19953
    assert len({key for key, _ in assignment}) == 19953
    assert Counter(owner for _, owner in assignment) == Counter(demand)
    assert all(repaired[key] & (1 << owner) for key, owner in assignment)
    assignment_raw = json.dumps(
        [[*key, owner] for key, owner in assignment],
        separators=(",", ":"),
    ).encode()

    certificate = {
        "input": {
            "canonicalSha256": EXPECTED_CANONICAL_SHA256,
            "leadFileSha256": sha256_bytes(LEAD.read_bytes()),
            "n": data["n"],
            "blue": len(data["blue"]),
            "bad": len(data["bad"]),
            "rows": len(rows),
        },
        "scope": {
            "selectedVertices": len(state["selected"]),
            "activeVertices": len(state["active_vertices"]),
            "activeEdges": len(state["active_edges"]),
            "demandedActiveEdges": len(state["demanded_active_edges"]),
        },
        "baseline": {
            "demandByOwner": demand,
            "sourceCount": len(base),
            "cuts": base_cuts,
        },
        "fullC5BaseAudit": {
            "validOwnerTerminalHalfInstances": len(terminals),
            "uniqueKeys": len(c5_masks),
            "newKeys": len(new_keys),
            "upgradedKeys": len(upgraded_keys),
            "combinedSourceCount": len(combined_all),
        },
        "minimumAbsorber": {
            "owner": 2,
            "pairCount": 14,
            "halfSlotCount": 28,
            "pairs": [[x, 2930] for x in range(29, 43)],
            "sources": [list(key) for key in absorber_keys],
            "dBMinusDMEach": 3,
            "adjustedSurplusEach": 1,
            "sourceKeysDistinct": True,
            "repairedCuts": repaired_cuts,
            "minimalityLowerBound": "baseline full-shore defect is 28 and each key has unit half-slot capacity",
        },
        "flow": {
            "sourceHistogramByOwnerMask": {
                str(mask): len(keys) for mask, keys in sorted(by_mask.items())
            },
            "sharedMaskAllocation": {"owner0": 876, "owner1": 876, "owner2": 848},
            "assignedSourceCount": len(assignment),
            "assignmentSha256": sha256_bytes(assignment_raw),
            "injective": True,
            "allAssignmentsEligible": True,
        },
        "smallestStatement": (
            "On the canonical N=2943 all-anchor R29 tuple, extending Available by "
            "CheckedC5BaseTransfer.Valid admits an injective matching; 28 new FreeHalf "
            "keys are necessary and sufficient, witnessed by (x,2930,h) for "
            "29<=x<=42 and h in {0,1}.  Assigning them to collision demands "
            "creates no FullBank token spend."
        ),
    }
    raw = json.dumps(certificate, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    out = HERE / "r29_c5base_absorber.json"
    out.write_bytes(raw)
    print(json.dumps({
        "certificate": str(out.relative_to(ROOT)),
        "certificateSha256": sha256_bytes(raw),
        "assignmentSha256": certificate["flow"]["assignmentSha256"],
        "baselineDefect": 28,
        "newC5BaseKeys": len(new_keys),
        "absorberHalfSlots": len(absorber_keys),
        "repairedFullShoreMargin": repaired_cuts[7]["margin"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
