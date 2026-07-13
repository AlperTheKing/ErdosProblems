"""Exact-integer helpers for the concrete R33 2943 selector trade.

The graph and rows come from the canonical R29 reconstruction.  Pattern
membership comes from the pinned R32 P5 implementation, and coherent matching
uses the R32 full-bank matcher with common-blue terminals disabled.
"""

from __future__ import annotations

import gc
import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAD_PATH = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
STRUCTURAL_GATE_PATH = (
    ROOT / "problems/23/writeup/_claude_r29_2943_structural_gate.py"
)
PATTERN5_GATE_PATH = ROOT / "problems/23/writeup/_claude_r29_pattern5_gate.py"
P5_CORE_PATH = ROOT / "tmp/fanout/p5_n12_census/p5_core.py"
FULLBANK_CORE_PATH = ROOT / "tmp/fanout/r32_n12_fullbank/fullbank_core.py"
COLLISION_CORE_PATH = (
    ROOT / "tmp/fanout/r32_n12_fullbank/collision_only_core.py"
)
JOIN_GATE_PATH = ROOT / "tmp/fanout/r32_join5886/independent_gate.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Reuse the join gate's canonical JSON and SHA routines.  Its coherent
# assignment schema is also the source of the ordered-base/component convention.
join_gate = load_module("r33_join_reference", JOIN_GATE_PATH)
json_bytes = join_gate.json_bytes
sha256_file = join_gate.sha256_file

sys.path.insert(0, str(P5_CORE_PATH.parent))
sys.path.insert(0, str(FULLBANK_CORE_PATH.parent))
import p5_core as p5  # noqa: E402
import fullbank_core as fullbank  # noqa: E402


PATTERN_P1 = 1
PATTERN_P3 = 2
PATTERN_P4 = 4
PATTERN_P5 = 8
ASSIGNMENT_COLUMNS = [
    "obligationOwner",
    "obligationOther",
    "obligationCopy",
    "obligationHalf",
    "sourceX",
    "sourceY",
    "sourceHalf",
    "destinationComponentRoot",
    "eligiblePatternMask",
]
OBLIGATION_COLUMNS = ["owner", "other", "copy", "half"]


def sha256_json(value: object) -> str:
    return hashlib.sha256(json_bytes(value)).hexdigest()


def load_lead():
    return load_module("r33_canonical_r29_lead", LEAD_PATH)


def canonical_incidence_sha(data: dict) -> str:
    payload = {
        "n": data["n"],
        "blue": sorted(data["blue"]),
        "bad": sorted(data["bad"]),
        "side": tuple(data["side"]),
        "rows": tuple(tuple(row) for row in data["rows"]),
        "selector_anchor_rows": [m["anchorRow"] for m in data["selectorMeta"]],
        "selector_start": data["selectorStart"],
    }
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=list,
    ).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def endpoint_rows(data: dict) -> dict[str, tuple[tuple[int, ...], ...]]:
    baseline = tuple(tuple(row) for row in data["rows"])
    anchor = list(baseline)
    for family, meta in enumerate(data["selectorMeta"]):
        anchor[data["selectorStart"] + family] = tuple(meta["anchorRow"])
    return {
        "baselineLocal": baseline,
        "metadataAnchor": tuple(anchor),
    }


def selector_choice_catalog(
    lead, data: dict, endpoints: dict[str, tuple[tuple[int, ...], ...]]
) -> dict:
    """Return zero-based lexicographic row IDs for all 676 selector families."""
    adj = lead.adjacency(data["n"], data["blue"])
    start, stop = data["selectorStart"], data["selectorStop"]
    choice_ids = {name: [] for name in endpoints}
    kind_counts = {
        name: {"local": 0, "anchor": 0} for name in endpoints
    }
    catalog_hash = hashlib.sha256()
    for family, atom in enumerate(data["atoms"][start:stop]):
        rows = lead.shortest_rows(adj, *atom)
        if len(rows) != 680 or len(set(rows)) != 680:
            raise AssertionError(f"selector family {family} is not a 680-row set")
        catalog_hash.update(str(len(rows)).encode("ascii"))
        catalog_hash.update(b":")
        catalog_hash.update(json_bytes(rows))
        catalog_hash.update(b"\n")
        row_id = {row: index for index, row in enumerate(rows)}
        for name, tuple_rows in endpoints.items():
            row = tuple_rows[start + family]
            if row not in row_id:
                raise AssertionError(f"{name} family {family} row is not canonical")
            choice_ids[name].append(row_id[row])
            kind_counts[name]["anchor" if 55 in row else "local"] += 1
    return {
        "choiceIdDefinition": (
            "zero-based index in the lexicographically sorted complete shortest-row "
            "family"
        ),
        "selectorStartAtomIndex": start,
        "selectorStopAtomIndexExclusive": stop,
        "selectorFamilies": stop - start,
        "rowsPerSelectorFamily": 680,
        "catalogSha256": catalog_hash.hexdigest(),
        "catalogDigestEncoding": "sha256 of repeated decimal-count ':' canonical-json '\\n'",
        "choiceIds": choice_ids,
        "kindCounts": kind_counts,
    }


