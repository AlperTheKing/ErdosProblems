"""Exact tester for the anchored-surplus candidate.

Candidate inequality from the zero-moat prefix-switch consult:

    T(v) + e_B(v, V0) <= N + sum_{x in Kcomp(v)} max(T(x)-N, 0).

The saturation-gated form is enough for C-alltie: if T(v)=N and v has a
zero-load B-neighbour, then the K-component of v must contain overload.
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import subprocess
from fractions import Fraction as F

from _h import Bconn, GENG, dec, loads, maxcut_all
from _superphi import blow
from _bdef_construct import Cn, is_triangle_free, mycielski, union_disjoint
from _satzmu_conn import kcomponents, struct_for_side
from _split_satzmu import battery


def build_adj(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def violations_for_side(n, adj, side, scope="all", coef=F(1), require_o=False):
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    _M, _ell, T, _mu, cyc = st
    O = {v for v in range(n) if T[v] > n}
    if require_o and not O:
        return []
    comps, find = kcomponents(n, cyc)
    V0 = {v for v in range(n) if T[v] == 0}
    out = []
    for v in range(n):
        zbd = sum(1 for w in adj[v] if side[v] != side[w] and w in V0)
        if scope == "sat" and T[v] != n:
            continue
        if scope == "sat-zero-neighbor" and not (T[v] == n and zbd > 0):
            continue
        C = comps[find(v)]
        surplus = sum(T[x] - n for x in C if T[x] > n)
        lhs = T[v] + zbd
        rhs = F(n) + coef * surplus
        if lhs > rhs:
            out.append(
                {
                    "v": v,
                    "lhs": lhs,
                    "rhs": rhs,
                    "T": T[v],
                    "zbd": zbd,
                    "C": tuple(sorted(C)),
                    "OinC": tuple(sorted(x for x in C if T[x] > n)),
                }
            )
    return out


def load_case(name, n, edges, scope, coef, require_o):
    info = loads(n, edges)
    if info is None:
        return name, 0, None
    viol = violations_for_side(n, info["adj"], info["side"], scope, coef, require_o)
    return name, len(viol), viol[:3] if viol else None


def worker_load(args):
    name, n, edges, scope, coef, require_o = args
    return load_case(name, n, edges, scope, coef, require_o)


def run_glued(scope, coef, require_o):
    total = 0
    first = None
    cases = 0
    for name, n, edges in battery():
        cases += 1
        _name, count, witness = load_case(name, n, edges, scope, coef, require_o)
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


def run_named(scope, coef, require_o):
    total = 0
    first = None
    for name, n, edges in named_cases():
        _name, count, witness = load_case(name, n, edges, scope, coef, require_o)
        print(f"named {name} violations={count}", flush=True)
        total += count
        first = first or ((_name, witness) if witness else None)
    print(f"named_total violations={total} first={first}", flush=True)
    return total


def run_census(nmin, nmax, scope, workers, coef, require_o):
    grand = 0
    first = None
    for n in range(nmin, nmax + 1):
        g6s = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True).stdout.split()
        tasks = []
        for g6 in g6s:
            nn, edges = dec(g6)
            tasks.append((g6, nn, edges, scope, coef, require_o))
        local = 0
        if workers > 1:
            ctx = mp.get_context("spawn")
            with ctx.Pool(processes=workers) as pool:
                it = pool.imap_unordered(worker_load, tasks, chunksize=16)
                for name, count, witness in it:
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


def run_n12_leaf(scope, coef, require_o):
    g6 = "J?AADBWM_}?"
    n0, e0 = dec(g6)
    edges = list(e0) + [(8, 11)]
    adj = build_adj(12, edges)
    cand = []
    for side in maxcut_all(12, adj):
        if not Bconn(12, adj, side):
            continue
        st = struct_for_side(12, adj, side)
        if st is None:
            continue
        gamma = sum(L * L for L in st[1].values())
        cand.append((side, gamma))
    if not cand:
        print("n12_leaf no_connected_gamma_sides", flush=True)
        return 0
    gmin = min(gamma for _side, gamma in cand)
    total = 0
    first = None
    sides = 0
    for side, gamma in cand:
        if gamma != gmin:
            continue
        sides += 1
        viol = violations_for_side(12, adj, side, scope, coef, require_o)
        total += len(viol)
        first = first or (viol[:3] if viol else None)
    print(f"n12_leaf gamma_min_sides={sides} violations={total} first={first}", flush=True)
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", choices=["all", "sat", "sat-zero-neighbor"], default="all")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--coef-num", type=int, default=1)
    ap.add_argument("--coef-den", type=int, default=1)
    ap.add_argument("--require-o", action="store_true")
    ap.add_argument("--nmin", type=int, default=7)
    ap.add_argument("--nmax", type=int, default=10)
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--skip-stress", action="store_true")
    args = ap.parse_args()
    coef = F(args.coef_num, args.coef_den)

    total = 0
    if not args.skip_stress:
        total += run_glued(args.scope, coef, args.require_o)
        total += run_named(args.scope, coef, args.require_o)
        total += run_n12_leaf(args.scope, coef, args.require_o)
    if not args.skip_census:
        total += run_census(args.nmin, args.nmax, args.scope, args.workers, coef, args.require_o)
    print(
        f"TOTAL scope={args.scope} coef={coef} require_o={args.require_o} violations={total}",
        flush=True,
    )


if __name__ == "__main__":
    main()
