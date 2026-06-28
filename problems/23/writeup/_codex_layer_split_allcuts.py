"""All-gamma-min-cut check for the symmetric layer-split certificate.

The main split probe uses the selected loads() cut.  This script enumerates
all maximum cuts, keeps connected-B cuts with minimum Gamma, and checks the
same split certificate on every such cut.
"""
from __future__ import annotations

import argparse
import subprocess
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, Bconn, bdist_restr, dec, geos, maxcut_all


def struct_for_side(n, adj, side):
    M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    if not M:
        return None
    T = [F(0)] * n
    ell = {}
    cyc = {}
    for f in M:
        paths = geos(adj, side, f[0], f[1])
        if not paths:
            return None
        cyc[f] = paths
        ell[f] = len(paths[0])
        sh = F(ell[f], len(paths))
        counts = [0] * n
        for path in paths:
            for v in path:
                counts[v] += 1
        for v, c in enumerate(counts):
            if c:
                T[v] += sh * c
    G = sum(ell[f] * ell[f] for f in M)
    return {"n": n, "adj": adj, "side": side, "M": M, "ell": ell, "cyc": cyc, "G": G}


def bdist_layers(adj, side, a):
    dist = {a: 0}
    q = deque([a])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if side[u] != side[v] and v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def split_check(info):
    n = info["n"]
    pfs = {}
    S = [F(0) for _ in range(n)]
    for f in info["M"]:
        paths = info["cyc"][f]
        nf = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        pf = {v: F(c, nf) for v, c in cnt.items()}
        pfs[f] = pf
        for v, x in pf.items():
            S[v] += x

    late = []
    for f in info["M"]:
        L = info["ell"][f]
        if L % 2 == 0:
            return False, ("even", f, L)
        dist = bdist_layers(info["adj"], info["side"], f[0])
        layers = [[] for _ in range(L)]
        for v in pfs[f]:
            i = dist[v]
            if i < 0 or i >= L:
                return False, ("bad_layer", f, v, i)
            layers[i].append(v)
        A = [sum(pfs[f][v] * S[v] for v in layers[i]) for i in range(L)]
        ok = False
        best = None
        best_data = None
        for t in range(1, L // 2 + 1):
            outer = sum(A[:t]) + sum(A[L - t :])
            center = sum(A[t : L - t])
            ogap = outer - F(2 * t * n, L)
            cgap = center - F((L - 2 * t) * n, L)
            margin = max(ogap, cgap)
            if best is None or margin < best:
                best = margin
                best_data = (t, outer, center, ogap, cgap, tuple(A), sum(A))
            if ogap <= 0 and cgap <= 0:
                ok = True
                if t != 1:
                    late.append((f, L, t, best_data))
                break
        if not ok:
            return False, (f, L, best_data)
    return True, late


def graph_probe(g6):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    candidates = []
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        M = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
        if not M:
            continue
        G = 0
        ok = True
        for u, v in M:
            d = bdist_restr(adj, side, u, v)
            if d < 0:
                ok = False
                break
            G += (d + 1) * (d + 1)
        if ok:
            candidates.append((side, G))
    if not candidates:
        return None

    gmin = min(G for _, G in candidates)
    checked = 0
    late_count = 0
    first_late = None
    for side, G in candidates:
        if G != gmin:
            continue
        info = struct_for_side(n, adj, side)
        if info is None:
            continue
        checked += 1
        ok, data = split_check(info)
        if not ok:
            return {"graphs": 1, "cuts": checked, "fail": (g6, "".join(map(str, side)), data), "late": 0, "first_late": None}
        if data:
            late_count += len(data)
            if first_late is None:
                first_late = (g6, "".join(map(str, side)), data[0])
    return {"graphs": 1, "cuts": checked, "fail": None, "late": late_count, "first_late": first_late}


def merge(acc, res):
    if res is None:
        return
    acc["graphs"] += res["graphs"]
    acc["cuts"] += res["cuts"]
    acc["late"] += res["late"]
    if res["fail"] is not None and acc["first_fail"] is None:
        acc["first_fail"] = res["fail"]
    if res["first_late"] is not None and acc["first_late"] is None:
        acc["first_late"] = res["first_late"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--max-n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()

    acc = {"graphs": 0, "cuts": 0, "late": 0, "first_fail": None, "first_late": None}
    for nn in range(5, args.max_n + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        if args.workers > 1:
            with ProcessPoolExecutor(max_workers=args.workers) as ex:
                for res in ex.map(graph_probe, out, chunksize=16):
                    merge(acc, res)
        else:
            for g6 in out:
                merge(acc, graph_probe(g6))
        print(
            f"N<={nn}: graphs={acc['graphs']} gamma_min_cuts={acc['cuts']} "
            f"first_fail={acc['first_fail']} late={acc['late']}",
            flush=True,
        )
    print("=== FINAL ===")
    print(acc)


if __name__ == "__main__":
    main()
