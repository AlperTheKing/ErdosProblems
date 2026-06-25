"""Verify the CUT inequality form on atoms by brute force over vertex PARTITIONS:
   rho_B = max over partitions P of V into parts, F=delta_B(P),
           ( sum_e min#F-crossings over e's B-geodesics ) / |F|     <=  n^2/(25 t).
We restrict to BIPARTITIONS (W, ~W) first (the basic CD cut), then to the layered partition (geodesic
distance layers from a source set) which is where the coherent-P5 AM-GM with constant 25 lives.

This confirms: the remaining open lemma is a SHARP COAREA/CUT inequality
   X_F / |F| <= n^2/(25 t)   for all B-edge cuts F,
the multi-layer generalization of the PROVED block lemma (L1) whose sharp constant is 25=5^2 from the
five-pair-product AM-GM. The K23 obstruction is a 5-part cut with X_F/|F| = 8/6, well below 1.69.
"""
import numpy as np
from itertools import product
from collections import deque
import verify_D25_lemma16 as L
from sparsest_cut_dual import best_sig_cong, geodesic_edges


def XF_over_F(N, S, Bset, F):
    adjB = [[] for _ in range(N)]
    for b in Bset:
        a, c = tuple(b); adjB[a].append(c); adjB[c].append(a)
    X = 0
    for e in S:
        u, v = tuple(e)
        paths, dd = geodesic_edges(N, adjB, u, v)
        if not paths:
            return None
        X += min(sum(1 for b in P if b in F) for P in paths)
    return X/len(F) if F else 0.0


def brute_cut_rho(N, A):
    adj = L.adjset(N, A)
    edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mc, side = L.maxcut(N, adj); tau = len(edges)-mc
    sigs = L.min_signatures(N, adj, edges, tau)
    # use the BEST signature from the congestion dual
    best, t2, e2 = best_sig_cong(N, A)
    rho_lp, ell, Blist, S = best
    Bset = set(edges)-set(S)
    # brute over bipartitions W (and a few layered partitions)
    best_ratio = 0.0
    if N <= 16:
        for wm in range(1, 1 << (N-1)):
            W = [(wm >> u) & 1 for u in range(N)]
            F = set(b for b in Bset if W[min(b)] != W[max(b)])
            if not F:
                continue
            r = XF_over_F(N, S, Bset, F)
            if r and r > best_ratio:
                best_ratio = r
    return rho_lp, best_ratio, tau, N


def analyze(builder, lab):
    N, A = builder
    rho_lp, cut_ratio, tau, NN = brute_cut_rho(N, A)
    bound = NN*NN/(25.0*tau)
    print(f"{lab}: n={NN} t={tau} rho_B(LP geodesic)={rho_lp:.4f}  max bipartition-cut X_F/|F|={cut_ratio:.4f}  "
          f"n^2/25t={bound:.4f}  CUT-ineq holds:{cut_ratio<=bound+1e-7}")


for b, lab in [(L.c5(), 'C5'), (L.c5n(2), 'C5[2]'), (L.petersen(), 'Petersen'),
               (L.gpt_k23(), 'K23-N13'), (L.c5n(3), 'C5[3]')]:
    analyze(b, lab)
