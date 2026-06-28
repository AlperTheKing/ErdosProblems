"""Exact tester for the direct-overload zero-port bound.

Candidate:

If a gamma-min connected-B maximum cut has O={T>N} nonempty, T[v] == N,
and zbd(v)=|N_B(v) cap {T=0}| > 0, then

    2 * direct_over(v) >= zbd(v),

where direct_over(v) sums T[o]-N over overloaded vertices o that share at
least one shortest bad-edge geodesic with v.

This quantitatively implies DIRECT-ZERO-SAT-O.
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import subprocess

from _bdef_construct import Cn, mycielski
from _h import Bconn, GENG, dec, loads, maxcut_all
from _satzmu_conn import struct_for_side
from _split_satzmu import battery
from _superphi import blow


def build_adj(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def gamma_value(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    return sum(L * L for L in st[1].values())


def gamma_min_sides(n, adj):
    cand = []
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        gamma = gamma_value(n, adj, side)
        if gamma is not None:
            cand.append((side, gamma))
    if not cand:
        return []
    gmin = min(g for _s, g in cand)
    return [s for s, g in cand if g == gmin]


def direct_sets(n, cyc):
    direct = [set() for _ in range(n)]
    for paths in cyc.values():
        for path in paths:
            support = set(path)
            for v in support:
                direct[v].update(support - {v})
    return direct


def violations_for_side(n, adj, side, include_records=False):
    st = struct_for_side(n, adj, side)
    if st is None:
        return [], []
    _bad, _ell, T, _mu, cyc = st
    O = {v for v in range(n) if T[v] > n}
    if not O:
        return [], []
    direct = direct_sets(n, cyc)
    zero = {v for v in range(n) if T[v] == 0}
    viol = []
    records = []
    for v in range(n):
        zbd = sum(1 for w in adj[v] if side[v] != side[w] and w in zero)
        if T[v] != n or zbd == 0:
            continue
        direct_os = sorted(o for o in O if o in direct[v])
        direct_over = sum(T[o] - n for o in direct_os)
        rec = {
            "v": v,
            "zbd": zbd,
            "direct_over": direct_over,
            "slack": 2 * direct_over - zbd,
            "O": tuple(sorted(O)),
            "direct_O": tuple(direct_os),
        }
        if 2 * direct_over < zbd:
            viol.append(rec)
        if include_records:
            records.append(rec)
    return viol, records


def load_case(name, n, edges):
    info = loads(n, edges)
    if info is None:
        return name, 0, None
    viol, _records = violations_for_side(n, info["adj"], info["side"])
    return name, len(viol), viol[:2] if viol else None


def worker_load(task):
    return load_case(*task)


def run_n12_leaf(verbose=False):
    g6 = "J?AADBWM_}?"
    n0, e0 = dec(g6)
    adj = build_adj(12, list(e0) + [(8, 11)])
    sides = gamma_min_sides(12, adj)
    total = 0
    first = None
    records = []
    for side in sides:
        viol, recs = violations_for_side(12, adj, side, include_records=verbose)
        total += len(viol)
        first = first or (viol[0] if viol else None)
        records.extend(recs)
    print(f"n12_leaf gamma_min_sides={len(sides)} violations={total} first={first}", flush=True)
    if verbose:
        for rec in records:
            print("  rec", rec, flush=True)
    return total


def run_glued():
    total = 0
    first = None
    cases = 0
    for name, n, edges in battery():
        cases += 1
        _name, count, witness = load_case(name, n, edges)
        total += count
        first = first or ((_name, witness) if witness else None)
    print(f"glued_load cases={cases} violations={total} first={first}", flush=True)
    return total


def named_cases():
    cases = []
    c5 = (5, Cn(5))
    n1, e1 = mycielski(*c5)
    n2, e2 = mycielski(n1, e1)
    m1, f1 = mycielski(7, Cn(7))
    cases.extend(
        [
            ("Grotzsch", n1, e1),
            ("MycGrotzsch", n2, e2),
            ("MycC7", m1, f1),
        ]
    )
    for g6, t in [
        ("J?AADBWeay?", 2),
        ("J???E?pNu\\?", 2),
        ("I?BD@g]Qo", 2),
        ("G?bF`w", 3),
    ]:
        n, edges = blow(g6, t)
        cases.append((f"{g6}[{t}]", n, edges))
    return cases


def run_named():
    total = 0
    first = None
    for name, n, edges in named_cases():
        _name, count, witness = load_case(name, n, edges)
        print(f"named {name} violations={count}", flush=True)
        total += count
        first = first or ((_name, witness) if witness else None)
    print(f"named_total violations={total} first={first}", flush=True)
    return total


def run_census_loads(nmin, nmax, workers):
    grand = 0
    first = None
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        tasks = []
        for g6 in g6s:
            nn, edges = dec(g6)
            tasks.append((g6, nn, edges))
        local = 0
        if workers > 1:
            ctx = mp.get_context("spawn")
            with ctx.Pool(processes=workers) as pool:
                for name, count, witness in pool.imap_unordered(worker_load, tasks, chunksize=16):
                    local += count
                    first = first or ((name, witness) if witness else None)
        else:
            for task in tasks:
                name, count, witness = worker_load(task)
                local += count
                first = first or ((name, witness) if witness else None)
        grand += local
        print(f"census_load N={n} graphs={len(tasks)} violations={local}", flush=True)
    print(f"census_load_total violations={grand} first={first}", flush=True)
    return grand


def run_all_gamma(nmin, nmax):
    grand = 0
    first = None
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        local = 0
        for g6 in g6s:
            nn, edges = dec(g6)
            adj = build_adj(nn, edges)
            for side in gamma_min_sides(nn, adj):
                viol, _records = violations_for_side(nn, adj, side)
                local += len(viol)
                first = first or ((g6, viol[0]) if viol else None)
        grand += local
        print(f"all_gamma N={n} graphs={len(g6s)} violations={local}", flush=True)
    print(f"all_gamma_total violations={grand} first={first}", flush=True)
    return grand


def all_gamma_graph_case(g6):
    nn, edges = dec(g6)
    adj = build_adj(nn, edges)
    local = 0
    first = None
    side_count = 0
    for side in gamma_min_sides(nn, adj):
        side_count += 1
        viol, _records = violations_for_side(nn, adj, side)
        local += len(viol)
        first = first or (viol[0] if viol else None)
    return g6, side_count, local, first


def run_all_gamma_parallel(nmin, nmax, workers):
    grand = 0
    first = None
    total_sides = 0
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        local = 0
        sides = 0
        if workers > 1:
            ctx = mp.get_context("spawn")
            with ctx.Pool(processes=workers) as pool:
                for g6, side_count, count, witness in pool.imap_unordered(all_gamma_graph_case, g6s, chunksize=16):
                    sides += side_count
                    local += count
                    first = first or ((g6, witness) if witness else None)
        else:
            for g6 in g6s:
                _g6, side_count, count, witness = all_gamma_graph_case(g6)
                sides += side_count
                local += count
                first = first or ((g6, witness) if witness else None)
        grand += local
        total_sides += sides
        print(
            f"all_gamma_parallel N={n} graphs={len(g6s)} gamma_min_sides={sides} violations={local}",
            flush=True,
        )
    print(
        f"all_gamma_parallel_total sides={total_sides} violations={grand} first={first}",
        flush=True,
    )
    return grand


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n12-leaf", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--stress", action="store_true")
    ap.add_argument("--census-loads", action="store_true")
    ap.add_argument("--all-gamma", action="store_true")
    ap.add_argument("--all-gamma-parallel", action="store_true")
    ap.add_argument("--nmin", type=int, default=7)
    ap.add_argument("--nmax", type=int, default=11)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()

    total = 0
    if args.n12_leaf:
        total += run_n12_leaf(args.verbose)
    if args.stress:
        total += run_glued()
        total += run_named()
    if args.census_loads:
        total += run_census_loads(args.nmin, args.nmax, args.workers)
    if args.all_gamma:
        total += run_all_gamma(args.nmin, args.nmax)
    if args.all_gamma_parallel:
        total += run_all_gamma_parallel(args.nmin, args.nmax, args.workers)
    if not (args.n12_leaf or args.stress or args.census_loads or args.all_gamma or args.all_gamma_parallel):
        total += run_n12_leaf(args.verbose)
        total += run_glued()
        total += run_named()
    print(f"TOTAL violations={total}", flush=True)


if __name__ == "__main__":
    main()
