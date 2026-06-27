#!/usr/bin/env python3
"""Adversarial hub-load test for the uniform-split claim U.
For a triangle-free graph G, take its GAMMA-MIN connected-B max cut, compute exactly (Fractions)
  T_uniform(v) = sum_{f in M} ell(f) * (#shortest cycles of f through v)/(#shortest cycles of f)
and test max_v T_uniform(v) <= K = N + (N^2 - Gamma).
Reports maxT (exact Fraction), K, ratio maxT/K, and slack K-maxT. Violation iff maxT>K.
"""
import sys
from fractions import Fraction as Fr
from census_GPI import dec, maxcut_all, gmin, geos

def Tuniform(n, E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    cuts=maxcut_all(n,adj)
    r=gmin(n,adj,cuts)
    if r is None: return None
    side,G,M,ell=r
    T=[Fr(0)]*n
    for (u,v) in M:
        Ps=geos(adj,side,u,v)
        nf=len(Ps)
        if nf==0: return ('geofail',G,n)
        share=Fr(ell[(u,v)], nf)
        for P in Ps:
            for w in P:
                T[w]+=share
    K=n+(n*n-G)
    maxT=max(T)
    return (n,G,K,maxT,T,side,M,ell)

def report(name, n, E):
    res=Tuniform(n,E)
    if res is None:
        print(f"{name}: no connected-B maxcut with bad edges (Gamma undefined)")
        return None
    if isinstance(res,tuple) and res[0]=='geofail':
        print(f"{name}: geofail N={res[2]} Gamma={res[1]}")
        return None
    n,G,K,maxT,T,side,M,ell=res
    ratio=float(maxT)/K if K>0 else float('inf')
    slack=K-maxT
    viol = maxT>K
    flag=" *** VIOLATION ***" if viol else ""
    print(f"{name}: N={n} Gamma={G} K={K} |M|={len(M)} maxT={maxT}={float(maxT):.4f} ratio={ratio:.4f} slack(K-maxT)={slack}={float(slack):.4f}{flag}")
    return dict(n=n,G=G,K=K,maxT=maxT,ratio=ratio,slack=slack,viol=viol,M=M,ell=ell,side=side,T=T)

if __name__=='__main__':
    pass
