"""Exact audits for the R33 anchored dense-blocker branch.

This script does not infer a collision-defect trade from a repeated state or
from a locked endpoint pair.  It checks only finite row/source counts and, for
small fixtures, whether a locked pair can be removed by a simultaneous legal
row reassignment.  Such an unlocking reassignment is deliberately not called
a CheckedCollisionDefectTrade.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
P5_DIR = ROOT / "tmp" / "fanout" / "p5_n12_census"
R32 = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
R29_LEAD = ROOT / "tmp" / "fanout" / "r29_gate" / "lead"

for path in (WRITEUP, PHT, P5_DIR, R32, R29_LEAD):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import (  # noqa: E402
    dec,
    graph6_for_orders,
    loads,
)
from _codex_r20_two_row_exchange_gate import (  # noqa: E402
    shortest_row_families,
)
from _codex_r23_heavy_alltuple_descent_gate import (  # noqa: E402
    rows_for_choice,
)
from collision_only_core import analyze_collision_only  # noqa: E402
from fullbank_core import (  # noqa: E402
    collision_obligations,
    collision_owners,
    project_masks,
)
import p5_core as p5  # noqa: E402
import r29_lead_gate  # noqa: E402


Edge = tuple[int, int]
Row = tuple[int, ...]


def edge(x: int, y: int) -> Edge:
    return (x, y) if x < y else (y, x)


def choose2(n: int) -> int:
    return n * (n - 1) // 2


def ceil_div(a: int, b: int) -> int:
    return -((-a) // b)


def merge_masks(*relations: dict[int, int]) -> dict[int, int]:
    out: dict[int, int] = {}
    for relation in relations:
        for source, mask in relation.items():
            out[source] = out.get(source, 0) | mask
    return out


def row_cooccurrences(rows: Iterable[Row]) -> Counter[Edge]:
    counts: Counter[Edge] = Counter()
    for row in rows:
        assert len(row) == 5 and len(set(row)) == 5
        counts.update(edge(x, y) for x, y in itertools.combinations(row, 2))
    return counts


def signed_degrees(
    n: int, blue: set[Edge], bad: set[Edge]
) -> tuple[list[int], dict[Edge, int]]:
    degree = [0] * n
    signs: dict[Edge, int] = {}
    for x, y in blue:
        signs[(x, y)] = 1
        degree[x] += 1
        degree[y] += 1
    for x, y in bad:
        signs[(x, y)] = -1
        degree[x] -= 1
        degree[y] -= 1
    return degree, signs


def sigma_pair(
    x: int, y: int, degree: list[int], signs: dict[Edge, int]
) -> int:
    return degree[x] + degree[y] - 2 * signs.get(edge(x, y), 0)


def triangle_free(n: int, graph: set[Edge]) -> bool:
    adjacency = [set() for _ in range(n)]
    for x, y in graph:
        adjacency[x].add(y)
        adjacency[y].add(x)
    return all(not (adjacency[x] & adjacency[y]) for x, y in graph)


def row_choice_indices(
    rows: tuple[Row, ...], families: tuple[tuple[Row, ...], ...]
) -> tuple[int, ...]:
    return tuple(family.index(row) for row, family in zip(rows, families))


def lock_mobility(
    locked_pairs: set[Edge],
    rows: tuple[Row, ...],
    families: tuple[tuple[Row, ...], ...] | None,
) -> dict:
    if families is None:
        return {
            "classified": False,
            "unlockablePairs": None,
            "forcedPairs": None,
            "firstUnlockingChange": None,
        }

    current = row_choice_indices(rows, families)
    unlockable = 0
    forced = 0
    first_change = None
    for pair in sorted(locked_pairs):
        witnesses = [
            index for index, row in enumerate(rows) if set(pair) <= set(row)
        ]
        assert witnesses
        replacements: list[tuple[int, int, int]] = []
        for index in witnesses:
            candidates = [
                candidate
                for candidate, row in enumerate(families[index])
                if not set(pair) <= set(row)
            ]
            if not candidates:
                break
            replacements.append((index, current[index], candidates[0]))
        else:
            unlockable += 1
            if first_change is None:
                first_change = {
                    "pair": list(pair),
                    "changes": [list(item) for item in replacements],
                }
            continue
        forced += 1
    assert unlockable + forced == len(locked_pairs)
    return {
        "classified": True,
        "unlockablePairs": unlockable,
        "forcedPairs": forced,
        "firstUnlockingChange": first_change,
    }


def endpoint_shadow_audit(
    *,
    n: int,
    blue: set[Edge],
    bad: set[Edge],
    rows: tuple[Row, ...],
    atoms: tuple[Edge, ...],
    shore: tuple[int, ...],
    demand: int,
    reach: int,
    collision_by_owner: dict[int, int],
    active_vertices: set[int],
    demanded_active_edges: set[Edge],
    families: tuple[tuple[Row, ...], ...] | None = None,
    operational_p13: dict[int, int] | None = None,
    operational_owner_order: tuple[int, ...] | None = None,
    operational_base_labels: dict[int, int] | None = None,
    operational_owner_components: tuple[int, ...] | None = None,
) -> dict:
    """Audit the exact endpoint-shadow source family for one Hall shore."""
    shore_set = set(shore)
    assert shore and reach < demand
    assert len(rows) == len(atoms)
    assert len(set(atoms)) == len(atoms)
    assert all(edge(row[0], row[-1]) == atom for row, atom in zip(rows, atoms))
    assert all(
        edge(x, y) in blue
        for row in rows
        for x, y in zip(row, row[1:])
    )

    cooccur = row_cooccurrences(rows)
    degree, signs = signed_degrees(n, blue, bad)
    row_sets = tuple(set(row) for row in rows)

    terminal_by_owner: dict[int, set[int]] = {}
    support_by_owner: dict[int, set[int]] = {}
    row_count_by_owner: dict[int, int] = {}
    collision_identity: dict[str, dict] = {}
    for owner in shore:
        owner_rows = [
            (row, atom)
            for row, atom in zip(rows, atoms)
            if owner in row
        ]
        terminals = {
            endpoint
            for _, atom in owner_rows
            for endpoint in atom
            if endpoint not in shore_set
        }
        support = {vertex for row, _ in owner_rows for vertex in row}
        row_count = len(owner_rows)
        reconstructed = 2 * (5 * row_count - len(support))
        assert reconstructed == collision_by_owner[owner]
        terminal_by_owner[owner] = terminals
        support_by_owner[owner] = support
        row_count_by_owner[owner] = row_count
        collision_identity[str(owner)] = {
            "rowsContainingOwner": row_count,
            "distinctCooccurringVertices": len(support),
            "externalTerminalEndpoints": len(terminals),
            "collision": reconstructed,
        }

    W = set().union(*terminal_by_owner.values()) if shore else set()
    assert not (W & shore_set)

    C: dict[int, set[int]] = {
        owner: {w for w in W if cooccur[edge(owner, w)] > 0}
        for owner in shore
    }
    incidence = sum(len(C[owner]) for owner in shore)
    q_uw = sum(cooccur[edge(owner, w)] for owner in shore for w in W)
    repeated = q_uw - incidence
    missing = len(shore) * len(W) - incidence
    assert repeated == sum(
        max(0, cooccur[edge(owner, w)] - 1)
        for owner in shore
        for w in W
    )

    shadow_owners: dict[Edge, set[int]] = defaultdict(set)
    endpoint_owners: dict[Edge, set[int]] = defaultdict(set)
    for owner in shore:
        for x, y in itertools.combinations(sorted(C[owner]), 2):
            shadow_owners[edge(x, y)].add(owner)
        for x, y in itertools.combinations(
            sorted(terminal_by_owner[owner]), 2
        ):
            endpoint_owners[edge(x, y)].add(owner)
    shadow = set(shadow_owners)
    endpoint_shadow = set(endpoint_owners)
    assert endpoint_shadow <= shadow

    q_w = {
        pair for pair in itertools.combinations(sorted(W), 2)
        if cooccur[edge(*pair)] > 0
    }
    q_w = {edge(*pair) for pair in q_w}
    locked_shadow = shadow & q_w
    free_shadow = shadow - q_w
    locked_endpoint = endpoint_shadow & q_w
    free_endpoint = endpoint_shadow - q_w
    anchored_bad_shadow = shadow & bad
    anchored_bad_endpoint = endpoint_shadow & bad
    assert anchored_bad_shadow <= locked_shadow
    assert anchored_bad_endpoint <= locked_endpoint

    p1_keys: set[tuple[int, int, int]] = set()
    p1_half0_reserved = 0
    for owner in shore:
        for w in W:
            if cooccur[edge(owner, w)] != 0:
                continue
            p1_keys.add((owner, w, 1))
            if edge(owner, w) in demanded_active_edges and owner in active_vertices:
                p1_half0_reserved += 1
            else:
                p1_keys.add((owner, w, 0))

    p3_keys: set[tuple[int, int, int]] = set()
    p3_half0_reserved = 0
    for x, y in sorted(free_shadow):
        witnesses = shadow_owners[(x, y)]
        assert witnesses
        assert sigma_pair(x, y, degree, signs) >= 0
        for a, b in ((x, y), (y, x)):
            p3_keys.add((a, b, 1))
            if edge(a, b) in demanded_active_edges and a in active_vertices:
                p3_half0_reserved += 1
            else:
                p3_keys.add((a, b, 0))

    assert p1_keys.isdisjoint(p3_keys)
    guaranteed_keys = p1_keys | p3_keys
    half1_keys = {
        key for key in guaranteed_keys if key[2] == 1
    }
    operational_formula = (
        2 * missing
        - p1_half0_reserved
        + 4 * len(free_shadow)
        - p3_half0_reserved
    )
    assert len(guaranteed_keys) == operational_formula
    half1_formula = missing + 2 * len(free_shadow)
    assert len(half1_keys) == half1_formula <= operational_formula

    coherent_guaranteed_keys = set(guaranteed_keys)
    coherent_half1_keys = set(half1_keys)

    if operational_p13 is not None:
        assert operational_owner_order is not None
        assert operational_base_labels is not None
        assert operational_owner_components is not None
        shore_mask = sum(
            1 << operational_owner_order.index(owner) for owner in shore
        )
        coherent_guaranteed_keys.clear()
        coherent_half1_keys.clear()
        for x, y, half in sorted(guaranteed_keys):
            sid = p5.source_id(n, x, y, half)
            mask = operational_p13.get(sid, 0)
            label = operational_base_labels.get(sid >> 1)
            if label is not None:
                mask &= sum(
                    1 << index
                    for index, component in enumerate(
                        operational_owner_components
                    )
                    if component == label
                )
            if mask & shore_mask:
                coherent_guaranteed_keys.add((x, y, half))
                if half == 1:
                    coherent_half1_keys.add((x, y, half))

    coherence_excluded = operational_formula - len(coherent_guaranteed_keys)
    half1_coherence_excluded = half1_formula - len(coherent_half1_keys)
    assert coherence_excluded >= 0 and half1_coherence_excluded >= 0
    assert len(coherent_guaranteed_keys) <= reach
    assert len(coherent_half1_keys) <= reach

    row_pair_capacity = sum(choose2(len(row_set & W)) for row_set in row_sets)
    assert len(q_w) <= row_pair_capacity <= 10 * len(rows)
    assert 2 * repeated <= demand
    assert q_uw <= 6 * len(rows)

    exact_shadow_lower = missing + 2 * len(free_shadow)
    section7_shadow_floor = ceil_div(
        sum(choose2(len(C[owner])) for owner in shore), len(shore)
    )
    section7_lower = missing + 2 * max(
        0, section7_shadow_floor - len(q_w)
    )
    assert section7_lower <= exact_shadow_lower

    half1_lock_rhs = missing + 2 * len(shadow) - demand + 1
    assert (
        2 * len(locked_shadow) + half1_coherence_excluded
        >= half1_lock_rhs
    )
    operational_lock_rhs = (
        2 * missing + 4 * len(shadow) - demand + 1
    )
    total_reservations = p1_half0_reserved + p3_half0_reserved
    assert (
        4 * len(locked_shadow) + total_reservations + coherence_excluded
        >= operational_lock_rhs
    )
    forced_total_locks = max(
        0,
        ceil_div(
            operational_lock_rhs
            - total_reservations
            - coherence_excluded,
            4,
        ),
    )
    forced_nonbad_locks = max(0, forced_total_locks - len(anchored_bad_shadow))

    dense_capacity_lhs = (
        len(shore) * len(W) + 2 * len(shadow) + repeated
    )
    dense_capacity_rhs = (
        demand - 1 + 26 * len(rows) + half1_coherence_excluded
    )
    assert dense_capacity_lhs <= dense_capacity_rhs

    endpoint_nonedge_free = sum(
        edge(*pair) not in blue and edge(*pair) not in bad
        for pair in free_endpoint
    )
    mobility = lock_mobility(locked_endpoint, rows, families)

    return {
        "shore": list(shore),
        "demand": demand,
        "reach": reach,
        "defect": demand - reach,
        "rows": len(rows),
        "W": len(W),
        "incidence_iUW": incidence,
        "load_qUW": q_uw,
        "repeated_eUW": repeated,
        "missingIncidences_A": missing,
        "pW": len(q_w),
        "rowPairCapacity": row_pair_capacity,
        "shadowPairs": len(shadow),
        "shadowLocked": len(locked_shadow),
        "shadowAnchoredBadLocks": len(anchored_bad_shadow),
        "shadowAdditionalLocks": len(locked_shadow - anchored_bad_shadow),
        "shadowFree": len(free_shadow),
        "endpointShadowPairs": len(endpoint_shadow),
        "endpointLocked": len(locked_endpoint),
        "endpointAnchoredBadLocks": len(anchored_bad_endpoint),
        "endpointAdditionalLocks": len(locked_endpoint - anchored_bad_endpoint),
        "endpointFree": len(free_endpoint),
        "endpointFreeGraphNonedges": endpoint_nonedge_free,
        "p1Half0Reserved": p1_half0_reserved,
        "p3Half0Reserved": p3_half0_reserved,
        "half1GuaranteedKeys": half1_formula,
        "operationalGuaranteedKeys": operational_formula,
        "half1CoherenceExcludedKeys": half1_coherence_excluded,
        "coherenceExcludedKeys": coherence_excluded,
        "coherentHalf1GuaranteedKeys": len(coherent_half1_keys),
        "coherentOperationalGuaranteedKeys": len(coherent_guaranteed_keys),
        "reachMinusOperationalFloor": reach - len(coherent_guaranteed_keys),
        "section7Lower": section7_lower,
        "exactShadowHalf1Lower": exact_shadow_lower,
        "half1LockRhs": half1_lock_rhs,
        "operationalLockRhs": operational_lock_rhs,
        "operationalForcedTotalLocks": forced_total_locks,
        "operationalForcedNonbadLocks": forced_nonbad_locks,
        "denseCapacityLhs": dense_capacity_lhs,
        "denseCapacityRhs": dense_capacity_rhs,
        "collisionIdentity": collision_identity,
        "terminalEndpointSets": {
            str(owner): sorted(terminals)
            for owner, terminals in terminal_by_owner.items()
        },
        "lockMobility": mobility,
    }


def small_tuple_audit(
    *,
    ctx: p5.GraphContext,
    info: dict,
    families: tuple[tuple[Row, ...], ...],
    choice: tuple[int, ...],
) -> tuple[dict, dict]:
    rows = rows_for_choice(families, choice)
    analysis = analyze_collision_only(ctx, rows, details=True)
    assert analysis["collisionDefect"] > 0
    state = p5.reconstruct_state(ctx, rows)
    owners = collision_owners(state)
    masks = p5.relation_masks(ctx, state)
    raw = project_masks(
        state,
        merge_masks(masks["p13"], masks["p4"], masks["p5"]),
        owners,
    )
    labels = {int(base): int(component) for base, component in analysis["baseLabels"]}
    owner_components = tuple(state.selected_comp[owner] for owner in owners)
    final_raw = {}
    for source, mask in raw.items():
        label = labels.get(source >> 1)
        if label is not None:
            mask &= sum(
                1 << index
                for index, component in enumerate(owner_components)
                if component == label
            )
        if mask:
            final_raw[source] = mask
    shore = tuple(analysis["hallWitness"]["owners"])
    shore_mask = sum(1 << owners.index(owner) for owner in shore)
    raw_reach = sum(bool(mask & shore_mask) for mask in final_raw.values())
    assert raw_reach == analysis["hallWitness"]["reach"]

    audit = endpoint_shadow_audit(
        n=ctx.n,
        blue=set(ctx.blue),
        bad=set(ctx.bad),
        rows=rows,
        atoms=tuple(info["M"]),
        shore=shore,
        demand=analysis["hallWitness"]["demand"],
        reach=raw_reach,
        collision_by_owner=state.collision,
        active_vertices=set(state.active_vertices),
        demanded_active_edges=set(state.demanded_active_edges),
        families=families,
        operational_p13=masks["p13"],
        operational_owner_order=state.owners,
        operational_base_labels=labels,
        operational_owner_components=tuple(
            state.selected_comp[owner] for owner in state.owners
        ),
    )
    unlocking = audit["lockMobility"]["firstUnlockingChange"]
    if unlocking is not None:
        new_choice = list(choice)
        for index, old_choice, new_row_choice in unlocking["changes"]:
            assert new_choice[index] == old_choice
            new_choice[index] = new_row_choice
        new_rows = rows_for_choice(families, tuple(new_choice))
        new_analysis = analyze_collision_only(ctx, new_rows)
        audit["lockMobility"].update({
            "firstUnlockingNewChoice": new_choice,
            "firstUnlockingNewDefect": new_analysis["collisionDefect"],
            "firstUnlockingDefectChange": (
                new_analysis["collisionDefect"] - analysis["collisionDefect"]
            ),
        })
    summary = {
        "choice": list(choice),
        "collisionDemand": analysis["collisionDemand"],
        "collisionDefect": analysis["collisionDefect"],
        "coherenceAutomatic": analysis["coherenceAutomatic"],
        "coherenceLabels": len(labels),
        "hallShore": list(shore),
        "hallDemand": analysis["hallWitness"]["demand"],
        "hallReach": raw_reach,
    }
    return summary, audit


def aggregate_failure_audits(audits: list[dict]) -> dict:
    assert audits
    canonical = json.dumps(audits, sort_keys=True, separators=(",", ":"))
    return {
        "failedTuples": len(audits),
        "shoreSizeHistogram": dict(sorted(Counter(
            len(audit["shore"]) for audit in audits
        ).items())),
        "defectHistogram": dict(sorted(Counter(
            audit["defect"] for audit in audits
        ).items())),
        "minEndpointShadowPairs": min(
            audit["endpointShadowPairs"] for audit in audits
        ),
        "maxEndpointShadowPairs": max(
            audit["endpointShadowPairs"] for audit in audits
        ),
        "minOperationalFloorSlack": min(
            audit["reachMinusOperationalFloor"] for audit in audits
        ),
        "maxOperationalFloorSlack": max(
            audit["reachMinusOperationalFloor"] for audit in audits
        ),
        "tuplesWithNoEndpointShadow": sum(
            audit["endpointShadowPairs"] == 0 for audit in audits
        ),
        "tuplesWithEndpointLocks": sum(
            audit["endpointLocked"] > 0 for audit in audits
        ),
        "tuplesWithUnlockableEndpointLock": sum(
            (audit["lockMobility"]["unlockablePairs"] or 0) > 0
            for audit in audits
        ),
        "tuplesWithForcedEndpointLock": sum(
            (audit["lockMobility"]["forcedPairs"] or 0) > 0
            for audit in audits
        ),
        "tuplesWithCoherenceExclusions": sum(
            audit["coherenceExcludedKeys"] > 0 for audit in audits
        ),
        "tuplesWithAdditionalEndpointLocks": sum(
            audit["endpointAdditionalLocks"] > 0 for audit in audits
        ),
        "tuplesForcingNonbadShadowLocks": sum(
            audit["operationalForcedNonbadLocks"] > 0 for audit in audits
        ),
        "tuplesForcingNonbadWithUnlockableEndpointLock": sum(
            audit["operationalForcedNonbadLocks"] > 0
            and (audit["lockMobility"]["unlockablePairs"] or 0) > 0
            for audit in audits
        ),
        "tuplesForcingNonbadWithoutUnlockableEndpointLock": sum(
            audit["operationalForcedNonbadLocks"] > 0
            and not (audit["lockMobility"]["unlockablePairs"] or 0) > 0
            for audit in audits
        ),
        "firstUnlockingChangesLoweringDefect": sum(
            audit["lockMobility"].get("firstUnlockingDefectChange", 0) < 0
            for audit in audits
        ),
        "firstUnlockingChangesPreservingDefect": sum(
            audit["lockMobility"].get("firstUnlockingDefectChange") == 0
            for audit in audits
        ),
        "firstUnlockingChangesIncreasingDefect": sum(
            audit["lockMobility"].get("firstUnlockingDefectChange", 0) > 0
            for audit in audits
        ),
        "maxCoherenceExcludedKeys": max(
            audit["coherenceExcludedKeys"] for audit in audits
        ),
        "maxOperationalForcedNonbadLocks": max(
            audit["operationalForcedNonbadLocks"] for audit in audits
        ),
        "auditSha256": hashlib.sha256(canonical.encode()).hexdigest(),
    }


def audit_materialized_small_failures() -> dict:
    records = []
    for order, filename in (
        (10, "census_n9_n10.json"),
        (11, "census_n11.json"),
        (12, "census_n12.json"),
    ):
        payload = json.loads((R32 / filename).read_text())
        record = payload["total"]["first"]["firstTupleFalsifier"]
        assert record["order"] == order
        n, graph_edges = dec(record["g6"])
        info = loads(n, graph_edges)
        assert info is not None
        families = shortest_row_families(info)
        sizes = tuple(len(family) for family in families)
        assert math.prod(sizes) == record["tupleCount"]
        assert triangle_free(n, set(info["Bset"]) | set(info["Mset"]))
        ctx = p5.make_graph_context(n, info["Bset"], info["Mset"])

        failed: list[dict] = []
        representative = None
        for choice in itertools.product(*(range(size) for size in sizes)):
            rows = rows_for_choice(families, choice)
            quick = analyze_collision_only(ctx, rows)
            if quick["collisionDefect"] == 0:
                continue
            summary, audit = small_tuple_audit(
                ctx=ctx, info=info, families=families, choice=choice
            )
            failed.append(audit)
            if tuple(choice) == tuple(record["choice"]):
                representative = {"summary": summary, "audit": audit}
        assert representative is not None
        records.append({
            "order": order,
            "g6": record["g6"],
            "familySizes": list(sizes),
            "tupleCount": math.prod(sizes),
            "representative": representative,
            "allFailuresOnMaterializedGraph": aggregate_failure_audits(failed),
        })
    return {
        "scope": (
            "all failed tuples on the three graphs whose first failures are "
            "materialized in the R32 census JSON files"
        ),
        "graphs": records,
        "failedTuplesAudited": sum(
            record["allFailuresOnMaterializedGraph"]["failedTuples"]
            for record in records
        ),
    }


def scan_failure_chunk(tasks: list[tuple[int, int, str]]) -> dict:
    failures = []
    examined = 0
    eligible = 0
    for order, graph_ordinal, g6 in tasks:
        n, graph_edges = dec(g6)
        info = loads(n, graph_edges)
        if info is None or any(length != 5 for length in info["ell"].values()):
            continue
        eligible += 1
        families = shortest_row_families(info)
        sizes = tuple(len(family) for family in families)
        ctx = p5.make_graph_context(n, info["Bset"], info["Mset"])
        for tuple_index, choice in enumerate(
            itertools.product(*(range(size) for size in sizes))
        ):
            examined += 1
            rows = rows_for_choice(families, choice)
            analysis = analyze_collision_only(ctx, rows)
            if analysis["collisionDefect"] > 0:
                failures.append({
                    "order": order,
                    "graphOrdinal": graph_ordinal,
                    "g6": g6,
                    "tupleIndex": tuple_index,
                    "choice": list(choice),
                    "defect": analysis["collisionDefect"],
                })
    return {"eligible": eligible, "examined": examined, "failures": failures}


def audit_full_census(workers: int) -> dict:
    started = time.time()
    graph6, generated = graph6_for_orders(5, 12)
    ordinal = Counter()
    tasks = []
    for g6 in graph6:
        order = dec(g6)[0]
        tasks.append((order, ordinal[order], g6))
        ordinal[order] += 1
    chunks = [tasks[index:index + 32] for index in range(0, len(tasks), 32)]
    failures = []
    eligible = 0
    examined = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for result in pool.map(scan_failure_chunk, chunks, chunksize=1):
            eligible += result["eligible"]
            examined += result["examined"]
            failures.extend(result["failures"])

    expected_by_order = {10: 32, 11: 120, 12: 145}
    actual_by_order = Counter(record["order"] for record in failures)
    assert dict(sorted(actual_by_order.items())) == expected_by_order
    assert len(failures) == 297
    assert len({record["g6"] for record in failures}) == 29
    assert examined == 40_228_399
    assert eligible == 992_618

    cache: dict[str, tuple[p5.GraphContext, dict, tuple[tuple[Row, ...], ...]]] = {}
    audits = []
    summaries = []
    by_order_audits: dict[int, list[dict]] = defaultdict(list)
    for record in failures:
        g6 = record["g6"]
        if g6 not in cache:
            n, graph_edges = dec(g6)
            info = loads(n, graph_edges)
            assert info is not None
            families = shortest_row_families(info)
            ctx = p5.make_graph_context(n, info["Bset"], info["Mset"])
            cache[g6] = ctx, info, families
        ctx, info, families = cache[g6]
        summary, audit = small_tuple_audit(
            ctx=ctx,
            info=info,
            families=families,
            choice=tuple(record["choice"]),
        )
        assert summary["collisionDefect"] == record["defect"]
        audits.append(audit)
        by_order_audits[record["order"]].append(audit)
        summaries.append({**record, **summary})

    failure_digest = hashlib.sha256(
        json.dumps(summaries, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    aggregate = aggregate_failure_audits(audits)
    first_forced_index = next(
        index
        for index, audit in enumerate(audits)
        if audit["operationalForcedNonbadLocks"] > 0
    )
    return {
        "scope": "all 297 failed tuples in the exact R32 N=5..12 census",
        "workers": workers,
        "elapsedSeconds": round(time.time() - started, 3),
        "generatedGraphs": sum(generated.values()),
        "eligibleGraphs": eligible,
        "examinedTuples": examined,
        "graphsWithFailures": len(cache),
        "failureRecordsSha256": failure_digest,
        "aggregate": aggregate,
        "byOrder": {
            str(order): aggregate_failure_audits(by_order_audits[order])
            for order in sorted(by_order_audits)
        },
        "firstFailureByOrder": {
            str(order): next(
                summary for summary in summaries if summary["order"] == order
            )
            for order in sorted(by_order_audits)
        },
        "firstForcedNonbadLock": {
            "record": summaries[first_forced_index],
            "audit": audits[first_forced_index],
        },
    }


def audit_2943() -> dict:
    data = r29_lead_gate.build()
    rows = tuple(data["rows"])
    atoms = tuple(data["atoms"])
    certificate = json.loads(
        (
            ROOT
            / "tmp"
            / "fanout"
            / "r33_trade_2943"
            / "certificate_replay.json"
        ).read_text()
    )
    local = certificate["tuples"]["allLocal"]
    hub_cut = next(
        cut for cut in local["hubHallCuts"] if cut["shoreMask"] == 7
    )
    collision = {
        int(owner): value
        for owner, value in local["collisionDemandByOwner"].items()
    }
    audit = endpoint_shadow_audit(
        n=data["n"],
        blue=set(data["blue"]),
        bad=set(data["bad"]),
        rows=rows,
        atoms=atoms,
        shore=tuple(hub_cut["owners"]),
        demand=hub_cut["demand"],
        reach=hub_cut["reach"],
        collision_by_owner=collision,
        active_vertices=set(range(data["n"])),
        demanded_active_edges=set(),
        families=None,
    )

    locked_pairs = audit["endpointLocked"]
    assert locked_pairs == 676
    assert audit["endpointFree"] == 650
    assert audit["operationalGuaranteedKeys"] == 2600
    lead_result = json.loads((R29_LEAD / "lead_result.json").read_text())
    assert lead_result["counts"]["rowHistogram"] == {"1": 707, "680": 676}
    assert lead_result["globalSelectorLandscape"]["familyShape"] == {
        "anchorRowsPerFamily": 676,
        "families": 676,
        "localRowsPerFamily": 4,
    }
    assert data["selectorStart"] == 676 and data["selectorStop"] == 1352
    # Every locked terminal pair is witnessed by one of the first 676 traffic
    # rows.  The remaining 707 nonselector families are exactly the singleton
    # side of the certified 707/676 row-family histogram.
    terminal_union = set().union(*(
        set(values) for values in audit["terminalEndpointSets"].values()
    ))
    cooccur = row_cooccurrences(rows)
    locked = {
        edge(x, y)
        for x, y in itertools.combinations(sorted(terminal_union), 2)
        if cooccur[edge(x, y)] > 0
    }
    witness_indices = {
        index
        for pair in locked
        for index, row in enumerate(rows)
        if set(pair) <= set(row)
    }
    assert witness_indices == set(range(data["selectorStart"]))
    audit["lockMobility"] = {
        "classified": True,
        "unlockablePairs": 0,
        "forcedPairs": 676,
        "firstUnlockingChange": None,
        "reason": (
            "all lock witnesses are the 676 rigid traffic families; the "
            "known 676-row defect trade changes selector families instead"
        ),
    }
    return {
        "tuple": "canonical-all-local",
        "certificateDefect": local["collisionDefect"],
        "knownTradeChangedRows": certificate["trade"]["changedSelectorRows"],
        "audit": audit,
    }


def first_forced_checked_trade_payload() -> dict:
    """Build one literal finite CheckedCollisionDefectTrade-shaped payload.

    This is a fixture certificate, not a universal theorem and not a Lean
    constructor.  Every field needed by the abstract structure is replayed:
    realized old/new rows, a simultaneous family-preserving row change, an
    exact old coherent matching, a coherent new matching, and strict decrease
    of unmatched obligations.
    """
    g6 = "K?ABAaJFdQN_"
    old_choice = (0, 6, 8, 5)
    new_choice = (0, 0, 0, 5)
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    assert info is not None
    families = shortest_row_families(info)
    ctx = p5.make_graph_context(n, info["Bset"], info["Mset"])
    old_rows = rows_for_choice(families, old_choice)
    new_rows = rows_for_choice(families, new_choice)
    changed = [
        index for index, (old, new) in enumerate(zip(old_rows, new_rows))
        if old != new
    ]
    assert changed == [1, 2]
    for index in changed:
        assert old_rows[index] in families[index]
        assert new_rows[index] in families[index]
        assert edge(old_rows[index][0], old_rows[index][-1]) == info["M"][index]
        assert edge(new_rows[index][0], new_rows[index][-1]) == info["M"][index]

    old = analyze_collision_only(ctx, old_rows, details=True)
    new = analyze_collision_only(ctx, new_rows, details=True)
    assert (old["collisionDemand"], old["collisionMatched"], old["collisionDefect"]) == (40, 37, 3)
    assert (new["collisionDemand"], new["collisionMatched"], new["collisionDefect"]) == (0, 0, 0)

    old_state = p5.reconstruct_state(ctx, old_rows)
    old_owners = collision_owners(old_state)
    old_obligations = {
        tuple(obligation)
        for owner in old_owners
        for obligation in collision_obligations(old_state, old_owners)[owner]
    }
    assignment = old["collisionAssignment"]
    matched_obligations = {
        tuple(record["obligation"]) for record in assignment
    }
    assigned_sources = {
        tuple(record["source"]) for record in assignment
    }
    assert len(matched_obligations) == len(assigned_sources) == len(assignment) == 37
    assert matched_obligations <= old_obligations
    unmatched = sorted(old_obligations - matched_obligations)
    assert len(unmatched) == old["collisionDefect"] == 3

    masks = p5.relation_masks(ctx, old_state)
    raw = project_masks(
        old_state,
        merge_masks(masks["p13"], masks["p4"], masks["p5"]),
        old_owners,
    )
    labels = {int(base): int(comp) for base, comp in old["baseLabels"]}
    base_component: dict[int, int] = {}
    explicit_assignment = []
    for record in assignment:
        owner = int(record["obligation"][0])
        owner_index = old_owners.index(owner)
        source = tuple(int(value) for value in record["source"])
        sid = p5.source_id(n, *source)
        base = sid >> 1
        component = old_state.selected_comp[owner]
        if base in labels:
            assert labels[base] == component
        assert raw.get(sid, 0) & (1 << owner_index)
        previous = base_component.setdefault(base, component)
        assert previous == component
        explicit_assignment.append({
            "obligation": record["obligation"],
            "source": record["source"],
            "component": component,
            "eligiblePatterns": record["eligiblePatterns"],
        })

    new_state = p5.reconstruct_state(ctx, new_rows)
    assert not collision_owners(new_state)
    canonical_assignment = json.dumps(
        explicit_assignment, sort_keys=True, separators=(",", ":")
    ).encode()
    return {
        "schema": "R33_FINITE_CHECKED_COLLISION_DEFECT_TRADE_PAYLOAD_V1",
        "scope": "one N=12 failed tuple; no universal claim",
        "g6": g6,
        "atoms": [list(atom) for atom in info["M"]],
        "rowChange": {
            "oldChoice": list(old_choice),
            "newChoice": list(new_choice),
            "changedIndices": changed,
            "oldRows": [list(row) for row in old_rows],
            "newRows": [list(row) for row in new_rows],
            "sameAnchoredFamiliesVerified": True,
        },
        "oldMatching": {
            "demand": len(old_obligations),
            "matched": len(matched_obligations),
            "unmatched": [list(obligation) for obligation in unmatched],
            "unmatchedCount": len(unmatched),
            "exactDefect": old["collisionDefect"],
            "hallWitness": old["hallWitness"],
            "baseLabels": old["baseLabels"],
            "assignment": explicit_assignment,
            "assignmentSha256": hashlib.sha256(canonical_assignment).hexdigest(),
            "sourceInjectiveVerified": True,
            "sourceRealizedVerified": True,
            "baseComponentCoherentVerified": True,
        },
        "newMatching": {
            "demand": 0,
            "matched": 0,
            "unmatched": [],
            "unmatchedCount": 0,
            "assignment": [],
            "coherentEmptyMatchingVerified": True,
        },
        "fewerUnmatched": True,
        "defectDecrease": 3,
    }


def common_endpoint_fan_arithmetic(limit: int = 32) -> dict:
    rows = []
    for t in range(1, limit + 1):
        collision_upper = 8 * (t - 1)
        free_sources_without_locks = 4 * choose2(t)
        if t == 1:
            forced_locks = None
            extra_rows = None
        else:
            forced_locks = max(
                0, choose2(t) - ((collision_upper - 1) // 4)
            )
            expected = max(0, choose2(t - 2))
            assert forced_locks == expected
            extra_rows = ceil_div(forced_locks, 3)
        rows.append({
            "terminalEndpoints": t,
            "collisionUpper": collision_upper,
            "unlockedP3Sources": free_sources_without_locks,
            "locksForcedByPositiveSingletonDefect": forced_locks,
            "extraRowsForcedAtCapacityThree": extra_rows,
            "positiveCollisionPossibleUnderUpperBound": t >= 2,
        })
    assert all(
        row["unlockedP3Sources"] >= row["collisionUpper"]
        for row in rows
        if row["terminalEndpoints"] >= 4
    )
    return {
        "checkedRange": [1, limit],
        "firstTerminalCountExcludedWithoutLocks": 4,
        "rows": rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-census", action="store_true")
    parser.add_argument(
        "--workers", type=int, default=min(61, os.cpu_count() or 1)
    )
    args = parser.parse_args()
    # CPython's Windows ProcessPoolExecutor has a platform maximum of 61.
    if not 1 <= args.workers <= 61:
        parser.error("--workers must be in 1..61 on Windows")
    return args


def main() -> None:
    args = parse_args()
    result = {
        "schema": "R33_ANCHORED_DENSE_BLOCKER_AUDIT_V1",
        "arithmetic": "exact integers and finite sets only",
        "small": (
            audit_full_census(args.workers)
            if args.full_census
            else audit_materialized_small_failures()
        ),
        "fixture2943": audit_2943(),
        "finiteCheckedTradePayload": first_forced_checked_trade_payload(),
        "commonEndpointFan": common_endpoint_fan_arithmetic(),
        "nonClaim": (
            "row unlocking, repeated states, and large p_W are not treated "
            "as CheckedCollisionDefectTrade certificates"
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
