#!/usr/bin/env python3
"""Exact owner-shore boundary profiles for the C5[3] lex-min obstruction."""

from __future__ import annotations

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
WRITEUP = ROOT / "problems" / "23" / "writeup"
SOFTCAP = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate"
for path in (HERE, WRITEUP, SOFTCAP):
    sys.path.insert(0, str(path))

from _codex_r20_c5_blowup_local_min_gate import balanced_c5, rows_of
import global_softcap as soft
from exchange_gate import build_metric, family_relation, shore_profile

T = 3
BAD = (12, 16, 11, 1, 5, 6, 26, 18, 22)
GOOD = (2, 19, 9, 21, 14, 4, 16, 6, 26)


def crosses(edge, shore):
    return (edge[0] in shore) != (edge[1] in shore)


def profile(ctx, metric):
    state = metric["state"]
    shore = set(metric["shore"])
    support_boundary = {e for e in state.support if crosses(e, shore)}
    active_boundary = {e for e in state.active_edges if crosses(e, shore)}
    outside_boundary = {
        e for e in ctx.blue
        if crosses(e, shore) and not (e[0] in state.selected and e[1] in state.selected)
    }
    blue_boundary = {e for e in ctx.blue if crosses(e, shore)}
    bad_boundary = {e for e in ctx.bad if crosses(e, shore)}
    active_internal = {
        e for e in state.active_edges if e[0] in shore and e[1] in shore
    }
    row_path_crossings = sum(
        crosses(soft.norm_edge(x, y), shore)
        for row in state.rows
        for x, y in zip(row, row[1:])
    )
    row_bad_crossings = sum(
        crosses(soft.norm_edge(row[0], row[-1]), shore)
        for row in state.rows
    )
    owner_row_incidence = sum(state.row_count[x] for x in shore)
    pair_support = sum(
        state.pair[x][y] > 0 for x in shore for y in range(ctx.n)
    )
    collision_units = sum(
        max(0, state.pair[x][y] - 1)
        for x in shore for y in range(ctx.n)
    )
    row_overload = 5 * owner_row_incidence - ctx.n * len(shore)

    p1 = family_relation(ctx, state, metric["owners"], "P1_sameFirst", "unscoped")
    p1_metric = dict(metric)
    p1_metric["relation"] = p1
    p1_shore = shore_profile(ctx, p1_metric, shore)
    full_shore = shore_profile(ctx, metric, shore)

    assert row_path_crossings >= row_bad_crossings
    assert blue_boundary == support_boundary | active_boundary | outside_boundary
    assert not (support_boundary & active_boundary)
    assert not (support_boundary & outside_boundary)
    assert not (active_boundary & outside_boundary)
    assert len(blue_boundary) - len(bad_boundary) >= 0
    assert collision_units == 5 * owner_row_incidence - pair_support
    assert metric["defect"] == full_shore["gap"]

    return {
        "shore": sorted(shore),
        "shoreSize": len(shore),
        "demand": full_shore["demand"],
        "fullCapacity": full_shore["capacity"],
        "fullDefect": full_shore["gap"],
        "p1Capacity": p1_shore["capacity"],
        "p1Gap": p1_shore["gap"],
        "supportBoundary": len(support_boundary),
        "activeBoundary": len(active_boundary),
        "outsideBlueBoundary": len(outside_boundary),
        "blueBoundary": len(blue_boundary),
        "badBoundary": len(bad_boundary),
        "maxCutSlack": len(blue_boundary) - len(bad_boundary),
        "activeInternal": len(active_internal),
        "rowPathCrossings": row_path_crossings,
        "rowBadCrossings": row_bad_crossings,
        "supportMultiplicityExcess": row_path_crossings - len(support_boundary),
        "ownerRowIncidence": owner_row_incidence,
        "pairSupport": pair_support,
        "collisionUnitsOnShore": collision_units,
        "rowOverload": row_overload,
        "twiceRowOverloadPlusInternalActive": 2 * (row_overload + len(active_internal)),
        "exposureEdges": len(active_boundary) + len(outside_boundary),
        "twiceExposureEdges": 2 * (len(active_boundary) + len(outside_boundary)),
    }


def main():
    _layers, info, families = balanced_c5(T)
    ctx = soft.make_graph_context(5 * T, info["Bset"], info["Mset"])
    payload = {}
    for name, choice in (("bad", BAD), ("good", GOOD)):
        metric = build_metric(
            ctx, rows_of(families, choice), force_full=True, p4_scope="unscoped"
        )
        payload[name] = {
            "choice": list(choice),
            "collisionUnits": metric["collision"],
            "globalDefect": metric["defect"],
            "maximumFlow": metric["flow"],
            "profile": profile(ctx, metric),
        }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