def component_roots(state: p5.TupleState) -> dict[int, int]:
    members: dict[int, list[int]] = defaultdict(list)
    for vertex in state.selected:
        members[state.selected_comp[vertex]].append(vertex)
    return {component: min(vertices) for component, vertices in members.items()}


def project_union(
    state: p5.TupleState,
    owners: tuple[int, ...],
    relations: Iterable[dict[int, int]],
) -> dict[int, int]:
    out: dict[int, int] = {}
    for relation in relations:
        projected = fullbank.project_masks(state, relation, owners)
        for source, mask in projected.items():
            out[source] = out.get(source, 0) | mask
    return out


def stage_reach_for_owners(
    state: p5.TupleState,
    masks: dict,
    shore: tuple[int, ...],
) -> dict[str, int]:
    old_index = {owner: index for index, owner in enumerate(state.owners)}
    old_shore = sum(1 << old_index[owner] for owner in shore)

    def reachable_sources(names: tuple[str, ...]) -> set[int]:
        reached: set[int] = set()
        for name in names:
            reached.update(
                source
                for source, mask in masks[name].items()
                if mask & old_shore
            )
        return reached

    p13 = reachable_sources(("p13",))
    p13p4 = reachable_sources(("p13", "p4"))
    p5_new = sum(
        source not in p13p4 and bool(mask & old_shore)
        for source, mask in masks["p5"].items()
    )
    return {
        "p1p3Reach": len(p13),
        "p1p3StrictP4Reach": len(p13p4),
        "p1p3StrictP4StaticP5Reach": len(p13p4) + p5_new,
        "staticP5NewReach": p5_new,
    }


def historical_p5_witness(
    ctx: p5.GraphContext,
    state: p5.TupleState,
    owners: tuple[int, ...],
    masks: dict,
) -> dict:
    """Check the 28 keys (3,56+2j,h) isolated by the R29 Pattern-5 gate."""
    hubs = tuple(owner for owner in (0, 1, 2) if owner in owners)
    old_index = {owner: index for index, owner in enumerate(state.owners)}
    hub_old_mask = sum(1 << old_index[owner] for owner in hubs)
    keys = [
        [3, 56 + 2 * arm, half]
        for arm in range(14)
        for half in (0, 1)
    ]
    source_ids = [p5.source_id(ctx.n, *key) for key in keys]
    all_p5_eligible = all(
        masks["p5"].get(source, 0) & hub_old_mask == hub_old_mask
        for source in source_ids
    )
    all_new_for_hubs = all(
        not (
            (masks["p13"].get(source, 0) | masks["p4"].get(source, 0))
            & hub_old_mask
        )
        for source in source_ids
    )
    return {
        "owners": list(hubs),
        "sourceKeys": keys,
        "sourceKeyCount": len(keys),
        "allStaticP5EligibleForEveryHub": all_p5_eligible,
        "allNewForHubShoreVsP1P3StrictP4": all_new_for_hubs,
        "exclusiveHalfKeys": len({tuple(key) for key in keys}) == len(keys),
        "sourceIds": source_ids,
    }


