#!/usr/bin/env python3
"""Probe a single g6: show uniform maxT, K, tau*, Gamma, and WHICH vertex attains maxT and HOW.
Also list the full T_uniform vector and the bad edges with their ell and #cycles."""
import sys
from fractions import Fraction as F
from census_GPI import dec, maxcut_all, gmin, geos, gpi_tau

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

for g6 in sys.argv[1:]:
    n,E=dec(g6); adj=adj_of(n,E)
    side,G,M,ell=gmin(n,adj,maxcut_all(n,adj))
    T=[F(0)]*n
    info=[]
    for (u,v) in M:
        Ps=geos(adj,side,u,v); nf=len(Ps); h=ell[(u,v)]; share=F(h,nf)
        cnt=[0]*n
        for P in Ps:
            for w in set(P): cnt[w]+=1
        T=[T[w]+share*cnt[w] for w in range(n)]
        info.append((u,v,h,nf))
    K=n+(n*n-G)
    rr=gpi_tau(n,E)
    tau=rr[2] if rr and not(isinstance(rr,tuple) and rr[0]=='LPfail') else None
    print(f"g6={g6} N={n} Gamma={G} (N^2={n*n}) K={K}")
    print(f"  bad edges (u,v,ell,#cyc): {info}")
    print(f"  T_uniform={[str(x) for x in T]}  maxT={max(T)}  sumT={sum(T)}")
    print(f"  uniform maxT<=K? {max(T)<=K}  maxT==K(C5q-tight)? {max(T)==K}  maxT==N? {max(T)==n}")
    print(f"  LP tau*={tau} (tau*==N? {abs(tau-n)<1e-9 if tau else None})  tau*<=maxT? {tau<=float(max(T))+1e-9 if tau else None}")
    print(f"  sum_f ell(f) = {sum(h for _,_,h,_ in info)} ; sum T / N = {sum(T)}/{n} (avg load)")
