# Verify tau* (vertex-load minimax) == rho* (toll-ratio max) as LP duality claims.
import sys, numpy as np
sys.path.insert(0,'.')
from scipy.optimize import linprog
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of
from flag_engine import enumerate_graphs
from pent_ratio import rho_star

def tau_star(N,adj,side,M):
    paths=[]; pe=[]; he=[]; edge_paths=[]
    for ei,e in enumerate(M):
        geos=all_shortest_geos(N,adj,side,*e); h=len(geos[0]); he.append(h); idxs=[]
        for P in geos: idxs.append(len(paths)); paths.append(P); pe.append(ei)
        edge_paths.append(idxs)
    nvar=len(paths)+1; tau=len(paths)
    c=np.zeros(nvar); c[tau]=1.0
    Aeq=np.zeros((len(M),nvar)); beq=np.ones(len(M))
    for ei,idxs in enumerate(edge_paths):
        for k in idxs: Aeq[ei,k]=1.0
    Aub=np.zeros((N,nvar))
    for k,P in enumerate(paths):
        w=he[pe[k]]
        for v in P: Aub[v,k]+=w
    for v in range(N): Aub[v,tau]=-1.0
    res=linprog(c,A_ub=Aub,b_ub=np.zeros(N),A_eq=Aeq,b_eq=beq,bounds=[(0,None)]*len(paths)+[(0,None)],method="highs")
    return res.fun

N=int(sys.argv[1]) if len(sys.argv)>1 else 9
mism=0; total=0; worst=0
for nn,A in enumerate_graphs(N, triangle_free=True):
    adj=[set(j for j in range(N) if (A[i]>>j)&1) for i in range(N)]; E=edges_of(adj)
    r,mc=gamma_min_cut(N,adj,E)
    if r is None: continue
    side,Gam,M=r
    if not M: continue
    total+=1
    t=tau_star(N,adj,side,M)
    rho,_=rho_star(N,adj,side,M)
    if abs(t-rho)>1e-5:
        mism+=1; worst=max(worst,abs(t-rho))
print(f"N={N}: {total} graphs; tau*!=rho* mismatches={mism} (worst |tau*-rho*|={worst:.2e})")
