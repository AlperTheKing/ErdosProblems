"""Dump positive-demand near-tight cases for the truncated-mass row-Hall target."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as F
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

from _angleD_O1 import gmin_sides
from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _test_fullg import build_K


def frac(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    best = None
    for side in sides:
        r = build_K(adj, side, n)
        if r is None:
            continue
        K, T = r
        O = [v for v in range(n) if T[v] > n]
        Q = [v for v in range(n) if T[v] <= n]
        if not O:
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, _T2, _mu, cyc = st
        pfs = []
        Xs = []
        supports = []
        for f in M:
            Ps = cyc[f]
            pf = [F(0) for _ in range(n)]
            supp = set()
            for P in Ps:
                for v in P:
                    pf[v] += F(1, len(Ps))
                    supp.add(v)
            pfs.append(pf)
            Xs.append(sum(pf[op] for op in O))
            supports.append(supp)
        for o in O:
            psi = [F(0) for _ in range(n)]
            ok = True
            for q in Q:
                s = sum(K[op][q] for op in O)
                R = F(n) - T[q]
                den = R + s
                if den <= 0:
                    ok = False
                    break
                psi[q] = K[o][q] / den if K[o][q] else F(0)
            if not ok:
                continue
            row_dem = [
                Xs[i] * (pfs[i][o] + sum(psi[q] * pfs[i][q] for q in Q))
                for i in range(len(M))
            ]
            for mask in range(1, 1 << len(M)):
                demand = sum((row_dem[i] for i in range(len(M)) if (mask >> i) & 1), F(0))
                if demand == 0:
                    continue
                A = [F(0) for _ in range(n)]
                U = set()
                for i in range(len(M)):
                    if (mask >> i) & 1:
                        U |= supports[i]
                        Xi = Xs[i]
                        if Xi:
                            for v, val in enumerate(pfs[i]):
                                if val:
                                    A[v] += Xi * val
                cap = sum(min(F(1), av) for av in A)
                slack = cap - demand
                rec = (
                    slack,
                    g6,
                    "".join(map(str, side)),
                    o,
                    mask.bit_count(),
                    len(M),
                    demand,
                    cap,
                    tuple(M[i] for i in range(len(M)) if (mask >> i) & 1),
                    tuple((v, A[v], (F(1) if v == o else psi[v] if v in Q else F(0))) for v in range(n) if A[v] or v == o),
                    tuple(sorted(U)),
                    tuple((op, T[op]) for op in O),
                )
                if best is None or rec < best:
                    best = rec
    return best


def main():
    workers = min(61, os.cpu_count() or 1)
    graphs = subprocess.run([GENG, "-tc", "11"], capture_output=True, text=True, check=True).stdout.split()
    hits = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            rec = fut.result()
            if rec is not None:
                hits.append(rec)
    hits.sort()
    print("workers", workers)
    print("positive_configs", len(hits))
    for rec in hits[:20]:
        slack, g6, side, o, k, m, demand, cap, edges, avec, U, Oloads = rec
        print({
            "slack": frac(slack),
            "g6": g6,
            "side": side,
            "o": o,
            "subset_size": k,
            "M_size": m,
            "demand": frac(demand),
            "cap": frac(cap),
            "edges": edges,
            "U": U,
            "Oloads": tuple((v, frac(t)) for v, t in Oloads),
            "A_h": tuple((v, frac(a), frac(h)) for v, a, h in avec),
        })


if __name__ == "__main__":
    main()
