"""Audit a possible UPO proof shortcut.

For a unique bad-edge geodesic P_f, every other shortest geodesic Q meets P_f
in a contiguous interval.  This checks whether the vertices of Q outside P_f
always lie in one component of the cut graph B - V(P_f).
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def component_map(n: int, adj, side, path: list[int]) -> dict[int, int]:
    pset = set(path)
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
    return {v: find(v) for v in rest}


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    _adj, cuts = gmins(n, edges)
    checked = 0
    multi = 0
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, _T, _mu, cyc = st
        for f in M:
            if len(cyc[f]) != 1:
                continue
            path = cyc[f][0]
            pset = set(path)
            cmap = component_map(n, adj, side, path)
            for g in M:
                for qpath in cyc[g]:
                    off = [v for v in qpath if v not in pset]
                    if not off:
                        continue
                    checked += 1
                    roots = {cmap[v] for v in off}
                    if len(roots) > 1:
                        multi += 1
                        return {
                            "graphs": 1,
                            "cuts": len(cuts),
                            "checked": checked,
                            "multi": multi,
                            "fail": (g6, ci, side_s, f, path, g, qpath, off, sorted(roots)),
                        }
    return {"graphs": 1 if cuts else 0, "cuts": len(cuts), "checked": checked, "multi": multi, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    acc = {"graphs": 0, "cuts": 0, "checked": 0, "multi": 0}
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
