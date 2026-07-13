#!/usr/bin/env python3
"""Exact replay of the nine-copy R57 compiled-interface countermodel."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = HERE / "inputs" / "r57_positive_defect_extension_gate" / "check_gate.py"
spec = importlib.util.spec_from_file_location("r57_gate", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load R57 exact gate")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def main() -> int:
    ctx = gate.soft.make_graph_context(16, gate.BASE_BLUE, {gate.BASE_BAD})
    families = tuple((gate.LEFT_ROW, gate.RIGHT_ROW) for _ in range(9))
    records = [(choice, gate.exact_model(ctx, rows))
               for choice, rows in gate.iter_family_states(families)]
    collision_minimum = min(model.collision_units for _, model in records)
    defect_minimum = min(model.defect for _, model in records
                         if model.collision_units == collision_minimum)
    face = [(choice, model) for choice, model in records
            if (model.collision_units, model.defect)
            == (collision_minimum, defect_minimum)]
    saturable = [(choice, model) for choice, model in face
                 if gate.pair_count(model.rows, gate.FORK_LEFT, gate.FORK_RIGHT) == 0
                 and gate.forced_divergence_feasible(model)]

    displayed_choice = (0, 0, 0, 0, 1, 1, 1, 1, 1)
    displayed = dict(records)[displayed_choice]
    core = gate.unit_core_certificate(displayed)
    if core is None:
        raise AssertionError("displayed state has no forced unit core")
    owner_set = {gate.CORE["s"], gate.CORE["t"], gate.CORE["a1"],
                 gate.CORE["a2"], gate.CORE["a3"], gate.CORE["b1"],
                 gate.CORE["b2"]}
    shore_selected_load = sum(5 * gate.pair_count(displayed.rows, v, v)
                              for v in owner_set)
    shore_zero = sum(gate.pair_count(displayed.rows, v, y) == 0
                     for v in owner_set for y in range(ctx.n))
    shore_collision = shore_selected_load + shore_zero - ctx.n * len(owner_set)
    internal_active = sum(left in owner_set and right in owner_set
                          for left, right in displayed.state.active_edges)
    grouped_capacity = 2 * (shore_zero - internal_active)
    grouped_demand = 2 * shore_collision
    payload = {
        "schema": "R57_POSITIVE_DEFECT_INTERFACE_COUNTERMODEL_REPLAY_V1",
        "arithmetic": "Python integers; exact integral grouped max flow",
        "scope": "compiled interface only; nine copies violate CompleteShortestRowDB.badKeys_nodup",
        "rowTuplesExhausted": len(records),
        "collisionMinimum": collision_minimum,
        "defectMinimumOnCollisionFace": defect_minimum,
        "lexMinimalStates": len(face),
        "lexStatesSaturatingBothForkHalves": len(saturable),
        "displayedChoice": list(displayed_choice),
        "displayedDemand": sum(displayed.demand),
        "displayedMaximumFlow": displayed.maximum_flow,
        "displayedGlobalDefect": displayed.defect,
        "unitCore": core,
        "ownerSet": [gate.BASE_NAMES[v] for v in sorted(owner_set)],
        "shoreSelectedLoad": shore_selected_load,
        "internalActive": internal_active,
        "orderTimesOwnerCardinality": ctx.n * len(owner_set),
        "shoreCollision": shore_collision,
        "shoreZero": shore_zero,
        "p1GroupedDemand": grouped_demand,
        "p1GroupedCapacity": grouped_capacity,
    }
    expected = {
        "rowTuplesExhausted": 512,
        "collisionMinimum": 179,
        "defectMinimumOnCollisionFace": 50,
        "lexMinimalStates": 420,
        "lexStatesSaturatingBothForkHalves": 420,
        "displayedDemand": 358,
        "displayedMaximumFlow": 308,
        "displayedGlobalDefect": 50,
        "shoreSelectedLoad": 200,
        "internalActive": 0,
        "orderTimesOwnerCardinality": 112,
        "shoreCollision": 159,
        "shoreZero": 71,
        "p1GroupedDemand": 318,
        "p1GroupedCapacity": 142,
    }
    for key, value in expected.items():
        if payload[key] != value:
            raise AssertionError((key, payload[key], value))
    if core["obligationCount"] != 293 or core["sourceCapacity"] != 292:
        raise AssertionError(core)
    if not core["positiveUnitDefect"]:
        raise AssertionError(core)
    if not shore_selected_load + internal_active > ctx.n * len(owner_set):
        raise AssertionError("owner overload missing")
    if not grouped_demand > grouped_capacity:
        raise AssertionError("P1 grouped deficiency missing")
    payload["verdict"] = "PASS_R57_POSITIVE_DEFECT_COMPILED_INTERFACE_COUNTERMODEL"
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
