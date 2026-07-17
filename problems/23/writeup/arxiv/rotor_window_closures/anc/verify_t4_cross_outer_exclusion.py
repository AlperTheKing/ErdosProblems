#!/usr/bin/env python3
"""Graph-only replay of the live t=4 middle-swap obstruction.

The complete atom census leaves 576 minimal 16/15 circuits on four
support-graph/owner embeddings.  A checked live swap

    (a,x,m,y,b) <-> (a,x,v,y,b)

would force x,y to be common blue neighbours of v,m and would force a,b to
be a distance-four cross-outer pair.  This script independently decodes the
four graph6 supports with NetworkX and exhausts that necessary geometry.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "t4_atom_circuit_census.json"
OUTPUT = HERE / "t4_cross_outer_exclusion.json"
EXPECTED_SOURCE_SHA = (
    "302e04ef5ff14c78cbe9dc5800ac0226e730ed0baca123585dc6469a82d66652"
)


def live_cross_outer_candidates(
    graph: nx.Graph, v: int, m: int
) -> list[tuple[int, int, int, int]]:
    """Return (a,x,y,b) candidates for the two checked length-four rows."""
    common = sorted(set(graph[v]) & set(graph[m]))
    candidates: set[tuple[int, int, int, int]] = set()

    for x in common:
        for y in common:
            if x == y:
                continue
            for a in graph[x]:
                if a in {v, m}:
                    continue
                for b in graph[y]:
                    if b in {v, m, a}:
                        continue
                    if len({a, x, m, y, b}) != 5:
                        continue
                    if len({a, x, v, y, b}) != 5:
                        continue
                    if nx.shortest_path_length(graph, a, b) == 4:
                        candidates.add((a, x, y, b))

    return sorted(candidates)


def canonical_sha(payload: dict) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if source.get("canonicalSha256") != EXPECTED_SOURCE_SHA:
        raise SystemExit("source census SHA marker mismatch")

    multiplicities = Counter(
        (hit["graph6"], hit["owner"]["v"], hit["owner"]["m"])
        for hit in source["hits"]
    )
    if sum(multiplicities.values()) != 576:
        raise SystemExit("expected exactly 576 complete atom circuits")

    rows = []
    total_candidates = 0
    for (graph6, v, m), circuit_count in sorted(multiplicities.items()):
        graph = nx.from_graph6_bytes(graph6.encode("ascii"))
        candidates = live_cross_outer_candidates(graph, v, m)
        total_candidates += len(candidates)
        rows.append(
            {
                "graph6": graph6,
                "n": graph.number_of_nodes(),
                "v": v,
                "m": m,
                "circuitCount": circuit_count,
                "commonBlue": sorted(set(graph[v]) & set(graph[m])),
                "liveCrossOuterCandidates": [list(item) for item in candidates],
            }
        )

    payload = {
        "schema": "r42-t4-cross-outer-exclusion-v1",
        "sourceCanonicalSha256": EXPECTED_SOURCE_SHA,
        "circuitCount": sum(multiplicities.values()),
        "supportOwnerTypeCount": len(multiplicities),
        "types": rows,
        "totalLiveCrossOuterCandidates": total_candidates,
        "verdict": (
            "PASS_NO_LIVE_MIDDLE_SWAP_GEOMETRY"
            if total_candidates == 0
            else "FAIL_LIVE_MIDDLE_SWAP_GEOMETRY_FOUND"
        ),
    }
    payload["canonicalSha256"] = canonical_sha(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2, sort_keys=True))
    if total_candidates != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
