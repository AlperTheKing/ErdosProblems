"""Collect equality cases for the direct unique-path overlap bound.

For a unique bad edge f, direct UPO is

    sum_g <p_f,p_g> <= N.

This script records rows where equality holds and basic structure of the
other geodesics depositing mass onto the unique path P_f.
"""
from __future__ import annotations

import argparse
import subprocess
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    ctr = Counter()
    examples = []
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
            total = F(0)
            contribs = []
            for g in M:
                k = len(cyc[g])
                hit_sum = 0
                hit_paths = []
                for qpath in cyc[g]:
                    hits = [v for v in qpath if v in pset]
                    hit_sum += len(hits)
                    if hits:
                        hit_paths.append((qpath, hits))
                val = F(hit_sum, k)
                total += val
                if g != f and val:
                    contribs.append((g, k, val, hit_paths))
            margin = F(n) - total
            ctr[("unique_rows",)] += 1
            if margin == 0:
                ctr[("equal_rows",)] += 1
                ctr[("path_len", len(path))] += 1
                ctr[("contributors", len(contribs))] += 1
                nested = all(all(set(qpath).issubset(pset) for qpath, _hits in hit_paths) for _g, _k, _val, hit_paths in contribs)
                ctr[("all_contrib_paths_nested", nested)] += 1
                if len(examples) < 10:
                    examples.append((repr(g6), ci, side_s, f, path, str(total), [(g, k, str(val), hit_paths) for g, k, val, hit_paths in contribs]))
    return ctr, examples


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    total = Counter()
    examples = []
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for ctr, exs in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                total.update(ctr)
                if len(examples) < 10:
                    examples.extend(exs[: 10 - len(examples)])
    else:
        for g6 in graphs:
            ctr, exs = graph_probe(g6)
            total.update(ctr)
            if len(examples) < 10:
                examples.extend(exs[: 10 - len(examples)])
    print("N", args.n)
    for k, v in sorted(total.items(), key=lambda kv: str(kv[0])):
        print(k, v)
    print("examples")
    for ex in examples:
        print(ex)


if __name__ == "__main__":
    main()
