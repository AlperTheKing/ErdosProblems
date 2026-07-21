#!/usr/bin/env python3
"""Exact audit of the unicyclic W144 capacity identity and center bound."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[3]
GENG = ROOT / "tools" / "nauty2_8_9" / "geng.exe"


def graph6(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(G, header=False).decode().strip()


def unique_cycle(G: nx.Graph) -> list[int]:
    cycles = nx.cycle_basis(G)
    assert len(cycles) == 1
    return cycles[0]


def branch_weights(G: nx.Graph, cycle: list[int]) -> dict[int, int]:
    K = set(cycle)
    weights = {z: 0 for z in cycle}
    H = G.subgraph(set(G) - K)
    for comp in nx.connected_components(H):
        roots = []
        for x in comp:
            roots.extend(y for y in G[x] if y in K)
        assert len(roots) == 1
        weights[roots[0]] += len(comp)
    return weights


def center_distance(G: nx.Graph) -> tuple[int, set[int]]:
    ecc = nx.eccentricity(G)
    radius = min(ecc.values())
    center = {v for v, value in ecc.items() if value == radius}
    distances = nx.multi_source_dijkstra_path_length(G, center)
    return max(distances.values()), center


def exact_m(G: nx.Graph, cycle: list[int]) -> int:
    K = set(cycle)
    outside = sorted(set(G) - K)
    best = 0
    for mask in range(1 << len(outside)):
        F = {outside[i] for i in range(len(outside)) if mask >> i & 1}
        if len(F) <= best or not nx.is_forest(G.subgraph(F)):
            continue
        comps = list(nx.connected_components(G.subgraph(F)))
        for z in cycle:
            if all(sum(1 for x in comp for y in G[x] if y in K and y != z) == 1
                   for comp in comps):
                best = len(F)
                break
    return best


def graphs_of_order(n: int):
    proc = subprocess.run(
        [str(GENG), "-cq", str(n), f"{n}:{n}"],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in proc.stdout.splitlines():
        if line:
            yield nx.from_graph6_bytes(line.encode())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=11)
    parser.add_argument("--exact-m-n", type=int, default=10)
    args = parser.parse_args()

    total = 0
    exact_total = 0
    min_slack = None
    tight = None
    max_e_minus_q = None
    for n in range(3, args.max_n + 1):
        order_count = 0
        for G in graphs_of_order(n):
            if G.number_of_edges() != n:
                continue
            cycle = unique_cycle(G)
            weights = branch_weights(G, cycle)
            q = n - len(cycle)
            formula = q - min(weights.values())
            e, center = center_distance(G)
            slack = formula - e
            if slack < 0:
                raise AssertionError(
                    (graph6(G), n, len(cycle), e, formula, weights, sorted(center))
                )
            if n <= args.exact_m_n:
                m_value = exact_m(G, cycle)
                exact_total += 1
                if m_value != formula:
                    raise AssertionError(
                        ("M identity", graph6(G), m_value, formula, weights)
                    )
            total += 1
            order_count += 1
            if min_slack is None or slack < min_slack:
                min_slack = slack
                tight = (graph6(G), n, len(cycle), e, formula, weights, sorted(center))
            delta = e - q
            if max_e_minus_q is None or delta > max_e_minus_q[0]:
                max_e_minus_q = (delta, graph6(G), n, len(cycle), e, q,
                                 weights, sorted(center))
        print(f"n={n}: {order_count}")
    print({
        "graphs": total,
        "exact_m_graphs": exact_total,
        "min_slack": min_slack,
        "tight": tight,
        "max_e_minus_q": max_e_minus_q,
    })


if __name__ == "__main__":
    main()
