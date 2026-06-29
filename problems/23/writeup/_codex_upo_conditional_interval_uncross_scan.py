"""Check the conditional interval uncrossing needed for UPO Hall.

We do not need every minimum Hall set to be an interval.  To prove Hall from
interval Hall it is enough that every subset I with h(I)<=0 has an interval J
with h(J)<=h(I).  Then a negative Hall violation would have a negative
interval violation.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def component_info(n: int, adj, side, path: list[int]):
    pset = set(path)
    pos = {v: i for i, v in enumerate(path)}
    rest = [v for v in range(n) if v not in pset]
    parent = {v: v for v in rest}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for u in rest:
        for v in adj[u]:
            if v in pset:
                continue
            if side[u] != side[v]:
                union(u, v)

    comps: dict[int, list[int]] = {}
    for v in rest:
        comps.setdefault(find(v), []).append(v)

    infos = []
    for vertices in comps.values():
        attach = set()
        for u in vertices:
            for x in adj[u]:
                if x in pset and side[u] != side[x]:
                    attach.add(pos[x])
        if attach:
            infos.append((min(attach), max(attach), len(vertices), tuple(sorted(vertices)), tuple(sorted(attach))))
    return infos


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    rows = 0
    checked_subsets = 0
    zero_subsets = 0
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, _T, _mu, cyc = st
        S = [F(0)] * n
        for g in M:
            k = len(cyc[g])
            seen: dict[int, F] = {}
            for path in cyc[g]:
                for v in path:
                    seen[v] = seen.get(v, F(0)) + F(1, k)
            for v, weight in seen.items():
                S[v] += weight

        for f in M:
            if len(cyc[f]) != 1:
                continue
            rows += 1
            path = cyc[f][0]
            L = len(path)
            d = [S[v] - 1 for v in path]
            infos = component_info(n, adj, side, path)

            def slack(mask: int) -> F:
                lhs = sum(d[i] for i in range(L) if (mask >> i) & 1)
                rhs = sum(
                    cap
                    for lo, hi, cap, _vs, _att in infos
                    if any((mask >> i) & 1 for i in range(lo, hi + 1))
                )
                return F(rhs) - lhs

            interval_slacks = []
            for a in range(L):
                mask = 0
                for b in range(a, L):
                    mask |= 1 << b
                    interval_slacks.append((mask, slack(mask)))

            for mask in range(1, 1 << L):
                h = slack(mask)
                if h <= 0:
                    checked_subsets += 1
                    if h == 0:
                        zero_subsets += 1
                    if min(v for _m, v in interval_slacks) > h:
                        return {
                            "rows": rows,
                            "checked_subsets": checked_subsets,
                            "zero_subsets": zero_subsets,
                            "fail": (
                                g6,
                                ci,
                                side_s,
                                f,
                                path,
                                mask,
                                str(h),
                                min((v, m) for m, v in interval_slacks),
                                [str(x) for x in d],
                                infos,
                            ),
                        }
    return {"rows": rows, "checked_subsets": checked_subsets, "zero_subsets": zero_subsets, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    acc = {"rows": 0, "checked_subsets": 0, "zero_subsets": 0}
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                for k in acc:
                    acc[k] += res[k]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            for k in acc:
                acc[k] += res[k]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, acc)
    print("fail", fail)


if __name__ == "__main__":
    main()
