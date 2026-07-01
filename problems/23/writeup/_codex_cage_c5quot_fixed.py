"""Fixed-ratio class quotient CAGE scout for nonuniform C5 blowups.

This tests a stronger quotient object than _codex_cage_c5quot_ydep.py:
one beta-routing and one ratio r_t per gap type must satisfy every
class-symmetric y budget simultaneously.
"""

from __future__ import annotations

import argparse

import numpy as np
from scipy.optimize import linprog, minimize

from _codex_cage_c5quot_ydep import H, VARS, AEQ, BEQ, BOUNDS, c5_data

LAYER_CLASS = [0, 4, 3, 2, 1]


def coeff_matrix(x):
    r = np.exp(x)
    cmat = np.zeros((5, len(VARS)))
    for col, (i, j, t) in enumerate(VARS):
        cmat[LAYER_CLASS[i], col] += r[t]
        cmat[LAYER_CLASS[j], col] += 1.0 / r[t]
    return cmat


def solve_beta(k, x):
    sizes, _n, m, _S, cap = c5_data(k)
    cmat = coeff_matrix(x)
    denom = sizes * cap
    mvars = len(VARS)
    aub = np.zeros((5, mvars + 1))
    aub[:, :mvars] = m * cmat
    aub[:, mvars] = -denom
    c = np.zeros(mvars + 1)
    c[mvars] = 1.0
    aeq = np.zeros((AEQ.shape[0], mvars + 1))
    aeq[:, :mvars] = AEQ
    bounds = BOUNDS + [(0.0, None)]
    res = linprog(c, A_ub=aub, b_ub=np.zeros(5), A_eq=aeq, b_eq=BEQ, bounds=bounds, method="highs")
    if not res.success:
        return None, float("inf")
    return res.x[:mvars], float(res.x[mvars])


def ratio_value(k, beta, x):
    sizes, _n, m, _S, cap = c5_data(k)
    den = sizes * cap
    load = m * (coeff_matrix(x) @ beta)
    return float(np.max(load / den)), load / den


def optimize_x(k, beta, x0):
    def obj(z):
        return ratio_value(k, beta, z)[0]

    res = minimize(
        obj,
        x0,
        method="Nelder-Mead",
        options={"maxiter": 4000, "xatol": 1e-11, "fatol": 1e-12},
    )
    if not res.success and res.fun > obj(x0):
        return x0, obj(x0)
    return res.x, float(res.fun)


def solve(k, rounds, restarts, seed):
    rng = np.random.default_rng(seed)
    starts = [np.zeros(4)]
    starts.extend(rng.normal(0.0, 0.8, 4) for _ in range(restarts))
    best = None
    for x in starts:
        beta = None
        eta = float("inf")
        for _ in range(rounds):
            beta2, eta2 = solve_beta(k, x)
            if beta2 is None:
                break
            beta = beta2
            eta = eta2
            x, eta_x = optimize_x(k, beta, x)
            eta = min(eta, eta_x)
        if beta is None:
            continue
        eta_final, ratios = ratio_value(k, beta, x)
        row = (eta_final, eta, x, beta, ratios)
        if best is None or eta_final < best[0]:
            best = row
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--kmax", type=int, default=0)
    ap.add_argument("--rounds", type=int, default=8)
    ap.add_argument("--restarts", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20260701)
    ap.add_argument("--dump", action="store_true")
    args = ap.parse_args()

    ks = range(args.k, args.kmax + 1) if args.kmax else [args.k]
    for k in ks:
        best = solve(k, args.rounds, args.restarts, args.seed + k)
        if best is None:
            print(f"k={k} failed")
            continue
        eta, _eta_lp, x, beta, ratios = best
        print(
            f"k={k} eta={eta:.12g} x={[float(f'{z:.6g}') for z in x]} "
            f"ratios={[float(f'{z:.9g}') for z in ratios]} nnz={int(np.sum(beta>1e-9))}",
            flush=True,
        )
        if args.dump:
            for val, var in sorted(
                [(float(val), var) for val, var in zip(beta, VARS) if val > 1e-9],
                reverse=True,
            ):
                print(f"  beta={val:.12g} var={var}", flush=True)


if __name__ == "__main__":
    main()
