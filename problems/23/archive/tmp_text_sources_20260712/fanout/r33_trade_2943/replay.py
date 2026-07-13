"""Replay the exact R33 collision-only trade on the 2943-vertex cage.

The two selector tuples are reconstructed from the R29 incidence oracle.  The
relation is the collision-only union P1 same-first, P3 row-companion, strict
P4, and static P5.  HitNeed is reported separately and never enters demand.

The all-local upper bound is the complete three-hub Hall shore.  The matching
lower bounds use literal, exclusive ordered FreeHalf keys and check one active
component per ordered base key.  R32's deterministic integral owner/source
flow supplies the hub assignments.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STRUCTURAL_GATE = ROOT / "problems/23/writeup/_claude_r29_2943_structural_gate.py"
PATTERN5_GATE = ROOT / "problems/23/writeup/_claude_r29_pattern5_gate.py"
D09_VERIFY = ROOT / "tmp/fanout/r29_gate/d09/retry2/verify.py"
R32_DIR = ROOT / "tmp/fanout/r32_n12_fullbank"
R32_FULLBANK = R32_DIR / "fullbank_core.py"
R32_COLLISION = R32_DIR / "collision_only_core.py"
HUBS = (0, 1, 2)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STRUCTURAL = load_module("r33_structural_gate", STRUCTURAL_GATE)
PATTERN5 = load_module("r33_pattern5_gate", PATTERN5_GATE)
D09 = load_module("r33_d09_verify", D09_VERIFY)
sys.path.insert(0, str(R32_DIR))
from fullbank_core import (  # noqa: E402
    canonical_sha,
    decode_source,
    owner_source_flow,
)


Source = tuple[int, int, int]
Obligation = tuple[int, int, int, int]


def norm(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_id(n: int, source: Source) -> int:
    x, y, half = source
    return 2 * (n * x + y) + half


def source_from_id(n: int, value: int) -> Source:
    decoded = tuple(decode_source(n, value))
    assert source_id(n, decoded) == value
    return decoded


def rows_sha(rows: Iterable[Iterable[int]]) -> str:
    return canonical_sha([list(row) for row in rows])


def tuple_descriptors(data: dict) -> tuple[dict, dict, tuple, tuple]:
    n = data["n"]
    start = data["selectorStart"]
    stop = data["selectorStop"]
    base_rows = tuple(tuple(row) for row in data["rows"])
    anchor_rows = list(base_rows)
    adjacency = D09.adj(n, data["blue"])

    local_ids: list[int] = []
    anchor_ids: list[int] = []
    local_ranks: list[int] = []
    anchor_ranks: list[int] = []
    local_rows: list[tuple[int, ...]] = []
    selected_anchor_rows: list[tuple[int, ...]] = []

    for offset, atom in enumerate(data["atoms"][start:stop]):
        family = tuple(D09.shortest(adjacency, *atom))
        assert len(family) == len(set(family)) == 680
        locals_ = tuple(row for row in family if 55 not in row)
        anchors = tuple(row for row in family if 55 in row)
        assert len(locals_) == 4 and len(anchors) == 676

        local = base_rows[start + offset]
        anchor = tuple(data["selectorMeta"][offset]["anchorRow"])
        assert local in locals_ and anchor in anchors
        assert local != anchor
        local_ids.append(family.index(local))
        anchor_ids.append(family.index(anchor))
        local_ranks.append(locals_.index(local))
        anchor_ranks.append(anchors.index(anchor))
        local_rows.append(local)
        selected_anchor_rows.append(anchor)
        anchor_rows[start + offset] = anchor

    anchor_rows_tuple = tuple(anchor_rows)
    full_local_ids = [0] * start + local_ids + [0] * (len(base_rows) - stop)
    full_anchor_ids = [0] * start + anchor_ids + [0] * (len(base_rows) - stop)
    local_exceptions = [
        {
            "selectorIndex": index,
            "globalRowIndex": start + index,
            "familyRowId": local_ids[index],
            "localRank": local_ranks[index],
        }
        for index in range(stop - start)
        if local_ids[index] != 676 or local_ranks[index] != 0
    ]

    local_doc = {
        "name": "canonical-all-local",
        "definition": "constructor baseline data['rows'][selectorStart:selectorStop]",
        "selectorFamilyRowIds": local_ids,
        "selectorLocalRanks": local_ranks,
        "fullFamilyRowIds": full_local_ids,
        "tupleId": canonical_sha(full_local_ids),
        "selectorRowsSha256": rows_sha(local_rows),
        "fullRowsSha256": rows_sha(base_rows),
        "wraparoundExceptionsToUniformLocalRank0": local_exceptions,
    }
    anchor_doc = {
        "name": "canonical-all-anchor",
        "definition": "selectorMeta[j]['anchorRow'] in every selector family",
        "selectorFamilyRowIds": anchor_ids,
        "selectorAnchorRanks": anchor_ranks,
        "fullFamilyRowIds": full_anchor_ids,
        "tupleId": canonical_sha(full_anchor_ids),
        "selectorRowsSha256": rows_sha(selected_anchor_rows),
        "fullRowsSha256": rows_sha(anchor_rows_tuple),
    }

    assert Counter(local_ids) == Counter({676: 674, 679: 2})
    assert local_exceptions == [
        {"selectorIndex": 337, "globalRowIndex": 1013, "familyRowId": 679, "localRank": 3},
        {"selectorIndex": 675, "globalRowIndex": 1351, "familyRowId": 679, "localRank": 3},
    ]
    expected_anchor_ids = list(range(2, 676, 2)) + [1]
    assert anchor_ids == expected_anchor_ids + expected_anchor_ids
    assert sum(a != b for a, b in zip(base_rows, anchor_rows_tuple)) == 676
    return local_doc, anchor_doc, base_rows, anchor_rows_tuple


def row_count(rows: tuple[tuple[int, ...], ...], n: int) -> list[int]:
    out = [0] * n
    for row in rows:
        for vertex in row:
            out[vertex] += 1
    return out


def collision_profile(state: dict, n: int) -> dict[int, int]:
    pair = state["pair"]
    return {
        owner: 2 * sum(max(0, pair[owner, other] - 1) for other in range(n))
        for owner in sorted(state["av"])
    }


def hit_profile(state: dict, rows: tuple[tuple[int, ...], ...], n: int) -> dict[int, int]:
    counts = row_count(rows, n)
    degree = Counter()
    for x, y in state["active_edges"]:
        if x in state["av"]:
            degree[x] += 1
            degree[y] += 1
    return {
        owner: max(0, degree[owner] - max(0, n - 5 * counts[owner]))
        for owner in sorted(state["av"])
    }


def is_reserved(state: dict, source: Source) -> bool:
    x, y, half = source
    return (
        half == 0
        and norm(x, y) in state["active_edges"]
        and x in state["av"]
    )


def signed_data(data: dict) -> tuple[list[int], dict[tuple[int, int], int]]:
    degree = [0] * data["n"]
    sign: dict[tuple[int, int], int] = {}
    for x, y in data["blue"]:
        sign[(x, y)] = 1
        degree[x] += 1
        degree[y] += 1
    for x, y in data["bad"]:
        sign[(x, y)] = -1
        degree[x] -= 1
        degree[y] -= 1
    return degree, sign


def sigma_pair(
    signed_degree: list[int], sign: dict[tuple[int, int], int], x: int, y: int
) -> int:
    return signed_degree[x] + signed_degree[y] - 2 * sign.get(norm(x, y), 0)


def p1_eligible(state: dict, owner: int, source: Source) -> bool:
    x, y, _half = source
    return (
        x == owner
        and x != y
        and state["pair"][x, y] == 0
        and not is_reserved(state, source)
    )


def p3_eligible(
    state: dict,
    owner: int,
    source: Source,
    signed_degree: list[int],
    sign: dict[tuple[int, int], int],
) -> bool:
    x, y, _half = source
    return (
        x != y
        and state["pair"][owner, x] > 0
        and state["pair"][owner, y] > 0
        and state["pair"][x, y] == 0
        and sigma_pair(signed_degree, sign, x, y) >= 0
        and not is_reserved(state, source)
    )


def rebuild_hub_p13(
    data: dict,
    state: dict,
    signed_degree: list[int],
    sign: dict[tuple[int, int], int],
) -> tuple[dict[Source, int], dict[Source, int], dict[Source, int]]:
    n = data["n"]
    p1: dict[Source, int] = {}
    p3: dict[Source, int] = {}
    for owner in HUBS:
        bit = 1 << owner
        for y in range(n):
            for half in (0, 1):
                source = (owner, y, half)
                if p1_eligible(state, owner, source):
                    p1[source] = p1.get(source, 0) | bit
        companions = [x for x in range(n) if state["pair"][owner, x] > 0]
        for x in companions:
            for y in companions:
                for half in (0, 1):
                    source = (x, y, half)
                    if p3_eligible(state, owner, source, signed_degree, sign):
                        p3[source] = p3.get(source, 0) | bit
    union = dict(p1)
    for source, mask in p3.items():
        union[source] = union.get(source, 0) | mask
    return p1, p3, union


def blue_adjacency(data: dict) -> list[set[int]]:
    adjacency = [set() for _ in range(data["n"])]
    for x, y in data["blue"]:
        adjacency[x].add(y)
        adjacency[y].add(x)
    return adjacency


def attachment_audit(
    data: dict,
    state: dict,
    *,
    allowed: set[int],
    boundary_vertices: set[int],
    owners: tuple[int, ...],
) -> dict:
    adjacency = blue_adjacency(data)
    component_of: dict[int, int] = {}
    components: list[frozenset[int]] = []
    boundaries: list[frozenset[int]] = []
    masks: list[int] = []

    for root in sorted(allowed):
        if root in component_of:
            continue
        cid = len(components)
        seen = {root}
        component_of[root] = cid
        queue = deque([root])
        while queue:
            x = queue.popleft()
            for y in adjacency[x]:
                if y in allowed and y not in seen:
                    seen.add(y)
                    component_of[y] = cid
                    queue.append(y)
        boundary = {
            y for x in seen for y in adjacency[x] if y in boundary_vertices
        }
        mask = 0
        for index, owner in enumerate(owners):
            if any(
                state["pair"][owner, a] > 0
                and state["comp"].get(a) == state["comp"].get(owner)
                for a in boundary
            ):
                mask |= 1 << index
        components.append(frozenset(seen))
        boundaries.append(frozenset(boundary))
        masks.append(mask)

    loss_cache: dict[tuple[int, int], int] = {}

    def switch_loss(left: int, right: int) -> int:
        key = (min(left, right), max(left, right))
        if key not in loss_cache:
            switched = components[left] | components[right]
            blue_cut = sum((x in switched) != (y in switched) for x, y in data["blue"])
            bad_cut = sum((x in switched) != (y in switched) for x, y in data["bad"])
            loss_cache[key] = blue_cut - bad_cut
        return loss_cache[key]

    return {
        "componentOf": component_of,
        "components": components,
        "boundaries": boundaries,
        "masks": masks,
        "switchLoss": switch_loss,
    }


def attachment_key_mask(state: dict, audit: dict, source: Source) -> int:
    x, y, _half = source
    if x == y or x not in audit["componentOf"] or y not in audit["componentOf"]:
        return 0
    if state["pair"][x, y] != 0 or is_reserved(state, source):
        return 0
    left = audit["componentOf"][x]
    right = audit["componentOf"][y]
    mask = audit["masks"][left] & audit["masks"][right]
    if not mask or audit["switchLoss"](left, right) < 0:
        return 0
    return mask


def hall_cuts(demand: tuple[int, ...], relation: dict[int, int]) -> list[dict]:
    out = []
    for shore in range(1, 1 << len(demand)):
        shore_demand = sum(
            amount for index, amount in enumerate(demand) if shore & (1 << index)
        )
        reach = sum(bool(mask & shore) for mask in relation.values())
        out.append(
            {
                "shoreMask": shore,
                "owners": [
                    HUBS[index]
                    for index in range(len(HUBS))
                    if shore & (1 << index)
                ],
                "demand": shore_demand,
                "reach": reach,
                "defect": max(0, shore_demand - reach),
                "signedGap": shore_demand - reach,
            }
        )
    return out


def collision_obligations(state: dict, owner: int, n: int) -> list[Obligation]:
    obligations: list[Obligation] = []
    for other in range(n):
        for copy in range(max(0, state["pair"][owner, other] - 1)):
            for half in (0, 1):
                obligations.append((owner, other, copy, half))
    return obligations


def matching_certificate(
    data: dict,
    state: dict,
    collision: dict[int, int],
    hub_flow,
    p1_masks: dict[Source, int],
    p3_masks: dict[Source, int],
    p5_masks: dict[Source, int],
    signed_degree: list[int],
    sign: dict[tuple[int, int], int],
) -> dict:
    n = data["n"]
    owners = tuple(owner for owner in sorted(state["av"]) if collision[owner] > 0)
    assigned: dict[int, list[Source]] = {owner: [] for owner in owners}
    pattern_of: dict[tuple[int, Source], str] = {}
    used: set[Source] = set()
    base_component: dict[tuple[int, int], int] = {}

    def add(owner: int, source: Source, pattern: str) -> bool:
        if source in used or is_reserved(state, source):
            return False
        component = state["comp"][owner]
        base = source[:2]
        if base in base_component and base_component[base] != component:
            return False
        if pattern == "P1":
            assert p1_eligible(state, owner, source)
        elif pattern == "P3":
            assert p3_eligible(state, owner, source, signed_degree, sign)
        elif pattern == "P5":
            owner_bit = 1 << HUBS.index(owner)
            assert p5_masks.get(source, 0) & owner_bit
        else:
            raise AssertionError(pattern)
        used.add(source)
        base_component[base] = component
        assigned[owner].append(source)
        pattern_of[owner, source] = pattern
        return True

    for encoded, owner_index in hub_flow.assignment:
        owner = HUBS[owner_index]
        source = source_from_id(n, encoded)
        bit = 1 << owner
        if p5_masks.get(source, 0) & bit:
            pattern = "P5"
        elif p1_masks.get(source, 0) & bit:
            pattern = "P1"
        else:
            assert p3_masks.get(source, 0) & bit
            pattern = "P3"
        assert add(owner, source, pattern)

    def fill_nonhub(owner: int) -> None:
        needed = collision[owner]
        for y in range(n):
            for half in (0, 1):
                if len(assigned[owner]) == needed:
                    return
                source = (owner, y, half)
                if p1_eligible(state, owner, source):
                    add(owner, source, "P1")
        companions = [x for x in range(n) if state["pair"][owner, x] > 0]
        for x in companions:
            for y in companions:
                for half in (0, 1):
                    if len(assigned[owner]) == needed:
                        return
                    source = (x, y, half)
                    if p3_eligible(state, owner, source, signed_degree, sign):
                        add(owner, source, "P3")
        raise AssertionError(
            f"owner {owner} has {len(assigned[owner])} sources for demand {needed}"
        )

    for owner in owners:
        if owner not in HUBS:
            fill_nonhub(owner)

    records: list[list[int]] = []
    unmatched: list[list[int]] = []
    per_owner_assigned: dict[str, int] = {}
    pattern_counts = Counter()
    for owner in owners:
        obligations = collision_obligations(state, owner, n)
        assert len(obligations) == collision[owner]
        sources = sorted(assigned[owner])
        per_owner_assigned[str(owner)] = len(sources)
        for obligation, source in zip(obligations, sources):
            component = state["comp"][owner]
            records.append([*obligation, *source, component])
            pattern_counts[pattern_of[owner, source]] += 1
        unmatched.extend([list(item) for item in obligations[len(sources) :]])

    assert len(records) == len(used)
    assert len({tuple(record[4:7]) for record in records}) == len(records)
    labels_from_records: dict[tuple[int, int], set[int]] = defaultdict(set)
    for record in records:
        labels_from_records[record[4], record[5]].add(record[7])
    assert all(len(components) == 1 for components in labels_from_records.values())
    assert all(not is_reserved(state, tuple(record[4:7])) for record in records)

    return {
        "matched": len(records),
        "unmatchedObligations": unmatched,
        "assignmentDigestDefinition": (
            "SHA256 canonical JSON of sorted [owner,other,copy,obligationHalf,"
            "sourceX,sourceY,sourceHalf,activeComponent] records"
        ),
        "assignmentSha256": canonical_sha(records),
        "physicalSourceSha256": canonical_sha(sorted([list(source) for source in used])),
        "baseComponentLabelsSha256": canonical_sha(
            sorted([x, y, component] for (x, y), component in base_component.items())
        ),
        "exclusivePhysicalKeyCount": len(used),
        "coherentOrderedBaseKeyCount": len(base_component),
        "activeComponentsUsed": sorted(set(base_component.values())),
        "assignedByOwner": per_owner_assigned,
        "assignedByPattern": dict(sorted(pattern_counts.items())),
    }


def analyze_tuple(
    name: str,
    data: dict,
    rows: tuple[tuple[int, ...], ...],
    tuple_doc: dict,
    signed_degree: list[int],
    sign: dict[tuple[int, int], int],
) -> dict:
    n = data["n"]
    state = PATTERN5.full_state(data, rows)
    collision = collision_profile(state, n)
    hit_need = hit_profile(state, rows, n)
    collision_owners = tuple(
        owner for owner in sorted(state["av"]) if collision[owner] > 0
    )
    assert {state["comp"][owner] for owner in collision_owners} == {0}
    for owner in HUBS:
        assert state["demand"][owner] == collision[owner] + hit_need[owner]

    p1, p3, p13 = rebuild_hub_p13(data, state, signed_degree, sign)
    assert p13 == state["masks"]
    p13_encoded = {source_id(n, source): mask for source, mask in p13.items()}
    p4 = attachment_audit(
        data,
        state,
        allowed=set(range(n)) - state["selected"],
        boundary_vertices=set(state["selected"]),
        owners=HUBS,
    )
    p5 = attachment_audit(
        data,
        state,
        allowed=set(range(n)) - state["av"],
        boundary_vertices=set(state["av"]),
        owners=HUBS,
    )
    p4_eligible = [sum(bool(mask & (1 << index)) for mask in p4["masks"]) for index in range(3)]
    p5_eligible = [sum(bool(mask & (1 << index)) for mask in p5["masks"]) for index in range(3)]

    p5_masks: dict[Source, int] = {}
    relation = dict(p13_encoded)
    if name == "all-local":
        assert p4_eligible == [0, 0, 0]
        assert p5_eligible == [0, 0, 0]
    elif name == "all-anchor":
        static_gate = PATTERN5.p5_at(data, rows, verbose=False)
        assert not static_gate["leaf_active"]
        assert static_gate["K"] == 1379
        assert static_gate["boundary"] == [1, 55]
        assert static_gate["xs_ok"] and static_gate["free_ok"]
        assert all(static_gate["elig"].values())
        assert static_gate["disjoint"] and static_gate["unreserved"]
        assert static_gate["loss"] == 26
        for x in (56 + 2 * index for index in range(14)):
            for half in (0, 1):
                source = (3, x, half)
                mask = attachment_key_mask(state, p5, source)
                assert mask == 7
                assert source not in p13
                p5_masks[source] = mask
                relation[source_id(n, source)] = mask
        assert len(p5_masks) == 28
    else:
        raise AssertionError(name)

    hub_demand = tuple(collision[owner] for owner in HUBS)
    flow = owner_source_flow(hub_demand, relation)
    cuts = hall_cuts(hub_demand, relation)
    matching = matching_certificate(
        data,
        state,
        collision,
        flow,
        p1,
        p3,
        p5_masks,
        signed_degree,
        sign,
    )
    demand_total = sum(collision.values())
    defect = demand_total - matching["matched"]
    if name == "all-local":
        full_shore = next(cut for cut in cuts if cut["shoreMask"] == 7)
        assert full_shore == {
            "shoreMask": 7,
            "owners": [0, 1, 2],
            "demand": 19950,
            "reach": 19925,
            "defect": 25,
            "signedGap": 25,
        }
        assert max(cut["defect"] for cut in cuts) == 25
        assert flow.value == 19925
        assert defect == 25
        maximality = (
            "hub shore has collision demand 19950 and complete P1/P3/P4/P5 "
            "physical reach 19925; coherent assignment attains total demand minus 25"
        )
    else:
        assert all(cut["defect"] == 0 for cut in cuts)
        assert flow.value == sum(hub_demand) == 19950
        assert defect == 0
        maximality = "exclusive coherent assignment saturates every collision obligation"

    relation_histogram = Counter(relation.values())
    state_assertions = {
        "allCollisionOwnersInOneActiveComponent": True,
        "baseKeyComponentCoherent": matching["activeComponentsUsed"] == [0],
        "exclusivePhysicalKeys": matching["exclusivePhysicalKeyCount"] == matching["matched"],
        "hitNeedExcludedFromDemand": True,
        "halfZeroReservationsExcluded": True,
        "p13MatchesIndependentR29Gate": p13 == state["masks"],
        "maximumProvedExactly": True,
    }
    assert all(state_assertions.values())

    return {
        **tuple_doc,
        "selectedVertices": len(state["selected"]),
        "activeVertices": len(state["av"]),
        "collisionOwners": list(collision_owners),
        "collisionDemand": demand_total,
        "collisionDemandByOwner": {
            str(owner): collision[owner] for owner in collision_owners
        },
        "hallDemandIncludesHitNeed": False,
        "hitNeedTypedBankSinkMetadata": {
            "total": sum(hit_need.values()),
            "byOwner": {
                str(owner): amount
                for owner, amount in hit_need.items()
                if amount > 0
            },
        },
        "maximumCoherentMatchingSize": matching["matched"],
        "collisionDefect": defect,
        "unmatchedObligations": matching.pop("unmatchedObligations"),
        "assignment": matching,
        "maximalityCertificate": maximality,
        "hubHallCuts": cuts,
        "relationAudit": {
            "relation": ["P1_sameFirst", "P3_rowCompanion", "strictP4", "staticP5"],
            "commonBlueIncluded": False,
            "p2Included": False,
            "p13PhysicalKeyHistogramByOwnerMask": {
                str(mask): count for mask, count in sorted(Counter(p13.values()).items())
            },
            "selectedStaticP5Keys": [list(source) for source in sorted(p5_masks)],
            "selectedStaticP5KeyCount": len(p5_masks),
            "hubUnionPhysicalKeyHistogramByOwnerMask": {
                str(mask): count for mask, count in sorted(relation_histogram.items())
            },
            "strictP4EligibleComponentCountByHub": dict(zip(map(str, HUBS), p4_eligible)),
            "staticP5EligibleComponentCountByHub": dict(zip(map(str, HUBS), p5_eligible)),
        },
        "assertions": state_assertions,
    }


def build_certificate() -> dict:
    data = STRUCTURAL.load()
    assert data["n"] == 2943
    assert len(data["blue"]) == 7039
    assert len(data["bad"]) == 1383
    assert data["selectorStart"] == 676 and data["selectorStop"] == 1352

    local_doc, anchor_doc, local_rows, anchor_rows = tuple_descriptors(data)
    signed_degree, sign = signed_data(data)
    local = analyze_tuple(
        "all-local", data, local_rows, local_doc, signed_degree, sign
    )
    anchor = analyze_tuple(
        "all-anchor", data, anchor_rows, anchor_doc, signed_degree, sign
    )

    assert local["collisionDemand"] == 30808
    assert local["maximumCoherentMatchingSize"] == 30783
    assert len(local["unmatchedObligations"]) == 25
    assert anchor["collisionDemand"] == 23108
    assert anchor["maximumCoherentMatchingSize"] == 23108
    assert anchor["unmatchedObligations"] == []

    source_paths = (
        STRUCTURAL_GATE,
        PATTERN5_GATE,
        D09_VERIFY,
        R32_FULLBANK,
        R32_COLLISION,
        Path(__file__).resolve(),
    )
    source_hashes = {
        str(path.relative_to(ROOT)).replace("\\", "/"): file_sha256(path)
        for path in source_paths
    }
    return {
        "schema": "r33-trade-2943-collision-certificate-v1",
        "arithmetic": "exact integer and finite-set operations only",
        "tupleIdConvention": (
            "zero-based index in D09's lexicographically enumerated oriented "
            "shortest-row family; rigid singleton families have ID 0"
        ),
        "graph": {
            "n": data["n"],
            "blueEdges": len(data["blue"]),
            "badEdges": len(data["bad"]),
            "rowFamilies": len(data["atoms"]),
            "selectorStartInclusive": data["selectorStart"],
            "selectorStopExclusive": data["selectorStop"],
            "selectorFamilies": data["selectorStop"] - data["selectorStart"],
            "canonicalIncidenceSha256": "fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f",
        },
        "model": {
            "demand": "active-scoped collision halves only",
            "relation": ["P1_sameFirst", "P3_rowCompanion", "strictP4", "staticP5"],
            "sourceCapacity": "one per ordered physical FreeHalf key (x,y,half)",
            "baseCoherence": "at most one active destination component per ordered base (x,y)",
            "hitNeed": "excluded from collision defect; retained only as typed bank-sink metadata",
        },
        "tuples": {
            "allLocal": local,
            "allAnchor": anchor,
        },
        "trade": {
            "changedSelectorRows": 676,
            "changedGlobalRowInterval": [676, 1352],
            "statedLabel": "28->0",
            "exactCollisionOnlyDefects": [25, 0],
            "statedLabelAccurateUnderRequestedTyping": False,
            "reason": (
                "the historical 28 counted three hub HitNeed units; collision-only "
                "demand is 19950 at the deficient hub shore, so its exact deficit is 25"
            ),
            "strictDefectDecrease": 25,
        },
        "sourceSha256": source_hashes,
        "assertions": {
            "canonicalTupleIdsReconstructed": True,
            "allLocalMaximumExact": True,
            "allAnchorMaximumExact": True,
            "exclusivePhysicalKeysBothEndpoints": True,
            "baseKeyComponentCoherentBothEndpoints": True,
            "hitNeedNeverIncludedInCollisionDemand": True,
            "advertised28To0CorrectedTo25To0": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=HERE / "certificate_replay.json"
    )
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    certificate = build_certificate()
    if args.verify is not None:
        existing = json.loads(args.verify.read_text(encoding="ascii"))
        assert existing == certificate
        output_path = args.verify
        mode = "verified"
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(certificate, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
            encoding="ascii",
        )
        output_path = args.output
        mode = "written"

    summary = {
        "mode": mode,
        "certificate": str(output_path.resolve()),
        "certificateSha256": file_sha256(output_path),
        "allLocal": {
            "demand": certificate["tuples"]["allLocal"]["collisionDemand"],
            "matched": certificate["tuples"]["allLocal"]["maximumCoherentMatchingSize"],
            "defect": certificate["tuples"]["allLocal"]["collisionDefect"],
        },
        "allAnchor": {
            "demand": certificate["tuples"]["allAnchor"]["collisionDemand"],
            "matched": certificate["tuples"]["allAnchor"]["maximumCoherentMatchingSize"],
            "defect": certificate["tuples"]["allAnchor"]["collisionDefect"],
        },
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
