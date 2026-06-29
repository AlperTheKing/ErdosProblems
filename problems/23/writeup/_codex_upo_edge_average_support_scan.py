"""Check per-bad-edge average overlap versus off-path fan support.

For unique f and another bad edge g, let
  dep_g = average_Q |Q cap P_f|.
  off_g = number of vertices outside P_f used by at least one Q in cyc(g).

Candidate: if g is not wholly nested in P_f (some/off all paths use outside),
then dep_g <= off_g.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

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
    pairs = 0
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
            P = cyc[f][0]
            pset = set(P)
            for g in M:
                if g == f:
                    continue
                den = len(cyc[g])
                dep = F(0)
                off = set()
                wholly_nested = True
                for Q in cyc[g]:
                    qset = set(Q)
                    dep += F(len(qset & pset), den)
                    if not qset <= pset:
                        wholly_nested = False
                    off.update(qset - pset)
                if dep == 0:
                    continue
                pairs += 1
                margin = F(len(off)) - dep
                rec = (margin, repr(g6), ci, side_s, f, P, g, len(cyc[g]), str(dep), len(off), wholly_nested, cyc[g])
                if worst is None or margin < worst[0]:
                    worst = rec
                if not wholly_nested and margin < 0:
                    return {"rows": rows, "pairs": pairs, "worst": worst, "fail": rec}
    return {"rows": rows, "pairs": pairs, "worst": worst, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    rows = pairs = 0
    worst = None
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                rows += res["rows"]
                pairs += res["pairs"]
                if res["worst"] and (worst is None or res["worst"][0] < worst[0]):
                    worst = res["worst"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            rows += res["rows"]
            pairs += res["pairs"]
            if res["worst"] and (worst is None or res["worst"][0] < worst[0]):
                worst = res["worst"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, "rows", rows, "pairs", pairs)
    print("worst", worst)
    print("fail", fail)


if __name__ == "__main__":
    main()
