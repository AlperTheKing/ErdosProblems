"""Local optimizer for the all-x PSC-50 scout.

This maximizes the PSC-50 violation objective over nonnegative x with
||x||_2=1 for selected cases.  It is only a numerical counterexample hunter.
"""

import argparse
import random

import numpy as np
from scipy.optimize import minimize

from _h import dec
from _stark1 import gmins
from _codex_psc50_scout import adj_of, build_two_lane, greedy_chords, p_matrix
from _satzmu_conn import struct_for_side
from _wf_lrsbreak_0 import build_k_lane


def data_for_case(kind):
    if kind == "n8":
        g6 = "G?" + chr(96) + "F" + chr(96) + "w"
        n, edges = dec(g6)
        adj, cuts = gmins(n, edges)
        return kind, n, adj, cuts[8]
    if kind == "two20":
        n, edges, side, _ = build_two_lane(20)
        return kind, n, adj_of(n, edges), side
    if kind == "k16":
        bad = greedy_chords(16, 5, 8)
        n, edges, side, _ = build_k_lane(16, 5, bad)
        return kind, n, adj_of(n, edges), side
    raise ValueError(kind)


def build_objective(n, adj, side):
    st = struct_for_side(n, adj, side)
    M, _ell, _T, _mu, cyc = st
    _fs, P = p_matrix(n, M, cyc)
    b_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    m_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    rhs = n + n * n / 25.0

    def margin_from_x(x):
        x = np.maximum(np.array(x, dtype=np.float64), 0.0)
        norm = np.linalg.norm(x)
        if norm <= 1e-12:
            return -1e9
        x = x / norm
        phi = P @ x
        L = float(phi @ phi)
        h = (n / L) * phi * phi
        xi = sum(abs(h[u] - h[v]) for u, v in b_edges) - sum(abs(h[u] - h[v]) for u, v in m_edges)
        return rhs - len(M) - L - xi / 50.0

    return len(M), margin_from_x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["n8", "two20", "k16"])
    ap.add_argument("--starts", type=int, default=200)
    args = ap.parse_args()
    name, n, adj, side = data_for_case(args.kind)
    dim, margin = build_objective(n, adj, side)
    rng = random.Random(98765 + dim)
    best = (1e9, None)
    bounds = [(0.0, None)] * dim

    def objective(y):
        return margin(y)

    # scipy minimizes; objective is the margin, so a negative value is a violation.
    starts = [np.ones(dim)]
    for j in range(dim):
        e = np.zeros(dim)
        e[j] = 1.0
        starts.append(e)
    for _ in range(args.starts):
        starts.append(np.array([rng.expovariate(1.0) for _ in range(dim)]))

    for s, x0 in enumerate(starts):
        res = minimize(objective, x0, method="SLSQP", bounds=bounds, options={"maxiter": 500, "ftol": 1e-12})
        val = margin(res.x)
        if val < best[0]:
            best = (val, res.x / max(1e-12, np.linalg.norm(res.x)), res.success, res.message)
            print("best", name, "start", s, "margin", best[0], "success", best[2], flush=True)
        if val < -1e-8:
            print("VIOL", name, "dim", dim, "margin", val, "x", best[1])
            return
    print("NO VIOL", name, "N", n, "dim", dim, "best_margin", best[0], "success", best[2])
    print("xhead", best[1][: min(20, dim)])


if __name__ == "__main__":
    main()
