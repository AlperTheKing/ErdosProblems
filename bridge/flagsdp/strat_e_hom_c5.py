#!/usr/bin/env python3
"""STRATEGY E -- HOMOMORPHISM / DOUBLE-COUNT to C5.

Goal: find a structural identity/inequality linking
   - a homomorphism-type count to C5 (or a weighted walk count built from the
     max-cut structure),
   - Gamma = sum_{uv in M} ell(uv)^2  (ell = d_B(u,v)+1),
   - the trivial bound N^2,
that is TIGHT exactly at C5[q] (the balanced blow-up).

This file is purely EXPLORATORY: it computes several candidate quantities on the
canonical instances (C5[q], odd cycles, Petersen, K23-N13, theta46) and on small
triangle-free graphs, to discover which combination gives Gamma <= N^2 with
equality at C5[q] and at C_{2k+1}.

KEY OBSERVATIONS DRIVING THE DESIGN
-----------------------------------
1. C5[q] has a graph hom G -> C5 (collapse each blow-up class to its C5 vertex).
   C_{2k+1} maps to C5 by a "winding" hom of degree 1 (for 2k+1 >= 5; C5 itself id).
   Triangle-free is necessary for any G->C5 hom-friendly structure: chi(C5)=3.

2. The eigenvector of C5's adjacency matrix for eigenvalue 2cos(2pi/5) ~ 0.618
   (the second-largest) is the natural "winding" coordinate.  Embedding V(G) on
   the unit circle at angles theta_v and scoring an edge by its angular wind is
   the standard way C5-blowups extremize.  For the max-cut/Gamma link we want a
   DISCRETE winding: assign each vertex a label in Z (a "height") so that B-edges
   step +-1 and M-edges close up an odd loop of length ell.

3. The cleanest candidate identity uses the B-graph DISTANCE.  For a bad edge
   uv, ell = d_B(u,v)+1.  Lay the (connected) B-graph out by a single potential
   phi: V -> R; a B-edge contributes (phi_u - phi_v)^2 >= 0; a bad edge's
   shortest B-path has >= ell-1 B-edges, so by Cauchy (phi_u-phi_v)^2 <= (ell-1)
   * (sum of squared steps along the path).  This is the COAREA route, known to
   cap at the LINEAR bound -- we re-measure it to calibrate, then add the
   QUADRATIC ingredient C5 provides.
"""
import itertools, math
from collections import deque
import numpy as np
from strat_e_probe import (adjset, maxcut, petersen, c5n, gpt_k23, theta46)
import flag_engine as fe


# ---------------------------------------------------------------------------
# Basic max-cut / B / M extraction
# ---------------------------------------------------------------------------
def cut_structure(N, adj):
    """Return (side, B_adj, M) for a MAXIMUM cut. B_adj = list of sets (cut edges),
    M = list of bad (monochromatic) edges (u<v)."""
    mc, side = maxcut(N, adj)
    adjB = [set() for _ in range(N)]
    M = []
    for u in range(N):
        for v in adj[u]:
            if v > u:
                if side[u] != side[v]:
                    adjB[u].add(v); adjB[v].add(u)
                else:
                    M.append((u, v))
    return side, adjB, M


def bfs_dist(N, adjB, src):
    d = [-1] * N
    d[src] = 0
    dq = deque([src])
    while dq:
        x = dq.popleft()
        for w in adjB[x]:
            if d[w] < 0:
                d[w] = d[x] + 1
                dq.append(w)
    return d


def gamma_value(N, adj):
    """Gamma = sum_{uv in M} (d_B(u,v)+1)^2 over the whole graph (B may be disconnected;
    bad edges are always within a B-component)."""
    side, adjB, M = cut_structure(N, adj)
    G = 0
    ells = []
    for (u, v) in M:
        d = bfs_dist(N, adjB, u)
        ell = d[v] + 1  # d[v] is even >=4, ell odd >=5
        if d[v] < 0:
            ell = None  # should not happen
        G += ell * ell
        ells.append(ell)
    return G, M, ells, adjB, side