def eligible_pattern_mask(
    ctx: p5.GraphContext,
    state: p5.TupleState,
    masks: dict,
    owner: int,
    source: int,
) -> int:
    x, y, _half = fullbank.decode_source(ctx.n, source)
    owner_index = state.owners.index(owner)
    owner_bit = 1 << owner_index
    pattern = 0
    if masks["p13"].get(source, 0) & owner_bit:
        if x == owner:
            pattern |= PATTERN_P1
        if (
            state.pair[owner][x] > 0
            and state.pair[owner][y] > 0
            and ctx.sigma_pair[x][y] >= 0
        ):
            pattern |= PATTERN_P3
        if not (pattern & (PATTERN_P1 | PATTERN_P3)):
            raise AssertionError("P1/P3 relation has no literal provider")
    if masks["p4"].get(source, 0) & owner_bit:
        pattern |= PATTERN_P4
    if masks["p5"].get(source, 0) & owner_bit:
        pattern |= PATTERN_P5
    return pattern


def assignment_certificate(
    ctx: p5.GraphContext,
    state: p5.TupleState,
    owners: tuple[int, ...],
    masks: dict,
    raw: dict[int, int],
    matching,
) -> tuple[list[list[int]], list[list[int]], dict[str, bool]]:
    obligations = fullbank.collision_obligations(state, owners)
    assigned: dict[int, list[int]] = {owner: [] for owner in owners}
    for source, owner_index in matching.assignment:
        assigned[owners[owner_index]].append(source)
    roots = component_roots(state)
    records: list[list[int]] = []
    unmatched: list[list[int]] = []
    for owner in owners:
        sources = sorted(assigned[owner])
        owner_obligations = obligations[owner]
        if len(sources) > len(owner_obligations):
            raise AssertionError("owner receives more sources than obligations")
        owner_index = owners.index(owner)
        for obligation, source in zip(owner_obligations, sources):
            if not (raw.get(source, 0) & (1 << owner_index)):
                raise AssertionError("assignment uses an ineligible source")
            x, y, half = fullbank.decode_source(ctx.n, source)
            component = state.selected_comp[owner]
            pattern = eligible_pattern_mask(ctx, state, masks, owner, source)
            if pattern == 0:
                raise AssertionError("assignment source has no named pattern")
            records.append(
                [*obligation, x, y, half, roots[component], pattern]
            )
        unmatched.extend([*obligation] for obligation in owner_obligations[len(sources):])

    source_keys = {(r[4], r[5], r[6]) for r in records}
    obligation_keys = {tuple(r[:4]) for r in records}
    base_component: dict[tuple[int, int], int] = {}
    coherent = True
    no_scoped_reserved = True
    for record in records:
        owner, _other, _copy, _ohalf, x, y, half, root, _pattern = record
        base = (x, y)
        previous = base_component.setdefault(base, root)
        coherent &= previous == root
        no_scoped_reserved &= not (
            half == 0
            and p5.edge(x, y) in state.demanded_active_edges
            and x in state.active_vertices
        )
        if roots[state.selected_comp[owner]] != root:
            coherent = False
    checks = {
        "exclusiveFreeHalfKeys": len(source_keys) == len(records),
        "oneSourcePerCollisionObligation": len(obligation_keys) == len(records),
        "baseKeyComponentCoherent": coherent,
        "allAssignedKeysOutsideScopedReserved": no_scoped_reserved,
        "assignmentCardinalityMatchesSolver": len(records) == matching.matched,
        "unmatchedCardinalityMatchesDefect": len(unmatched) == matching.defect,
    }
    if not all(checks.values()):
        raise AssertionError(checks)
    return records, unmatched, checks


