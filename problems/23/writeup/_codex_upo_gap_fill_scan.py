"""Check a stronger gap-fill form of conditional interval uncrossing.

For a unique path row, write h(I)=cap(I)-d(I).  The conditional uncrossing
needed for UPO says that every I with h(I)<=0 has an interval J with
h(J)<=h(I).  A simple proof would follow if, whenever h(I)<=0, some internal
gap of I can be filled without increasing h.  This scanner tests that stronger
local step on the exact census.
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


def gap_fills(mask: int, L: int):
    bits = [i for i in range(L) if (mask >> i) & 1]
    if not bits:
        return
    prev = bits[0]
    for x in bits[1:]:
        if x > prev + 1:
            gap_mask = 0
            for j in range(prev + 1, x):
                gap_mask |= 1 << j
            yield mask | gap_mask
        prev = x


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    _adj, cuts = gmins(n, edges)
    rows = 0
    checked = 0
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, _ell, _T, _mu, cyc = st
        S = [F(0)] * n
        for g in M:
            k = len(cyc[g])
            seen: dict[int, F] = {}
            for path in cyc[g]:
                for v in path:
                    seen[v] = seen.get(v, F(0)) + F(1, k)
            for v, weight in seen.items():
                S[v] += weight
        for f in M:
            if len(cyc[f]) != 1:
                continue
            rows += 1
            path = cyc[f][0]
            L = len(path)
            d = [S[v] - 1 for v in path]
            infos = component_info(n, adj, side, path)

            def slack(mask: int) -> F:
                lhs = sum(d[i] for i in range(L) if (mask >> i) & 1)
                rhs = sum(
                    cap
                    for lo, hi, cap, _vs, _att in infos
                    if any((mask >> i) & 1 for i in range(lo, hi + 1))
                )
                return F(rhs) - lhs

            for mask in range(1, 1 << L):
                fills = list(gap_fills(mask, L))
                if not fills:
                    continue
                h = slack(mask)
                if h >= 0:
                    continue
                checked += 1
                best = min((slack(m2), m2) for m2 in fills)
                if best[0] > h:
                    return {
                        "rows": rows,
                        "checked": checked,
                        "fail": (
                            repr(g6),
                            ci,
                            side_s,
                            f,
                            path,
                            mask,
                            str(h),
                            (str(best[0]), best[1]),
                            [str(x) for x in d],
                            infos,
                        ),
                    }
    return {"rows": rows, "checked": checked, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    acc = {"rows": 0, "checked": 0}
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                acc["rows"] += res["rows"]
                acc["checked"] += res["checked"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            acc["rows"] += res["rows"]
            acc["checked"] += res["checked"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, acc)
    print("fail", fail)


if __name__ == "__main__":
    main()
