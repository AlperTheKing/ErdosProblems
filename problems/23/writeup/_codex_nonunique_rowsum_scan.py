"""Scan ROWSUM margins for bad edges with multiple shortest B-geodesics."""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec
from _stark1 import gmins
from _satzmu_conn import struct_for_side


def fmt(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def pf_for(cyc, f):
    den = len(cyc[f])
    cnt = {}
    for P in cyc[f]:
        for v in P:
            cnt[v] = cnt.get(v, 0) + 1
    return {v: F(c, den) for v, c in cnt.items()}


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
        st = struct_for_side(n, adj, [int(c) for c in side_s])
        if st is None:
            continue
        M, ell, T, mu, cyc = st
        pfs = {g: pf_for(cyc, g) for g in M}
        S = [F(0) for _ in range(n)]
        for pf in pfs.values():
            for v, x in pf.items():
                S[v] += x
        for f in M:
            if len(cyc[f]) <= 1:
                continue
            checked += 1
            row = sum(pfs[f][v] * S[v] for v in pfs[f])
            rec = (F(n) - row, g6, ci, side_s, f, len(cyc[f]), row, F(ell[f]))
            if worst is None or rec[0] < worst[0]:
                worst = rec
    return {"graphs": 1 if cuts else 0, "cuts": len(cuts), "checked": checked, "worst": worst}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    acc = {"graphs": 0, "cuts": 0, "checked": 0, "worst": None}
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            iterator = ex.map(graph_probe, graphs, chunksize=args.chunksize)
            for i, res in enumerate(iterator, 1):
                acc["graphs"] += res["graphs"]
                acc["cuts"] += res["cuts"]
                acc["checked"] += res["checked"]
                if res["worst"] and (acc["worst"] is None or res["worst"][0] < acc["worst"][0]):
                    acc["worst"] = res["worst"]
                if i % 10000 == 0:
                    print("processed", i, "checked", acc["checked"], "worst_margin", fmt(acc["worst"][0]) if acc["worst"] else None, flush=True)
    else:
        for res in map(graph_probe, graphs):
            acc["graphs"] += res["graphs"]
            acc["cuts"] += res["cuts"]
            acc["checked"] += res["checked"]
            if res["worst"] and (acc["worst"] is None or res["worst"][0] < acc["worst"][0]):
                acc["worst"] = res["worst"]
    print("N", args.n, {k: acc[k] for k in ("graphs", "cuts", "checked")})
    print("worst", [fmt(x) for x in acc["worst"]] if acc["worst"] else None)


if __name__ == "__main__":
    main()
