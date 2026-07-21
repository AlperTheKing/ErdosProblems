#!/usr/bin/env python3
"""Test the direct maximum-induced-tree / center-geodesic boundary lemma.

The existential statement tested is the weakest form sufficient for W144:
there are an eta-realizer x, a nearest center c, a shortest x-c path Q, a
largest induced tree T among those containing Q, an exterior boundary vertex
z, and two T-neighbors a,b of z such that the unique a-b path in T meets Q in
at most one vertex.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
IND2 = HERE.parent / "attack_ind2_multicycle"
sys.path.insert(0, str(IND2))
from analyze_tight_deletions import center_depth, girth, records  # noqa: E402


def induced_tree_masks(graph: nx.Graph) -> list[int]:
    vertices = sorted(graph)
    n = len(vertices)
    answer = []
    for mask in range(1, 1 << n):
        size = mask.bit_count()
        if size == 1:
            answer.append(mask)
            continue
        chosen = [vertices[i] for i in range(n) if mask & (1 << i)]
        subgraph = graph.subgraph(chosen)
        if subgraph.number_of_edges() == size - 1 and nx.is_connected(subgraph):
            answer.append(mask)
    return answer


def mask_of(vertices: set[int] | list[int]) -> int:
    mask = 0
    for v in vertices:
        mask |= 1 << v
    return mask


def witness_for_tree(
    graph: nx.Graph, tree_mask: int, qset: set[int]
) -> dict | None:
    tree_vertices = {v for v in graph if tree_mask & (1 << v)}
    tree = graph.subgraph(tree_vertices)
    for z in sorted(set(graph) - tree_vertices):
        neighbors = sorted(set(graph[z]) & tree_vertices)
        for a, b in itertools.combinations(neighbors, 2):
            path = nx.shortest_path(tree, a, b)
            overlap = sorted(set(path) & qset)
            if len(overlap) <= 1:
                return {
                    "z": z,
                    "a": a,
                    "b": b,
                    "tree_path": path,
                    "q_overlap": overlap,
                }
    return None


def audit_graph(code: bytes, graph: nx.Graph) -> tuple[bool, dict]:
    eta, center = center_depth(graph)
    distance_to_center = nx.multi_source_dijkstra_path_length(graph, center)
    realizers = sorted(v for v, value in distance_to_center.items() if value == eta)
    trees = induced_tree_masks(graph)
    choices = []
    best_overlap = None
    for x in realizers:
        for c in sorted(center):
            if nx.shortest_path_length(graph, x, c) != eta:
                continue
            for q in nx.all_shortest_paths(graph, x, c):
                qset = set(q)
                qmask = mask_of(qset)
                containing = [mask for mask in trees if mask & qmask == qmask]
                maximum_order = max(mask.bit_count() for mask in containing)
                maximum = [mask for mask in containing if mask.bit_count() == maximum_order]
                choice = {
                    "x": x,
                    "c": c,
                    "q": q,
                    "maximum_order": maximum_order,
                    "maximum_tree_count": len(maximum),
                    "trees": [],
                }
                for mask in maximum:
                    witness = witness_for_tree(graph, mask, qset)
                    tree_vertices = [v for v in graph if mask & (1 << v)]
                    min_overlap = None
                    min_row = None
                    tree = graph.subgraph(tree_vertices)
                    for z in sorted(set(graph) - set(tree_vertices)):
                        neighbors = sorted(set(graph[z]) & set(tree_vertices))
                        for a, b in itertools.combinations(neighbors, 2):
                            path = nx.shortest_path(tree, a, b)
                            overlap = sorted(set(path) & qset)
                            if min_overlap is None or len(overlap) < min_overlap:
                                min_overlap = len(overlap)
                                min_row = {
                                    "z": z,
                                    "a": a,
                                    "b": b,
                                    "tree_path": path,
                                    "q_overlap": overlap,
                                }
                    if min_overlap is not None:
                        best_overlap = (
                            min_overlap
                            if best_overlap is None
                            else min(best_overlap, min_overlap)
                        )
                    choice["trees"].append(
                        {
                            "vertices": tree_vertices,
                            "witness": witness,
                            "minimum_overlap": min_overlap,
                            "minimum_overlap_row": min_row,
                        }
                    )
                    if witness is not None:
                        return True, {
                            "graph6": code.decode(),
                            "eta": eta,
                            "center": sorted(center),
                            "realizers": realizers,
                            "choice": choice,
                        }
                choices.append(choice)
    return False, {
        "graph6": code.decode(),
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "girth": girth(graph),
        "eta": eta,
        "center": sorted(center),
        "realizers": realizers,
        "best_overlap": best_overlap,
        "edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges()),
        "choices": choices,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--min-beta", type=int, default=1)
    parser.add_argument("--output", type=Path, default=HERE / "max_tree_geodesic_boundary.json")
    args = parser.parse_args()
    checked = 0
    first_failure = None
    per_order: dict[str, int] = {}
    for n in range(5, args.max_n + 1):
        count = 0
        for code, graph in records(n):
            g = girth(graph)
            if g is None or g < 5:
                continue
            if graph.number_of_edges() - graph.number_of_nodes() + 1 < args.min_beta:
                continue
            eta, _ = center_depth(graph)
            if eta == 0:
                continue
            checked += 1
            count += 1
            success, detail = audit_graph(code, graph)
            if not success:
                first_failure = detail
                break
        per_order[str(n)] = count
        if first_failure is not None:
            break
    result = {
        "statement": "exists x,c,Q, maximum induced T containing Q, boundary z,a,b with |Tpath(a,b) intersect Q|<=1",
        "max_n": args.max_n,
        "min_beta": args.min_beta,
        "checked": checked,
        "per_order": per_order,
        "first_failure": first_failure,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if first_failure is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
