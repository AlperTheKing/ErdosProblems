#!/usr/bin/env python3
"""Electrical-flow / spectral probe for the local lemma (R): ell_max(w)*R(w) <= K = N+(N^2-Gamma).

Framing: uniform-split routing sends, for each bad edge f=xy, a UNIT vertex-flow from x to y spread
uniformly over the n_f shortest B-geodesics. R(w)=sum_f p_f(w) is the VERTEX-congestion of this
multicommodity flow. Gamma=sum_f ell(f)^2 is sum of (geodesic-length+1)^2.

We compute, exactly (Fractions) where rational:
  - R(w), T_uniform(w), ell_max(w)
  - effective resistance R_eff^B(x,y) in B (unit resistors) for each bad edge f=xy
  - Thomson/Dirichlet energy of the uniform-split flow per commodity (EDGE-based)
  - relation of sum_f ell(f)*R_eff(f) and Gamma; sum over congestion

Goal: find an electrical/energy quantity Q with (a) Q == Gamma or Q tied to N^2-Gamma at C5[q],
(b) ell_max(w)*R(w) <= something(Q,N). Print diagnostics on C5[q], n8, small census, Mycielski.
"""
import sys, io, contextlib
from fractions import Fraction as F
from collections import deque
import numpy as np
# import census_GPI quietly (it prints at module load)
with contextlib.redirect_stdout(io.StringIO()):
    from census_GPI import dec, maxcut_all, gmin, geos, blow

def build_adj(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def b_edges(n,adj,side):
    """edges of B (the cut/bipartite subgraph)"""
    return [(u,v) for u in range(n) for v in adj[u] if v>u and side[u]!=side[v]]

def reff_all_pairs(n,Bedges):
    """effective resistance matrix via Laplacian pseudoinverse (unit resistors)."""
    L=np.zeros((n,n))
    for u,v in Bedges:
        L[u,u]+=1; L[v,v]+=1; L[u,v]-=1; L[v,u]-=1
    Lp=np.linalg.pinv(L)
    d=np.diag(Lp)
    Reff=d[:,None]+d[None,:]-2*Lp
    return Reff

def uniform_split(n,adj,side,M,ell):
    """Return R(w), T(w), ellmax(w) (exact Fractions), and per-edge geodesic data."""
    R=[F(0) for _ in range(n)]; T=[F(0) for _ in range(n)]; ellmax=[0]*n
    perf={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        perf[f]=(Ps,nf)
        share1=F(1,nf); shareL=F(ell[f],nf)
        for P in Ps:
            for v in P:
                R[v]+=share1; T[v]+=shareL
                if ell[f]>ellmax[v]: ellmax[v]=ell[f]
    return R,T,ellmax,perf

def analyze(name,n,E,verbose=True):
    adj=build_adj(n,E)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None:
        if verbose: print(f"{name}: no gmin");
        return None
    side,G,M,ell=r
    Bed=b_edges(n,adj,side)
    R,T,ellmax,perf=uniform_split(n,adj,side,M,ell)
    K=n+(n*n-G)
    Reff=reff_all_pairs(n,Bed)
    # sum_f ell(f) * Reff(f)  and  sum_f ell(f)^2 = Gamma ; note Reff(f) <= ell(f)-1 (path of length ell-1)
    sum_ellReff=sum(ell[f]*Reff[f[0],f[1]] for f in M)
    sum_ell=sum(ell[f] for f in M)
    sum_ell2=sum(ell[f]**2 for f in M)
    # the binding vertex
    wstar=max(range(n), key=lambda w: ellmax[w]*R[w])
    lhs=ellmax[wstar]*R[wstar]
    if verbose:
        print(f"=== {name}: N={n} Gamma={G} N^2={n*n} K={K} |M|={len(M)} |B|={len(Bed)} ===")
        print(f"  max_w ellmax(w)*R(w) = {lhs} ({float(lhs):.3f})  <= K={K}? {lhs<=K}  slack={K-float(lhs):.3f}")
        print(f"  at w*={wstar}: ellmax={ellmax[wstar]} R={R[wstar]} ({float(R[wstar]):.3f}) T_unif={T[wstar]} ({float(T[wstar]):.3f})")
        print(f"  sum_f ell^2=Gamma={sum_ell2}  sum_f ell*Reff(f)={float(sum_ellReff):.3f}  sum_f ell={sum_ell}")
        print(f"  max Reff over M={float(max(Reff[f[0],f[1]] for f in M)):.4f}  (each <= ell-1)")
    return dict(n=n,G=G,K=K,M=M,ell=ell,R=R,T=T,ellmax=ellmax,Reff=Reff,side=side,Bed=Bed,lhs=lhs,wstar=wstar,perf=perf,adj=adj)

if __name__=="__main__":
    for q in (2,3,4):
        analyze(f"C5[{q}]",*blow(q))
    analyze("n8",*dec("G?\x60F\x60w"))
    # a non-tight high-Gamma census graph
    analyze("N11a",*dec("J?BD@g]Qvo?"))
