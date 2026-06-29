"""Stats for the pointwise UNIQUE-BASE candidate.

For a unique row f with unique path P, define for every path position i:
  uload(i): number of unique-geodesic contributors g != f through P[i];
  cover(i): number of off-path B-component spans containing i.

This script records the largest uload, the largest tight uload with
uload == cover, and the first witnesses.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _codex_upo_conditional_interval_uncross_scan import component_info


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    rows = positions = 0
    max_u = (-1, None)
    max_tight_u = (-1, None)
    min_margin = (10**9, None)
    hist: dict[int, int] = {}
    tight_hist: dict[int, int] = {}

    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, _T, _mu, cyc = st
        for f in M:
            if len(cyc[f]) != 1:
                continue
            rows += 1
            path = cyc[f][0]
            pos = {v: i for i, v in enumerate(path)}
            infos = component_info(n, adj, side, path)
            cover = [
                sum(1 for lo, hi, _cap, _vs, _att in infos if lo <= i <= hi)
                for i in range(len(path))
            ]
            uload = [0] * len(path)
            labels = [[] for _ in path]
            for g in M:
                if g == f or len(cyc[g]) != 1:
                    continue
                qpath = cyc[g][0]
                for v in qpath:
                    if v in pos:
                        i = pos[v]
                        uload[i] += 1
                        labels[i].append((g, tuple(qpath)))

            for i, (u, c) in enumerate(zip(uload, cover)):
                positions += 1
                hist[u] = hist.get(u, 0) + 1
                rec = (repr(g6), ci, side_s, f, tuple(path), i, path[i], u, c, tuple(infos), tuple(labels[i]))
                if u > max_u[0]:
                    max_u = (u, rec)
                margin = c - u
                if margin < min_margin[0]:
                    min_margin = (margin, rec)
                if u == c:
                    tight_hist[u] = tight_hist.get(u, 0) + 1
                    if u > max_tight_u[0]:
                        max_tight_u = (u, rec)
                if margin < 0:
                    return {
                        "rows": rows,
                        "positions": positions,
                        "hist": hist,
                        "tight_hist": tight_hist,
                        "max_u": max_u,
                        "max_tight_u": max_tight_u,
                        "min_margin": min_margin,
                        "fail": rec,
                    }

    return {
        "rows": rows,
        "positions": positions,
        "hist": hist,
        "tight_hist": tight_hist,
        "max_u": max_u,
        "max_tight_u": max_tight_u,
        "min_margin": min_margin,
        "fail": None,
    }


def merge_counts(dst: dict[int, int], src: dict[int, int]) -> None:
    for k, v in src.items():
        dst[k] = dst.get(k, 0) + v


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()

    rows = positions = 0
    hist: dict[int, int] = {}
    tight_hist: dict[int, int] = {}
    max_u = (-1, None)
    max_tight_u = (-1, None)
    min_margin = (10**9, None)
    fail = None

    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            it = ex.map(graph_probe, graphs, chunksize=args.chunksize)
            for res in it:
                rows += res["rows"]
                positions += res["positions"]
                merge_counts(hist, res["hist"])
                merge_counts(tight_hist, res["tight_hist"])
                if res["max_u"][0] > max_u[0]:
                    max_u = res["max_u"]
                if res["max_tight_u"][0] > max_tight_u[0]:
                    max_tight_u = res["max_tight_u"]
                if res["min_margin"][0] < min_margin[0]:
                    min_margin = res["min_margin"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            rows += res["rows"]
            positions += res["positions"]
            merge_counts(hist, res["hist"])
            merge_counts(tight_hist, res["tight_hist"])
            if res["max_u"][0] > max_u[0]:
                max_u = res["max_u"]
            if res["max_tight_u"][0] > max_tight_u[0]:
                max_tight_u = res["max_tight_u"]
            if res["min_margin"][0] < min_margin[0]:
                min_margin = res["min_margin"]
            if res["fail"] is not None:
                fail = res["fail"]
                break

    print("N", args.n, "rows", rows, "positions", positions)
    print("hist", sorted(hist.items()))
    print("tight_hist", sorted(tight_hist.items()))
    print("max_u", max_u)
    print("max_tight_u", max_tight_u)
    print("min_margin", min_margin)
    print("fail", fail)


if __name__ == "__main__":
    main()
