#!/usr/bin/env python3
"""Independent reconfirmation of the N=12 worst-case (min-slack) graph using the
ORIGINAL census_GPI functions (dec, maxcut_all, gmin, geos) -- a different code
path than AUDIT_Tuniform_n12.py. EXACT Fractions. Also re-derives K, Gamma, maxT."""
import sys
from fractions import Fraction
# import functions from census_GPI WITHOUT the __main__ block by importing as module
import importlib.util
spec=importlib.util.spec_from_file_location("cg","E:/Projects/ErdosProblems/problems/23/writeup/census_GPI.py")
# census_GPI runs prints at import; suppress by redirecting stdout
import io, contextlib
cg=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(cg)

def check(g6):
    n,E=cg.dec(g6)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    cuts=cg.maxcut_all(n,adj)
    r=cg.gmin(n,adj,cuts)
    assert r is not None, "no gmin cut"
    side,G,M,ell=r
    K=n+(n*n-G)
    T=[Fraction(0) for _ in range(n)]
    for (u,v) in M:
        Ps=cg.geos(adj,side,u,v)
        nf=len(Ps); share=Fraction(ell[(u,v)],nf)
        for P in Ps:
            for w in P: T[w]+=share
    maxT=max(T)
    return n,G,K,maxT,M,ell

for g6 in ["K?ABBBwerwBw"]:
    n,G,K,maxT,M,ell=check(g6)
    print(f"g6={g6} N={n} Gamma={G} K={K} maxT={maxT} ({float(maxT)}) slack(K-maxT)={Fraction(K)-maxT} OK(maxT<=K):{maxT<=K}")
    print(f"  badedges M={M}")
    print(f"  ell={ell}")
