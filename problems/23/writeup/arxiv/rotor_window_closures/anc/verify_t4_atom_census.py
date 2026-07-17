"""Independent NetworkX replay of every t=4 bad-atom completion."""

from __future__ import annotations

import json
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
SUPPORT_PATH = HERE / "t4_support_graph_census.json"
ATOM_PATH = HERE / "t4_atom_circuit_census.json"


def verify_hash(payload):
    body = dict(payload)
    claimed = body.pop("canonicalSha256")
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    assert sha256(canonical.encode("ascii")).hexdigest() == claimed
    return claimed


def triangle_free(graph):
    return sum(nx.triangles(graph).values()) == 0


def footprint(graph, pair):
    rows = tuple(nx.all_shortest_paths(graph, *pair))
    assert rows and all(len(row) == 5 for row in rows)
    return frozenset(tuple(sorted(edge)) for row in rows
                     for edge in zip(row, row[1:])), len(rows)


def deletion_sdr(atom_footprints, support_edges):
    for deleted in range(16):
        incidence = nx.Graph()
        left = [("a", i) for i in range(16) if i != deleted]
        right = [("e", edge) for edge in support_edges]
        incidence.add_nodes_from(left, bipartite=0)
        incidence.add_nodes_from(right, bipartite=1)
        for i in range(16):
            if i == deleted:
                continue
            for edge in atom_footprints[i]:
                incidence.add_edge(("a", i), ("e", edge))
        matching = nx.algorithms.bipartite.maximum_matching(incidence, top_nodes=left)
        if any(node not in matching for node in left):
            return False
    return True


def hit_key(graph6, owner, bad_edges):
    return (graph6, owner["v"], owner["m"], tuple(sorted(bad_edges)))


def main():
    support_payload = json.loads(SUPPORT_PATH.read_text())
    atom_payload = json.loads(ATOM_PATH.read_text())
    support_hash = verify_hash(support_payload)
    atom_hash = verify_hash(atom_payload)
    expected = {hit_key(hit["graph6"], hit["owner"],
                        tuple(tuple(edge) for edge in hit["badEdges"]))
                for hit in atom_payload["hits"]}
    observed = set()
    counts = Counter()
    for record in support_payload["candidates"]:
        graph = nx.from_graph6_bytes(record["graph6"].encode("ascii"))
        colors = nx.algorithms.bipartite.color(graph)
        support_edges = frozenset(tuple(sorted(edge)) for edge in graph.edges)
        dist = dict(nx.all_pairs_shortest_path_length(graph))
        pairs = tuple((u, v) for u in graph for v in graph if u < v
                      and colors[u] == colors[v] and dist[u].get(v) == 4)
        footprints = {pair: footprint(graph, pair) for pair in pairs}
        for owner in record["ownerEmbeddings"]:
            v, m = owner["v"], owner["m"]
            remaining = tuple(pair for pair in pairs if v not in pair and m not in pair)
            if len(remaining) < 8:
                counts["insufficientRemainingPairs"] += 1
                continue
            for bv in combinations(owner["dist4V"], 4):
                for bm in combinations(owner["dist4M"], 4):
                    if not (set(bv) & set(bm)):
                        continue
                    counts["ownerChoices"] += 1
                    forced = {tuple(sorted((v, b))) for b in bv}
                    forced |= {tuple(sorted((m, b))) for b in bm}
                    forced_graph = nx.Graph()
                    forced_graph.add_nodes_from(graph)
                    forced_graph.add_edges_from(support_edges | forced)
                    if not triangle_free(forced_graph):
                        counts["forcedTriangleReject"] += 1
                        continue
                    for extra in combinations(remaining, 8):
                        counts["extraChoices"] += 1
                        bad_edges = tuple(sorted(forced | set(extra)))
                        if len(bad_edges) != 16:
                            continue
                        full = nx.Graph()
                        full.add_nodes_from(graph)
                        full.add_edges_from(support_edges | set(bad_edges))
                        if not triangle_free(full):
                            counts["triangleReject"] += 1
                            continue
                        counts["trianglePass"] += 1
                        atom_footprints = tuple(footprints[pair][0] for pair in bad_edges)
                        union = frozenset().union(*atom_footprints)
                        degree = Counter(edge for fp in atom_footprints for edge in fp)
                        if union != support_edges or min(degree.values(), default=0) < 2:
                            counts["unionOrMultiplicityReject"] += 1
                            continue
                        counts["unionMultiplicityPass"] += 1
                        if not deletion_sdr(atom_footprints, support_edges):
                            counts["circuitReject"] += 1
                            continue
                        counts["circuitPass"] += 1
                        observed.add(hit_key(record["graph6"], owner, bad_edges))
    assert counts == Counter(atom_payload["counts"])
    assert observed == expected and len(observed) == 576
    result = {
        "verdict": "PASS_INDEPENDENT_NETWORKX_ATOM_CENSUS",
        "supportCanonicalSha256": support_hash,
        "atomCanonicalSha256": atom_hash,
        "countsEqual": True,
        "hitSetsEqual": True,
        "hits": len(observed),
        "shortestPathEngine": "networkx.all_shortest_paths",
        "sdrEngine": "networkx.bipartite.maximum_matching",
    }
    out = HERE / "t4_atom_census_verification.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
