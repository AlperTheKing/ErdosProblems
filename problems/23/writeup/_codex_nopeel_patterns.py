"""Summarize near-tight no-peel phantom-Hall support patterns.

Groups subsets H by coarse support geometry:
  (|H|, idle_o, core_size, multiplicity histogram)
and records the smallest phantom-Hall slack seen in each group.
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


def side_patterns(args):
    g6, n, adj, side, max_m = args
    st = struct_for_side(n, adj, side)
    if st is None:
        return {}
    M, _ell, _T2, _mu, cyc = st
    if len(M) > max_m:
        return {}
    K, T = build_K(adj, side, n)
    O = [v for v in range(n) if T[v] > n]
    Q = [v for v in range(n) if T[v] <= n]
    if not O:
        return {}
    pf = {f: pf_dict(cyc, f) for f in M}
    supp = {f: set(pf[f]) for f in M}
    x_f = {f: sum(pf[f].get(o, F(0)) for o in O) for f in M}
    s = {q: sum(K[o][q] for o in O) for q in Q}
    ml = list(M)
    out = {}
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
        idle = n - len(all_support)
        active_idx = [ml.index(f) for f in active]
        for mask in range(1, 1 << len(active_idx)):
            H = [ml[active_idx[i]] for i in range(len(active_idx)) if (mask >> i) & 1]
            union = set()
            for f in H:
                union.update(supp[f])
            no_peel = True
            privs = []
            mult = {v: 0 for v in union}
            for f in H:
                for v in supp[f]:
                    mult[v] += 1
            for f in H:
                other = set()
                for g in H:
                    if g != f:
                        other.update(supp[g])
                priv = len(supp[f] - other)
                privs.append(priv)
                if c_f[f] <= priv:
                    no_peel = False
            if not no_peel:
                continue
            hist = {}
            for m in mult.values():
                hist[m] = hist.get(m, 0) + 1
            core_size = hist.get(len(H), 0)
            key = (len(H), idle, core_size, tuple(sorted(hist.items())), tuple(sorted(privs)))
            dem = sum(c_f[f] for f in H)
            slack = F(len(union) + idle) - dem
            cur = out.get(key)
            if cur is None or slack < cur["slack"]:
                out[key] = dict(slack=slack, g6=g6, side="".join(map(str, side)), o=o, O=O, H=H)
    return out


def graph_jobs(g6, max_m):
    n, e = dec(g6)
    adj, cuts = gmins(n, e)
    return [(g6, n, adj, side, max_m) for side in cuts]


def merge(acc, part):
    for key, val in part.items():
        cur = acc.get(key)
        if cur is None or val["slack"] < cur["slack"]:
            acc[key] = val


def run(nmax, workers, max_m, keep):
    jobs = []
    for nn in range(5, nmax + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            jobs.extend(graph_jobs(g6, max_m))
    acc = {}
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for part in ex.map(side_patterns, jobs, chunksize=16):
                merge(acc, part)
    else:
        for job in jobs:
            merge(acc, side_patterns(job))
    rows = sorted(acc.items(), key=lambda kv: kv[1]["slack"])[:keep]
    for idx, (key, val) in enumerate(rows, 1):
        print(f"\n#{idx}: slack={val['slack']} ({float(val['slack']):.6f}) key={key}")
        print(f"  g6={val['g6']} side={val['side']} o={val['o']} O={val['O']} H={val['H']}")
    print(f"\npatterns={len(acc)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--nmax", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--max-m", type=int, default=14)
    ap.add_argument("--keep", type=int, default=20)
    args = ap.parse_args()
    run(args.nmax, args.workers, args.max_m, args.keep)
