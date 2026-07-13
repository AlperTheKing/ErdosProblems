"""Exact coherent collision Hall for P1 + P3 + strict P4 + P5.

Common-blue is absent.  HitNeed is deliberately not part of Hall demand; it is
reported only as separately bank-funded metadata.  Existing half-zero active
edge exclusions remain in force because they are part of ``FreeHalf``
availability, not a new common-blue reservation.
"""

from __future__ import annotations

from typing import Iterable

from fullbank_core import (
    CollisionResult,
    canonical_sha,
    coherent_collision_match,
    collision_obligations,
    collision_owners,
    decode_source,
    door_match,
    project_masks,
)
import p5_core as p5


def _merge(*relations: dict[int, int]) -> dict[int, int]:
    out: dict[int, int] = {}
    for relation in relations:
        for source, mask in relation.items():
            out[source] = out.get(source, 0) | mask
    return out


def _fast_hall(
    state: p5.TupleState,
    owners: tuple[int, ...],
    relation: dict[int, int],
) -> tuple[int, int, int, int]:
    """Return matched, defect, worst shore, and worst reach exactly."""
    demand = tuple(state.collision[owner] for owner in owners)
    total = sum(demand)
    count = len(owners)
    full_mask = (1 << count) - 1
    hist = [0] * (1 << count)
    for mask in relation.values():
        hist[mask] += 1
    subset = hist[:]
    for index in range(count):
        bit = 1 << index
        for mask in range(1 << count):
            if mask & bit:
                subset[mask] += subset[mask ^ bit]
    demand_sum = [0] * (1 << count)
    max_defect = 0
    worst_mask = 0
    worst_reach = 0
    for mask in range(1, 1 << count):
        bit = mask & -mask
        index = bit.bit_length() - 1
        demand_sum[mask] = demand_sum[mask ^ bit] + demand[index]
        reach = len(relation) - subset[full_mask ^ mask]
        defect = demand_sum[mask] - reach
        if defect > max_defect:
            max_defect = defect
            worst_mask = mask
            worst_reach = reach
    return total - max_defect, max_defect, worst_mask, worst_reach


def _coherence_automatic(
    state: p5.TupleState,
    owners: tuple[int, ...],
    relation: dict[int, int],
) -> bool:
    components_by_base: dict[int, set[int]] = {}
    for source, mask in relation.items():
        base = source >> 1
        components = components_by_base.setdefault(base, set())
        for index, owner in enumerate(owners):
            if mask & (1 << index):
                components.add(state.selected_comp[owner])
                if len(components) > 1:
                    return False
    return True


