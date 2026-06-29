"""Check whether total extra path load is bounded by component span lengths.

For unique P_f, define extra load E=sum_{v in P_f}(S(v)-1).  For each
component C of B - V(P_f), let spanlen(C)=hi-lo+1.  Candidate lemma:

    E <= sum_C spanlen(C).

Together with |C| >= spanlen(C), this would imply direct UPO.
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
            margin = span_sum - extra
            rec = (margin, repr(g6), ci, side_s, f, path, str(extra), str(span_sum), infos)
            if worst is None or margin < worst[0]:
                worst = rec
            if margin < 0:
                return {"rows": rows, "worst": worst, "fail": rec}
    return {"rows": rows, "worst": worst, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    rows = 0
    worst = None
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                rows += res["rows"]
                if res["worst"] and (worst is None or res["worst"][0] < worst[0]):
                    worst = res["worst"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            rows += res["rows"]
            if res["worst"] and (worst is None or res["worst"][0] < worst[0]):
                worst = res["worst"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, "rows", rows)
    print("worst", worst)
    print("fail", fail)


if __name__ == "__main__":
    main()
