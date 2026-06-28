"""Probe blow-up-inspired layer-neighbor bounds for ROWSUM-O.

For a fixed bad edge f=ab, write
  A_i(f) = sum_{v in layer_i(f)} p_f(v) S(v)
where S(v)=sum_g p_g(v).  In one-bad-class odd-cycle blow-ups, the
intermediate A_i are bounded by adjacent part sizes via min-product.

This script tests naive generalizations:
  internal_avg: A_i <= (|I_{i-1}|+|I_{i+1}|)/2
  internal_min: A_i <= min(|I_{i-1}|,|I_{i+1}|)
  endpoint_B:  S(a)+S(b) <= deg_B(a)+deg_B(b)

These are diagnostics only; failures identify missing compensation terms.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from collections import deque

from _h import GENG, dec
from _stark1 import gmins
from _satzmu_conn import struct_for_side


def side_str(side):
    if isinstance(side, int):
        return str(side)
    return "".join(str(int(x)) for x in side)


def pf_dict(cyc, f):
    ps = cyc[f]
    k = len(ps)
    d = {}
    for path in ps:
        for v in path:
            d[v] = d.get(v, F(0)) + F(1, k)
    return d


def bdist_layers(adj, side, a):
    n = len(adj)
    dist = [-1] * n
    dist[a] = 0
    q = deque([a])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if side[u] == side[v]:
                continue
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def check_side(args):
    g6, n, adj, side, max_m = args
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, _T, _mu, cyc = st
    if len(M) > max_m:
        return None
    pf = {f: pf_dict(cyc, f) for f in M}
    S = [F(0) for _ in range(n)]
    for d in pf.values():
        for v, x in d.items():
            S[v] += x
    worst = {
        "internal_avg": (F(0), None),
        "internal_min": (F(0), None),
        "endpoint_B": (F(0), None),
    }
    for f in M:
        a, b = f
        L = ell[f]
        dist = bdist_layers(adj, side, a)
        layers = [[] for _ in range(L)]
        for v, x in pf[f].items():
            i = dist[v]
            if i < 0 or i >= L:
                return ("bad_layer", {"g6": g6, "side": side_str(side), "f": f, "v": v, "dist": i})
            layers[i].append(v)
        contrib = []
        for layer in layers:
            contrib.append(sum(pf[f].get(v, F(0)) * S[v] for v in layer))
        for i in range(1, L - 1):
            avg_cap = F(len(layers[i - 1]) + len(layers[i + 1]), 2)
            min_cap = F(min(len(layers[i - 1]), len(layers[i + 1])))
            gap = contrib[i] - avg_cap
            if gap > worst["internal_avg"][0]:
                worst["internal_avg"] = (gap, (g6, side_str(side), f, i, contrib[i], avg_cap, [len(x) for x in layers]))
            gap = contrib[i] - min_cap
            if gap > worst["internal_min"][0]:
                worst["internal_min"] = (gap, (g6, side_str(side), f, i, contrib[i], min_cap, [len(x) for x in layers]))
        degBa = sum(1 for v in adj[a] if side[v] != side[a])
        degBb = sum(1 for v in adj[b] if side[v] != side[b])
        gap = S[a] + S[b] - F(degBa + degBb)
        if gap > worst["endpoint_B"][0]:
            worst["endpoint_B"] = (gap, (g6, side_str(side), f, S[a] + S[b], degBa + degBb))
    return worst


def jobs(nmax, max_m):
    for nn in range(5, nmax + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for side in cuts:
                yield (g6, n, adj, side, max_m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--max-n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--max-m", type=int, default=14)
    args = ap.parse_args()
    acc = {
        "internal_avg": (F(0), None),
        "internal_min": (F(0), None),
        "endpoint_B": (F(0), None),
    }
    count = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for res in ex.map(check_side, jobs(args.max_n, args.max_m), chunksize=16):
            if res is None:
                continue
            if isinstance(res, tuple) and res[0] == "bad_layer":
                print("BAD_LAYER", res[1])
                return
            count += 1
            for k in acc:
                if res[k][0] > acc[k][0]:
                    acc[k] = res[k]
    print(f"checked={count}")
    for k, (gap, wit) in acc.items():
        print(f"{k}: max_gap={gap} ({float(gap):.6g})")
        if wit:
            print(f"  witness={wit}")


if __name__ == "__main__":
    main()
