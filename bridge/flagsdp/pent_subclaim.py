"""
The biased-pentagonal facet that fractional maximizers use is the HAT  phi = (1/4,1/2,1/4) on a
3-vertex 'middle' of overlapping geodesics. General checkable SUB-CLAIM proposed as the cut-metric
crux:

  (PBP)  For every triangle-free G (max cut), and every phi>=0 that is a NONNEGATIVE COMBINATION OF
         'pentagonal hats' (vectors supported on a B-geodesic with the C5-tight profile, i.e. the
         hypermetric Q_b=0 facets b=(+1,-1,+1) read multiplicatively as 1/4,1/2,1/4 weights),
         the GPI holds: Lhs(phi) <= K sum phi.

We test the SHARPER necessary condition that the cut-metric route reduces to:
  rho* (the true worst fractional ratio) <= K  for ALL graphs (this is GPI itself, already num-true N<=11),
AND that rho* is achieved by a CUT-METRIC phi (L1-embeddable toll) -- i.e. phi* whose level sets are
'laminar/pentagonal'. Concretely we test the ONE numerically-checkable inequality that would CLOSE the
biased-pentagonal facet if true:

  (KEY)  rho* <= max( best01 ,  max over PAIRS (e,f) of bad edges sharing a geodesic vertex of
                      the local hat-ratio )   ...

Instead of guessing the facet family, give the cleanest CHECKABLE crux inequality:
  (C*)  rho*(G)  <=  K(G)  with a UNIFORM MARGIN bounded away from tightness EXCEPT at Gamma=N^2.
We measure, per graph, the normalized slack  (K - rho*)/K  and confirm it ->0 ONLY as Gamma->N^2.
This is the invariant the biased pentagonal facet must reproduce.
"""
import sys, numpy as np
sys.path.insert(0,'.')
from pent_ratio import rho_star, best01
from mycielskian_check import gamma_min_cut, edges_of
from flag_engine import enumerate_graphs
import time

N=int(sys.argv[1]) if len(sys.argv)>1 else 9
rows=[]; t0=time.time()
for nn,A in enumerate_graphs(N, triangle_free=True):
    if time.time()-t0>500: print("timebox"); break
    adj=[set(j for j in range(N) if (A[i]>>j)&1) for i in range(N)]; E=edges_of(adj)
    r,mc=gamma_min_cut(N,adj,E)
    if r is None: continue
    side,Gam,M=r
    if not M: continue
    K=N+N*N-Gam
    rho,phi=rho_star(N,adj,side,M)
    rows.append((Gam, rho, K, (K-rho)/K, rho<=K+1e-6))
viol=[r for r in rows if not r[4]]
print(f"N={N}: {len(rows)} graphs; GPI(rho*<=K) violations={len(viol)}")
# correlation: normalized slack vs deficit
import numpy as np
arr=np.array([(g,rho,K,sl) for (g,rho,K,sl,ok) in rows])
# graphs at deficit 0 (Gamma=N^2)
d0=[r for r in rows if N*N-r[0]==0]
print(f"  deficit-0 graphs (Gamma=N^2): {len(d0)}; their (K-rho)/K =", [round(r[3],4) for r in d0][:10])
mins=min(rows,key=lambda r:r[3])
print(f"  smallest normalized slack overall (K-rho)/K = {mins[3]:.5f} at Gamma={mins[0]} (deficit={N*N-mins[0]})")
print(f"  -> slack ->0 ONLY at deficit 0? min-slack among deficit>0 graphs =",
      min((r[3] for r in rows if N*N-r[0]>0), default=None))
