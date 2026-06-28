"""Exact tests for EDGE-SHADOW-CAP and zero-mu consequences.

Candidate:
  For each B-edge e=uv, r_e(f)=p_f(u)+p_f(v)-tau_f(e), and
      sum_f ell(f) r_e(f) <= N.

Stronger pointwise candidate:
      c_e(x)=sum_f r_e(f) p_f(x) <= 1.

Zero-mu hierarchy requested by the user:
  1. PESC-ZMU: for mu(uv)=0, sum_f (p_f(u)+p_f(v))p_f(x)<=1 for all x.
  2. ZMU-CAP:  for mu(uv)=0, T(u)+T(v)<=N.
  3. A-alltie gate: mu(uv)=0 and T(u)=N => T(v)=0.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as F
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

from _angleD_O1 import gmin_sides
from _h import GENG, dec
from _satzmu_conn import struct_for_side


def side_report(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st

    pfs = []
    taus = []
    b_edges = sorted(mu)
    bset = set(b_edges)
    for f in M:
        Ps = cyc[f]
        pf = [F(0) for _ in range(n)]
        tau = {e: F(0) for e in b_edges}
        for P in Ps:
            for v in P:
                pf[v] += F(1, len(Ps))
            for i in range(len(P) - 1):
                e = (min(P[i], P[i + 1]), max(P[i], P[i + 1]))
                if e in bset:
                    tau[e] += F(1, len(Ps))
        pfs.append(pf)
        taus.append(tau)

    stats = {
        "sides": 1,
        "b_edges": len(b_edges),
        "zmu_edges": 0,
        "pesc_zmu_fail": 0,
        "zmu_cap_fail": 0,
        "sat_gate_fail": 0,
        "esc_fail": 0,
        "pesc_fail": 0,
    }
    first = {}

    for e in b_edges:
        u, v = e
        rvals = [pfs[i][u] + pfs[i][v] - taus[i][e] for i in range(len(M))]
        esc = sum(ell[M[i]] * rvals[i] for i in range(len(M)))
        if esc > n:
            stats["esc_fail"] += 1
            first.setdefault("esc", (e, esc, n))
        for x in range(n):
            ce = sum(rvals[i] * pfs[i][x] for i in range(len(M)))
            if ce > 1:
                stats["pesc_fail"] += 1
                first.setdefault("pesc", (e, x, ce))
                break

        if mu[e] == 0:
            stats["zmu_edges"] += 1
            s = T[u] + T[v]
            if s > n:
                stats["zmu_cap_fail"] += 1
                first.setdefault("zmu_cap", (e, T[u], T[v], s, n))
            for a, b in ((u, v), (v, u)):
                if T[a] == n and T[b] != 0:
                    stats["sat_gate_fail"] += 1
                    first.setdefault("sat_gate", (a, b, e, T[a], T[b]))

            for x in range(n):
                ce_z = sum((pfs[i][u] + pfs[i][v]) * pfs[i][x] for i in range(len(M)))
                if ce_z > 1:
                    stats["pesc_zmu_fail"] += 1
                    first.setdefault("pesc_zmu", (e, x, ce_z))
                    break

    return stats, first


def merge_stats(a, b):
    for k, v in b.items():
        a[k] = a.get(k, 0) + v


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    stats = {"graphs": 1, "gamma_sides": 0}
    first = {}
    for side in sides:
        r = side_report(n, adj, side)
        if r is None:
            continue
        st, fs = r
        stats["gamma_sides"] += 1
        merge_stats(stats, st)
        for k, v in fs.items():
            first.setdefault(k, (g6, "".join(map(str, side)), v))
    return stats, first


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=11)
    ap.add_argument("--workers", type=int, default=min(61, os.cpu_count() or 1))
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    total = {}
    first = {}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            st, fs = fut.result()
            merge_stats(total, st)
            for k, v in fs.items():
                first.setdefault(k, v)

    print("workers", args.workers)
    print("N", args.n)
    print("stats", total)
    print("first", first)


if __name__ == "__main__":
    main()
