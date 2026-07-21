#!/usr/bin/env python3
"""Independent checks for the W144 two-good-deletion proof audit."""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
OBSTRUCTION = "J??CBBOi?{?"


def girth(graph: nx.Graph) -> int | None:
    best: int | None = None
    for source in graph:
        dist = {source: 0}
        parent: dict[int, int | None] = {source: None}
        queue = [source]
        for u in queue:
            for w in graph[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    parent[w] = u
                    queue.append(w)
                elif parent[u] != w:
                    length = dist[u] + dist[w] + 1
                    best = length if best is None else min(best, length)
    return best


def invariants(graph: nx.Graph) -> dict[str, object]:
    distances = dict(nx.all_pairs_shortest_path_length(graph))
    eccentricities = {
        u: max(distances[u].values()) for u in graph
    }
    radius = min(eccentricities.values())
    center = {u for u in graph if eccentricities[u] == radius}
    center_distance = {
        x: min(distances[x][c] for c in center) for x in graph
    }
    eta = max(center_distance.values())
    realizers = {x for x in graph if center_distance[x] == eta}
    return {
        "radius": radius,
        "center": center,
        "eta": eta,
        "realizers": realizers,
        "distances": distances,
        "eccentricities": eccentricities,
    }


def deletion_records(graph: nx.Graph) -> list[dict[str, object]]:
    base = invariants(graph)
    radius = int(base["radius"])
    eta = int(base["eta"])
    realizers = set(base["realizers"])
    distances = base["distances"]
    records: list[dict[str, object]] = []
    for v in graph:
        deleted = graph.copy()
        deleted.remove_node(v)
        beta = deleted.number_of_edges() - deleted.number_of_nodes() + 1
        if not nx.is_connected(deleted) or beta < 1:
            records.append({"v": v, "admissible": False})
            continue
        after = invariants(deleted)
        surviving_realizers = realizers - {v}
        close_realizer = any(
            distances[x][v] <= radius - eta + 1
            for x in surviving_realizers
        )
        certified = int(after["radius"]) < radius or (
            int(after["radius"]) == radius and close_realizer
        )
        new_centers = set(after["center"]) - set(base["center"])
        unique_eccentric = {
            u: [
                x
                for x in graph
                if distances[u][x] == base["eccentricities"][u]
            ]
            for u in new_centers
        }
        records.append(
            {
                "v": v,
                "admissible": True,
                "beta_after": beta,
                "radius_after": after["radius"],
                "eta_after": after["eta"],
                "center_after": sorted(after["center"]),
                "good": int(after["eta"]) >= eta,
                "local_certificate": certified,
                "new_centers": sorted(new_centers),
                "new_center_eccentric_vertices": unique_eccentric,
            }
        )
    return records


def main() -> None:
    graph = nx.from_graph6_bytes(OBSTRUCTION.encode("ascii"))
    base = invariants(graph)
    records = deletion_records(graph)
    admissible = [record for record in records if record["admissible"]]
    good = [record["v"] for record in admissible if record["good"]]
    certified = [
        record["v"] for record in admissible if record["local_certificate"]
    ]

    assert graph.number_of_nodes() == 11
    assert graph.number_of_edges() == 13
    assert graph.number_of_edges() - graph.number_of_nodes() + 1 == 3
    assert girth(graph) == 5
    assert base["radius"] == 3
    assert base["center"] == {0, 8, 9}
    assert base["eta"] == 3
    assert base["realizers"] == {5}
    assert good == [3, 4, 6, 8, 9]
    assert certified == []

    for record in admissible:
        if (
            not record["good"]
            and int(record["radius_after"]) <= int(base["radius"])
            and record["v"] != 5
        ):
            for u in record["new_centers"]:
                assert record["new_center_eccentric_vertices"][u] == [record["v"]]

    output = {
        "graph6": OBSTRUCTION,
        "order": graph.number_of_nodes(),
        "size": graph.number_of_edges(),
        "girth": girth(graph),
        "cycle_rank": graph.number_of_edges() - graph.number_of_nodes() + 1,
        "radius": base["radius"],
        "center": sorted(base["center"]),
        "eta": base["eta"],
        "eta_realizers": sorted(base["realizers"]),
        "good_deletions": good,
        "local_metric_certificates": certified,
        "deletions": records,
    }
    path = HERE / "two_good_deletion_obstruction.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", **output}, default=list))


if __name__ == "__main__":
    main()
