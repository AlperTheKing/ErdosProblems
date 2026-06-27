#!/usr/bin/env python3
"""CONSTRUCTIVE GPI attempt: the UNIFORM-SPLIT routing. For each bad edge f, split its ell(f) units EQUALLY over
ALL its shortest B-geodesic odd-cycles; vertex load T(v) = sum_{f, C ni v} ell(f)/n_f  (n_f=# shortest cycles of f).
If max_v T(v) <= K = N + (N^2 - Gamma) for EVERY triangle-free graph, the uniform-split routing is an EXPLICIT
certificate => the GPI is proved CONSTRUCTIVELY (no LP, no dual toll needed). Exact-test on full census N<=10 +
the C5[q]/n8/N11 witnesses. (Memory: canonical/BFS routing FAILS unbalanced; uniform-split is maximally balanced.)"""
import subprocess
from fractions import Fraction as F
from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG

def uniform_split_maxload(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    T=[F(0) for _ in range(n)]
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        if nf==0: return ('disconnected',)
        share=F(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=share
    K=n+(n*n-G)
    mx=max(T)
    return (G, n, K, mx, T)

# witnesses
print("=== UNIFORM-SPLIT routing: max_v T(v) <= K = N+(N^2-Gamma) ?  (exact Fractions) ===")
def show(name,n,E):
    res=uniform_split_maxload(n,E)
    if res is None: print(f"  {name}: no gmin"); return
    if res[0]=='disconnected': print(f"  {name}: disconnected geodesic"); return
    G,n2,K,mx,T=res
    print(f"  {name:7} N={n2} Gamma={G} K={K} | uniform-split max_v T(v)={mx} ({float(mx):.3f}) | <=K? {mx<=K} | max-T<=N (tight target)? {mx<=n2}")
for q in (2,3,4): show(f"C5[{q}]",*blow(q))
show("n8",*dec("G?\x60F\x60w"))
show("N11a",*dec("J?BD@g]Qvo?")); show("N11b",*dec("J?AAD@ON@[?")); show("N11c",*dec("J?AAD@WM_{?"))

print("\n=== full census N=5..10: uniform-split violations (max_v T(v) > K) ===")
for nn in range(5,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    viol=0; ntot=0; worst=F(-10**9); worstg=None
    for g6 in out:
        n,E=dec(g6); res=uniform_split_maxload(n,E)
        if res is None or res[0]=='disconnected': continue
        G,n2,K,mx,T=res; ntot+=1
        gap=mx-K
        if gap>worst: worst=gap; worstg=(g6,G,float(mx),K)
        if mx>K: viol+=1
    print(f"  N={nn}: configs={ntot} | uniform-split violations(max T>K)={viol} | worst(maxT-K)={float(worst):.3f} @ {worstg}",flush=True)
print("\nIf 0 violations across census => uniform-split routing CONSTRUCTIVELY certifies the GPI (explicit, no LP/dual).")
print("If violations => uniform-split insufficient (routing choice essential); report the failing structure.")
