"""Exact probe for explicit positive ground states of the Hardy matrix H.

For a symmetric Z-matrix H, a positive vector h with Hh >= 0 proves H is PSD
by the ground-state representation.  This script tests simple scale-free
candidates depending only on the load T:

  one       h=1
  cap       h=min(1, N/T) on T>0
  inv       h=N/T on T>0, h=1 on T=0
  cap2      h=min(1, (N/T)^2) on T>0
  inv2      h=(N/T)^2 on T>0, h=1 on T=0

The candidates are exact rational except square-root variants, which are not
included here.  A failure means the candidate cannot be a universal proof.
"""

from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec, Bconn
from _hardy_gate import BETA, build_H, maxcut_ls
from _satzmu_conn import struct_for_side
from _schur_absorption_hall_gate import adj_from_edges
from _stark1 import gmins
from _bdef_construct import Cn, mycielski
from _Klocal_gate import glued_c5_chain
from _wf_deficit_farkas import odd_blowup


def mat_vec(H, h):
    return [sum(row[j] * h[j] for j in range(len(h))) for row in H]


def candidates(T, N):
    out = {"one": [], "cap": [], "inv": [], "cap2": [], "inv2": []}
    for tv in T:
        if tv == 0:
            ratio = F(1)
        else:
            ratio = N / tv
        out["one"].append(F(1))
        out["inv"].append(ratio)
        out["cap"].append(min(F(1), ratio))
        out["inv2"].append(ratio * ratio)
        out["cap2"].append(min(F(1), ratio * ratio))
    return out


def test_cut(name, n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, _mu, cyc = st
    if not M:
        return None
    H = build_H(n, M, ell, T, cyc, BETA)
    N = F(n)
    recs = {}
    for cname, h in candidates(T, N).items():
        vals = mat_vec(H, h)
        mn = min(vals)
        arg = vals.index(mn)
        recs[cname] = (mn, {"name": name, "n": n, "side": "".join(map(str, side)), "v": arg, "T": T[arg], "h": h[arg]})
    return recs


def gfam(name, n, edges):
    adj = adj_from_edges(n, edges)
    try:
        _gamma, cuts = gmins(n, edges)
    except Exception:
        return []
    return [test_cut(name, n, adj, side) for side in cuts]


def worker_g6(g6):
    n, edges = dec(g6)
    return gfam(f"cen{n}", n, edges)


def merge(acc, recs):
    if recs is None:
        return
    for rec in recs:
        if rec is None:
            continue
        acc["cuts"] += 1
        for cname, (mn, payload) in rec.items():
            if mn < 0:
                acc["fail"][cname] = acc["fail"].get(cname, 0) + 1
            if cname not in acc["worst"] or mn < acc["worst"][cname][0]:
                acc["worst"][cname] = (mn, payload)


def run(args):
    acc = {"cuts": 0, "fail": {}, "worst": {}}
    for n in range(args.min_n, args.max_n + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()[:: args.stride]
        if args.workers > 1:
            with ProcessPoolExecutor(max_workers=args.workers) as ex:
                for recs in ex.map(worker_g6, g6s, chunksize=16):
                    merge(acc, recs)
        else:
            for g6 in g6s:
                merge(acc, worker_g6(g6))
        print("census", n, "cuts", acc["cuts"], "fail", acc["fail"], flush=True)

    # A few structured stress cuts without enumerating all cuts.
    grN, grE = mycielski(5, Cn(5))
    for name, n, edges in [("Grotzsch", grN, grE), ("MycGrotzsch", *mycielski(grN, grE))]:
        adj = adj_from_edges(n, edges)
        merge(acc, [test_cut(name, n, adj, maxcut_ls(n, adj))])
    for q in range(2, 12):
        n, edges, side = glued_c5_chain(q)
        merge(acc, [test_cut(f"chain{q}", n, adj_from_edges(n, edges), side)])
    for sizes in [(2, 1, 2, 1, 2), (5, 4, 5, 4, 5), (6, 5, 6, 5, 6)]:
        n, edges = odd_blowup(5, list(sizes))
        # Side pattern used in the C5 guardrail: classes 0,1,3 vs 2,4.
        side = []
        for i, sz in enumerate(sizes):
            side.extend([1 if i in (0, 1, 3) else 0] * sz)
        merge(acc, [test_cut(f"blow{sizes}", n, adj_from_edges(n, edges), side)])

    print("RESULT cuts", acc["cuts"])
    for cname in sorted(acc["worst"]):
        mn, payload = acc["worst"][cname]
        print(cname, "fail", acc["fail"].get(cname, 0), "min", mn, float(mn), payload)


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--workers", type=int, default=1)
    return ap.parse_args()


if __name__ == "__main__":
    run(parse_args())
