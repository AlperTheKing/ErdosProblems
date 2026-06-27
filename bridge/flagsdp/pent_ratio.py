"""
DECISIVE sufficiency test for the cut-metric angle.

GPI  <=>  for all phi>=0:  Lhs(phi) := sum_e h_e min_P sum_{v in P} phi(v)  <=  K sum_v phi(v),  K=N+N^2-Gamma.
Lhs is concave & positively-homogeneous in phi; the worst ratio rho* := max_{phi>=0, sum phi=1} Lhs(phi)
satisfies GPI <=> rho* <= K.

QUESTION (the crux of the cut-metric reduction): is the maximizer phi* always 0/1 (a single cut up to scale)?
If YES on the whole census, then  rho* = max over 0/1 cuts S of Lhs(1_S)/|S|  and GPI <=> 0/1 cut-Hall
(which we already verified holds). That would REDUCE GPI to 0/1 cut-Hall -- making the cut-metric route viable.
If NO (some graph has a strictly fractional maximizer with ratio > best 0/1 ratio), the reduction FAILS and
0/1 cut-Hall is genuinely insufficient -- pinning the EXACT crux.

We compute rho* exactly by LP. Lhs concave => max over the simplex is at... not necessarily a vertex (concave
max can be interior). So we solve: max t s.t. for a chosen geodesic-selection it's a min; handle the min by
introducing, per bad edge, the constraint Lhs uses the CHEAPEST geodesic. Since we MAXIMIZE Lhs and Lhs is a
min over geodesics, max_phi min_P(...) is a concave maximization -> use the epigraph: introduce y_e <= sum_{v in P} phi(v)
for every geodesic P of e, and maximize sum_e h_e y_e s.t. sum phi=1, phi>=0. (y_e = min_P, pushed up to the min.)
This LP's optimum = rho*. Then check if optimal phi is 0/1.
"""
import sys, numpy as np
sys.path.insert(0,'.')
from scipy.optimize import linprog
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of
from flag_engine import enumerate_graphs

def rho_star(N,adj,side,M):
    geos={e:all_shortest_geos(N,adj,side,*e) for e in M}
    he={e:len(geos[e][0]) for e in M}
    # vars: phi[0..N-1], y[e]  ; maximize sum_e he*y_e
    ne=len(M); nv=N+ne
    c=np.zeros(nv)
    for i,e in enumerate(M): c[N+i]=-he[e]   # linprog minimizes
    # constraints: y_e - sum_{v in P} phi[v] <= 0  for each geodesic P of e
    rows=[]; rhs=[]
    for i,e in enumerate(M):
        for P in geos[e]:
            row=np.zeros(nv); row[N+i]=1.0
            for v in P: row[v]-=1.0
            rows.append(row); rhs.append(0.0)
    Aub=np.array(rows); bub=np.array(rhs)
    Aeq=np.zeros((1,nv)); Aeq[0,:N]=1.0; beq=[1.0]
    bounds=[(0,None)]*N+[(None,None)]*ne
    res=linprog(c,A_ub=Aub,b_ub=bub,A_eq=Aeq,b_eq=beq,bounds=bounds,method="highs")
    return -res.fun, res.x[:N]

def best01(N,adj,side,M):
    geos={e:all_shortest_geos(N,adj,side,*e) for e in M}
    he={e:len(geos[e][0]) for e in M}
    best=0.0
    for mask in range(1,1<<N):
        S=set(v for v in range(N) if (mask>>v)&1)
        lhs=sum(he[e]*min(sum(1 for v in P if v in S) for P in geos[e]) for e in M)
        best=max(best,lhs/len(S))
    return best

N=int(sys.argv[1]) if len(sys.argv)>1 else 8
gap_found=0; total=0; worst=None
for nn,A in enumerate_graphs(N, triangle_free=True):
    adj=[set(j for j in range(N) if (A[i]>>j)&1) for i in range(N)]; E=edges_of(adj)
    r,mc=gamma_min_cut(N,adj,E)
    if r is None: continue
    side,Gam,M=r
    if not M: continue
    total+=1; K=N+N*N-Gam
    rho,phi=rho_star(N,adj,side,M)
    b01=best01(N,adj,side,M)
    # rho >= b01 always (0/1 is feasible). gap => fractional strictly better.
    if rho>b01+1e-6:
        gap_found+=1
        if worst is None or rho-b01>worst[0]:
            worst=(rho-b01,rho,b01,K,Gam,sorted(E),phi.round(4).tolist())
print(f"N={N}: graphs={total}; FRACTIONAL strictly beats 0/1 in {gap_found} graphs")
if worst:
    g,rho,b01,K,Gam,E,phi=worst
    print(f"  WORST gap={g:.5f}: rho*(frac)={rho:.5f} best01={b01:.5f} K={K} Gamma={Gam}")
    print(f"  rho* still <= K? {rho<=K+1e-6}  | fractional phi*={phi}")
    print(f"  edges={E}")
else:
    print("  0/1 ALWAYS achieves rho*  => GPI <=> 0/1 cut-Hall on this N (cut-metric reduction VALID here)")
