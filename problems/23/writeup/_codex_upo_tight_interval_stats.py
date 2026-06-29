"""Collect stats for zero-slack interval Hall cases."""
from __future__ import annotations

import argparse
import subprocess
from collections import Counter
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
            infos.append((min(attach), max(attach), len(vertices), tuple(sorted(vertices)), tuple(sorted(attach))))
    return infos


def laminar(intervals):
    for i in range(len(intervals)):
        l1, r1 = intervals[i]
        for j in range(i + 1, len(intervals)):
            l2, r2 = intervals[j]
            if (l1 < l2 < r1 < r2) or (l2 < l1 < r2 < r1):
                return False
    return True


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    ctr = Counter()
    examples = []
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, _T, _mu, cyc = st
        S = [F(0)] * n
        for g in M:
            den = len(cyc[g])
            for qpath in cyc[g]:
                for v in qpath:
                    S[v] += F(1, den)
        for f in M:
            if len(cyc[f]) != 1:
                continue
            path = cyc[f][0]
            pos = {v: i for i, v in enumerate(path)}
            infos = component_info(n, adj, side, path)
            d = [S[v] - 1 for v in path]
            L = len(path)
            for a in range(L):
                lhs = F(0)
                for b in range(a, L):
                    lhs += d[b]
                    cap = sum(F(c) for lo, hi, c, _vs, _att in infos if not (hi < a or b < lo))
                    if cap != lhs:
                        continue
                    ctr[("tight_all",)] += 1
                    if lhs <= 0:
                        continue
                    intervals = []
                    gs = set()
                    qcount = 0
                    for g in M:
                        if g == f:
                            continue
                        den = len(cyc[g])
                        for qpath in cyc[g]:
                            hits = sorted(pos[v] for v in qpath if v in pos and a <= pos[v] <= b)
                            if hits:
                                intervals.append((hits[0], hits[-1]))
                                gs.add(g)
                                qcount += 1
                    ctr[("tight_positive",)] += 1
                    ctr[("qcount", qcount)] += 1
                    ctr[("gcount", len(gs))] += 1
                    ctr[("laminar", laminar(intervals))] += 1
                    if len(examples) < 5:
                        examples.append((g6, ci, side_s, f, path, (a, b), str(lhs), len(gs), qcount, intervals, infos))
    return ctr, examples


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    total = Counter()
    examples = []
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for ctr, exs in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                total.update(ctr)
                if len(examples) < 5:
                    examples.extend(exs[: 5 - len(examples)])
    else:
        for g6 in graphs:
            ctr, exs = graph_probe(g6)
            total.update(ctr)
            if len(examples) < 5:
                examples.extend(exs[: 5 - len(examples)])
    print("N", args.n)
    for k, v in sorted(total.items(), key=lambda kv: str(kv[0])):
        print(k, v)
    print("examples")
    for ex in examples:
        print(ex)


if __name__ == "__main__":
    main()
