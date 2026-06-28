"""Stress explicit layer prices.

Modes:
  power: c[f,i] proportional A[f,i]^theta.
  l5boost: c=(3,3,4,3,3)/16 for L=5 and uniform for other lengths.

Here A[f,i] = sum_{v in layer i of f} p_f(v) S(v).  The price certificate uses
c=1/b with sum_i c[f,i]=1 automatically; it passes a cut if every vertex budget
sum b[f,i] p_f(v) is at most N.

This is a float diagnostic.  Any survivor needs exact rational follow-up.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor

from _h import GENG, dec
from _layerprice import layers_of
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def info_for_side(n, adj, side):
    st = struct_for_side(n, adj, list(side))
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    return {"n": n, "adj": adj, "side": list(side), "M": M, "ell": ell, "T": T, "mu": mu, "cyc": cyc}


def pfs_and_S(info):
    pfs = {}
    S = [0.0] * info["n"]
    for f in info["M"]:
        den = len(info["cyc"][f])
        cnt = {}
        for path in info["cyc"][f]:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        pf = {v: c / den for v, c in cnt.items()}
        pfs[f] = pf
        for v, val in pf.items():
            S[v] += val
    return pfs, S


def c_values(L, A, mode, theta):
    if mode == "l5boost" and L == 5:
        return [3 / 16, 3 / 16, 4 / 16, 3 / 16, 3 / 16]
    if mode == "l5boost":
        return [1 / L] * L
    denom = sum(a**theta for a in A)
    if denom <= 0:
        return None
    return [(a**theta) / denom for a in A]


def max_gap(info, theta, mode):
    n = info["n"]
    pfs, S = pfs_and_S(info)
    budget = [0.0] * n
    for f in info["M"]:
        lay, _, h = layers_of(info, f)
        pf = pfs[f]
        A = [sum(pf[v] * S[v] for v in lay[i]) for i in range(h + 1)]
        c = c_values(h + 1, A, mode, theta)
        if c is None:
            return float("inf")
        for i, a in enumerate(A):
            if c[i] <= 0:
                return float("inf")
            b = 1.0 / c[i]
            for v in lay[i]:
                budget[v] += b * pf[v]
    return max(budget) - n


def graph_probe(args):
    g6, theta, mode = args
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    if not cuts:
        return {"graphs": 0, "cuts": 0, "fails": 0, "worst": -1e100, "witness": None}
    fails = 0
    worst = -1e100
    witness = None
    for side_s in cuts:
        info = info_for_side(n, adj, tuple(int(x) for x in side_s))
        if info is None:
            continue
        gap = max_gap(info, theta, mode)
        if gap > worst:
            worst = gap
            witness = {"g6": g6, "side": side_s, "gap": gap}
        if gap > 1e-8:
            fails += 1
    return {"graphs": 1, "cuts": len(cuts), "fails": fails, "worst": worst, "witness": witness}


def merge(acc, res):
    acc["graphs"] += res["graphs"]
    acc["cuts"] += res["cuts"]
    acc["fails"] += res["fails"]
    if res["witness"] is not None and res["worst"] > acc["worst"]:
        acc["worst"] = res["worst"]
        acc["witness"] = res["witness"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, default=11)
    ap.add_argument("--theta", type=float, default=0.5)
    ap.add_argument("--mode", choices=["power", "l5boost"], default="power")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=128)
    args = ap.parse_args()

    out = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    print(f"generated N={args.n} graphs={len(out)} mode={args.mode} theta={args.theta}", flush=True)
    acc = {"graphs": 0, "cuts": 0, "fails": 0, "worst": -1e100, "witness": None}
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for i, res in enumerate(
                ex.map(graph_probe, ((g, args.theta, args.mode) for g in out), chunksize=args.chunksize),
                1,
            ):
                merge(acc, res)
                if i % 50000 == 0:
                    print(f"processed={i} acc={acc}", flush=True)
    else:
        for i, g6 in enumerate(out, 1):
            merge(acc, graph_probe((g6, args.theta, args.mode)))
            if i % 50000 == 0:
                print(f"processed={i} acc={acc}", flush=True)
    print("=== FINAL ===")
    print(acc)


if __name__ == "__main__":
    main()
