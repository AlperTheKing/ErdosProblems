"""Exact diagnostic for a support-Hall strengthening of P5.

For singleton overload O={o}, define psi(o)=1 and
psi(q)=a_q/(N-4a_q).  P5 is equivalent to

    sum_f c_f <= N

where

    c_f = x_f^2 + sum_{q != o} psi(q) * (ell(f)-4*x_f) * p_f(q),
    x_f = p_f(o).

This diagnostic tests the stronger Hall-type condition

    sum_{f in F'} c_f <= | union_{f in F'} supp(p_f) |

for every subset F' of bad edges, when the number of bad edges is small
enough to enumerate all subsets.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as F
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

from _h import GENG, dec
from _angleD_O1 import gmin_sides
from _test_fullg import build_K
from _satzmu_conn import struct_for_side


MAX_BAD_EDGES = 24


def check_config(n, adj, side):
    r = build_K(adj, side, n)
    if r is None:
        return None
    K, T = r
    O = [v for v in range(n) if T[v] > n]
    if len(O) != 1:
        return None
    o = O[0]
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, _T2, _mu, cyc = st
    if len(M) > MAX_BAD_EDGES:
        return {"status": "skip", "m": len(M)}

    psi = [F(0) for _ in range(n)]
    psi[o] = F(1)
    for q in range(n):
        if q == o:
            continue
        a = K[o][q]
        if a > 0:
            psi[q] = a / (F(n) - 4 * a)

    demands = []
    supports = []
    for f in M:
        Ps = cyc[f]
        pf = [F(0) for _ in range(n)]
        supp = set()
        for P in Ps:
            for v in P:
                pf[v] += F(1, len(Ps))
                supp.add(v)
        x = pf[o]
        c = x * x + sum(
            psi[q] * (ell[f] - 4 * x) * pf[q] for q in range(n) if q != o
        )
        demands.append(c)
        supports.append(supp)

    worst = None
    m = len(M)
    for mask in range(1, 1 << m):
        demand = sum((demands[i] for i in range(m) if (mask >> i) & 1), F(0))
        union = set()
        for i in range(m):
            if (mask >> i) & 1:
                union |= supports[i]
        slack = F(len(union)) - demand
        rec = (slack, mask, demand, len(union), [M[i] for i in range(m) if (mask >> i) & 1])
        if worst is None or slack < worst[0]:
            worst = rec
        if slack < 0:
            return {
                "status": "fail",
                "o": o,
                "worst": worst,
                "T": T,
                "M": M,
                "demands": demands,
            }
    return {"status": "ok", "o": o, "worst": worst, "m": m}


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    total = 0
    skips = 0
    first = None
    worst = None
    for side in sides:
        r = check_config(n, adj, side)
        if r is None:
            continue
        if r["status"] == "skip":
            skips += 1
            continue
        total += 1
        if r["status"] == "fail":
            first = (g6, "".join(map(str, side)), r)
            break
        if worst is None or r["worst"][0] < worst[0]:
            worst = (r["worst"][0], g6, "".join(map(str, side)), r)
    return {"g6": g6, "total": total, "skips": skips, "first": first, "worst": worst}


def main():
    workers = min(61, os.cpu_count() or 1)
    graphs = subprocess.run(
        [GENG, "-tc", "11"], capture_output=True, text=True, check=True
    ).stdout.split()
    total = 0
    skips = 0
    first = None
    worst = None
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            r = fut.result()
            done += 1
            total += r["total"]
            skips += r["skips"]
            if r["first"] is not None and first is None:
                first = r["first"]
                break
            if r["worst"] is not None and (worst is None or r["worst"][0] < worst[0]):
                worst = r["worst"]

    print(f"workers {workers}")
    print(f"done_graphs {done}")
    print(f"configs {total}")
    print(f"skips {skips}")
    print(f"first {first}")
    print(f"worst {worst}")


if __name__ == "__main__":
    main()
