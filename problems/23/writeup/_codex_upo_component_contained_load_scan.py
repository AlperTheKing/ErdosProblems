"""Check component-local load for intervals contained in a component span.

For unique P_f and each off-path component C with span [lo,hi], sum the
demands |Q cap P_f|/|cyc(g)| over all g!=f, Q in cyc(g), whose overlap
interval is contained in [lo,hi].  Candidate:

    contained_load(C) <= |C|.

This is stronger/different than the global flow because the same demand may be
counted for several containing components if spans are nested.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

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
    rows = 0
    comps = 0
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
            pos = {v: i for i, v in enumerate(P)}
            infos = component_info(n, adj, side, P)
            loads = [F(0) for _ in infos]
            for g in M:
                if g == f:
                    continue
                den = len(cyc[g])
                for Q in cyc[g]:
                    hits = sorted(pos[v] for v in Q if v in pos)
                    if not hits:
                        continue
                    lo, hi = hits[0], hits[-1]
                    dem = F(len(hits), den)
                    for j, (clo, chi, _cap, _vs, _att) in enumerate(infos):
                        if clo <= lo and hi <= chi:
                            loads[j] += dem
            for j, load in enumerate(loads):
                comps += 1
                cap = F(infos[j][2])
                margin = cap - load
                rec = (margin, repr(g6), ci, side_s, f, P, j, infos[j], str(load), str(cap))
                if worst is None or margin < worst[0]:
                    worst = rec
                if margin < 0:
                    return {"rows": rows, "comps": comps, "worst": worst, "fail": rec}
    return {"rows": rows, "comps": comps, "worst": worst, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    rows = comps = 0
    worst = None
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                rows += res["rows"]
                comps += res["comps"]
                if res["worst"] and (worst is None or res["worst"][0] < worst[0]):
                    worst = res["worst"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            rows += res["rows"]
            comps += res["comps"]
            if res["worst"] and (worst is None or res["worst"][0] < worst[0]):
                worst = res["worst"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, "rows", rows, "comps", comps)
    print("worst", worst)
    print("fail", fail)


if __name__ == "__main__":
    main()
