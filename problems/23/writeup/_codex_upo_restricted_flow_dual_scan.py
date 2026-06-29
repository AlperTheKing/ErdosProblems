"""Inspect dual Hall subsets for restricted interval flow."""
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


def graph_probe(g6: str, max_nodes: int):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for x, y in edges:
        adj[x].add(y)
        adj[y].add(x)
    _adj, cuts = gmins(n, edges)
    checked = 0
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
            pos = {v: i for i, v in enumerate(path)}
            infos = component_info(n, adj, side, path)
            L = len(path)
            for a in range(L):
                for b in range(a, L):
                    nodes = []
                    for g in M:
                        if g == f:
                            continue
                        den = len(cyc[g])
                        for qpath in cyc[g]:
                            hits = sorted(pos[v] for v in qpath if v in pos and a <= pos[v] <= b)
                            if hits:
                                touched = tuple(
                                    j for j, (lo, hi, _cap, _vs, _att) in enumerate(infos) if not (hi < a or b < lo)
                                )
                                # In the restricted flow every demand node touches the same component set: those hitting target.
                                nodes.append((F(len(hits), den), g, tuple(qpath), tuple(hits), touched))
                    if 1 < len(nodes) <= max_nodes:
                        checked += 1
                        # Since all nodes touch the same component set, only the all-node subset can bind.
                        total = sum((node[0] for node in nodes), F(0))
                        cap = sum(F(infos[j][2]) for j in nodes[0][4])
                        if total == cap:
                            return {
                                "checked": checked,
                                "result": (g6, ci, side_s, f, path, (a, b), str(total), str(cap), nodes, infos),
                            }
    return {"checked": checked, "result": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    ap.add_argument("--max-nodes", type=int, default=8)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    checked = 0
    result = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(lambda g: graph_probe(g, args.max_nodes), graphs, chunksize=args.chunksize):
                checked += res["checked"]
                if res["result"] is not None:
                    result = res["result"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6, args.max_nodes)
            checked += res["checked"]
            if res["result"] is not None:
                result = res["result"]
                break
    print("N", args.n, "checked", checked)
    print("result", result)


if __name__ == "__main__":
    main()
