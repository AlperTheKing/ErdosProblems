"""Scan exact margins for ROWSUM + c*(ell-<p,p>) <= N."""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec
from _stark1 import gmins
from _satzmu_conn import struct_for_side


def pfs_for(info):
    pfs = {}
    S = [F(0) for _ in range(info["n"])]
    for f in info["M"]:
        paths = info["cyc"][f]
        den = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        pf = {v: F(c, den) for v, c in cnt.items()}
        pfs[f] = pf
        for v, x in pf.items():
            S[v] += x
    return pfs, S


def fmt(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def graph_probe(args):
    g6, coeff = args
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    best_ratio = None
    worst_margin = None
    rows = 0
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, mu, cyc = st
        if not M:
            continue
        pfs, S = pfs_for({"n": n, "M": M, "cyc": cyc})
        for f in M:
            rows += 1
            row = sum(x * S[v] for v, x in pfs[f].items())
            self = sum(x * x for x in pfs[f].values())
            dil = F(ell[f]) - self
            gap = F(n) - row
            if dil > 0:
                ratio = gap / dil
                rec = (ratio, g6, ci, side_s, f, row, self, F(ell[f]), gap, dil)
                if best_ratio is None or ratio < best_ratio[0]:
                    best_ratio = rec
            margin = gap - coeff * dil
            recm = (margin, g6, ci, side_s, f, row, self, F(ell[f]), gap, dil)
            if worst_margin is None or margin < worst_margin[0]:
                worst_margin = recm
    return {"graphs": 1 if cuts else 0, "cuts": len(cuts), "rows": rows, "ratio": best_ratio, "margin": worst_margin}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--coeff", default="1/2")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    if "/" in args.coeff:
        a, b = args.coeff.split("/", 1)
        coeff = F(int(a), int(b))
    else:
        coeff = F(args.coeff)
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    acc = {"graphs": 0, "cuts": 0, "rows": 0, "ratio": None, "margin": None}
    items = ((g, coeff) for g in graphs)
    iterator = None
    if args.workers > 1:
        ex = ProcessPoolExecutor(max_workers=args.workers)
        iterator = ex.map(graph_probe, items, chunksize=args.chunksize)
    else:
        ex = None
        iterator = map(graph_probe, items)
    try:
        for i, res in enumerate(iterator, 1):
            acc["graphs"] += res["graphs"]
            acc["cuts"] += res["cuts"]
            acc["rows"] += res["rows"]
            if res["ratio"] and (acc["ratio"] is None or res["ratio"][0] < acc["ratio"][0]):
                acc["ratio"] = res["ratio"]
            if res["margin"] and (acc["margin"] is None or res["margin"][0] < acc["margin"][0]):
                acc["margin"] = res["margin"]
            if i % 5000 == 0:
                print("processed", i, "best_ratio", fmt(acc["ratio"][0]) if acc["ratio"] else None, "worst_margin", fmt(acc["margin"][0]) if acc["margin"] else None, flush=True)
    finally:
        if ex is not None:
            ex.shutdown()
    print("N", args.n, "graphs", acc["graphs"], "cuts", acc["cuts"], "rows", acc["rows"], "coeff", fmt(coeff))
    for name in ("ratio", "margin"):
        rec = acc[name]
        print(name, [fmt(x) for x in rec] if rec else None)


if __name__ == "__main__":
    main()
