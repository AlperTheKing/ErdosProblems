"""Compare LPD worst-y weights with CAGE alpha-LP dual weights.

This is a floating diagnostic.  It asks whether the CAGE dual core is the
same object as the LPD/CORR KKT core, or a different certificate artifact.
"""

from __future__ import annotations

import argparse

import numpy as np
from scipy.optimize import minimize

from _codex_cage import blowup_edges, build_instance, solve_cage
from _codex_cage_kkt import alpha_lp_with_dual
from _h import dec, loads
from _layerprice import layers_of


def lpd_setup(info):
    n = info["n"]
    layers = [(f,) + layers_of(info, f) for f in info["M"]]
    s = np.zeros(n)
    for _f, lay, pf, h in layers:
        for i in range(h + 1):
            for v in lay[i]:
                s[v] += pf[v]
    return layers, s


def corr_gap(layers, s, n, y):
    lhs = 0.0
    for _f, lay, pf, h in layers:
        w = [sum(y[v] * pf[v] for v in lay[i]) for i in range(h + 1)]
        for i in range(h + 1):
            for j in range(i + 1, h + 1):
                lhs += np.sqrt(max(w[i], 0.0) * max(w[j], 0.0))
    rhs = 0.5 * sum((n - s[v]) * y[v] for v in range(n))
    return lhs - rhs


def lpd_max_y(info, restarts=16):
    n = info["n"]
    layers, s = lpd_setup(info)
    rng = np.random.default_rng(2307)
    best = None

    def objective(z):
        y = np.maximum(z, 0.0)
        total = float(np.sum(y))
        if total <= 0:
            return 0.0
        y = y / total * n
        return -corr_gap(layers, s, n, y)

    starts = [np.ones(n)] + [rng.random(n) for _ in range(restarts)]
    for z0 in starts:
        res = minimize(
            objective,
            z0,
            method="Nelder-Mead",
            options={"maxiter": 5000, "xatol": 1e-8, "fatol": 1e-11},
        )
        y = np.maximum(res.x, 0.0)
        y = y / np.sum(y) * n
        gap = corr_gap(layers, s, n, y)
        if best is None or gap > best[0]:
            best = (float(gap), y)
    return best


def cosine(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(a @ b / (na * nb))


def compare(label, info, rounds, restarts):
    inst = build_instance(info, label)
    row = solve_cage(inst, rounds=rounds, restarts=restarts)
    res, _costs = alpha_lp_with_dual(inst, row["x"])
    lam = -np.asarray(res.ineqlin.marginals, dtype=float)
    # Put both on the same simplex scale for comparison.
    lam_simplex = lam / np.sum(lam) * info["n"] if np.sum(lam) > 0 else lam
    gap, y = lpd_max_y(info)
    t = np.asarray([float(v) for v in info["T"]])
    overload = np.maximum(t - info["n"], 0.0)
    print(f"{label}: n={info['n']} Gamma={info['G']} M={len(info['M'])}")
    print(f"  CAGE eta={float(res.x[-1]):.9f} gap={row['gap']:+.6g} lambda_nnz={int(np.sum(lam>1e-9))}")
    print(f"  LPD max corr-gap={gap:+.9f} y_nnz={int(np.sum(y>1e-7))}")
    print(f"  cos(lambda,y)={cosine(lam_simplex,y):.6f} cos(lambda,overload)={cosine(lam_simplex,overload):.6f} cos(y,overload)={cosine(y,overload):.6f}")
    print(f"  lambda={np.round(lam_simplex,3).tolist()}")
    print(f"  y     ={np.round(y,3).tolist()}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=8)
    ap.add_argument("--restarts", type=int, default=8)
    args = ap.parse_args()
    cases = [
        ("I?BD@g]Qo", 1),
        ("I?ABCc]}?", 1),
        ("I?rFf_{N?", 1),
        ("J???E?pNu\\?", 2),
    ]
    for g6, blow in cases:
        n, edges = dec(g6) if blow == 1 else blowup_edges(g6, blow)
        info = loads(n, edges)
        if info is None:
            print(f"{g6}[{blow}]: loads None")
            continue
        compare(f"{g6}[{blow}]", info, args.rounds, args.restarts)


if __name__ == "__main__":
    main()
