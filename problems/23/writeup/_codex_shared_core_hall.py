"""Exact test for a shared-core residual Hall strengthening of PHANTOM-HALL.

For fixed row o and active subset H, let private_H(f) be the number of
vertices used only by f inside H.  The proposed decomposition pays
min(c_f(o), private_H(f)) from private vertices and routes the residual
through vertices shared by at least two H-supports, plus the global idle bank.

Residual Hall candidate:
  for all J subset H,
    sum_{f in J} max(0, c_f(o)-private_H(f))
      <= | union_{f in J} (supp(f) cap shared_H) | + idle_o.
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


def check_side(args):
    g6, n, adj, side, max_m = args
    st = struct_for_side(n, adj, side)
    if st is None:
        return (0, None)
    M, _ell, _T2, _mu, cyc = st
    if len(M) > max_m:
        return (0, None)
    K, T = build_K(adj, side, n)
    O = [v for v in range(n) if T[v] > n]
    Q = [v for v in range(n) if T[v] <= n]
    if not O:
        return (1, None)
    pf = {f: pf_dict(cyc, f) for f in M}
    supp = {f: set(pf[f]) for f in M}
    x_f = {f: sum(pf[f].get(o, F(0)) for o in O) for f in M}
    s = {q: sum(K[o][q] for o in O) for q in Q}
    ml = list(M)
    for o in O:
        psi = {
            q: K[o][q] / (F(n) - T[q] + s[q])
            for q in Q
            if (F(n) - T[q] + s[q]) > 0
        }
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
            mult = {}
            for f in H:
                for v in supp[f]:
                    mult[v] = mult.get(v, 0) + 1
            shared = {v for v, k in mult.items() if k >= 2}
            residual = {}
            for f in H:
                private = sum(1 for v in supp[f] if mult[v] == 1)
                residual[f] = c_f[f] - private
                if residual[f] < 0:
                    residual[f] = F(0)
            hlen = len(H)
            for jmask in range(1, 1 << hlen):
                J = [H[i] for i in range(hlen) if (jmask >> i) & 1]
                demand = sum(residual[f] for f in J)
                cap = set()
                for f in J:
                    cap.update(supp[f] & shared)
                rhs = F(len(cap) + idle)
                if demand > rhs:
                    return (
                        1,
                        {
                            "g6": g6,
                            "side": format(side, f"0{n}b"),
                            "o": o,
                            "O": O,
                            "H": H,
                            "J": J,
                            "demand": demand,
                            "rhs": rhs,
                            "idle": idle,
                            "shared": sorted(shared),
                        },
                    )
    return (1, None)


def graph_tasks(n, max_m):
    geng = subprocess.Popen([GENG, "-tc", str(n)], stdout=subprocess.PIPE, text=True)
    assert geng.stdout is not None
    for line in geng.stdout:
        g6 = line.strip()
        if not g6:
            continue
        nn, edges = dec(g6)
        adj, cuts = gmins(nn, edges)
        for side in cuts:
            yield (g6, nn, adj, side, max_m)
    geng.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--max-n", type=int, default=9)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--max-m", type=int, default=14)
    args = ap.parse_args()
    total = 0
    for n in range(7, args.max_n + 1):
        tasks = list(graph_tasks(n, args.max_m))
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for checked, fail in ex.map(check_side, tasks, chunksize=16):
                total += checked
                if fail is not None:
                    print("SHARED_CORE_HALL_FAIL")
                    for k, v in fail.items():
                        print(f"{k}={v}")
                    return
        print(f"N={n} tasks={len(tasks)} cumulative_checked={total}", flush=True)
    print(f"SHARED_CORE_HALL_OK checked={total}")


if __name__ == "__main__":
    main()
