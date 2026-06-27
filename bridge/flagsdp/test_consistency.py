"""Consistency: uniform routing is ONE feasible point, so maxT(uniform) >= tau*(LP).
Verify, and report the gap maxT(uniform)-tau*(LP): if it's often 0, uniform IS optimal."""
import numpy as np
from scipy.optimize import linprog
from flag_engine import enumerate_graphs
from mycielskian_check import all_shortest_geos, Bconnected, edges_of, maxcut_value, gamma_of
def adjset(n,A):
    adj=[set() for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if (A[i]>>j)&1: adj[i].add(j)
    return adj
def lp_tau(N,adj,side,M):
    paths=[]; pe=[]; he=[]; edge_paths=[]
    for ei,(u,v) in enumerate(M):
        geos=all_shortest_geos(N,adj,side,u,v); h=len(geos[0]); he.append(h); idxs=[]
        for P in geos: idxs.append(len(paths)); paths.append(P); pe.append(ei)
        edge_paths.append(idxs)
    nvar=len(paths)+1; tau=len(paths); c=np.zeros(nvar); c[tau]=1.0
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
def maxT_uniform(N,adj,side,M):
    T=np.zeros(N)
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v); w=1.0/len(geos); h=len(geos[0])
        for P in geos:
            for x in P: T[x]+=h*w
    return T.max()
worst_uni_minus_lp=-1; cnt=0; uni_optimal=0
for N in range(5,10):
    for (n,A) in enumerate_graphs(N,triangle_free=True):
        adj=adjset(n,A); E=edges_of(adj); mc=maxcut_value(n,E)
        for mask in range(1<<(n-1)):
            c=sum(1 for (u,v) in E if ((mask>>u)&1)!=((mask>>v)&1))
            if c!=mc: continue
            side=[(mask>>u)&1 for u in range(n)]
            if not Bconnected(n,adj,side): continue
            G,M=gamma_of(n,adj,side)
            if G is None or not M: continue
            mt=maxT_uniform(n,adj,side,M); tl=lp_tau(n,adj,side,M)
            cnt+=1
            d=mt-tl
            if d<-1e-6: print("  ANOMALY uniform<LP", n,G,mt,tl)
            if abs(d)<1e-6: uni_optimal+=1
            worst_uni_minus_lp=max(worst_uni_minus_lp,d)
print(f"checked={cnt}; max(maxT_uniform - tau*_LP)={worst_uni_minus_lp:.4f}; uniform-is-LP-optimal in {uni_optimal}/{cnt}")
