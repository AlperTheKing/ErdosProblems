#!/usr/bin/env python3
"""Total mass sum_v T_uniform(v) and its relation to Gamma.
For a bad edge f, each shortest cycle C through f has ell(f) vertices; uniform split gives each cycle weight
ell(f)/n_f; so this f's contribution to sum_v T(v) = sum_{cycles C} ell(f)/n_f * |C| = ell(f)/n_f * sum_C |C|.
But |C| = ell(f) for EVERY shortest cycle (they all have length ell(f))!  So contribution = ell(f)^2.
=> sum_v T_uniform(v) = sum_f ell(f)^2 = Gamma  EXACTLY.
Therefore maxT >= Gamma/N (avg), and the claim maxT<=K=N+(N^2-Gamma) is an UPPER bound on the max of a
distribution whose SUM is exactly Gamma. Verify this identity exactly, and tabulate maxT vs Gamma/N vs K."""
import subprocess
from fractions import Fraction as F
from census_GPI import dec, maxcut_all, gmin, geos, GENG

def stats(g6):
    n,E=dec(g6)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    T=[F(0) for _ in range(n)]
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        if nf==0: return None
        share=F(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=share
    K=n+(n*n-G); maxT=max(T); tot=sum(T)
    return n,G,K,maxT,tot

print("=== verify  sum_v T_uniform(v) == Gamma  exactly, and maxT vs N+(N^2-Gamma) ===")
bad_identity=0
for nn in range(5,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    worst=None
    for g6 in out:
        s=stats(g6)
        if s is None: continue
        n,G,K,maxT,tot=s
        if tot!=G: bad_identity+=1; print("  IDENTITY FAIL",g6,"tot",tot,"Gamma",G)
        slack=K-maxT
        if worst is None or slack<worst[0]: worst=(slack,g6,n,G,K,maxT,tot)
    if worst:
        slack,g6,n,G,K,maxT,tot=worst
        print(f"  N={nn}: identity OK | tightest: Gamma={G} K={K} maxT={maxT}({float(maxT):.3f}) sum_T={tot} slack={float(slack):.3f} g6={g6}")
print(f"identity failures total: {bad_identity}")
print("\nKey identity: sum_v T(v)=Gamma. So maxT in [Gamma/N, ...]; need maxT <= N+(N^2-Gamma).")
print("Equivalently  maxT + (Gamma - N) <= N^2  ... but sum_T=Gamma so this couples max to the whole vector.")
