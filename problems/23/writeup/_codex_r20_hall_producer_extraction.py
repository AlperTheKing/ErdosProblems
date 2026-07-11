"""Exact C5[3] six-cycle trade analyzer for the R20 global minimum.

``HallFailureHasDescent`` is false: the reference balanced C5[3] row tuple is
a Hall-failing two-local minimum.  This analyzer therefore does not implement
or test the obsolete at-most-two-row producer claim.

For a C5[3] row tuple, regard each of its five layer columns as a balanced
three-symbol column.  The deterministic cycle-trade rule is:

1. Choose an internal target column and a nonadjacent source column.
2. Relabel the source by one of the six symbol permutations and replace the
   target column by it.
3. Retain the candidates changing exactly six rows whose old/new target-symbol
   transport graph is K3,3 minus a perfect matching, hence one alternating
   6-cycle.
4. Choose the exact minimum by
   ``(score, target column, source column, permutation, choice)``.

The trade candidates are structural; arbitrary k-row neighbors are never
enumerated.  A separate exact CP-SAT model certifies both the minimum changed
row count from the reference tuple and the global obligation-score minimum.
All graph, Hall, score, trade, and optimization constraints are integer-exact.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor
from itertools import permutations
from pathlib import Path

from ortools.sat.python import cp_model

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _codex_r19_global_base_census import (  # noqa: E402
    edge,
    evaluate_rows,
    global_candidates,
    multiplicities,
    owner_demands,
)
from _codex_r20_c5_blowup_local_min_gate import (  # noqa: E402
    balanced_c5,
    rows_of,
    run_start,
    verify_graph,
)
from _codex_r20_two_row_exchange_gate import obligation_score  # noqa: E402


REFERENCE_CHOICE = (12, 16, 11, 1, 5, 6, 26, 18, 22)
T = 3
N = 15
PERMUTATIONS = tuple(permutations(range(3)))


def score_state(info, families, choice):
    rows = rows_of(families, choice)
    count = multiplicities(N, rows)
    collision_units = sum(
        max(0, count[x][y] - 1)
        for x in range(N)
        for y in range(N)
    )
    vertices = {vertex for row in rows for vertex in row}
    support = {
        edge(u, v)
        for row in rows
        for u, v in zip(row, row[1:])
    }
    active = tuple(sorted(
        graph_edge
        for graph_edge in info["Bset"]
        if graph_edge[0] in vertices
        and graph_edge[1] in vertices
        and graph_edge not in support
    ))
    score = 2 * collision_units + 2 * len(active)
    assert score == obligation_score(N, info, rows)
    return score, collision_units, active


def canonical_full_matching(demands, candidates):
    nodes = [
        (owner, index)
        for owner in sorted(demands)
        for index in range(len(demands[owner]))
    ]
    nodes.sort(key=lambda node: (len(candidates[node[0]]), node))
    source_owner = {}
    demand_source = {}

    def augment(node, seen):
        owner, _ = node
        for source in sorted(candidates[owner]):
            if source in seen:
                continue
            seen.add(source)
            previous = source_owner.get(source)
            if previous is None or augment(previous, seen):
                source_owner[source] = node
                demand_source[node] = source
                return True
        return False

    unmatched = []
    for node in nodes:
        if not augment(node, set()):
            unmatched.append(node)
    assert len(demand_source) + len(unmatched) == len(nodes)
    return demand_source, tuple(sorted(unmatched))


def alternating_closure(demands, candidates, matching, unmatched):
    source_owner = {source: node for node, source in matching.items()}
    left = set(unmatched)
    right = set()
    left_order = list(unmatched)
    queue = deque(unmatched)
    while queue:
        node = queue.popleft()
        owner, _ = node
        matched_source = matching.get(node)
        for source in sorted(candidates[owner]):
            if source == matched_source or source in right:
                continue
            right.add(source)
            next_node = source_owner.get(source)
            if next_node is not None and next_node not in left:
                left.add(next_node)
                left_order.append(next_node)
                queue.append(next_node)
    assert len(left) > len(right)
    return {
        "left": left,
        "right": right,
        "leftOrder": tuple(left_order),
    }


def build_hall_instance(info, families, choice):
    rows = rows_of(families, choice)
    count = multiplicities(N, rows)
    vertices = set().union(*(set(row) for row in rows))
    support = {
        edge(u, v)
        for row in rows
        for u, v in zip(row, row[1:])
    }
    active = {
        graph_edge
        for graph_edge in info["Bset"]
        if graph_edge[0] in vertices
        and graph_edge[1] in vertices
        and graph_edge not in support
    }
    reservation_conflicts = tuple(sorted(
        graph_edge for graph_edge in active
        if count[graph_edge[0]][graph_edge[1]] != 0
    ))
    assert not reservation_conflicts
    reserved = {
        source
        for u, v in active
        for source in ((u, v, 0), (v, u, 0))
    }
    raw = owner_demands(count, vertices, active)
    demands = {
        owner: [item for item in items if item[0] == "collision"]
        for owner, items in raw.items()
    }
    demands = {owner: items for owner, items in demands.items() if items}
    candidates = {
        owner: {
            source: relation
            for source, relation in global_candidates(
                owner,
                N,
                count,
                info["adj"],
                info["Bset"],
                info["Mset"],
                "row-reserved",
            ).items()
            if source not in reserved
        }
        for owner in demands
    }
    matching, unmatched = canonical_full_matching(demands, candidates)
    if not unmatched:
        return {
            "status": "pass",
            "demands": demands,
            "candidates": candidates,
            "matching": matching,
            "active": active,
            "reserved": reserved,
        }
    closure = alternating_closure(
        demands, candidates, matching, unmatched
    )
    return {
        "status": "fail",
        "demands": demands,
        "candidates": candidates,
        "matching": matching,
        "unmatched": unmatched,
        "closure": closure,
        "active": active,
        "reserved": reserved,
    }


def hall_summary(hall):
    demand_count = sum(map(len, hall["demands"].values()))
    free_sources = set().union(*(
        set(sources) for sources in hall["candidates"].values()
    )) if hall["candidates"] else set()
    out = {
        "status": hall["status"],
        "collisionHalfDemands": demand_count,
        "eligibleUnreservedFreeHalves": len(free_sources),
        "matched": len(hall["matching"]),
        "reservedHitHalves": len(hall["reserved"]),
    }
    if hall["status"] == "fail":
        closure = hall["closure"]
        out.update({
            "unmatched": len(hall["unmatched"]),
            "hallLeft": len(closure["left"]),
            "hallRight": len(closure["right"]),
            "hallDeficiency": len(closure["left"]) - len(closure["right"]),
            "rootCollisionHalves": [
                hall["demands"][owner][index]
                for owner, index in hall["unmatched"]
            ],
        })
    return out


def decode_choice(choice):
    return tuple(
        (row_index // 9, (row_index // 3) % 3, row_index % 3)
        for row_index in choice
    )


def encode_triples(triples):
    return tuple(
        (a * 3 + b) * 3 + c for a, b, c in triples
    )


def row_columns(choice):
    triples = decode_choice(choice)
    return (
        tuple(cell // 3 for cell in range(9)),
        tuple(triple[0] for triple in triples),
        tuple(triple[1] for triple in triples),
        tuple(triple[2] for triple in triples),
        tuple(cell % 3 for cell in range(9)),
    )


def is_transport_six_cycle(old_values, new_values, changed):
    relation = Counter(
        (old_values[cell], new_values[cell]) for cell in changed
    )
    if len(changed) != 6 or len(relation) != 6:
        return False
    old_degree = Counter(old for old, _ in relation)
    new_degree = Counter(new for _, new in relation)
    return (
        old_degree == Counter({0: 2, 1: 2, 2: 2})
        and new_degree == Counter({0: 2, 1: 2, 2: 2})
    )


def minimum_cycle_trade(info, families, choice):
    old_state = score_state(info, families, choice)
    old_columns = row_columns(choice)
    old_triples = decode_choice(choice)
    candidates = []
    raw_candidates = 0
    for target_column in (1, 2, 3):
        for source_column in range(5):
            if abs(source_column - target_column) <= 1:
                continue
            for permutation in PERMUTATIONS:
                raw_candidates += 1
                new_triples = list(old_triples)
                for cell in range(9):
                    updated = list(new_triples[cell])
                    updated[target_column - 1] = permutation[
                        old_columns[source_column][cell]
                    ]
                    new_triples[cell] = tuple(updated)
                new_choice = encode_triples(new_triples)
                new_columns = row_columns(new_choice)
                changed = tuple(
                    cell for cell in range(9)
                    if choice[cell] != new_choice[cell]
                )
                if not is_transport_six_cycle(
                    old_columns[target_column],
                    new_columns[target_column],
                    changed,
                ):
                    continue
                new_state = score_state(info, families, new_choice)
                assert all(
                    sorted(column) == sorted(new_column)
                    for column, new_column in zip(
                        old_columns, new_columns
                    )
                )
                candidate = {
                    "targetColumn": target_column,
                    "sourceColumn": source_column,
                    "symbolPermutation": permutation,
                    "transportEdges": tuple(sorted({
                        (old_columns[target_column][cell],
                         new_columns[target_column][cell])
                        for cell in changed
                    })),
                    "oldChoice": choice,
                    "newChoice": new_choice,
                    "changedRows": changed,
                    "k": len(changed),
                    "oldScore": old_state[0],
                    "newScore": new_state[0],
                    "scoreDelta": new_state[0] - old_state[0],
                    "collisionDelta": new_state[1] - old_state[1],
                    "activeDelta": len(new_state[2]) - len(old_state[2]),
                    "newActiveEdges": new_state[2],
                }
                key = (
                    new_state[0],
                    target_column,
                    source_column,
                    permutation,
                    new_choice,
                )
                candidates.append((key, candidate))
    if not candidates:
        return None, raw_candidates
    return min(candidates, key=lambda item: item[0])[1], raw_candidates


def exact_score_model(reference=None):
    """Literal Boolean model of the compiled C5[3] obligation score."""
    model = cp_model.CpModel()
    value = {}
    for cell in range(9):
        left, right = divmod(cell, 3)
        fixed = (left, None, None, None, right)
        for column in range(5):
            for symbol in range(3):
                value[cell, column, symbol] = model.NewBoolVar(
                    f"value_{cell}_{column}_{symbol}"
                )
            model.AddExactlyOne(
                value[cell, column, symbol] for symbol in range(3)
            )
            if fixed[column] is not None:
                model.Add(
                    value[cell, column, fixed[column]] == 1
                )

    used = {}
    for column in range(5):
        for symbol in range(3):
            used[column, symbol] = model.NewBoolVar(
                f"used_{column}_{symbol}"
            )
            model.AddMaxEquality(
                used[column, symbol],
                [value[cell, column, symbol] for cell in range(9)],
            )

    pair_used = {}
    for left_column in range(5):
        for right_column in range(left_column + 1, 5):
            for left_symbol in range(3):
                for right_symbol in range(3):
                    occurrences = []
                    for cell in range(9):
                        occurrence = model.NewBoolVar(
                            "occurrence_"
                            f"{cell}_{left_column}_{right_column}_"
                            f"{left_symbol}_{right_symbol}"
                        )
                        model.Add(
                            occurrence <= value[
                                cell, left_column, left_symbol
                            ]
                        )
                        model.Add(
                            occurrence <= value[
                                cell, right_column, right_symbol
                            ]
                        )
                        model.Add(
                            occurrence >=
                            value[cell, left_column, left_symbol]
                            + value[cell, right_column, right_symbol] - 1
                        )
                        occurrences.append(occurrence)
                    pair_used[
                        left_column,
                        right_column,
                        left_symbol,
                        right_symbol,
                    ] = model.NewBoolVar(
                        "pair_"
                        f"{left_column}_{right_column}_"
                        f"{left_symbol}_{right_symbol}"
                    )
                    model.AddMaxEquality(
                        pair_used[
                            left_column,
                            right_column,
                            left_symbol,
                            right_symbol,
                        ],
                        occurrences,
                    )

    adjacent_used_products = []
    for column in range(4):
        for left_symbol in range(3):
            for right_symbol in range(3):
                both_used = model.NewBoolVar(
                    f"adjacent_used_{column}_{left_symbol}_{right_symbol}"
                )
                model.Add(both_used <= used[column, left_symbol])
                model.Add(both_used <= used[column + 1, right_symbol])
                model.Add(
                    both_used >= used[column, left_symbol]
                    + used[column + 1, right_symbol] - 1
                )
                adjacent_used_products.append(both_used)

    row_values = []
    for cell in range(9):
        row_value = model.NewIntVar(0, 26, f"row_value_{cell}")
        model.Add(
            row_value ==
            9 * sum(symbol * value[cell, 1, symbol]
                    for symbol in range(3))
            + 3 * sum(symbol * value[cell, 2, symbol]
                      for symbol in range(3))
            + sum(symbol * value[cell, 3, symbol]
                  for symbol in range(3))
        )
        row_values.append(row_value)

    total_used = sum(used.values())
    total_pair_used = sum(pair_used.values())
    adjacent_pair_used = sum(
        pair_used[column, column + 1, left_symbol, right_symbol]
        for column in range(4)
        for left_symbol in range(3)
        for right_symbol in range(3)
    )
    score = model.NewIntVar(0, 1000, "obligation_score")
    model.Add(
        score ==
        450 - 2 * total_used - 4 * total_pair_used
        + 2 * sum(adjacent_used_products) - 2 * adjacent_pair_used
    )

    changed = []
    if reference is not None:
        for cell, old_value in enumerate(reference):
            is_changed = model.NewBoolVar(f"changed_{cell}")
            model.Add(row_values[cell] == old_value).OnlyEnforceIf(
                is_changed.Not()
            )
            model.Add(row_values[cell] != old_value).OnlyEnforceIf(
                is_changed
            )
            changed.append(is_changed)
    return model, row_values, score, tuple(changed)


def exact_solver():
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 0
    return solver


def solve_minimum_k(info, families, reference):
    old_score = score_state(info, families, reference)[0]
    model, row_values, score, changed = exact_score_model(reference)
    model.Add(score < old_score)
    model.Minimize(sum(changed))
    solver = exact_solver()
    status = solver.Solve(model)
    assert status == cp_model.OPTIMAL
    choice = tuple(solver.Value(row_value) for row_value in row_values)
    state = score_state(info, families, choice)
    k = sum(old != new for old, new in zip(reference, choice))
    assert k == solver.Value(sum(changed))
    assert state[0] == solver.Value(score) < old_score
    return {
        "solverStatus": "OPTIMAL",
        "minimumK": k,
        "choice": choice,
        "score": state[0],
        "changedRows": tuple(
            cell for cell in range(9)
            if reference[cell] != choice[cell]
        ),
    }


def solve_canonical_global_minimum(info, families):
    model, row_values, score, _ = exact_score_model()
    model.Minimize(score)
    solver = exact_solver()
    status = solver.Solve(model)
    assert status == cp_model.OPTIMAL
    minimum_score = solver.Value(score)

    lex_model, lex_rows, lex_score, _ = exact_score_model()
    lex_model.Add(lex_score == minimum_score)
    lex_model.Minimize(sum(
        row_value * (28 ** (8 - cell))
        for cell, row_value in enumerate(lex_rows)
    ))
    lex_solver = exact_solver()
    lex_status = lex_solver.Solve(lex_model)
    assert lex_status == cp_model.OPTIMAL
    choice = tuple(lex_solver.Value(row_value) for row_value in lex_rows)
    state = score_state(info, families, choice)
    assert state[0] == minimum_score
    hall = build_hall_instance(info, families, choice)
    return {
        "solverStatus": "OPTIMAL",
        "score": minimum_score,
        "lexicographicChoice": choice,
        "collisionUnits": state[1],
        "activeEdges": state[2],
        "hall": hall_summary(hall),
    }


def analyze_choice(info, families, choice, global_minimum):
    old_state = score_state(info, families, choice)
    old_hall = build_hall_instance(info, families, choice)
    trade, candidate_count = minimum_cycle_trade(info, families, choice)
    if trade is None:
        return {
            "covered": False,
            "missingState": "no six-row column transport cycle exists",
            "choice": choice,
            "score": old_state[0],
            "hall": hall_summary(old_hall),
        }
    new_hall = build_hall_instance(
        info, families, trade["newChoice"]
    )
    covered = (
        trade["scoreDelta"] < 0
        and trade["newScore"] == global_minimum
        and new_hall["status"] == "pass"
    )
    return {
        "covered": covered,
        "missingState": None if covered else (
            "minimum column-transport six-cycle trade does not reach a Hall-passing "
            "global minimum"
        ),
        "choice": choice,
        "score": old_state[0],
        "collisionUnits": old_state[1],
        "activeEdges": old_state[2],
        "hall": hall_summary(old_hall),
        "cycleTradeCandidates": candidate_count,
        "trade": trade,
        "targetHall": hall_summary(new_hall),
    }


def collect_start_results(starts, seed, workers):
    jobs = [
        (T, seed + index, index % 2 == 0)
        for index in range(starts)
    ]
    if workers == 1:
        results = list(map(run_start, jobs))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(run_start, jobs, chunksize=1))
    counts = Counter(result["status"] for result in results)
    falsifiers = sorted(
        (result for result in results if result["status"] == "falsifier"),
        key=lambda result: (
            tuple(result["choice"]),
            result["seed"],
            result["structured"],
        ),
    )
    return counts, falsifiers


def positive_int(value):
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--starts", type=positive_int, default=256)
    parser.add_argument("--seed", type=int, default=20260711)
    parser.add_argument(
        "--workers",
        type=positive_int,
        default=min(61, os.cpu_count() or 1),
    )
    parser.add_argument(
        "--reference-only",
        action="store_true",
        help="skip the 256-start local-minimum coverage run",
    )
    args = parser.parse_args()
    if args.workers > 61:
        parser.error("--workers must not exceed 61")
    return args


def main():
    args = parse_args()
    layers, info, families = balanced_c5(T)
    graph_check = verify_graph(T, layers, info, families)
    global_minimum = solve_canonical_global_minimum(info, families)
    assert global_minimum["hall"]["status"] == "pass"
    reference_minimum_k = solve_minimum_k(
        info, families, REFERENCE_CHOICE
    )
    reference = analyze_choice(
        info,
        families,
        REFERENCE_CHOICE,
        global_minimum["score"],
    )
    assert reference["hall"]["hallLeft"] == 84
    assert reference["hall"]["hallRight"] == 72
    assert reference["hall"]["hallDeficiency"] == 12

    start_counts = Counter()
    falsifiers = []
    analyses = []
    first_cycle_falsifier = None
    if not args.reference_only:
        start_counts, falsifiers = collect_start_results(
            args.starts, args.seed, args.workers
        )
        for falsifier in falsifiers:
            choice = tuple(falsifier["choice"])
            analysis = analyze_choice(
                info, families, choice, global_minimum["score"]
            )
            analyses.append(analysis)
            if not analysis["covered"] and first_cycle_falsifier is None:
                first_cycle_falsifier = {
                    "source": falsifier,
                    "analysis": analysis,
                }

    trade_k_histogram = Counter(
        analysis["trade"]["k"]
        for analysis in analyses
        if analysis.get("trade") is not None
    )
    trade_score_histogram = Counter(
        analysis["trade"]["newScore"]
        for analysis in analyses
        if analysis.get("trade") is not None
    )
    covered = sum(analysis["covered"] for analysis in analyses)
    payload = {
        "parameters": vars(args),
        "graphCheck": graph_check,
        "obsoleteClaim": "HallFailureHasDescent / at-most-two extraction is false",
        "rule": (
            "replace one internal column by a symbol permutation of a "
            "nonadjacent column; retain six-row K3,3-minus-matching transport "
            "cycles; choose minimum (score,target,source,permutation,choice)"
        ),
        "canonicalGlobalMinimum": global_minimum,
        "referenceMinimumDescent": reference_minimum_k,
        "reference": reference,
        "startStatus": dict(sorted(start_counts.items())),
        "twoLocalFalsifierOccurrences": len(falsifiers),
        "uniqueTwoLocalFalsifiers": len({
            tuple(falsifier["choice"]) for falsifier in falsifiers
        }),
        "cycleTradeCovered": covered,
        "cycleTradeMissed": len(analyses) - covered,
        "tradeKHistogram": {
            str(k): count for k, count in sorted(trade_k_histogram.items())
        },
        "tradeTargetScoreHistogram": {
            str(score): count
            for score, count in sorted(trade_score_histogram.items())
        },
        "allCycleTradesReachHallPassingGlobalMinimum": (
            covered == len(analyses)
        ),
        "firstCycleFalsifier": first_cycle_falsifier,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
