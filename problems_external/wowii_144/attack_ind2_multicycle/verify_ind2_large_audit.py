#!/usr/bin/env python3
"""Fast, exact verifier/search for the W144-IND2 multicyclic lemma.

For every input graph this computes girth, center set, eta, and all quantities
needed for the deletion decision directly.  It stops at the first valid
deletion witness, but emits the complete deletion table if a graph fails.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

import networkx as nx

from audit_ind2_large import (
    attach_tail,
    attach_two_tails,
    center_depth,
    cycle_rank,
    cycle_with_ear,
    deletion_table,
    girth,
    graph6,
    handcuff,
    random_ear_graph,
    random_subdivided_core,
    random_tree_plus_edges,
    theta,
)


def targeted_families():
    """Deterministic high-girth ear/block/tail families on 14--40 vertices."""
    for a in range(2, 11):
        for b in range(a, 12):
            for c in range(b, 13):
                if a + b < 5:
                    continue
                core = theta(a, b, c)
                for tail in (0, 2, 5, 8):
                    graph = attach_tail(core, 0, tail)
                    if 14 <= len(graph) <= 40:
                        yield f"theta({a},{b},{c})+tail({tail})", graph
                for tail in (1, 3):
                    graph = attach_two_tails(core, 0, tail, 1, tail + 1)
                    if 14 <= len(graph) <= 40:
                        yield f"theta({a},{b},{c})+2tails({tail},{tail+1})", graph

    for g1 in range(5, 13):
        for g2 in range(5, 13):
            for bridge in range(0, 8):
                core = handcuff(g1, g2, bridge)
                roots = [0, min(g1, len(core) - 1)]
                for tail in (0, 3, 7):
                    graph = attach_tail(core, roots[0], tail)
                    if 14 <= len(graph) <= 40:
                        yield f"handcuff({g1},{g2},{bridge})+tail({tail})", graph
                for t1 in (1, 3):
                    graph = attach_two_tails(core, roots[0], t1, roots[1], t1 + 2)
                    if 14 <= len(graph) <= 40:
                        yield f"handcuff({g1},{g2},{bridge})+2tails({t1},{t1+2})", graph

    for g in range(5, 18):
        for separation in sorted({2, max(2, g // 2), g - 2}):
            for ear_length in (3, 5, 8, 11):
                core = cycle_with_ear(g, separation, ear_length)
                core_girth = girth(core)
                if core_girth is None or core_girth < 5:
                    continue
                for tail in (0, 4, 8):
                    graph = attach_tail(core, 0, tail)
                    if 14 <= len(graph) <= 40:
                        yield f"ear({g},{separation},{ear_length})+tail({tail})", graph
                graph = attach_two_tails(core, 0, 3, separation, 5)
                if 14 <= len(graph) <= 40:
                    yield f"ear({g},{separation},{ear_length})+2tails(3,5)", graph


def base_record(graph: nx.Graph) -> dict:
    g = girth(graph)
    assert g is not None
    eta, center, radius = center_depth(graph)
    return {
        "n": len(graph),
        "m": graph.number_of_edges(),
        "rank": cycle_rank(graph),
        "girth": g,
        "eta": eta,
        "radius": radius,
        "center": center,
        "phi": g + eta,
        "graph6": graph6(graph),
        "edges": sorted([min(u, v), max(u, v)] for u, v in graph.edges()),
    }


def first_witness(graph: nx.Graph, base: dict) -> dict | None:
    articulation = set(nx.articulation_points(graph))
    center = base["center"]
    center_distances = nx.multi_source_dijkstra_path_length(graph, center)
    candidates = [
        v
        for v in graph
        if v not in articulation and cycle_rank(graph) - graph.degree[v] + 1 >= 1
    ]
    candidates.sort(key=lambda v: (graph.degree[v], -center_distances[v], v))
    for v in candidates:
        h = graph.copy()
        h.remove_node(v)
        assert nx.is_connected(h) and cycle_rank(h) >= 1
        gh = girth(h)
        assert gh is not None
        etah, centerh, radiush = center_depth(h)
        row = {
            "v": v,
            "degree": graph.degree[v],
            "rank_h": cycle_rank(h),
            "girth_h": gh,
            "eta_h": etah,
            "radius_h": radiush,
            "center_h": centerh,
            "phi_h": gh + etah,
            "slack": gh + etah - base["phi"],
        }
        if row["slack"] >= 0:
            return row
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=14420260718)
    parser.add_argument("--random-trials", type=int, default=5000)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("ind2_large_audit_results.json"),
    )
    args = parser.parse_args()

    counts = Counter()
    witness_slack = Counter()
    order_counts = Counter()
    tight_examples = []
    counterexample = None

    def check(name: str, corpus: str, graph: nx.Graph) -> bool:
        nonlocal counterexample
        graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
        assert 14 <= len(graph) <= 40
        assert nx.is_connected(graph)
        g = girth(graph)
        assert g is not None and g >= 5
        assert cycle_rank(graph) >= 2
        base = base_record(graph)
        witness = first_witness(graph, base)
        counts[corpus] += 1
        order_counts[len(graph)] += 1
        if witness is None:
            _, rows = deletion_table(graph)
            counterexample = {
                "name": name,
                "corpus": corpus,
                "base": base,
                "deletions": rows,
                "best_slack": max(
                    row["slack"] for row in rows if row["admissible"]
                ),
            }
            return False
        witness_slack[witness["slack"]] += 1
        if witness["slack"] == 0 and len(tight_examples) < 40:
            tight_examples.append(
                {
                    "name": name,
                    "corpus": corpus,
                    "graph6": base["graph6"],
                    "n": base["n"],
                    "girth": base["girth"],
                    "eta": base["eta"],
                    "rank": base["rank"],
                    "witness": witness,
                }
            )
        return True

    for name, graph in targeted_families():
        if not check(name, "deterministic", graph):
            break

    rng = random.Random(args.seed)
    generators = (random_ear_graph, random_tree_plus_edges, random_subdivided_core)
    if counterexample is None:
        for trial in range(args.random_trials):
            n = rng.randint(14, 40)
            generator = generators[trial % len(generators)]
            graph = generator(rng, n)
            name = f"{generator.__name__}(seed={args.seed},trial={trial},n={n})"
            if not check(name, "random", graph):
                break

    result = {
        "lemma": "exists v: G-v connected cyclic and phi(G-v)>=phi(G)",
        "phi": "girth + maximum distance to center set",
        "seed": args.seed,
        "requested_random_trials": args.random_trials,
        "counts": dict(counts),
        "order_counts": {str(k): v for k, v in sorted(order_counts.items())},
        "first_witness_slack_counts": {
            str(k): v for k, v in sorted(witness_slack.items())
        },
        "tight_examples": tight_examples,
        "counterexample": counterexample,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if counterexample is not None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
