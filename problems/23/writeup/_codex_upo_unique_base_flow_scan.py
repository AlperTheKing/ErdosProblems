"""Flow version of UNIQUE-BASE for unique-path UPO.

For a unique row f, create demand nodes for each g != f with len(cyc[g])=1 and
Q cap P_f nonempty, demand = |Q cap P_f|.  Component capacities are only their
span lengths hi-lo+1, not full |C|.  A demand can route to a component whose
span intersects its overlap interval.

Feasibility implies the scalar UNIQUE-BASE interval inequalities.
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
from _codex_upo_conditional_interval_uncross_scan import component_info


def maxflow(demands, caps, edges):
    nd, nc = len(demands), len(caps)
    n = 2 + nd + nc
    src, sink = 0, 1
    cap = [[F(0) for _ in range(n)] for _ in range(n)]
    total = sum(demands, F(0))
    for i, d in enumerate(demands):
        cap[src][2 + i] = d
    for j, c in enumerate(caps):
        cap[2 + nd + j][sink] = c
    big = total + 1
    for i, j in edges:
        cap[2 + i][2 + nd + j] = big
    flow = F(0)
    while True:
        par = [-1] * n
        par[src] = src
        q = deque([src])
        while q and par[sink] == -1:
            u = q.popleft()
            for v in range(n):
                if par[v] == -1 and cap[u][v] > 0:
                    par[v] = u
                    q.append(v)
                    if v == sink:
                        break
        if par[sink] == -1:
            break
        v = sink
        b = None
        while v != src:
            u = par[v]
            b = cap[u][v] if b is None else min(b, cap[u][v])
            v = u
        v = sink
        while v != src:
            u = par[v]
            cap[u][v] -= b
            cap[v][u] += b
            v = u
        flow += b
    return flow, total


def graph_probe(g6: str):
    n, edges0 = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges0:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges0)
    rows = demand_nodes = 0
    worst = None
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, _T, _mu, cyc = st
        for f in M:
            if len(cyc[f]) != 1:
                continue
            rows += 1
            path = cyc[f][0]
            pos = {v: i for i, v in enumerate(path)}
            infos = component_info(n, adj, side, path)
            caps = [F(hi - lo + 1) for lo, hi, _cap, _vs, _att in infos]
            demands = []
            intervals = []
            labels = []
            for g in M:
                if g == f or len(cyc[g]) != 1:
                    continue
                qpath = cyc[g][0]
                hits = sorted(pos[v] for v in qpath if v in pos)
                if not hits:
                    continue
                demands.append(F(len(hits)))
                intervals.append((hits[0], hits[-1]))
                labels.append((g, tuple(qpath), tuple(hits)))
            if not demands:
                continue
            demand_nodes += len(demands)
            edges = []
            for i, (a, b) in enumerate(intervals):
                for j, (lo, hi, _cap, _vs, _att) in enumerate(infos):
                    if not (hi < a or b < lo):
                        edges.append((i, j))
            flow, total = maxflow(demands, caps, edges)
            margin = sum(caps, F(0)) - total
            rec = (total - flow, margin, repr(g6), ci, side_s, f, path, [str(d) for d in demands], intervals, infos, labels)
            if worst is None or rec[0] > worst[0]:
                worst = rec
            if flow != total:
                return {"rows": rows, "demand_nodes": demand_nodes, "worst": worst, "fail": rec}
    return {"rows": rows, "demand_nodes": demand_nodes, "worst": worst, "fail": None}


def clean(rec):
    if rec is None:
        return None
    return [str(x) if isinstance(x, F) else x for x in rec]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    rows = demand_nodes = 0
    worst = fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                rows += res["rows"]
                demand_nodes += res["demand_nodes"]
                if res["worst"] and (worst is None or res["worst"][0] > worst[0]):
                    worst = res["worst"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            rows += res["rows"]
            demand_nodes += res["demand_nodes"]
            if res["worst"] and (worst is None or res["worst"][0] > worst[0]):
                worst = res["worst"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, "rows", rows, "demand_nodes", demand_nodes)
    print("worst", clean(worst))
    print("fail", clean(fail))


if __name__ == "__main__":
    main()
