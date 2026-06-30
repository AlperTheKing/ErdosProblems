"""Random scan for violations of the 'Perron maximizes F' principle.

For x>=0, ||x||=1, define F(x)=||Px||^2 + Xi_x/50.
This script checks whether random x can exceed the Perron-vector value.
It is only a floating scout.
"""

import argparse
import random
import subprocess

import numpy as np

from _h import GENG, dec
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _codex_psc50_scout import p_matrix, psc50_case, adj_of, build_two_lane, greedy_chords
from _wf_lrsbreak_0 import build_k_lane


def F_value(n, adj, side, x):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, _ell, _T, _mu, cyc = st
    if not M:
        return None
    _fs, P = p_matrix(n, M, cyc)
    x = np.maximum(np.array(x, dtype=np.float64), 0.0)
    norm = float(np.linalg.norm(x))
    if norm <= 1e-12:
        return None
    x /= norm
    phi = P @ x
    L = float(phi @ phi)
    h = (n / L) * phi * phi
    b_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] != side[v]]
    m_edges = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
    xi = sum(abs(h[u] - h[v]) for u, v in b_edges) - sum(abs(h[u] - h[v]) for u, v in m_edges)
    return L + xi / 50.0, L, xi, len(M)


def scan_case(name, n, adj, side, trials):
    rec = psc50_case(name, n, adj, side)
    if rec is None:
        return None
    st = struct_for_side(n, adj, side)
    dim = len(st[0])
    perr = rec["lambda"] + rec["Xi"] / 50.0
    rng = random.Random(7829 + 31 * n + dim)
    best = (-1.0, None)
    vectors = [np.ones(dim)]
    for j in range(dim):
        e = np.zeros(dim)
        e[j] = 1.0
        vectors.append(e)
    for _ in range(trials):
        vectors.append(np.array([rng.random() for _ in range(dim)]))
        vectors.append(np.array([rng.expovariate(1.0) for _ in range(dim)]))
    for x in vectors:
        val = F_value(n, adj, side, x)
        if val is None:
            continue
        if val[0] > best[0]:
            best = (val[0], val, x[: min(10, dim)].copy())
        if val[0] > perr + 1e-8:
            print("BEATS_PERRON", name, "N", n, "dim", dim, "perrF", perr, "F", val)
            print("xhead", x[: min(20, dim)])
            raise SystemExit(1)
    return perr, best, dim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--trials", type=int, default=10)
    args = ap.parse_args()
    cases = 0
    closest = None

    for n0 in range(7, args.max_n + 1):
        graphs = subprocess.run([GENG, "-tc", str(n0)], capture_output=True, text=True, check=True).stdout.split()
        for g6 in graphs:
            n, edges = dec(g6)
            adj, cuts = gmins(n, edges)
            for ci, side in enumerate(cuts):
                out = scan_case(f"{g6}:{ci}", n, adj, side, args.trials)
                if out is None:
                    continue
                cases += 1
                perr, best, dim = out
                gap = perr - best[0]
                if closest is None or gap < closest[0]:
                    closest = (gap, f"{g6}:{ci}", n, dim, perr, best[0])
        print("done", n0, "cases", cases, "closest", closest, flush=True)

    for L in range(8, 22, 2):
        n, edges, side, _ = build_two_lane(L)
        out = scan_case(f"two{L}", n, adj_of(n, edges), side, max(args.trials, 100))
        cases += 1
        perr, best, dim = out
        gap = perr - best[0]
        if closest is None or gap < closest[0]:
            closest = (gap, f"two{L}", n, dim, perr, best[0])

    for L, k, gapv in ((12, 4, 6), (14, 4, 8), (16, 5, 8)):
        bad = greedy_chords(L, k, gapv)
        n, edges, side, _ = build_k_lane(L, k, bad)
        out = scan_case(f"k{L}", n, adj_of(n, edges), side, max(args.trials, 100))
        cases += 1
        perr, best, dim = out
        gap = perr - best[0]
        if closest is None or gap < closest[0]:
            closest = (gap, f"k{L}", n, dim, perr, best[0])

    print("NO RANDOM BEATS", "cases", cases, "closest", closest)


if __name__ == "__main__":
    main()
