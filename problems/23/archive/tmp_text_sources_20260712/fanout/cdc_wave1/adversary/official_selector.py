#!/usr/bin/env python3
"""Official coherence-free six-relation selector evaluator.

This module reuses only the exact graph/state/max-flow primitives from
``selector_core``.  It replaces the diagnostic strict-P4 relation by the
official coherence-free R23 outside-attachment predicate: a boundary vertex
must co-occur with the owner, but no owner/attachment active-component
equality is imposed.  P5 retains its active-component condition.
"""

from __future__ import annotations

from collections import Counter
from itertools import product
from typing import Sequence

import selector_core as base


FAMILIES = (
    "P1_sameFirst",
    "P2_commonBad",
    "P3_rowCompanion",
    "P4_outsideAttachment",
    "P5_quiescentAttachment",
    "commonBlue",
)


def outside_attachment_relation(
    graph: base.CutGraph,
    state: base.TupleState,
    owners: tuple[int, ...],
) -> tuple[dict[base.SourceKey, int], dict[str, int | bool]]:
    system = base.component_system(
        graph,
        frozenset(range(graph.n)) - state.selected,
        state.selected,
    )
    masks = []
    for boundary in system.boundaries:
        mask = 0
        for index, owner in enumerate(owners):
            if any(state.pair[owner][attach] > 0 for attach in boundary):
                mask |= 1 << index
        masks.append(mask)
    relation: dict[base.SourceKey, int] = {}
    negative = 0
    checked = 0
    for left, left_vertices in enumerate(system.components):
        for right, right_vertices in enumerate(system.components):
            mask = masks[left] & masks[right]
            if not mask:
                continue
            switch = left_vertices | right_vertices
            nonnegative = base.sigma_set(graph, switch) >= 0
            for x in left_vertices:
                for y in right_vertices:
                    if x == y or state.pair[x][y] != 0:
                        continue
                    checked += 1
                    if not nonnegative:
                        negative += 1
                        continue
                    relation[x, y, 0] = mask
                    relation[x, y, 1] = mask
    return relation, {
        "components": len(system.components),
        "nonemptyBoundaries": sum(bool(item) for item in system.boundaries),
        "checkedOrderedBases": checked,
        "negativeOrderedBases": negative,
        "ownerAttachmentActiveComponentEquality": False,
    }


def relation_families(
    graph: base.CutGraph, state: base.TupleState
) -> tuple[tuple[int, ...], dict[str, dict[base.SourceKey, int]], dict[str, dict]]:
    owners, strict, strict_audit = base.relation_families(graph, state)
    p4, p4_audit = outside_attachment_relation(graph, state, owners)
    relations = {
        "P1_sameFirst": strict["P1_sameFirst"],
        "P2_commonBad": strict["P2_commonBad"],
        "P3_rowCompanion": strict["P3_rowCompanion"],
        "P4_outsideAttachment": p4,
        "P5_quiescentAttachment": strict["P5_quiescentAttachment"],
        "commonBlue": strict["commonBlue"],
    }
    audit = {
        "P1_sameFirst": strict_audit["P1_sameFirst"],
        "P2_commonBad": strict_audit["P2_commonBad"],
        "P3_rowCompanion": strict_audit["P3_rowCompanion"],
        "P4_outsideAttachment": p4_audit,
        "P5_quiescentAttachment": strict_audit["P5_quiescentAttachment"],
        "commonBlue": strict_audit["commonBlue"],
    }
    return owners, relations, audit


def merge_relations(
    relations: dict[str, dict[base.SourceKey, int]]
) -> dict[base.SourceKey, int]:
    union: dict[base.SourceKey, int] = {}
    for family in FAMILIES:
        for key, mask in relations[family].items():
            union[key] = union.get(key, 0) | mask
    return union


