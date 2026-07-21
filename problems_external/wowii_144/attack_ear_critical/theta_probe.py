#!/usr/bin/env python3
"""Exact parameter probe for 2-connected cycle-rank-two (theta) graphs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent


def theta(lengths: tuple[int, int, int]) -> tuple[nx.Graph, list[list[int]]]:
    graph = nx.Graph()
    graph.add_nodes_from([0, 1])
    paths: list[list[int]] = []
    nxt = 2
    for length in lengths:
        path = [0]
        for _ in range(length - 1):
            path.append(nxt)
            nxt += 1
        path.append(1)
        nx.add_path(graph, path)
        paths.append(path)
    return graph, paths


def inv(graph: nx.Graph) -> dict:
    ecc = nx.eccentricity(graph)
    radius = min(ecc.values())
    center = {v for v, value in ecc.items() if value == radius}
    dist = nx.multi_source_shortest_path_length if False else None
    lengths = nx.multi_source_dijkstra_path_length(graph, center)
    eta = max(lengths.values())
    return {"radius": radius, "center": center, "eta": eta}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-length", type=int, default=20)
    parser.add_argument("--output", type=Path, default=HERE / "theta_probe.json")
    args = parser.parse_args()
    totals = {
        "theta": 0,
        "with_bad_internal": 0,
        "shortest_path_has_good": 0,
        "middle_path_has_good": 0,
        "longest_path_has_good": 0,
        "every_path_has_good": 0,
        "some_path_all_bad": 0,
        "failure": 0,
    }
    exceptions: dict[str, list] = {key: [] for key in totals if key not in {"theta"}}
    for a in range(1, args.max_length + 1):
        for b in range(a, args.max_length + 1):
            for c in range(b, args.max_length + 1):
                if a == b == 1 or a + b < 5:
                    continue
                graph, paths = theta((a, b, c))
                if graph.number_of_edges() != a + b + c:
                    continue
                totals["theta"] += 1
                old = inv(graph)
                deltas: list[list[int]] = []
                for path in paths:
                    values = []
                    for v in path[1:-1]:
                        subgraph = graph.copy()
                        subgraph.remove_node(v)
                        values.append(inv(subgraph)["eta"] - old["eta"])
                    deltas.append(values)
                has_good = [any(value >= 0 for value in values) for values in deltas]
                if any(value < 0 for values in deltas for value in values):
                    totals["with_bad_internal"] += 1
                for i, name in enumerate(
                    ("shortest_path_has_good", "middle_path_has_good", "longest_path_has_good")
                ):
                    if has_good[i]:
                        totals[name] += 1
                    elif len(exceptions[name]) < 20:
                        exceptions[name].append({"lengths": [a, b, c], "eta": old["eta"], "deltas": deltas})
                if all(has_good):
                    totals["every_path_has_good"] += 1
                if any(values and all(value < 0 for value in values) for values in deltas):
                    totals["some_path_all_bad"] += 1
                if not any(has_good):
                    totals["failure"] += 1
                    if len(exceptions["failure"]) < 20:
                        exceptions["failure"].append({"lengths": [a, b, c], "eta": old["eta"], "deltas": deltas})
    result = {"max_length": args.max_length, "totals": totals, "exceptions": exceptions}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()
