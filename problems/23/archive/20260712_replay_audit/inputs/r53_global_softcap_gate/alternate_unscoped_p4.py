#!/usr/bin/env python3
"""Independently replay the corrected coherence-free P4 relation on N89."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FIXTURE_GATE = ROOT / "tmp" / "fanout" / "p5_fixtures" / "gate.py"
R35_N24 = ROOT / "tmp" / "fanout" / "r35_24_trade" / "evaluate_trade.py"
N12_PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct" / "n12_pht.py"
sys.path.insert(0, str(HERE))
import global_softcap as soft  # noqa: E402


def canonical_sha(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def load_fixture_module():
    spec = importlib.util.spec_from_file_location("r53_alt_fixture", FIXTURE_GATE)
    if spec is None or spec.loader is None:
        raise RuntimeError(FIXTURE_GATE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def unscoped_p4(ctx, state, owners):
    allowed = set(range(ctx.n)) - state.selected
    comp_id, components, component_masks = soft._components(
        ctx.n, ctx.blue, allowed
    )
    boundaries = []
    for component in components:
        boundary = set()
        for x in component:
            boundary.update(y for y in ctx.blue_adj[x] if y in state.selected)
        boundaries.append(boundary)
    eligible = []
    for boundary in boundaries:
        mask = 0
        for index, owner in enumerate(owners):
            if any(state.pair[owner][a] > 0 for a in boundary):
                mask |= 1 << index
        eligible.append(mask)
    relation = {}
    checked = 0
    negative = 0
    for left, xs in enumerate(components):
        if not eligible[left]:
            continue
        for right, ys in enumerate(components):
            owner_mask = eligible[left] & eligible[right]
            if not owner_mask:
                continue
            nonnegative = ctx.sigma(
                component_masks[left] | component_masks[right]
            ) >= 0
            for x in xs:
                for y in ys:
                    if x == y or state.pair[x][y] != 0:
                        continue
                    checked += 1
                    if not nonnegative:
                        negative += 1
                        continue
                    base = ctx.n * x + y
                    relation[base] = relation.get(base, 0) | owner_mask
    return relation, {
        "components": len(components),
        "nonemptyBoundaries": sum(bool(item) for item in boundaries),
        "checkedOrderedBases": checked,
        "negativeOrderedBases": negative,
        "componentEqualityRequired": False,
    }


def main() -> int:
    fixtures = load_fixture_module()
    fixture = fixtures.build_89()
    ctx = soft.make_graph_context(fixture.n, fixture.blue, fixture.bad)
    state = soft.reconstruct_state(ctx, fixture.rows)
    owners, demand = soft.global_demands(state)

    relations = {}
    audits = {}
    builders = (
        ("P1_sameFirst", soft._p1),
        ("P2_commonBad", soft._p2_common_bad),
        ("P3_rowCompanion", soft._p3),
        ("commonBlue", soft._common_blue),
        ("P4_unscopedOutsideAttachment", unscoped_p4),
        ("P5_quiescentAttachment", soft._p5),
    )
    union = {}
    for name, builder in builders:
        relation, audit = builder(ctx, state, owners)
        relations[name] = relation
        audits[name] = audit
        soft._merge_relation(union, relation)
    flow, assigned = soft.solve_grouped_flow(
        ctx.n,
        owners,
        demand,
        union,
        state.active_edges,
        extract_assignment=True,
    )

    records = []
    source_keys = []
    owner_index = {owner: index for index, owner in enumerate(owners)}
    for owner in owners:
        obligations = list(soft.collision_obligations(state, owner))
        sources = sorted(assigned[owner])
        for obligation, source in zip(obligations, sources):
            x, y, _half = source
            bit = 1 << owner_index[owner]
            base = ctx.n * x + y
            families = [
                name
                for name, relation in relations.items()
                if relation.get(base, 0) & bit
            ]
            records.append(
                {
                    "obligation": list(obligation),
                    "source": list(source),
                    "families": families,
                }
            )
            source_keys.append(source)
    checks = {
        "fullFlow": flow["defect"] == 0 and len(records) == sum(demand),
        "actualFreeHalfSinks": all(
            x != y and state.pair[x][y] == 0 for x, y, _half in source_keys
        ),
        "unitKeyCapacity": len(source_keys) == len(set(source_keys)),
        "eligible": all(record["families"] for record in records),
        "activeEdgeCapacityTwo": not state.active_edges,
    }
    if not all(checks.values()):
        raise AssertionError(checks)

    def scalar_evaluation(local_ctx, rows):
        local_state = soft.reconstruct_state(local_ctx, rows)
        local_owners, local_demand = soft.global_demands(local_state)
        local_union = {}
        for _name, builder in builders:
            relation, _audit = builder(local_ctx, local_state, local_owners)
            soft._merge_relation(local_union, relation)
        local_flow, _assigned = soft.solve_grouped_flow(
            local_ctx.n,
            local_owners,
            local_demand,
            local_union,
            local_state.active_edges,
        )
        return {
            "globalDemand": sum(local_demand),
            "maximumFlow": local_flow["maximumFlow"],
            "defect": local_flow["defect"],
            "shoreOwners": local_flow["minCutSourceOwners"],
        }

    r1_n24 = fixtures.build_24()
    r35 = load_module("r53_alt_r35", R35_N24)
    r35_ctx = soft.make_graph_context(r35.N, r35.BLUE, r35.BAD)
    r35_trade_state = (0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 31, 44)
    r35_trade_rows = tuple(
        r35.ROW_FAMILIES[index][choice]
        for index, choice in enumerate(r35_trade_state)
    )
    r35_states = {tuple(r35.DISPLAYED)}
    for atom, radix in enumerate(r35.RADICES):
        for choice in range(radix):
            candidate = list(r35.DISPLAYED)
            candidate[atom] = choice
            r35_states.add(tuple(candidate))
    r35_local = []
    for candidate in sorted(r35_states):
        rows = tuple(
            r35.ROW_FAMILIES[index][choice]
            for index, choice in enumerate(candidate)
        )
        result = scalar_evaluation(r35_ctx, rows)
        r35_local.append((result["defect"], candidate, result))
    r35_local.sort(key=lambda item: (item[0], item[1]))

    n12 = load_module("r53_alt_n12", N12_PHT)
    n, edges = n12.dec("K??E@cyjFgWk")
    info = n12.loads(n, edges)
    if info is None:
        raise AssertionError("N12 cut unavailable")
    n12_families = n12.shortest_row_families(info)
    diagnostics = {
        "n12_common_blue_choice_0_4_7_9": scalar_evaluation(
            soft.make_graph_context(n, info["Bset"], info["Mset"]),
            n12.rows_for_choice(n12_families, (0, 4, 7, 9)),
        ),
        "n24_r1_fixed_rows": scalar_evaluation(
            soft.make_graph_context(r1_n24.n, r1_n24.blue, r1_n24.bad),
            r1_n24.rows,
        ),
        "n89_singleton_row_database": {
            "globalDemand": sum(demand),
            "maximumFlow": flow["maximumFlow"],
            "defect": flow["defect"],
            "shoreOwners": flow["minCutSourceOwners"],
        },
        "n24_r35_displayed": scalar_evaluation(r35_ctx, r35.DISPLAYED_ROWS),
        "n24_r35_old_one_row_trade": scalar_evaluation(
            r35_ctx, r35_trade_rows
        ),
        "n24_r35_hamming_le_one": {
            "statesExhausted": len(r35_states),
            "minimumDefect": r35_local[0][0],
            "minimumState": list(r35_local[0][1]),
            "minimumResult": r35_local[0][2],
        },
    }
    payload = {
        "schema": "R53_N89_UNSCOPED_P4_INDEPENDENT_REPLAY_V2",
        "status": "CORRECTED_MODEL_INDEPENDENT_REPLAY_PASS",
        "relationComparedWithArchive": (
            "P4 drops the archived strict selected-component equality; this "
            "is the same coherence-free relation used by the corrected model"
        ),
        "globalDemand": sum(demand),
        "maximumFlow": flow["maximumFlow"],
        "defect": flow["defect"],
        "checks": checks,
        "familyStats": {
            name: soft._relation_stats(relations[name], audits[name])
            for name, _builder in builders
        },
        "namedDiagnostics": diagnostics,
        "assignments": records,
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    output = HERE / "n89_unscoped_p4_alternate.json"
    output.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii"
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "demand": payload["globalDemand"],
                "flow": payload["maximumFlow"],
                "defect": payload["defect"],
                "canonicalPayloadSha256": payload["canonicalPayloadSha256"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