def analyze_tuple(
    graph: base.CutGraph, rows: Sequence[Sequence[int]]
) -> dict:
    state = base.reconstruct_state(graph, rows)
    owners, relations, audit = relation_families(graph, state)
    union = merge_relations(relations)
    flow = base.solve_literal_grouped_flow(graph, state, owners, union)
    shores = base.enumerate_grouped_shores(state, owners, union)
    if shores.get("enumerated"):
        expected = max(0, -shores["minimumShore"]["slack"])
        if flow["defect"] != expected:
            raise AssertionError((flow, shores["minimumShore"]))
    obligations = list(base.collision_obligations(state))
    if len(obligations) != flow["totalDemand"]:
        raise AssertionError("CollisionHalf enumeration/demand mismatch")
    demand = base.collision_demand(state)
    return {
        "model": {
            "demand": "every global CollisionHalf",
            "sinks": "actual FreeHalf(sourceX,sourceY,half)",
            "relations": list(FAMILIES),
            "p4OwnerAttachmentActiveComponentEquality": False,
            "literalKeyCapacity": 1,
            "activeUndirectedEdgeAggregateCapacity": 2,
            "arithmetic": "Python integers only",
        },
        "rows": [list(row) for row in state.rows],
        "rowSha256": base.canonical_sha([list(row) for row in state.rows]),
        "collisionUnits": base.collision_units(state),
        "collisionHalfDemand": flow["totalDemand"],
        "collisionOwners": list(owners),
        "demandByOwner": {str(owner): demand[owner] for owner in owners},
        "selectedVertices": sorted(state.selected),
        "activeEdges": [list(edge) for edge in sorted(state.active_edges)],
        "activeVertices": sorted(state.active_vertices),
        "familyStats": {
            family: {
                "literalFreeHalfKeys": len(relations[family]),
                "ownerKeyArcs": sum(
                    mask.bit_count() for mask in relations[family].values()
                ),
                "audit": audit[family],
            }
            for family in FAMILIES
        },
        "unionLiteralFreeHalfKeys": len(union),
        "flow": flow,
        "shoreAudit": shores,
        "verdict": "PASS" if flow["defect"] == 0 else "FAIL",
    }


def exhaustive_minimum_collision_tuples(
    graph: base.CutGraph,
    row_db: tuple[tuple[base.Edge, tuple[base.Row, ...]], ...],
    *,
    tuple_cap: int = 1_000_000,
    stop_after_first_passing_minimum: bool = False,
) -> dict:
    sizes = [len(rows) for _edge, rows in row_db]
    tuple_count = 1
    for size in sizes:
        tuple_count *= size
    if not sizes:
        tuple_count = 1
    if tuple_count > tuple_cap:
        return {
            "exhaustive": False,
            "rowFamilySizes": sizes,
            "tupleCount": tuple_count,
            "tupleCap": tuple_cap,
        }
    minimum = None
    minima: list[tuple[tuple[int, ...], tuple[base.Row, ...]]] = []
    histogram: Counter[int] = Counter()
    for choice in product(*(range(size) for size in sizes)):
        rows = tuple(row_db[index][1][item] for index, item in enumerate(choice))
        units = base.collision_units(base.reconstruct_state(graph, rows))
        histogram[units] += 1
        if minimum is None or units < minimum:
            minimum = units
            minima = [(choice, rows)]
        elif units == minimum:
            minima.append((choice, rows))
    if minimum is None:
        minimum = 0
        minima = [((), ())]
    analyzed = []
    for choice, rows in minima:
        result = analyze_tuple(graph, rows)
        analyzed.append(
            {
                "choice": list(choice),
                "defect": result["flow"]["defect"],
                "verdict": result["verdict"],
                "rowSha256": result["rowSha256"],
                "analysis": result,
            }
        )
        if stop_after_first_passing_minimum and result["verdict"] == "PASS":
            break
    all_evaluated = len(analyzed) == len(minima)
    any_pass = any(item["verdict"] == "PASS" for item in analyzed)
    return {
        "exhaustive": True,
        "rowFamilySizes": sizes,
        "tupleCount": tuple_count,
        "collisionHistogram": {
            str(key): value for key, value in sorted(histogram.items())
        },
        "minimumCollisionUnits": minimum,
        "minimumTupleCount": len(minima),
        "minimumTuplesEvaluated": len(analyzed),
        "allMinimumTuplesEvaluated": all_evaluated,
        "minimumTuples": analyzed,
        "selectorVerdict": (
            "PASS_SOME_MINIMUM_TUPLE"
            if any_pass
            else "FAIL_ALL_MINIMUM_TUPLES"
            if all_evaluated
            else "UNRESOLVED_MINIMUM_TUPLES"
        ),
    }


__all__ = [
    "FAMILIES",
    "analyze_tuple",
    "exhaustive_minimum_collision_tuples",
    "outside_attachment_relation",
    "relation_families",
]
