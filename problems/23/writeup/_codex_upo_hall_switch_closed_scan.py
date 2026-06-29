"""Test a zero-closed switch proof for UPO Hall.

For Hall subset I, close it by all zero-demand path positions
Z0={i:S(x_i)-1=0}.  Let Y(I) be outside components whose span intersects I.
Test:
  Hall(I) >= lambda(W), W = {x_i: i in I union Z0} union Y(I).
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


def outside_components(adj, side, path):
    pset = set(path)
    pos = {v: i for i, v in enumerate(path)}
    seen = set()
    comps = []
    for s in range(len(adj)):
        if s in pset or s in seen:
            continue
        q = deque([s])
        seen.add(s)
        vs = set()
        att = set()
        while q:
            u = q.popleft()
            vs.add(u)
            for v in adj[u]:
                if side[u] == side[v]:
                    continue
                if v in pset:
                    att.add(pos[v])
                elif v not in seen:
                    seen.add(v)
                    q.append(v)
        if att:
            comps.append((min(att), max(att), vs, att))
    return comps


def switch_slack(adj, side, W):
    W = set(W)
    b = m = 0
    for u in range(len(adj)):
        for v in adj[u]:
            if u < v and ((u in W) != (v in W)):
                if side[u] != side[v]:
                    b += 1
                else:
                    m += 1
    return F(b - m)


def graph_probe(g6):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    rows = sets = 0
    worst = None
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
            rows += 1
            path = cyc[f][0]
            demands = [S[v] - 1 for v in path]
            zero = {i for i, d in enumerate(demands) if d == 0}
            comps = outside_components(adj, side, path)
            for mask in range(1, 1 << len(path)):
                I = [i for i in range(len(path)) if (mask >> i) & 1]
                dem = sum((demands[i] for i in I), F(0))
                if dem == 0:
                    continue
                sets += 1
                yverts = set()
                for lo, hi, verts, _att in comps:
                    if any(lo <= i <= hi for i in I):
                        yverts.update(verts)
                hall = F(len(yverts)) - dem
                closed = set(I) | zero
                W = yverts | {path[i] for i in closed}
                lam = switch_slack(adj, side, W)
                margin = hall - lam
                rec = (margin, hall, lam, g6, ci, side_s, f, path, demands, mask, sorted(closed), sorted(yverts))
                if worst is None or margin < worst[0]:
                    worst = rec
                if margin < 0:
                    return {"graphs": 1, "cuts": len(cuts), "rows": rows, "sets": sets, "worst": worst, "fail": rec}
    return {"graphs": 1 if cuts else 0, "cuts": len(cuts), "rows": rows, "sets": sets, "worst": worst, "fail": None}


def fmt(x):
    return str(x.numerator) if isinstance(x, F) and x.denominator == 1 else str(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    acc = {"graphs": 0, "cuts": 0, "rows": 0, "sets": 0, "worst": None}
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            iterator = ex.map(graph_probe, graphs, chunksize=args.chunksize)
            for i, res in enumerate(iterator, 1):
                for k in ("graphs", "cuts", "rows", "sets"):
                    acc[k] += res[k]
                if res["worst"] and (acc["worst"] is None or res["worst"][0] < acc["worst"][0]):
                    acc["worst"] = res["worst"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
                if i % 10000 == 0:
                    print("processed", i, "rows", acc["rows"], "sets", acc["sets"], "worst", fmt(acc["worst"][0]) if acc["worst"] else None, flush=True)
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            for k in ("graphs", "cuts", "rows", "sets"):
                acc[k] += res[k]
            if res["worst"] and (acc["worst"] is None or res["worst"][0] < acc["worst"][0]):
                acc["worst"] = res["worst"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, {k: v for k, v in acc.items() if k != "worst"})
    print("worst", [fmt(x) if isinstance(x, F) else x for x in acc["worst"]] if acc["worst"] else None)
    print("fail", [fmt(x) if isinstance(x, F) else x for x in fail] if fail else None)


if __name__ == "__main__":
    main()
