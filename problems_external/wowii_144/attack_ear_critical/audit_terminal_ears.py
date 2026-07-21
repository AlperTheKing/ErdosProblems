#!/usr/bin/env python3
"""Audit exact terminal degree-two ears in eta-tight 2-connected graphs.

This is a diagnostic for the registered one-step eta deletion lemma.  It does
not replace that lemma by a location rule.  For every maximal degree-two ear
whose internal deletions all lower eta, it records radius changes and the
new-center/unique-eccentric-point witnesses forced by a nonincreasing-radius
deletion.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
IND2 = HERE.parent / "attack_ind2_multicycle"
sys.path.insert(0, str(IND2))
from analyze_tight_deletions import center_depth, cycle_rank, girth, records  # noqa: E402


def invariants(graph: nx.Graph) -> dict:
    ecc = nx.eccentricity(graph)
    radius = min(ecc.values())
    center = {v for v, value in ecc.items() if value == radius}
    dist = nx.multi_source_dijkstra_path_length(graph, center)
    eta = max(dist.values())
    realizers = {v for v, value in dist.items() if value == eta}
    return {
        "ecc": ecc,
        "radius": radius,
        "center": center,
        "eta": eta,
        "realizers": realizers,
    }


def maximal_degree_two_ears(graph: nx.Graph) -> list[list[int]]:
    """Return paths [endpoint, internal..., endpoint], once per path."""
    high = {v for v in graph if graph.degree[v] != 2}
    seen: set[frozenset[int]] = set()
    ears: list[list[int]] = []
    for endpoint in sorted(high):
        for first in sorted(graph[endpoint]):
            if first in high:
                continue
            path = [endpoint, first]
            previous, current = endpoint, first
            while current not in high:
                onward = [w for w in graph[current] if w != previous]
                if len(onward) != 1:
                    raise AssertionError(("not a degree-two chain", path, onward))
                previous, current = current, onward[0]
                path.append(current)
            key = frozenset(path[1:-1])
            if key and key not in seen:
                seen.add(key)
                ears.append(path)
    return ears


def deletion_row(graph: nx.Graph, old: dict, v: int) -> dict | None:
    subgraph = graph.copy()
    subgraph.remove_node(v)
    if not nx.is_connected(subgraph) or cycle_rank(subgraph) < 1:
        return None
    new = invariants(subgraph)
    new_centers = new["center"] - old["center"]
    uep = []
    for u in sorted(new_centers):
        far = {x for x, value in old["ecc"].items() if False}
        distance = nx.single_source_shortest_path_length(graph, u)
        eccentric = max(distance.values())
        far = sorted(x for x, value in distance.items() if value == eccentric)
        if far == [v]:
            uep.append(u)
    return {
        "v": v,
        "degree": graph.degree[v],
        "delta_eta": new["eta"] - old["eta"],
        "delta_radius": new["radius"] - old["radius"],
        "eta": new["eta"],
        "radius": new["radius"],
        "center": sorted(new["center"]),
        "new_centers": sorted(new_centers),
        "uep_new_centers": uep,
    }


def audit(max_n: int, show: int) -> dict:
    totals = {
        "graphs": 0,
        "biconnected": 0,
        "eta_tight_biconnected": 0,
        "ears": 0,
        "all_bad_ears": 0,
        "all_bad_ears_with_radius_increase": 0,
        "all_bad_ears_all_radius_nonincrease": 0,
        "all_bad_ears_all_radius_increase": 0,
        "all_bad_ears_mixed_radius_behavior": 0,
        "ears_noncontiguous_radius_increase": 0,
        "maximum_all_bad_ear_interior_length": 0,
        "bad_radius_nonincrease_deletions": 0,
        "bad_radius_nonincrease_with_good_new_center": 0,
        "bad_radius_nonincrease_without_good_new_center": 0,
        "bad_radius_nonincrease_nonrealizer": 0,
    }
    examples: list[dict] = []
    exchange_failures: list[dict] = []
    for n in range(5, max_n + 1):
        for code, graph in records(n):
            g = girth(graph)
            if g is None or g < 5 or cycle_rank(graph) < 2:
                continue
            totals["graphs"] += 1
            if not nx.is_biconnected(graph):
                continue
            totals["biconnected"] += 1
            old = invariants(graph)
            all_rows = [deletion_row(graph, old, v) for v in sorted(graph)]
            admissible = [row for row in all_rows if row is not None]
            rows_by_vertex = {row["v"]: row for row in admissible}
            for row in admissible:
                if row["delta_eta"] >= 0 or row["delta_radius"] > 0:
                    continue
                totals["bad_radius_nonincrease_deletions"] += 1
                if row["v"] not in old["realizers"]:
                    totals["bad_radius_nonincrease_nonrealizer"] += 1
                exchanged = [
                    u
                    for u in row["new_centers"]
                    if u in rows_by_vertex and rows_by_vertex[u]["delta_eta"] >= 0
                ]
                if exchanged:
                    totals["bad_radius_nonincrease_with_good_new_center"] += 1
                else:
                    totals["bad_radius_nonincrease_without_good_new_center"] += 1
                    if len(exchange_failures) < show:
                        exchange_failures.append(
                            {
                                "graph6": code.decode(),
                                "n": n,
                                "beta": cycle_rank(graph),
                                "girth": g,
                                "radius": old["radius"],
                                "eta": old["eta"],
                                "center": sorted(old["center"]),
                                "realizers": sorted(old["realizers"]),
                                "bad_deletion": row,
                                "new_center_deletions": {
                                    str(u): rows_by_vertex.get(u)
                                    for u in row["new_centers"]
                                },
                            }
                        )
            if max(row["delta_eta"] for row in admissible) != 0:
                continue
            totals["eta_tight_biconnected"] += 1
            good = [row for row in admissible if row["delta_eta"] >= 0]
            for ear in maximal_degree_two_ears(graph):
                totals["ears"] += 1
                rows = [deletion_row(graph, old, v) for v in ear[1:-1]]
                if any(row is None for row in rows):
                    raise AssertionError((code.decode(), ear, "inadmissible ear interior"))
                radius_flags = [row["delta_radius"] > 0 for row in rows]
                true_positions = [i for i, flag in enumerate(radius_flags) if flag]
                if true_positions and true_positions != list(range(min(true_positions), max(true_positions) + 1)):
                    totals["ears_noncontiguous_radius_increase"] += 1
                if any(row["delta_eta"] >= 0 for row in rows):
                    continue
                totals["all_bad_ears"] += 1
                totals["maximum_all_bad_ear_interior_length"] = max(
                    totals["maximum_all_bad_ear_interior_length"], len(rows)
                )
                if all(radius_flags):
                    totals["all_bad_ears_all_radius_increase"] += 1
                elif any(radius_flags):
                    totals["all_bad_ears_mixed_radius_behavior"] += 1
                if any(row["delta_radius"] > 0 for row in rows):
                    totals["all_bad_ears_with_radius_increase"] += 1
                else:
                    totals["all_bad_ears_all_radius_nonincrease"] += 1
                if len(examples) < show:
                    examples.append(
                        {
                            "graph6": code.decode(),
                            "n": n,
                            "edges": graph.number_of_edges(),
                            "beta": cycle_rank(graph),
                            "girth": g,
                            "radius": old["radius"],
                            "eta": old["eta"],
                            "center": sorted(old["center"]),
                            "realizers": sorted(old["realizers"]),
                            "ear": ear,
                            "ear_rows": rows,
                            "good_deletions": good,
                        }
                    )
    return {
        "max_n": max_n,
        "totals": totals,
        "exchange_failures": exchange_failures,
        "examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=11)
    parser.add_argument("--show", type=int, default=20)
    parser.add_argument("--output", type=Path, default=HERE / "terminal_ear_audit.json")
    args = parser.parse_args()
    result = audit(args.max_n, args.show)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["totals"], indent=2))
    print(f"examples={len(result['examples'])}")


if __name__ == "__main__":
    main()
