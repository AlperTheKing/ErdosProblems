"""Pointwise UNIQUE-BASE test.

For a unique row f with path P, define at each path position i:
  uload(i) = number of unique-geodesic contributors g != f whose unique path
             contains x_i;
  cover(i) = number of off-path component spans containing i.

If uload(i) <= cover(i) pointwise, then for every interval I:
  U(I) <= sum_{i in I} cover(i) <= base(I),
where base(I) counts full active span lengths and is at least the cover count
over I.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _codex_upo_conditional_interval_uncross_scan import component_info


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    rows = positions = 0
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
            cover = [sum(1 for lo, hi, _cap, _vs, _att in infos if lo <= i <= hi) for i in range(len(path))]
            uload = [0] * len(path)
            labels = [[] for _ in path]
            for g in M:
                if g == f or len(cyc[g]) != 1:
                    continue
                qpath = cyc[g][0]
                for v in qpath:
                    if v in pos:
                        i = pos[v]
                        uload[i] += 1
                        labels[i].append((g, tuple(qpath)))
            for i, (u, c) in enumerate(zip(uload, cover)):
                positions += 1
                margin = c - u
                rec = (margin, repr(g6), ci, side_s, f, path, i, u, c, infos, labels[i])
                if worst is None or margin < worst[0]:
                    worst = rec
                if margin < 0:
                    return {"rows": rows, "positions": positions, "worst": worst, "fail": rec}
    return {"rows": rows, "positions": positions, "worst": worst, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    rows = positions = 0
    worst = fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                rows += res["rows"]
                positions += res["positions"]
                if res["worst"] and (worst is None or res["worst"][0] < worst[0]):
                    worst = res["worst"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            rows += res["rows"]
            positions += res["positions"]
            if res["worst"] and (worst is None or res["worst"][0] < worst[0]):
                worst = res["worst"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, "rows", rows, "positions", positions)
    print("worst", worst)
    print("fail", fail)


if __name__ == "__main__":
    main()
