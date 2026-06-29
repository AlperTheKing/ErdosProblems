"""Check the UPO structural lemma: unique-path overlaps are intervals.

For every gamma-min connected-B max cut, if a bad edge f has a unique
shortest B-geodesic P_f, then every shortest B-geodesic Q of every bad edge
should meet P_f in a contiguous interval of P_f.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def is_contiguous_on_path(path: list[int], other: list[int]) -> bool:
    pos = {v: i for i, v in enumerate(path)}
    hits = sorted(pos[v] for v in other if v in pos)
    if len(hits) <= 1:
        return True
    return hits[-1] - hits[0] + 1 == len(hits)


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    _adj, cuts = gmins(n, edges)
    unique_rows = 0
    comparisons = 0
    for ci, side_s in enumerate(cuts):
        st = struct_for_side(n, adj, [int(c) for c in side_s])
        if st is None:
            continue
        M, _ell, _T, _mu, cyc = st
        for f in M:
            if len(cyc[f]) != 1:
                continue
            unique_rows += 1
            path = cyc[f][0]
            for g in M:
                for qpath in cyc[g]:
                    comparisons += 1
                    if not is_contiguous_on_path(path, qpath):
                        return {
                            "graphs": 1,
                            "cuts": len(cuts),
                            "unique_rows": unique_rows,
                            "comparisons": comparisons,
                            "fail": (g6, ci, side_s, f, path, g, qpath),
                        }
    return {
        "graphs": 1 if cuts else 0,
        "cuts": len(cuts),
        "unique_rows": unique_rows,
        "comparisons": comparisons,
        "fail": None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()

    graphs = subprocess.run(
        [GENG, "-tc", str(args.n)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()

    acc = {"graphs": 0, "cuts": 0, "unique_rows": 0, "comparisons": 0}
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            iterator = ex.map(graph_probe, graphs, chunksize=args.chunksize)
            for i, res in enumerate(iterator, 1):
                for k in acc:
                    acc[k] += res[k]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
                if i % 10000 == 0:
                    print(
                        "processed",
                        i,
                        "unique_rows",
                        acc["unique_rows"],
                        "comparisons",
                        acc["comparisons"],
                        flush=True,
                    )
    else:
        for i, g6 in enumerate(graphs, 1):
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
