"""Stress dense same-side chord constructions.

The two-lane family refutes universal ROWSUM/SPEC with only four bad edges.
This script tries to densify the same mechanism by adding many same-parity
path chords to a bipartite path-plus-two-lanes scaffold, while preserving
triangle-freeness, and checks whether the displayed parity cut remains
maximum.

Purpose: understand whether spectral excess can coexist with high bad-edge
count, or whether max-cut breaks immediately when the sparse obstruction is
densified.
"""

from __future__ import annotations

import argparse
from itertools import combinations

import numpy as np

from _M_full_detour_counterexample import maxcut
from _M_tailswitch_gate import cutsize, tri_free
from _gram_spectral import build_O
from _h import Bconn
from _satzmu_conn import struct_for_side
from _tail_positive_extra_counterexample import adj_from_edges


def scaffold(L: int):
    E = []
    for i in range(L):
        E.append((i, i + 1))
    a0 = L + 1
    b0 = 2 * (L + 1)
    for i in range(L + 1):
        E.append((i, a0 + i))
        E.append((i, b0 + i))
    for i in range(L):
        for u in (a0 + i, b0 + i):
            for v in (a0 + i + 1, b0 + i + 1):
                E.append((u, v))
    n = 3 * (L + 1)
    side = [0] * n
    for i in range(L + 1):
        side[i] = i % 2
        side[a0 + i] = 1 - side[i]
        side[b0 + i] = 1 - side[i]
    return n, E, side


def greedy_chords(L: int, mode: str):
    """Return same-parity path chords, greedily kept triangle-free."""
    candidates = []
    for parity in (0, 1):
        verts = [i for i in range(L + 1) if i % 2 == parity]
        for a, b in combinations(verts, 2):
            if b - a >= 4:
                if mode == "all":
                    score = (-(b - a), a, b)
                elif mode == "long":
                    score = (abs((a + b) - L), -(b - a), a, b)
                elif mode == "short":
                    score = ((b - a), a, b)
                else:
                    raise ValueError(mode)
                candidates.append((score, a, b))
    candidates.sort()
    chosen = []
    adj_bad = {i: set() for i in range(L + 1)}
    for _score, a, b in candidates:
        # Avoid triangles inside each parity bad graph.
        if adj_bad[a] & adj_bad[b]:
            continue
        chosen.append((a, b))
        adj_bad[a].add(b)
        adj_bad[b].add(a)
    return chosen


def analyze(L: int, mode: str, limit: int | None):
    n, E, side = scaffold(L)
    chords = greedy_chords(L, mode)
    if limit is not None:
        chords = chords[:limit]
    E = sorted({(min(a, b), max(a, b)) for a, b in E + chords})
    adj = adj_from_edges(n, E)
    base = cutsize(n, adj, side)
    status, opt, bound = maxcut(n, E)
    st = struct_for_side(n, adj, side) if Bconn(n, adj, side) else None
    m = len(st[0]) if st else 0
    rho = None
    maxrow = None
    gamma = None
    if st:
        M, ell, _T, _mu, cyc = st
        gamma = sum(ell[f] * ell[f] for f in M)
        info = {"n": n, "M": M, "ell": ell, "cyc": cyc}
        O, _lvec, _P = build_O(info)
        rho = float(np.linalg.eigvalsh(O)[-1]) if len(M) else 0.0
        maxrow = float(max(O.sum(axis=1))) if len(M) else 0.0
    return {
        "L": L,
        "mode": mode,
        "limit": limit,
        "n": n,
        "edges": len(E),
        "tri": tri_free(n, adj),
        "Bconn": Bconn(n, adj, side),
        "m": m,
        "high_bad": 25 * m > n * n,
        "base": base,
        "opt": opt,
        "bound": bound,
        "global_max": base == opt == int(bound),
        "rho": rho,
        "maxrow": maxrow,
        "gamma": gamma,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lengths", default="12,16,20,24")
    ap.add_argument("--modes", default="all,long,short")
    args = ap.parse_args()
    for L in [int(x) for x in args.lengths.split(",") if x]:
        for mode in [x for x in args.modes.split(",") if x]:
            full = greedy_chords(L, mode)
            limits = sorted({4, 8, 12, 16, 24, len(full)})
            for limit in limits:
                if limit > len(full):
                    continue
                r = analyze(L, mode, limit)
                print(
                    "L={L} mode={mode} limit={limit} n={n} m={m} high={high_bad} "
                    "tri={tri} max={global_max} cut={base}/{opt} rho={rho} row={maxrow} gamma={gamma}".format(**r),
                    flush=True,
                )


if __name__ == "__main__":
    main()
