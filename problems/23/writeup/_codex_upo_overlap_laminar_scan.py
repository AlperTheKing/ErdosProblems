"""Check laminarity of geodesic-overlap intervals inside target corridors."""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor

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
    rows = 0
    targets = 0
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
            L = len(path)
            for a in range(L):
                for b in range(a, L):
                    intervals = []
                    for g in M:
                        if g == f:
                            continue
                        for qpath in cyc[g]:
                            hits = sorted(pos[v] for v in qpath if v in pos and a <= pos[v] <= b)
                            if hits:
                                intervals.append((hits[0], hits[-1], g, tuple(qpath)))
                    targets += 1
                    for i in range(len(intervals)):
                        l1, r1, g1, q1 = intervals[i]
                        for j in range(i + 1, len(intervals)):
                            l2, r2, g2, q2 = intervals[j]
                            if (l1 < l2 < r1 < r2) or (l2 < l1 < r2 < r1):
                                return {
                                    "rows": rows,
                                    "targets": targets,
                                    "fail": (g6, ci, side_s, f, path, (a, b), intervals[i], intervals[j]),
                                }
    return {"rows": rows, "targets": targets, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    acc = {"rows": 0, "targets": 0}
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
