"""Check restricted flow for each target interval [a,b].

For unique f and target interval J=[a,b], each Q in cyc(g), g!=f, contributes
|Q cap J|/|cyc(g)|.  It may route to components whose span intersects J.
This is equivalent to interval Hall but keeps the geodesic-node structure.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from collections import deque

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


class Flow:
    def __init__(self, n: int):
        self.g = [[] for _ in range(n)]

    def add(self, u: int, v: int, c: F) -> None:
        self.g[u].append([v, c, len(self.g[v])])
        self.g[v].append([u, F(0), len(self.g[u]) - 1])

    def maxflow(self, s: int, t: int) -> F:
        flow = F(0)
        while True:
            par = [None] * len(self.g)
            par[s] = (-1, -1)
            q = deque([s])
            while q and par[t] is None:
                u = q.popleft()
                for i, (v, c, _r) in enumerate(self.g[u]):
                    if c > 0 and par[v] is None:
                        par[v] = (u, i)
                        q.append(v)
            if par[t] is None:
                return flow
            aug = None
            v = t
            while v != s:
                u, i = par[v]
                c = self.g[u][i][1]
                aug = c if aug is None or c < aug else aug
                v = u
            assert aug is not None
            v = t
            while v != s:
                u, i = par[v]
                rev = self.g[u][i][2]
                self.g[u][i][1] -= aug
                self.g[v][rev][1] += aug
                v = u
            flow += aug


def component_info(n: int, adj, side, path: list[int]):
    pset = set(path)
    pos = {v: i for i, v in enumerate(path)}
    rest = [v for v in range(n) if v not in pset]
    parent = {v: v for v in rest}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for u in rest:
        for v in adj[u]:
            if v in pset:
                continue
            if side[u] != side[v]:
                union(u, v)
    comps: dict[int, list[int]] = {}
    for v in rest:
        comps.setdefault(find(v), []).append(v)
    infos = []
    for vertices in comps.values():
        attach = set()
        for u in vertices:
            for x in adj[u]:
                if x in pset and side[u] != side[x]:
                    attach.add(pos[x])
        if attach:
            infos.append((min(attach), max(attach), len(vertices), tuple(sorted(vertices)), tuple(sorted(attach))))
    return infos


def hit_count(path: list[int], qpath: list[int], a: int, b: int) -> int:
    pos = {v: i for i, v in enumerate(path)}
    return sum(1 for v in qpath if v in pos and a <= pos[v] <= b)


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for x, y in edges:
        adj[x].add(y)
        adj[y].add(x)
    _adj, cuts = gmins(n, edges)
    rows = 0
    targets = 0
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
            L = len(path)
            infos = component_info(n, adj, side, path)
            for a in range(L):
                for b in range(a, L):
                    demands = []
                    for g in M:
                        if g == f:
                            continue
                        den = len(cyc[g])
                        for qpath in cyc[g]:
                            cnt = hit_count(path, qpath, a, b)
                            if cnt:
                                demands.append((F(cnt, den), g, qpath))
                    targets += 1
                    if not demands:
                        continue
                    hit_comps = [j for j, (lo, hi, _c, _vs, _att) in enumerate(infos) if not (hi < a or b < lo)]
                    source = 0
                    dem_base = 1
                    comp_base = dem_base + len(demands)
                    sink = comp_base + len(hit_comps)
                    fl = Flow(sink + 1)
                    total = F(0)
                    for i, (dem, _g, _qpath) in enumerate(demands):
                        total += dem
                        fl.add(source, dem_base + i, dem)
                        for jj in range(len(hit_comps)):
                            fl.add(dem_base + i, comp_base + jj, total + 1)
                    for jj, comp_index in enumerate(hit_comps):
                        fl.add(comp_base + jj, sink, F(infos[comp_index][2]))
                    value = fl.maxflow(source, sink)
                    if value != total:
                        return {
                            "rows": rows,
                            "targets": targets,
                            "fail": (g6, ci, side_s, f, path, (a, b), str(total), str(value), demands, infos),
                        }
    return {"rows": rows, "targets": targets, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    acc = {"rows": 0, "targets": 0}
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                for k in acc:
                    acc[k] += res[k]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            for k in acc:
                acc[k] += res[k]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, acc)
    print("fail", fail)


if __name__ == "__main__":
    main()