def analyze_collision_only(
    ctx: p5.GraphContext,
    rows: Iterable[Iterable[int]],
    *,
    details: bool = False,
) -> dict:
    state = p5.reconstruct_state(ctx, rows)
    owners = collision_owners(state)
    hit_slots = sum(state.hit_need.get(owner, 0) for owner in state.active_vertices)
    if not owners:
        result = {
            "full": True,
            "collisionDemand": 0,
            "collisionMatched": 0,
            "collisionDefect": 0,
            "hallDemandIncludesHitNeed": False,
            "hitNeedSlotsSeparate": hit_slots,
            "hitNeedDoorFundable": None,
            "doorMatchedSlots": None,
            "doorDefectSlots": None,
            "owners": [],
            "allDemandOwners": list(state.owners),
            "activeVertices": len(state.active_vertices),
            "activeEdges": len(state.active_edges),
            "demandedActiveEdges": len(state.demanded_active_edges),
            "sourceKeys": 0,
            "coherenceLabels": 0,
            "coherenceAutomatic": True,
            "searchNodes": 0,
            "p13Keys": 0,
            "p4Keys": 0,
            "p5Keys": 0,
            "p4CheckedSwitches": 0,
            "p4NegativeSwitchesRejected": 0,
            "p5CheckedSwitches": 0,
            "p5NegativeSwitches": 0,
            "p5ReservedCandidates": 0,
            "commonBlueCandidates": 0,
            "commonBlueUsed": 0,
            "newReservationEdges": 0,
            "pruneCheckedCapacity": 0,
        }
        if details:
            doors = door_match(state, ctx.n)
            result.update({
                "hitNeedDoorFundable": doors.defect_slots == 0,
                "doorMatchedSlots": doors.matched_slots,
                "doorDefectSlots": doors.defect_slots,
                "state": p5.state_details(ctx, state),
                "collisionAssignment": [],
                "baseLabels": [],
                "hallWitness": {"owners": [], "demand": 0, "reach": 0},
                "doorAssignmentSeparate": [
                    {"owner": owner, "edge": list(edge), "copies": 25}
                    for edge, owner in doors.assignment
                ],
            })
        return result
    masks = p5.relation_masks(ctx, state)
    raw = project_masks(
        state,
        _merge(masks["p13"], masks["p4"], masks["p5"]),
        owners,
    )
    coherence_automatic = _coherence_automatic(state, owners, raw)
    if details or not coherence_automatic:
        collision = coherent_collision_match(ctx, state, owners, raw, ())
    else:
        matched, defect, shore, reach = _fast_hall(state, owners, raw)
        demand = sum(state.collision[owner] for owner in owners)
        collision = CollisionResult(
            exact=True,
            demand=demand,
            matched=matched,
            defect=defect,
            assignment=(),
            selected_terminals=(),
            base_labels=(),
            search_nodes=0,
            raw_source_count=len(raw),
            final_source_count=len(raw),
            deducted_raw_keys=(),
            witness_owner_mask=shore,
            witness_demand=(
                sum(
                    state.collision[owner]
                    for index, owner in enumerate(owners)
                    if shore & (1 << index)
                )
            ),
            witness_reach=reach,
        )
    doors = door_match(state, ctx.n) if details else None
    result = {
        "full": collision.defect == 0,
        "collisionDemand": collision.demand,
        "collisionMatched": collision.matched,
        "collisionDefect": collision.defect,
        "hallDemandIncludesHitNeed": False,
        "hitNeedSlotsSeparate": hit_slots,
        "hitNeedDoorFundable": None if doors is None else doors.defect_slots == 0,
        "doorMatchedSlots": None if doors is None else doors.matched_slots,
        "doorDefectSlots": None if doors is None else doors.defect_slots,
        "owners": list(owners),
        "allDemandOwners": list(state.owners),
        "activeVertices": len(state.active_vertices),
        "activeEdges": len(state.active_edges),
        "demandedActiveEdges": len(state.demanded_active_edges),
        "sourceKeys": collision.raw_source_count,
        "coherenceLabels": len(collision.base_labels),
        "coherenceAutomatic": coherence_automatic,
        "searchNodes": collision.search_nodes,
        "p13Keys": len(masks["p13"]),
        "p4Keys": len(masks["p4"]),
        "p5Keys": len(masks["p5"]),
        "p4CheckedSwitches": masks["p4Audit"]["checkedSwitches"],
        "p4NegativeSwitchesRejected": masks["p4Audit"]["negativeSwitches"],
        "p5CheckedSwitches": masks["p5Audit"]["checkedSwitches"],
        "p5NegativeSwitches": masks["p5Audit"]["negativeSwitches"],
        "p5ReservedCandidates": masks["p5Audit"]["reservedCandidates"],
        "commonBlueCandidates": 0,
        "commonBlueUsed": 0,
        "newReservationEdges": 0,
        "pruneCheckedCapacity": 0,
    }
    if details:
        obligations = collision_obligations(state, owners)
        assigned: dict[int, list[int]] = {owner: [] for owner in owners}
        for source, owner_index in collision.assignment:
            assigned[owners[owner_index]].append(source)
        records = []
        for owner in owners:
            for obligation, source in zip(obligations[owner], sorted(assigned[owner])):
                sid = source
                old_index = state.owners.index(owner)
                owner_bit = 1 << old_index
                patterns = []
                if masks["p13"].get(sid, 0) & owner_bit:
                    patterns.append("P1/P3")
                if masks["p4"].get(sid, 0) & owner_bit:
                    patterns.append("P4")
                if masks["p5"].get(sid, 0) & owner_bit:
                    patterns.append("P5")
                records.append(
                    {
                        "obligation": list(obligation),
                        "source": list(decode_source(ctx.n, source)),
                        "eligiblePatterns": patterns,
                    }
                )
        result["state"] = p5.state_details(ctx, state)
        result["collisionAssignment"] = records
        result["baseLabels"] = [list(item) for item in collision.base_labels]
        result["hallWitness"] = {
            "owners": [
                owner for index, owner in enumerate(owners)
                if collision.witness_owner_mask & (1 << index)
            ],
            "demand": collision.witness_demand,
            "reach": collision.witness_reach,
        }
        assert doors is not None
        result["doorAssignmentSeparate"] = [
            {"owner": owner, "edge": list(edge), "copies": 25}
            for edge, owner in doors.assignment
        ]
    return result


__all__ = ["analyze_collision_only", "canonical_sha"]
