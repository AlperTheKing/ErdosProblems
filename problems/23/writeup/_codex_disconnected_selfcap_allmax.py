"""Disconnected positive-K self-cap checker.

Candidate:
If a connected maximum cut has at least two positive K-components, then every
positive K-component C satisfies T(v) <= |C| for all v in C.

This is scale-invariant and implies O-K-CONNECTED: if O is nonempty, no
disconnected positive K-support is possible because T(v)>N>=|C|.
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import subprocess

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
    multi_cuts = 0
    first_bad = None
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, mu, cyc = st
        comps, find = kcomponents(n, cyc)
        pos = [[v for v in C if T[v] > 0] for C in comps.values() if any(T[v] > 0 for v in C)]
        if len(pos) <= 1:
            continue
        multi_cuts += 1
        for C in pos:
            m = len(C)
            for v in C:
                if T[v] > m:
                    first_bad = {
                        "g6": g6,
                        "side": tuple(side),
                        "component": tuple(sorted(C)),
                        "component_size": m,
                        "v": v,
                        "Tv": str(T[v]),
                        "T_component": tuple(str(T[x]) for x in sorted(C)),
                    }
                    return g6, multi_cuts, first_bad
    return g6, multi_cuts, first_bad


def scan_n(N, workers):
    g6s = subprocess.run([GENG, "-tc", str(N)], capture_output=True, text=True).stdout.split()
    total_multi = 0
    first = None
    if workers > 1:
        ctx = mp.get_context("spawn")
        with ctx.Pool(processes=workers) as pool:
            for g6, multi, bad in pool.imap_unordered(scan_graph, g6s, chunksize=8):
                total_multi += multi
                if bad is not None:
                    first = bad
                    pool.terminate()
                    break
    else:
        for g6 in g6s:
            _, multi, bad = scan_graph(g6)
            total_multi += multi
            if bad is not None:
                first = bad
                break
    return total_multi, first


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, default=7)
    ap.add_argument("--nmax", type=int, default=11)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()
    for N in range(args.nmin, args.nmax + 1):
        total, first = scan_n(N, args.workers)
        print(f"N={N}: multi-positive-K connected maxcuts={total} first_bad={first}", flush=True)
        if first is not None:
            break


if __name__ == "__main__":
    main()