def build_endpoint(
    ctx: p5.GraphContext,
    rows: tuple[tuple[int, ...], ...],
    tuple_label: str,
    choice_ids: list[int],
    kind_counts: dict[str, int],
    *,
    solve_with_historical_p5_only: bool = False,
) -> dict:
    state = p5.reconstruct_state(ctx, rows)
    owners = fullbank.collision_owners(state)
    masks = p5.relation_masks(ctx, state)
    raw = project_union(
        state,
        owners,
        (masks["p13"], masks["p4"], masks["p5"]),
    )
    p5_witness = historical_p5_witness(ctx, state, owners, masks)
    solve_raw = raw
    if solve_with_historical_p5_only:
        solve_raw = project_union(state, owners, (masks["p13"], masks["p4"]))
        old_index = {owner: index for index, owner in enumerate(state.owners)}
        for source in p5_witness["sourceIds"]:
            old_mask = masks["p5"].get(source, 0)
            mask = sum(
                1 << index
                for index, owner in enumerate(owners)
                if old_mask & (1 << old_index[owner])
            )
            if mask:
                solve_raw[source] = solve_raw.get(source, 0) | mask
    matching = fullbank.coherent_collision_match(ctx, state, owners, solve_raw, ())
    records, unmatched, checks = assignment_certificate(
        ctx, state, owners, masks, raw, matching
    )
    p5_only_source_keys = sorted(
        {tuple(record[4:7]) for record in records if record[8] == PATTERN_P5}
    )
    historical_p5_keys = {
        tuple(key) for key in p5_witness["sourceKeys"]
    }
    doors = fullbank.door_match(state, ctx.n)
    witness_owners = [
        owner
        for index, owner in enumerate(owners)
        if matching.witness_owner_mask & (1 << index)
    ]
    witness_defect = matching.witness_demand - matching.witness_reach
    hall_upper = matching.demand - max(0, witness_defect)
    if matching.defect == 0:
        hall_upper = matching.demand
    max_proved = matching.matched == hall_upper
    checks.update(
        {
            "hallDemandExcludesHitNeed": True,
            "maximumProvedByAssignmentAndHallUpperBound": max_proved,
            "hitNeedReportedOnlyAsTypedBankSinkMetadata": True,
            "noCommonBlueRelation": True,
            "noP2Relation": True,
            "integerOnly": True,
        }
    )
    if solve_with_historical_p5_only:
        checks.update(
            {
                "everyP5OnlyAssignedKeyIsHistoricalWitness28": (
                    set(p5_only_source_keys) <= historical_p5_keys
                ),
                "allHistorical28KeysAreUsedAsP5OnlyAssignments": (
                    set(p5_only_source_keys) == historical_p5_keys
                ),
            }
        )
    if not all(checks.values()):
        raise AssertionError(checks)
    hub_shore = tuple(owner for owner in (0, 1, 2) if owner in owners)
    hub_stage = stage_reach_for_owners(state, masks, hub_shore)
    hub_collision = sum(state.collision[owner] for owner in hub_shore)
    hub_hit = sum(state.hit_need.get(owner, 0) for owner in hub_shore)
    assignment_digest = sha256_json(records)
    unmatched_digest = sha256_json(unmatched)
    endpoint = {
        "tuple": {
            "label": tuple_label,
            "tupleId": "sha256:" + sha256_json(rows),
            "rowTupleSha256": sha256_json(rows),
            "selectorChoiceIds": choice_ids,
            "selectorChoiceIdsSha256": sha256_json(choice_ids),
            "selectorRowKindCounts": kind_counts,
        },
        "state": {
            "selectedVertices": len(state.selected),
            "activeVertices": len(state.active_vertices),
            "activeEdges": len(state.active_edges),
            "demandedActiveEdges": len(state.demanded_active_edges),
            "collisionOwners": list(owners),
            "collisionOwnerCount": len(owners),
            "collisionDemandByOwner": [
                [owner, state.collision[owner]] for owner in owners
            ],
        },
        "relation": {
            "sourceKeys": len(raw),
            "assignmentSearchSourceKeys": len(solve_raw),
            "assignmentSearchUsesOnlyHistorical28FromP5": (
                solve_with_historical_p5_only
            ),
            "p1p3Keys": len(masks["p13"]),
            "strictP4Keys": len(masks["p4"]),
            "staticP5Keys": len(masks["p5"]),
            "p4CheckedSwitches": masks["p4Audit"]["checkedSwitches"],
            "p4NegativeSwitchesRejected": masks["p4Audit"]["negativeSwitches"],
            "p5CheckedSwitches": masks["p5Audit"]["checkedSwitches"],
            "p5NegativeSwitchesRejected": masks["p5Audit"]["negativeSwitches"],
            "hubShore": {
                "owners": list(hub_shore),
                "collisionDemand": hub_collision,
                **hub_stage,
            },
            "historicalStaticP5Witness28": {
                key: value
                for key, value in p5_witness.items()
                if key != "sourceIds"
            },
        },
        "matching": {
            "demand": matching.demand,
            "maximumCoherentMatchingSize": matching.matched,
            "collisionDefect": matching.defect,
            "assignmentColumns": ASSIGNMENT_COLUMNS,
            "assignment": records,
            "assignmentSha256": assignment_digest,
            "unmatchedObligationColumns": OBLIGATION_COLUMNS,
            "unmatchedObligations": unmatched,
            "unmatchedObligationsSha256": unmatched_digest,
            "usedOrderedBaseKeys": len({(r[4], r[5]) for r in records}),
            "p5OnlyAssignedSourceKeys": len(p5_only_source_keys),
            "p5OnlyAssignedSourceKeysSha256": sha256_json(p5_only_source_keys),
            "solverSearchNodes": matching.search_nodes,
            "solverBaseLabels": [list(label) for label in matching.base_labels],
            "hallUpperBound": hall_upper,
            "hallWitness": {
                "owners": witness_owners,
                "demand": matching.witness_demand,
                "reach": matching.witness_reach,
                "defect": witness_defect,
            },
        },
        "hitNeedSeparateTypedBankSinks": {
            "includedInCollisionDemand": False,
            "sinkCount": doors.demand_slots,
            "doorOnlyDiagnosticIsNotPartOfCollisionCertificate": True,
            "matchedDoorSinks": doors.matched_slots,
            "doorSinkDefect": doors.defect_slots,
            "doorAssignmentColumns": ["owner", "edgeU", "edgeV"],
            "doorAssignment": [
                [owner, edge[0], edge[1]] for edge, owner in doors.assignment
            ],
            "hubSinkCount": hub_hit,
        },
        "assertions": checks,
    }
    del state, masks, raw, solve_raw, matching, records, unmatched
    gc.collect()
    return endpoint


