"""One-bad-edge island checker for disconnected positive K-support.

Candidate:
If a connected maximum cut has at least two positive K-components, then each
positive K-component contains geodesic support from exactly one bad edge.

If true, DISCONNECTED-K-SELFCAP follows immediately: for a component C with
only bad edge f, T(v)=ell(f) p_f(v) <= ell(f) <= |C|.
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import subprocess

from _h import Bconn, GENG, dec, loads, maxcut_all
from _satzmu_conn import kcomponents, struct_for_side


def build_adj(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def scan_side(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return 0, None
    M, ell, T, mu, cyc = st
    comps, find = kcomponents(n, cyc)
    pos = [C for C in comps.values() if any(T[v] > 0 for v in C)]
    if len(pos) <= 1:
        return 0, None

    bad_edges_by_root = {}
    for f in M:
        root = find(f[0])
        bad_edges_by_root.setdefault(root, []).append(f)

    for C in pos:
        root = find(next(iter(C)))
        bads = bad_edges_by_root.get(root, [])
        if len(bads) != 1:
            return 1, {
                "side": tuple(side),
                "component": tuple(sorted(C)),
                "T_component": tuple(str(T[v]) for v in sorted(C)),
                "bad_edges": tuple(tuple(e) for e in bads),
                "M": tuple(tuple(e) for e in M),
            }
    return 1, None


def scan_graph(g6):
    n, E = dec(g6)
    adj = build_adj(n, E)
    multi_cuts = 0
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        multi, bad = scan_side(n, adj, side)
        multi_cuts += multi
        if bad is not None:
            bad["g6"] = g6
            return g6, multi_cuts, bad
    return g6, multi_cuts, None


def scan_selected(nmin, nmax):
    total_multi = 0
    first = None
    for N in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(N)], capture_output=True, text=True).stdout.split()
        n_multi = 0
        for g6 in g6s:
            n, E = dec(g6)
            info = loads(n, E)
            if info is None:
                continue
            multi, bad = scan_side(info["n"], info["adj"], info["side"])
            n_multi += multi
            if bad is not None and first is None:
                bad["g6"] = g6
                first = bad
        total_multi += n_multi
        print(f"selected N={N}: multi-positive-K cuts={n_multi} first_bad={first}", flush=True)
        if first is not None:
            break
    return total_multi, first


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
    ap.add_argument("--selected", action="store_true")
    args = ap.parse_args()

    if args.selected:
        scan_selected(args.nmin, args.nmax)
        return

    for N in range(args.nmin, args.nmax + 1):
        total, first = scan_n(N, args.workers)
        print(f"N={N}: multi-positive-K connected maxcuts={total} first_bad={first}", flush=True)
        if first is not None:
            break


if __name__ == "__main__":
    main()
