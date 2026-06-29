"""Check an outside-detour capacity candidate for UPO.

For a unique bad-edge geodesic P_f, every other shortest bad-edge geodesic Q
meets P_f in a contiguous interval I.  This script tests whether the endpoints
of I have a B-path whose internal vertices avoid P_f and whose internal
outside-vertex count is at least |I|.

The self interval Q=P_f is ignored: it is paid by P_f itself.
"""
from __future__ import annotations

import argparse
import subprocess
from collections import deque
from concurrent.futures import ProcessPoolExecutor

from _h import GENG, dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def b_distance_avoiding(
    adj: list[set[int]],
    side: list[int],
    src: int,
    dst: int,
    forbidden_internal: set[int],
) -> int | None:
    q = deque([src])
    dist = {src: 0}
    while q:
        u = q.popleft()
        for v in adj[u]:
            if side[u] == side[v]:
                continue
            if v != dst and v in forbidden_internal:
                continue
            if v not in dist:
                dist[v] = dist[u] + 1
                if v == dst:
                    return dist[v]
                q.append(v)
    return None


def interval_on(path: list[int], other: list[int]) -> tuple[int, int] | None:
    pos = {v: i for i, v in enumerate(path)}
    hits = sorted(pos[v] for v in other if v in pos)
    if not hits:
        return None
    if hits[-1] - hits[0] + 1 != len(hits):
        return None
    return hits[0], hits[-1]


def graph_probe(args_tuple: tuple[str, int]):
    g6, min_interval = args_tuple
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    _adj, cuts = gmins(n, edges)
    intervals = 0
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
            path_set = set(path)
            for g in M:
                for qpath in cyc[g]:
                    if g == f and qpath == path:
                        continue
                    ij = interval_on(path, qpath)
                    if ij is None:
                        return {
                            "graphs": 1,
                            "cuts": len(cuts),
                            "intervals": intervals,
                            "fail": ("noncontig", g6, ci, side_s, f, path, g, qpath),
                        }
                    i, j = ij
                    r = j - i + 1
                    if r < min_interval:
                        continue
                    intervals += 1
                    src, dst = path[i], path[j]
                    forbidden = path_set - {src, dst}
                    dist = b_distance_avoiding(adj, side, src, dst, forbidden)
                    # Internal outside vertices on such a detour are dist - 1.
                    if dist is None or dist - 1 < r:
                        return {
                            "graphs": 1,
                            "cuts": len(cuts),
                            "intervals": intervals,
                            "fail": (
                                "detour",
                                g6,
                                ci,
                                side_s,
                                f,
                                path,
                                g,
                                qpath,
                                (i, j),
                                r,
                                dist,
                            ),
                        }
    return {"graphs": 1 if cuts else 0, "cuts": len(cuts), "intervals": intervals, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    ap.add_argument("--min-interval", type=int, default=2)
    args = ap.parse_args()

    graphs = subprocess.run(
        [GENG, "-tc", str(args.n)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()

    acc = {"graphs": 0, "cuts": 0, "intervals": 0}
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            jobs = ((g6, args.min_interval) for g6 in graphs)
            iterator = ex.map(graph_probe, jobs, chunksize=args.chunksize)
            for i, res in enumerate(iterator, 1):
                for k in acc:
                    acc[k] += res[k]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
                if i % 10000 == 0:
                    print("processed", i, "intervals", acc["intervals"], flush=True)
    else:
        for g6 in graphs:
            res = graph_probe((g6, args.min_interval))
            for k in acc:
                acc[k] += res[k]
            if res["fail"] is not None:
                fail = res["fail"]
                break

    print("N", args.n, acc)
    print("fail", fail)


if __name__ == "__main__":
    main()