def build_certificate() -> dict:
    lead = load_lead()
    data = lead.build()
    endpoints = endpoint_rows(data)
    catalog = selector_choice_catalog(lead, data, endpoints)
    ctx = p5.make_graph_context(data["n"], data["blue"], data["bad"])
    baseline = build_endpoint(
        ctx,
        endpoints["baselineLocal"],
        "baseline-local: canonical displayed local row in every selector family",
        catalog["choiceIds"]["baselineLocal"],
        catalog["kindCounts"]["baselineLocal"],
    )
    anchor = build_endpoint(
        ctx,
        endpoints["metadataAnchor"],
        "metadata-anchor: selectorMeta.anchorRow in every selector family",
        catalog["choiceIds"]["metadataAnchor"],
        catalog["kindCounts"]["metadataAnchor"],
        solve_with_historical_p5_only=True,
    )
    baseline_hub = baseline["relation"]["hubShore"]
    baseline_hits = baseline["hitNeedSeparateTypedBankSinks"]
    legacy_gap = (
        baseline_hub["collisionDemand"]
        + baseline_hits["hubSinkCount"]
        - baseline_hub["p1p3StrictP4StaticP5Reach"]
    )
    top_assertions = {
        "canonicalGraphIs2943Cage": (
            data["n"] == 2943
            and len(data["blue"]) == 7039
            and len(data["bad"]) == 1383
        ),
        "tradeChangesExactly676SelectorRows": sum(
            left != right
            for left, right in zip(
                endpoints["baselineLocal"], endpoints["metadataAnchor"]
            )
        )
        == 676,
        "fromTupleIsExactlyBaselineLocal": (
            baseline["tuple"]["selectorRowKindCounts"]
            == {"local": 676, "anchor": 0}
        ),
        "toTupleIsExactlyMetadataAnchor": (
            anchor["tuple"]["selectorRowKindCounts"]
            == {"local": 0, "anchor": 676}
        ),
        "collisionOnlyBaselineDefectIs25": (
            baseline["matching"]["collisionDefect"] == 25
        ),
        "collisionOnlyBaselineDefectIsNot28": (
            baseline["matching"]["collisionDefect"] != 28
        ),
        "legacyMixedHubGapIs28": legacy_gap == 28,
        "legacy28EqualsCollision25PlusThreeHitNeed": (
            legacy_gap
            == baseline["matching"]["collisionDefect"]
            + baseline_hits["hubSinkCount"]
            and baseline_hits["hubSinkCount"] == 3
        ),
        "metadataAnchorCollisionDefectIsZero": (
            anchor["matching"]["collisionDefect"] == 0
        ),
        "fullStaticP5AddsAtLeast28HubReachAtAnchor": (
            anchor["relation"]["hubShore"]["staticP5NewReach"] >= 28
        ),
        "historical28StaticP5KeysAreAValidNewHubWitness": (
            anchor["relation"]["historicalStaticP5Witness28"][
                "sourceKeyCount"
            ]
            == 28
            and anchor["relation"]["historicalStaticP5Witness28"][
                "allStaticP5EligibleForEveryHub"
            ]
            and anchor["relation"]["historicalStaticP5Witness28"][
                "allNewForHubShoreVsP1P3StrictP4"
            ]
            and anchor["relation"]["historicalStaticP5Witness28"][
                "exclusiveHalfKeys"
            ]
        ),
        "anchorAssignmentNeedsNoOtherP5Keys": (
            anchor["relation"]["assignmentSearchUsesOnlyHistorical28FromP5"]
            and anchor["matching"]["p5OnlyAssignedSourceKeys"] == 28
            and anchor["assertions"][
                "allHistorical28KeysAreUsedAsP5OnlyAssignments"
            ]
        ),
        "allAssignmentsUseExclusiveCoherentKeys": (
            baseline["assertions"]["exclusiveFreeHalfKeys"]
            and baseline["assertions"]["baseKeyComponentCoherent"]
            and anchor["assertions"]["exclusiveFreeHalfKeys"]
            and anchor["assertions"]["baseKeyComponentCoherent"]
        ),
        "hitNeedExcludedAtBothEndpoints": (
            not baseline["hitNeedSeparateTypedBankSinks"][
                "includedInCollisionDemand"
            ]
            and not anchor["hitNeedSeparateTypedBankSinks"][
                "includedInCollisionDemand"
            ]
        ),
    }
    if not all(top_assertions.values()):
        raise AssertionError(top_assertions)
    dependencies = {
        str(path.relative_to(ROOT)).replace("\\", "/"): sha256_file(path)
        for path in (
            LEAD_PATH,
            STRUCTURAL_GATE_PATH,
            PATTERN5_GATE_PATH,
            P5_CORE_PATH,
            FULLBANK_CORE_PATH,
            COLLISION_CORE_PATH,
            JOIN_GATE_PATH,
        )
    }
    return {
        "schema": "R33_2943_COLLISION_SELECTOR_TRADE_V1",
        "arithmetic": "exact integer and finite sets only",
        "relation": {
            "name": "collision-only FreeHalf",
            "includedPatterns": [
                "P1 same-first",
                "P3 row-companion",
                "strict P4 outside-selected attachment",
                "static P5 quiescent attachment",
            ],
            "excludedPatterns": ["P2", "common-blue"],
            "hitNeedIncluded": False,
            "sourceCapacity": 1,
            "obligationCapacity": 1,
            "baseKeyComponentCoherent": True,
            "scopedReservedHalfZeroCapacity": 0,
            "patternMask": {"P1": 1, "P3": 2, "P4": 4, "P5": 8},
        },
        "canonicalInput": {
            "n": data["n"],
            "blueEdges": len(data["blue"]),
            "badEdges": len(data["bad"]),
            "rows": len(data["rows"]),
            "canonicalIncidenceSha256": canonical_incidence_sha(data),
            "leadCanonicalRowsSha256": hashlib.sha256(
                lead.canonical_bytes(data)
            ).hexdigest(),
            "dependencySha256": dependencies,
        },
        "selectorCatalog": {
            key: value
            for key, value in catalog.items()
            if key not in ("choiceIds", "kindCounts")
        },
        "trade": {
            "from": "baselineLocal",
            "to": "metadataAnchor",
            "changedSelectorFamilies": 676,
            "r33LabelCorrection": (
                "The concrete endpoints are the reconstruction's baseline-local "
                "tuple and its selectorMeta metadata-anchor tuple. Collision-only "
                "defect is 25->0; 28 was the legacy hub gap after adding 3 HitNeed."
            ),
        },
        "endpoints": {
            "baselineLocal": baseline,
            "metadataAnchor": anchor,
        },
        "assertions": top_assertions,
    }


__all__ = [
    "ASSIGNMENT_COLUMNS",
    "HERE",
    "OBLIGATION_COLUMNS",
    "ROOT",
    "build_certificate",
    "component_roots",
    "endpoint_rows",
    "fullbank",
    "json_bytes",
    "load_lead",
    "p5",
    "project_union",
    "selector_choice_catalog",
    "sha256_file",
    "sha256_json",
    "stage_reach_for_owners",
]
