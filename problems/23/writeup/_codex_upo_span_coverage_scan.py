"""Test whether off-path component spans cover each geodesic overlap interval.

For a unique bad edge f with path P, and any other bad edge geodesic Q whose
intersection with P is [r,s], the candidate lemma is:

    every position in [r,s] lies in the span of some component of B - V(P).

Together with cap(C) >= span(C)+1, this would imply the already-gated
subinterval corridor capacity.
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
    rows = checks = 0
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
            infos = component_info(n, adj, side, path)
            covered = set()
            for lo, hi, _cap, _vs, _att in infos:
                covered.update(range(lo, hi + 1))
            for g in M:
                if g == f:
                    continue
                for qpath in cyc[g]:
                    hits = sorted(pos[v] for v in qpath if v in pos)
                    if not hits:
                        continue
                    checks += 1
                    lo, hi = hits[0], hits[-1]
                    missing = [i for i in range(lo, hi + 1) if i not in covered]
                    if missing:
                        return {
                            "rows": rows,
                            "checks": checks,
                            "fail": (
                                repr(g6),
                                ci,
                                side_s,
                                f,
                                path,
                                g,
                                tuple(qpath),
                                (lo, hi),
                                missing,
                                infos,
                            ),
                        }
    return {"rows": rows, "checks": checks, "fail": None}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    rows = checks = 0
    fail = None
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                rows += res["rows"]
                checks += res["checks"]
                if res["fail"] is not None:
                    fail = res["fail"]
                    break
    else:
        for g6 in graphs:
            res = graph_probe(g6)
            rows += res["rows"]
            checks += res["checks"]
            if res["fail"] is not None:
                fail = res["fail"]
                break
    print("N", args.n, "rows", rows, "checks", checks)
    print("fail", fail)


if __name__ == "__main__":
    main()
