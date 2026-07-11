"""Exact-integer CP-SAT discovery model for the C5[t] row-choice potential."""

from __future__ import annotations

import argparse
import json

from ortools.sat.python import cp_model

from _codex_r19_global_base_census import edge, evaluate_rows
from _codex_r20_c5_blowup_local_min_gate import balanced_c5, rows_of, verify_graph
from _codex_r20_two_row_exchange_gate import obligation_score


WITNESS_T3 = (12, 16, 11, 1, 5, 6, 26, 18, 22)


def build_model(t: int, score_upper: int | None = None):
    n = 5 * t
    layers, info, families = balanced_c5(t)
    model = cp_model.CpModel()
    choose = [
        [model.new_bool_var(f"z_{i}_{r}") for r in range(len(family))]
        for i, family in enumerate(families)
    ]
    for row_vars in choose:
        model.add_exactly_one(row_vars)

    collision = []
    pair_count = {}
    covered = {}
    for x in range(n):
        for y in range(n):
            terms = [
                choose[i][r]
                for i, family in enumerate(families)
                for r, row in enumerate(family)
                if x in row and y in row
            ]
            count = model.new_int_var(0, len(families), f"cnt_{x}_{y}")
            model.add(count == sum(terms) if terms else count == 0)
            pair_count[(x, y)] = count
            cov = model.new_bool_var(f"covered_{x}_{y}")
            model.add(count >= 1).only_enforce_if(cov)
            model.add(count == 0).only_enforce_if(cov.Not())
            covered[(x, y)] = cov
            excess = model.new_int_var(0, len(families), f"exc_{x}_{y}")
            model.add_max_equality(excess, [count - 1, 0])
            collision.append(excess)

    selected = []
    for v in range(n):
        terms = [
            choose[i][r]
            for i, family in enumerate(families)
            for r, row in enumerate(family)
            if v in row
        ]
        flag = model.new_bool_var(f"selected_{v}")
        model.add_max_equality(flag, terms)
        selected.append(flag)

    support = {}
    for u, v in sorted(info["Bset"]):
        terms = [
            choose[i][r]
            for i, family in enumerate(families)
            for r, row in enumerate(family)
            if edge(u, v) in {edge(a, b) for a, b in zip(row, row[1:])}
        ]
        flag = model.new_bool_var(f"support_{u}_{v}")
        model.add_max_equality(flag, terms)
        support[(u, v)] = flag

    active = []
    active_by_edge = {}
    for u, v in sorted(info["Bset"]):
        flag = model.new_bool_var(f"active_{u}_{v}")
        model.add_bool_and([selected[u], selected[v], support[(u, v)].Not()]).only_enforce_if(flag)
        model.add_bool_or([selected[u].Not(), selected[v].Not(), support[(u, v)], flag])
        active.append(flag)
        active_by_edge[(u, v)] = flag

    score = model.new_int_var(0, 2 * (n * n * len(families) + len(info["Bset"])), "score")
    model.add(score == 2 * sum(collision) + 2 * sum(active))
    if score_upper is not None:
        model.add(score <= score_upper)
    state = {
        "pairCount": pair_count,
        "covered": covered,
        "collision": collision,
        "active": active_by_edge,
    }
    return model, choose, score, layers, info, families, state


def solve_score(t: int, workers: int):
    model, choose, score, layers, info, families, _ = build_model(t)
    model.minimize(score)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    status = solver.solve(model)
    assert status == cp_model.OPTIMAL
    choice = tuple(
        next(r for r, z in enumerate(row_vars) if solver.value(z))
        for row_vars in choose
    )
    return {
        "status": solver.status_name(status),
        "score": solver.value(score),
        "choice": choice,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "wallTime": solver.wall_time,
    }, (layers, info, families)


def solve_min_trade(t: int, workers: int, witness, upper: int):
    model, choose, score, layers, info, families, _ = build_model(t, upper)
    unchanged = []
    for i, row_vars in enumerate(choose):
        unchanged.append(row_vars[witness[i]])
    model.maximize(sum(unchanged))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    status = solver.solve(model)
    assert status == cp_model.OPTIMAL
    choice = tuple(
        next(r for r, z in enumerate(row_vars) if solver.value(z))
        for row_vars in choose
    )
    return {
        "status": solver.status_name(status),
        "score": solver.value(score),
        "choice": choice,
        "hamming": sum(a != b for a, b in zip(choice, witness)),
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "wallTime": solver.wall_time,
    }, (layers, info, families)


