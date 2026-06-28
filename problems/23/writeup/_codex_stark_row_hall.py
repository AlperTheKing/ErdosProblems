"""Exact Hall diagnostic for the STAR-K-multi row-sum inequality.

For each overloaded row o in O, set

    s_q = sum_{o' in O} K[o',q],  R_q=N-T(q),
    psi_o(q) = K[o,q] / (R_q+s_q).

The row-sum inequality

    sum_q K[o,q] R_q/(R_q+s_q) >= T(o)-N

is equivalent to the full-set packing inequality

    sum_f X_f * (p_f(o) + sum_q psi_o(q) p_f(q)) <= N,

where X_f=sum_{o' in O}p_f(o').  This script tests the stronger
support-Hall condition for these row demands.
"""
from fractions import Fraction as F
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

from _angleD_O1 import gmin_sides
from _codex_p5_hall_flow import exact_hall_flow
from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _test_fullg import build_K


def row_hall_configs(n, adj, side):
    r = build_K(adj, side, n)
    if r is None:
        return []
    K, T = r
    O = [v for v in range(n) if T[v] > n]
    if not O:
        return []
    Q = [v for v in range(n) if T[v] <= n]
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, _ell, _T2, _mu, cyc = st

    pf_by_f = []
    supports = []
    for f in M:
        Ps = cyc[f]
        pf = [F(0) for _ in range(n)]
        supp = set()
        for P in Ps:
            for v in P:
                pf[v] += F(1, len(Ps))
                supp.add(v)
        pf_by_f.append(pf)
        supports.append(supp)

    out = []
    for o in O:
        psi = [F(0) for _ in range(n)]
        denbad = []
        for q in Q:
            s = sum(K[op][q] for op in O)
            R = F(n) - T[q]
            den = R + s
            if den <= 0:
                denbad.append((q, R, s, den))
            elif K[o][q] > 0:
                psi[q] = K[o][q] / den
        if denbad:
            out.append({"status": "denbad", "o": o, "denbad": denbad})
            continue
        demands = []
        for pf in pf_by_f:
            X = sum(pf[op] for op in O)
            c = X * (pf[o] + sum(psi[q] * pf[q] for q in Q))
            demands.append(c)
        slack, cut_bad, cut_vertices, flow, total = exact_hall_flow(n, demands, supports)
        out.append(
            {
                "status": "ok" if flow == total else "fail",
                "o": o,
                "slack": slack,
                "cut_bad": cut_bad,
                "cut_vertices": cut_vertices,
                "flow": flow,
                "total": total,
                "M": M,
                "T": T,
                "O": O,
            }
        )
    return out


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    total = fails = 0
    first = None
    for side in sides:
        for r in row_hall_configs(n, adj, side):
            total += 1
            if r["status"] != "ok":
                fails += 1
                if first is None:
                    first = (g6, "".join(map(str, side)), r)
    return total, fails, first


def main():
    workers = min(61, os.cpu_count() or 1)
    graphs = subprocess.run(
        [GENG, "-tc", "11"], capture_output=True, text=True, check=True
    ).stdout.split()
    total = fails = 0
    first = None
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            t, f, ex = fut.result()
            done += 1
            total += t
            fails += f
            if ex is not None and first is None:
                first = ex
                break
    print("workers", workers)
    print("done_graphs", done)
    print("configs", total)
    print("fails", fails)
    print("first", first)


if __name__ == "__main__":
    main()
