"""Test interval-only switch-slack proof for unique-path interval Hall.

For a unique path P and interval I=[a,b], let Y(I) be the union of outside
B-components whose attachment span intersects I.  Let W = {x_i: i in I} union
Y(I).  Candidate:

    |Y(I)| - sum_{i in I}(S(x_i)-1) >= delta_B(W)-delta_M(W).

Since max-cut gives delta_B(W)-delta_M(W) >= 0, this would prove interval Hall.
The earlier switch scanner tested all subsets; this one isolates intervals.
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
    path_set = set(path)
    pos = {v: i for i, v in enumerate(path)}
    seen = set()
    comps = []
    for start in range(len(adj)):
        if start in path_set or start in seen:
            continue
        q = deque([start])
        seen.add(start)
        verts = set()
        attaches = set()
        while q:
            u = q.popleft()
            verts.add(u)
            for v in adj[u]:
                if side[u] == side[v]:
                    continue
                if v in path_set:
                    attaches.add(pos[v])
                elif v not in seen:
                    seen.add(v)
                    q.append(v)
        if attaches:
            comps.append((min(attaches), max(attaches), verts, attaches))
    return comps


def switch_slack(adj, side, W):
    b = m = 0
    W = set(W)
    for u in range(len(adj)):
        for v in adj[u]:
            if u < v and ((u in W) != (v in W)):
                if side[u] != side[v]:
                    b += 1
                else:
                    m += 1
    return F(b - m)


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    rows = intervals = 0
    worst = None
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, _T, _mu, cyc = st
        S = [F(0)] * n
        for g in M:
            den = len(cyc[g])
            seen = {}
            for qpath in cyc[g]:
                for v in qpath:
                    seen[v] = seen.get(v, F(0)) + F(1, den)
            for v, val in seen.items():
                S[v] += val
        for f in M:
            if len(cyc[f]) != 1:
                continue
            rows += 1
            path = cyc[f][0]
            comps = outside_components(adj, side, path)
            d = [S[v] - 1 for v in path]
            L = len(path)
            for a in range(L):
                demand = F(0)
                for b in range(a, L):
                    demand += d[b]
                    if demand == 0:
                        continue
                    intervals += 1
                    yverts = set()
                    for lo, hi, verts, _att in comps:
                        if not (hi < a or b < lo):
                            yverts.update(verts)
                    hall = F(len(yverts)) - demand
                    W = yverts | {path[i] for i in range(a, b + 1)}
                    lam = switch_slack(adj, side, W)
                    margin = hall - lam
                    rec = (margin, hall, lam, repr(g6), ci, side_s, f, path, (a, b), [str(x) for x in d], sorted(yverts))
                    if worst is None or margin < worst[0]:
                        worst = rec
                    if margin < 0:
                        return {"rows": rows, "intervals": intervals, "worst": worst, "fail": rec}
    return {"rows": rows, "intervals": intervals, "worst": worst, "fail": None}


def fmt(x):
    return str(x.numerator) if isinstance(x, F) and x.denominator == 1 else str(x)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    rows = intervals = 0
    worst = None
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                rows += res["rows"]
                intervals += res["intervals"]
                if res["worst"] and (worst is None or res["worst"][0] < worst[0]):
                    worst = res["worst"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            rows += res["rows"]
            intervals += res["intervals"]
            if res["worst"] and (worst is None or res["worst"][0] < worst[0]):
                worst = res["worst"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, "rows", rows, "intervals", intervals)
    print("worst", [fmt(x) if isinstance(x, F) else x for x in worst] if worst else None)
    print("fail", [fmt(x) if isinstance(x, F) else x for x in fail] if fail else None)


if __name__ == "__main__":
    main()
