"""Classify bottleneck subset sizes for STAR-K-multi row-Hall on N=11."""
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


def row_demands(n, adj, side):
    r = build_K(adj, side, n)
    if r is None:
        return []
    K, T = r
    O = [v for v in range(n) if T[v] > n]
    Q = [v for v in range(n) if T[v] <= n]
    if not O:
        return []
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, _ell, _T2, _mu, cyc = st
    pfs = []
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
        supports.append(supp)
    out = []
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
        if not ok:
            continue
        demands = []
        for pf in pfs:
            X = sum(pf[op] for op in O)
            demands.append(X * (pf[o] + sum(psi[q] * pf[q] for q in Q)))
        out.append((o, M, demands, supports))
    return out


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    total = 0
    hist = {}
    examples = []
    worst = None
    for side in sides:
        for o, M, demands, supports in row_demands(n, adj, side):
            total += 1
            m = len(M)
            best = None
            for mask in range(1, 1 << m):
                d = sum((demands[i] for i in range(m) if (mask >> i) & 1), F(0))
                U = set()
                for i in range(m):
                    if (mask >> i) & 1:
                        U |= supports[i]
                slack = F(len(U)) - d
                rec = (slack, mask, d, len(U))
                if best is None or slack < best[0]:
                    best = rec
            if best is None:
                continue
            sz = best[1].bit_count()
            full = sz == m
            key = "full" if full else sz
            hist[key] = hist.get(key, 0) + 1
            if len(examples) < 10 and not full:
                examples.append((g6, "".join(map(str, side)), o, m, best, [M[i] for i in range(m) if (best[1] >> i) & 1]))
            if worst is None or best[0] < worst[0]:
                worst = (best[0], g6, "".join(map(str, side)), o, m, best)
    return total, hist, examples, worst


def main():
    workers = min(61, os.cpu_count() or 1)
    graphs = subprocess.run([GENG, "-tc", "11"], capture_output=True, text=True, check=True).stdout.split()
    total = 0
    hist = {}
    examples = []
    worst = None
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            t, h, ex, w = fut.result()
            total += t
            for k, v in h.items():
                hist[k] = hist.get(k, 0) + v
            for e in ex:
                if len(examples) < 10:
                    examples.append(e)
            if w is not None and (worst is None or w[0] < worst[0]):
                worst = w
    print("workers", workers)
    print("configs", total)
    print("hist", hist)
    print("examples", examples)
    print("worst", worst)


if __name__ == "__main__":
    main()
