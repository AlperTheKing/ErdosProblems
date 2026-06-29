"""Test pathwise overlap bound for bad edges with a unique shortest B-geodesic."""
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


def path_load(cyc, M, P):
    ps = set(P)
    total = F(0)
    for g in M:
        total += sum(len(ps.intersection(Q)) for Q in cyc[g]) / F(len(cyc[g]))
    return total


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
        for f in M:
            if len(cyc[f]) != 1:
                continue
            checked += 1
            P = cyc[f][0]
            val = path_load(cyc, M, P)
            rec = (F(n) - val, g6, ci, side_s, f, P, val)
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
        for i, g in enumerate(graphs, 1):
            res = graph_probe(g)
            acc["graphs"] += res["graphs"]
            acc["cuts"] += res["cuts"]
            acc["checked"] += res["checked"]
            if res["worst"] and (acc["worst"] is None or res["worst"][0] < acc["worst"][0]):
                acc["worst"] = res["worst"]
    print("N", args.n, {k: acc[k] for k in ("graphs", "cuts", "checked")})
    print("worst", [fmt(x) for x in acc["worst"]] if acc["worst"] else None)


if __name__ == "__main__":
    main()
