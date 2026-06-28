"""Dump N=11 STAR-K-multi row-Hall cases whose tightest subset has size 3."""
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


def row_data(n, adj, side):
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
    M, ell, _T2, _mu, cyc = st
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
        Xs = []
        for pf in pfs:
            X = sum(pf[op] for op in O)
            Xs.append(X)
            demands.append(X * (pf[o] + sum(psi[q] * pf[q] for q in Q)))
        out.append((o, O, Q, T, M, ell, pfs, supports, demands, Xs, psi))
    return out


def best_subset(demands, supports):
    m = len(demands)
    best = None
    for mask in range(1, 1 << m):
        d = sum((demands[i] for i in range(m) if (mask >> i) & 1), F(0))
        U = set()
        for i in range(m):
            if (mask >> i) & 1:
                U |= supports[i]
        slack = F(len(U)) - d
        rec = (slack, mask, d, len(U), tuple(sorted(U)))
        if best is None or rec < best:
            best = rec
    return best


def frac(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    hits = []
    for side in sides:
        side_s = "".join(map(str, side))
        for o, O, Q, T, M, ell, pfs, supports, demands, Xs, psi in row_data(n, adj, side):
            best = best_subset(demands, supports)
            if best is None or best[1].bit_count() != 3 or len(M) == 3:
                continue
            slack, mask, d, usize, U = best
            idxs = [i for i in range(len(M)) if (mask >> i) & 1]
            records = []
            for i in idxs:
                records.append(
                    {
                        "i": i,
                        "edge": M[i],
                        "ell": ell[M[i]],
                        "X": frac(Xs[i]),
                        "demand": frac(demands[i]),
                        "support": tuple(sorted(supports[i])),
                        "pfO": {op: frac(pfs[i][op]) for op in O if pfs[i][op]},
                    }
                )
            hits.append(
                {
                    "g6": g6,
                    "side": side_s,
                    "o": o,
                    "O": O,
                    "Q": Q,
                    "T_O": {op: frac(T[op]) for op in O},
                    "M_size": len(M),
                    "slack": frac(slack),
                    "demand": frac(d),
                    "union_size": usize,
                    "union": U,
                    "bad_edges": records,
                }
            )
    return hits


def main():
    workers = min(61, os.cpu_count() or 1)
    graphs = subprocess.run([GENG, "-tc", "11"], capture_output=True, text=True, check=True).stdout.split()
    hits = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            hits.extend(fut.result())
    hits.sort(key=lambda h: (F(h["slack"]), h["g6"], h["side"], h["o"]))
    print("workers", workers)
    print("triple_hits", len(hits))
    for h in hits[:30]:
        print(h)
    if len(hits) > 30:
        print("remaining_hits_omitted", len(hits) - 30)


if __name__ == "__main__":
    main()
