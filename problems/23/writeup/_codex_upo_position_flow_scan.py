"""Test a position-flow certificate for UNIQUE-PATH OVERLAP.

For a unique bad-edge geodesic P_f, the self row contributes one unit of load
at each path vertex.  The remaining demand at position i is S(P_f[i])-1.
This checker asks whether that demand can be assigned to B-components outside
P_f, where a component may pay position i if its attachment span on P_f covers
i.  Component capacity is its number of outside vertices.
"""
from __future__ import annotations

import argparse
import subprocess
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def outside_components(adj: list[set[int]], side: list[int], path: list[int]) -> list[tuple[int, int, int]]:
    path_set = set(path)
    pos = {v: i for i, v in enumerate(path)}
    seen: set[int] = set()
    comps: list[tuple[int, int, int]] = []
    for start in range(len(adj)):
        if start in path_set or start in seen:
            continue
        q = deque([start])
        seen.add(start)
        verts = []
        attaches = set()
        while q:
            u = q.popleft()
            verts.append(u)
            for v in adj[u]:
                if side[u] == side[v]:
                    continue
                if v in path_set:
                    attaches.add(pos[v])
                elif v not in seen:
                    seen.add(v)
                    q.append(v)
        if attaches:
            comps.append((min(attaches), max(attaches), len(verts)))
    return comps


def maxflow_fraction(demands: list[F], comps: list[tuple[int, int, int]]) -> F:
    active = [(i, d) for i, d in enumerate(demands) if d > 0]
    np = len(active)
    nc = len(comps)
    source = np + nc
    sink = source + 1
    graph = [[] for _ in range(sink + 1)]

    def add(u: int, v: int, cap: F) -> None:
        graph[u].append([v, cap, len(graph[v])])
        graph[v].append([u, F(0), len(graph[u]) - 1])

    total = sum((d for _i, d in active), F(0))
    for node, (_i, d) in enumerate(active):
        add(source, node, d)
    for node, (i, _d) in enumerate(active):
        for j, (lo, hi, _cap) in enumerate(comps):
            if lo <= i <= hi:
                add(node, np + j, total)
    for j, (_lo, _hi, cap) in enumerate(comps):
        add(np + j, sink, F(cap))

    flow = F(0)
    while True:
        parent: list[tuple[int, int] | None] = [None] * len(graph)
        parent[source] = (-1, -1)
        q = deque([source])
        while q and parent[sink] is None:
            u = q.popleft()
            for ei, (v, cap, _rev) in enumerate(graph[u]):
                if cap > 0 and parent[v] is None:
                    parent[v] = (u, ei)
                    q.append(v)
                    if v == sink:
                        break
        if parent[sink] is None:
            return flow
        aug = None
        v = sink
        while v != source:
            u, ei = parent[v]  # type: ignore[misc]
            cap = graph[u][ei][1]
            aug = cap if aug is None or cap < aug else aug
            v = u
        assert aug is not None
        v = sink
        while v != source:
            u, ei = parent[v]  # type: ignore[misc]
            to, cap, rev = graph[u][ei]
            graph[u][ei][1] = cap - aug
            graph[to][rev][1] += aug
            v = u
        flow += aug


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    _adj, cuts = gmins(n, edges)
    checked = 0
    total_demand = F(0)
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, _T, _mu, cyc = st
        S = [F(0) for _ in range(n)]
        for g in M:
            den = len(cyc[g])
            for qpath in cyc[g]:
                for v in qpath:
                    S[v] += F(1, den)
        for f in M:
            if len(cyc[f]) != 1:
                continue
            checked += 1
            path = cyc[f][0]
            demands = [S[v] - 1 for v in path]
            if any(d < 0 for d in demands):
                return {"graphs": 1, "cuts": len(cuts), "checked": checked, "demand": total_demand, "fail": ("negative", g6, ci, side_s, f, path, demands)}
            demand = sum(demands, F(0))
            total_demand += demand
            comps = outside_components(adj, side, path)
            flow = maxflow_fraction(demands, comps)
            if flow != demand:
                return {
                    "graphs": 1,
                    "cuts": len(cuts),
                    "checked": checked,
                    "demand": total_demand,
                    "fail": ("flow", g6, ci, side_s, f, path, demands, comps, flow, demand),
                }
    return {"graphs": 1 if cuts else 0, "cuts": len(cuts), "checked": checked, "demand": total_demand, "fail": None}


def fmt(x):
    return str(x.numerator) if isinstance(x, F) and x.denominator == 1 else str(x)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    acc = {"graphs": 0, "cuts": 0, "checked": 0, "demand": F(0)}
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            iterator = ex.map(graph_probe, graphs, chunksize=args.chunksize)
            for i, res in enumerate(iterator, 1):
                for k in acc:
                    acc[k] += res[k]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
                if i % 10000 == 0:
                    print("processed", i, "checked", acc["checked"], "demand", fmt(acc["demand"]), flush=True)
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            for k in acc:
                acc[k] += res[k]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, {k: (fmt(v) if k == "demand" else v) for k, v in acc.items()})
    print("fail", fail)


if __name__ == "__main__":
    main()
