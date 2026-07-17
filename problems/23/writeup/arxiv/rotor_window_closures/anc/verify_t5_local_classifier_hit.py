#!/usr/bin/env python3
"""Independent exact replay of the R48 t=5 local-classifier hit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import networkx as nx


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
                    {
                        norm(path[k], path[k + 1])
                        for path in rows
                        for k in range(4)
                    }
                )
                atoms.append(
                    {
                        "shore": shore,
                        "u": u,
                        "v": v,
                        "rows": rows,
                        "footprint": footprint,
                    }
                )
    return atoms


def matching_size(left, right, incidence):
    graph = nx.Graph()
    left_nodes = [("l", x) for x in left]
    right_nodes = [("r", x) for x in right]
    graph.add_nodes_from(left_nodes, bipartite=0)
    graph.add_nodes_from(right_nodes, bipartite=1)
    graph.add_edges_from(
        (("l", x), ("r", y)) for x, y in incidence
    )
    matching = nx.algorithms.bipartite.maximum_matching(graph, top_nodes=left_nodes)
    return sum(node in matching for node in left_nodes)


def first_step(row, owner):
    if row[0] == owner:
        return row[1]
    if row[-1] == owner:
        return row[-2]
    raise AssertionError("owner is not an endpoint")


def local_vector(atoms, chosen, graph, owner, active):
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
        "dStep": 4 - step_rank,
        "dCoverage": 4 - coverage_rank,
        "incident": incident,
        "forced": forced,
        "stepIncidence": [list(edge) for edge in sorted(step_incidence)],
        "coverageIncidence": [list(edge) for edge in sorted(coverage_incidence)],
    }


def construct_rows(atoms, chosen, graph, owner, active, classifier):
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
        norm(row[k], row[k + 1])
        for row in rows.values()
        for k in range(4)
    }
    neighbours = sorted(graph[owner])
    assert norm(owner, active) not in support_edges
    assert all(norm(owner, y) in support_edges for y in neighbours if y != active)
    assert sum(owner in row for row in rows.values()) == 5
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


def minimum_switch_sigma(vertex_count, blue, bad):
    best = None
    best_mask = None
    for mask in range(1 << (vertex_count - 1)):
        inside = lambda v: False if v == 0 else bool(mask & (1 << (v - 1)))
        sigma = sum(inside(u) != inside(v) for u, v in blue) - sum(
            inside(u) != inside(v) for u, v in bad
        )
        if best is None or sigma < best:
            best = sigma
            best_mask = mask
    return best, [v for v in range(vertex_count) if v and best_mask & (1 << (v - 1))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    claimed_sha = source.pop("canonicalSha256")
    assert canonical_sha(source) == claimed_sha

    left_n, right_n = source["left"], source["right"]
    graph = nx.from_graph6_bytes(source["hit"]["graph6"].encode("ascii"))
    support_edges = sorted(norm(*edge) for edge in graph.edges())
    assert support_edges == sorted(norm(*edge) for edge in source["hit"]["supportEdges"])
    assert nx.is_connected(graph) and nx.is_bipartite(graph)
    assert len(support_edges) == 24

    atoms = all_atoms(graph, left_n, right_n)
    atom_index = {(a["shore"], a["u"], a["v"]): i for i, a in enumerate(atoms)}
    chosen = []
    for record in source["hit"]["selectedAtoms"]:
        key = (record["shore"], record["u"], record["v"])
        i = atom_index[key]
        assert set(map(tuple, record["rows"])) == set(atoms[i]["rows"])
        assert set(map(tuple, record["footprintEdges"])) == set(atoms[i]["footprint"])
        chosen.append(i)
    assert len(chosen) == len(set(chosen)) == 25

    bad_edges = sorted(norm(atoms[i]["u"], atoms[i]["v"]) for i in chosen)
    full = graph.copy()
    full.add_edges_from(bad_edges)
    assert all(value == 0 for value in nx.triangles(full).values())
    sdr_sizes = deletion_sdrs(atoms, chosen, support_edges)
    assert sdr_sizes == [24] * 25
    multiplicities = {
        edge: sum(edge in atoms[i]["footprint"] for i in chosen)
        for edge in support_edges
    }
    assert min(multiplicities.values()) >= 2

    classifier = source["hit"]["selectionMeta"]["localClassifiers"]["0"]
    owner = 0
    active = classifier["activeNeighbour"]
    vector = local_vector(atoms, chosen, graph, owner, active)
    assert [vector[k] for k in ["eForced", "iStep", "dStep", "dCoverage"]] == [0, 0, 0, 0]
    rows, selected_support = construct_rows(
        atoms, chosen, graph, owner, active, classifier
    )

    active_graph = nx.Graph()
    active_graph.add_nodes_from(graph.nodes())
    active_graph.add_edges_from(set(support_edges) - selected_support)
    component = nx.node_connected_component(active_graph, owner)
    active_bad_atoms = [
        i for i in chosen if atoms[i]["u"] in component and atoms[i]["v"] in component
    ]
    min_sigma, switch = minimum_switch_sigma(len(graph), support_edges, bad_edges)

    result = {
        "schema": "t5-local-classifier-hit-verification-v1",
        "sourceCanonicalSha256": claimed_sha,
        "supportVertices": len(graph),
        "supportEdges": len(support_edges),
        "selectedAtoms": len(chosen),
        "triangleCount": sum(nx.triangles(full).values()) // 3,
        "minimumMultiplicity": min(multiplicities.values()),
        "deletionSdrSizes": sdr_sizes,
        "owner": owner,
        "activeNeighbour": active,
        "classifierVector": [
            vector["eForced"],
            vector["iStep"],
            vector["dStep"],
            vector["dCoverage"],
        ],
        "selectedRows": {str(i): list(row) for i, row in sorted(rows.items())},
        "rowCountOwner": sum(owner in row for row in rows.values()),
        "activeComponent": sorted(component),
        "activeBadAtoms": active_bad_atoms,
        "activeOwner": bool(active_bad_atoms),
        "minimumDisplayedCutSigma": min_sigma,
        "minimumDisplayedCutSwitch": switch,
        "verdict": "PASS_TRIANGLE_FREE_ZERO_VECTOR_LOCAL_PROFILE",
    }
    result["canonicalSha256"] = canonical_sha(result)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
