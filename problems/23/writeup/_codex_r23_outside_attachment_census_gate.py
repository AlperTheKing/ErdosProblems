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
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from itertools import product

from _codex_r19_global_base_census import dec, graph6_for_orders, loads
from _codex_r20_two_row_exchange_gate import (
    minimum_neighbor_scores,
    obligation_score,
    shortest_row_families,
)
from _codex_r23_outside_attachment_full_obligation_gate import full_owner_flow


def evaluate_graph(
    g6: str, minima_only: bool = False, include_outside: bool = True,
    failure_limit: int = 2
):
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    if info is None:
        return {"status": "skipNoCut", "order": n}
    if any(length != 5 for length in info["ell"].values()):
        return {"status": "skipNotAll5", "order": n}

    families = shortest_row_families(info)
    family_sizes = tuple(len(family) for family in families)
    scored = []
    for choice in product(*(range(size) for size in family_sizes)):
        rows = tuple(
            families[index][row_index]
            for index, row_index in enumerate(choice)
        )
        scored.append((obligation_score(n, info, rows), choice, rows))
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
    first_nonactive_alternative = None
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
                if not active_alternative and first_nonactive_alternative is None:
                    first_nonactive_alternative = {
                        "g6": g6,
                        "order": n,
                        "choice": list(choice),
                        "rows": [list(row) for row in old_rows],
                        "flow": old_record,
                        "descent": first_descent,
                    }
            elif best_two is not None and best_two < score:
                only_two_row_descent += 1
            else:
                no_two_row_descent += 1
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
        "firstNonActiveAlternative": first_nonactive_alternative,
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
    args = parser.parse_args()
    if args.workers > 64:
        parser.error("--workers must not exceed 64")

    graph6, generated = graph6_for_orders(args.min_order, args.max_order)
    aggregate = Counter()
    status = Counter()
    by_order = {}
    first = []
    first_nonactive_alternative = None
    tasks = [(g6, args.minima_only, not args.no_outside, 2) for g6 in graph6]
    if args.workers == 1:
        results = (evaluate_graph(*task) for task in tasks)
        pool = None
    else:
        pool = ProcessPoolExecutor(max_workers=args.workers)
        results = pool.map(_evaluate_task, tasks, chunksize=4)
    try:
        for result in results:
            status[result["status"]] += 1
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
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    decisive_failures = (
        aggregate["failingMinimizers"] if args.minima_only
        else aggregate["failures"]
    )
    return 1 if decisive_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
