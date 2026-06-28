"""Classify bottleneck subset sizes for the Q-CAP sublemma.

Q-CAP for fixed row o and bad-edge subset H:

    sum_{q in Q} psi_o(q) A_H(q) <= sum_{q in Q} min(1,A_H(q)).

This dumps the subset-size histogram for the minimum Q-CAP slack.
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


def qcap_slack(mask, Xs, pfs, psi, Q):
    A = {q: F(0) for q in Q}
    for i in range(len(pfs)):
        if (mask >> i) & 1:
            Xi = Xs[i]
            if Xi:
                pf = pfs[i]
                for q in Q:
                    if pf[q]:
                        A[q] += Xi * pf[q]
    lhs = sum(psi[q] * A[q] for q in Q)
    rhs = sum(min(F(1), A[q]) for q in Q)
    return rhs - lhs, lhs, rhs, tuple((q, A[q], psi[q]) for q in Q if A[q] or psi[q])


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    total = fail = 0
    hist = {}
    first = None
    worst = None
    examples = []
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
            best = None
            for mask in range(1, 1 << len(M)):
                slack, lhs, rhs, Avec = qcap_slack(mask, Xs, pfs, psi, Q)
                if lhs == 0 and rhs == 0:
                    continue
                rec = (slack, mask, lhs, rhs, Avec)
                if best is None or rec < best:
                    best = rec
                if slack < 0:
                    fail += 1
                    if first is None:
                        first = (g6, "".join(map(str, side)), o, mask, lhs, rhs, [M[i] for i in range(len(M)) if (mask >> i) & 1], Avec)
            if best is None:
                continue
            total += 1
            sz = best[1].bit_count()
            key = "full" if sz == len(M) else sz
            hist[key] = hist.get(key, 0) + 1
            rec = (best[0], g6, "".join(map(str, side)), o, len(M), best)
            if worst is None or rec < worst:
                worst = rec
            if len(examples) < 12 and key != "full":
                examples.append(rec)
    return total, fail, hist, first, worst, examples


def merge(a, b):
    for k, v in b.items():
        a[k] = a.get(k, 0) + v


def frac(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def main():
    workers = min(61, os.cpu_count() or 1)
    graphs = subprocess.run([GENG, "-tc", "11"], capture_output=True, text=True, check=True).stdout.split()
    total = fail = 0
    hist = {}
    first = None
    worst = None
    examples = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            t, f, h, ex, w, es = fut.result()
            total += t
            fail += f
            merge(hist, h)
            if ex is not None and first is None:
                first = ex
            if w is not None and (worst is None or w < worst):
                worst = w
            for e in es:
                if len(examples) < 12:
                    examples.append(e)
    print("workers", workers)
    print("configs", total)
    print("fails", fail)
    print("hist", hist)
    print("first", first)
    if worst:
        slack, g6, side, o, m, best = worst
        print("worst", {
            "slack": frac(slack),
            "g6": g6,
            "side": side,
            "o": o,
            "M_size": m,
            "subset_size": best[1].bit_count(),
            "lhs": frac(best[2]),
            "rhs": frac(best[3]),
        })
    print("examples", examples[:12])


if __name__ == "__main__":
    main()
