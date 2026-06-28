"""Stress a saturation-qualified component-deficit cut.

Candidate.  For a gamma-min connected-B max cut with O={T>N}, let C be a
positive K-component disjoint from O.  Define

    deficit(C) = N*|C| - sum_{v in C} T(v).

Then deficit(C) is at least the number of B-boundary edges whose endpoint in C
is saturated (T=N).

This is weaker than the false self-cap statement and is saturation-qualified:
it would rule out a saturated Q-only K-component because such a component has
deficit 0 but, with O nonempty and B connected, has a B-boundary edge.
"""

from __future__ import annotations

import argparse
import multiprocessing as mp
import subprocess
from fractions import Fraction as F

from _codex_direct_overload import build_adj, gamma_min_sides, named_cases
from _cond1_proof import build_K
from _h import Bconn, GENG, bdist_restr, dec, maxcut_all
from _split_satzmu import battery


def k_components(K, n):
    seen = [False] * n
    comps = []
    for s in range(n):
        if seen[s] or all(K[s][v] == 0 for v in range(n)):
            continue
        stack = [s]
        seen[s] = True
        comp = []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in range(n):
                if not seen[v] and K[u][v] > 0:
                    seen[v] = True
                    stack.append(v)
        comps.append(sorted(comp))
    return comps


def struct_for_side(n, adj, side):
    from _satzmu_conn import struct_for_side as base_struct

    st = base_struct(n, adj, side)
    if st is None:
        return None
    M, ell, _T, _mu, cyc = st
    bset = set()
    for u in range(n):
        for v in adj[u]:
            if u < v and side[u] != side[v]:
                bset.add((u, v))
    return {"n": n, "adj": adj, "side": side, "Bset": bset, "M": M, "ell": ell, "cyc": cyc}


def gamma_min_connected_sides(n, adj):
    cand = []
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        gamma = 0
        ok = True
        for u in range(n):
            for v in adj[u]:
                if u < v and side[u] == side[v]:
                    d = bdist_restr(adj, side, u, v)
                    if d < 0:
                        ok = False
                        break
                    gamma += (d + 1) ** 2
            if not ok:
                break
        if ok:
            cand.append((gamma, side))
    if not cand:
        return []
    best = min(g for g, _side in cand)
    return [side for g, side in cand if g == best]


def violations_for_info(info):
    K, T, O, _Q, N, n = build_K(info)
    if not O:
        return []
    Oset = set(O)
    out = []
    for comp in k_components(K, n):
        C = set(comp)
        if C & Oset:
            continue
        deficit = F(N * len(C)) - sum(T[v] for v in comp)
        sat_boundary = 0
        full_boundary = 0
        for a, b in info["Bset"]:
            if (a in C) ^ (b in C):
                full_boundary += 1
                cend = a if a in C else b
                if T[cend] == N:
                    sat_boundary += 1
        if deficit < sat_boundary:
            out.append(
                {
                    "component": tuple(comp),
                    "deficit": str(deficit),
                    "sat_boundary": sat_boundary,
                    "full_boundary": full_boundary,
                    "T": tuple(str(T[v]) for v in comp),
                    "O": tuple(O),
                }
            )
    return out


def graph_case(args):
    name, n, edges, mode = args
    adj = build_adj(n, edges)
    sides = gamma_min_connected_sides(n, adj) if mode == "all-gamma" else gamma_min_sides(n, adj)
    total = 0
    first = None
    for side in sides:
        info = struct_for_side(n, adj, side)
        if info is None:
            continue
        bad = violations_for_info(info)
        if bad:
            total += len(bad)
            first = first or {"side": tuple(side), "violation": bad[0]}
    return name, len(sides), total, first


def run_census(nmin, nmax, workers, mode):
    grand = 0
    total_sides = 0
    first = None
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        tasks = [(g6, *dec(g6), mode) for g6 in g6s]
        local = 0
        sides = 0
        if workers > 1:
            ctx = mp.get_context("spawn")
            with ctx.Pool(processes=workers) as pool:
                it = pool.imap_unordered(graph_case, tasks, chunksize=16)
                for name, side_count, count, witness in it:
                    sides += side_count
                    local += count
                    first = first or ((name, witness) if witness else None)
        else:
            for task in tasks:
                name, side_count, count, witness = graph_case(task)
                sides += side_count
                local += count
                first = first or ((name, witness) if witness else None)
        grand += local
        total_sides += sides
        print(f"census N={n} graphs={len(g6s)} sides={sides} violations={local}", flush=True)
    print(f"census_total sides={total_sides} violations={grand} first={first}", flush=True)
    return grand


def run_named(mode):
    total = 0
    first = None
    for name, n, edges in named_cases():
        _name, sides, count, witness = graph_case((name, n, edges, mode))
        total += count
        first = first or ((_name, witness) if witness else None)
        print(f"named {name} sides={sides} violations={count}", flush=True)
    print(f"named_total violations={total} first={first}", flush=True)
    return total


def run_glued(mode):
    total = 0
    first = None
    cases = 0
    sides = 0
    for name, n, edges in battery():
        cases += 1
        _name, side_count, count, witness = graph_case((name, n, edges, mode))
        sides += side_count
        total += count
        first = first or ((_name, witness) if witness else None)
    print(f"glued cases={cases} sides={sides} violations={total} first={first}", flush=True)
    return total


def run_n12_leaf(mode):
    g6 = "J?AADBWM_}?"
    n0, e0 = dec(g6)
    edges = list(e0) + [(8, 11)]
    name, sides, count, witness = graph_case((g6 + "+8-11", 12, edges, mode))
    print(f"n12_leaf {name} sides={sides} violations={count} first={witness}", flush=True)
    return count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, default=7)
    ap.add_argument("--nmax", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--mode", choices=["loads-gamma", "all-gamma"], default="all-gamma")
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--named", action="store_true")
    ap.add_argument("--glued", action="store_true")
    ap.add_argument("--n12-leaf", action="store_true")
    args = ap.parse_args()

    total = 0
    if args.census:
        total += run_census(args.nmin, args.nmax, args.workers, args.mode)
    if args.named:
        total += run_named(args.mode)
    if args.glued:
        total += run_glued(args.mode)
    if args.n12_leaf:
        total += run_n12_leaf(args.mode)
    if not (args.census or args.named or args.glued or args.n12_leaf):
        total += run_named(args.mode)
        total += run_glued(args.mode)
        total += run_n12_leaf(args.mode)
    print(f"TOTAL violations={total}", flush=True)


if __name__ == "__main__":
    main()
