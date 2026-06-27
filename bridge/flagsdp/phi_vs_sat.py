import numpy as np
from scipy.optimize import linprog
import flag_engine as FE
from mycielskian_check import edges_of, gamma_min_cut, all_shortest_geos
def to_setadj(n,A): return [set(j for j in range(n) if (A[i]>>j)&1) for i in range(n)]
def solve(N,adj,side,M):
    paths=[];pe=[];he=[];ep=[]
    for ei,(u,v) in enumerate(M):
        g=all_shortest_geos(N,adj,side,u,v)
        if not g: return None
        h=len(g[0]); he.append(h); idx=[]
        for P in g: idx.append(len(paths)); paths.append(P); pe.append(ei)
        ep.append(idx)
    nv=len(paths)+1; tau=len(paths)
    c=np.zeros(nv); c[tau]=1.0
    Aeq=np.zeros((len(M),nv)); beq=np.ones(len(M))
    for ei,idx in enumerate(ep):
        for k in idx: Aeq[ei,k]=1
    Aub=np.zeros((N,nv))
    for k,P in enumerate(paths):
        for v in P: Aub[v,k]+=he[pe[k]]
    for v in range(N): Aub[v,tau]=-1
    r=linprog(c,A_ub=Aub,b_ub=np.zeros(N),A_eq=Aeq,b_eq=beq,bounds=[(0,None)]*nv,method="highs")
    if not r.success: return None
    x=r.x[:len(paths)]; Tv=Aub[:,:len(paths)].dot(x)
    return Tv,-r.ineqlin.marginals,r.fun
# Check complementary slackness: phi_v>0 => Tv=tau*. And relate tau* to cap N.
cs_ok=0; tot=0; phi_at_tau=0
for N in range(5,9):
    for (nn,A) in FE.enumerate_graphs(N,triangle_free=True):
        adj=to_setadj(N,A); res,mc=gamma_min_cut(N,adj,edges_of(adj))
        if res is None: continue
        side,G,M=res
        if not M: continue
        out=solve(N,adj,side,M)
        if out is None: continue
        Tv,phi,tau=out; tot+=1
        pos=phi>1e-7
        if pos.any():
            # all phi-positive vertices at tau*?
            if np.all(np.abs(Tv[pos]-tau)<1e-5): phi_at_tau+=1
print("LP graphs %d: phi-positive set == saturated(T=tau*) in %d (complementary slackness)"%(tot,phi_at_tau))
