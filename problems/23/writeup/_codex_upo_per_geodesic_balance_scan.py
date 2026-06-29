"""Measure per-geodesic overlap against off-path vertices for unique P_f."""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    rows = 0
    qcount = 0
    worst_all = None
    worst_nonnested = None
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
            P = cyc[f][0]
            pset = set(P)
            for g in M:
                if g == f:
                    continue
                for Q in cyc[g]:
                    hits = [v for v in Q if v in pset]
                    if not hits:
                        continue
                    qcount += 1
                    off = len([v for v in Q if v not in pset])
                    diff = len(hits) - off
                    rec = (diff, repr(g6), ci, side_s, f, P, g, Q, len(hits), off)
                    if worst_all is None or diff > worst_all[0]:
                        worst_all = rec
                    if off > 0 and (worst_nonnested is None or diff > worst_nonnested[0]):
                        worst_nonnested = rec
    return {"rows": rows, "qcount": qcount, "worst_all": worst_all, "worst_nonnested": worst_nonnested}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    rows = 0
    qcount = 0
    worst_all = None
    worst_nonnested = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                rows += res["rows"]
                qcount += res["qcount"]
                if res["worst_all"] and (worst_all is None or res["worst_all"][0] > worst_all[0]):
                    worst_all = res["worst_all"]
                if res["worst_nonnested"] and (
                    worst_nonnested is None or res["worst_nonnested"][0] > worst_nonnested[0]
                ):
                    worst_nonnested = res["worst_nonnested"]
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            rows += res["rows"]
            qcount += res["qcount"]
            if res["worst_all"] and (worst_all is None or res["worst_all"][0] > worst_all[0]):
                worst_all = res["worst_all"]
            if res["worst_nonnested"] and (
                worst_nonnested is None or res["worst_nonnested"][0] > worst_nonnested[0]
            ):
                worst_nonnested = res["worst_nonnested"]
    print("N", args.n, "rows", rows, "qcount", qcount)
    print("worst_all", worst_all)
    print("worst_nonnested", worst_nonnested)


if __name__ == "__main__":
    main()
