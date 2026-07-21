#!/usr/bin/env python3
"""Falsifier-first stress for the separable W144-GCOMB parameter cover.

The generator is deterministic.  It builds 1-sums of cycles, theta blocks,
subdivided dense cores, high-girth cubic cores, and rooted trees.  Every
retained graph is connected, cyclic, separable, has girth at least five, and
has order in the requested interval.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent


@dataclass(frozen=True)
class NamedGraph:
    name: str
    graph: nx.Graph


def exact_girth(graph: nx.Graph) -> int | None:
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


def theta(lengths: tuple[int, int, int]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from([0, 1])
    next_vertex = 2
    for length in lengths:
        previous = 0
        for _ in range(length - 1):
            graph.add_edge(previous, next_vertex)
            previous = next_vertex
            next_vertex += 1
        graph.add_edge(previous, 1)
    return nx.convert_node_labels_to_integers(graph)


def subdivide(core: nx.Graph, lengths: list[int]) -> nx.Graph:
    edges = sorted(tuple(sorted(edge)) for edge in core.edges())
    if len(edges) != len(lengths):
        raise ValueError("one length is required for every core edge")
    graph = nx.Graph()
    graph.add_nodes_from(core.nodes())
    next_vertex = max(core.nodes(), default=-1) + 1
    for (u, v), length in zip(edges, lengths, strict=True):
        previous = u
        for _ in range(length - 1):
            graph.add_edge(previous, next_vertex)
            previous = next_vertex
            next_vertex += 1
        graph.add_edge(previous, v)
    return nx.convert_node_labels_to_integers(graph)


def one_sum(left: nx.Graph, right: nx.Graph, root_left: int, root_right: int) -> nx.Graph:
    graph = nx.Graph(left)
    next_vertex = max(graph.nodes(), default=-1) + 1
    mapping: dict[int, int] = {root_right: root_left}
    for vertex in right:
        if vertex != root_right:
            mapping[vertex] = next_vertex
            next_vertex += 1
    graph.add_edges_from((mapping[u], mapping[v]) for u, v in right.edges())
    return nx.convert_node_labels_to_integers(graph)


def path_block(added_vertices: int) -> nx.Graph:
    return nx.path_graph(added_vertices + 1)


def star_block(leaves: int) -> nx.Graph:
    return nx.star_graph(leaves)


def core_catalogue(seed: int) -> list[NamedGraph]:
    rng = random.Random(seed)
    blocks: list[NamedGraph] = []
    for length in range(5, 13):
        blocks.append(NamedGraph(f"C{length}", nx.cycle_graph(length)))
    for a in range(1, 7):
        for b in range(max(a, 2), 8):
            for c in range(b, 9):
                if a + b >= 5:
                    blocks.append(NamedGraph(f"theta({a},{b},{c})", theta((a, b, c))))

    fixed_cores = [
        ("K4", nx.complete_graph(4)),
        ("K5", nx.complete_graph(5)),
        ("K6", nx.complete_graph(6)),
        ("K33", nx.complete_bipartite_graph(3, 3)),
        ("cube", nx.cubical_graph()),
        ("petersen", nx.petersen_graph()),
        ("heawood", nx.heawood_graph()),
    ]
    for core_name, core in fixed_cores:
        core = nx.convert_node_labels_to_integers(core)
        patterns: list[list[int]] = [[2] * core.number_of_edges()]
        if exact_girth(core) is not None and exact_girth(core) >= 5:
            patterns.append([1] * core.number_of_edges())
        for _ in range(18):
            patterns.append([rng.randint(1, 3) for _ in core.edges()])
        for index, lengths in enumerate(patterns):
            graph = subdivide(core, lengths)
            girth = exact_girth(graph)
            if girth is not None and girth >= 5 and graph.number_of_nodes() <= 42:
                blocks.append(NamedGraph(f"subdiv-{core_name}-{index}", graph))
    return blocks


def deterministic_cases(blocks: list[NamedGraph]) -> list[NamedGraph]:
    cases: list[NamedGraph] = []
    cycles = [block for block in blocks if block.name.startswith("C")]
    thetas = [block for block in blocks if block.name.startswith("theta")]
    subdivided = [block for block in blocks if block.name.startswith("subdiv")]

    for first in cycles:
        for second in cycles:
            graph = one_sum(first.graph, second.graph, 0, 0)
            if 14 <= graph.number_of_nodes() <= 50:
                cases.append(NamedGraph(f"cycle-pair:{first.name}+{second.name}", graph))
            graph = one_sum(graph, path_block(5), 0, 0)
            if 14 <= graph.number_of_nodes() <= 50:
                cases.append(NamedGraph(f"cycle-pair-tail:{first.name}+{second.name}", graph))

    for block in thetas[::7]:
        for cycle in cycles[::2]:
            graph = one_sum(block.graph, cycle.graph, 0, 0)
            if 14 <= graph.number_of_nodes() <= 50:
                cases.append(NamedGraph(f"theta-cycle:{block.name}+{cycle.name}", graph))
            rooted = one_sum(graph, star_block(4), max(graph), 0)
            if 14 <= rooted.number_of_nodes() <= 50:
                cases.append(NamedGraph(f"theta-cycle-star:{block.name}+{cycle.name}", rooted))

    for block in subdivided:
        if block.graph.number_of_nodes() > 44:
            continue
        graph = one_sum(block.graph, path_block(min(6, 50 - block.graph.number_of_nodes())), 0, 0)
        if 14 <= graph.number_of_nodes() <= 50:
            cases.append(NamedGraph(f"core-tail:{block.name}", graph))
        for cycle in cycles[::3]:
            graph = one_sum(block.graph, cycle.graph, 0, 0)
            if 14 <= graph.number_of_nodes() <= 50:
                cases.append(NamedGraph(f"core-cycle:{block.name}+{cycle.name}", graph))
    return cases


def random_case(rng: random.Random, blocks: list[NamedGraph], min_n: int, max_n: int) -> NamedGraph:
    target = rng.randint(min_n, max_n)
    first = rng.choice(blocks)
    while first.graph.number_of_nodes() >= target:
        first = rng.choice(blocks)
    graph = nx.Graph(first.graph)
    names = [first.name]
    attachments = 0
    while graph.number_of_nodes() < target:
        remaining = target - graph.number_of_nodes()
        options: list[NamedGraph] = [
            block for block in blocks if block.graph.number_of_nodes() - 1 <= remaining
        ]
        if remaining >= 1:
            options.append(NamedGraph(f"P+{remaining}", path_block(remaining)))
        if remaining >= 2:
            options.append(NamedGraph(f"star+{min(remaining, 6)}", star_block(min(remaining, 6))))
        block = rng.choice(options)
        root_left = rng.choice(list(graph))
        root_right = rng.choice(list(block.graph))
        graph = one_sum(graph, block.graph, root_left, root_right)
        names.append(block.name)
        attachments += 1
        if attachments > 8 and graph.number_of_nodes() < target:
            remaining = target - graph.number_of_nodes()
            graph = one_sum(graph, path_block(remaining), rng.choice(list(graph)), 0)
            names.append(f"P+{remaining}")
    if attachments == 0:
        graph = one_sum(graph, path_block(1), 0, 0)
        names.append("P+1")
    return NamedGraph("random:" + "+".join(names), graph)


def evaluate(item: NamedGraph) -> dict[str, object] | None:
    graph = item.graph
    if not nx.is_connected(graph) or nx.is_biconnected(graph):
        return None
    n = graph.number_of_nodes()
    girth = exact_girth(graph)
    if girth is None or girth < 5:
        return None
    eccentricity = nx.eccentricity(graph)
    radius = min(eccentricity.values())
    center = {v for v, value in eccentricity.items() if value == radius}
    center_distances = nx.multi_source_dijkstra_path_length(graph, center)
    eta = max(center_distances.values())
    diameter = max(eccentricity.values())
    maximum_degree = max(dict(graph.degree()).values())
    beta = graph.number_of_edges() - n + 1
    terms = {
        "degree": maximum_degree - 2,
        "diameter": diameter - math.floor(girth / 2),
        "order_rank": n - girth - beta + 1,
    }
    rhs = max(terms.values())
    return {
        "name": item.name,
        "graph6": nx.to_graph6_bytes(graph, header=False).strip().decode("ascii"),
        "n": n,
        "m": graph.number_of_edges(),
        "girth": girth,
        "beta": beta,
        "diameter": diameter,
        "radius": radius,
        "maximum_degree": maximum_degree,
        "center": sorted(center),
        "eta": eta,
        "terms": terms,
        "rhs": rhs,
        "slack": rhs - eta,
        "articulations": sorted(nx.articulation_points(graph)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260718)
    parser.add_argument("--trials", type=int, default=30000)
    parser.add_argument("--min-n", type=int, default=14)
    parser.add_argument("--max-n", type=int, default=50)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output", type=Path, default=HERE / "gcomb_cut_stress_results.json")
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        raise SystemExit("workers must lie in 1..8")

    blocks = core_catalogue(args.seed)
    generated = deterministic_cases(blocks)
    rng = random.Random(args.seed)
    generated.extend(
        random_case(rng, blocks, args.min_n, args.max_n)
        for _ in range(args.trials)
    )

    unique: dict[str, NamedGraph] = {}
    for item in generated:
        code = nx.to_graph6_bytes(item.graph, header=False).strip().decode("ascii")
        unique.setdefault(code, item)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        evaluated = list(executor.map(evaluate, unique.values(), chunksize=64))
    records = [record for record in evaluated if record is not None]
    records.sort(key=lambda record: (record["slack"], record["n"], record["graph6"]))

    failures = [record for record in records if record["slack"] < 0]
    equalities = [record for record in records if record["slack"] == 0]
    source_counts = Counter(record["name"].split(":", 1)[0] for record in records)
    equality_sources = Counter(record["name"].split(":", 1)[0] for record in equalities)
    order_counts = Counter(record["n"] for record in records)
    summary = {
        "seed": args.seed,
        "trials": args.trials,
        "workers": args.workers,
        "min_n": args.min_n,
        "max_n": args.max_n,
        "catalogue_blocks": len(blocks),
        "generated": len(generated),
        "unique_labelled": len(unique),
        "retained_separable_girth_at_least_five": len(records),
        "failures": len(failures),
        "minimum_slack": min((record["slack"] for record in records), default=None),
        "equalities": len(equalities),
        "source_counts": dict(sorted(source_counts.items())),
        "equality_source_counts": dict(sorted(equality_sources.items())),
        "order_counts": {str(key): value for key, value in sorted(order_counts.items())},
        "first_failure": failures[0] if failures else None,
        "first_100_tight": records[:100],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                key: summary[key]
                for key in (
                    "seed",
                    "trials",
                    "workers",
                    "generated",
                    "unique_labelled",
                    "retained_separable_girth_at_least_five",
                    "failures",
                    "minimum_slack",
                    "equalities",
                    "first_failure",
                )
            },
            sort_keys=True,
        )
    )
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
