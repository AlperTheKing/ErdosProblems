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
    phi=-r.ineqlin.marginals
    return Tv,phi,r.fun
# For each graph with overload at the LP optimum, check: does phi* live on Q={T<N}?
# Complementary slackness: phi_v>0 only if vertex v is saturated (T_v=tau*). At a tight graph tau*=N
# so saturated=={T=N}. Test whether phi mass on {T<tau*-eps} is ~0 (it MUST be, by CS) — and whether
# the saturated set has T below the cap N (i.e. dual lives where load is at the max, not necessarily underloaded).
import sys
Nmax=int(sys.argv[1]) if len(sys.argv)>1 else 9
nonflat=0; tot=0; phi_on_strictly_under=0
for N in range(5,Nmax+1):
    for (nn,A) in FE.enumerate_graphs(N,triangle_free=True):
        adj=to_setadj(N,A); res,mc=gamma_min_cut(N,adj,edges_of(adj))
        if res is None: continue
        side,G,M=res
        if not M: continue
        out=solve(N,adj,side,M)
        if out is None: continue
        Tv,phi,tau=out; tot+=1
        if tau> N+1e-6: nonflat+=1  # graphs where the cap N is actually below tau* (none expected: tau*<=N? no, <=K)
        # phi mass on vertices strictly below cap N
        under=phi[Tv<N-1e-6].sum(); allp=phi.sum()
        if allp>1e-9 and under>1e-6*allp: phi_on_strictly_under+=1
print("LP graphs:",tot," tau*>N count:",nonflat," graphs with phi mass on {T<N}:",phi_on_strictly_under)
