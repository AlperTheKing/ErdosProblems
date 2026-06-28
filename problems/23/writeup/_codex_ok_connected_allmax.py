"""Check O-K-CONNECTED over all connected maximum cuts.

O-K-CONNECTED: if O={v:T(v)>N} is nonempty, the positive K-support has
exactly one component, where K-components are induced by shortest bad-geodesic
supports.
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import kcomponents, struct_for_side


def build_adj(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def scan_graph(g6):
    n, E = dec(g6)
    adj = build_adj(n, E)
    total = 0
    hist = Counter()
    first_multi = None
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, mu, cyc = st
        O = {v for v, t in enumerate(T) if t > n}
        if not O:
            continue
        total += 1
        comps, find = kcomponents(n, cyc)
        pos = [C for C in comps.values() if any(T[v] > 0 for v in C)]
        hist[len(pos)] += 1
        if len(pos) > 1 and first_multi is None:
            first_multi = {
                "g6": g6,
                "side": tuple(side),
                "O": tuple(sorted(O)),
                "components": tuple(tuple(sorted(C)) for C in pos),
                "T": tuple(str(t) for t in T),
            }
    return g6, total, dict(hist), first_multi


def scan_n(N, workers):
    g6s = subprocess.run([GENG, "-tc", str(N)], capture_output=True, text=True).stdout.split()
    total = 0
    hist = Counter()
    first = None
    if workers > 1:
        ctx = mp.get_context("spawn")
        with ctx.Pool(processes=workers) as pool:
            it = pool.imap_unordered(scan_graph, g6s, chunksize=8)
            for g6, subtotal, subhist, subfirst in it:
                total += subtotal
                hist.update(subhist)
                if subfirst is not None:
                    first = subfirst
                    pool.terminate()
                    break
    else:
        for g6 in g6s:
            _, subtotal, subhist, subfirst = scan_graph(g6)
            total += subtotal
            hist.update(subhist)
            if subfirst is not None:
                first = subfirst
                break
    return total, hist, first


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, default=7)
    ap.add_argument("--nmax", type=int, default=11)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()
    for N in range(args.nmin, args.nmax + 1):
        total, hist, first = scan_n(N, args.workers)
        print(
            f"N={N}: connected-maxcut O-cuts={total} "
            f"positive-K-component-counts={dict(sorted(hist.items()))} "
            f"first_multi={first}",
            flush=True,
        )
        if first is not None:
            break


if __name__ == "__main__":
    main()
