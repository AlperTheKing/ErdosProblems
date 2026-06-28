r"""Dump near-tight phantom-Hall instances with private-support anatomy.

For each fixed overloaded row o and subset H of active bad edges, phantom-Hall
slack is

    slack(H) = |union supp(H)| + idle_o - sum_{f in H} c_f(o).

This script records the smallest exact slacks and the peeling data:

    private_H(f) = |supp(f) \ union_{g in H\{f}} supp(g)|.

It is a diagnostic for the proposed minimal-counterexample proof.
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


def pf_dict(cyc, f):
    ps = cyc[f]
    k = len(ps)
    d = {}
    for path in ps:
        for v in path:
            d[v] = d.get(v, F(0)) + F(1, k)
    return d


def add_top(top, item, keep):
    top.append(item)
    top.sort(key=lambda x: x["slack"])
    del top[keep:]


def side_dump(args):
    g6, n, adj, side, max_m, keep = args
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, _ell, _T2, _mu, cyc = st
    if len(M) > max_m:
        return []
    K, T = build_K(adj, side, n)
    O = [v for v in range(n) if T[v] > n]
    Q = [v for v in range(n) if T[v] <= n]
    if not O:
        return []
    pf = {f: pf_dict(cyc, f) for f in M}
    supp = {f: set(pf[f]) for f in M}
    x_f = {f: sum(pf[f].get(o, F(0)) for o in O) for f in M}
    s = {q: sum(K[o][q] for o in O) for q in Q}
    ml = list(M)
    top = []

    for o in O:
        psi = {q: K[o][q] / (F(n) - T[q] + s[q]) for q in Q if (F(n) - T[q] + s[q]) > 0}
        c_f = {
            f: x_f[f]
            * (pf[f].get(o, F(0)) + sum(psi.get(q, F(0)) * pf[f].get(q, F(0)) for q in Q))
            for f in M
        }
        active = [f for f in ml if c_f[f] > 0]
        if not active:
            continue
        all_support = set()
        for f in active:
            all_support.update(supp[f])
        idle_set = set(range(n)) - all_support
        idle = len(idle_set)
        active_idx = [ml.index(f) for f in active]
        for mask in range(1, 1 << len(active_idx)):
            H = [ml[active_idx[i]] for i in range(len(active_idx)) if (mask >> i) & 1]
            union = set()
            for f in H:
                union.update(supp[f])
            dem = sum(c_f[f] for f in H)
            slack = F(len(union) + idle) - dem
            priv = {}
            no_peel = True
            mult = {v: 0 for v in union}
            for f in H:
                for v in supp[f]:
                    mult[v] += 1
            core = sorted(v for v, m in mult.items() if m == len(H))
            multiplicity_hist = {}
            for m in mult.values():
                multiplicity_hist[m] = multiplicity_hist.get(m, 0) + 1
            for f in H:
                other = set()
                for g in H:
                    if g != f:
                        other.update(supp[g])
                priv[f] = len(supp[f] - other)
                if c_f[f] <= priv[f]:
                    no_peel = False
            common_endpoints = set(H[0])
            for f in H[1:]:
                common_endpoints &= set(f)
            add_top(
                top,
                dict(
                    slack=slack,
                    g6=g6,
                    side="".join(map(str, side)),
                    N=n,
                    o=o,
                    O=O,
                    H=H,
                    H_size=len(H),
                    active_size=len(active),
                    dem=dem,
                    union_size=len(union),
                    idle=idle,
                    idle_vertices=sorted(idle_set),
                    no_peel=no_peel,
                    common_endpoints=sorted(common_endpoints),
                    core=core,
                    multiplicity_hist=multiplicity_hist,
                    per_f=[
                        dict(f=f, c=c_f[f], priv=priv[f], supp=sorted(supp[f]), x=x_f[f])
                        for f in H
                    ],
                ),
                keep,
            )
    return top


def graph_jobs(g6, max_m, keep):
    n, e = dec(g6)
    adj, cuts = gmins(n, e)
    return [(g6, n, adj, side, max_m, keep) for side in cuts]


def run(nmax, workers, max_m, keep):
    jobs = []
    for nn in range(5, nmax + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            jobs.extend(graph_jobs(g6, max_m, keep))
    top = []
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for part in ex.map(side_dump, jobs, chunksize=16):
                for item in part:
                    add_top(top, item, keep)
    else:
        for job in jobs:
            for item in side_dump(job):
                add_top(top, item, keep)

    for idx, item in enumerate(top, 1):
        print(f"\n#{idx}: slack={item['slack']} ({float(item['slack']):.6f})")
        print(
            f"  g6={item['g6']} N={item['N']} side={item['side']} o={item['o']} O={item['O']} "
            f"H_size={item['H_size']} active={item['active_size']} no_peel={item['no_peel']}"
        )
        print(
            f"  dem={item['dem']} union={item['union_size']} idle={item['idle']} "
            f"idle_vertices={item['idle_vertices']} common_endpoints={item['common_endpoints']}"
        )
        print(f"  core={item['core']} multiplicity_hist={item['multiplicity_hist']}")
        for row in item["per_f"]:
            print(
                f"    f={row['f']} c={row['c']} priv={row['priv']} x={row['x']} supp={row['supp']}"
            )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--nmax", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--max-m", type=int, default=14)
    ap.add_argument("--keep", type=int, default=10)
    args = ap.parse_args()
    run(args.nmax, args.workers, args.max_m, args.keep)
