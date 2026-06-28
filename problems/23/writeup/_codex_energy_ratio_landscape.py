"""Float landscape for the corridor-energy ratio.

For a fixed connected-B max-cut configuration, the LPD' / corridor-energy
form is

    <T-N, y> <= E(y)

where

    E(y) = sum_f sum_{i<j} (sqrt(w[f,i]) - sqrt(w[f,j]))^2.

This diagnostic maximizes <T-N,y>/E(y) over the simplex.  It is not an
acceptance gate; it identifies near-sharp CE cores.
"""
from __future__ import annotations

import argparse
import random
import subprocess
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.optimize import minimize

from _codex_lpd_dual_probe import info_for_side, layer_terms
from _h import GENG, dec
from _stark1 import gmins


def ratio_optimize(info, starts=8, seed=1):
    n = info["n"]
    terms = layer_terms(info)
    T = np.array([float(x) for x in info["T"]])

    def vals(y):
        left = float(np.dot(T - n, y))
        energy = 0.0
        for _f, edge_terms in terms:
            roots = []
            for layer in edge_terms:
                w = sum(y[v] * p for v, p in layer)
                roots.append(np.sqrt(max(w, 0.0)))
            energy += sum((roots[i] - roots[j]) ** 2 for i in range(len(roots)) for j in range(i + 1, len(roots)))
        return left, energy

    def objective(y):
        left, energy = vals(y)
        if energy <= 1e-11:
            return 1e3 if left < 0 else -1e3
        return -left / energy

    rng = random.Random(seed)
    candidates = [np.full(n, 1.0 / n)]
    for v in range(n):
        y = np.zeros(n)
        y[v] = 1.0
        candidates.append(y)
    for _ in range(starts):
        y = np.array([rng.random() for _ in range(n)])
        y /= y.sum()
        candidates.append(y)

    cons = [{"type": "eq", "fun": lambda y: np.sum(y) - 1.0}]
    bounds = [(0.0, 1.0)] * n
    best = None
    for x0 in candidates:
        res = minimize(objective, x0, method="SLSQP", bounds=bounds, constraints=cons, options={"maxiter": 1000, "ftol": 1e-12})
        left, energy = vals(res.x)
        ratio = left / energy if energy > 1e-9 else -1e9
        if best is None or ratio > best[0]:
            best = (ratio, left, energy, res.x, res.success)
    return best


def graph_probe(args):
    g6, starts = args
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    if not cuts:
        return {"graphs": 0, "cuts": 0, "best": None}
    best = None
    for idx, side_s in enumerate(cuts):
        info = info_for_side(n, adj, tuple(int(c) for c in side_s))
        ratio, left, energy, y, success = ratio_optimize(info, starts=starts, seed=idx + 101)
        rec = {
            "ratio": ratio,
            "left": left,
            "energy": energy,
            "n": n,
            "g6": g6,
            "cut_index": idx,
            "side": side_s,
            "support": tuple(i for i, a in enumerate(y) if a > 1e-7),
            "T_support": tuple(str(info["T"][i]) for i, a in enumerate(y) if a > 1e-7),
            "M": tuple(info["M"]),
            "success": success,
        }
        if best is None or rec["ratio"] > best["ratio"]:
            best = rec
    return {"graphs": 1, "cuts": len(cuts), "best": best}


def merge(acc, res, keep):
    acc["graphs"] += res["graphs"]
    acc["cuts"] += res["cuts"]
    if res["best"] is None:
        return
    acc["records"].append(res["best"])
    acc["records"].sort(key=lambda r: -r["ratio"])
    del acc["records"][keep:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, default=10)
    ap.add_argument("--starts", type=int, default=4)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=32)
    ap.add_argument("--keep", type=int, default=20)
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    print(f"generated N={args.n} graphs={len(graphs)} starts={args.starts}", flush=True)
    acc = {"graphs": 0, "cuts": 0, "records": []}
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for i, res in enumerate(ex.map(graph_probe, ((g, args.starts) for g in graphs), chunksize=args.chunksize), 1):
                merge(acc, res, args.keep)
                if i % 1000 == 0:
                    print(f"processed={i} graphs={acc['graphs']} cuts={acc['cuts']} best_ratio={acc['records'][0]['ratio'] if acc['records'] else None}", flush=True)
    else:
        for i, g6 in enumerate(graphs, 1):
            merge(acc, graph_probe((g6, args.starts)), args.keep)
            if i % 1000 == 0:
                print(f"processed={i} graphs={acc['graphs']} cuts={acc['cuts']} best_ratio={acc['records'][0]['ratio'] if acc['records'] else None}", flush=True)

    print("=== FINAL ===")
    print({"graphs": acc["graphs"], "cuts": acc["cuts"]})
    for rec in acc["records"]:
        print(rec)


if __name__ == "__main__":
    main()
