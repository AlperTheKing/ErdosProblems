#!/usr/bin/env python3
"""Exact simple-unit realization gate for the six-vertex soft-cap core.

The weighted abstract obstruction has two bad edges whose unique shortest
blue rows share a length-three prefix.  Here each bad edge receives a private,
strictly longer blue detour.  The detours are edge-disjoint, so they certify
maximum-cut optimality without changing either shortest-row family.
"""

from __future__ import annotations

import argparse
from collections import deque
from itertools import combinations
import json
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOFTCAP = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate"
for path in (HERE, SOFTCAP):
    sys.path.insert(0, str(path))

from ortools.sat.python import cp_model  # noqa: E402
import global_softcap as soft  # noqa: E402
from exchange_gate import EVALUATION_ORDER, family_relation  # noqa: E402


def edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def build_graph(detour_length: int):
    if detour_length < 6 or detour_length % 2:
        raise ValueError("detour length must be even and at least six")
    blue = {edge(0, 1), edge(1, 2), edge(2, 3), edge(3, 4), edge(3, 5)}
    bad = {edge(0, 4), edge(0, 5)}
    protection = []
    next_vertex = 6
    for target in (4, 5):
        internal = list(range(next_vertex, next_vertex + detour_length - 1))
        next_vertex += detour_length - 1
        path = [0, *internal, target]
        for x, y in zip(path, path[1:]):
            blue.add(edge(x, y))
        protection.append(tuple(path))
    return next_vertex, frozenset(blue), frozenset(bad), tuple(protection)


def adjacency(n: int, edges):
    adj = [[] for _ in range(n)]
    for x, y in edges:
        adj[x].append(y)
        adj[y].append(x)
    for nbrs in adj:
        nbrs.sort()
    return adj


def shortest_rows(n: int, blue, start: int, target: int):
    adj = adjacency(n, blue)
    dist = [-1] * n
    dist[start] = 0
    queue = deque([start])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1
                queue.append(y)
    if dist[target] < 0:
        raise AssertionError("blue graph disconnected across a bad edge")
    rows = []

    def visit(x: int, path: list[int]):
        if x == target:
            rows.append(tuple(path))
            return
        for y in adj[x]:
            if dist[y] == dist[x] + 1 and dist[y] <= dist[target]:
                visit(y, [*path, y])

    visit(start, [start])
    return dist[target], tuple(rows)


def graph_checks(n: int, blue, bad, protection, exhaust_cut: bool):
    all_edges = set(blue) | set(bad)
    adj = adjacency(n, all_edges)
    triangles = []
    for x in range(n):
        for y in adj[x]:
            if x < y:
                common = set(adj[x]) & set(adj[y])
                triangles.extend((x, y, z) for z in sorted(common) if y < z)
    bad_to_path = {edge(path[0], path[-1]): path for path in protection}
    path_edges = []
    for bad_edge in sorted(bad):
        path = bad_to_path[bad_edge]
        items = {edge(x, y) for x, y in zip(path, path[1:])}
        if not items <= set(blue):
            raise AssertionError("protection path leaves blue graph")
        path_edges.append(items)
    protection_disjoint = all(
        not (left & right) for left, right in combinations(path_edges, 2)
    )
    # Every crossing bad edge has a crossing edge on its private blue path;
    # disjoint paths make this injection a max-cut certificate.
    max_cut_certificate = protection_disjoint and set(bad_to_path) == set(bad)
    minimum_sigma = None
    minimum_mask = None
    if exhaust_cut:
        ctx = soft.make_graph_context(n, blue, bad)
        minimum_sigma = 10**9
        for mask in range(1 << (n - 1)):
            value = ctx.sigma(mask)
            if value < minimum_sigma:
                minimum_sigma = value
                minimum_mask = mask
    return {
        "triangleFree": not triangles,
        "triangles": triangles,
        "protectionPathsEdgeDisjoint": protection_disjoint,
        "maximumCutByProtectionPaths": max_cut_certificate,
        "exhaustiveMinimumSigma": minimum_sigma,
        "exhaustiveMinimumMask": minimum_mask,
        "gammaMinimal": max_cut_certificate and not triangles,
    }


