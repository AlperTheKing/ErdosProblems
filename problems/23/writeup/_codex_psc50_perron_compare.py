"""Compare ALLX-PSC50 local optimizer directions with Perron directions."""

import argparse
import random

import numpy as np
from scipy.optimize import minimize

from _codex_psc50_allx_opt import data_for_case, build_objective
from _codex_psc50_scout import p_matrix
from _satzmu_conn import struct_for_side


def perron_vector(n, adj, side):
    M, _ell, _T, _mu, cyc = struct_for_side(n, adj, side)
    _fs, P = p_matrix(n, M, cyc)
    O = P.T @ P
    vals, vecs = np.linalg.eigh(O)
    x = vecs[:, -1]
    if x.sum() < 0:
        x = -x
    x = np.maximum(x, 0.0)
    return x / np.linalg.norm(x), vals[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["n8", "two20", "k16"])
    ap.add_argument("--starts", type=int, default=100)
    args = ap.parse_args()
    _name, n, adj, side = data_for_case(args.kind)
    dim, margin = build_objective(n, adj, side)
    perr, lam = perron_vector(n, adj, side)
    best = (margin(perr), perr, "perron")
    starts = [np.ones(dim), perr]
    for j in range(dim):
        e = np.zeros(dim)
        e[j] = 1.0
        starts.append(e)
    rng = random.Random(4431 + dim)
    for _ in range(args.starts):
        starts.append(np.array([rng.expovariate(1.0) for _ in range(dim)]))

    for idx, x0 in enumerate(starts):
        res = minimize(margin, x0, method="SLSQP", bounds=[(0.0, None)] * dim, options={"maxiter": 500, "ftol": 1e-12})
        x = np.maximum(res.x, 0.0)
        x /= max(1e-12, np.linalg.norm(x))
        val = margin(x)
        if val < best[0]:
            best = (val, x, f"start{idx}")
    cos = abs(float(best[1] @ perr))
    print(args.kind, "dim", dim, "perron_lambda", lam, "perron_margin", margin(perr))
    print("best_margin", best[0], "source", best[2], "cos_perron", cos)
    print("best_head", best[1][: min(20, dim)])
    print("perr_head", perr[: min(20, dim)])


if __name__ == "__main__":
    main()
