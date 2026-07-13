#!/usr/bin/env python3
"""My own CP-SAT encoding of the active-scope gate (reachability unrolling,
NOT the engine's 2-commodity flow; independent implementation) plus a
per-edge latent-feasibility model. Used as a cross-check of the solver-free
factored decisions in v5_core."""

from __future__ import annotations

from ortools.sat.python import cp_model

from v5_core import norm


def _base_model(chosen_atoms, adj, owner, active, n):
    model = cp_model.CpModel()
    support_edges = sorted({norm(u, w) for u in adj for w in adj[u]})
    vx0 = norm(owner, active)
    row_vars = []
    for i, atom in enumerate(chosen_atoms):
        rv = [model.new_bool_var(f"r{i}_{j}") for j in range(len(atom["rows"]))]
        model.add_exactly_one(rv)
        row_vars.append(rv)

    def rows_where(pred):
        return [
            row_vars[i][j]
            for i, atom in enumerate(chosen_atoms)
            for j, row in enumerate(atom["rows"])
            if pred(tuple(row))
        ]

    used = {}
    for e in support_edges:
        terms = rows_where(
            lambda row, e=e: e in {norm(row[k], row[k + 1]) for k in range(4)}
        )
        u = model.new_bool_var(f"used_{e}")
        if terms:
            model.add_bool_or(terms).only_enforce_if(u)
            for t in terms:
                model.add_implication(t, u)
        else:
            model.add(u == 0)
        used[e] = u

    model.add(sum(rows_where(lambda row: owner in row)) == 5)
    model.add(used[vx0] == 0)
    star = [y for y in sorted(adj[owner]) if y != active]
    for y in star:
        model.add(used[norm(owner, y)] == 1)
        model.add(
            sum(rows_where(lambda row, y=y: active in row and y in row)) >= 1
        )
    model.add(sum(rows_where(lambda row: active in row)) >= 1)
    return model, row_vars, used, support_edges


def gate_capture(chosen_atoms, adj, owner, active, n, workers=8):
    """SAT iff some profile-consistent selection captures a chosen atom
    (both endpoints in owner's latent component). Reachability unrolling."""
    model, row_vars, used, support_edges = _base_model(
        chosen_atoms, adj, owner, active, n
    )
    latent = {}
    for e in support_edges:
        l = model.new_bool_var(f"lat_{e}")
        model.add(l + used[e] == 1)
        latent[e] = l
    # BFS unrolling: reach[d][v]
    depth = n - 1
    reach = [[model.new_bool_var(f"reach0_{v}") for v in range(n)]]
    for v in range(n):
        model.add(reach[0][v] == (1 if v == owner else 0))
    for d in range(depth):
        cur = [model.new_bool_var(f"reach{d+1}_{v}") for v in range(n)]
        for v in range(n):
            terms = [reach[d][v]]
            for w in sorted(adj[v]):
                t = model.new_bool_var(f"step{d}_{w}_{v}")
                model.add_bool_and([reach[d][w], latent[norm(v, w)]]).only_enforce_if(t)
                model.add_bool_or(
                    [reach[d][w].negated(), latent[norm(v, w)].negated(), t]
                )
                terms.append(t)
            model.add_max_equality(cur[v], terms)
        reach.append(cur)
    final = reach[-1]
    cap = []
    for i, atom in enumerate(chosen_atoms):
        c = model.new_bool_var(f"cap_{i}")
        model.add_bool_and([final[atom["u"]], final[atom["v"]]]).only_enforce_if(c)
        cap.append(c)
    model.add_bool_or(cap)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = 300.0
    status = solver.solve(model)
    name = solver.status_name(status)
    selection = None
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        selection = [
            atom["rows"][next(j for j, v in enumerate(row_vars[i]) if solver.value(v))]
            for i, atom in enumerate(chosen_atoms)
        ]
    return name, selection


def gate_edge_unused(chosen_atoms, adj, owner, active, n, e, workers=8):
    """SAT iff a profile-consistent selection exists with edge e unused."""
    model, row_vars, used, _ = _base_model(chosen_atoms, adj, owner, active, n)
    model.add(used[tuple(e)] == 0)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = 120.0
    status = solver.solve(model)
    return solver.status_name(status)