def staged_metric(n: int, blue, bad, rows):
    ctx = soft.make_graph_context(n, blue, bad)
    state = soft.reconstruct_state(ctx, rows)
    owners, demand = soft.global_demands(state)
    relation = {}
    stages = []
    for family in EVALUATION_ORDER:
        addition = family_relation(ctx, state, owners, family, "unscoped")
        for base, mask in addition.items():
            relation[base] = relation.get(base, 0) | mask
        flow, assignment = soft.solve_grouped_flow(
            n, owners, demand, relation, state.active_edges
        )
        stages.append(
            {
                "family": family,
                "relationBases": len(relation),
                "flow": flow["maximumFlow"],
                "defect": flow["defect"],
                "shore": flow["minCutSourceOwners"],
                "assignmentSize": len(assignment),
            }
        )
    return {
        "collisionUnits": sum(demand) // 2,
        "demand": sum(demand),
        "selectedVertices": len(state.selected),
        "activeEdges": len(state.active_edges),
        "stages": stages,
    }


def global_c5_payload(n: int, blue, bad, workers: int):
    graph_edges = sorted(set(blue) | set(bad))
    m = len(bad)
    model = cp_model.CpModel()
    in_class = [[model.new_bool_var(f"x_{v}_{i}") for i in range(5)] for v in range(n)]
    for row in in_class:
        model.add(sum(row) == 1)
    # Both bad edges share vertex zero, so global cyclic relabeling permits
    # fixing zero in V0 and the two other endpoints in V4.
    model.add(in_class[0][0] == 1)
    model.add(in_class[4][4] == 1)
    model.add(in_class[5][4] == 1)
    sizes = [model.new_int_var(0, n, f"size_{i}") for i in range(5)]
    for i in range(5):
        model.add(sizes[i] == sum(in_class[v][i] for v in range(n)))
    for i in range(5):
        j = (i + 1) % 5
        product = model.new_int_var(0, n * n, f"product_{i}")
        model.add_multiplication_equality(product, [sizes[i], sizes[j]])
        model.add(product >= m)
        crossing = []
        for index, (u, v) in enumerate(graph_edges):
            uv = model.new_bool_var(f"e_{i}_{index}_uv")
            vu = model.new_bool_var(f"e_{i}_{index}_vu")
            model.add(uv <= in_class[u][i])
            model.add(uv <= in_class[v][j])
            model.add(uv >= in_class[u][i] + in_class[v][j] - 1)
            model.add(vu <= in_class[v][i])
            model.add(vu <= in_class[u][j])
            model.add(vu >= in_class[v][i] + in_class[u][j] - 1)
            crossing.extend((uv, vu))
        model.add(sum(crossing) >= m)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 230053
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": solver.status_name(status), "classes": None}
    classes = [
        [v for v in range(n) if solver.value(in_class[v][i])] for i in range(5)
    ]
    return {"status": solver.status_name(status), "classes": classes}


def evaluate(detour_length: int, workers: int, exhaust_cut: bool):
    n, blue, bad, protection = build_graph(detour_length)
    families = []
    distances = []
    for start, target in sorted(bad):
        distance, rows = shortest_rows(n, blue, start, target)
        distances.append(distance)
        families.append(rows)
    if any(distance != 4 for distance in distances):
        raise AssertionError(distances)
    if any(len(rows) != 1 for rows in families):
        raise AssertionError([len(rows) for rows in families])
    rows = tuple(items[0] for items in families)
    checks = graph_checks(n, blue, bad, protection, exhaust_cut)
    metric = staged_metric(n, blue, bad, rows)
    c5 = global_c5_payload(n, blue, bad, workers)
    return {
        "detourLength": detour_length,
        "n": n,
        "blueEdges": len(blue),
        "badEdges": len(bad),
        "protectionPaths": protection,
        "shortestRows": rows,
        "checks": checks,
        "metric": metric,
        "globalC5": c5,
        "dichotomyPass": metric["stages"][-1]["defect"] == 0 or c5["classes"] is not None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lengths", type=int, nargs="+", default=[6, 8, 10, 12])
    parser.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 1))
    parser.add_argument("--exhaust-cut-length", type=int, default=6)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        parser.error("workers must be in 1..64")
    payload = {
        "schema": "UNIT_DETOUR_SOFTCAP_CORE_V1",
        "arithmetic": "integer cut/path enumeration, Dinic max flow, integer CP-SAT",
        "instances": [
            evaluate(length, args.workers, length == args.exhaust_cut_length)
            for length in args.lengths
        ],
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0 if all(item["dichotomyPass"] for item in payload["instances"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
