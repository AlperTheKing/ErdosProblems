"""Test simple splits of the truncated-mass row-Hall inequality.

For A_H(v)=sum_{f in H} X_f p_f(v), row o demand is

    A_H(o) + sum_{q in Q} psi_o(q) A_H(q).

This tests whether the two parts are separately dominated by capped
mass on O and Q:

    A_H(o) <= sum_{v in O} min(1,A_H(v))
    sum_Q psi_o(q) A_H(q) <= sum_Q min(1,A_H(q)).

If true, truncated-mass would split into two simpler lemmas.
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


def frac(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    stats = {"configs": 0, "O_fail": 0, "Q_fail": 0}
    first = {}
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
                psi[q] = K[o][q] / den if K[o][q] else F(0)
            if ok:
                psis[o] = psi
        for o, psi in psis.items():
            for mask in range(1, 1 << len(M)):
                A = [F(0) for _ in range(n)]
                for i in range(len(M)):
                    if (mask >> i) & 1:
                        Xi = Xs[i]
                        if Xi:
                            for v, val in enumerate(pfs[i]):
                                if val:
                                    A[v] += Xi * val
                if not any(A):
                    continue
                stats["configs"] += 1
                O_lhs = A[o]
                O_rhs = sum(min(F(1), A[v]) for v in O)
                Q_lhs = sum(psi[q] * A[q] for q in Q)
                Q_rhs = sum(min(F(1), A[q]) for q in Q)
                if O_lhs > O_rhs:
                    stats["O_fail"] += 1
                    first.setdefault("O", (g6, "".join(map(str, side)), o, mask, O_lhs, O_rhs, O, [M[i] for i in range(len(M)) if (mask >> i) & 1]))
                if Q_lhs > Q_rhs:
                    stats["Q_fail"] += 1
                    first.setdefault("Q", (g6, "".join(map(str, side)), o, mask, Q_lhs, Q_rhs, O, [M[i] for i in range(len(M)) if (mask >> i) & 1]))
    return stats, first


def merge(a, b):
    for k, v in b.items():
        a[k] = a.get(k, 0) + v


def main():
    workers = min(61, os.cpu_count() or 1)
    graphs = subprocess.run([GENG, "-tc", "11"], capture_output=True, text=True, check=True).stdout.split()
    total = {}
    first = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            stats, ex = fut.result()
            merge(total, stats)
            for k, v in ex.items():
                first.setdefault(k, v)
    print("workers", workers)
    print("stats", total)
    for k, v in first.items():
        g6, side, o, mask, lhs, rhs, O, edges = v
        print(k, {
            "g6": g6,
            "side": side,
            "o": o,
            "mask": mask,
            "lhs": frac(lhs),
            "rhs": frac(rhs),
            "O": O,
            "edges": edges,
        })


if __name__ == "__main__":
    main()
