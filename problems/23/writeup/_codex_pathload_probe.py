"""Probe the pathwise strengthening of ROWSUM-O.

For a fixed bad edge f, ROWSUM-O is the average over shortest B-geodesics
P for f of

    pathload(P) = sum_{v in P} S(v),  S(v)=sum_g p_g(v).

This diagnostic tests the stronger candidate pathload(P) <= N for every
shortest bad-geodesic.  A failure means ROWSUM-O genuinely needs averaging
over shortest geodesics or over a larger structure.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec, loads


def exact_s(info):
    s = [F(0) for _ in range(info["n"])]
    for f in info["M"]:
        paths = info["cyc"][f]
        nf = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        for v, c in cnt.items():
            s[v] += F(c, nf)
    return s


def graph_probe(g6):
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None:
        return None

    s = exact_s(info)
    worst_gap = F(-10**9)
    worst = None
    row_worst_gap = F(-10**9)
    row_worst = None

    for f in info["M"]:
        paths = info["cyc"][f]
        nf = len(paths)

        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        rowsum = sum(F(c, nf) * s[v] for v, c in cnt.items())
        rgap = rowsum - n
        if rgap > row_worst_gap:
            row_worst_gap = rgap
            row_worst = (g6, n, f, rowsum, len(paths))

        for path in paths:
            val = sum(s[v] for v in path)
            gap = val - n
            if gap > worst_gap:
                worst_gap = gap
                worst = (g6, n, f, val, tuple(path), len(paths), rowsum)

    return {
        "graphs": 1,
        "rows": len(info["M"]),
        "path_fail": 1 if worst_gap > 0 else 0,
        "rowsum_fail": 1 if row_worst_gap > 0 else 0,
        "worst_gap": worst_gap,
        "worst": worst,
        "row_worst_gap": row_worst_gap,
        "row_worst": row_worst,
    }


def merge(acc, res):
    if res is None:
        return
    acc["graphs"] += res["graphs"]
    acc["rows"] += res["rows"]
    acc["path_fail"] += res["path_fail"]
    acc["rowsum_fail"] += res["rowsum_fail"]
    if res["worst_gap"] > acc["worst_gap"]:
        acc["worst_gap"] = res["worst_gap"]
        acc["worst"] = res["worst"]
    if res["row_worst_gap"] > acc["row_worst_gap"]:
        acc["row_worst_gap"] = res["row_worst_gap"]
        acc["row_worst"] = res["row_worst"]


def run(max_n, workers):
    acc = {
        "graphs": 0,
        "rows": 0,
        "path_fail": 0,
        "rowsum_fail": 0,
        "worst_gap": F(-10**9),
        "worst": None,
        "row_worst_gap": F(-10**9),
        "row_worst": None,
    }
    for nn in range(5, max_n + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        if workers > 1:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                for res in ex.map(graph_probe, out, chunksize=32):
                    merge(acc, res)
        else:
            for g6 in out:
                merge(acc, graph_probe(g6))
        print(
            f"N<={nn}: graphs={acc['graphs']} rows={acc['rows']} "
            f"path_fail={acc['path_fail']} rowsum_fail={acc['rowsum_fail']} "
            f"worst_path_gap={acc['worst_gap']}",
            flush=True,
        )
    return acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--max-n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()

    acc = run(args.max_n, args.workers)
    print("=== FINAL ===")
    print(f"graphs={acc['graphs']} rows={acc['rows']}")
    print(f"path_fail={acc['path_fail']} rowsum_fail={acc['rowsum_fail']}")
    print(f"worst_path_gap={acc['worst_gap']} ({float(acc['worst_gap']):+.6g})")
    print(f"worst_path={acc['worst']}")
    print(f"worst_rowsum_gap={acc['row_worst_gap']} ({float(acc['row_worst_gap']):+.6g})")
    print(f"worst_rowsum={acc['row_worst']}")


if __name__ == "__main__":
    main()
