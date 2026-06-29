"""Audit shape of extra demand d_i=S(x_i)-1 along unique paths."""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def is_monotone(xs: list[F]) -> bool:
    return all(xs[i] <= xs[i + 1] for i in range(len(xs) - 1)) or all(xs[i] >= xs[i + 1] for i in range(len(xs) - 1))


def is_unimodal(xs: list[F]) -> bool:
    n = len(xs)
    for p in range(n):
        if all(xs[i] <= xs[i + 1] for i in range(p)) and all(xs[i] >= xs[i + 1] for i in range(p, n - 1)):
            return True
    return False


def is_valley(xs: list[F]) -> bool:
    n = len(xs)
    for p in range(n):
        if all(xs[i] >= xs[i + 1] for i in range(p)) and all(xs[i] <= xs[i + 1] for i in range(p, n - 1)):
            return True
    return False


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    rows = 0
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
            d = [S[v] - 1 for v in path]
            if not is_monotone(d):
                return {"rows": rows, "fail": ("monotone", g6, ci, side_s, f, path, [str(x) for x in d])}
    return {"rows": rows, "fail": None}


def graph_probe_unimodal(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    rows = 0
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
            d = [S[v] - 1 for v in path]
            if not (is_unimodal(d) or is_valley(d)):
                return {"rows": rows, "fail": ("unimodal_or_valley", g6, ci, side_s, f, path, [str(x) for x in d])}
    return {"rows": rows, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    ap.add_argument("--mode", choices=["monotone", "unimodal"], default="unimodal")
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    probe = graph_probe if args.mode == "monotone" else graph_probe_unimodal
    rows = 0
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(probe, graphs, chunksize=args.chunksize):
                rows += res["rows"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = probe(g6)
            rows += res["rows"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, "mode", args.mode, "rows", rows)
    print("fail", fail)


if __name__ == "__main__":
    main()
