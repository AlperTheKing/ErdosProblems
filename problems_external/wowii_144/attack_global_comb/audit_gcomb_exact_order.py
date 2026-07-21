#!/usr/bin/env python3
"""Exact nauty audit of the global W144-GCOMB parameter cover at one order."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from collections import Counter
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


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


def record(code: bytes, graph: nx.Graph, girth: int) -> dict[str, object]:
    n = graph.number_of_nodes()
    beta = graph.number_of_edges() - n + 1
    eccentricity = nx.eccentricity(graph)
    radius = min(eccentricity.values())
    center = {v for v, value in eccentricity.items() if value == radius}
    eta = max(nx.multi_source_dijkstra_path_length(graph, center).values())
    diameter = max(eccentricity.values())
    maximum_degree = max(dict(graph.degree()).values())
    articulations = sorted(nx.articulation_points(graph))
    is_cycle = all(degree == 2 for _, degree in graph.degree())
    kappa = int(not articulations and not is_cycle)
    terms = {
        "degree": maximum_degree - 2 + kappa,
        "diameter": diameter - math.floor(girth / 2),
        "order_rank": n - girth - beta + 1,
    }
    rhs = max(terms.values())
    return {
        "graph6": code.decode("ascii"),
        "n": n,
        "m": graph.number_of_edges(),
        "girth": girth,
        "beta": beta,
        "diameter": diameter,
        "radius": radius,
        "maximum_degree": maximum_degree,
        "center": sorted(center),
        "eta": eta,
        "kappa": kappa,
        "terms": terms,
        "rhs": rhs,
        "slack": rhs - eta,
        "articulations": articulations,
        "tight_terms": sorted(key for key, value in terms.items() if value == eta),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--order", type=int, default=14)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "gcomb_exact_order14_results.json",
    )
    args = parser.parse_args()
    process = subprocess.Popen(
        [str(GENG), "-ctfq", str(args.order)],
        stdout=subprocess.PIPE,
        text=False,
    )
    assert process.stdout is not None

    generated = 0
    retained = 0
    minimum_slack: int | None = None
    failures: list[dict[str, object]] = []
    equalities: list[dict[str, object]] = []
    cut_equalities: list[dict[str, object]] = []
    equality_types: Counter[str] = Counter()
    equality_tight_terms: Counter[str] = Counter()
    for line in process.stdout:
        code = line.strip()
        if not code:
            continue
        generated += 1
        graph = nx.from_graph6_bytes(code)
        girth = exact_girth(graph)
        if girth is None or girth < 5:
            continue
        retained += 1
        data = record(code, graph, girth)
        slack = int(data["slack"])
        minimum_slack = slack if minimum_slack is None else min(minimum_slack, slack)
        if slack < 0:
            failures.append(data)
        if slack == 0:
            equalities.append(data)
            is_cut = bool(data["articulations"])
            if is_cut:
                cut_equalities.append(data)
            beta = int(data["beta"])
            equality_types[
                ("cut" if is_cut else "2connected")
                + ("-unicyclic" if beta == 1 else "-multicyclic")
            ] += 1
            equality_tight_terms["+".join(data["tight_terms"])] += 1
    if process.wait() != 0:
        raise RuntimeError("geng failed")

    result = {
        "command": [str(GENG), "-ctfq", str(args.order)],
        "order": args.order,
        "generated_connected_triangle_C4_free": generated,
        "retained_connected_cyclic_girth_at_least_five": retained,
        "failures": len(failures),
        "minimum_slack": minimum_slack,
        "equalities": len(equalities),
        "cut_equalities": len(cut_equalities),
        "equality_types": dict(sorted(equality_types.items())),
        "equality_tight_terms": dict(sorted(equality_tight_terms.items())),
        "failure_records": failures,
        "equality_records": equalities,
        "cut_equality_records": cut_equalities,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "order",
                    "generated_connected_triangle_C4_free",
                    "retained_connected_cyclic_girth_at_least_five",
                    "failures",
                    "minimum_slack",
                    "equalities",
                    "cut_equalities",
                    "equality_types",
                    "equality_tight_terms",
                )
            },
            sort_keys=True,
        )
    )
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
