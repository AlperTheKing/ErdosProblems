"""Exact CP-SAT falsifier search for global-minimum Hall on C5 blow-ups.

The five positive part sizes are rotated so the displayed alternating cut
leaves a minimum adjacent product bad.  Every shortest row for every bad edge
is included.  The model first proves the global obligation-score optimum and
then asks whether a Hall-failing row tuple exists at that exact optimum.

CP-SAT is used only for finite integer discovery.  Any returned tuple is
replayed by the independent integer matcher/score implementation.
"""

from __future__ import annotations

import argparse
import json
from itertools import product

from ortools.sat.python import cp_model

from _codex_r19_global_base_census import edge, evaluate_rows
from _codex_r20_min_demand_blowup_gate import quotient_cut_value, rotate_at_min_product
from _codex_r20_two_row_exchange_gate import obligation_score


def build_fixture(raw_sizes, preserve=False):
    sizes = tuple(raw_sizes) if preserve else tuple(rotate_at_min_product(tuple(raw_sizes)))
    offsets = [0]
    for size in sizes:
        offsets.append(offsets[-1] + size)

    def vertex(part, index):
        return offsets[part] + index

    layers = tuple(
        tuple(vertex(part, index) for index in range(sizes[part]))
        for part in range(5)
    )
    n = sum(sizes)
    graph_edges = {
        edge(u, v)
        for part in range(5)
        for u in layers[part]
        for v in layers[(part + 1) % 5]
    }
    side = tuple(1 if part in (1, 3) else 0 for part, layer in enumerate(layers) for _ in layer)
    blue = {e for e in graph_edges if side[e[0]] != side[e[1]]}
    bad = graph_edges - blue
    maximum = max(
        quotient_cut_value(sizes, ones)
        for ones in product(*(range(size + 1) for size in sizes))
    )
    assert len(blue) == maximum
    assert len(bad) == sizes[0] * sizes[4]

    adjacency = [set() for _ in range(n)]
    for u, v in graph_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    assert not any(adjacency[u] & adjacency[v] for u, v in graph_edges)

    families = []
    bad_order = []
    for u in layers[0]:
        for v in layers[4]:
            family = tuple(
                (u, x1, x2, x3, v)
                for x1 in layers[1]
                for x2 in layers[2]
                for x3 in layers[3]
            )
            assert family
            families.append(family)
            bad_order.append(edge(u, v))
    info = {
        "n": n,
        "adj": adjacency,
        "Bset": blue,
        "Mset": bad,
        "badOrder": tuple(bad_order),
    }
    return sizes, layers, info, tuple(families)


def build_model(info, families, score_equal=None):
    n = info["n"]
    model = cp_model.CpModel()
    choose = [
        [model.new_bool_var(f"z_{i}_{r}") for r in range(len(family))]
        for i, family in enumerate(families)
    ]
    for row in choose:
        model.add_exactly_one(row)

    pair_count = {}
    covered = {}
    collision = []
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
            pair_count[x, y] = count
            cov = model.new_bool_var(f"cov_{x}_{y}")
            model.add(count >= 1).only_enforce_if(cov)
            model.add(count == 0).only_enforce_if(cov.Not())
            covered[x, y] = cov
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
    active = {}
    for u, v in sorted(info["Bset"]):
        terms = [
            choose[i][r]
            for i, family in enumerate(families)
            for r, row in enumerate(family)
            if edge(u, v) in {edge(a, b) for a, b in zip(row, row[1:])}
        ]
        used = model.new_bool_var(f"support_{u}_{v}")
        model.add_max_equality(used, terms)
        support[u, v] = used
        flag = model.new_bool_var(f"active_{u}_{v}")
        model.add_bool_and([selected[u], selected[v], used.Not()]).only_enforce_if(flag)
        model.add_bool_or([selected[u].Not(), selected[v].Not(), used, flag])
        active[u, v] = flag

    upper = 2 * (n * n * len(families) + len(info["Bset"]))
    score = model.new_int_var(0, upper, "score")
    model.add(score == 2 * sum(collision) + 2 * sum(active.values()))
    if score_equal is not None:
        model.add(score == score_equal)
    return model, choose, score, pair_count, covered, active


def selected_choice(solver, choose):
    return tuple(
        next(i for i, z in enumerate(row) if solver.value(z))
        for row in choose
    )


def rows_of(families, choice):
    return tuple(families[i][r] for i, r in enumerate(choice))