def solve_failing_optimum(t: int, workers: int, optimum: int):
    """Ask whether any globally optimal row tuple violates finite Hall."""
    n = 5 * t
    model, choose, score, layers, info, families, state = build_model(t, optimum)
    model.add(score == optimum)
    owner = [model.new_bool_var(f"hall_owner_{x}") for x in range(n)]
    demand_terms = []
    for x in range(n):
        demand = model.new_int_var(0, 2 * 5 * len(families), f"hall_demand_{x}")
        model.add(demand == 2 * sum(
            state["pairCount"][(x, y)] - state["covered"][(x, y)]
            for y in range(n)
        ))
        contribution = model.new_int_var(0, 2 * 5 * len(families), f"hall_left_{x}")
        model.add_multiplication_equality(contribution, [owner[x], demand])
        demand_terms.append(contribution)

    candidates = []
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            eligible_terms = [owner[a]]
            for x in range(n):
                term = model.new_bool_var(f"hall_comp_{x}_{a}_{b}")
                lits = [owner[x], state["covered"][(x, a)], state["covered"][(x, b)]]
                model.add_bool_and(lits).only_enforce_if(term)
                model.add_bool_or([lit.Not() for lit in lits] + [term])
                eligible_terms.append(term)
            eligible = model.new_bool_var(f"hall_eligible_{a}_{b}")
            model.add_max_equality(eligible, eligible_terms)
            for half in range(2):
                candidate = model.new_bool_var(f"hall_source_{a}_{b}_{half}")
                required = [state["covered"][(a, b)].Not(), eligible]
                if half == 0 and edge(a, b) in state["active"]:
                    required.append(state["active"][edge(a, b)].Not())
                model.add_bool_and(required).only_enforce_if(candidate)
                model.add_bool_or([lit.Not() for lit in required] + [candidate])
                candidates.append(candidate)
    model.add(sum(demand_terms) >= sum(candidates) + 1)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    status = solver.solve(model)
    out = {
        "status": solver.status_name(status),
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "wallTime": solver.wall_time,
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        choice = tuple(
            next(r for r, z in enumerate(row_vars) if solver.value(z))
            for row_vars in choose
        )
        out.update({
            "choice": choice,
            "score": solver.value(score),
            "hallOwners": [x for x in range(n) if solver.value(owner[x])],
            "rows": [list(row) for row in rows_of(families, choice)],
        })
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--t", type=int, default=3)
    parser.add_argument("--workers", type=int, default=64)
    args = parser.parse_args()
    if args.t < 2:
        parser.error("--t must be at least 2")
    if not 1 <= args.workers <= 64:
        parser.error("--workers must be between 1 and 64")

    optimum, data = solve_score(args.t, args.workers)
    layers, info, families = data
    graph_check = verify_graph(args.t, layers, info, families)
    optimum_rows = rows_of(families, optimum["choice"])
    assert obligation_score(5 * args.t, info, optimum_rows) == optimum["score"]
    match_kind, _, match_detail = evaluate_rows(
        f"C5[{args.t}]-cpsat-optimum", 5 * args.t, info, optimum_rows, "row-reserved"
    )
    optimum["matching"] = match_kind
    optimum["matchingDetail"] = match_detail
    optimum["rows"] = [list(row) for row in optimum_rows]
    failing_optimum = solve_failing_optimum(
        args.t, args.workers, optimum["score"]
    )

    trade = None
    if args.t == 3:
        witness_rows = rows_of(families, WITNESS_T3)
        witness_score = obligation_score(15, info, witness_rows)
        trade, _ = solve_min_trade(
            3, args.workers, WITNESS_T3, witness_score - 1
        )
        trade_rows = rows_of(families, trade["choice"])
        assert obligation_score(15, info, trade_rows) == trade["score"]
        trade["rows"] = [list(row) for row in trade_rows]

    print(json.dumps({
        "parameters": vars(args),
        "graphCheck": graph_check,
        "globalOptimum": optimum,
        "failingGlobalOptimumSearch": failing_optimum,
        "minimumStrictTradeFromWitness": trade,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
