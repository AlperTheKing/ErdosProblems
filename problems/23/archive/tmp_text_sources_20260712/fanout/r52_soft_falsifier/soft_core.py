#!/usr/bin/env python3
"""Exact coherence-free production collision matching.

Obligations are active collision halves. Sources are deduplicated physical
FreeHalf keys ``(sourceX, sourceY, half)``. Eligibility is the production
P1/P2/P3/strict-P4/P5/common-blue union reconstructed by ``p5_core``. The
only relaxation is deletion of BaseKeyComponentCoherent.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P5_DIR = ROOT / "tmp" / "fanout" / "p5_n12_census"
FULLBANK_DIR = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
for directory in (P5_DIR, FULLBANK_DIR):
    value = str(directory)
    if value not in sys.path:
        sys.path.insert(0, value)

import p5_core as p5  # noqa: E402
import fullbank_core as fullbank  # noqa: E402


SOURCE_FAMILIES = ("P1", "P2", "P3", "strict-P4", "P5", "common-blue")


def canonical_sha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


def projected_soft_relation(ctx: p5.GraphContext, state: p5.TupleState):
    """Return collision owners, all-six relation, and family audit data."""
    owners = fullbank.collision_owners(state)
    masks = p5.relation_masks(ctx, state)
    relation = fullbank.project_masks(state, masks["five"], owners)
    return owners, relation, masks


def hall_defect(
    demand: tuple[int, ...], relation: dict[int, int]
) -> tuple[int, int, int, int]:
    """Exact Hall deficit and a maximum-deficiency owner shore.

    Returns ``(maximum_defect, shore_mask, shore_demand, shore_reach)``.
    Every obligation at one owner has the same source neighborhood, so owner
    capacities are an exact quotient of the literal obligation graph.
    """
    owner_count = len(demand)
    if owner_count == 0:
        return 0, 0, 0, 0
    full_mask = (1 << owner_count) - 1
    source_histogram = [0] * (1 << owner_count)
    for owner_mask in relation.values():
        if owner_mask:
            source_histogram[owner_mask] += 1
    subset_sources = source_histogram[:]
    for owner_index in range(owner_count):
        bit = 1 << owner_index
        for mask in range(1 << owner_count):
            if mask & bit:
                subset_sources[mask] += subset_sources[mask ^ bit]

    demand_sum = [0] * (1 << owner_count)
    best = (0, 0, 0, 0)
    for shore in range(1, 1 << owner_count):
        bit = shore & -shore
        owner_index = bit.bit_length() - 1
        demand_sum[shore] = demand_sum[shore ^ bit] + demand[owner_index]
        reach = len(relation) - subset_sources[full_mask ^ shore]
        defect = demand_sum[shore] - reach
        if defect > best[0]:
            best = (defect, shore, demand_sum[shore], reach)
    return best


def analyze_soft(
    ctx: p5.GraphContext,
    rows: Iterable[Iterable[int]],
    *,
    details: bool = False,
) -> dict:
    state = p5.reconstruct_state(ctx, rows)
    owners, relation, masks = projected_soft_relation(ctx, state)
    demand_by_owner = tuple(state.collision[owner] for owner in owners)
    total_demand = sum(demand_by_owner)
    defect, shore, shore_demand, shore_reach = hall_defect(
        demand_by_owner, relation
    )
    matched = total_demand - defect
    if defect < 0 or matched < 0:
        raise AssertionError((total_demand, matched, defect))

    assignment = ()
    if details or defect > 0:
        flow = fullbank.owner_source_flow(demand_by_owner, relation)
        if flow.value != matched:
            raise AssertionError({
                "hallMatched": matched,
                "dinicMatched": flow.value,
            })
        assignment = flow.assignment
        if defect > 0 and (
            flow.witness_demand != shore_demand
            or flow.witness_reach != shore_reach
        ):
            # Distinct maximum-deficiency shores are allowed, but both must
            # certify the same positive defect.
            if flow.witness_demand - flow.witness_reach != defect:
                raise AssertionError("Dinic residual shore has wrong defect")

    source_arc_count = sum(mask.bit_count() for mask in relation.values())
    result = {
        "deltaSoft": defect,
        "collisionDemand": total_demand,
        "maximumMatching": matched,
        "owners": list(owners),
        "demandByOwner": {
            str(owner): state.collision[owner] for owner in owners
        },
        "sourceKeys": len(relation),
        "sourceOwnerArcs": source_arc_count,
        "physicalSourceIdentity": "(ordered sourceX, ordered sourceY, half)",
        "sourceFamilies": list(SOURCE_FAMILIES),
        "baseKeyComponentCoherent": False,
        "hitNeedExcluded": True,
        "hitNeedSlotsSeparate": sum(
            state.hit_need.get(owner, 0) for owner in state.active_vertices
        ),
        "worstShoreOwners": [
            owner for index, owner in enumerate(owners)
            if shore & (1 << index)
        ],
        "worstShoreDemand": shore_demand,
        "worstShoreReach": shore_reach,
        "p13Keys": len(masks["p13"]),
        "commonBlueKeys": len(masks["p2"]),
        "strictP4Keys": len(masks["p4"]),
        "p5Keys": len(masks["p5"]),
    }
    if details:
        result["rows"] = [list(row) for row in state.rows]
        result["state"] = p5.state_details(ctx, state)
        result["relation"] = [
            {
                "source": list(p5.decode_source(ctx.n, source)),
                "owners": [
                    owner for index, owner in enumerate(owners)
                    if owner_mask & (1 << index)
                ],
            }
            for source, owner_mask in sorted(relation.items())
        ]
        result["matching"] = [
            {
                "source": list(p5.decode_source(ctx.n, source)),
                "owner": owners[owner_index],
            }
            for source, owner_index in assignment
        ]
        result["relationSha256"] = canonical_sha(result["relation"])
        result["matchingSha256"] = canonical_sha(result["matching"])
    return result


def delta_soft(ctx: p5.GraphContext, rows: Iterable[Iterable[int]]) -> int:
    return analyze_soft(ctx, rows)["deltaSoft"]
