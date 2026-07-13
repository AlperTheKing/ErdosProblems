"""Exact N<=12 census for the strong active-owner probe statement.

For every connected triangle-free graph, ``loads`` pins the connected
Gamma-minimum maximum cut.  On all-length-five instances this program uses
the complete shortest-row database, enumerates the full row product, computes
the exact coherent P1/P3/P4/P5 collision-matching defect, and checks every
tuple attaining the global minimum defect.

Every active owner must have at least one of:

* a valid common-blue probe with sigma >= 2 and both halves unreserved;
* a genuine two-edge detour present in the complete row database; or
* an explicit row tuple with strictly smaller matching defect.

The last alternative is retained in the certificate schema, although it is
necessarily impossible at a correctly computed global defect minimum.  All
arithmetic and matching checks are integral.
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
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITEUP = ROOT / "problems" / "23" / "writeup"
R32 = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
P5 = ROOT / "tmp" / "fanout" / "p5_n12_census"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
for path in (WRITEUP, R32, P5, PHT):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice  # noqa: E402
from collision_only_core import canonical_sha  # noqa: E402
from fullbank_core import (  # noqa: E402
    coherent_collision_match,
    collision_owners,
    project_masks,
)
import p5_core as p5  # noqa: E402


SCHEMA = "R40_STRONG_ACTIVE_OWNER_PROBE_CENSUS_V1"


def edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def merge_relations(*relations: dict[int, int]) -> dict[int, int]:
    merged: dict[int, int] = {}
    for relation in relations:
        for source, mask in relation.items():
            merged[source] = merged.get(source, 0) | mask
    return merged


def coherence_automatic(
    state: p5.TupleState, owners: tuple[int, ...], relation: dict[int, int]
) -> bool:
    components_by_base: dict[int, set[int]] = {}
    for source, mask in relation.items():
        components = components_by_base.setdefault(source >> 1, set())
        for index, owner in enumerate(owners):
            if mask & (1 << index):
                components.add(state.selected_comp[owner])
                if len(components) > 1:
                    return False
    return True


def fast_hall_defect(
    state: p5.TupleState, owners: tuple[int, ...], relation: dict[int, int]
) -> tuple[int, int, int, int]:
    """Return matched, defect, worst owner mask, and worst reach exactly."""
    demand = tuple(state.collision[owner] for owner in owners)
    total = sum(demand)
    count = len(owners)
    full_mask = (1 << count) - 1
    histogram = [0] * (1 << count)
    for mask in relation.values():
        histogram[mask] += 1
    subset = histogram[:]
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


def matching_analysis(ctx: p5.GraphContext, state: p5.TupleState) -> dict:
    """Exact production collision defect, reusing an already rebuilt state."""
    owners = collision_owners(state)
    demand = sum(state.collision[owner] for owner in owners)
    if not owners:
        return {
            "demand": 0,
            "matched": 0,
            "defect": 0,
            "owners": [],
            "sourceKeys": 0,
            "coherenceAutomatic": True,
            "searchNodes": 0,
            "hallOwners": [],
            "hallDemand": 0,
            "hallReach": 0,
        }
    masks = p5.relation_masks(ctx, state)
    raw = project_masks(
        state,
        merge_relations(masks["p13"], masks["p4"], masks["p5"]),
        owners,
    )
    automatic = coherence_automatic(state, owners, raw)
    if automatic:
        matched, defect, worst_mask, worst_reach = fast_hall_defect(
            state, owners, raw
        )
        search_nodes = 0
        hall_demand = sum(
            state.collision[owner]
            for index, owner in enumerate(owners)
            if worst_mask & (1 << index)
        )
    else:
        collision = coherent_collision_match(ctx, state, owners, raw, ())
        matched = collision.matched
        defect = collision.defect
        worst_mask = collision.witness_owner_mask
        worst_reach = collision.witness_reach
        hall_demand = collision.witness_demand
        search_nodes = collision.search_nodes
    return {
        "demand": demand,
        "matched": matched,
        "defect": defect,
        "owners": list(owners),
        "sourceKeys": len(raw),
        "coherenceAutomatic": automatic,
        "searchNodes": search_nodes,
        "hallOwners": [
            owner for index, owner in enumerate(owners)
            if worst_mask & (1 << index)
        ],
        "hallDemand": hall_demand,
        "hallReach": worst_reach,
    }


def active_adjacency(state: p5.TupleState) -> dict[int, list[int]]:
    adjacency = {owner: [] for owner in state.active_vertices}
    for x, y in state.demanded_active_edges:
        adjacency[x].append(y)
        adjacency[y].append(x)
    for neighbors in adjacency.values():
        neighbors.sort()
    return adjacency


def support_adjacency(state: p5.TupleState) -> dict[int, list[int]]:
    adjacency = {owner: [] for owner in state.active_vertices}
    for x, y in state.support:
        if x in adjacency:
            adjacency[x].append(y)
        if y in adjacency:
            adjacency[y].append(x)
    for owner in adjacency:
        adjacency[owner] = sorted(set(adjacency[owner]))
    return adjacency


def row_edges(row: tuple[int, ...]) -> set[tuple[int, int]]:
    return {edge(x, y) for x, y in zip(row, row[1:])}


def selected_support(rows: tuple[tuple[int, ...], ...]) -> set[tuple[int, int]]:
    return set().union(*(row_edges(row) for row in rows))


def support_occurrences(
    rows: tuple[tuple[int, ...], ...], target: tuple[int, int]
) -> int:
    return sum(target in row_edges(row) for row in rows)


def is_reserved(state: p5.TupleState, x: int, y: int, half: int) -> bool:
    return (
        half == 0
        and edge(x, y) in state.demanded_active_edges
        and x in state.active_vertices
    )


def singleton_sigma(ctx: p5.GraphContext, vertex: int) -> int:
    return sum(vertex in item for item in ctx.blue) - sum(
        vertex in item for item in ctx.bad
    )


def classify_owner(
    ctx: p5.GraphContext,
    state: p5.TupleState,
    families: tuple[tuple[tuple[int, ...], ...], ...],
    family_sets: tuple[frozenset[tuple[int, ...]], ...],
    choice: tuple[int, ...],
    owner: int,
    active_adj: dict[int, list[int]],
    support_adj: dict[int, list[int]],
) -> dict:
    probes = []
    successes = []
    active_neighbors = active_adj[owner]
    support_neighbors = support_adj[owner]
    sigma_x = {x: singleton_sigma(ctx, x) for x in active_neighbors}
    sigma_y = {y: singleton_sigma(ctx, y) for y in support_neighbors}
    for x in active_neighbors:
        for y in support_neighbors:
            if x == y:
                continue
            pair_count = state.pair[x][y]
            base = {
                "activeNeighbor": x,
                "supportNeighbor": y,
                "pairCount": pair_count,
                "sigma": ctx.sigma_pair[x][y],
                "singletonSigmaX": sigma_x[x],
                "singletonSigmaY": sigma_y[y],
                "singletonIdentity": (
                    ctx.sigma_pair[x][y] == sigma_x[x] + sigma_y[y]
                ),
            }
            if pair_count == 0:
                sigma = ctx.sigma_pair[x][y]
                reserved = [is_reserved(state, x, y, half) for half in (0, 1)]
                valid = (
                    x in ctx.blue_adj[owner]
                    and y in ctx.blue_adj[owner]
                    and edge(x, y) not in ctx.blue
                    and edge(x, y) not in ctx.bad
                    and sigma >= 2
                    and not any(reserved)
                )
                probe = {
                    **base,
                    "kind": "strongCommonBlue" if valid else "weakFree",
                    "reservedHalves": reserved,
                    "validCommonBlue": valid,
                }
                probes.append(probe)
                if valid:
                    successes.append(probe)
                continue

            covering = []
            for atom, row in enumerate(state.rows):
                if x not in row or y not in row:
                    continue
                separation = abs(row.index(x) - row.index(y))
                candidate = None
                in_complete_db = False
                if separation == 2:
                    left, right = sorted((row.index(x), row.index(y)))
                    replacement = list(row)
                    replacement[left + 1] = owner
                    candidate = tuple(replacement)
                    in_complete_db = (
                        candidate != row and candidate in family_sets[atom]
                    )
                cover = {
                    "atom": atom,
                    "selectedRowIndex": choice[atom],
                    "selectedRow": list(row),
                    "separation": separation,
                    "replacementRow": None if candidate is None else list(candidate),
                    "replacementRowIndex": (
                        families[atom].index(candidate) if in_complete_db else None
                    ),
                    "inCompleteRowDB": in_complete_db,
                }
                if in_complete_db:
                    middle = row[left + 1]
                    old_edges = [edge(x, middle), edge(middle, y)]
                    new_edges = [edge(x, owner), edge(owner, y)]
                    old_occurrences = [
                        support_occurrences(state.rows, item) for item in old_edges
                    ]
                    new_rows = list(state.rows)
                    new_rows[atom] = candidate
                    new_rows_tuple = tuple(new_rows)
                    new_support = selected_support(new_rows_tuple)
                    old_unique = sum(value == 1 for value in old_occurrences)
                    genuinely_new = sum(item not in state.support for item in new_edges)
                    support_delta = len(new_support) - len(state.support)
                    active_precondition = all(
                        item in state.demanded_active_edges
                        and item not in state.support
                        for item in new_edges
                    )
                    fully_unsaturated = old_occurrences == [1, 1]
                    freed_ordered = []
                    if fully_unsaturated:
                        target_state = p5.reconstruct_state(ctx, new_rows_tuple)
                        for a, b in (
                            (middle, x), (x, middle), (middle, y), (y, middle)
                        ):
                            if target_state.pair[a][b] == 0:
                                freed_ordered.append({
                                    "orderedPair": [a, b],
                                    "halves": [
                                        {
                                            "half": half,
                                            "reserved": is_reserved(
                                                target_state, a, b, half
                                            ),
                                        }
                                        for half in (0, 1)
                                    ],
                                })
                    cover["supportMonotonicity"] = {
                        "oldMiddle": middle,
                        "oldEdges": [list(item) for item in old_edges],
                        "newEdges": [list(item) for item in new_edges],
                        "oldEdgeSupportOccurrences": old_occurrences,
                        "oldPairCounts": [
                            state.pair[middle][x], state.pair[middle][y]
                        ],
                        "newEdgesAbsentOldSupport": [
                            item not in state.support for item in new_edges
                        ],
                        "newEdgesActiveBefore": [
                            item in state.demanded_active_edges for item in new_edges
                        ],
                        "r41ActivePrecondition": active_precondition,
                        "oldUniqueCountU": old_unique,
                        "genuinelyNewSupportEdges": genuinely_new,
                        "oldSupportSize": len(state.support),
                        "newSupportSize": len(new_support),
                        "supportDelta": support_delta,
                        "generalSupportIdentity": (
                            support_delta == genuinely_new - old_unique
                        ),
                        "r41SupportIdentity": (
                            support_delta == 2 - old_unique
                            if active_precondition else None
                        ),
                        "r41Monotone": (
                            support_delta >= 0 if active_precondition else None
                        ),
                        "multiplicitySaturated": (
                            state.pair[middle][x] >= 2
                            and state.pair[middle][y] >= 2
                        ),
                        "fullyUnsaturated": fully_unsaturated,
                        "freedOrderedPairs": freed_ordered,
                        "allFourOrderedPairsFreed": (
                            len(freed_ordered) == 4 if fully_unsaturated else None
                        ),
                    }
                covering.append(cover)
            valid_cover = next(
                (cover for cover in covering if cover["inCompleteRowDB"]), None
            )
            probe = {
                **base,
                "kind": "twoEdgeDetour" if valid_cover else "coveredNoDetour",
                "covers": covering,
                "validDetour": valid_cover,
            }
            probes.append(probe)
            if valid_cover:
                successes.append(probe)

    all_sigma_weak = bool(probes) and all(
        probe["sigma"] < 2 for probe in probes
    )
    active_class_zero = bool(active_neighbors) and all(
        sigma_x[x] == 0 for x in active_neighbors
    )
    support_class_zero = bool(support_neighbors) and all(
        sigma_y[y] == 0 for y in support_neighbors
    )
    weak_identity_valid = all(
        probe.get("singletonIdentity", False)
        and probe["singletonSigmaX"] >= 0
        and probe["singletonSigmaY"] >= 0
        and probe["sigma"] < 2
        for probe in probes
    ) if all_sigma_weak else None
    one_class_zero = (
        weak_identity_valid and (active_class_zero or support_class_zero)
        if all_sigma_weak else None
    )
    cut_tight = sorted(
        {vertex for vertex, value in sigma_x.items() if value == 0}
        | {vertex for vertex, value in sigma_y.items() if value == 0}
    )

    if successes:
        category = successes[0]["kind"]
    elif not active_neighbors:
        category = "noActiveNeighbor"
    elif not support_neighbors:
        category = "noSupportNeighbor"
    elif not probes:
        category = "noDistinctProbe"
    else:
        kinds = {probe["kind"] for probe in probes}
        category = (
            "weakFreeOnly" if kinds == {"weakFree"}
            else "coveredNoDetourOnly" if kinds == {"coveredNoDetour"}
            else "mixedWeakAndCoveredNoDetour"
        )
    return {
        "owner": owner,
        "category": category,
        "activeNeighbors": active_neighbors,
        "supportNeighbors": support_neighbors,
        "singletonSigmaX": {str(k): v for k, v in sorted(sigma_x.items())},
        "singletonSigmaY": {str(k): v for k, v in sorted(sigma_y.items())},
        "singletonSigmaHistogramX": {
            str(value): count for value, count in sorted(Counter(sigma_x.values()).items())
        },
        "singletonSigmaHistogramY": {
            str(value): count for value, count in sorted(Counter(sigma_y.values()).items())
        },
        "allProbeSigmasWeak": all_sigma_weak,
        "weakSingletonIdentityValid": weak_identity_valid,
        "activeClassAllZero": active_class_zero,
        "supportClassAllZero": support_class_zero,
        "oneClassZeroReduction": one_class_zero,
        "cutTightVertices": cut_tight,
        "cutTightDetourExposed": any(
            success["kind"] == "twoEdgeDetour"
            and (
                success["activeNeighbor"] in cut_tight
                or success["supportNeighbor"] in cut_tight
            )
            for success in successes
        ),
        "probeCount": len(probes),
        "probes": probes,
        "success": successes[0] if successes else None,
    }


def explicit_lower_trade(
    ctx: p5.GraphContext,
    families: tuple[tuple[tuple[int, ...], ...], ...],
    old_choice: tuple[int, ...],
    old_defect: int,
    best_choice: tuple[int, ...],
    best_analysis: dict,
) -> dict | None:
    """Emit a checked lower tuple; prefer a one-row replacement when present."""
    for atom, family in enumerate(families):
        for replacement in range(len(family)):
            if replacement == old_choice[atom]:
                continue
            choice = list(old_choice)
            choice[atom] = replacement
            rows = rows_for_choice(families, tuple(choice))
            state = p5.reconstruct_state(ctx, rows)
            analysis = matching_analysis(ctx, state)
            if analysis["defect"] < old_defect:
                return {
                    "kind": "oneRow",
                    "changedAtoms": [atom],
                    "newChoice": choice,
                    "newRows": [list(row) for row in rows],
                    "oldDefect": old_defect,
                    "newMatching": analysis,
                }
    if best_analysis["defect"] < old_defect:
        changed = [
            index for index, (old, new) in enumerate(zip(old_choice, best_choice))
            if old != new
        ]
        rows = rows_for_choice(families, best_choice)
        return {
            "kind": "multiRow",
            "changedAtoms": changed,
            "newChoice": list(best_choice),
            "newRows": [list(row) for row in rows],
            "oldDefect": old_defect,
            "newMatching": best_analysis,
        }
    return None


def witness_record(
    *,
    order: int,
    ordinal: int,
    g6: str,
    info: dict,
    families: tuple[tuple[tuple[int, ...], ...], ...],
    choice: tuple[int, ...],
    tuple_index: int,
    state: p5.TupleState,
    matching: dict,
    owner_result: dict,
    trade: dict | None,
) -> dict:
    record = {
        "order": order,
        "graphOrdinal": ordinal,
        "g6": g6,
        "blue": [list(item) for item in sorted(info["Bset"])],
        "bad": [list(item) for item in sorted(info["Mset"])],
        "badEdgeOrder": [list(item) for item in info["M"]],
        "familySizes": [len(family) for family in families],
        "completeRowDB": [
            [list(row) for row in family] for family in families
        ],
        "tupleIndex": tuple_index,
        "choice": list(choice),
        "selectedRows": [list(row) for row in state.rows],
        "matching": matching,
        "activeOwners": sorted(state.active_vertices),
        "failedOwner": owner_result,
        "defectLoweringRowTrade": trade,
    }
    record["recordSha256"] = canonical_sha(record)
    return record


def analyze_graph(task: tuple[int, int, str]) -> dict:
    order, ordinal, g6 = task
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    if info is None:
        return {"status": "skipNoCut", "order": order}
    if any(length != 5 for length in info["ell"].values()):
        return {"status": "skipNotAll5", "order": order}
    families = shortest_row_families(info)
    family_sets = tuple(frozenset(family) for family in families)
    sizes = tuple(len(family) for family in families)
    ctx = p5.make_graph_context(n, info["Bset"], info["Mset"])

    minimum: int | None = None
    positive_minimizers: list[tuple[int, tuple[int, ...]]] = []
    minimizer_count = 0
    categories = Counter()
    singleton_x_hist = Counter()
    singleton_y_hist = Counter()
    weak_reduction = Counter()
    support_audit = Counter()
    active_owner_checks = 0
    first_failure = None

    def check_minimizer(
        tuple_index: int,
        choice: tuple[int, ...],
        state: p5.TupleState,
        matching: dict,
    ) -> None:
        nonlocal active_owner_checks, first_failure
        active_adj = active_adjacency(state)
        support_adj = support_adjacency(state)
        for owner in sorted(state.active_vertices):
            active_owner_checks += 1
            result = classify_owner(
                ctx, state, families, family_sets, choice, owner,
                active_adj, support_adj,
            )
            categories[result["category"]] += 1
            singleton_x_hist.update(
                {int(value): count for value, count in result["singletonSigmaHistogramX"].items()}
            )
            singleton_y_hist.update(
                {int(value): count for value, count in result["singletonSigmaHistogramY"].items()}
            )
            if result["allProbeSigmasWeak"]:
                weak_reduction["allProbeSigmasWeak"] += 1
                weak_reduction["identityValid"] += int(
                    result["weakSingletonIdentityValid"] is True
                )
                weak_reduction["oneClassZero"] += int(
                    result["oneClassZeroReduction"] is True
                )
                weak_reduction["cutTightDetour"] += int(
                    result["cutTightDetourExposed"]
                )
            for probe in result["probes"]:
                for cover in probe.get("covers", []):
                    audit = cover.get("supportMonotonicity")
                    if audit is None:
                        continue
                    support_audit["genuineDetours"] += 1
                    support_audit[
                        f"supportDelta={audit['supportDelta']}"
                    ] += 1
                    support_audit[
                        "genuinelyNewEdges=%d" % audit["genuinelyNewSupportEdges"]
                    ] += 1
                    support_audit["generalIdentityPass"] += int(
                        audit["generalSupportIdentity"]
                    )
                    support_audit["r41ActivePrecondition"] += int(
                        audit["r41ActivePrecondition"]
                    )
                    support_audit["r41IdentityPass"] += int(
                        audit["r41SupportIdentity"] is True
                    )
                    support_audit["r41MonotonePass"] += int(
                        audit["r41Monotone"] is True
                    )
                    support_audit["multiplicitySaturated"] += int(
                        audit["multiplicitySaturated"]
                    )
                    support_audit["fullyUnsaturated"] += int(
                        audit["fullyUnsaturated"]
                    )
                    support_audit["allFourOrderedPairsFreed"] += int(
                        audit["allFourOrderedPairsFreed"] is True
                    )
            if result["success"] is not None:
                continue
            trade = explicit_lower_trade(
                ctx, families, choice, matching["defect"],
                choice, matching,
            )
            if result["allProbeSigmasWeak"]:
                weak_reduction["defectLoweringTrade"] += int(trade is not None)
            if trade is not None:
                categories["defectLoweringRowTrade"] += 1
                return
            if first_failure is None:
                first_failure = witness_record(
                    order=order,
                    ordinal=ordinal,
                    g6=g6,
                    info=info,
                    families=families,
                    choice=choice,
                    tuple_index=tuple_index,
                    state=state,
                    matching=matching,
                    owner_result=result,
                    trade=trade,
                )

    tuple_count = math.prod(sizes)
    for tuple_index, choice in enumerate(
        itertools.product(*(range(size) for size in sizes))
    ):
        rows = rows_for_choice(families, choice)
        state = p5.reconstruct_state(ctx, rows)
        matching = matching_analysis(ctx, state)
        defect = matching["defect"]
        if defect == 0:
            if minimum != 0:
                minimum = 0
                positive_minimizers.clear()
                minimizer_count = 0
            minimizer_count += 1
            check_minimizer(tuple_index, choice, state, matching)
        elif minimum != 0 and (minimum is None or defect < minimum):
            minimum = defect
            positive_minimizers = [(tuple_index, choice)]
        elif defect == minimum:
            positive_minimizers.append((tuple_index, choice))
    if minimum is None:
        raise AssertionError("eligible graph has no row tuple")
    if minimum > 0:
        minimizer_count = len(positive_minimizers)
        for tuple_index, choice in positive_minimizers:
            rows = rows_for_choice(families, choice)
            state = p5.reconstruct_state(ctx, rows)
            matching = matching_analysis(ctx, state)
            if matching["defect"] != minimum:
                raise AssertionError("positive minimizer replay changed defect")
            check_minimizer(tuple_index, choice, state, matching)
    best_index = 0 if minimum == 0 else positive_minimizers[0][0]
    return {
        "status": "failure" if first_failure else "pass",
        "order": order,
        "tupleCount": tuple_count,
        "minimumDefect": minimum,
        "minimizerCount": minimizer_count,
        "activeOwnerChecks": active_owner_checks,
        "categories": dict(categories),
        "singletonXHistogram": dict(singleton_x_hist),
        "singletonYHistogram": dict(singleton_y_hist),
        "weakReduction": dict(weak_reduction),
        "supportAudit": dict(support_audit),
        "witness": first_failure,
        "bestTupleIndex": best_index,
    }


def analyze_chunk(chunk: list[tuple[int, int, str]]) -> dict:
    counts = Counter()
    categories = Counter()
    minima = Counter()
    singleton_x = Counter()
    singleton_y = Counter()
    weak_reduction = Counter()
    support_audit = Counter()
    first_witness = None
    for task in chunk:
        result = analyze_graph(task)
        status = result["status"]
        counts[status] += 1
        if status in {"pass", "failure"}:
            counts["eligibleGraphs"] += 1
            counts["rowTuples"] += result["tupleCount"]
            counts["defectMinimizers"] += result["minimizerCount"]
            counts["activeOwnerChecks"] += result["activeOwnerChecks"]
            minima[result["minimumDefect"]] += 1
            categories.update(result["categories"])
            singleton_x.update(result["singletonXHistogram"])
            singleton_y.update(result["singletonYHistogram"])
            weak_reduction.update(result["weakReduction"])
            support_audit.update(result["supportAudit"])
        if first_witness is None and result.get("witness") is not None:
            first_witness = result["witness"]
    return {
        "counts": counts,
        "categories": categories,
        "minima": minima,
        "singletonX": singleton_x,
        "singletonY": singleton_y,
        "weakReduction": weak_reduction,
        "supportAudit": support_audit,
        "witness": first_witness,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=5)
    parser.add_argument("--n-max", type=int, default=12)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--chunk-size", type=int, default=16)
    parser.add_argument("--progress-every", type=int, default=500)
    parser.add_argument("--limit-graphs", type=int)
    parser.add_argument("--graph6", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 5 <= args.n_min <= args.n_max <= 12:
        parser.error("orders must satisfy 5 <= n-min <= n-max <= 12")
    if not 1 <= args.workers <= 8:
        parser.error("workers must be in 1..8")
    if args.chunk_size <= 0:
        parser.error("chunk-size must be positive")
    if args.limit_graphs is not None and args.limit_graphs <= 0:
        parser.error("limit-graphs must be positive")
    return args


def main() -> int:
    args = parse_args()
    started = time.time()
    if args.graph6:
        rows = args.graph6
        generated = Counter(dec(g6)[0] for g6 in rows)
    else:
        rows, generated = graph6_for_orders(args.n_min, args.n_max)
    by_order: dict[int, list[str]] = {
        order: [] for order in range(args.n_min, args.n_max + 1)
    }
    for g6 in rows:
        by_order.setdefault(dec(g6)[0], []).append(g6)

    tasks = []
    stream_sha = {}
    generated_used = {}
    for order in sorted(by_order):
        graphs = by_order[order]
        if args.limit_graphs is not None:
            graphs = graphs[:args.limit_graphs]
        generated_used[str(order)] = len(graphs)
        stream_sha[str(order)] = hashlib.sha256(
            "".join(g6 + "\n" for g6 in graphs).encode("ascii")
        ).hexdigest()
        tasks.extend((order, ordinal, g6) for ordinal, g6 in enumerate(graphs))
    chunks = [
        tasks[index:index + args.chunk_size]
        for index in range(0, len(tasks), args.chunk_size)
    ]

    counts = Counter()
    categories = Counter()
    minima = Counter()
    singleton_x = Counter()
    singleton_y = Counter()
    weak_reduction = Counter()
    support_audit = Counter()
    first_witness = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for chunk_index, result in enumerate(
            pool.map(analyze_chunk, chunks, chunksize=1), start=1
        ):
            counts.update(result["counts"])
            categories.update(result["categories"])
            minima.update(result["minima"])
            singleton_x.update(result["singletonX"])
            singleton_y.update(result["singletonY"])
            weak_reduction.update(result["weakReduction"])
            support_audit.update(result["supportAudit"])
            if first_witness is None and result["witness"] is not None:
                first_witness = result["witness"]
            if args.progress_every and chunk_index % args.progress_every == 0:
                print(
                    "chunks=%d/%d eligible=%d tuples=%d minimizers=%d failures=%d elapsed=%ds"
                    % (
                        chunk_index,
                        len(chunks),
                        counts["eligibleGraphs"],
                        counts["rowTuples"],
                        counts["defectMinimizers"],
                        counts["failure"],
                        int(time.time() - started),
                    ),
                    flush=True,
                )

    payload = {
        "schema": SCHEMA,
        "statement": (
            "At every global matching-defect-minimal complete-row tuple, "
            "each ActiveOwner has a valid sigma>=2 common-blue probe, a "
            "genuine two-edge detour, or an explicit defect-lowering row trade."
        ),
        "integerOnly": True,
        "workers": args.workers,
        "orders": [args.n_min, args.n_max],
        "generatedByOrder": generated_used,
        "graphStreamSha256": stream_sha,
        "counts": dict(sorted(counts.items())),
        "minimumDefectHistogram": {
            str(value): count for value, count in sorted(minima.items())
        },
        "ownerClassification": dict(sorted(categories.items())),
        "singletonSigmaHistogramByRole": {
            "activeNeighborX": {
                str(value): count for value, count in sorted(singleton_x.items())
            },
            "supportNeighborY": {
                str(value): count for value, count in sorted(singleton_y.items())
            },
        },
        "allWeakReduction": dict(sorted(weak_reduction.items())),
        "r41SupportMonotonicityAudit": dict(sorted(support_audit.items())),
        "smallestExactWitness": first_witness,
        "verdict": "FAIL" if first_witness else "PASS",
        "elapsedSeconds": int(time.time() - started),
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii"
    )
    print(json.dumps({
        "verdict": payload["verdict"],
        "counts": payload["counts"],
        "ownerClassification": payload["ownerClassification"],
        "sha256": payload["canonicalPayloadSha256"],
    }, sort_keys=True))
    return 2 if first_witness else 0


if __name__ == "__main__":
    raise SystemExit(main())
