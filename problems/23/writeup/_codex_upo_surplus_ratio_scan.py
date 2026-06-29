"""Scan the surplus part of direct UPO for unique rows.

Let extra=sum_{v in P_f}(S(v)-1).  Let span_sum=sum_C spanlen(C) and
surplus=sum_C (|C|-spanlen(C)).  Direct UPO is

    extra <= span_sum + surplus.

This script measures the positive overrun extra-span_sum against surplus.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

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
    rows = 0
    positive = 0
    worst = None
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, _T, _mu, cyc = st
        S = [F(0)] * n
        for g in M:
            den = len(cyc[g])
            seen: dict[int, F] = {}
            for qpath in cyc[g]:
                for v in qpath:
                    seen[v] = seen.get(v, F(0)) + F(1, den)
            for v, w in seen.items():
                S[v] += w
        for f in M:
            if len(cyc[f]) != 1:
                continue
            rows += 1
            path = cyc[f][0]
            extra = sum(S[v] - 1 for v in path)
            infos = component_info(n, adj, side, path)
            span_sum = sum(F(hi - lo + 1) for lo, hi, _cap, _vs, _att in infos)
            surplus = sum(F(cap - (hi - lo + 1)) for lo, hi, cap, _vs, _att in infos)
            over = extra - span_sum
            if over <= 0:
                continue
            positive += 1
            ratio = over / surplus if surplus else None
            rec = (ratio, over, surplus, repr(g6), ci, side_s, f, path, str(extra), str(span_sum), infos)
            if ratio is None or ratio > 1:
                return {"rows": rows, "positive": positive, "worst": rec, "fail": rec}
            if worst is None or ratio > worst[0]:
                worst = rec
    return {"rows": rows, "positive": positive, "worst": worst, "fail": None}


def fmt(x):
    if x is None:
        return "None"
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    rows = 0
    positive = 0
    worst = None
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                rows += res["rows"]
                positive += res["positive"]
                if res["worst"] and (worst is None or res["worst"][0] > worst[0]):
                    worst = res["worst"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            rows += res["rows"]
            positive += res["positive"]
            if res["worst"] and (worst is None or res["worst"][0] > worst[0]):
                worst = res["worst"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, "rows", rows, "positive_overrun", positive)
    print("worst", None if worst is None else [fmt(x) for x in worst])
    print("fail", fail)


if __name__ == "__main__":
    main()
