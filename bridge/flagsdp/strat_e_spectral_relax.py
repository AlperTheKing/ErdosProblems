#!/usr/bin/env python3
"""STRATEGY E: the cleanest spectral RELAXATION lower bound on nu*, tested for whether
it reaches 25 t^2 / N^2.

Idea (the genuine spectral content of nu*): nu* = tau* = fractional odd-cycle cover.
A spectral LOWER bound on nu* comes from a feasible SOLUTION to the packing LP, i.e.
a fractional odd-cycle packing y>=0 with edge-loads <=1. The eigenvalue/Rayleigh
approach builds y from a vertex potential.

We test the SPECIFIC construction the cut-geometry route needs:
   For each bad edge e=uv in M (max cut), the shortest odd cycle has length d_B(u,v)+1.
   The 'cycle-degree inequality (6)' gives  sum_{v in C} d(v) <= N(L-1)/2.
   Summing the proposed packing y_C = 25t/N^2 * (expected private-cycle count) gives
   load 1.  The spectral surrogate: replace the combinatorial packing by the
   EIGENVECTOR of the bad-edge graph M projected onto B.

We compute, for each instance:
  (a) Lambda := largest eigenvalue of  D_B^{-1/2} A_M D_B^{-1/2}  style operator  (does NOT exist cleanly; we use raw)
  (b) the Hoffman-Lovasz lower bound on nu* via the THETA-FUNCTION of the
      'odd-cycle conflict graph' -- too big to compute, so instead we use the
      cleanest computable surrogate: the LP value with cycles restricted to
      SHORTEST odd cycles only (geodesic packing) -- call it nu*_geo.
  We test whether nu*_geo >= 25 t^2/N^2 (a WEAKER, more spectral-friendly packing).
"""
import itertools
import numpy as np
from scipy.optimize import linprog
from strat_e_probe import (adjset, maxcut, tau_int, all_odd_cycles,
                           petersen, c5n, gpt_k23, theta46)
import flag_engine as fe


def shortest_odd_cycles_through_each_bad_edge(N, adj, side):
    """For the fixed max cut, M = bad edges. For each bad edge uv, find shortest
    odd cycle = uv + shortest B-path u..v. Return list of such cycles (edge sets)."""
    # B adjacency
    adjB = [set() for _ in range(N)]
    M = []
    for u in range(N):
        for v in adj[u]:
            if v > u:
                if side[u] != side[v]:
                    adjB[u].add(v)
                    adjB[v].add(u)
                else:
                    M.append((u, v))
    cycles = []
    for (u, v) in M:
        # BFS shortest path in B from u to v
        from collections import deque
        prev = {u: None}
        dq = deque([u])
        found = False
        while dq:
            x = dq.popleft()
            if x == v:
                found = True
                break
            for w in adjB[x]:
                if w not in prev:
                    prev[w] = x
                    dq.append(w)
        if not found:
            continue
        path = []
        cur = v
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        # cycle edges = path edges + bad edge uv
        ce = set()
        for i in range(len(path) - 1):
            ce.add(tuple(sorted((path[i], path[i + 1]))))
        ce.add(tuple(sorted((u, v))))
        cycles.append(frozenset(ce))
    return list(set(cycles)), M


def nu_geo(N, adj):
    """Max packing restricted to shortest-odd-cycles-through-bad-edges (and all their
    cut-translates). This is the 'geodesic skeleton' relaxation closest to a spectral
    construction."""
    mc, side = maxcut(N, adj)
    cyc, M = shortest_odd_cycles_through_each_bad_edge(N, adj, side)
    if not cyc:
        return 0.0
    edges = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u]
    eidx = {e: i for i, e in enumerate(edges)}
    ne = len(edges)
    nc = len(cyc)
    c = -np.ones(nc)
    A_ub = np.zeros((ne, nc))
    b_ub = np.ones(ne)
    for j, C in enumerate(cyc):
        for e in C:
            A_ub[eidx[tuple(sorted(e))]][j] += 1.0
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * nc, method="highs")
    return -res.fun


def run():
    named = [(*petersen(), "Petersen"), (*gpt_k23(), "K23-N13"), (*theta46(), "theta46"),
             (*c5n(1), "C5[1]"), (*c5n(2), "C5[2]"), (*c5n(3), "C5[3]")]
    print("=== Geodesic-skeleton packing nu*_geo vs 25t^2/N^2 (does a restricted/spectral packing suffice?) ===", flush=True)
    for (N, A, label) in named:
        adj = adjset(N, A)
        t = tau_int(N, adj)
        ng = nu_geo(N, adj)
        target = 25.0 * t * t / (N * N)
        ok = "OK" if ng >= target - 1e-6 else "FAIL<-- geodesic packing insufficient"
        print(f"  {label:10s} N={N:2d} t={t:2d} nu*_geo={ng:7.3f} 25t^2/N^2={target:7.3f} {ok}", flush=True)

    print("\n=== Exhaustive N<=9: does nu*_geo >= 25t^2/N^2 always? (tests if shortest-cycle packing closes it) ===", flush=True)
    for N in range(5, 10):
        states = fe.enumerate_graphs(N, triangle_free=True)
        viol = 0
        worst = 1e9
        worst_inst = None
        cnt = 0
        for (n, A) in states:
            adj = adjset(n, A)
            t = tau_int(n, adj)
            if t == 0:
                continue
            ng = nu_geo(n, adj)
            target = 25.0 * t * t / (n * n)
            slack = ng - target
            cnt += 1
            if slack < worst:
                worst = slack
                worst_inst = (n, t, round(ng, 3), round(target, 3))
            if slack < -1e-6:
                viol += 1
        print(f"  N={N}: {cnt} graphs, geodesic-packing violations of 25t^2/N^2 = {viol}; "
              f"min slack={worst:+.4f} at {worst_inst}", flush=True)


if __name__ == "__main__":
    run()
