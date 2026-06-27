"""
PER-CUT (0/1 toll) form of the biased pentagonal facet, the building block of the cut-metric route.

For phi = 1_S (a cut), the GPI integrand decomposes via layer-cake into these. The 0/1 cut-Hall is:
   sum_e h_e * min_P |P cap S|  <=  (N+N^2-Gamma) |S|.     (NECESSARY; known not sufficient alone.)

The CUT-METRIC claim is sharper: it asks for a SINGLE pentagonal facet F_S(per cut) such that
   (a) sum_e h_e (geodesic-crossing of S)  <= F_S   for every cut S    [local pentagonal facet]
   (b) sum_S lambda_S F_S = (N+N^2-Gamma) sum phi  when phi=sum lambda_S 1_S   [integrates exactly]
The naive 5-subset pentagonal is too weak (gives min |P cap S| only as a count, the WRONG min direction
shown dead). The 'biased' version weights the pentagonal by the bad-edge measure on classes.

HERE we test the cleanest checkable consequence the angle predicts:
  PENTAGONAL-BIASED CUT INEQUALITY (PBCI):  For every triangle-free G (max cut B,M), every cut S subset V:
     sum_{e in M} h_e * c_S(e)  <=  |S| * (N+N^2-Gamma)/N * ???   -- we DON'T assume the constant; instead
  we directly test the strongest local facet that is tight on C5[q]:
     sum_{e in M} h_e * mS(e)  <=  (N + N^2 - Gamma) |S|         where  mS(e)=min_P |P cap S|.
  (This is exactly 0/1 cut-Hall. We verify it holds across the census AND record its slack, to see whether
   it is the right facet -- i.e. whether equality is achieved at the SAME S where the full LP is tight.)
"""
import sys, numpy as np, itertools
sys.path.insert(0,'.')
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of
from flag_engine import enumerate_graphs

def adj_from_edges(n,E):
    adj=[set() for _ in range(n)]
    for u,v in E: adj[u].add(v); adj[v].add(u)
    return adj

worst_ratio=0.0; worst=None; nchk=0; viol=0
N=int(sys.argv[1]) if len(sys.argv)>1 else 9
for nn,A in enumerate_graphs(N, triangle_free=True):
    adj=[set(j for j in range(N) if (A[i]>>j)&1) for i in range(N)]; E=edges_of(adj)
    res,mc=gamma_min_cut(N,adj,E)
    if res is None: continue
    side,Gam,M=res
    if not M: continue
    K=N+N*N-Gam
    # precompute geodesics per bad edge
    geos={e:all_shortest_geos(N,adj,side,*e) for e in M}
    he={e:len(geos[e][0]) for e in M}
    # check 0/1 cut-Hall over ALL cuts S (2^N too big for N=9 -> 512 ok)
    for mask in range(1<<N):
        Sset=set(v for v in range(N) if (mask>>v)&1)
        if not Sset: continue
        lhs=0
        for e in M:
            mS=min(sum(1 for v in P if v in Sset) for P in geos[e])
            lhs+=he[e]*mS
        rhs=K*len(Sset)
        nchk+=1
        if lhs>rhs+1e-9:
            viol+=1
            if worst is None or lhs-rhs>worst_ratio:
                worst_ratio=lhs-rhs; worst=(adj,side,Sset,lhs,rhs,Gam,M)
print(f"N={N}: checked {nchk} (graph,cut) pairs; 0/1 cut-Hall violations={viol}")
if worst:
    adj,side,Sset,lhs,rhs,Gam,M=worst
    print(f"  WORST violation lhs={lhs} rhs={rhs} Gamma={Gam} S={sorted(Sset)} |S|={len(Sset)}")
    print("  edges:",edges_of(adj))
else:
    print("  no violations: 0/1 cut-Hall HOLDS on full census")
