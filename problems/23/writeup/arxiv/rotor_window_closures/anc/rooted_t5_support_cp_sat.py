#!/usr/bin/env python3
"""Rooted t=5 live-rotor support/circuit search.

This is a falsifier engine, not a proof by bounded search.  It fixes the live
middle-swap core in a connected 24-edge bipartite support graph and asks for a
triangle-free 25-atom family whose complete distance-four footprints form an
inclusion-minimal defect-one transversal circuit.

The rooted labels are:

  left:  v=0, m=1, a=2, b=3
  right: x=0, y=1

and the mandatory blue paths are (a,x,v,y,b) and (a,x,m,y,b).

The former t=4-derived common bad neighbour and the scalar row-count
condition ``r(owner)=5`` are optional regression gates.  Neither is imposed
by default in the t=5 search.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import permutations
from pathlib import Path

import networkx as nx
from ortools.sat.python import cp_model


V, M, A, B, SHARED = 0, 1, 2, 3, 4
X, Y = 0, 1


def norm(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def and2(model: cp_model.CpModel, left, right, name: str):
    out = model.new_bool_var(name)
    model.add(out <= left)
    model.add(out <= right)
    model.add(out >= left + right - 1)
    return out


def and_all(model: cp_model.CpModel, terms, name: str):
    terms = list(terms)
    out = model.new_bool_var(name)
    for term in terms:
        model.add(out <= term)
    model.add(out >= sum(terms) - len(terms) + 1)
    return out


def build_rooted_support_model(
    left_n: int,
    right_n: int,
    require_shared_bad_neighbour: bool,
    require_live_pair_geometry: bool,
):
    if left_n < 7 or right_n < 5:
        raise ValueError("t=5 two-owner roots require left >= 7 and right >= 5")

    model = cp_model.CpModel()
    edge = {
        (u, r): model.new_bool_var(f"e_{u}_{r}")
        for u in range(left_n)
        for r in range(right_n)
    }
    model.add(sum(edge.values()) == 24)

    # The two complete shortest rows differing only at the middle.
    for key in [(A, X), (V, X), (M, X), (V, Y), (M, Y), (B, Y)]:
        model.add(edge[key] == 1)

    # Both rotating owners are degree-five blue-star owners.
    model.add(sum(edge[V, r] for r in range(right_n)) == 5)
    model.add(sum(edge[M, r] for r in range(right_n)) == 5)

    # Every support vertex occurs, as F* is connected.
    for u in range(left_n):
        model.add(sum(edge[u, r] for r in range(right_n)) >= 1)
    for r in range(right_n):
        model.add(sum(edge[u, r] for u in range(left_n)) >= 1)

    # Single-commodity connectivity flow rooted at v.
    node_count = left_n + right_n
    outflow = [[] for _ in range(node_count)]
    inflow = [[] for _ in range(node_count)]
    for u in range(left_n):
        for r in range(right_n):
            rr = left_n + r
            f_lr = model.new_int_var(0, node_count - 1, f"flr_{u}_{r}")
            f_rl = model.new_int_var(0, node_count - 1, f"frl_{u}_{r}")
            model.add(f_lr <= (node_count - 1) * edge[u, r])
            model.add(f_rl <= (node_count - 1) * edge[u, r])
            outflow[u].append(f_lr)
            inflow[rr].append(f_lr)
            outflow[rr].append(f_rl)
            inflow[u].append(f_rl)
    model.add(sum(outflow[V]) - sum(inflow[V]) == node_count - 1)
    for z in range(node_count):
        if z == V:
            continue
        model.add(sum(inflow[z]) - sum(outflow[z]) == 1)

    # Distance-two relations on each shore.
    has2_left = {}
    for u in range(left_n):
        for w in range(u + 1, left_n):
            witnesses = [
                and2(model, edge[u, r], edge[w, r], f"l2w_{u}_{w}_{r}")
                for r in range(right_n)
            ]
            has2_left[u, w] = model.new_bool_var(f"l2_{u}_{w}")
            model.add_max_equality(has2_left[u, w], witnesses)

    has2_right = {}
    for r in range(right_n):
        for s in range(r + 1, right_n):
            witnesses = [
                and2(model, edge[u, r], edge[u, s], f"r2w_{r}_{s}_{u}")
                for u in range(left_n)
            ]
            has2_right[r, s] = model.new_bool_var(f"r2_{r}_{s}")
            model.add_max_equality(has2_right[r, s], witnesses)

    def l2(u: int, w: int):
        return has2_left[min(u, w), max(u, w)]

    def r2(r: int, s: int):
        return has2_right[min(r, s), max(r, s)]

    # Exact distance-four: a two-step in the shore square, but no length-two
    # blue path.  Under the latter condition the two square witnesses cannot
    # reuse the same opposite-shore vertex, so they give a simple 4-path.
    d4_left = {}
    for u in range(left_n):
        for w in range(u + 1, left_n):
            via = [
                and2(model, l2(u, z), l2(z, w), f"l4w_{u}_{w}_{z}")
                for z in range(left_n)
                if z not in {u, w}
            ]
            path4 = model.new_bool_var(f"l4path_{u}_{w}")
            model.add_max_equality(path4, via)
            d4 = model.new_bool_var(f"l4_{u}_{w}")
            model.add(d4 <= path4)
            model.add(d4 + l2(u, w) <= 1)
            model.add(d4 >= path4 - l2(u, w))
            d4_left[u, w] = d4

    d4_right = {}
    for r in range(right_n):
        for s in range(r + 1, right_n):
            via = [
                and2(model, r2(r, z), r2(z, s), f"r4w_{r}_{s}_{z}")
                for z in range(right_n)
                if z not in {r, s}
            ]
            path4 = model.new_bool_var(f"r4path_{r}_{s}")
            model.add_max_equality(path4, via)
            d4 = model.new_bool_var(f"r4_{r}_{s}")
            model.add(d4 <= path4)
            model.add(d4 + r2(r, s) <= 1)
            model.add(d4 >= path4 - r2(r, s))
            d4_right[r, s] = d4

    def ld4(u: int, w: int):
        return d4_left[min(u, w), max(u, w)]

    def rd4(r: int, s: int):
        return d4_right[min(r, s), max(r, s)]

    coverage_cache = {}

    def right_pair_on_distance_four_row(p: int, q: int):
        key = tuple(sorted((p, q)))
        if key in coverage_cache:
            return coverage_cache[key]
        witnesses = []

        # The pair occupies the two right-shore internal positions of a row
        # whose bad endpoints lie on the left shore.
        for first, second in [(p, q), (q, p)]:
            for l0 in range(left_n):
                for l2 in range(left_n):
                    if l2 == l0:
                        continue
                    for l4 in range(left_n):
                        if l4 in {l0, l2}:
                            continue
                        witnesses.append(
                            and_all(
                                model,
                                [
                                    edge[l0, first],
                                    edge[l2, first],
                                    edge[l2, second],
                                    edge[l4, second],
                                    ld4(l0, l4),
                                ],
                                f"covL_{p}_{q}_{first}_{l0}_{l2}_{l4}",
                            )
                        )

        # Or the pair occupies two of the three right-shore positions of a
        # row whose bad endpoints lie on the right shore.
        for extra in range(right_n):
            if extra in {p, q}:
                continue
            for r0, r2, r4 in permutations((p, q, extra)):
                for l1 in range(left_n):
                    for l3 in range(left_n):
                        if l1 == l3:
                            continue
                        witnesses.append(
                            and_all(
                                model,
                                [
                                    edge[l1, r0],
                                    edge[l1, r2],
                                    edge[l3, r2],
                                    edge[l3, r4],
                                    rd4(r0, r4),
                                ],
                                f"covR_{p}_{q}_{r0}_{r2}_{r4}_{l1}_{l3}",
                            )
                        )
        covered = model.new_bool_var(f"right_pair_row_{p}_{q}")
        model.add_max_equality(covered, witnesses)
        coverage_cache[key] = covered
        return covered

    # Rooted live atom.  The shared owner bad neighbour is a t=4-derived
    # regression condition, not a default t=5 hypothesis.
    model.add(ld4(A, B) == 1)
    if require_shared_bad_neighbour:
        model.add(ld4(V, SHARED) == 1)
        model.add(ld4(M, SHARED) == 1)
    model.add(sum(ld4(V, u) for u in range(left_n) if u != V) >= 5)
    model.add(sum(ld4(M, u) for u in range(left_n) if u != M) >= 5)
    model.add(sum(d4_left.values()) + sum(d4_right.values()) >= 25)

    if require_live_pair_geometry:
        # In the source tuple vx is active, so every other v-neighbour must
        # share a selected shortest row with x.  At the target, exactly one
        # of mx,my is active; statically, one of those two pair-cover profiles
        # must be available in the complete row database.
        for s in range(right_n):
            if s != X:
                model.add(edge[V, s] <= right_pair_on_distance_four_row(X, s))
        target_active_x = model.new_bool_var("support_target_active_x")
        target_active_y = model.new_bool_var("support_target_active_y")
        model.add(target_active_x + target_active_y == 1)
        for active, choice in [(X, target_active_x), (Y, target_active_y)]:
            for s in range(right_n):
                if s == active:
                    continue
                model.add(
                    edge[M, s] + choice - 1
                    <= right_pair_on_distance_four_row(active, s)
                )

    # Safe label symmetries: vertices beyond the five rooted left vertices and
    # beyond x,y on the right have no distinguished role.
    left_degrees = [sum(edge[u, r] for r in range(right_n)) for u in range(left_n)]
    right_degrees = [sum(edge[u, r] for u in range(left_n)) for r in range(right_n)]
    rooted_left = 5 if require_shared_bad_neighbour else 4
    for u in range(rooted_left, left_n - 1):
        model.add(left_degrees[u] >= left_degrees[u + 1])
    for r in range(2, right_n - 1):
        model.add(right_degrees[r] >= right_degrees[r + 1])

    return model, edge


def graph_from_solution(solver, edge, left_n: int, right_n: int) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(left_n + right_n))
    for (u, r), var in edge.items():
        if solver.value(var):
            graph.add_edge(u, left_n + r)
    return graph


def xor_var(model: cp_model.CpModel, a, b, name: str):
    out = model.new_bool_var(name)
    model.add(out >= a - b)
    model.add(out >= b - a)
    model.add(out <= a + b)
    model.add(out <= 2 - a - b)
    return out


def minimum_switch_sigma(
    vertex_count: int,
    blue_edges: list[tuple[int, int]],
    bad_edges: list[tuple[int, int]],
    workers: int,
    time_limit: float,
):
    model = cp_model.CpModel()
    side = [model.new_bool_var(f"s_{v}") for v in range(vertex_count)]
    model.add(side[0] == 0)
    blue_cross = [
        xor_var(model, side[u], side[v], f"b_{i}")
        for i, (u, v) in enumerate(blue_edges)
    ]
    bad_cross = [
        xor_var(model, side[u], side[v], f"m_{i}")
        for i, (u, v) in enumerate(bad_edges)
    ]
    model.minimize(sum(blue_cross) - sum(bad_cross))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = min(workers, 8)
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = 1
    status = solver.solve(model)
    if status != cp_model.OPTIMAL:
        return None, solver.status_name(status)
    switch = {v for v in range(vertex_count) if solver.value(side[v])}
    sigma = sum((u in switch) ^ (v in switch) for u, v in blue_edges) - sum(
        (u in switch) ^ (v in switch) for u, v in bad_edges
    )
    return (sigma, switch), solver.status_name(status)


def distance_four_atoms(graph: nx.Graph, left_n: int, right_n: int):
    atoms = []
    shores = [("L", list(range(left_n))), ("R", list(range(left_n, left_n + right_n)))]
    for shore, vertices in shores:
        for i, u in enumerate(vertices):
            for w in vertices[i + 1 :]:
                if nx.shortest_path_length(graph, u, w) != 4:
                    continue
                rows = [tuple(path) for path in nx.all_shortest_paths(graph, u, w)]
                footprint = sorted(
                    {
                        tuple(sorted((path[k], path[k + 1])))
                        for path in rows
                        for k in range(4)
                    }
                )
                atoms.append(
                    {
                        "shore": shore,
                        "u": u,
                        "v": w,
                        "rows": rows,
                        "footprintEdges": footprint,
                    }
                )
    return atoms


def active_scope_profile_for_fixed_selection(
    graph: nx.Graph,
    atoms: list[dict],
    chosen: list[int],
    owner: int,
    active: int,
    workers: int,
    time_limit: float,
):
    """Choose one row per atom and require a positive active owner scope."""
    support_edges = sorted(norm(*edge) for edge in graph.edges())
    model = cp_model.CpModel()
    row_selected = {}
    for i in chosen:
        variables = [
            model.new_bool_var(f"scope_row_{i}_{j}")
            for j in range(len(atoms[i]["rows"]))
        ]
        model.add(sum(variables) == 1)
        row_selected[i] = variables

    def row_terms(predicate):
        return [
            row_selected[i][j]
            for i in chosen
            for j, row in enumerate(atoms[i]["rows"])
            if predicate(tuple(row))
        ]

    selected_support = {}
    active_edge = {}
    for edge in support_edges:
        uses = row_terms(
            lambda row, e=edge: e
            in {norm(row[k], row[k + 1]) for k in range(4)}
        )
        present = model.new_bool_var(f"scope_support_{edge[0]}_{edge[1]}")
        model.add(sum(uses) >= present)
        model.add(sum(uses) <= len(chosen) * present)
        selected_support[edge] = present
        active_var = model.new_bool_var(f"scope_active_{edge[0]}_{edge[1]}")
        model.add(active_var + present == 1)
        active_edge[edge] = active_var

    neighbours = sorted(graph[owner])
    model.add(sum(row_terms(lambda row: owner in row)) == 5)
    for neighbour in neighbours:
        present = selected_support[norm(owner, neighbour)]
        model.add(present == (0 if neighbour == active else 1))
        if neighbour != active:
            model.add(
                sum(
                    row_terms(
                        lambda row, y=neighbour: active in row and y in row
                    )
                )
                >= 1
            )
    model.add(sum(row_terms(lambda row: active in row)) >= 1)

    scope_atom = {i: model.new_bool_var(f"scope_atom_{i}") for i in chosen}
    model.add(sum(scope_atom.values()) == 1)
    flows = []
    for commodity in range(2):
        flow = {}
        for edge in support_edges:
            for u, v in [edge, edge[::-1]]:
                var = model.new_bool_var(f"scope_flow_{commodity}_{u}_{v}")
                model.add(var <= active_edge[edge])
                flow[u, v] = var
        flows.append(flow)
        for z in graph.nodes():
            outflow = sum(var for (u, _), var in flow.items() if u == z)
            inflow = sum(var for (_, v), var in flow.items() if v == z)
            endpoint = "u" if commodity == 0 else "v"
            sink = sum(scope_atom[i] for i in chosen if atoms[i][endpoint] == z)
            model.add(outflow - inflow == (1 if z == owner else 0) - sink)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = min(workers, 8)
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = 1
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, solver.status_name(status)
    scope = next(i for i, var in scope_atom.items() if solver.value(var))
    return {
        "owner": owner,
        "activeNeighbour": active,
        "scopeAtom": scope,
        "scopeBadEdge": [atoms[scope]["u"], atoms[scope]["v"]],
        "selectedRows": {
            str(i): list(atoms[i]["rows"][next(
                j for j, var in enumerate(row_selected[i]) if solver.value(var)
            )])
            for i in chosen
        },
        "activeEdges": [
            list(edge) for edge, var in active_edge.items() if solver.value(var)
        ],
        "flows": [
            [[u, v] for (u, v), var in flow.items() if solver.value(var)]
            for flow in flows
        ],
    }, solver.status_name(status)


def choose_minimal_circuit(
    graph: nx.Graph,
    atoms: list[dict],
    left_n: int,
    right_n: int,
    workers: int,
    time_limit: float,
    minimize_core_deficit: bool,
    max_core_deficit: int | None,
    require_two_owner_profile: bool,
    require_live_transition_profile: bool,
    require_shared_bad_neighbour: bool,
    owner_row_count: int | None,
    support_min_multiplicity: int,
    require_deletion_sdr: bool,
    require_bad_triangle_free: bool,
    selected_atom_count: int,
    owner_bad_degree: int,
    classifier_owners: tuple[int, ...],
    require_active_scope: bool,
    classifier_active_min_degree: int,
    classifier_allowed_active: frozenset[int] | None,
):
    support_edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    edge_index = {edge: i for i, edge in enumerate(support_edges)}
    for atom in atoms:
        atom["footprint"] = [edge_index[tuple(edge)] for edge in atom["footprintEdges"]]

    atom_index = {
        (atom["shore"], atom["u"], atom["v"]): i for i, atom in enumerate(atoms)
    }

    def left_atom(u: int, w: int):
        return atom_index[("L", min(u, w), max(u, w))]

    required = [left_atom(A, B)]
    if require_shared_bad_neighbour:
        required.extend([left_atom(V, SHARED), left_atom(M, SHARED)])
    live_atom = left_atom(A, B)
    live_rows = {tuple(row) for row in atoms[live_atom]["rows"]}
    expected_v = (A, left_n + X, V, left_n + Y, B)
    expected_m = (A, left_n + X, M, left_n + Y, B)
    if expected_v not in live_rows or expected_m not in live_rows:
        return None, "rooted live rows absent after exact shortest-path replay", None

    model = cp_model.CpModel()
    selected = [model.new_bool_var(f"atom_{i}") for i in range(len(atoms))]
    model.add(sum(selected) == selected_atom_count)
    for idx in required:
        model.add(selected[idx] == 1)

    # The production t=5 window has five bad-star atoms at each owner.
    owner_v = [i for i, atom in enumerate(atoms) if V in {atom["u"], atom["v"]}]
    owner_m = [i for i, atom in enumerate(atoms) if M in {atom["u"], atom["v"]}]
    model.add(sum(selected[i] for i in owner_v) == owner_bad_degree)
    model.add(sum(selected[i] for i in owner_m) == owner_bad_degree)

    # The selected bad graph is triangle-free on each cut shore.
    if require_bad_triangle_free:
        for vertices, tag in [
            (list(range(left_n)), "L"),
            (list(range(left_n, left_n + right_n)), "R"),
        ]:
            for i, u in enumerate(vertices):
                for j in range(i + 1, len(vertices)):
                    w = vertices[j]
                    for z in vertices[j + 1 :]:
                        keys = [
                            (tag, min(u, w), max(u, w)),
                            (tag, min(u, z), max(u, z)),
                            (tag, min(w, z), max(w, z)),
                        ]
                        if all(key in atom_index for key in keys):
                            model.add(
                                sum(selected[atom_index[key]] for key in keys) <= 2
                            )

    # A minimal defect-one circuit has multiplicity at least two.  Lower
    # values are diagnostic relaxations used to locate the first obstruction.
    for e in range(len(support_edges)):
        incident = [i for i, atom in enumerate(atoms) if e in atom["footprint"]]
        model.add(
            sum(selected[i] for i in incident) >= support_min_multiplicity
        )

    # Exact deletion-SDR certificates.  If atom ex is selected, every support
    # edge is matched once to a distinct selected atom other than ex.
    if require_deletion_sdr:
        for ex in range(len(atoms)):
            by_edge = [[] for _ in support_edges]
            by_atom = [[] for _ in atoms]
            for i, atom in enumerate(atoms):
                if i == ex:
                    continue
                for e in atom["footprint"]:
                    match = model.new_bool_var(f"mat_{ex}_{i}_{e}")
                    model.add(match <= selected[ex])
                    model.add(match <= selected[i])
                    by_edge[e].append(match)
                    by_atom[i].append(match)
            for bucket in by_edge:
                model.add(sum(bucket) == selected[ex])
            for bucket in by_atom:
                if bucket:
                    model.add(sum(bucket) <= selected[ex])

    classifier_data = {}
    for owner in classifier_owners:
        neighbours = sorted(graph[owner])
        if len(neighbours) != 5:
            return None, "OWNER_BLUE_DEGREE_NOT_FIVE", None
        incident = [
            i for i, atom in enumerate(atoms) if owner in {atom["u"], atom["v"]}
        ]

        # Forced(v)=Inc(v): no selected nonincident atom may have every
        # complete shortest row passing through the owner.
        for i, atom in enumerate(atoms):
            if i in incident:
                continue
            if all(owner in row for row in atom["rows"]):
                model.add(selected[i] == 0)

        active_vars = {
            x: model.new_bool_var(f"classifier_{owner}_active_{x}")
            for x in neighbours
        }
        model.add(sum(active_vars.values()) == 1)
        for x, active_var in active_vars.items():
            if graph.degree[x] < classifier_active_min_degree:
                model.add(active_var == 0)
            if classifier_allowed_active is not None and x not in classifier_allowed_active:
                model.add(active_var == 0)
        step_matches = {}
        coverage_matches = {}

        for active, active_var in active_vars.items():
            support_neighbours = [y for y in neighbours if y != active]

            # Every selected incident atom has a first step avoiding the
            # active edge.  Four distinct incident atoms can be matched to
            # the four supported neighbours.
            allowed_steps = {}
            for i in incident:
                atom = atoms[i]
                steps = set()
                for row in atom["rows"]:
                    if row[0] == owner:
                        steps.add(row[1])
                    elif row[-1] == owner:
                        steps.add(row[-2])
                    else:
                        raise AssertionError("incident atom row lost its endpoint")
                allowed_steps[i] = steps - {active}
                if not allowed_steps[i]:
                    model.add(selected[i] + active_var <= 1)

            for y in support_neighbours:
                bucket = []
                for i in incident:
                    if y not in allowed_steps[i]:
                        continue
                    var = model.new_bool_var(
                        f"classifier_step_{owner}_{active}_{i}_{y}"
                    )
                    model.add(var <= active_var)
                    model.add(var <= selected[i])
                    step_matches[active, i, y] = var
                    bucket.append(var)
                model.add(sum(bucket) == active_var)
            for i in incident:
                model.add(
                    sum(
                        var
                        for (x, j, _), var in step_matches.items()
                        if x == active and j == i
                    )
                    <= active_var
                )

            # Four distinct nonincident atoms cover the four active/support
            # pairs with owner-avoiding rows.
            nonincident = [i for i in range(len(atoms)) if i not in incident]
            for y in support_neighbours:
                bucket = []
                for i in nonincident:
                    if not any(
                        owner not in row and active in row and y in row
                        for row in atoms[i]["rows"]
                    ):
                        continue
                    var = model.new_bool_var(
                        f"classifier_cov_{owner}_{active}_{i}_{y}"
                    )
                    model.add(var <= active_var)
                    model.add(var <= selected[i])
                    coverage_matches[active, i, y] = var
                    bucket.append(var)
                model.add(sum(bucket) == active_var)
            for i in nonincident:
                model.add(
                    sum(
                        var
                        for (x, j, _), var in coverage_matches.items()
                        if x == active and j == i
                    )
                    <= active_var
                )

        classifier_data[owner] = {
            "active": active_vars,
            "step": step_matches,
            "coverage": coverage_matches,
        }

    row_selected = None
    active_choice = None
    if require_two_owner_profile:
        row_selected = []
        for i, atom in enumerate(atoms):
            row_vars = [model.new_bool_var(f"row_{i}_{j}") for j in range(len(atom["rows"]))]
            model.add(sum(row_vars) == selected[i])
            row_selected.append(row_vars)

        def row_terms(predicate):
            return [
                row_selected[i][j]
                for i, atom in enumerate(atoms)
                for j, row in enumerate(atom["rows"])
                if predicate(tuple(row))
            ]

        active_choice = {}
        for owner in [V, M]:
            neighbours = sorted(graph[owner])
            if len(neighbours) != 5:
                return None, "OWNER_BLUE_DEGREE_NOT_FIVE", None
            choices = []
            if owner_row_count is not None:
                model.add(
                    sum(row_terms(lambda row, o=owner: o in row))
                    == owner_row_count
                )
            for neighbour in neighbours:
                active = model.new_bool_var(f"active_{owner}_{neighbour}")
                active_choice[owner, neighbour] = active
                choices.append(active)
                incident = norm(owner, neighbour)
                edge_uses = row_terms(
                    lambda row, e=incident: e
                    in {norm(row[k], row[k + 1]) for k in range(4)}
                )
                model.add(sum(edge_uses) == 0).only_enforce_if(active)
                model.add(sum(edge_uses) >= 1).only_enforce_if(active.Not())
                model.add(sum(row_terms(lambda row, x=neighbour: x in row)) >= active)
                for support_neighbour in neighbours:
                    if support_neighbour == neighbour:
                        continue
                    pair_rows = row_terms(
                        lambda row, x=neighbour, y=support_neighbour: x in row and y in row
                    )
                    model.add(sum(pair_rows) >= active)
            model.add(sum(choices) == 1)

    transition_rows = None
    transition_active_choice = None
    if require_live_transition_profile:
        transition_rows = {"source": [], "target": []}
        for i, atom in enumerate(atoms):
            source_vars = [
                model.new_bool_var(f"source_row_{i}_{j}")
                for j in range(len(atom["rows"]))
            ]
            target_vars = [
                model.new_bool_var(f"target_row_{i}_{j}")
                for j in range(len(atom["rows"]))
            ]
            model.add(sum(source_vars) == selected[i])
            model.add(sum(target_vars) == selected[i])
            if i != live_atom:
                for source_var, target_var in zip(source_vars, target_vars):
                    model.add(source_var == target_var)
            transition_rows["source"].append(source_vars)
            transition_rows["target"].append(target_vars)

        source_live = atoms[live_atom]["rows"].index(expected_m)
        target_live = atoms[live_atom]["rows"].index(expected_v)
        model.add(transition_rows["source"][live_atom][source_live] == 1)
        model.add(transition_rows["target"][live_atom][target_live] == 1)

        def transition_terms(state: str, predicate):
            return [
                transition_rows[state][i][j]
                for i, atom in enumerate(atoms)
                for j, row in enumerate(atom["rows"])
                if predicate(tuple(row))
            ]

        support_cache = {}

        def selected_support(state: str, edge_key: tuple[int, int]):
            key = (state, norm(*edge_key))
            if key in support_cache:
                return support_cache[key]
            uses = transition_terms(
                state,
                lambda row, e=key[1]: e
                in {norm(row[k], row[k + 1]) for k in range(4)},
            )
            present = model.new_bool_var(
                f"{state}_support_{key[1][0]}_{key[1][1]}"
            )
            model.add(sum(uses) >= present)
            model.add(sum(uses) <= selected_atom_count * present)
            support_cache[key] = present
            return present

        x_node = left_n + X
        y_node = left_n + Y

        # Source state: v has the live active edge vx, while every other
        # incident blue edge (in particular vy) is selected support.
        for neighbour in sorted(graph[V]):
            present = selected_support("source", (V, neighbour))
            model.add(present == (0 if neighbour == x_node else 1))
        for support_neighbour in sorted(graph[V]):
            if support_neighbour == x_node:
                continue
            model.add(
                sum(
                    transition_terms(
                        "source",
                        lambda row, s=support_neighbour: x_node in row and s in row,
                    )
                )
                >= 1
            )

        # Target state: replacing the live row activates exactly one of mx,my.
        # All other m-star edges stay selected; the active/support pairs are
        # covered in the target tuple.
        active_x = model.new_bool_var("target_m_active_x")
        active_y = model.new_bool_var("target_m_active_y")
        model.add(active_x + active_y == 1)
        transition_active_choice = {x_node: active_x, y_node: active_y}
        for neighbour in sorted(graph[M]):
            present = selected_support("target", (M, neighbour))
            if neighbour == x_node:
                model.add(present + active_x == 1)
            elif neighbour == y_node:
                model.add(present + active_y == 1)
            else:
                model.add(present == 1)
        for active_neighbour, active in transition_active_choice.items():
            for support_neighbour in sorted(graph[M]):
                if support_neighbour == active_neighbour:
                    continue
                pair_rows = transition_terms(
                    "target",
                    lambda row, x=active_neighbour, y=support_neighbour:
                        x in row and y in row,
                )
                model.add(sum(pair_rows) >= 1).only_enforce_if(active)

        # The disappearing middle is fully supported in the source, and the
        # entering owner is fully supported in the target.
        for neighbour in sorted(graph[M]):
            model.add(selected_support("source", (M, neighbour)) == 1)
        for neighbour in sorted(graph[V]):
            model.add(selected_support("target", (V, neighbour)) == 1)

    worst_deficit = None
    if minimize_core_deficit:
        worst_deficit = model.new_int_var(0, 25, "worst_core_switch_deficit")
        model.minimize(worst_deficit)

    separation_rounds = 0
    active_scope_rejections = 0
    while True:
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        solver.parameters.num_search_workers = min(workers, 8)
        solver.parameters.random_seed = 1
        status = solver.solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            if status == cp_model.INFEASIBLE and active_scope_rejections:
                return (
                    None,
                    f"INFEASIBLE_AFTER_{active_scope_rejections}_SCOPE_REJECTIONS",
                    None,
                )
            return None, solver.status_name(status), None

        chosen = [i for i, var in enumerate(selected) if solver.value(var)]
        active_scope_profiles = {}
        if require_active_scope:
            for owner, data in classifier_data.items():
                active = next(
                    x for x, var in data["active"].items() if solver.value(var)
                )
                witness, scope_status = active_scope_profile_for_fixed_selection(
                    graph,
                    atoms,
                    chosen,
                    owner,
                    active,
                    workers,
                    time_limit,
                )
                if witness is None:
                    if scope_status != "INFEASIBLE":
                        return None, "ACTIVE_SCOPE_" + scope_status, None
                    model.add(
                        sum(selected[i] for i in chosen) + data["active"][active]
                        <= len(chosen)
                    )
                    active_scope_rejections += 1
                    break
                active_scope_profiles[str(owner)] = witness
            else:
                pass
            if len(active_scope_profiles) != len(classifier_data):
                continue
        if not minimize_core_deficit:
            meta = {"separationRounds": 0}
            if require_two_owner_profile:
                meta["activeNeighbours"] = {
                    str(owner): next(
                        neighbour
                        for neighbour in sorted(graph[owner])
                        if solver.value(active_choice[owner, neighbour])
                    )
                    for owner in [V, M]
                }
                meta["selectedRows"] = [
                    list(atoms[i]["rows"][next(
                        j for j, var in enumerate(row_selected[i]) if solver.value(var)
                    )])
                    for i in chosen
                ]
            if require_live_transition_profile:
                meta["sourceActiveOwner"] = V
                meta["sourceActiveNeighbour"] = left_n + X
                meta["targetActiveOwner"] = M
                meta["targetActiveNeighbour"] = next(
                    neighbour
                    for neighbour, active in transition_active_choice.items()
                    if solver.value(active)
                )
                for state in ["source", "target"]:
                    meta[f"selectedRows{state.title()}"] = [
                        list(atoms[i]["rows"][next(
                            j
                            for j, var in enumerate(transition_rows[state][i])
                            if solver.value(var)
                        )])
                        for i in chosen
                    ]
            if classifier_data:
                meta["localClassifiers"] = {}
                for owner, data in classifier_data.items():
                    active = next(x for x, var in data["active"].items() if solver.value(var))
                    meta["localClassifiers"][str(owner)] = {
                        "activeNeighbour": active,
                        "stepMatching": [
                            [i, y]
                            for (x, i, y), var in data["step"].items()
                            if x == active and solver.value(var)
                        ],
                        "coverageMatching": [
                            [i, y]
                            for (x, i, y), var in data["coverage"].items()
                            if x == active and solver.value(var)
                        ],
                    }
            if active_scope_profiles:
                meta["activeScopeProfiles"] = active_scope_profiles
            return chosen, solver.status_name(status), meta

        chosen_bad = [(atoms[i]["u"], atoms[i]["v"]) for i in chosen]
        separation, separation_status = minimum_switch_sigma(
            graph.number_of_nodes(),
            support_edges,
            chosen_bad,
            workers,
            time_limit,
        )
        if separation is None:
            return None, "CUT_" + separation_status, None
        sigma, switch = separation
        actual_deficit = max(0, -sigma)
        relaxed_deficit = solver.value(worst_deficit)
        if actual_deficit <= relaxed_deficit:
            meta = {
                "separationRounds": separation_rounds,
                "minimumCoreSigma": sigma,
                "worstCoreDeficit": actual_deficit,
                "worstCoreSwitch": sorted(switch),
            }
            if require_two_owner_profile:
                meta["activeNeighbours"] = {
                    str(owner): next(
                        neighbour
                        for neighbour in sorted(graph[owner])
                        if solver.value(active_choice[owner, neighbour])
                    )
                    for owner in [V, M]
                }
                meta["selectedRows"] = [
                    list(atoms[i]["rows"][next(
                        j for j, var in enumerate(row_selected[i]) if solver.value(var)
                    )])
                    for i in chosen
                ]
            if require_live_transition_profile:
                meta["sourceActiveOwner"] = V
                meta["sourceActiveNeighbour"] = left_n + X
                meta["targetActiveOwner"] = M
                meta["targetActiveNeighbour"] = next(
                    neighbour
                    for neighbour, active in transition_active_choice.items()
                    if solver.value(active)
                )
                for state in ["source", "target"]:
                    meta[f"selectedRows{state.title()}"] = [
                        list(atoms[i]["rows"][next(
                            j
                            for j, var in enumerate(transition_rows[state][i])
                            if solver.value(var)
                        )])
                        for i in chosen
                    ]
            if classifier_data:
                meta["localClassifiers"] = {}
                for owner, data in classifier_data.items():
                    active = next(x for x, var in data["active"].items() if solver.value(var))
                    meta["localClassifiers"][str(owner)] = {
                        "activeNeighbour": active,
                        "stepMatching": [
                            [i, y]
                            for (x, i, y), var in data["step"].items()
                            if x == active and solver.value(var)
                        ],
                        "coverageMatching": [
                            [i, y]
                            for (x, i, y), var in data["coverage"].items()
                            if x == active and solver.value(var)
                        ],
                    }
            if active_scope_profiles:
                meta["activeScopeProfiles"] = active_scope_profiles
            if max_core_deficit is not None and actual_deficit > max_core_deficit:
                return None, f"MIN_DEFICIT_{actual_deficit}", meta
            return chosen, solver.status_name(status), {
                **meta,
            }

        bad_cross_terms = [
            selected[i]
            for i, atom in enumerate(atoms)
            if (atom["u"] in switch) ^ (atom["v"] in switch)
        ]
        fixed_blue_cross = sum(
            (u in switch) ^ (v in switch) for u, v in support_edges
        )
        model.add(sum(bad_cross_terms) - fixed_blue_cross <= worst_deficit)
        separation_rounds += 1


def verify_hit(
    graph: nx.Graph,
    atoms: list[dict],
    chosen: list[int],
    support_min_multiplicity: int,
    require_deletion_sdr: bool,
    require_bad_triangle_free: bool,
    selected_atom_count: int,
) -> None:
    if len(chosen) != selected_atom_count:
        raise AssertionError("atom count")
    support_edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    support_nodes = [("e", i) for i in range(24)]

    full_graph = graph.copy()
    for i in chosen:
        full_graph.add_edge(atoms[i]["u"], atoms[i]["v"])
    if require_bad_triangle_free and any(nx.triangles(full_graph).values()):
        raise AssertionError("full graph is not triangle-free")

    for edge in support_edges:
        multiplicity = sum(edge in map(tuple, atoms[i]["footprintEdges"]) for i in chosen)
        if multiplicity < support_min_multiplicity:
            raise AssertionError("support multiplicity")

    if not require_deletion_sdr:
        return

    for ex in chosen:
        incidence = nx.Graph()
        left_nodes = [("a", i) for i in chosen if i != ex]
        incidence.add_nodes_from(left_nodes, bipartite=0)
        incidence.add_nodes_from(support_nodes, bipartite=1)
        for i in chosen:
            if i == ex:
                continue
            footprint = {
                support_edges.index(tuple(edge)) for edge in atoms[i]["footprintEdges"]
            }
            incidence.add_edges_from((("a", i), ("e", e)) for e in footprint)
        matching = nx.algorithms.bipartite.maximum_matching(incidence, top_nodes=left_nodes)
        if sum(1 for node in left_nodes if node in matching) != 24:
            raise AssertionError(f"deletion SDR failed at atom {ex}")


def canonical_sha(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", type=int, required=True)
    parser.add_argument("--right", type=int, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--max-supports", type=int, default=50)
    parser.add_argument("--support-time", type=float, default=20.0)
    parser.add_argument("--circuit-time", type=float, default=20.0)
    parser.add_argument("--minimize-core-deficit", action="store_true")
    parser.add_argument("--max-core-deficit", type=int)
    parser.add_argument("--require-two-owner-profile", action="store_true")
    parser.add_argument("--require-live-transition-profile", action="store_true")
    parser.add_argument("--require-shared-bad-neighbour", action="store_true")
    parser.add_argument("--owner-row-count", type=int)
    parser.add_argument("--support-min-multiplicity", type=int, default=2)
    parser.add_argument("--skip-deletion-sdr", action="store_true")
    parser.add_argument("--skip-bad-triangle-free", action="store_true")
    parser.add_argument("--selected-atom-count", type=int, default=25)
    parser.add_argument("--owner-bad-degree", type=int, default=5)
    parser.add_argument(
        "--local-classifier",
        choices=["none", "v", "m", "both"],
        default="none",
    )
    parser.add_argument("--require-active-scope", action="store_true")
    parser.add_argument("--classifier-active-min-degree", type=int, default=0)
    parser.add_argument("--classifier-active-right-index", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        raise SystemExit("--workers must lie in 1..8")
    if args.left + args.right > 24:
        raise SystemExit("a cyclic 24-edge connected support has at most 24 vertices")

    if args.require_two_owner_profile and args.require_live_transition_profile:
        raise SystemExit("choose at most one profile mode")
    if args.local_classifier != "none" and (
        args.require_two_owner_profile or args.require_live_transition_profile
    ):
        raise SystemExit("local classifier and row-profile modes are alternatives")
    if args.require_active_scope and args.local_classifier == "none":
        raise SystemExit("--require-active-scope requires --local-classifier")
    if args.classifier_active_min_degree < 0:
        raise SystemExit("--classifier-active-min-degree must be nonnegative")
    if args.classifier_active_right_index is not None and not (
        0 <= args.classifier_active_right_index < args.right
    ):
        raise SystemExit("--classifier-active-right-index is outside the right shore")
    if args.owner_row_count is not None and not args.require_two_owner_profile:
        raise SystemExit("--owner-row-count requires --require-two-owner-profile")
    if not 0 <= args.support_min_multiplicity <= 2:
        raise SystemExit("--support-min-multiplicity must lie in 0..2")
    if args.selected_atom_count < 1 or args.owner_bad_degree < 0:
        raise SystemExit("atom count and owner bad degree must be nonnegative")
    if not args.skip_deletion_sdr and args.selected_atom_count != 25:
        raise SystemExit("deletion-SDR mode requires --selected-atom-count 25")
    model, edge = build_rooted_support_model(
        args.left,
        args.right,
        args.require_shared_bad_neighbour,
        args.require_live_transition_profile,
    )
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.support_time
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = 1

    result = {
        "schema": "rooted-t5-support-circuit-search-v1",
        "left": args.left,
        "right": args.right,
        "workers": args.workers,
        "supportLimit": args.max_supports,
        "requireTwoOwnerProfile": args.require_two_owner_profile,
        "requireLiveTransitionProfile": args.require_live_transition_profile,
        "requireSharedBadNeighbour": args.require_shared_bad_neighbour,
        "ownerRowCount": args.owner_row_count,
        "supportMinMultiplicity": args.support_min_multiplicity,
        "requireDeletionSdr": not args.skip_deletion_sdr,
        "requireBadTriangleFree": not args.skip_bad_triangle_free,
        "selectedAtomCount": args.selected_atom_count,
        "ownerBadDegree": args.owner_bad_degree,
        "localClassifier": args.local_classifier,
        "requireActiveScope": args.require_active_scope,
        "classifierActiveMinDegree": args.classifier_active_min_degree,
        "classifierActiveRightIndex": args.classifier_active_right_index,
        "supportsSolved": 0,
        "supportsWithAtLeast25Atoms": 0,
        "circuitStatuses": {},
        "hit": None,
        "scope": "falsifier search; a no-hit is not a proof",
    }

    for _ in range(args.max_supports):
        status = solver.solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            result["supportTerminalStatus"] = solver.status_name(status)
            break
        result["supportsSolved"] += 1
        graph = graph_from_solution(solver, edge, args.left, args.right)
        atoms = distance_four_atoms(graph, args.left, args.right)
        if len(atoms) >= 25:
            result["supportsWithAtLeast25Atoms"] += 1
            chosen, circuit_status, selection_meta = choose_minimal_circuit(
                graph,
                atoms,
                args.left,
                args.right,
                args.workers,
                args.circuit_time,
                args.minimize_core_deficit,
                args.max_core_deficit,
                args.require_two_owner_profile,
                args.require_live_transition_profile,
                args.require_shared_bad_neighbour,
                args.owner_row_count,
                args.support_min_multiplicity,
                not args.skip_deletion_sdr,
                not args.skip_bad_triangle_free,
                args.selected_atom_count,
                args.owner_bad_degree,
                {
                    "none": (),
                    "v": (V,),
                    "m": (M,),
                    "both": (V, M),
                }[args.local_classifier],
                args.require_active_scope,
                args.classifier_active_min_degree,
                None
                if args.classifier_active_right_index is None
                else frozenset({args.left + args.classifier_active_right_index}),
            )
            result["circuitStatuses"][circuit_status] = (
                result["circuitStatuses"].get(circuit_status, 0) + 1
            )
            if chosen is not None:
                verify_hit(
                    graph,
                    atoms,
                    chosen,
                    args.support_min_multiplicity,
                    not args.skip_deletion_sdr,
                    not args.skip_bad_triangle_free,
                    args.selected_atom_count,
                )
                result["hit"] = {
                    "supportEdges": [list(edge) for edge in sorted(graph.edges())],
                    "graph6": nx.to_graph6_bytes(graph, header=False).decode("ascii").strip(),
                    "atomCountAvailable": len(atoms),
                    "selectionMeta": selection_meta,
                    "selectedAtoms": [
                        {
                            "shore": atoms[i]["shore"],
                            "u": atoms[i]["u"],
                            "v": atoms[i]["v"],
                            "rows": [list(row) for row in atoms[i]["rows"]],
                            "footprintEdges": [list(e) for e in atoms[i]["footprintEdges"]],
                        }
                        for i in chosen
                    ],
                }
                result["verdict"] = "HIT_PATH_REALIZABLE_T5_MINIMAL_CIRCUIT"
                break

        # Exclude this exact rooted labeled support and continue.
        differences = []
        for var in edge.values():
            differences.append(1 - var if solver.value(var) else var)
        model.add(sum(differences) >= 1)
    else:
        result["supportTerminalStatus"] = "LIMIT_REACHED"

    if result["hit"] is None:
        result["verdict"] = "NO_HIT_WITHIN_EXPLICIT_LIMIT"
    result["canonicalSha256"] = canonical_sha(result)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
