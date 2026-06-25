#!/usr/bin/env python3
"""STRATEGY F probe: theta-decomposition / series-parallel reduction for D25 (nu* >= 25 t^2/n^2).

Goal: understand EXACTLY how the fractional (not geodesic) routing in the theta gadget achieves the bound,
and test whether a series-parallel reduction tracking (t, n, bundle-congestion) can carry the constant 25
from the C5 base case through theta/2-cut steps.

We build the THETA ATOM:
  - one bad edge e = (u,v)  (an M-edge / odd chord)
  - two internally-disjoint B-paths between u and v, of even lengths 4 and 6 (so e+path = odd cycle len 5 and 7).
Then compute per-atom: tau, n, nu* (LP), and the lemma-16 kappa*.

We also test the DILUTION construction (theta gadget H disjoint-union with C5[t] joined by one edge) that
KILLED the single-rate congestion route, to see whether D25 (nu* >= 25 t^2/n^2) -- which is GLOBAL, additive
across blocks -- survives, confirming that the right invariant is additive (t,n), not local congestion.
"""
import itertools
import numpy as np
from collections import deque
from scipy.optimize import linprog
import verify_D25_lemma16 as L


def build(N, edge_list):
    A = [0] * N
    for (u, v) in edge_list:
        A[u] |= 1 << v
        A[v] |= 1 << u
    return N, A


def nu_star(N, A):
    """max fractional odd-cycle packing: max sum y_C s.t. for each edge sum_{C ni e} y_C <= 1, y>=0."""
    adj = L.adjset(N, A)
    edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    cyc = L.all_odd_cycles_v(N, adj)
    if not cyc:
        return 0.0, []
    nC = len(cyc)
    c = -np.ones(nC)  # maximize sum y
    A_ub = []
    b_ub = []
    for a in edges:
        row = np.zeros(nC)
        for ci, C in enumerate(cyc):
            if a in C:
                row[ci] = 1.0
        A_ub.append(row)
        b_ub.append(1.0)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=[(0, None)] * nC, method="highs")
    return (-res.fun if res.success else 0.0), (res.x if res.success else [])


def theta_atom(len1=4, len2=6):
    """bad edge u-v plus two B-paths of given (even) lengths. u=0, v=1. M-edge = (0,1)."""
    edges = [(0, 1)]  # the bad edge
    nxt = 2
    # path 1: u - a1 - a2 - ... - v  with len1 edges => len1-1 internal vertices
    prev = 0
    for k in range(len1 - 1):
        edges.append((prev, nxt))
        prev = nxt
        nxt += 1
    edges.append((prev, 1))
    # path 2
    prev = 0
    for k in range(len2 - 1):
        edges.append((prev, nxt))
        prev = nxt
        nxt += 1
    edges.append((prev, 1))
    return build(nxt, edges)


def report(N, A, label):
    adj = L.adjset(N, A)
    mc, side = L.maxcut(N, adj)
    e = sum(len(adj[u]) for u in range(N)) // 2
    tau = e - mc
    nu, _ = nu_star(N, A)
    target = 25.0 * tau * tau / (N * N) if N > 0 else 0
    ok = nu >= target - 1e-7
    print(f"{label:22s} n={N:3d} e={e:3d} tau={tau:3d} nu*={nu:.4f}  25t^2/n^2={target:.4f}  D25:{ok}", flush=True)
    return N, tau, nu


if __name__ == "__main__":
    print("=== STRATEGY F: theta atom + series-parallel diagnostics ===\n", flush=True)

    print("-- single theta atoms (bad edge + two B-paths len L1,L2) --")
    for (l1, l2) in [(4, 4), (4, 6), (6, 6), (4, 8), (6, 8)]:
        N, A = theta_atom(l1, l2)
        report(N, A, f"theta({l1},{l2})")

    print("\n-- C5 base case (the irreducible atom where 25 appears) --")
    report(*L.c5(), "C5")
    report(*L.c5n(2), "C5[2]")

    print("\n-- K23-N13 obstruction (theta-rich) --")
    report(*L.gpt_k23(), "K23-N13")
    print("DONE", flush=True)
