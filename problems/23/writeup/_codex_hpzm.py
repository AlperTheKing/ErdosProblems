"""Exact tester for the half-port zero-moat prefix charge.

Candidate from the zero-moat prefix-switch consult:

For a gamma-min connected-B maximum cut, if O is nonempty, T[v] == N, and
v has at least one zero-load B-neighbour, define

  k(v) = |N_B(v) cap {T=0}|,
  over(C(v)) = sum_{x in Kcomp(v), T[x] > N} (T[x] - N).

For every oriented shortest-geodesic prefix A through v, let

  m_v(A) = min Delta_beta(A union Z),

where Z ranges over all zero-load vertex subsets containing all zero-load
B-neighbours of v. The weighted prefixes use

  lambda = ell(f) / (2 * N * |P_f|)

for each of the two prefixes of each shortest f-geodesic containing v.
The rejected scalar is

  k(v) + sum_A lambda_A * m_v(A) <= 2 * over(C(v)).

The repaired leakage scalar suggested after the N=12 failure is

  k(v) + sum_A lambda_A max(0, m_v(A)-Delta_beta(A)+k(v))
      <= 2 * over(C(v)).

This script is an exact Fraction checker. It is exploratory, not a proof.
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import subprocess
from fractions import Fraction as F

from _bdef_construct import Cn, mycielski
from _h import Bconn, GENG, dec, loads, maxcut_all
from _satzmu_conn import kcomponents, struct_for_side
from _split_satzmu import battery
from _superphi import blow


def build_adj(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def edge_sets(n, adj, side):
    B = set()
    M = set()
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            e = (u, v)
            if side[u] != side[v]:
                B.add(e)
            else:
                M.add(e)
    return B, M


def cut_loss(B, M, S):
    S = set(S)
    db = sum(1 for u, v in B if (u in S) ^ (v in S))
    dm = sum(1 for u, v in M if (u in S) ^ (v in S))
    return db - dm


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


def min_zero_moat_loss(B, M, A, zero_vertices, required_zero):
    zero_vertices = sorted(zero_vertices)
    required_zero = set(required_zero)
    optional = [z for z in zero_vertices if z not in required_zero]
    base = set(A) | required_zero
    best = None
    # The exact stress cases that trigger this condition have tiny V0. If this
    # ever becomes large, replace this brute force with a small s-t min-cut.
    for mask in range(1 << len(optional)):
        S = set(base)
        for i, z in enumerate(optional):
            if (mask >> i) & 1:
                S.add(z)
        val = cut_loss(B, M, S)
        if best is None or val < best:
            best = val
    return best if best is not None else cut_loss(B, M, base)


def hpzm_for_side(n, adj, side, only_violations=True, mode="old"):
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    bad_edges, ell, T, _mu, cyc = st
    O = {v for v in range(n) if T[v] > n}
    if not O:
        return []
    comps, find = kcomponents(n, cyc)
    Bset, Mset = edge_sets(n, adj, side)
    zero = {v for v in range(n) if T[v] == 0}
    out = []
    for v in range(n):
        if T[v] != n:
            continue
        zero_ports = {w for w in adj[v] if side[v] != side[w] and w in zero}
        if not zero_ports:
            continue
        C = comps[find(v)]
        over = sum(T[x] - n for x in C if T[x] > n)
        weighted = F(0)
        weighted_raw = F(0)
        weighted_leak = F(0)
        weight_sum = F(0)
        samples = []
        for f in bad_edges:
            paths = cyc[f]
            if not paths:
                continue
            lam = F(ell[f], 2 * n * len(paths))
            for P in paths:
                for i, x in enumerate(P):
                    if x != v:
                        continue
                    prefixes = (frozenset(P[: i + 1]), frozenset(P[i:]))
                    for A in prefixes:
                        raw = cut_loss(Bset, Mset, A)
                        m = min_zero_moat_loss(Bset, Mset, A, zero, zero_ports)
                        leak = max(0, m - raw + len(zero_ports))
                        weighted += lam * m
                        weighted_raw += lam * raw
                        weighted_leak += lam * leak
                        weight_sum += lam
                        if len(samples) < 6:
                            samples.append((tuple(P), tuple(sorted(A)), raw, m, leak))
        if mode == "old":
            lhs = F(len(zero_ports)) + weighted
        elif mode == "leak":
            lhs = F(len(zero_ports)) + weighted_leak
        else:
            raise ValueError(f"unknown mode {mode}")
        rhs = 2 * over
        rec = {
            "mode": mode,
            "v": v,
            "lhs": lhs,
            "rhs": rhs,
            "slack": rhs - lhs,
            "k": len(zero_ports),
            "weighted_m": weighted,
            "weighted_raw": weighted_raw,
            "weighted_leak": weighted_leak,
            "weight_sum": weight_sum,
            "over": over,
            "zero_ports": tuple(sorted(zero_ports)),
            "O": tuple(sorted(O)),
            "C": tuple(sorted(C)),
            "samples": samples,
        }
        if (not only_violations) or lhs > rhs:
            out.append(rec)
    return out


def run_n12_leaf(verbose=False, mode="old"):
    g6 = "J?AADBWM_}?"
    n0, e0 = dec(g6)
    adj = build_adj(12, list(e0) + [(8, 11)])
    total = 0
    first = None
    records = []
    sides = gamma_min_sides(12, adj)
    for side in sides:
        viol = hpzm_for_side(12, adj, side, only_violations=True, mode=mode)
        total += len(viol)
        first = first or (viol[0] if viol else None)
        if verbose:
            records.extend(hpzm_for_side(12, adj, side, only_violations=False, mode=mode))
    print(f"n12_leaf mode={mode} gamma_min_sides={len(sides)} violations={total} first={first}", flush=True)
    if verbose:
        for rec in records:
            print("  rec", rec, flush=True)
    return total


def load_case(name, n, edges, mode):
    info = loads(n, edges)
    if info is None:
        return name, 0, None
    viol = hpzm_for_side(n, info["adj"], info["side"], only_violations=True, mode=mode)
    return name, len(viol), viol[:2] if viol else None


def worker_load(task):
    return load_case(*task)


def run_glued(mode):
    total = 0
    first = None
    cases = 0
    for name, n, edges in battery():
        cases += 1
        _name, count, witness = load_case(name, n, edges, mode)
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


def run_named(mode):
    total = 0
    first = None
    for name, n, edges in named_cases():
        _name, count, witness = load_case(name, n, edges, mode)
        print(f"named {name} violations={count}", flush=True)
        total += count
        first = first or ((_name, witness) if witness else None)
    print(f"named_total violations={total} first={first}", flush=True)
    return total


def run_census_loads(nmin, nmax, workers, mode):
    grand = 0
    first = None
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        tasks = []
        for g6 in g6s:
            nn, edges = dec(g6)
            tasks.append((g6, nn, edges, mode))
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


def run_all_gamma(nmin, nmax, mode):
    grand = 0
    first = None
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        local = 0
        for g6 in g6s:
            nn, edges = dec(g6)
            adj = build_adj(nn, edges)
            for side in gamma_min_sides(nn, adj):
                viol = hpzm_for_side(nn, adj, side, only_violations=True, mode=mode)
                local += len(viol)
                first = first or ((g6, viol[0]) if viol else None)
        grand += local
        print(f"all_gamma N={n} graphs={len(g6s)} violations={local}", flush=True)
    print(f"all_gamma_total violations={grand} first={first}", flush=True)
    return grand


def all_gamma_graph_case(task):
    g6, mode = task
    nn, edges = dec(g6)
    adj = build_adj(nn, edges)
    local = 0
    first = None
    side_count = 0
    for side in gamma_min_sides(nn, adj):
        side_count += 1
        viol = hpzm_for_side(nn, adj, side, only_violations=True, mode=mode)
        local += len(viol)
        first = first or (viol[0] if viol else None)
    return g6, side_count, local, first


def run_all_gamma_parallel(nmin, nmax, workers, mode):
    grand = 0
    first = None
    total_sides = 0
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        tasks = [(g6, mode) for g6 in g6s]
        local = 0
        sides = 0
        if workers > 1:
            ctx = mp.get_context("spawn")
            with ctx.Pool(processes=workers) as pool:
                for g6, side_count, count, witness in pool.imap_unordered(all_gamma_graph_case, tasks, chunksize=16):
                    sides += side_count
                    local += count
                    first = first or ((g6, witness) if witness else None)
        else:
            for task in tasks:
                g6, side_count, count, witness = all_gamma_graph_case(task)
                sides += side_count
                local += count
                first = first or ((g6, witness) if witness else None)
        grand += local
        total_sides += sides
        print(
            f"all_gamma_parallel mode={mode} N={n} graphs={len(g6s)} gamma_min_sides={sides} violations={local}",
            flush=True,
        )
    print(
        f"all_gamma_parallel_total mode={mode} sides={total_sides} violations={grand} first={first}",
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
    ap.add_argument("--mode", choices=["old", "leak"], default="old")
    args = ap.parse_args()

    total = 0
    if args.n12_leaf:
        total += run_n12_leaf(args.verbose, args.mode)
    if args.stress:
        total += run_glued(args.mode)
        total += run_named(args.mode)
    if args.census_loads:
        total += run_census_loads(args.nmin, args.nmax, args.workers, args.mode)
    if args.all_gamma:
        total += run_all_gamma(args.nmin, args.nmax, args.mode)
    if args.all_gamma_parallel:
        total += run_all_gamma_parallel(args.nmin, args.nmax, args.workers, args.mode)
    if not (args.n12_leaf or args.stress or args.census_loads or args.all_gamma or args.all_gamma_parallel):
        total += run_n12_leaf(args.verbose, args.mode)
        total += run_glued(args.mode)
        total += run_named(args.mode)
    print(f"TOTAL mode={args.mode} violations={total}", flush=True)


if __name__ == "__main__":
    main()
