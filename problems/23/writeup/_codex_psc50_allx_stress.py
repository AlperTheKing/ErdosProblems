"""Floating stress for an all-x strengthening of PSC-50.

This is only a scout.  It tests whether

  ||P x||^2 + |M| + Xi(N(Px)^2/||Px||^2)/50 <= N + N^2/25

appears to hold for arbitrary nonnegative bad-edge weights x, not only the
Perron vector.  Any positive result here is evidence only.
"""

import argparse
import random
import subprocess

import numpy as np

from _h import GENG, dec
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _codex_psc50_scout import (
    adj_of,
    build_two_lane,
    greedy_chords,
    p_matrix,
)
from _wf_lrsbreak_0 import build_k_lane


def allx_margin(n, adj, side, x):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, _ell, _T, _mu, cyc = st
    if not M:
        return None
    _fs, P = p_matrix(n, M, cyc)
    x = np.array(x, dtype=np.float64)
    norm = float(np.linalg.norm(x))
    if norm == 0.0:
        return None
    x /= norm
    phi = P @ x
    lam = float(phi @ phi)
    if lam <= 1e-12:
        return None
    h = (n / lam) * (phi * phi)
    b_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    m_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    xi = sum(abs(h[u] - h[v]) for u, v in b_edges) - sum(abs(h[u] - h[v]) for u, v in m_edges)
    margin = n + n * n / 25.0 - len(M) - lam - xi / 50.0
    return margin, lam, xi, len(M), len(M)


def vectors(dim, n, trials):
    for j in range(dim):
        e = np.zeros(dim)
        e[j] = 1.0
        yield e
    yield np.ones(dim)
    rng = random.Random(12345 + 1009 * dim + n)
    for _ in range(trials):
        yield np.array([rng.random() for _ in range(dim)])
        yield np.array([rng.expovariate(1.0) for _ in range(dim)])


def test_case(name, n, adj, side, trials):
    st = struct_for_side(n, adj, side)
    if st is None or not st[0]:
        return None
    dim = len(st[0])
    best = None
    for x in vectors(dim, n, trials):
        rec = allx_margin(n, adj, side, x)
        if rec is None:
            continue
        if best is None or rec[0] < best[0]:
            best = rec + (x[: min(8, len(x))].copy(),)
        if rec[0] < -1e-8:
            print("VIOL", name, "N", n, "margin", rec[0], "lambda", rec[1], "Xi", rec[2])
            print("xhead", x[: min(12, len(x))])
            raise SystemExit(1)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--trials", type=int, default=40)
    args = ap.parse_args()
    worst = None
    cases = 0

    for n0 in range(7, args.max_n + 1):
        graphs = subprocess.run([GENG, "-tc", str(n0)], capture_output=True, text=True, check=True).stdout.split()
        for g6 in graphs:
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for ci, side in enumerate(cuts):
                rec = test_case(f"{g6}:{ci}", n, adj, side, args.trials)
                if rec is None:
                    continue
                cases += 1
                if worst is None or rec[0] < worst[0]:
                    worst = rec + (f"{g6}:{ci}", n)
        print("done census", n0, "cases", cases, "worst", worst[:5] if worst else None, flush=True)

    for L in range(8, 22, 2):
        n, edges, side, _bad = build_two_lane(L)
        rec = test_case(f"two{L}", n, adj_of(n, edges), side, max(args.trials, 400))
        cases += 1
        if worst is None or rec[0] < worst[0]:
            worst = rec + (f"two{L}", n)

    for L, k, gap in ((12, 4, 6), (14, 4, 8), (16, 5, 8)):
        bad = greedy_chords(L, k, gap)
        n, edges, side, _ = build_k_lane(L, k, bad)
        rec = test_case(f"k{L}", n, adj_of(n, edges), side, max(args.trials, 400))
        cases += 1
        if worst is None or rec[0] < worst[0]:
            worst = rec + (f"k{L}", n)

    print("NO VIOL", "cases", cases, "worst", worst)


if __name__ == "__main__":
    main()