def solve_optimum(info, families, workers, time_limit):
    model, choose, score, _, _, _ = build_model(info, families)
    model.minimize(score)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.solve(model)
    out = {
        "status": solver.status_name(status),
        "wallTime": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }
    if status == cp_model.OPTIMAL:
        out["score"] = solver.value(score)
        out["choice"] = selected_choice(solver, choose)
    return out


def solve_failing_optimum(info, families, optimum, workers, time_limit):
    n = info["n"]
    model, choose, score, pair_count, covered, active = build_model(
        info, families, optimum
    )
    owner = [model.new_bool_var(f"owner_{x}") for x in range(n)]
    model.add(sum(owner) >= 1)
    left_terms = []
    for x in range(n):
        demand = model.new_int_var(0, 2 * 5 * len(families), f"demand_{x}")
        model.add(demand == 2 * sum(pair_count[x, y] - covered[x, y] for y in range(n)))
        term = model.new_int_var(0, 2 * 5 * len(families), f"left_{x}")
        model.add_multiplication_equality(term, [owner[x], demand])
        left_terms.append(term)

    right_terms = []
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            witnesses = [owner[a]]
            for x in range(n):
                witness = model.new_bool_var(f"comp_{x}_{a}_{b}")
                lits = [owner[x], covered[x, a], covered[x, b]]
                model.add_bool_and(lits).only_enforce_if(witness)
                model.add_bool_or([lit.Not() for lit in lits] + [witness])
                witnesses.append(witness)
            eligible = model.new_bool_var(f"eligible_{a}_{b}")
            model.add_max_equality(eligible, witnesses)
            free = covered[a, b].Not()
            for half in range(2):
                available = model.new_bool_var(f"source_{a}_{b}_{half}")
                required = [free, eligible]
                active_edge = active.get(edge(a, b))
                if half == 0 and active_edge is not None:
                    required.append(active_edge.Not())
                model.add_bool_and(required).only_enforce_if(available)
                model.add_bool_or([lit.Not() for lit in required] + [available])
                right_terms.append(available)
    model.add(sum(left_terms) >= sum(right_terms) + 1)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.solve(model)
    out = {
        "status": solver.status_name(status),
        "wallTime": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        out["score"] = solver.value(score)
        out["choice"] = selected_choice(solver, choose)
        out["owners"] = [x for x in range(n) if solver.value(owner[x])]
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", required=True, help="five comma-separated positive integers")
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--time-limit", type=float, default=900.0)
    parser.add_argument("--preserve", action="store_true",
        help="preserve the supplied cyclic order; requires A4*A0 to define a maximum cut")
    args = parser.parse_args()
    sizes_in = tuple(int(x) for x in args.sizes.split(","))
    if len(sizes_in) != 5 or min(sizes_in) < 1:
        parser.error("--sizes needs five positive integers")
    if not 1 <= args.workers <= 64:
        parser.error("--workers must be in [1,64]")

    sizes, layers, info, families = build_fixture(sizes_in, args.preserve)
    optimum = solve_optimum(info, families, args.workers, args.time_limit)
    failing = None
    replay = None
    if optimum["status"] == "OPTIMAL":
        choice = optimum["choice"]
        rows = rows_of(families, choice)
        assert obligation_score(info["n"], info, rows) == optimum["score"]
        kind, _, detail = evaluate_rows(
            f"C5{sizes}", info["n"], info, rows, "row-reserved"
        )
        replay = {"status": kind, "detail": detail}
        failing = solve_failing_optimum(
            info, families, optimum["score"], args.workers, args.time_limit
        )
        if failing["status"] in ("FEASIBLE", "OPTIMAL"):
            bad_rows = rows_of(families, failing["choice"])
            assert obligation_score(info["n"], info, bad_rows) == optimum["score"]
            kind, _, detail = evaluate_rows(
                f"C5{sizes}-failing", info["n"], info, bad_rows, "row-reserved"
            )
            assert kind == "fail"
            failing["independentReplay"] = detail
            failing["rows"] = [list(row) for row in bad_rows]

    print(json.dumps({
        "inputSizes": sizes_in,
        "rotatedSizes": sizes,
        "n": info["n"],
        "badEdges": len(info["Mset"]),
        "rowsPerBad": len(families[0]),
        "rowChoiceVariables": sum(map(len, families)),
        "globalOptimum": optimum,
        "optimumReplay": replay,
        "failingGlobalOptimumSearch": failing,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
