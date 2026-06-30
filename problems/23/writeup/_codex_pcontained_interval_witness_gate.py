"""Gate that P-contained position-flow deficits have interval Hall witnesses.

For the position-flow on path positions versus off-path component spans,
Hall failure a priori permits arbitrary subsets of positions.  Since component
neighborhoods are intervals, the expected proof can reduce to a single path
interval.  This script checks that every deficit reported by the P-contained
flow has a negative-slack interval [a,b].
"""

from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _codex_net_globalmax_probe import contained_flow_failures
from _h import Bconn, GENG, dec
from _satzmu_conn import struct_for_side


def min_interval_slack(load: list[F], spans: list[tuple[int, int, int]]):
    best = (F(10**9), None)
    L = len(load)
    for a in range(L):
        dem = F(0)
        for b in range(a, L):
            dem += load[b]
            cap = sum(F(size) for lo, hi, size in spans if not (hi < a or b < lo))
            slack = cap - dem
            if slack < best[0]:
                best = (slack, (a, b, dem, cap))
    return best


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    deficits = misses = 0
    first = None
    for mask in range(1 << (n - 1)):
        side = [(mask >> v) & 1 for v in range(n)]
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, _T, _mu, cyc = st
        for fail in contained_flow_failures(n, adj, side):
            deficits += 1
            f, path, chords, spans, _total, _flow = fail
            load = [F(0) for _ in path]
            for lo, hi, g in chords:
                w = F(1, len(cyc[g]))
                for i in range(lo, hi + 1):
                    load[i] += w
            best = min_interval_slack(load, spans)
            if best[0] >= 0:
                misses += 1
                if first is None:
                    first = (g6, "".join(map(str, side)), f, path, chords, spans, best)
    return {"graphs": 1, "deficits": deficits, "misses": misses, "first": first}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=16)
    args = ap.parse_args()

    totals = {"graphs": 0, "deficits": 0, "misses": 0}
    first = None
    for nn in range(6, args.max_n + 1):
        graphs = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True).stdout.split()
        part = {"graphs": 0, "deficits": 0, "misses": 0}
        if args.workers > 1:
            with ProcessPoolExecutor(max_workers=args.workers) as ex:
                for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                    for k in part:
                        part[k] += res[k]
                    if first is None and res["first"] is not None:
                        first = res["first"]
        else:
            for g6 in graphs:
                res = graph_probe(g6)
                for k in part:
                    part[k] += res[k]
                if first is None and res["first"] is not None:
                    first = res["first"]
        for k in totals:
            totals[k] += part[k]
        print(f"N={nn} {part}", flush=True)
        if first is not None:
            break
    print("TOTAL", totals, flush=True)
    print("FIRST", first, flush=True)


if __name__ == "__main__":
    main()
