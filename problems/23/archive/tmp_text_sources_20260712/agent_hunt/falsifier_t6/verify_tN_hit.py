#!/usr/bin/env python3
"""Independent exact replay of a rooted t=N classifier hit (port of
verify_t5_local_classifier_hit.py, parametric in t).

Recomputes from the graph6 string alone: complete row DB, circuit axioms
(triangle-freeness, multiplicity >= 2, all deletion-SDRs), the four-number
classifier vector for the recorded owner/active pair, a constructive row
selection realizing the profile, the intrinsic active component and captured
bad atoms, and the exact minimum displayed-cut sigma (CP-SAT OPTIMAL +
Gray-code brute force when the order allows).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import networkx as nx
from ortools.sat.python import cp_model


def norm(u, v):
    return (u, v) if u < v else (v, u)


def canonical_sha(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def all_atoms(graph, left_n, right_n):
    atoms = []
    shores = [
        ("L", list(range(left_n))),
        ("R", list(range(left_n, left_n + right_n))),
    ]
    for shore, vertices in shores:
        for i, u in enumerate(vertices):
            for v in vertices[i + 1 :]:
                if nx.shortest_path_length(graph, u, v) != 4:
                    continue
                rows = sorted(tuple(path) for path in nx.all_shortest_paths(graph, u, v))
                footprint = sorted(
                    {norm(path[k], path[k + 1]) for path in rows for k in range(4)}
                )
                atoms.append(
                    {"shore": shore, "u": u, "v": v, "rows": rows, "footprint": footprint}
                )
    return atoms


def matching_size(left, right, incidence):
    graph = nx.Graph()
    left_nodes = [("l", x) for x in left]
    right_nodes = [("r", x) for x in right]
    graph.add_nodes_from(left_nodes, bipartite=0)
    graph.add_nodes_from(right_nodes, bipartite=1)
    graph.add_edges_from((("l", x), ("r", y)) for x, y in incidence)
    matching = nx.algorithms.bipartite.maximum_matching(graph, top_nodes=left_nodes)
    return sum(node in matching for node in left_nodes)


def first_step(row, owner):
    if row[0] == owner:
        return row[1]
    if row[-1] == owner:
        return row[-2]
    raise AssertionError("owner is not an endpoint")


def local_vector(atoms, chosen, graph, owner, active, t):
    neighbours = sorted(graph[owner])
    support = [y for y in neighbours if y != active]
    incident = [i for i in chosen if owner in {atoms[i]["u"], atoms[i]["v"]}]
    nonincident = [i for i in chosen if i not in incident]
    forced = [i for i in chosen if all(owner in row for row in atoms[i]["rows"])]
    e_forced = len(set(forced) - set(incident))

    step_incidence = []
    empty_steps = 0
    for i in incident:
        steps = {first_step(row, owner) for row in atoms[i]["rows"]} & set(support)
        if not steps:
            empty_steps += 1
        step_incidence.extend((y, i) for y in steps)
    step_rank = matching_size(support, incident, step_incidence)

    coverage_incidence = []
    for y in support:
        for i in nonincident:
            if any(
                owner not in row and active in row and y in row
                for row in atoms[i]["rows"]
            ):
                coverage_incidence.append((y, i))
    coverage_rank = matching_size(support, nonincident, coverage_incidence)
    return {
        "eForced": e_forced,
        "iStep": empty_steps,
        "dStep": (t - 1) - step_rank,
        "dCoverage": (t - 1) - coverage_rank,
        "incident": incident,
    }


def construct_rows(atoms, chosen, graph, owner, active, classifier, t):
    incident = {i for i in chosen if owner in {atoms[i]["u"], atoms[i]["v"]}}
    step_match = {i: y for i, y in classifier["stepMatching"]}
    coverage_match = {i: y for i, y in classifier["coverageMatching"]}
    rows = {}
    for i in chosen:
        if i in incident:
            if i in step_match:
                y = step_match[i]
                candidates = [
                    row for row in atoms[i]["rows"] if first_step(row, owner) == y
                ]
            else:
                candidates = [
                    row for row in atoms[i]["rows"] if first_step(row, owner) != active
                ]
        elif i in coverage_match:
            y = coverage_match[i]
            candidates = [
                row
                for row in atoms[i]["rows"]
                if owner not in row and active in row and y in row
            ]
        else:
            candidates = [row for row in atoms[i]["rows"] if owner not in row]
        if not candidates:
            raise AssertionError(f"no constructive row for atom {i}")
        rows[i] = min(candidates)

    support_edges = {
        norm(row[k], row[k + 1]) for row in rows.values() for k in range(4)
    }
    neighbours = sorted(graph[owner])
    assert norm(owner, active) not in support_edges
    assert all(norm(owner, y) in support_edges for y in neighbours if y != active)
    assert sum(owner in row for row in rows.values()) == t
    assert any(active in row for row in rows.values())
    assert all(
        any(active in row and y in row for row in rows.values())
        for y in neighbours
        if y != active
    )
    return rows, support_edges


def deletion_sdrs(atoms, chosen, support_edges):
    sizes = []
    right = [("e", edge) for edge in support_edges]
    for excluded in chosen:
        left = [("a", i) for i in chosen if i != excluded]
        graph = nx.Graph()
        graph.add_nodes_from(left, bipartite=0)
        graph.add_nodes_from(right, bipartite=1)
        for i in chosen:
            if i == excluded:
                continue
            graph.add_edges_from(
                (("a", i), ("e", edge)) for edge in atoms[i]["footprint"]
            )
        matching = nx.algorithms.bipartite.maximum_matching(graph, top_nodes=left)
        sizes.append(sum(node in matching for node in left))
    return sizes


def min_sigma_bruteforce(vertex_count, blue, bad):
    """Gray-code exact minimum of sigma(S) over all switches."""
    if vertex_count > 24:
        return None, None
    adj_delta = [[] for _ in range(vertex_count)]
    for u, v in blue:
        adj_delta[u].append((v, 1))
        adj_delta[v].append((u, 1))
    for u, v in bad:
        adj_delta[u].append((v, -1))
        adj_delta[v].append((u, -1))
    inside = [False] * vertex_count
    sigma = 0
    best = 0
    best_set = []
    total = 1 << (vertex_count - 1)
    for g in range(1, total):
        flip = (g & -g).bit_length()  # vertex index 1..n-1 (vertex 0 fixed out)
        delta = 0
        for w, weight in adj_delta[flip]:
            delta += weight * (1 if not (inside[w] ^ inside[flip]) else -1)
        # after flipping `flip`, each incident edge toggles cross status
        inside[flip] = not inside[flip]
        sigma += delta
        if sigma < best:
            best = sigma
            best_set = [v for v in range(vertex_count) if inside[v]]
    return best, best_set


def min_sigma_cpsat(vertex_count, blue, bad, workers=8, time_limit=120.0):
    model = cp_model.CpModel()
    side = [model.new_bool_var(f"s_{v}") for v in range(vertex_count)]
    model.add(side[0] == 0)

    def xor(a, b, name):
        out = model.new_bool_var(name)
        model.add(out >= a - b)
        model.add(out >= b - a)
        model.add(out <= a + b)
        model.add(out <= 2 - a - b)
        return out

    blue_cross = [xor(side[u], side[v], f"b{i}") for i, (u, v) in enumerate(blue)]
    bad_cross = [xor(side[u], side[v], f"m{i}") for i, (u, v) in enumerate(bad)]
    model.minimize(sum(blue_cross) - sum(bad_cross))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = 1
    status = solver.solve(model)
    if status != cp_model.OPTIMAL:
        return None, solver.status_name(status)
    switch = [v for v in range(vertex_count) if solver.value(side[v])]
    sigma = sum((u in switch) != (v in switch) for u, v in blue) - sum(
        (u in switch) != (v in switch) for u, v in bad
    )
    return (sigma, switch), "OPTIMAL"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--hit-index", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    claimed_sha = source.pop("canonicalSha256")
    assert canonical_sha(source) == claimed_sha
    t = source["t"]

    left_n, right_n = source["left"], source["right"]
    hit = source["hits"][args.hit_index]
    graph = nx.from_graph6_bytes(hit["graph6"].encode("ascii"))
    support_edges = sorted(norm(*edge) for edge in graph.edges())
    assert support_edges == sorted(norm(*edge) for edge in hit["supportEdges"])
    assert nx.is_connected(graph) and nx.is_bipartite(graph)
    assert len(support_edges) == t * t - 1
    assert len(graph) == left_n + right_n

    atoms = all_atoms(graph, left_n, right_n)
    atom_index = {(a["shore"], a["u"], a["v"]): i for i, a in enumerate(atoms)}
    chosen = []
    for record in hit["selectedAtoms"]:
        key = (record["shore"], record["u"], record["v"])
        i = atom_index[key]
        assert set(map(tuple, record["rows"])) == set(atoms[i]["rows"])
        assert set(map(tuple, (tuple(e) for e in record["footprintEdges"]))) == set(
            atoms[i]["footprint"]
        )
        chosen.append(i)
    assert len(chosen) == len(set(chosen)) == t * t

    bad_edges = sorted(norm(atoms[i]["u"], atoms[i]["v"]) for i in chosen)
    full = graph.copy()
    full.add_edges_from(bad_edges)
    assert all(value == 0 for value in nx.triangles(full).values())
    sdr_sizes = deletion_sdrs(atoms, chosen, support_edges)
    assert sdr_sizes == [t * t - 1] * (t * t)
    multiplicities = {
        edge: sum(edge in atoms[i]["footprint"] for i in chosen)
        for edge in support_edges
    }
    assert min(multiplicities.values()) >= 2

    owner_key = sorted(hit["selectionMeta"]["localClassifiers"])[0]
    classifier = hit["selectionMeta"]["localClassifiers"][owner_key]
    owner = int(owner_key)
    assert graph.degree[owner] == t
    owner_bad_degree = sum(owner in edge for edge in bad_edges)
    assert owner_bad_degree == t
    active = classifier["activeNeighbour"]
    vector = local_vector(atoms, chosen, graph, owner, active, t)
    assert [vector[k] for k in ["eForced", "iStep", "dStep", "dCoverage"]] == [0, 0, 0, 0]
    rows, selected_support = construct_rows(
        atoms, chosen, graph, owner, active, classifier, t
    )

    active_graph = nx.Graph()
    active_graph.add_nodes_from(graph.nodes())
    active_graph.add_edges_from(set(support_edges) - selected_support)
    component = nx.node_connected_component(active_graph, owner)
    active_bad_atoms = [
        i for i in chosen if atoms[i]["u"] in component and atoms[i]["v"] in component
    ]

    # Preferred scope witness: replay the engine's recorded scope selection.
    scope_replay = None
    scope_meta = hit["selectionMeta"].get("activeScopeProfiles", {}).get(owner_key)
    if scope_meta is not None:
        witness_rows = {int(k): tuple(v) for k, v in scope_meta["selectedRows"].items()}
        assert set(witness_rows) == set(chosen)
        for i, row in witness_rows.items():
            assert row in set(atoms[i]["rows"]), f"foreign row for atom {i}"
        w_support = {
            norm(row[k], row[k + 1]) for row in witness_rows.values() for k in range(4)
        }
        neighbours = sorted(graph[owner])
        assert norm(owner, scope_meta["activeNeighbour"]) not in w_support
        assert all(
            norm(owner, y) in w_support
            for y in neighbours
            if y != scope_meta["activeNeighbour"]
        )
        assert sum(owner in row for row in witness_rows.values()) == t
        assert any(scope_meta["activeNeighbour"] in row for row in witness_rows.values())
        assert all(
            any(
                scope_meta["activeNeighbour"] in row and y in row
                for row in witness_rows.values()
            )
            for y in neighbours
            if y != scope_meta["activeNeighbour"]
        )
        w_active = nx.Graph()
        w_active.add_nodes_from(graph.nodes())
        w_active.add_edges_from(set(support_edges) - w_support)
        w_component = nx.node_connected_component(w_active, owner)
        scope_atom = scope_meta["scopeAtom"]
        assert atoms[scope_atom]["u"] in w_component
        assert atoms[scope_atom]["v"] in w_component
        assert scope_atom in chosen
        scope_replay = {
            "scopeAtom": scope_atom,
            "scopeBadEdge": [atoms[scope_atom]["u"], atoms[scope_atom]["v"]],
            "activeComponent": sorted(w_component),
            "latentEdgeCount": len(set(support_edges) - w_support),
            "selectedSupportCount": len(w_support),
            "capturedBadAtoms": [
                i
                for i in chosen
                if atoms[i]["u"] in w_component and atoms[i]["v"] in w_component
            ],
        }

    brute, brute_switch = min_sigma_bruteforce(len(graph), support_edges, bad_edges)
    cpsat, cpsat_status = min_sigma_cpsat(len(graph), support_edges, bad_edges)
    if brute is not None and cpsat is not None:
        assert brute == cpsat[0], (brute, cpsat[0])

    result = {
        "schema": "tN-local-classifier-hit-verification-v1",
        "t": t,
        "sourceCanonicalSha256": claimed_sha,
        "hitIndex": args.hit_index,
        "supportVertices": len(graph),
        "supportEdges": len(support_edges),
        "selectedAtoms": len(chosen),
        "triangleCount": sum(nx.triangles(full).values()) // 3,
        "minimumMultiplicity": min(multiplicities.values()),
        "deletionSdrAllPass": sdr_sizes == [t * t - 1] * (t * t),
        "owner": owner,
        "ownerBlueDegree": graph.degree[owner],
        "ownerBadDegree": owner_bad_degree,
        "activeNeighbour": active,
        "classifierVector": [
            vector["eForced"],
            vector["iStep"],
            vector["dStep"],
            vector["dCoverage"],
        ],
        "constructiveRowCountOwner": sum(owner in row for row in rows.values()),
        "constructiveActiveComponent": sorted(component),
        "constructiveActiveBadAtoms": active_bad_atoms,
        "scopeReplay": scope_replay,
        "minimumDisplayedCutSigmaCpSat": None if cpsat is None else cpsat[0],
        "cpSatStatus": cpsat_status,
        "minimumDisplayedCutSwitch": None if cpsat is None else cpsat[1],
        "minimumDisplayedCutSigmaBrute": brute,
        "verdict": "PASS_T6_ZERO_VECTOR_PROFILE_REPLAY",
    }
    result["canonicalSha256"] = canonical_sha(result)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
