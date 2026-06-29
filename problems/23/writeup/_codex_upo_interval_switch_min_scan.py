"""Compare interval Hall slack with min cut-loss over component switches.

For unique f and interval J on P_f, let H be components whose span hits J.
For every subset Y of H, flip S = J-vertices union vertices(Y).  Compute
Delta=|delta_B(S)|-|delta_M(S)|.  Test whether Hall slack h(J) >= min_Y Delta.
If true, maxcut Delta>=0 would imply interval Hall.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


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
            infos.append((min(attach), max(attach), len(vertices), set(vertices), tuple(sorted(attach))))
    return infos


def delta(edges, side, S: set[int]) -> int:
    db = dm = 0
    for u, v in edges:
        if (u in S) == (v in S):
            continue
        if side[u] != side[v]:
            db += 1
        else:
            dm += 1
    return db - dm


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    rows = 0
    intervals = 0
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, _T, _mu, cyc = st
        Sload = [F(0)] * n
        for g in M:
            den = len(cyc[g])
            for qpath in cyc[g]:
                for v in qpath:
                    Sload[v] += F(1, den)
        for f in M:
            if len(cyc[f]) != 1:
                continue
            rows += 1
            path = cyc[f][0]
            infos = component_info(n, adj, side, path)
            d = [Sload[v] - 1 for v in path]
            L = len(path)
            for a in range(L):
                lhs = F(0)
                base_vertices = set()
                for b in range(a, L):
                    lhs += d[b]
                    base_vertices.add(path[b])
                    hit = [idx for idx, (lo, hi, _cap, _verts, _att) in enumerate(infos) if not (hi < a or b < lo)]
                    cap = sum(F(infos[idx][2]) for idx in hit)
                    h = cap - lhs
                    intervals += 1
                    if len(hit) > 18:
                        continue
                    best = None
                    for mask in range(1 << len(hit)):
                        S = set(base_vertices)
                        for j, idx in enumerate(hit):
                            if (mask >> j) & 1:
                                S |= infos[idx][3]
                        val = delta(edges, side, S)
                        if best is None or val < best:
                            best = val
                    if best is not None and h < best:
                        return {
                            "rows": rows,
                            "intervals": intervals,
                            "fail": (g6, ci, side_s, f, path, (a, b), str(h), best, len(hit), infos),
                        }
    return {"rows": rows, "intervals": intervals, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    acc = {"rows": 0, "intervals": 0}
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
