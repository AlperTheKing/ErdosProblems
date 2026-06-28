"""Float probe for the LPD dual/KKT core.

For a fixed connected-B max-cut configuration, maximize

    F(y) = sum_f (sum_i sqrt(w[f,i]))^2

over y>=0, sum_v y_v=1, where w[f,i]=sum_{v in layer_i(f)} y_v p_f(v).
Layer-price feasibility is equivalent to max F(y) <= N.

This is diagnostic only: it is meant to expose the active support and the
structure of hard y-vectors.  Acceptance still needs exact Fraction checks.
"""
from __future__ import annotations

import argparse
import random

import numpy as np
from scipy.optimize import minimize

from _h import dec
from _layerprice import layers_of, solve_layerprice
from _satzmu_conn import struct_for_side
from _stark1 import gmins


def info_for_side(n, adj, side):
    st = struct_for_side(n, adj, list(side))
    if st is None:
        raise ValueError("invalid side")
    M, ell, T, mu, cyc = st
    return {"n": n, "adj": adj, "side": list(side), "M": M, "ell": ell, "T": T, "mu": mu, "cyc": cyc}


def layer_terms(info):
    terms = []
    for f in info["M"]:
        lay, pf, h = layers_of(info, f)
        edge_terms = []
        for i in range(h + 1):
            edge_terms.append([(v, pf[v]) for v in lay[i]])
        terms.append((f, edge_terms))
    return terms


def objective_factory(info):
    terms = layer_terms(info)

    def value(y):
        total = 0.0
        for _f, edge_terms in terms:
            s = 0.0
            for layer in edge_terms:
                w = sum(y[v] * p for v, p in layer)
                if w > 0:
                    s += np.sqrt(w)
            total += s * s
        return total

    return value


def optimize(info, starts=40, seed=1):
    n = info["n"]
    rng = random.Random(seed)
    value = objective_factory(info)
    cons = [{"type": "eq", "fun": lambda y: np.sum(y) - 1.0}]
    bounds = [(0.0, 1.0)] * n
    candidates = [np.full(n, 1.0 / n)]
    for v in range(n):
        y = np.zeros(n)
        y[v] = 1.0
        candidates.append(y)
    for _ in range(starts):
        xs = np.array([rng.random() for _ in range(n)])
        xs /= xs.sum()
        candidates.append(xs)

    best = None
    for x0 in candidates:
        res = minimize(lambda y: -value(y), x0, method="SLSQP", bounds=bounds, constraints=cons, options={"maxiter": 1000, "ftol": 1e-12})
        val = value(res.x)
        if best is None or val > best[0]:
            best = (val, res.x, res.success, res.message)
    return best


def report(g6, side_index=None, side_bits=None, starts=40):
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    if side_bits is not None:
        side = tuple(int(c) for c in side_bits)
        label = side_bits
    else:
        side_s = cuts[side_index or 0]
        side = tuple(int(c) for c in side_s)
        label = str(side_s)
    info = info_for_side(n, adj, side)
    tstar, ok = solve_layerprice(info)
    val, y, success, msg = optimize(info, starts=starts)
    support = [(i, y[i]) for i in range(n) if y[i] > 1e-7]
    support.sort(key=lambda x: -x[1])
    print(f"g6={g6} side={label} n={n} |M|={len(info['M'])}")
    print(f"primal_tstar={tstar:.12f} ok={ok}")
    print(f"dual_max={val:.12f} gap_to_N={val-n:+.12f} opt_success={success} msg={msg}")
    print("support", [(i, round(float(a), 8)) for i, a in support])
    print("T", [str(x) for x in info["T"]])
    print("M", info["M"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("g6")
    ap.add_argument("--side-index", type=int, default=None)
    ap.add_argument("--side-bits", default=None)
    ap.add_argument("--starts", type=int, default=40)
    args = ap.parse_args()
    report(args.g6, args.side_index, args.side_bits, args.starts)


if __name__ == "__main__":
    main()
