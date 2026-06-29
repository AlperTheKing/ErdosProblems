"""Test a component-span flow certificate for UNIQUE-PATH OVERLAP.

For a bad edge f with a unique shortest B-geodesic P, the self contribution
uses one unit of capacity at each vertex of P.  Every other shortest geodesic
Q contributes a contiguous interval I=Q cap P.  This checker asks whether the
remaining interval demand can be fractionally assigned to B-components outside
P.  An outside component C may pay for I if I is contained in the attachment
span of C on P.

If feasible, the row obeys UPO by |P| + outside capacity <= N.
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


def interval_on(path: list[int], other: list[int]) -> tuple[int, int] | None:
    pos = {v: i for i, v in enumerate(path)}
    hits = sorted(pos[v] for v in other if v in pos)
    if not hits:
        return None
    if hits[-1] - hits[0] + 1 != len(hits):
        return None
    return hits[0], hits[-1]


def outside_components(
    adj: list[set[int]],
    side: list[int],
    path: list[int],
) -> list[tuple[int, int, int]]:
    path_set = set(path)
    pos = {v: i for i, v in enumerate(path)}
    outside = [v for v in range(len(adj)) if v not in path_set]
    seen: set[int] = set()
    comps: list[tuple[int, int, int]] = []
    for start in outside:
        if start in seen:
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


def maxflow_fraction(intervals: dict[tuple[int, int], F], comps: list[tuple[int, int, int]]) -> F:
    """Ford-Fulkerson over a tiny bipartite network with Fraction capacities."""
    interval_keys = list(intervals)
    ni = len(interval_keys)
    nc = len(comps)
    source = ni + nc
    sink = source + 1
    graph = [[] for _ in range(sink + 1)]

    def add(u: int, v: int, cap: F) -> None:
        graph[u].append([v, cap, len(graph[v])])
        graph[v].append([u, F(0), len(graph[u]) - 1])

    total = F(0)
    for i, key in enumerate(interval_keys):
        cap = intervals[key]
        total += cap
        add(source, i, cap)
    inf = total
    for i, (a, b) in enumerate(interval_keys):
        for j, (lo, hi, _cap) in enumerate(comps):
            if lo <= a and b <= hi:
                add(i, ni + j, inf)
    for j, (_lo, _hi, cap) in enumerate(comps):
        add(ni + j, sink, F(cap))

    flow = F(0)
    while True:
        parent: list[tuple[int, int] | None] = [None] * len(graph)
        q = deque([source])
        parent[source] = (-1, -1)
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
        for f in M:
            if len(cyc[f]) != 1:
                continue
            checked += 1
            path = cyc[f][0]
            intervals: dict[tuple[int, int], F] = {}
            for g in M:
                for qpath in cyc[g]:
                    if g == f and qpath == path:
                        continue
                    ij = interval_on(path, qpath)
                    if ij is None:
                        return {"graphs": 1, "cuts": len(cuts), "checked": checked, "demand": total_demand, "fail": ("noncontig", g6, ci, side_s, f, path, g, qpath)}
                    i, j = ij
                    intervals[(i, j)] = intervals.get((i, j), F(0)) + F(j - i + 1, len(cyc[g]))
            demand = sum(intervals.values(), F(0))
            total_demand += demand
            comps = outside_components(adj, side, path)
            flow = maxflow_fraction(intervals, comps)
            if flow != demand:
                return {
                    "graphs": 1,
                    "cuts": len(cuts),
                    "checked": checked,
                    "demand": total_demand,
                    "fail": ("flow", g6, ci, side_s, f, path, intervals, comps, flow, demand),
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
