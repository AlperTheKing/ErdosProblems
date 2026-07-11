"""Exact all-tuple census for the corrected R23 four-pattern relation.

For each connected triangle-free graph in the requested order range, select
the existing Gamma-minimum connected maximum cut, require every bad edge to
have ell=5, enumerate every coherent shortest-row tuple, and run the corrected
full owner flow:

* collision halves plus HitNeed obligations;
* active half-zero reservations;
* same-owner, row-companion, and outside-component attachment sources.

This is deliberately stronger evidence than a global-minimum-only gate: every
coherent tuple is tested.  All graph, row, demand, capacity, and flow arithmetic
is integral exact.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from itertools import product

from _codex_r19_global_base_census import dec, graph6_for_orders, loads
from _codex_r20_two_row_exchange_gate import (
    minimum_neighbor_scores,
    obligation_score,
    shortest_row_families,
)
from _codex_r23_outside_attachment_full_obligation_gate import (
    active_scoped_obligation_score,
    full_owner_flow,
)


def edge_distance(edges, source, target):
    adjacency = {}
    for x, y in edges:
        adjacency.setdefault(x, set()).add(y)
        adjacency.setdefault(y, set()).add(x)
    queue = deque([(source, 0)])
    seen = {source}
    while queue:
        x, distance = queue.popleft()
        if x == target:
            return distance
        for y in adjacency.get(x, ()):
            if y not in seen:
                seen.add(y)
                queue.append((y, distance + 1))
    return None


def edge_radius(edges, atom, selected_edge):
    a, b = atom
    x, y = selected_edge
    oriented = []
    for left, right in ((x, y), (y, x)):
        d_left = edge_distance(edges, a, left)
        d_right = edge_distance(edges, b, right)
        if d_left is not None and d_right is not None:
            oriented.append(d_left + d_right)
    return min(oriented) if oriented else None


def evaluate_graph(
    g6: str, minima_only: bool = False, include_outside: bool = True,
    failure_limit: int = 2, max_product: int = 0, score_mode: str = "global",
    min_product: int = 0,
):
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    if info is None:
        return {"status": "skipNoCut", "order": n}
    if any(length != 5 for length in info["ell"].values()):
        return {"status": "skipNotAll5", "order": n}

    families = shortest_row_families(info)
    family_sizes = tuple(len(family) for family in families)
    total_product = 1
    for size in family_sizes:
        total_product *= size
    if min_product and total_product < min_product:
        return {
            "status": "skipLight", "order": n, "g6": g6,
            "tuples": total_product, "familySizes": family_sizes,
        }
    if max_product and total_product > max_product:
        return {
            "status": "skipHeavy", "order": n, "g6": g6,
            "tuples": total_product, "familySizes": family_sizes,
        }
    scored = []
    for choice in product(*(range(size) for size in family_sizes)):
        rows = tuple(
            families[index][row_index]
            for index, row_index in enumerate(choice)
        )
        score = (
            obligation_score(n, info, rows)
            if score_mode == "global"
            else active_scoped_obligation_score(
                n, set(info["Bset"]), set(info["Mset"]), rows
            )
        )
        scored.append((score, choice, rows))
    total = len(scored)
    minimum_score = min(score for score, _, _ in scored)
    score_by_choice = {choice: score for score, choice, _ in scored}
    minimizing_tuples = sum(score == minimum_score for score, _, _ in scored)
    selected = (
        [item for item in scored if item[0] == minimum_score]
        if minima_only else scored
    )

    failures = 0
    failing_minimizers = 0
    failing_choices = []
    first = []
    for score, choice, rows in selected:
        if score_mode == "scoped" and score == 0:
            record = {
                "full": True, "totalDemand": 0, "activeComponents": 0,
                "activeEdges": 0,
            }
            failed = False
        else:
            record = full_owner_flow(
                n,
                set(info["Bset"]),
                set(info["Mset"]),
                rows,
                g6,
                require_full=False,
                quiet=True,
                scope="active",
                include_outside=include_outside,
            )
            failed = not record["full"]
        if score == minimum_score:
            failing_minimizers += int(failed)
        if failed:
            failures += 1
            failing_choices.append((choice, score, record))
            if len(first) < failure_limit:
                first.append({
                    "g6": g6,
                    "order": n,
                    "badEdges": [list(edge) for edge in info["M"]],
                    "familySizes": list(family_sizes),
                    "rowChoice": list(choice),
                    "rows": [list(row) for row in rows],
                    "flow": record,
                })
    one_row_descent = 0
    only_two_row_descent = 0
    no_two_row_descent = 0
    one_row_reduces_active = 0
    one_row_kills_active = 0
    active_alternative_descent = 0
    internal_alternative_descent = 0
    monotone_one_row_descent = 0
    internal_killer_descent = 0
    k4_killer_descent = 0
    radius_three_absorbing_descent = 0
    no_killer_but_one_row_descent = 0
    hfar_failures = 0
    hfar_no_radius_three = 0
    hfar_radius_three_no_absorbing = 0
    hfar_no_one_row_descent = 0
    negative_one_row_delta_sum = 0
    nonnegative_one_row_delta_sum = 0
    first_nonactive_alternative = None
    first_three_outcome_failure = None
    first_nonnegative_delta_sum = None
    if not minima_only:
        for choice, score, old_record in failing_choices:
            old_rows = tuple(
                families[i][choice[i]] for i in range(len(choice))
            )
            old_vertices = {v for row in old_rows for v in row}
            old_support = {
                tuple(sorted((x, y)))
                for row in old_rows for x, y in zip(row, row[1:])
            }
            old_active = {
                edge for edge in info["Bset"]
                if edge[0] in old_vertices and edge[1] in old_vertices
                and edge not in old_support
            }
            active_atom_distances = [
                edge_distance(old_active, *bad_edge)
                for bad_edge in info["M"]
            ]
            active_atom_distances = [
                distance for distance in active_atom_distances
                if distance is not None
            ]
            hfar = bool(active_atom_distances) and min(active_atom_distances) >= 6
            hfar_failures += int(hfar)
            radius_three_pairs = [
                (index, selected_edge)
                for index, bad_edge in enumerate(info["M"])
                for selected_edge in old_support
                if edge_radius(old_active, bad_edge, selected_edge) == 3
            ]
            has_radius_three = bool(radius_three_pairs)
            hfar_no_radius_three += int(hfar and not has_radius_three)
            delta_sum = sum(
                score_by_choice[
                    choice[:index] + (replacement,) + choice[index + 1:]
                ] - score
                for index, size in enumerate(family_sizes)
                for replacement in range(size)
                if replacement != choice[index]
            )
            negative_one_row_delta_sum += int(delta_sum < 0)
            nonnegative_one_row_delta_sum += int(delta_sum >= 0)
            if delta_sum >= 0 and first_nonnegative_delta_sum is None:
                first_nonnegative_delta_sum = {
                    "g6": g6,
                    "order": n,
                    "choice": list(choice),
                    "rows": [list(row) for row in old_rows],
                    "score": score,
                    "deltaSum": delta_sum,
                    "flow": old_record,
                }
            best_one, best_two = minimum_neighbor_scores(
                choice, family_sizes, score_by_choice
            )
            if best_one is not None and best_one < score:
                one_row_descent += 1
                reduces = False
                kills = False
                active_alternative = False
                internal_alternative = False
                monotone_descent = False
                internal_killer = False
                k4_killer = False
                radius_three_absorbing = False
                first_descent = None
                for index, size in enumerate(family_sizes):
                    for replacement in range(size):
                        if replacement == choice[index]:
                            continue
                        neighbor = (
                            choice[:index] + (replacement,) + choice[index + 1:]
                        )
                        if score_by_choice[neighbor] >= score:
                            continue
                        neighbor_rows = tuple(
                            families[i][neighbor[i]] for i in range(len(neighbor))
                        )
                        neighbor_record = full_owner_flow(
                            n,
                            set(info["Bset"]),
                            set(info["Mset"]),
                            neighbor_rows,
                            g6,
                            require_full=False,
                            quiet=True,
                            scope="active",
                            include_outside=include_outside,
                        )
                        reduces = reduces or (
                            neighbor_record["activeComponents"]
                            < old_record["activeComponents"]
                        )
                        kills = kills or neighbor_record["activeComponents"] == 0
                        replacement_row = families[index][replacement]
                        replacement_edges = {
                            tuple(sorted((x, y)))
                            for x, y in zip(replacement_row, replacement_row[1:])
                        }
                        active_alternative = active_alternative or (
                            replacement_edges <= old_active
                        )
                        internal_alternative = internal_alternative or (
                            replacement_edges <= (old_active | old_support)
                            and set(replacement_row) <= old_vertices
                        )
                        is_internal = (
                            replacement_edges <= (old_active | old_support)
                            and set(replacement_row) <= old_vertices
                        )
                        active_count = len(replacement_edges & old_active)
                        is_killer = (
                            is_internal
                            and active_count >= 3
                            and neighbor_record["activeComponents"] == 0
                        )
                        internal_killer = internal_killer or is_killer
                        atom_distance = edge_distance(
                            old_active, *info["M"][index]
                        )
                        k4_killer = k4_killer or (
                            is_killer
                            and active_count == 4
                            and atom_distance == 4
                        )
                        supported_edges = replacement_edges & old_support
                        is_radius_three_absorbing = (
                            is_killer
                            and active_count == 3
                            and len(supported_edges) == 1
                            and edge_radius(
                                old_active,
                                info["M"][index],
                                next(iter(supported_edges)),
                            ) == 3
                        )
                        radius_three_absorbing = (
                            radius_three_absorbing or is_radius_three_absorbing
                        )
                        if score_mode == "global":
                            old_collision_units = (
                                score // 2 - old_record["activeEdges"]
                            )
                            new_collision_units = (
                                score_by_choice[neighbor] // 2
                                - neighbor_record["activeEdges"]
                            )
                            monotone_descent = monotone_descent or (
                                new_collision_units <= old_collision_units
                                and neighbor_record["activeEdges"]
                                < old_record["activeEdges"]
                            )
                        if first_descent is None:
                            first_descent = {
                                "changedRow": index,
                                "replacement": replacement,
                                "oldRow": list(old_rows[index]),
                                "newRow": list(replacement_row),
                                "oldScore": score,
                                "newScore": score_by_choice[neighbor],
                                "replacementEdges": [list(e) for e in sorted(replacement_edges)],
                                "oldActiveEdges": [list(e) for e in sorted(old_active)],
                                "newActiveComponents": neighbor_record["activeComponents"],
                            }
                one_row_reduces_active += int(reduces)
                one_row_kills_active += int(kills)
                active_alternative_descent += int(active_alternative)
                internal_alternative_descent += int(internal_alternative)
                monotone_one_row_descent += int(monotone_descent)
                internal_killer_descent += int(internal_killer)
                k4_killer_descent += int(k4_killer)
                radius_three_absorbing_descent += int(radius_three_absorbing)
                no_killer_but_one_row_descent += int(not internal_killer)
                hfar_radius_three_no_absorbing += int(
                    hfar and has_radius_three and not radius_three_absorbing
                )
                if not active_alternative and first_nonactive_alternative is None:
                    first_nonactive_alternative = {
                        "g6": g6,
                        "order": n,
                        "choice": list(choice),
                        "rows": [list(row) for row in old_rows],
                        "flow": old_record,
                        "descent": first_descent,
                    }
                if (
                    first_three_outcome_failure is None
                    and (
                        not internal_killer
                        or (hfar and not has_radius_three)
                        or (hfar and has_radius_three and not radius_three_absorbing)
                    )
                ):
                    first_three_outcome_failure = {
                        "g6": g6,
                        "order": n,
                        "choice": list(choice),
                        "rows": [list(row) for row in old_rows],
                        "score": score,
                        "flow": old_record,
                        "activeAtomDistances": active_atom_distances,
                        "radiusThreePairs": [
                            [index, list(edge)]
                            for index, edge in radius_three_pairs
                        ],
                        "internalKiller": internal_killer,
                        "radiusThreeAbsorbing": radius_three_absorbing,
                    }
            elif best_two is not None and best_two < score:
                only_two_row_descent += 1
                hfar_no_one_row_descent += int(hfar)
            else:
                no_two_row_descent += 1
                hfar_no_one_row_descent += int(hfar)
    return {
        "status": "eligible",
        "order": n,
        "graphs": 1,
        "tuples": total,
        "checkedTuples": len(selected),
        "failures": failures,
        "minimumScore": minimum_score,
        "minimizingTuples": minimizing_tuples,
        "failingMinimizers": failing_minimizers,
        "oneRowDescent": one_row_descent,
        "onlyTwoRowDescent": only_two_row_descent,
        "noAtMostTwoDescent": no_two_row_descent,
        "oneRowReducesActive": one_row_reduces_active,
        "oneRowKillsActive": one_row_kills_active,
        "activeAlternativeDescent": active_alternative_descent,
        "internalAlternativeDescent": internal_alternative_descent,
        "monotoneOneRowDescent": monotone_one_row_descent,
        "internalKillerDescent": internal_killer_descent,
        "k4KillerDescent": k4_killer_descent,
        "radiusThreeAbsorbingDescent": radius_three_absorbing_descent,
        "noKillerButOneRowDescent": no_killer_but_one_row_descent,
        "hfarFailures": hfar_failures,
        "hfarNoRadiusThree": hfar_no_radius_three,
        "hfarRadiusThreeNoAbsorbing": hfar_radius_three_no_absorbing,
        "hfarNoOneRowDescent": hfar_no_one_row_descent,
        "negativeOneRowDeltaSum": negative_one_row_delta_sum,
        "nonnegativeOneRowDeltaSum": nonnegative_one_row_delta_sum,
        "firstNonActiveAlternative": first_nonactive_alternative,
        "firstThreeOutcomeFailure": first_three_outcome_failure,
        "firstNonnegativeDeltaSum": first_nonnegative_delta_sum,
        "first": first,
    }


def _evaluate_task(task):
    return evaluate_graph(*task)


def positive(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-order", type=positive, default=5)
    parser.add_argument("--max-order", type=positive, default=10)
    parser.add_argument("--workers", type=positive, default=min(48, os.cpu_count() or 1))
    parser.add_argument("--failure-limit", type=int, default=4)
    parser.add_argument("--minima-only", action="store_true")
    parser.add_argument("--no-outside", action="store_true")
    parser.add_argument("--max-product", type=int, default=0)
    parser.add_argument("--min-product", type=int, default=0)
    parser.add_argument("--omit-heavy-list", action="store_true")
    parser.add_argument("--score-mode", choices=("global", "scoped"), default="global")
    args = parser.parse_args()
    if args.workers > 64:
        parser.error("--workers must not exceed 64")

    graph6, generated = graph6_for_orders(args.min_order, args.max_order)
    aggregate = Counter()
    status = Counter()
    by_order = {}
    first = []
    first_nonactive_alternative = None
    first_three_outcome_failure = None
    first_nonnegative_delta_sum = None
    heavy = []
    heavy_count = 0
    heavy_tuples = 0
    tasks = [
        (
            g6, args.minima_only, not args.no_outside, 2,
            args.max_product, args.score_mode, args.min_product,
        )
        for g6 in graph6
    ]
    if args.workers == 1:
        results = (evaluate_graph(*task) for task in tasks)
        pool = None
    else:
        pool = ProcessPoolExecutor(max_workers=args.workers)
        results = pool.map(_evaluate_task, tasks, chunksize=4)
    try:
        for result in results:
            status[result["status"]] += 1
            if result["status"] == "skipHeavy":
                heavy_count += 1
                heavy_tuples += result["tuples"]
                if not args.omit_heavy_list:
                    heavy.append({
                        "g6": result["g6"], "order": result["order"],
                        "tuples": result["tuples"],
                        "familySizes": result["familySizes"],
                    })
            if result["status"] != "eligible":
                continue
            aggregate["graphs"] += result["graphs"]
            aggregate["tuples"] += result["tuples"]
            aggregate["checkedTuples"] += result["checkedTuples"]
            aggregate["failures"] += result["failures"]
            aggregate["minimizingTuples"] += result["minimizingTuples"]
            aggregate["failingMinimizers"] += result["failingMinimizers"]
            aggregate["oneRowDescent"] += result["oneRowDescent"]
            aggregate["onlyTwoRowDescent"] += result["onlyTwoRowDescent"]
            aggregate["noAtMostTwoDescent"] += result["noAtMostTwoDescent"]
            aggregate["oneRowReducesActive"] += result["oneRowReducesActive"]
            aggregate["oneRowKillsActive"] += result["oneRowKillsActive"]
            aggregate["activeAlternativeDescent"] += result["activeAlternativeDescent"]
            aggregate["internalAlternativeDescent"] += result["internalAlternativeDescent"]
            aggregate["monotoneOneRowDescent"] += result["monotoneOneRowDescent"]
            aggregate["internalKillerDescent"] += result["internalKillerDescent"]
            aggregate["k4KillerDescent"] += result["k4KillerDescent"]
            aggregate["radiusThreeAbsorbingDescent"] += result["radiusThreeAbsorbingDescent"]
            aggregate["noKillerButOneRowDescent"] += result["noKillerButOneRowDescent"]
            aggregate["hfarFailures"] += result["hfarFailures"]
            aggregate["hfarNoRadiusThree"] += result["hfarNoRadiusThree"]
            aggregate["hfarRadiusThreeNoAbsorbing"] += result["hfarRadiusThreeNoAbsorbing"]
            aggregate["hfarNoOneRowDescent"] += result["hfarNoOneRowDescent"]
            aggregate["negativeOneRowDeltaSum"] += result["negativeOneRowDeltaSum"]
            aggregate["nonnegativeOneRowDeltaSum"] += result["nonnegativeOneRowDeltaSum"]
            row = by_order.setdefault(
                result["order"], {
                    "graphs": 0,
                    "tuples": 0,
                    "checkedTuples": 0,
                    "failures": 0,
                    "minimizingTuples": 0,
                    "failingMinimizers": 0,
                    "oneRowDescent": 0,
                    "onlyTwoRowDescent": 0,
                    "noAtMostTwoDescent": 0,
                    "oneRowReducesActive": 0,
                    "oneRowKillsActive": 0,
                    "activeAlternativeDescent": 0,
                    "internalAlternativeDescent": 0,
                    "monotoneOneRowDescent": 0,
                    "internalKillerDescent": 0,
                    "k4KillerDescent": 0,
                    "radiusThreeAbsorbingDescent": 0,
                    "noKillerButOneRowDescent": 0,
                    "hfarFailures": 0,
                    "hfarNoRadiusThree": 0,
                    "hfarRadiusThreeNoAbsorbing": 0,
                    "hfarNoOneRowDescent": 0,
                    "negativeOneRowDeltaSum": 0,
                    "nonnegativeOneRowDeltaSum": 0,
                }
            )
            for key in row:
                row[key] += result[key]
            for failure in result["first"]:
                if len(first) < args.failure_limit:
                    first.append(failure)
            if (
                first_nonactive_alternative is None
                and result["firstNonActiveAlternative"] is not None
            ):
                first_nonactive_alternative = result["firstNonActiveAlternative"]
            if (
                first_three_outcome_failure is None
                and result["firstThreeOutcomeFailure"] is not None
            ):
                first_three_outcome_failure = result["firstThreeOutcomeFailure"]
            if (
                first_nonnegative_delta_sum is None
                and result["firstNonnegativeDeltaSum"] is not None
            ):
                first_nonnegative_delta_sum = result["firstNonnegativeDeltaSum"]
    finally:
        if pool is not None:
            pool.shutdown()

    payload = {
        "orders": [args.min_order, args.max_order],
        "workers": args.workers,
        "minimaOnly": args.minima_only,
        "includeOutside": not args.no_outside,
        "generatedGraphs": len(graph6),
        "generatedByOrder": {str(k): v for k, v in sorted(generated.items())},
        "status": dict(sorted(status.items())),
        **dict(aggregate),
        "byOrder": {str(k): v for k, v in sorted(by_order.items())},
        "firstFailures": first,
        "firstNonActiveAlternative": first_nonactive_alternative,
        "firstThreeOutcomeFailure": first_three_outcome_failure,
        "firstNonnegativeDeltaSum": first_nonnegative_delta_sum,
        "maxProduct": args.max_product,
        "minProduct": args.min_product,
        "scoreMode": args.score_mode,
        "heavyCount": heavy_count,
        "heavyTuples": heavy_tuples,
        "heavy": sorted(heavy, key=lambda row: (-row["tuples"], row["g6"])),
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    decisive_failures = (
        aggregate["failingMinimizers"] if args.minima_only
        else aggregate["failures"]
    )
    return 1 if decisive_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
