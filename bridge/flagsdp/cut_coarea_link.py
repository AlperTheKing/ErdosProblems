"""The congestion dual is a 0/1 B-edge cut F. We now LINK rho_B <= n^2/(25t) to a CUT inequality and
test whether it follows from cut-domination (CD) / the (Sep) separator lemma.

A 0/1 length ell = (1/|F|) 1_F where F subset B-edges. d^B_ell(e) = (min #F-edges on a B-geodesic of e)/|F|
... but the dual uses ALL B-paths, not just geodesics? In the congestion LP we restricted to geodesics.
For the TRUE rho_B (geodesic-restricted), the dual cut F satisfies:
   rho_B = ( sum_e [min over e's B-geodesics of #F-edges used] ) / |F|.

For F = delta_B(W) for a vertex set W (an actual cut of B), a geodesic of e=uv crosses delta_B(W) an even
number of times if u,v same side, odd if opposite. Since u,v are SAME max-cut side... but W is arbitrary.

CLEANER: the relevant cuts are VERTEX cuts. For W subset V, F = E_B(W, ~W). A bad edge e=uv:
  - if u,v on SAME side of W: its geodesics cross F an even # of times (>=0).
  - if u,v on OPPOSITE sides of W: geodesics cross F an odd # (>=1).
So #demands forced across F >= #{bad edges split by W} = e_M(W,~W) (bad edges in the cut delta(W)).
And |F| = e_B(W,~W). So rho_B >= e_M(W,~W)/e_B(W,~W). CD says e_M(W,~W)<=e_B(W,~W) => that ratio <=1.
But rho_B can be >1 (K23: 1.333) because a SINGLE geodesic may cross F MULTIPLE times (count with
multiplicity). So the cut bound is rho_B = max_F (crossing-count-with-mult)/|F|.

TEST: compute, for the tight dual cut F at K23, the vertex set W it corresponds to, and the quantities
e_M(W), e_B(W), and the with-multiplicity crossing count. Verify rho_B = (mult-crossing)/|F| and see how
n^2/(25t) bounds it. This pins the EXACT cut inequality to prove.
"""
import numpy as np
from collections import deque
import verify_D25_lemma16 as L
from sparsest_cut_dual import best_sig_cong, geodesic_edges


def analyze(builder, lab):
    N, A = builder
    best, tau, edges = best_sig_cong(N, A)
    if best is None:
        print(f"{lab}: skip"); return
    rho, ell, Blist, S = best
    F = set(b for b, v in ell.items() if v > 1e-6)
    Bset = set(edges)-set(S)
    adjB = [[] for _ in range(N)]
    for b in Bset:
        a, c = tuple(b); adjB[a].append(c); adjB[c].append(a)
    # min #F-edges over geodesics per bad edge
    total_min_cross = 0
    for e in S:
        u, v = tuple(e)
        paths, dd = geodesic_edges(N, adjB, u, v)
        best_cross = min(sum(1 for b in P if b in F) for P in paths)
        total_min_cross += best_cross
    print(f"\n{lab}: n={N} t={tau} rho_B={rho:.4f} n^2/25t={N*N/(25*tau):.4f}")
    print(f"   tight cut F: |F|={len(F)} B-edges; sum_e min#F-crossings={total_min_cross}; "
          f"ratio={total_min_cross/len(F):.4f} (=rho_B? {abs(total_min_cross/len(F)-rho)<1e-6})")
    # Try to realize F as a vertex cut delta_B(W): find W via 2-coloring B - F
    # F-removal components of B give a 2-coloring candidate
    adjBmF = [[] for _ in range(N)]
    for b in Bset-F:
        a, c = tuple(b); adjBmF[a].append(c); adjBmF[c].append(a)
    comp = [-1]*N; nc = 0
    for s in range(N):
        if comp[s] == -1:
            comp[s] = nc; q = deque([s])
            while q:
                x = q.popleft()
                for y in adjBmF[x]:
                    if comp[y] == -1:
                        comp[y] = nc; q.append(y)
            nc += 1
    print(f"   B-F has {nc} components (F is a union of cuts between them)")


for b, lab in [(L.gpt_k23(), 'K23-N13'), (L.petersen(), 'Petersen'), (L.c5n(2), 'C5[2]')]:
    analyze(b, lab)
