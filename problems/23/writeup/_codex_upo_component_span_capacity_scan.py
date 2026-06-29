"""Check the component span-capacity lemma for unique paths.

Candidate lemma: if P_f is the unique shortest B-geodesic for f, and C is a
component of B - V(P_f) with attachment span [lo,hi] on P_f, then

    |C| >= hi - lo + 1.

The heuristic is that a smaller component would contain a B-detour between
the endpoint attachments that is no longer than the P_f segment, contradicting
uniqueness.  This script exact-checks the lemma on the census.
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
    rows = 0
    comps = 0
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
            for lo, hi, cap, vertices, attach in component_info(n, adj, side, path):
                comps += 1
                if cap < hi - lo + 1:
                    return {
                        "rows": rows,
                        "comps": comps,
                        "fail": (repr(g6), ci, side_s, f, path, (lo, hi, cap, vertices, attach)),
                    }
    return {"rows": rows, "comps": comps, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    acc = {"rows": 0, "comps": 0}
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                acc["rows"] += res["rows"]
                acc["comps"] += res["comps"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            acc["rows"] += res["rows"]
            acc["comps"] += res["comps"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, acc)
    print("fail", fail)


if __name__ == "__main__":
    main()
