#!/usr/bin/env python3
"""Exact probe of the direct W144-ROOT unicyclic witness lemma."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
IND2 = HERE.parent / "attack_ind2_multicycle"
sys.path.insert(0, str(IND2))
from analyze_tight_deletions import center_depth, cycle_rank, girth, records  # noqa: E402


def distance_to_set(graph: nx.Graph, source: int, targets: set[int]) -> int:
    lengths = nx.single_source_shortest_path_length(graph, source)
    return min(lengths[t] for t in targets)


def first_witness(graph: nx.Graph, realizers: list[int], eta: int) -> dict | None:
    vertices = sorted(graph)
    realizer_set = set(realizers)
    for size in range(3, len(vertices) + 1):
        for subset_tuple in itertools.combinations(vertices, size):
            subset = set(subset_tuple)
            roots_here = sorted(subset & realizer_set)
            if not roots_here:
                continue
            subgraph = graph.subgraph(subset).copy()
            if subgraph.number_of_edges() != subgraph.number_of_nodes():
                continue
            if not nx.is_connected(subgraph):
                continue
            center = set(nx.center(subgraph))
            for root in roots_here:
                depth = distance_to_set(subgraph, root, center)
                if depth >= eta:
                    return {
                        "root": root,
                        "vertices": sorted(subset),
                        "girth": girth(subgraph),
                        "radius": nx.radius(subgraph),
                        "center": sorted(center),
                        "rooted_depth": depth,
                    }
    return None


def audit(min_n: int, max_n: int) -> dict:
    total = 0
    per_order: dict[str, int] = {}
    witness_hash = hashlib.sha256()
    failure = None
    for n in range(min_n, max_n + 1):
        checked = 0
        for code, graph in records(n):
            g = girth(graph)
            if g is None or g < 5 or cycle_rank(graph) < 2:
                continue
            checked += 1
            total += 1
            eta, center = center_depth(graph)
            realizers = [
                x for x in sorted(graph)
                if distance_to_set(graph, x, set(center)) == eta
            ]
            witness = first_witness(graph, realizers, eta)
            if witness is None:
                failure = {
                    "graph6": code.decode(),
                    "n": n,
                    "m": graph.number_of_edges(),
                    "rank": cycle_rank(graph),
                    "girth": g,
                    "radius": nx.radius(graph),
                    "eta": eta,
                    "center": sorted(center),
                    "realizers": realizers,
                    "edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges()),
                }
                break
            witness_hash.update(
                f"{code.decode()}:{witness['root']}:{','.join(map(str, witness['vertices']))}\n".encode()
            )
        per_order[str(n)] = checked
        if failure is not None:
            break
    return {
        "statement": "some eta-realizer has an induced connected unicyclic rooted-depth witness",
        "min_n": min_n,
        "max_n": max_n,
        "total_checked": total,
        "per_order": per_order,
        "canonical_witness_sha256": witness_hash.hexdigest(),
        "failure": failure,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=11)
    parser.add_argument("--output", type=Path, default=HERE / "rooted_unicyclic_witness_results.json")
    args = parser.parse_args()
    result = audit(args.min_n, args.max_n)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["failure"] is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
