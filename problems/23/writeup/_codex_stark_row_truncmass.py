"""Test a truncated-mass strengthening of STAR-K-multi row-Hall.

For H a subset of bad edges, set

    A_H(v) = sum_{f in H} X_f p_f(v),   X_f=sum_{o in O}p_f(o).

For fixed o in O, row-Hall demand is

    D_o(H)=sum_{f in H} X_f*(p_f(o)+sum_{q in Q}psi_o(q)p_f(q)).

This script tests the stronger inequality

    D_o(H) <= sum_v min(1, A_H(v)).

It implies row-Hall because A_H is supported on union supp(p_f).
"""
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


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    total = fails = 0
    first = None
    worst = None
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
        for f in M:
            Ps = cyc[f]
            pf = [F(0) for _ in range(n)]
            for P in Ps:
                for v in P:
                    pf[v] += F(1, len(Ps))
            pfs.append(pf)
            Xs.append(sum(pf[op] for op in O))
        psis = {}
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
                if K[o][q] > 0:
                    psi[q] = K[o][q] / den
            if ok:
                psis[o] = psi
        m = len(M)
        for o, psi in psis.items():
            row_dem = [
                Xs[i] * (pfs[i][o] + sum(psi[q] * pfs[i][q] for q in Q))
                for i in range(m)
            ]
            for mask in range(1, 1 << m):
                total += 1
                demand = sum((row_dem[i] for i in range(m) if (mask >> i) & 1), F(0))
                A = [F(0) for _ in range(n)]
                for i in range(m):
                    if (mask >> i) & 1:
                        Xi = Xs[i]
                        if Xi == 0:
                            continue
                        pf = pfs[i]
                        for v in range(n):
                            if pf[v]:
                                A[v] += Xi * pf[v]
                cap = sum((min(F(1), A[v]) for v in range(n)), F(0))
                slack = cap - demand
                if worst is None or slack < worst[0]:
                    worst = (slack, g6, "".join(map(str, side)), o, mask, demand, cap)
                if slack < 0:
                    fails += 1
                    first = (g6, "".join(map(str, side)), o, mask, demand, cap, [M[i] for i in range(m) if (mask >> i) & 1], O, T)
                    return total, fails, first, worst
    return total, fails, first, worst


def main():
    workers = min(61, os.cpu_count() or 1)
    graphs = subprocess.run([GENG, "-tc", "11"], capture_output=True, text=True, check=True).stdout.split()
    total = fails = 0
    first = None
    worst = None
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            t, f, ex, w = fut.result()
            done += 1
            total += t
            fails += f
            if w is not None and (worst is None or w[0] < worst[0]):
                worst = w
            if ex is not None and first is None:
                first = ex
                break
    print("workers", workers)
    print("done_graphs", done)
    print("configs", total)
    print("fails", fails)
    print("first", first)
    print("worst", worst)


if __name__ == "__main__":
    main()
