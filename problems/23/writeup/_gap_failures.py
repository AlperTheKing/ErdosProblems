"""Examine the restricted-max FAILURE cases (bad-carrying K-comp C where restricted cut != max cut of G[C]).
Question: do these failures ever happen for HIGH-load (near-critical) components? The induction gap only needs
restricted-max for CRITICAL (T==N) components. If all failures have avg-load << N (low), the gap survives.
Report for each failure: |C|, avg load = mass/|C|, max T on C, N, ratio avgT/N, and the cut deficit
(internal max - restricted) and boundary structure. Census N<=10."""
from fractions import Fraction as F
from itertools import product
from collections import deque
import subprocess
from _h import dec, GENG, loads
from _bdef_construct import Kcomponents, build_K_T

def induced_maxcut(C, adj):
    C=list(C); idx={v:i for i,v in enumerate(C)}; m=len(C)
    iedges=[(idx[u],idx[v]) for u in C for v in adj[u] if v in idx and v>u]
    best=0
    for bits in range(1<<m):
        s=[(bits>>i)&1 for i in range(m)]
        c=sum(1 for u,v in iedges if s[u]!=s[v])
        if c>best: best=c
    return best
def restricted_cut(C, adj, side):
    Cs=set(C)
    return sum(1 for u in C for v in adj[u] if v in Cs and v>u and side[u]!=side[v])

results=[]
for nn in range(7,11):
    outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    for g6 in outg:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        adj=info['adj']; side=info['side']; K,T,M,ell,N=build_K_T(info)
        for C in Kcomponents(K,N):
            Cs=set(C)
            if not any(f[0] in Cs and f[1] in Cs for f in M): continue
            if len(C)>13: continue
            mc=induced_maxcut(C,adj); rc=restricted_cut(C,adj,side)
            if rc==mc: continue
            mass=sum(T[v] for v in C); avg=mass/len(C); maxT=max(T[v] for v in C)
            results.append((g6,N,len(C),float(avg),float(maxT),float(avg/N),mc-rc))

print(f"total restricted-max failures: {len(results)}")
if results:
    print("Sorted by avgT/N descending (highest-load failures first):")
    for r in sorted(results,key=lambda x:-x[5])[:15]:
        print(f"  {r[0]} N={r[1]} |C|={r[2]} avgT={r[3]:.2f} maxT={r[4]:.2f} avgT/N={r[5]:.3f} cut-deficit={r[6]}")
    print(f"\nMAX avgT/N among failures = {max(r[5] for r in results):.4f}  (critical would be 1.0)")
    print(f"MAX maxT/N among failures = {max(r[4]/r[1] for r in results):.4f}")
