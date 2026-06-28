"""All-gamma-min-cut probe for fractional symmetric layer splits.

For a bad edge f, define B_t = OUT_t - 2t*N/L and r = ROWSUM(f)-N.
An integer split needs some t with r <= B_t <= 0.

A fractional split allows convex averaging between shell splits, so it only
needs the scalar interval [min_t B_t, max_t B_t] to meet [r,0].  Equivalently:

    min_t B_t <= 0,   max_t B_t >= r,   r <= 0.

This still yields ROWSUM-O by averaging the corresponding OUT/CEN
inequalities, but it repairs tie-cut cases where integer B_t jumps over the
valid interval.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _codex_layer_split_allcuts import graph_probe as integer_graph_probe
from _codex_layer_split_allcuts import struct_for_side, bdist_layers
from _h import GENG, Bconn, bdist_restr, dec, maxcut_all


def fractional_check(info, support12=False):
    n = info["n"]
    pfs = {}
    S = [F(0) for _ in range(n)]
    for f in info["M"]:
        paths = info["cyc"][f]
        nf = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        pf = {v: F(c, nf) for v, c in cnt.items()}
        pfs[f] = pf
        for v, x in pf.items():
            S[v] += x

    for f in info["M"]:
        L = info["ell"][f]
        dist = bdist_layers(info["adj"], info["side"], f[0])
        layers = [[] for _ in range(L)]
        for v in pfs[f]:
            layers[dist[v]].append(v)
        A = [sum(pfs[f][v] * S[v] for v in layers[i]) for i in range(L)]
        row = sum(A)
        r = row - n
        bvals = []
        max_t = min(2, L // 2) if support12 else L // 2
        for t in range(1, max_t + 1):
            outer = sum(A[:t]) + sum(A[L - t :])
            bvals.append(outer - F(2 * t * n, L))
        if r > 0 or min(bvals) > 0 or max(bvals) < r:
            return False, (f, L, tuple(A), row, r, tuple(bvals))
    return True, None


def graph_probe(job):
    g6, support12 = job
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    candidates = []
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
        if not M:
            continue
        G = 0
        ok = True
        for u, v in M:
            d = bdist_restr(adj, side, u, v)
            if d < 0:
                ok = False
                break
            G += (d + 1) * (d + 1)
        if ok:
            candidates.append((side, G))
    if not candidates:
        return None
    gmin = min(G for _, G in candidates)
    checked = 0
    int_fail = 0
    for side, G in candidates:
        if G != gmin:
            continue
        info = struct_for_side(n, adj, side)
        if info is None:
            continue
        checked += 1
        ok, data = fractional_check(info, support12=support12)
        if not ok:
            return {"graphs": 1, "cuts": checked, "frac_fail": (g6, "".join(map(str, side)), data), "int_fail": int_fail}
    # Reuse integer probe only as a count marker for this graph.
    ires = integer_graph_probe(g6)
    if ires and ires["fail"] is not None:
        int_fail = 1
    return {"graphs": 1, "cuts": checked, "frac_fail": None, "int_fail": int_fail}


def merge(acc, res):
    if res is None:
        return
    acc["graphs"] += res["graphs"]
    acc["cuts"] += res["cuts"]
    acc["int_fail_graphs"] += res["int_fail"]
    if res["frac_fail"] is not None and acc["first_frac_fail"] is None:
        acc["first_frac_fail"] = res["frac_fail"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--max-n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--support12", action="store_true")
    args = ap.parse_args()
    acc = {"graphs": 0, "cuts": 0, "int_fail_graphs": 0, "first_frac_fail": None}
    for nn in range(5, args.max_n + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        if args.workers > 1:
            with ProcessPoolExecutor(max_workers=args.workers) as ex:
                for res in ex.map(graph_probe, [(g6, args.support12) for g6 in out], chunksize=16):
                    merge(acc, res)
        else:
            for g6 in out:
                merge(acc, graph_probe((g6, args.support12)))
        print(f"N<={nn}: {acc}", flush=True)
    print("=== FINAL ===")
    print(acc)


if __name__ == "__main__":
    main()
