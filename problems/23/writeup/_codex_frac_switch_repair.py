"""Probe local repair of fractional-SPLIT-bad gamma-min cuts.

For each graph, enumerate connected-B gamma-min maximum cuts.  A cut is good if
the fractional SPLIT certificate holds for all bad edges.  For every bad cut,
test whether a one-vertex flip that remains inside the gamma-min cut family
already reaches a good cut, and whether a path of such flips reaches a good cut.
"""
from __future__ import annotations

import argparse
import subprocess
from collections import deque
from concurrent.futures import ProcessPoolExecutor

from _frac_selected_gate import frac_ok_cut
from _h import GENG, dec
from _stark1 import gmins


def flip_one(side: tuple[int, ...], v: int) -> tuple[int, ...]:
    out = list(side)
    out[v] = 1 - out[v]
    return tuple(out)


def graph_probe(g6: str):
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    if not cuts:
        return {
            "graphs": 0,
            "cuts": 0,
            "bad": 0,
            "single_miss": 0,
            "path_miss": 0,
            "w_single": None,
            "w_path": None,
        }

    sides = [tuple(int(x) for x in s) for s in cuts]
    index = {s: i for i, s in enumerate(sides)}
    good = [bool(frac_ok_cut(n, adj, list(s))) for s in sides]
    bad_indices = [i for i, ok in enumerate(good) if not ok]
    if not bad_indices:
        return {
            "graphs": 1,
            "cuts": len(sides),
            "bad": 0,
            "single_miss": 0,
            "path_miss": 0,
            "w_single": None,
            "w_path": None,
        }

    neigh = [[] for _ in sides]
    for i, s in enumerate(sides):
        for v in range(n):
            j = index.get(flip_one(s, v))
            if j is not None:
                neigh[i].append(j)

    single_miss = 0
    path_miss = 0
    w_single = None
    w_path = None
    for i in bad_indices:
        single_ok = any(good[j] for j in neigh[i])
        if not single_ok:
            single_miss += 1
            if w_single is None:
                w_single = (g6, "".join(map(str, sides[i])), sum(good), len(sides))

        seen = {i}
        q = deque([i])
        path_ok = False
        while q and not path_ok:
            cur = q.popleft()
            for j in neigh[cur]:
                if j in seen:
                    continue
                if good[j]:
                    path_ok = True
                    break
                seen.add(j)
                q.append(j)
        if not path_ok:
            path_miss += 1
            if w_path is None:
                w_path = (g6, "".join(map(str, sides[i])), sum(good), len(sides), len(seen))

    return {
        "graphs": 1,
        "cuts": len(sides),
        "bad": len(bad_indices),
        "single_miss": single_miss,
        "path_miss": path_miss,
        "w_single": w_single,
        "w_path": w_path,
    }


def merge(acc, res):
    for key in ("graphs", "cuts", "bad", "single_miss", "path_miss"):
        acc[key] += res[key]
    if acc["w_single"] is None and res["w_single"] is not None:
        acc["w_single"] = res["w_single"]
    if acc["w_path"] is None and res["w_path"] is not None:
        acc["w_path"] = res["w_path"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--max-n", type=int, default=11)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()

    acc = {
        "graphs": 0,
        "cuts": 0,
        "bad": 0,
        "single_miss": 0,
        "path_miss": 0,
        "w_single": None,
        "w_path": None,
    }
    for nn in range(7, args.max_n + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True).stdout.split()
        jobs = out
        if args.workers > 1:
            with ProcessPoolExecutor(max_workers=args.workers) as ex:
                for res in ex.map(graph_probe, jobs, chunksize=16):
                    merge(acc, res)
        else:
            for g6 in jobs:
                merge(acc, graph_probe(g6))
        print(f"N<={nn}: {acc}", flush=True)

    print("=== FINAL ===")
    print(acc)


if __name__ == "__main__":
    main()
