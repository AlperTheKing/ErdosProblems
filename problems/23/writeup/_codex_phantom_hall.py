"""Exact test for row-Hall repaired by row-idle phantom capacity.

For fixed overloaded row o, define c_f(o) as in the row-Hall attempt.
Support-Hall was false:

    sum_{f in H} c_f(o) <= |union supp(p_f)|.

This tests the repaired family

    sum_{f in H} c_f(o) <= |union supp(H)| + idle_o,

where idle_o is the number of vertices outside the union of supports of all
active f with c_f(o)>0.  It also tests the analogous truncated-mass repair.

This is not a proof; it is a gate for a possible "phantom capacity" transport.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec
from _opencap import build_K
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _stark1 import odd_blowup
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free


def empty_result(skip=0):
    return dict(
        cuts=0,
        skip=skip,
        ph_fail=0,
        tm_ph_fail=0,
        row_fail=0,
        subset_gt_full=0,
        tm_subset_gt_full=0,
        oside_fail=0,
        worst=(F(-10**9), None),
        worst_subset_full=(F(-10**9), None),
        worst_oside=(F(-10**9), None),
    )


def pf_dict(cyc, f):
    ps = cyc[f]
    k = len(ps)
    d = {}
    for path in ps:
        for v in path:
            d[v] = d.get(v, F(0)) + F(1, k)
    return d


def side_check(args):
    g6, n, adj, side, max_m = args
    st = struct_for_side(n, adj, side)
    if st is None:
        return empty_result()
    M, ell, _T2, _mu, cyc = st
    if len(M) > max_m:
        return empty_result(skip=1)
    K, T = build_K(adj, side, n)
    N = n
    O = [v for v in range(n) if T[v] > N]
    Q = [v for v in range(n) if T[v] <= N]
    if not O:
        return empty_result()

    pf = {f: pf_dict(cyc, f) for f in M}
    supp = {f: set(pf[f]) for f in M}
    x_f = {f: sum(pf[f].get(o, F(0)) for o in O) for f in M}
    s = {q: sum(K[o][q] for o in O) for q in Q}
    ml = list(M)

    out = dict(
        cuts=1,
        skip=0,
        ph_fail=0,
        tm_ph_fail=0,
        row_fail=0,
        subset_gt_full=0,
        tm_subset_gt_full=0,
        oside_fail=0,
        worst=(F(-10**9), None),
        worst_subset_full=(F(-10**9), None),
        worst_oside=(F(-10**9), None),
    )
    for o in O:
        psi = {q: K[o][q] / (F(N) - T[q] + s[q]) for q in Q if (F(N) - T[q] + s[q]) > 0}
        c_f = {
            f: x_f[f]
            * (pf[f].get(o, F(0)) + sum(psi.get(q, F(0)) * pf[f].get(q, F(0)) for q in Q))
            for f in M
        }
        active = [f for f in ml if c_f[f] > 0]
        if not active:
            continue
        all_support = set()
        a_all = {}
        for f in active:
            all_support.update(supp[f])
            for v, pv in pf[f].items():
                a_all[v] = a_all.get(v, F(0)) + x_f[f] * pv
        idle = N - len(all_support)
        full_dem = sum(c_f[f] for f in active)
        full_def = full_dem - F(len(all_support))
        full_tm_cap = sum(min(F(1), a_all.get(v, F(0))) for v in a_all)
        full_tm_def = full_dem - full_tm_cap
        if full_dem > N:
            out["row_fail"] += 1

        active_idx = [ml.index(f) for f in active]
        # Enumerate subsets of active edges only; inactive edges add no demand.
        for mask in range(1, 1 << len(active_idx)):
            H = [ml[active_idx[i]] for i in range(len(active_idx)) if (mask >> i) & 1]
            dem = sum(c_f[f] for f in H)
            union = set()
            a_h = {}
            for f in H:
                union.update(supp[f])
                for v, pv in pf[f].items():
                    a_h[v] = a_h.get(v, F(0)) + x_f[f] * pv
            ph_cap = F(len(union) + idle)
            tm_cap = sum(min(F(1), a_h.get(v, F(0))) for v in a_h) + F(idle)
            o_direct = sum(x_f[f] * pf[f].get(o, F(0)) for f in H)
            o_cap = sum(min(F(1), a_h.get(v, F(0))) for v in O) + F(idle)
            ph_excess = dem - ph_cap
            tm_excess = dem - tm_cap
            oside_excess = o_direct - o_cap
            support_def = dem - F(len(union))
            tm_def = dem - sum(min(F(1), a_h.get(v, F(0))) for v in a_h)
            if ph_excess > 0:
                out["ph_fail"] += 1
            if tm_excess > 0:
                out["tm_ph_fail"] += 1
            if oside_excess > 0:
                out["oside_fail"] += 1
            if support_def > full_def:
                out["subset_gt_full"] += 1
            if tm_def > full_tm_def:
                out["tm_subset_gt_full"] += 1
            excess = max(ph_excess, tm_excess)
            if excess > out["worst"][0]:
                out["worst"] = (
                    excess,
                    dict(
                        g6=g6,
                        side="".join(map(str, side)),
                        N=N,
                        o=o,
                        H=H,
                        dem=dem,
                        union=len(union),
                        idle=idle,
                        ph_cap=ph_cap,
                        tm_cap=tm_cap,
                        active=len(active),
                        full_def=full_def,
                        full_tm_def=full_tm_def,
                    ),
                )
            subset_gap = max(support_def - full_def, tm_def - full_tm_def)
            if subset_gap > out["worst_subset_full"][0]:
                out["worst_subset_full"] = (
                    subset_gap,
                    dict(
                        g6=g6,
                        side="".join(map(str, side)),
                        N=N,
                        o=o,
                        H=H,
                        support_def=support_def,
                        full_def=full_def,
                        tm_def=tm_def,
                        full_tm_def=full_tm_def,
                        idle=idle,
                        active=len(active),
                    ),
                )
            if oside_excess > out["worst_oside"][0]:
                out["worst_oside"] = (
                    oside_excess,
                    dict(
                        g6=g6,
                        side="".join(map(str, side)),
                        N=N,
                        o=o,
                        H=H,
                        o_direct=o_direct,
                        o_cap=o_cap,
                        idle=idle,
                        O=O,
                        active=len(active),
                    ),
                )
    return out


def graph_jobs_from_edges(name, n, e, max_m):
    adj, cuts = gmins(n, e)
    return [(name, n, adj, side, max_m) for side in cuts]


def graph_jobs(g6, max_m):
    n, e = dec(g6)
    return graph_jobs_from_edges(g6, n, e, max_m)


def merge(acc, res):
    for key in ["cuts", "skip", "ph_fail", "tm_ph_fail", "row_fail", "subset_gt_full", "tm_subset_gt_full", "oside_fail"]:
        acc[key] += res[key]
    if res["worst"][0] > acc["worst"][0]:
        acc["worst"] = res["worst"]
    if res["worst_subset_full"][0] > acc["worst_subset_full"][0]:
        acc["worst_subset_full"] = res["worst_subset_full"]
    if res["worst_oside"][0] > acc["worst_oside"][0]:
        acc["worst_oside"] = res["worst_oside"]


def census_jobs(nmax, max_m):
    jobs = []
    for nn in range(5, nmax + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            jobs.extend(graph_jobs(g6, max_m))
    return jobs


def adversarial_jobs(max_m):
    jobs = []
    cur = (5, Cn(5))
    cur = mycielski(*cur)
    jobs.extend(graph_jobs_from_edges("Grotzsch11", cur[0], cur[1], max_m))
    cur = mycielski(*cur)
    # N=23 is handled by Claude's specialized gate; exhaustive max-cut
    # generation here is too slow for a routine local battery.
    c7m = mycielski(7, Cn(7))
    jobs.extend(graph_jobs_from_edges("MycC7_15", c7m[0], c7m[1], max_m))

    for sizes in [
        [1, 3, 2, 2, 3],
        [2, 3, 2, 2, 3],
        [1, 4, 3, 2, 4],
        [2, 4, 2, 3, 4],
        [1, 5, 3, 2, 5],
        [1, 8, 4, 3, 8],
        [1, 12, 6, 4, 12],
    ]:
        n, e, _adj, _side = odd_blowup(5, sizes)
        if n <= 22:
            jobs.extend(graph_jobs_from_edges(f"C5{sizes}", n, e, max_m))

    g15 = mycielski(7, Cn(7))
    gr = mycielski(5, Cn(5))
    for iN, iE in [(5, Cn(5)), (7, Cn(7))]:
        for gN, gE in [g15, gr]:
            for br in [[(0, 0)], [(0, 1)], [(0, 2)], [(0, 0), (2, 3)]]:
                if any(j >= gN for _, j in br):
                    continue
                n, e = union_disjoint((iN, iE), (gN, gE))
                for i, j in br:
                    e = e + [(i, iN + j)]
                if n <= 22 and is_triangle_free(n, e):
                    jobs.extend(graph_jobs_from_edges(f"glue{iN}+{gN}+{br}", n, e, max_m))
    return jobs


def run_jobs(jobs, workers):
    acc = dict(
        cuts=0,
        skip=0,
        ph_fail=0,
        tm_ph_fail=0,
        row_fail=0,
        subset_gt_full=0,
        tm_subset_gt_full=0,
        oside_fail=0,
        worst=(F(-10**9), None),
        worst_subset_full=(F(-10**9), None),
        worst_oside=(F(-10**9), None),
    )
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for res in ex.map(side_check, jobs, chunksize=16):
                merge(acc, res)
    else:
        for job in jobs:
            merge(acc, side_check(job))
    print(f"cuts={acc['cuts']} skip={acc['skip']} row_fail={acc['row_fail']} ph_fail={acc['ph_fail']} tm_ph_fail={acc['tm_ph_fail']}")
    print(f"subset_gt_full={acc['subset_gt_full']} tm_subset_gt_full={acc['tm_subset_gt_full']} oside_fail={acc['oside_fail']}")
    print(f"worst={acc['worst'][0]} ({float(acc['worst'][0]):+.6f})")
    print(acc["worst"][1])
    print(f"worst_subset_full={acc['worst_subset_full'][0]} ({float(acc['worst_subset_full'][0]):+.6f})")
    print(acc["worst_subset_full"][1])
    print(f"worst_oside={acc['worst_oside'][0]} ({float(acc['worst_oside'][0]):+.6f})")
    print(acc["worst_oside"][1])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--nmax", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--max-m", type=int, default=14)
    ap.add_argument("--mode", choices=["census", "adversarial", "all"], default="census")
    args = ap.parse_args()
    jobs = []
    if args.mode in ("census", "all"):
        jobs.extend(census_jobs(args.nmax, args.max_m))
    if args.mode in ("adversarial", "all"):
        jobs.extend(adversarial_jobs(args.max_m))
    run_jobs(jobs, args.workers)
