"""Replay the R33 2943 certificate without rerunning maximum flow.

Maximality is checked from the stored feasible assignment plus an exact Hall
upper bound at the deficient endpoint.  The zero-defect endpoint is maximal
because its assignment saturates every collision obligation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from certificate_core import (
    ASSIGNMENT_COLUMNS,
    HERE,
    OBLIGATION_COLUMNS,
    component_roots,
    endpoint_rows,
    fullbank,
    load_lead,
    p5,
    project_union,
    selector_choice_catalog,
    sha256_json,
    stage_reach_for_owners,
)


CERTIFICATE = HERE / "certificate.json"


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def replay_endpoint(ctx, rows, endpoint: dict, catalog: dict, endpoint_name: str) -> dict:
    state = p5.reconstruct_state(ctx, rows)
    owners = fullbank.collision_owners(state)
    masks = p5.relation_masks(ctx, state)
    raw = project_union(
        state,
        owners,
        (masks["p13"], masks["p4"], masks["p5"]),
    )
    matching = endpoint["matching"]
    records = matching["assignment"]
    unmatched = matching["unmatchedObligations"]
    assert_equal(matching["assignmentColumns"], ASSIGNMENT_COLUMNS, "assignment columns")
    assert_equal(
        matching["unmatchedObligationColumns"],
        OBLIGATION_COLUMNS,
        "unmatched columns",
    )
    assert_equal(sha256_json(records), matching["assignmentSha256"], "assignment digest")
    assert_equal(
        sha256_json(unmatched),
        matching["unmatchedObligationsSha256"],
        "unmatched digest",
    )
    assert_equal(sha256_json(rows), endpoint["tuple"]["rowTupleSha256"], "tuple digest")
    assert_equal(
        "sha256:" + sha256_json(rows), endpoint["tuple"]["tupleId"], "tuple ID"
    )
    assert_equal(
        endpoint["tuple"]["selectorChoiceIds"],
        catalog["choiceIds"][endpoint_name],
        "selector choice IDs",
    )
    assert_equal(
        sha256_json(endpoint["tuple"]["selectorChoiceIds"]),
        endpoint["tuple"]["selectorChoiceIdsSha256"],
        "selector choice digest",
    )

    obligations_by_owner = fullbank.collision_obligations(state, owners)
    all_obligations = {
        tuple(obligation)
        for owner in owners
        for obligation in obligations_by_owner[owner]
    }
    assigned_obligations = {tuple(record[:4]) for record in records}
    unmatched_set = {tuple(obligation) for obligation in unmatched}
    assert len(assigned_obligations) == len(records)
    assert len(unmatched_set) == len(unmatched)
    assert assigned_obligations.isdisjoint(unmatched_set)
    assert assigned_obligations | unmatched_set == all_obligations

    owner_index = {owner: index for index, owner in enumerate(owners)}
    state_owner_index = {owner: index for index, owner in enumerate(state.owners)}
    roots = component_roots(state)
    used_sources: set[tuple[int, int, int]] = set()
    base_component: dict[tuple[int, int], int] = {}
    pattern_hist = {"P1": 0, "P3": 0, "P4": 0, "P5": 0}
    p5_only_source_keys: set[tuple[int, int, int]] = set()
    for record in records:
        owner, _other, _copy, _ohalf, x, y, half, root, pattern = record
        source = p5.source_id(ctx.n, x, y, half)
        assert raw.get(source, 0) & (1 << owner_index[owner])
        key = (x, y, half)
        assert key not in used_sources
        used_sources.add(key)
        expected_root = roots[state.selected_comp[owner]]
        assert root == expected_root
        previous = base_component.setdefault((x, y), root)
        assert previous == root
        assert not (
            half == 0
            and p5.edge(x, y) in state.demanded_active_edges
            and x in state.active_vertices
        )
        old_bit = 1 << state_owner_index[owner]
        exact_pattern = 0
        if masks["p13"].get(source, 0) & old_bit:
            if x == owner:
                exact_pattern |= 1
            if (
                state.pair[owner][x] > 0
                and state.pair[owner][y] > 0
                and ctx.sigma_pair[x][y] >= 0
            ):
                exact_pattern |= 2
        if masks["p4"].get(source, 0) & old_bit:
            exact_pattern |= 4
        if masks["p5"].get(source, 0) & old_bit:
            exact_pattern |= 8
        assert pattern == exact_pattern and pattern != 0
        if pattern == 8:
            p5_only_source_keys.add(key)
        for name, bit in (("P1", 1), ("P3", 2), ("P4", 4), ("P5", 8)):
            if pattern & bit:
                pattern_hist[name] += 1

    demand = sum(state.collision[owner] for owner in owners)
    matched = len(records)
    defect = demand - matched
    assert_equal(demand, matching["demand"], "collision demand")
    assert_equal(matched, matching["maximumCoherentMatchingSize"], "matching size")
    assert_equal(defect, matching["collisionDefect"], "collision defect")
    assert_equal(defect, len(unmatched), "unmatched cardinality")

    witness = matching["hallWitness"]
    witness_mask = sum(
        1 << owner_index[owner] for owner in witness["owners"]
    )
    witness_demand = sum(state.collision[owner] for owner in witness["owners"])
    witness_reach = sum(bool(mask & witness_mask) for mask in raw.values())
    assert_equal(witness_demand, witness["demand"], "Hall witness demand")
    assert_equal(witness_reach, witness["reach"], "Hall witness reach")
    assert_equal(witness_demand - witness_reach, witness["defect"], "Hall defect")
    hall_upper = demand - max(0, witness_demand - witness_reach)
    if defect == 0:
        hall_upper = demand
    assert_equal(hall_upper, matching["hallUpperBound"], "Hall upper bound")
    assert matched == hall_upper
    p5_only_sorted = sorted(p5_only_source_keys)
    assert_equal(
        len(p5_only_sorted),
        matching["p5OnlyAssignedSourceKeys"],
        "P5-only assignment keys",
    )
    assert_equal(
        sha256_json(p5_only_sorted),
        matching["p5OnlyAssignedSourceKeysSha256"],
        "P5-only assignment digest",
    )

    assert_equal(len(raw), endpoint["relation"]["sourceKeys"], "relation keys")
    assert_equal(len(masks["p13"]), endpoint["relation"]["p1p3Keys"], "P1/P3 keys")
    assert_equal(len(masks["p4"]), endpoint["relation"]["strictP4Keys"], "P4 keys")
    assert_equal(len(masks["p5"]), endpoint["relation"]["staticP5Keys"], "P5 keys")
    hub = tuple(endpoint["relation"]["hubShore"]["owners"])
    hub_stage = stage_reach_for_owners(state, masks, hub)
    for key, value in hub_stage.items():
        assert_equal(value, endpoint["relation"]["hubShore"][key], f"hub {key}")
    if endpoint["relation"]["assignmentSearchUsesOnlyHistorical28FromP5"]:
        historical = {
            tuple(key)
            for key in endpoint["relation"]["historicalStaticP5Witness28"][
                "sourceKeys"
            ]
        }
        assert p5_only_source_keys == historical

    doors = fullbank.door_match(state, ctx.n)
    bank = endpoint["hitNeedSeparateTypedBankSinks"]
    assert bank["includedInCollisionDemand"] is False
    assert_equal(doors.demand_slots, bank["sinkCount"], "separate HitNeed sinks")
    assert_equal(doors.matched_slots, bank["matchedDoorSinks"], "Door sinks matched")
    assert_equal(doors.defect_slots, bank["doorSinkDefect"], "Door sink defect")
    assert bank["doorOnlyDiagnosticIsNotPartOfCollisionCertificate"] is True
    assert all(endpoint["assertions"].values())
    return {
        "tupleId": endpoint["tuple"]["tupleId"],
        "demand": demand,
        "maximumCoherentMatchingSize": matched,
        "collisionDefect": defect,
        "unmatchedObligations": len(unmatched),
        "assignmentSha256": matching["assignmentSha256"],
        "hallWitness": witness,
        "eligiblePatternUseCounts": pattern_hist,
        "exclusiveSourceKeys": len(used_sources),
        "coherentOrderedBaseKeys": len(base_component),
    }


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text(encoding="ascii"))
    assert certificate["schema"] == "R33_2943_COLLISION_SELECTOR_TRADE_V1"
    assert certificate["arithmetic"] == "exact integer and finite sets only"
    assert certificate["relation"]["hitNeedIncluded"] is False
    assert certificate["relation"]["excludedPatterns"] == ["P2", "common-blue"]
    lead = load_lead()
    data = lead.build()
    rows = endpoint_rows(data)
    catalog = selector_choice_catalog(lead, data, rows)
    stored_catalog = certificate["selectorCatalog"]
    for key, value in stored_catalog.items():
        assert_equal(catalog[key], value, f"selector catalog {key}")
    ctx = p5.make_graph_context(data["n"], data["blue"], data["bad"])
    summaries = {}
    for name in ("baselineLocal", "metadataAnchor"):
        summaries[name] = replay_endpoint(
            ctx,
            rows[name],
            certificate["endpoints"][name],
            catalog,
            name,
        )
    assert summaries["baselineLocal"]["collisionDefect"] == 25
    assert summaries["metadataAnchor"]["collisionDefect"] == 0
    assert all(certificate["assertions"].values())
    output = {
        "schema": "R33_2943_COLLISION_SELECTOR_TRADE_REPLAY_V1",
        "certificateSha256": hashlib.sha256(CERTIFICATE.read_bytes()).hexdigest(),
        "status": "PASS",
        "endpoints": summaries,
        "labelCorrection": certificate["trade"]["r33LabelCorrection"],
    }
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
