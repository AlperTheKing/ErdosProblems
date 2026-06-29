"""Exhaustive Hall-subset stats for the geodesic-interval packing flow.

Demand nodes are (g,Q) intervals Q cap P_f with weight |Q cap P_f|/|cyc(g)|.
Component nodes are off-path B-components with capacity |C|.  A demand node is
adjacent to a component when their intervals intersect.  This script examines
the Hall slack over all demand-node subsets when the number of demands is
small enough.
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
from _codex_upo_geodesic_interval_flow_scan import component_info, overlap_interval


def graph_probe(args):
    g6, max_demands = args
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
            infos = component_info(n, adj, side, path)
            demands = []
            for g in M:
                if g == f:
                    continue
                den = len(cyc[g])
                for qpath in cyc[g]:
                    ov = overlap_interval(path, qpath)
                    if ov is None:
                        continue
                    lo, hi, length = ov
                    demands.append((lo, hi, F(length, den), g, qpath))
            ctr[("rows",)] += 1
            ctr[("demands", len(demands))] += 1
            if not demands or len(demands) > max_demands:
                continue
            ctr[("exhausted_rows",)] += 1
            best = None
            tight_count = 0
            for mask in range(1, 1 << len(demands)):
                lhs = F(0)
                touched = set()
                subset_size = 0
                for i, (lo, hi, dem, _g, _qpath) in enumerate(demands):
                    if (mask >> i) & 1:
                        subset_size += 1
                        lhs += dem
                        for j, (c_lo, c_hi, _cap, _vs, _att) in enumerate(infos):
                            if not (c_hi < lo or hi < c_lo):
                                touched.add(j)
                rhs = sum(F(infos[j][2]) for j in touched)
                slack = rhs - lhs
                if best is None or slack < best[0]:
                    best = (slack, mask, subset_size, len(touched), lhs, rhs)
                if slack == 0:
                    tight_count += 1
            if best is not None:
                ctr[("min_slack", str(best[0]))] += 1
                ctr[("best_subset_size", best[2])] += 1
                ctr[("best_touched_components", best[3])] += 1
                ctr[("has_tight_subset", tight_count > 0)] += 1
                if len(examples) < 8 and best[0] == 0:
                    chosen = [demands[i] for i in range(len(demands)) if (best[1] >> i) & 1]
                    touched_infos = [
                        infos[j]
                        for j in range(len(infos))
                        if any(not (infos[j][1] < lo or hi < infos[j][0]) for lo, hi, _dem, _g, _q in chosen)
                    ]
                    examples.append((repr(g6), ci, side_s, f, path, best, chosen, touched_infos))
    return ctr, examples


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--max-demands", type=int, default=16)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    total = Counter()
    examples = []
    items = ((g, args.max_demands) for g in graphs)
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for ctr, exs in ex.map(graph_probe, items, chunksize=args.chunksize):
                total.update(ctr)
                if len(examples) < 8:
                    examples.extend(exs[: 8 - len(examples)])
    else:
        for item in items:
            ctr, exs = graph_probe(item)
            total.update(ctr)
            if len(examples) < 8:
                examples.extend(exs[: 8 - len(examples)])
    print("N", args.n)
    for k, v in sorted(total.items(), key=lambda kv: str(kv[0])):
        print(k, v)
    print("examples")
    for ex in examples:
        print(ex)


if __name__ == "__main__":
    main()
