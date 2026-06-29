"""Check whether UPO position-flow Hall minima are attained on intervals."""
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


def min_hall_slacks(demands, comps):
    n = len(demands)
    best_all = None
    best_all_mask = None
    best_int = None
    best_int_pair = None
    for mask in range(1, 1 << n):
        dem = sum((demands[i] for i in range(n) if (mask >> i) & 1), F(0))
        cap = sum(F(c) for lo, hi, c in comps if any((mask >> i) & 1 for i in range(lo, hi + 1)))
        slack = cap - dem
        if best_all is None or slack < best_all:
            best_all = slack
            best_all_mask = mask
    for a in range(n):
        for b in range(a, n):
            dem = sum(demands[a : b + 1], F(0))
            cap = sum(F(c) for lo, hi, c in comps if not (hi < a or b < lo))
            slack = cap - dem
            if best_int is None or slack < best_int:
                best_int = slack
                best_int_pair = (a, b)
    return best_all, best_all_mask, best_int, best_int_pair


def graph_probe(g6):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    checked = 0
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
            checked += 1
            path = cyc[f][0]
            demands = [S[v] - 1 for v in path]
            comps = outside_components(adj, side, path)
            ba, bam, bi, bip = min_hall_slacks(demands, comps)
            rec = (ba, bi, g6, ci, side_s, f, path, demands, comps, bam, bip)
            if worst is None or ba < worst[0]:
                worst = rec
            if ba != bi:
                return {"graphs": 1, "cuts": len(cuts), "checked": checked, "worst": worst, "fail": rec}
    return {"graphs": 1 if cuts else 0, "cuts": len(cuts), "checked": checked, "worst": worst, "fail": None}


def fmt(x):
    return str(x.numerator) if isinstance(x, F) and x.denominator == 1 else str(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    acc = {"graphs": 0, "cuts": 0, "checked": 0, "worst": None}
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            iterator = ex.map(graph_probe, graphs, chunksize=args.chunksize)
            for i, res in enumerate(iterator, 1):
                acc["graphs"] += res["graphs"]
                acc["cuts"] += res["cuts"]
                acc["checked"] += res["checked"]
                if res["worst"] and (acc["worst"] is None or res["worst"][0] < acc["worst"][0]):
                    acc["worst"] = res["worst"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
                if i % 10000 == 0:
                    print("processed", i, "checked", acc["checked"], "worst", fmt(acc["worst"][0]) if acc["worst"] else None, flush=True)
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            acc["graphs"] += res["graphs"]
            acc["cuts"] += res["cuts"]
            acc["checked"] += res["checked"]
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
