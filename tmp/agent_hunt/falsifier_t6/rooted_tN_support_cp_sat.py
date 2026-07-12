#!/usr/bin/env python3
"""Rooted t=N live-rotor support/circuit falsifier engine (port of Codex's
rooted_t5_support_cp_sat.py, parametrised in the equality scale t).

This is a falsifier engine, not a proof by bounded search.  It fixes the live
middle-swap core in a connected (t^2-1)-edge bipartite support graph and asks
for a triangle-free t^2-atom family whose complete distance-four footprints
form an inclusion-minimal defect-one transversal circuit, carrying a
zero-vector local owner profile (four-number classifier) with positive
active scope.

Rooted labels:
  left:  v=0, m=1, a=2, b=3
  right: x=0, y=1
mandatory blue paths: (a,x,v,y,b) and (a,x,m,y,b).

t=6 arithmetic: 35 support edges, 36 atoms, owner blue degree 6 = owner bad
degree 6, step rank 5, coverage rank 5, owner row count 6.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import networkx as nx
from ortools.sat.python import cp_model


V, M, A, B = 0, 1, 2, 3
X, Y = 0, 1


def norm(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def and2(model: cp_model.CpModel, left, right, name: str):
    out = model.new_bool_var(name)
    model.add(out <= left)
    model.add(out <= right)
    model.add(out >= left + right - 1)
    return out


def build_rooted_support_model(left_n: int, right_n: int, t: int):
    edge_total = t * t - 1
    if left_n < t + 2 or right_n < t:
        raise ValueError("two-owner roots require left >= t+2 and right >= t")

    model = cp_model.CpModel()
    edge = {
        (u, r): model.new_bool_var(f"e_{u}_{r}")
        for u in range(left_n)
        for r in range(right_n)
    }
    model.add(sum(edge.values()) == edge_total)

    # The two complete shortest rows differing only at the middle.
    for key in [(A, X), (V, X), (M, X), (V, Y), (M, Y), (B, Y)]:
        model.add(edge[key] == 1)

    # Both rotating owners are degree-t blue-star owners.
    model.add(sum(edge[V, r] for r in range(right_n)) == t)
    model.add(sum(edge[M, r] for r in range(right_n)) == t)

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

    # Exact distance-four: a two-step in the shore square without a
    # length-two blue path.
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

    # Rooted live atom plus owner bad-degree headroom.
    model.add(ld4(A, B) == 1)
    model.add(sum(ld4(V, u) for u in range(left_n) if u != V) >= t)
    model.add(sum(ld4(M, u) for u in range(left_n) if u != M) >= t)
    model.add(sum(d4_left.values()) + sum(d4_right.values()) >= t * t)

    # Safe label symmetries beyond the four rooted left vertices and x,y.
    left_degrees = [sum(edge[u, r] for r in range(right_n)) for u in range(left_n)]
    right_degrees = [sum(edge[u, r] for u in range(left_n)) for r in range(right_n)]
    for u in range(4, left_n - 1):
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
    t: int,
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
    model.add(sum(row_terms(lambda row: owner in row)) == t)
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
    }, solver.status_name(status)


def choose_minimal_circuit(
    graph: nx.Graph,
    atoms: list[dict],
    left_n: int,
    right_n: int,
    t: int,
    workers: int,
    time_limit: float,
    classifier_owners: tuple[int, ...],
    require_active_scope: bool,
):
    edge_total = t * t - 1
    atom_total = t * t
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
    live_atom = left_atom(A, B)
    live_rows = {tuple(row) for row in atoms[live_atom]["rows"]}
    expected_v = (A, left_n + X, V, left_n + Y, B)
    expected_m = (A, left_n + X, M, left_n + Y, B)
    if expected_v not in live_rows or expected_m not in live_rows:
        return None, "rooted live rows absent after exact shortest-path replay", None

    model = cp_model.CpModel()
    selected = [model.new_bool_var(f"atom_{i}") for i in range(len(atoms))]
    model.add(sum(selected) == atom_total)
    for idx in required:
        model.add(selected[idx] == 1)

    # t bad-star atoms at each owner.
    owner_v = [i for i, atom in enumerate(atoms) if V in {atom["u"], atom["v"]}]
    owner_m = [i for i, atom in enumerate(atoms) if M in {atom["u"], atom["v"]}]
    model.add(sum(selected[i] for i in owner_v) == t)
    model.add(sum(selected[i] for i in owner_m) == t)

    # The selected bad graph is triangle-free on each cut shore.
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

    # Minimal defect-one circuit necessary condition: multiplicity >= 2.
    for e in range(len(support_edges)):
        incident = [i for i, atom in enumerate(atoms) if e in atom["footprint"]]
        model.add(sum(selected[i] for i in incident) >= 2)

    # Exact deletion-SDR certificates.
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
        if len(neighbours) != t:
            return None, "OWNER_BLUE_DEGREE_NOT_T", None
        incident = [
            i for i, atom in enumerate(atoms) if owner in {atom["u"], atom["v"]}
        ]

        # Forced(v)=Inc(v).
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
        step_matches = {}
        coverage_matches = {}

        for active, active_var in active_vars.items():
            support_neighbours = [y for y in neighbours if y != active]

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
            rejected = False
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
                    t,
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
                    rejected = True
                    break
                active_scope_profiles[str(owner)] = witness
            if rejected:
                continue

        meta = {"activeScopeRejections": active_scope_rejections}
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


def verify_hit(
    graph: nx.Graph,
    atoms: list[dict],
    chosen: list[int],
    t: int,
) -> None:
    edge_total = t * t - 1
    if len(chosen) != t * t:
        raise AssertionError("atom count")
    support_edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    if len(support_edges) != edge_total:
        raise AssertionError("support edge count")
    support_nodes = [("e", i) for i in range(edge_total)]

    full_graph = graph.copy()
    for i in chosen:
        full_graph.add_edge(atoms[i]["u"], atoms[i]["v"])
    if any(nx.triangles(full_graph).values()):
        raise AssertionError("full graph is not triangle-free")

    for edge in support_edges:
        multiplicity = sum(edge in map(tuple, atoms[i]["footprintEdges"]) for i in chosen)
        if multiplicity < 2:
            raise AssertionError("support multiplicity")

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
        if sum(1 for node in left_nodes if node in matching) != edge_total:
            raise AssertionError(f"deletion SDR failed at atom {ex}")


def canonical_sha(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--t", type=int, default=6)
    parser.add_argument("--left", type=int, required=True)
    parser.add_argument("--right", type=int, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--max-supports", type=int, default=50)
    parser.add_argument("--support-time", type=float, default=30.0)
    parser.add_argument("--circuit-time", type=float, default=60.0)
    parser.add_argument(
        "--local-classifier", choices=["none", "v", "m", "both"], default="v"
    )
    parser.add_argument("--require-active-scope", action="store_true")
    parser.add_argument("--max-hits", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    t = args.t
    if not 1 <= args.workers <= 8:
        raise SystemExit("--workers must lie in 1..8")
    if args.left + args.right > t * t - 1:
        raise SystemExit("a cyclic connected support has at most t^2-1 vertices")
    if args.require_active_scope and args.local_classifier == "none":
        raise SystemExit("--require-active-scope requires --local-classifier")

    model, edge = build_rooted_support_model(args.left, args.right, t)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.support_time
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = 1

    result = {
        "schema": "rooted-tN-support-circuit-search-v1",
        "t": t,
        "left": args.left,
        "right": args.right,
        "workers": args.workers,
        "supportLimit": args.max_supports,
        "localClassifier": args.local_classifier,
        "requireActiveScope": args.require_active_scope,
        "supportsSolved": 0,
        "supportsWithEnoughAtoms": 0,
        "circuitStatuses": {},
        "hits": [],
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
        if len(atoms) >= t * t:
            result["supportsWithEnoughAtoms"] += 1
            chosen, circuit_status, selection_meta = choose_minimal_circuit(
                graph,
                atoms,
                args.left,
                args.right,
                t,
                args.workers,
                args.circuit_time,
                {
                    "none": (),
                    "v": (V,),
                    "m": (M,),
                    "both": (V, M),
                }[args.local_classifier],
                args.require_active_scope,
            )
            result["circuitStatuses"][circuit_status] = (
                result["circuitStatuses"].get(circuit_status, 0) + 1
            )
            if chosen is not None:
                verify_hit(graph, atoms, chosen, t)
                result["hits"].append(
                    {
                        "supportEdges": [list(edge) for edge in sorted(graph.edges())],
                        "graph6": nx.to_graph6_bytes(graph, header=False)
                        .decode("ascii")
                        .strip(),
                        "atomCountAvailable": len(atoms),
                        "selectionMeta": selection_meta,
                        "selectedAtoms": [
                            {
                                "shore": atoms[i]["shore"],
                                "u": atoms[i]["u"],
                                "v": atoms[i]["v"],
                                "rows": [list(row) for row in atoms[i]["rows"]],
                                "footprintEdges": [
                                    list(e) for e in atoms[i]["footprintEdges"]
                                ],
                            }
                            for i in chosen
                        ],
                    }
                )
                if len(result["hits"]) >= args.max_hits:
                    break

        # Exclude this exact rooted labeled support and continue.
        differences = []
        for var in edge.values():
            differences.append(1 - var if solver.value(var) else var)
        model.add(sum(differences) >= 1)
    else:
        result["supportTerminalStatus"] = "LIMIT_REACHED"

    result["verdict"] = (
        "HIT_TN_MINIMAL_CIRCUIT_CLASSIFIER"
        if result["hits"]
        else "NO_HIT_WITHIN_EXPLICIT_LIMIT"
    )
    result["canonicalSha256"] = canonical_sha(result)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