# ---------------------------------------------------------------------------
# HOM-TO-C5 quantities
# ---------------------------------------------------------------------------
C5_ADJ = np.array([[0,1,0,0,1],
                   [1,0,1,0,0],
                   [0,1,0,1,0],
                   [0,0,1,0,1],
                   [1,0,0,1,0]], dtype=float)


def count_hom_to_C5(N, adj):
    """Exact number of graph homomorphisms G -> C5 (brute force for small N)."""
    nbr = [tuple(adj[u]) for u in range(N)]
    cnt = 0
    color = [0]*N
    order = list(range(N))
    def rec(i):
        nonlocal cnt
        if i == N:
            cnt += 1
            return
        v = order[i]
        for c in range(5):
            ok = True
            for w in nbr[v]:
                if w < v:  # already colored (assume order = identity, check assigned)
                    pass
            # full check at end is simpler; do incremental on lower-indexed nbrs
            for w in nbr[v]:
                if w < v and C5_ADJ[c][color[w]] == 0:
                    ok = False; break
            if ok:
                color[v] = c
                rec(i+1)
        return
    rec(0)
    return cnt


def hom_count_via_matrix(N, adj, t):
    """Number of homomorphisms from the path P_t (t edges) ... not used directly;
    placeholder for walk-based counts.  hom(P_t, C5) = 5 * 2^t (regular)."""
    return None


# ---------------------------------------------------------------------------
# DISCRETE WINDING POTENTIAL (the core Strategy-E construction)
# ---------------------------------------------------------------------------
def winding_eigvec(N, adj):
    """Second-largest-eigenvalue eigenvector of A(G): the 'C5 winding' coordinate.
    For C5[q] this is (a blow-up of) cos(2pi k/5); we test sum over bad edges."""
    A = np.zeros((N, N))
    for u in range(N):
        for v in adj[u]:
            A[u][v] = 1.0
    w, V = np.linalg.eigh(A)
    # eigenvalues ascending; the C5-winding pair is around 2cos(2pi/5)=0.618*deg-scale
    return w, V


# ---------------------------------------------------------------------------
# CANDIDATE INEQUALITY ZOO
# ---------------------------------------------------------------------------
def candidates(N, adj):
    G, M, ells, adjB, side = gamma_value(N, adj)
    beta = len(M)
    res = {'N': N, 'beta': beta, 'Gamma': G, 'N2': N*N, 'ells': ells}
    # hom to C5
    if N <= 16:
        res['homC5'] = count_hom_to_C5(N, adj)
    # B-edge count
    eB = sum(len(s) for s in adjB)//2
    res['eB'] = eB
    return res


def run():
    named = [(*c5n(1), "C5[1]"), (*c5n(2), "C5[2]"), (*c5n(3), "C5[3]"),
             (*petersen(), "Petersen"), (*gpt_k23(), "K23-N13"), (*theta46(), "theta46")]
    # also odd cycles C5,C7,C9
    def cycle(L):
        A = [0]*L
        for i in range(L):
            A[i] |= 1 << ((i+1)%L); A[(i+1)%L] |= 1<<i
        return L, A
    named += [(*cycle(5), "C5"), (*cycle(7), "C7"), (*cycle(9), "C9"), (*cycle(11), "C11")]

    print("=== Strategy E hom-to-C5: basic invariants ===", flush=True)
    print(f"{'name':10s} {'N':>3s} {'beta':>4s} {'Gamma':>6s} {'N^2':>5s} {'G/N2':>6s} {'homC5':>8s} {'eB':>4s} ells", flush=True)
    for (N, A, label) in named:
        adj = adjset(N, A)
        c = candidates(N, adj)
        homc5 = c.get('homC5','-')
        print(f"{label:10s} {N:>3d} {c['beta']:>4d} {c['Gamma']:>6d} {c['N2']:>5d} "
              f"{c['Gamma']/c['N2']:>6.3f} {str(homc5):>8s} {c['eB']:>4d} {c['ells']}", flush=True)


if __name__ == "__main__":
    run()
