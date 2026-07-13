#!/usr/bin/env python3
"""Exact grouped-cap row-exchange gate for the R53 global soft flow.

The flow domain is every global CollisionHalf.  Sinks are literal off-diagonal
FreeHalf triples.  Each key has capacity one, and the four keys over an active
undirected edge share capacity two.  All arithmetic and max flow are integral.

For a row tuple w, write C(w) for global collisionUnits and D(w) for the exact
grouped-flow defect.  The gate tests collision minimizers and Hamming-one/two
exchanges.  For the old minimum-cut owner shore U it also verifies the exact
identity

  gap_w(U) - gap_e(U) = deletedDemand(U) + gainedCapacity(U).

This is the correction missed by capacity-gain-only exchange statements.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations, product
import json
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
WRITEUP = ROOT / "problems" / "23" / "writeup"
SOFTCAP = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate"
for path in (WRITEUP, SOFTCAP):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
import global_softcap as soft  # noqa: E402


N12_G6 = "K??E@cyjFgWk"
FAMILY_ORDER = (
    "P1_sameFirst",
    "P2_commonBad",
    "P3_rowCompanion",
    "P4_outsideAttachment",
    "P5_quiescentAttachment",
    "commonBlue",
)
EVALUATION_ORDER = (
    "P1_sameFirst",
    "P2_commonBad",
    "P3_rowCompanion",
    "commonBlue",
    "P4_outsideAttachment",
    "P5_quiescentAttachment",
)


def rows_for_choice(families, choice):
    return tuple(families[index][row] for index, row in enumerate(choice))


def one_neighbors(choice, family_sizes):
    for index, size in enumerate(family_sizes):
        for replacement in range(size):
            if replacement != choice[index]:
                yield choice[:index] + (replacement,) + choice[index + 1 :]


def two_neighbors(choice, family_sizes):
    for left, right in combinations(range(len(choice)), 2):
        for left_replacement in range(family_sizes[left]):
            if left_replacement == choice[left]:
                continue
            for right_replacement in range(family_sizes[right]):
                if right_replacement == choice[right]:
                    continue
                neighbor = list(choice)
                neighbor[left] = left_replacement
                neighbor[right] = right_replacement
                yield tuple(neighbor)


def add_mask(relation, base, owner_bit):
    relation[base] = relation.get(base, 0) | owner_bit


def components(n, edges, allowed):
    adjacency = [[] for _ in range(n)]
    for x, y in edges:
        if x in allowed and y in allowed:
            adjacency[x].append(y)
            adjacency[y].append(x)
    component_of = [-1] * n
    groups = []
    masks = []
    for root in sorted(allowed):
        if component_of[root] >= 0:
            continue
        cid = len(groups)
        component_of[root] = cid
        queue = [root]
        group = []
        mask = 0
        for x in queue:
            group.append(x)
            mask |= 1 << x
            for y in adjacency[x]:
                if component_of[y] < 0:
                    component_of[y] = cid
                    queue.append(y)
        groups.append(group)
        masks.append(mask)
    return component_of, groups, masks


def attachment_relation(
    ctx,
    state,
    owners,
    *,
    allowed,
    boundary_vertices,
    require_active_component,
):
    """Pinned P4/P5 component relation, independent of upstream edits."""
    if not owners or not allowed or not boundary_vertices:
        return {}
    _comp_id, component_list, component_masks = components(ctx.n, ctx.blue, allowed)
    boundaries = []
    for component in component_list:
        boundary = set()
        for x in component:
            boundary.update(y for y in ctx.blue_adj[x] if y in boundary_vertices)
        boundaries.append(boundary)

    eligible_masks = []
    for boundary in boundaries:
        mask = 0
        for index, owner in enumerate(owners):
            owner_component = state.selected_comp[owner]
            if any(
                state.pair[owner][attach] > 0
                and (
                    not require_active_component
                    or state.selected_comp[attach] == owner_component
                )
                for attach in boundary
            ):
                mask |= 1 << index
        eligible_masks.append(mask)

    relation = {}
    for left_id, left_vertices in enumerate(component_list):
        left_mask = eligible_masks[left_id]
        if not left_mask:
            continue
        for right_id, right_vertices in enumerate(component_list):
            owner_mask = left_mask & eligible_masks[right_id]
            if not owner_mask:
                continue
            if ctx.sigma(component_masks[left_id] | component_masks[right_id]) < 0:
                continue
            for x in left_vertices:
                for y in right_vertices:
                    if x != y and state.pair[x][y] == 0:
                        add_mask(relation, ctx.n * x + y, owner_mask)
    return relation


def family_relation(ctx, state, owners, family, p4_scope):
    relation = {}
    if family == "P1_sameFirst":
        for index, owner in enumerate(owners):
            bit = 1 << index
            for y in range(ctx.n):
                if y != owner and state.pair[owner][y] == 0:
                    add_mask(relation, ctx.n * owner + y, bit)
        return relation
    if family == "P2_commonBad":
        for index, owner in enumerate(owners):
            bit = 1 << index
            for x in sorted(ctx.bad_adj[owner]):
                for y in sorted(ctx.bad_adj[owner]):
                    if (
                        x != y
                        and state.pair[x][y] == 0
                        and ctx.sigma_pair[x][y] >= 0
                    ):
                        add_mask(relation, ctx.n * x + y, bit)
        return relation
    if family == "P3_rowCompanion":
        for index, owner in enumerate(owners):
            bit = 1 << index
            companions = [
                x for x in range(ctx.n) if state.pair[owner][x] > 0
            ]
            for x in companions:
                for y in companions:
                    if (
                        x != y
                        and state.pair[x][y] == 0
                        and ctx.sigma_pair[x][y] >= 0
                    ):
                        add_mask(relation, ctx.n * x + y, bit)
        return relation
    if family == "commonBlue":
        for index, owner in enumerate(owners):
            bit = 1 << index
            for x in sorted(ctx.blue_adj[owner]):
                for y in sorted(ctx.blue_adj[owner]):
                    if (
                        x != y
                        and state.pair[x][y] == 0
                        and ctx.sigma_pair[x][y] >= 2
                    ):
                        add_mask(relation, ctx.n * x + y, bit)
        return relation
    if family == "P4_outsideAttachment":
        return attachment_relation(
            ctx,
            state,
            owners,
            allowed=set(range(ctx.n)) - state.selected,
            boundary_vertices=set(state.selected),
            require_active_component=p4_scope == "strict",
        )
    if family == "P5_quiescentAttachment":
        return attachment_relation(
            ctx,
            state,
            owners,
            allowed=set(range(ctx.n)) - state.active_vertices,
            boundary_vertices=set(state.active_vertices),
            require_active_component=True,
        )
    raise ValueError(family)


def build_metric(ctx, rows, *, force_full=False, p4_scope="unscoped"):
    """Evaluate one tuple, stopping after defect zero unless full relation is needed."""
    state = soft.reconstruct_state(ctx, rows)
    owners, demand = soft.global_demands(state)
    nonfree_active = [
        (x, y)
        for x, y in state.active_edges
        if state.pair[x][y] != 0 or state.pair[y][x] != 0
    ]
    if nonfree_active:
        raise AssertionError(("active edge is not a four-FreeHalf block", nonfree_active))

    incidence = sum(sum(row) for row in state.pair)
    if incidence != 25 * len(state.rows):
        raise AssertionError((incidence, len(state.rows)))

    relation = {}
    flow = None
    evaluated = []
    for family in EVALUATION_ORDER:
        addition = family_relation(ctx, state, owners, family, p4_scope)
        for base, mask in addition.items():
            relation[base] = relation.get(base, 0) | mask
        evaluated.append(family)
        flow, _assigned = soft.solve_grouped_flow(
            ctx.n, owners, demand, relation, state.active_edges
        )
        if flow["defect"] == 0 and not force_full:
            break
    if flow is None:
        flow, _assigned = soft.solve_grouped_flow(
            ctx.n, owners, demand, relation, state.active_edges
        )

    collision = sum(demand) // 2
    if 2 * collision != sum(demand):
        raise AssertionError("CollisionHalf demand is not even")
    return {
        "state": state,
        "owners": owners,
        "demand": demand,
        "relation": relation,
        "collision": collision,
        "defect": flow["defect"],
        "flow": flow["maximumFlow"],
        "shore": tuple(flow["minCutSourceOwners"]),
        "evaluated": tuple(evaluated),
        "full": len(evaluated) == len(EVALUATION_ORDER),
    }


def shore_profile(ctx, metric, shore):
    """Exact demand and grouped capacity of one vertex-owner shore."""
    shore = set(shore)
    owner_mask = 0
    shore_demand = 0
    for index, (owner, amount) in enumerate(zip(metric["owners"], metric["demand"])):
        if owner in shore:
            owner_mask |= 1 << index
            shore_demand += amount

    if owner_mask == 0:
        return {"demand": 0, "capacity": 0, "gap": 0}

    state = metric["state"]
    active_base = {}
    for x, y in state.active_edges:
        active_base[ctx.n * x + y] = (x, y)
        active_base[ctx.n * y + x] = (x, y)

    direct = sum(
        2
        for base, mask in metric["relation"].items()
        if base not in active_base and mask & owner_mask
    )
    grouped = 0
    for x, y in state.active_edges:
        eligible = 2 * bool(
            metric["relation"].get(ctx.n * x + y, 0) & owner_mask
        )
        eligible += 2 * bool(
            metric["relation"].get(ctx.n * y + x, 0) & owner_mask
        )
        grouped += min(2, eligible)
    capacity = direct + grouped
    return {
        "demand": shore_demand,
        "capacity": capacity,
        "gap": shore_demand - capacity,
        "directCapacity": direct,
        "groupedCapacity": grouped,
    }


def exchange_decomposition(ctx, old_metric, new_metric):
    """Decompose improvement on the old exact minimum-cut shore."""
    shore = old_metric["shore"]
    old_profile = shore_profile(ctx, old_metric, shore)
    new_profile = shore_profile(ctx, new_metric, shore)
    if old_profile["gap"] != old_metric["defect"]:
        raise AssertionError((old_profile, old_metric["defect"], shore))
    deleted = old_profile["demand"] - new_profile["demand"]
    gained = new_profile["capacity"] - old_profile["capacity"]
    improvement = old_profile["gap"] - new_profile["gap"]
    if improvement != deleted + gained:
        raise AssertionError((improvement, deleted, gained))
    return {
        "shore": list(shore),
        "oldDemand": old_profile["demand"],
        "newDemand": new_profile["demand"],
        "oldCapacity": old_profile["capacity"],
        "newCapacity": new_profile["capacity"],
        "deletedDemand": deleted,
        "gainedCapacity": gained,
        "shoreImprovement": improvement,
        "oldGap": old_profile["gap"],
        "newGap": new_profile["gap"],
    }


def compact_metric(choice, metric):
    return {
        "choice": list(choice),
        "collisionUnits": metric["collision"],
        "flowDefect": metric["defect"],
        "maximumFlow": metric["flow"],
        "minimumCutOwners": list(metric["shore"]),
        "evaluatedRelations": list(metric["evaluated"]),
    }


def analyze_graph(task):
    order, ordinal, g6, detailed, p4_scope = task
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    if info is None:
        return {"status": "skipNoCut", "order": order}
    if any(length != 5 for length in info["ell"].values()):
        return {"status": "skipNotAll5", "order": order}

    families = shortest_row_families(info)
    family_sizes = tuple(len(family) for family in families)
    choices = tuple(product(*(range(size) for size in family_sizes)))
    ctx = soft.make_graph_context(n, info["Bset"], info["Mset"])
    metrics = {}
    rows_cache = {}
    for choice in choices:
        rows = rows_for_choice(families, choice)
        rows_cache[choice] = rows
        metrics[choice] = build_metric(ctx, rows, p4_scope=p4_scope)

    minimum_collision = min(metric["collision"] for metric in metrics.values())
    minimum_choices = [
        choice for choice, metric in metrics.items()
        if metric["collision"] == minimum_collision
    ]
    minimum_failures = [
        choice for choice in minimum_choices if metrics[choice]["defect"] > 0
    ]
    minimum_passes = [
        choice for choice in minimum_choices if metrics[choice]["defect"] == 0
    ]
    failures = [choice for choice in choices if metrics[choice]["defect"] > 0]

    full_cache = {}

    def full_metric(choice):
        cached = full_cache.get(choice)
        if cached is None:
            metric = metrics[choice]
            cached = metric if metric["full"] else build_metric(
                ctx, rows_cache[choice], force_full=True, p4_scope=p4_scope
            )
            full_cache[choice] = cached
        return cached

    counters = Counter()
    first = {}
    first_exchange = None
    first_two_row_required = None
    first_minimum_exchange = None

    def save_first(label, old_choice, old_metric, candidates=()):
        if label in first:
            return
        ordered = sorted(
            candidates,
            key=lambda choice: (
                metrics[choice]["collision"], metrics[choice]["defect"], choice
            ),
        )
        first[label] = {
            "order": order,
            "ordinal": ordinal,
            "g6": g6,
            "familySizes": list(family_sizes),
            "old": compact_metric(old_choice, old_metric),
            "bestCandidate": compact_metric(ordered[0], metrics[ordered[0]])
            if ordered else None,
        }

    for old_choice in failures:
        old = metrics[old_choice]
        one = tuple(one_neighbors(old_choice, family_sizes))
        two_exact = tuple(two_neighbors(old_choice, family_sizes))
        up_to_two = one + two_exact

        one_lex = [
            choice for choice in one
            if (metrics[choice]["collision"], metrics[choice]["defect"])
            < (old["collision"], old["defect"])
        ]
        two_lex = [
            choice for choice in up_to_two
            if (metrics[choice]["collision"], metrics[choice]["defect"])
            < (old["collision"], old["defect"])
        ]
        one_flow = [
            choice for choice in one
            if metrics[choice]["collision"] <= old["collision"]
            and metrics[choice]["defect"] < old["defect"]
        ]
        two_flow = [
            choice for choice in up_to_two
            if metrics[choice]["collision"] <= old["collision"]
            and metrics[choice]["defect"] < old["defect"]
        ]

        for label, candidates in (
            ("oneLex", one_lex),
            ("twoLex", two_lex),
            ("oneFlow", one_flow),
            ("twoFlow", two_flow),
        ):
            counters[label] += bool(candidates)
            if not candidates:
                save_first("no" + label[0].upper() + label[1:], old_choice, old, one if label.startswith("one") else up_to_two)

        corrected_by_radius = {}
        monotone_by_radius = {}
        capacity_only_by_radius = {}
        for radius, candidates in ((1, one_flow), (2, two_flow)):
            corrected = []
            monotone = []
            capacity_only = []
            for choice in candidates:
                decomposition = exchange_decomposition(
                    ctx, full_metric(old_choice), full_metric(choice)
                )
                if decomposition["shoreImprovement"] > 0:
                    corrected.append((choice, decomposition))
                    if (
                        decomposition["deletedDemand"] >= 0
                        and decomposition["gainedCapacity"] >= 0
                    ):
                        monotone.append((choice, decomposition))
                    if (
                        decomposition["deletedDemand"] == 0
                        and decomposition["gainedCapacity"] > 0
                    ):
                        capacity_only.append((choice, decomposition))
            corrected_by_radius[radius] = corrected
            monotone_by_radius[radius] = monotone
            capacity_only_by_radius[radius] = capacity_only
            counters[f"correctedR{radius}"] += bool(corrected)
            counters[f"monotoneR{radius}"] += bool(monotone)
            counters[f"capacityOnlyR{radius}"] += bool(capacity_only)
            if not corrected:
                save_first(f"noCorrectedR{radius}", old_choice, old, candidates)
            if not monotone:
                save_first(f"noMonotoneR{radius}", old_choice, old, candidates)
            if not capacity_only:
                save_first(f"noCapacityOnlyR{radius}", old_choice, old, candidates)

        if first_exchange is None and corrected_by_radius[2]:
            choice, decomposition = min(
                corrected_by_radius[2],
                key=lambda item: (
                    metrics[item[0]]["collision"],
                    metrics[item[0]]["defect"],
                    item[0],
                ),
            )
            first_exchange = {
                "order": order,
                "ordinal": ordinal,
                "g6": g6,
                "familySizes": list(family_sizes),
                "old": compact_metric(old_choice, old),
                "new": compact_metric(choice, metrics[choice]),
                "hamming": sum(a != b for a, b in zip(old_choice, choice)),
                "decomposition": decomposition,
            }
        if (
            first_two_row_required is None
            and not one_flow
            and corrected_by_radius[2]
        ):
            choice, decomposition = min(
                corrected_by_radius[2],
                key=lambda item: (
                    metrics[item[0]]["collision"],
                    metrics[item[0]]["defect"],
                    item[0],
                ),
            )
            first_two_row_required = {
                "order": order,
                "ordinal": ordinal,
                "g6": g6,
                "familySizes": list(family_sizes),
                "old": compact_metric(old_choice, old),
                "new": compact_metric(choice, metrics[choice]),
                "hamming": sum(a != b for a, b in zip(old_choice, choice)),
                "decomposition": decomposition,
            }
        if (
            first_minimum_exchange is None
            and old["collision"] == minimum_collision
            and corrected_by_radius[2]
        ):
            choice, decomposition = min(
                corrected_by_radius[2],
                key=lambda item: (
                    metrics[item[0]]["collision"],
                    metrics[item[0]]["defect"],
                    item[0],
                ),
            )
            first_minimum_exchange = {
                "order": order,
                "ordinal": ordinal,
                "g6": g6,
                "familySizes": list(family_sizes),
                "old": compact_metric(old_choice, old),
                "new": compact_metric(choice, metrics[choice]),
                "hamming": sum(a != b for a, b in zip(old_choice, choice)),
                "decomposition": decomposition,
            }

    if minimum_failures:
        first_failing_minimum = {
            "order": order,
            "ordinal": ordinal,
            "g6": g6,
            "familySizes": list(family_sizes),
            "minimumCollisionUnits": minimum_collision,
            "failure": compact_metric(
                minimum_failures[0], metrics[minimum_failures[0]]
            ),
        }
    else:
        first_failing_minimum = None

    if not minimum_passes:
        first_no_feasible_minimum = {
            "order": order,
            "ordinal": ordinal,
            "g6": g6,
            "familySizes": list(family_sizes),
            "minimumCollisionUnits": minimum_collision,
            "minimumChoices": len(minimum_choices),
            "firstFailure": compact_metric(
                minimum_failures[0], metrics[minimum_failures[0]]
            ),
        }
    else:
        first_no_feasible_minimum = None

    result = {
        "status": "tested",
        "order": order,
        "tupleCount": len(choices),
        "flowFailures": len(failures),
        "minimumCollisionUnits": minimum_collision,
        "minimumChoiceCount": len(minimum_choices),
        "minimumFailureCount": len(minimum_failures),
        "minimumPassCount": len(minimum_passes),
        "counts": dict(counters),
        "firstFailingMinimum": first_failing_minimum,
        "firstNoFeasibleMinimum": first_no_feasible_minimum,
        "first": first,
        "firstExchange": first_exchange,
        "firstTwoRowRequired": first_two_row_required,
        "firstMinimumExchange": first_minimum_exchange,
    }
    if detailed:
        result["minimumChoices"] = [
            compact_metric(choice, metrics[choice]) for choice in minimum_choices
        ]
    return result


def positive_int(value):
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=positive_int, default=5)
    parser.add_argument("--n-max", type=positive_int, default=10)
    parser.add_argument("--workers", type=positive_int, default=min(32, os.cpu_count() or 1))
    parser.add_argument("--graph6", action="append", default=[])
    parser.add_argument("--n12", action="store_true", help="run the canonical N12 fixture")
    parser.add_argument("--detailed", action="store_true")
    parser.add_argument(
        "--p4-scope", choices=("unscoped", "strict"), default="unscoped"
    )
    args = parser.parse_args()
    if args.n_min > args.n_max:
        parser.error("--n-min must not exceed --n-max")
    if args.workers > 64:
        parser.error("--workers must not exceed 64")
    return args


def main():
    args = parse_args()
    graph6 = list(args.graph6)
    if args.n12:
        graph6.append(N12_G6)
    if graph6:
        generated = Counter(dec(g6)[0] for g6 in graph6)
    else:
        graph6, generated = graph6_for_orders(args.n_min, args.n_max)

    ordinals = Counter()
    tasks = []
    for g6 in graph6:
        order, _edges = dec(g6)
        tasks.append((order, ordinals[order], g6, args.detailed, args.p4_scope))
        ordinals[order] += 1

    status = Counter()
    by_order = {}
    first = {}
    first_failing_minimum = None
    first_no_feasible_minimum = None
    first_exchange = None
    first_two_row_required = None
    first_minimum_exchange = None

    def consume(result):
        nonlocal first_failing_minimum, first_no_feasible_minimum
        nonlocal first_exchange, first_two_row_required, first_minimum_exchange
        status[result["status"]] += 1
        counts = by_order.setdefault(result["order"], Counter())
        counts[result["status"]] += 1
        if result["status"] != "tested":
            return
        counts["tuples"] += result["tupleCount"]
        counts["flowFailures"] += result["flowFailures"]
        counts["minimumChoices"] += result["minimumChoiceCount"]
        counts["minimumFailingChoices"] += result["minimumFailureCount"]
        counts["minimumPassingChoices"] += result["minimumPassCount"]
        counts["graphsWithFailingMinimum"] += int(result["minimumFailureCount"] > 0)
        counts["graphsWithNoFeasibleMinimum"] += int(result["minimumPassCount"] == 0)
        for key, value in result["counts"].items():
            counts[key] += value
        if first_failing_minimum is None and result["firstFailingMinimum"]:
            first_failing_minimum = result["firstFailingMinimum"]
        if first_no_feasible_minimum is None and result["firstNoFeasibleMinimum"]:
            first_no_feasible_minimum = result["firstNoFeasibleMinimum"]
        if first_exchange is None and result["firstExchange"]:
            first_exchange = result["firstExchange"]
        if first_two_row_required is None and result["firstTwoRowRequired"]:
            first_two_row_required = result["firstTwoRowRequired"]
        if first_minimum_exchange is None and result["firstMinimumExchange"]:
            first_minimum_exchange = result["firstMinimumExchange"]
        for label, witness in result["first"].items():
            first.setdefault(label, witness)
        if args.detailed:
            first.setdefault("detailedGraph", {
                "order": result["order"],
                "minimumCollisionUnits": result["minimumCollisionUnits"],
                "minimumChoices": result["minimumChoices"],
            })

    if args.workers == 1:
        for task in tasks:
            consume(analyze_graph(task))
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            for result in executor.map(analyze_graph, tasks, chunksize=8):
                consume(result)

    payload = {
        "schema": "CDC_WAVE1_GROUPED_CAP_EXCHANGE_V1",
        "arithmetic": "Python integers only; exact integral Dinic max flow",
        "coverage": {
            "requestedOrders": [args.n_min, args.n_max],
            "fixtureMode": bool(args.graph6 or args.n12),
            "generatedByOrder": {str(k): v for k, v in sorted(generated.items())},
            "status": dict(status),
        },
        "model": {
            "demand": "all global CollisionHalf identities",
            "sink": "actual off-diagonal FreeHalf triples",
            "keyCapacity": 1,
            "activeEdgeGroupedCapacity": 2,
            "relations": list(FAMILY_ORDER),
            "p4Scope": args.p4_scope,
            "rowPotential": ["global collisionUnits", "grouped flow defect"],
        },
        "byOrder": {
            str(order): dict(sorted(counts.items()))
            for order, counts in sorted(by_order.items())
        },
        "firstFailingCollisionMinimum": first_failing_minimum,
        "firstGraphWithNoFeasibleCollisionMinimum": first_no_feasible_minimum,
        "firstExchange": first_exchange,
        "firstTwoRowRequired": first_two_row_required,
        "firstMinimumExchange": first_minimum_exchange,
        "firstClaimFailures": first,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 1 if first_no_feasible_minimum is not None else 0


if __name__ == "__main__":
    raise SystemExit(main())
