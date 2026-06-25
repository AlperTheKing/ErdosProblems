"""Test the CLOSING conjecture: the worst B-cut F (maximizing X_F/|F|) is a LAYERED cut, i.e. F = the
edges between consecutive distance-layers from some vertex/source set, OR more weakly, the worst W is a
'prefix' of a BFS layering. If so, the PROVED coherent-P5 block AM-GM (5 pair-products -> 25) closes it.

We brute-force the worst bipartition W at K23 and small atoms, then CHECK whether the optimal W is a
distance-prefix in B from some source set (i.e. W = {v: d_B(A, v) <= r} for some A subset V, r).
"""
import numpy as np
from collections import deque
import verify_D25_lemma16 as L
from sparsest_cut_dual import best_sig_cong, geodesic_edges
from cut_inequality_verify import XF_over_F


def bfs_layers_from(N, adjB, A):
    d = [-1]*N
    q = deque()
    for a in A:
        d[a] = 0; q.append(a)
    while q:
        x = q.popleft()
        for y in adjB[x]:
            if d[y] < 0:
                d[y] = d[x]+1; q.append(y)
    return d


def analyze(builder, lab):
    N, A = builder
    best, tau, edges = best_sig_cong(N, A)
    if best is None:
        print(f"{lab}: skip"); return
    rho_lp, ell, Blist, S = best
    Bset = set(edges)-set(S)
    adjB = [[] for _ in range(N)]
    for b in Bset:
        a, c = tuple(b); adjB[a].append(c); adjB[c].append(a)
    # find worst W
    bestr = 0.0; bestW = None
    for wm in range(1, 1 << (N-1)):
        W = frozenset(u for u in range(N) if (wm >> u) & 1)
        F = set(b for b in Bset if (min(b) in W) != (max(b) in W))
        if not F:
            continue
        r = XF_over_F(N, S, Bset, F)
        if r and r > bestr:
            bestr = r; bestW = W
    # is bestW a distance-prefix from SOME source set A and radius r?
    is_layered = False; witness = None
    for am in range(1, 1 << N):
        Aset = [u for u in range(N) if (am >> u) & 1]
        if len(Aset) > 4:
            continue
        d = bfs_layers_from(N, adjB, Aset)
        for r in range(0, N):
            prefix = frozenset(u for u in range(N) if 0 <= d[u] <= r)
            if prefix == bestW or prefix == frozenset(range(N))-bestW:
                is_layered = True; witness = (tuple(Aset), r); break
        if is_layered:
            break
    print(f"{lab}: n={N} t={tau} worst X_F/|F|={bestr:.4f} (=rho_B {rho_lp:.4f}? {abs(bestr-rho_lp)<1e-6}) "
          f"bound={N*N/(25*tau):.4f}")
    print(f"   worst W (|W|={len(bestW)}) is a B-distance-prefix from <=4 sources: {is_layered} {witness if is_layered else ''}")


for b, lab in [(L.c5(), 'C5'), (L.c5n(2), 'C5[2]'), (L.petersen(), 'Petersen'), (L.gpt_k23(), 'K23-N13')]:
    analyze(b, lab)
