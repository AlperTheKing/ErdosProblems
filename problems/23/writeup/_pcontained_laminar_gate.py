"""Check laminarity/noncrossing of P-contained bad rows inside a unique row.

For a unique row f with path P, collect every bad row g!=f that has a shortest
geodesic wholly contained in P.  Such a geodesic is a subpath interval [a,b] on
P.  This gate checks whether these P-contained intervals ever cross.

This is narrower than _codex_upo_overlap_laminar_scan.py, which includes
non-contained overlap intervals and fails at N=11.
"""

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def graph_probe(graph6):
    n, edges = dec(graph6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    rows = 0
    intervals_checked = 0
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        bad_edges, _ell, _T, _mu, cyc = st
        for f in bad_edges:
            if len(cyc[f]) != 1:
                continue
            rows += 1
            path = cyc[f][0]
            pset = set(path)
            pos = {v: i for i, v in enumerate(path)}
            intervals = []
            for g in bad_edges:
                if g == f:
                    continue
                for q in cyc[g]:
                    if set(q) <= pset:
                        inds = sorted(pos[v] for v in q)
                        intervals.append((inds[0], inds[-1], g, tuple(q)))
            intervals_checked += len(intervals)
            for i in range(len(intervals)):
                l1, r1, g1, q1 = intervals[i]
                for j in range(i + 1, len(intervals)):
                    l2, r2, g2, q2 = intervals[j]
                    if (l1 < l2 < r1 < r2) or (l2 < l1 < r2 < r1):
                        return {
                            "rows": rows,
                            "intervals": intervals_checked,
                            "fail": (graph6, ci, side_s, f, path, intervals[i], intervals[j]),
                        }
    return {"rows": rows, "intervals": intervals_checked, "fail": None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    acc = {"rows": 0, "intervals": 0}
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                acc["rows"] += res["rows"]
                acc["intervals"] += res["intervals"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for graph6 in graphs:
            res = graph_probe(graph6)
            acc["rows"] += res["rows"]
            acc["intervals"] += res["intervals"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, acc)
    print("fail", fail)


if __name__ == "__main__":
    main()
