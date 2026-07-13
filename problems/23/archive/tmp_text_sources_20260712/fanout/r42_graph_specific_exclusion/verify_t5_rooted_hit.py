#!/usr/bin/env python3
"""Independent NetworkX replay of a rooted t=5 support-circuit hit."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import networkx as nx


def canonical_sha_without_marker(payload: dict) -> str:
    body = dict(payload)
    body.pop("canonicalSha256", None)
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.payload.read_text(encoding="utf-8"))
    if payload["verdict"] != "HIT_PATH_REALIZABLE_T5_MINIMAL_CIRCUIT":
        raise SystemExit("payload does not contain a hit")
    if canonical_sha_without_marker(payload) != payload["canonicalSha256"]:
        raise SystemExit("canonical payload hash mismatch")

    left_n = payload["left"]
    right_n = payload["right"]
    hit = payload["hit"]
    graph = nx.Graph()
    graph.add_nodes_from(range(left_n + right_n))
    graph.add_edges_from(tuple(edge) for edge in hit["supportEdges"])

    assert graph.number_of_edges() == 24
    assert nx.is_connected(graph)
    assert nx.is_bipartite(graph)
    assert graph.degree[0] == graph.degree[1] == 5
    assert {left_n, left_n + 1} <= (set(graph[0]) & set(graph[1]))

    support_edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    support_index = {edge: i for i, edge in enumerate(support_edges)}
    atoms = hit["selectedAtoms"]
    assert len(atoms) == 25

    bad_edges = []
    footprints = []
    for atom in atoms:
        u, v = atom["u"], atom["v"]
        assert (u < left_n) == (v < left_n)
        assert nx.shortest_path_length(graph, u, v) == 4
        actual_rows = sorted(tuple(path) for path in nx.all_shortest_paths(graph, u, v))
        claimed_rows = sorted(tuple(path) for path in atom["rows"])
        assert actual_rows == claimed_rows
        actual_footprint = {
            tuple(sorted((path[i], path[i + 1])))
            for path in actual_rows
            for i in range(4)
        }
        claimed_footprint = {tuple(edge) for edge in atom["footprintEdges"]}
        assert actual_footprint == claimed_footprint
        bad_edges.append(tuple(sorted((u, v))))
        footprints.append({support_index[edge] for edge in actual_footprint})

    assert len(set(bad_edges)) == 25
    full_graph = graph.copy()
    full_graph.add_edges_from(bad_edges)
    assert not any(nx.triangles(full_graph).values())
    assert sum(0 in edge for edge in bad_edges) == 5
    assert sum(1 in edge for edge in bad_edges) == 5
    assert tuple(sorted((0, 4))) in bad_edges
    assert tuple(sorted((1, 4))) in bad_edges
    assert tuple(sorted((2, 3))) in bad_edges

    live_atom = bad_edges.index((2, 3))
    live_rows = {tuple(row) for row in atoms[live_atom]["rows"]}
    assert (2, left_n, 0, left_n + 1, 3) in live_rows
    assert (2, left_n, 1, left_n + 1, 3) in live_rows

    multiplicity = Counter(edge for footprint in footprints for edge in footprint)
    assert set(multiplicity) == set(range(24))
    assert min(multiplicity.values()) >= 2

    deletion_matching_sizes = []
    for excluded in range(25):
        incidence = nx.Graph()
        atom_nodes = [("a", i) for i in range(25) if i != excluded]
        edge_nodes = [("e", e) for e in range(24)]
        incidence.add_nodes_from(atom_nodes, bipartite=0)
        incidence.add_nodes_from(edge_nodes, bipartite=1)
        for i in range(25):
            if i == excluded:
                continue
            incidence.add_edges_from((("a", i), ("e", e)) for e in footprints[i])
        matching = nx.algorithms.bipartite.maximum_matching(incidence, top_nodes=atom_nodes)
        size = sum(node in matching for node in atom_nodes)
        deletion_matching_sizes.append(size)
        assert size == 24

    verification = {
        "schema": "rooted-t5-support-hit-independent-verification-v1",
        "sourceCanonicalSha256": payload["canonicalSha256"],
        "supportVertices": graph.number_of_nodes(),
        "supportEdges": graph.number_of_edges(),
        "badAtoms": len(atoms),
        "minimumSupportMultiplicity": min(multiplicity.values()),
        "deletionMatchingSizes": deletion_matching_sizes,
        "liveMiddleSwapRows": 2,
        "verdict": "PASS_PATH_REALIZABLE_T5_MINIMAL_CIRCUIT",
    }
    raw = json.dumps(verification, sort_keys=True, separators=(",", ":")).encode("ascii")
    verification["canonicalSha256"] = hashlib.sha256(raw).hexdigest()
    out = args.payload.with_name(args.payload.stem + "_verification.json")
    out.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(verification, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
