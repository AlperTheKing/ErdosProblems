#!/usr/bin/env python3
"""Independent verifier for the degree--girth audit artifacts."""

from __future__ import annotations

import itertools
import json
import subprocess
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


def exact_girth(graph: nx.Graph) -> int | None:
    answer = None
    for source in graph:
        dist = {source: 0}
        parent = {source: None}
        queue = [source]
        for u in queue:
            for v in graph[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    queue.append(v)
                elif parent[u] != v:
                    candidate = dist[u] + dist[v] + 1
                    answer = candidate if answer is None else min(answer, candidate)
    return answer


def exact_tree_order(graph: nx.Graph) -> int:
    vertices = tuple(graph)
    for deleted_count in range(len(vertices)):
        for deleted in itertools.combinations(vertices, deleted_count):
            remaining = set(vertices).difference(deleted)
            if nx.is_tree(graph.subgraph(remaining)):
                return len(remaining)
    return 1


def center_depth(graph: nx.Graph) -> tuple[int, set[int]]:
    eccentricity = nx.eccentricity(graph)
    radius = min(eccentricity.values())
    center = {v for v, value in eccentricity.items() if value == radius}
    distances = nx.multi_source_dijkstra_path_length(graph, center)
    return max(distances.values()), center


def generated(order: int):
    run = subprocess.Popen([str(GENG), "-ctfq", str(order)], stdout=subprocess.PIPE)
    assert run.stdout is not None
    for line in run.stdout:
        code = line.strip()
        if code:
            yield code.decode(), nx.from_graph6_bytes(code)
    if run.wait() != 0:
        raise RuntimeError("geng failed")


def verify_record(record: dict) -> None:
    graph = nx.from_graph6_bytes(record["graph6"].encode())
    assert graph.number_of_nodes() == record["n"]
    assert graph.number_of_edges() == record["m"]
    assert exact_girth(graph) == record["girth"]
    assert max(dict(graph.degree()).values()) == record["maximum_degree"]
    assert exact_tree_order(graph) == record["tree"]


def main() -> None:
    degree_artifact = json.loads((HERE / "degree_girth_audit.json").read_text())
    conditional_artifact = json.loads((HERE / "conditional_strong_audit.json").read_text())
    verify_record(degree_artifact["first_failure_plus_g_minus_1"])
    verify_record(degree_artifact["first_minimum_slack_plus_g_minus_2"])
    verify_record(conditional_artifact["first_residual"])

    count = strong_failures = conditional = conditional_failures = 0
    minimum = None
    per_order = {}
    for n in range(5, degree_artifact["max_n"] + 1):
        per_order[n] = 0
        for _, graph in generated(n):
            g = exact_girth(graph)
            beta = graph.number_of_edges() - graph.number_of_nodes() + 1
            if g is None or g < 5 or beta < 2 or not nx.is_biconnected(graph):
                continue
            count += 1
            per_order[n] += 1
            delta = max(dict(graph.degree()).values())
            tree = exact_tree_order(graph)
            slack = tree - (delta + g - 2)
            minimum = slack if minimum is None else min(minimum, slack)
            assert slack >= 0
            if tree < delta + g - 1:
                strong_failures += 1
            eta, _ = center_depth(graph)
            diameter = nx.diameter(graph)
            if eta == delta and diameter - g // 2 < eta:
                conditional += 1
                if tree < delta + g - 1:
                    conditional_failures += 1

    assert count == degree_artifact["counts"]["graphs"] == 5644
    assert strong_failures == degree_artifact["counts"]["fails_plus_g_minus_1"] == 4
    assert minimum == degree_artifact["minimum_slack_plus_g_minus_2"] == 0
    assert {str(k): v for k, v in per_order.items()} == degree_artifact["per_order"]
    assert conditional == conditional_artifact["residual_graphs"] == 104
    assert conditional_failures == conditional_artifact["failures"] == 0
    print({
        "verified_graphs": count,
        "minimum_degree_girth_slack": minimum,
        "universal_strong_failures": strong_failures,
        "conditional_residuals": conditional,
        "conditional_strong_failures": conditional_failures,
    })


if __name__ == "__main__":
    main()
