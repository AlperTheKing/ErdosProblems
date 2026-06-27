#!/usr/bin/env python3
"""Probe: examine the n=8 witness and search census for the graph maximizing maxT/K and maxT-share-at-hub."""
import subprocess
from fractions import Fraction as Fr
from census_GPI import dec, maxcut_all, gmin, geos, GENG
from hub_adv import Tuniform

# the cited n=8 witness
w="G?`F`w"
n,E=dec(w)
print("witness",w,"n",n,"E",E)
res=Tuniform(n,E)
if res:
    n,G,K,maxT,T,side,M,ell=res
    print(f"  N={n} Gamma={G} K={K} M={M} ell={ell} side={side}")
    print(f"  T={[str(x) for x in T]} maxT={maxT} ratio={float(maxT)/K:.4f}")

# census scan N=5..12: track max ratio, and max maxT, and min slack
print("\n=== census scan: max ratio, max maxT, min slack ===")
for nn in range(5,13):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    best_ratio=(-1,None); best_maxT=(Fr(-1),None); min_slack=(Fr(10**9),None); nviol=0
    for g6 in out:
        n,E=dec(g6); r=Tuniform(n,E)
        if r is None or (isinstance(r,tuple) and r[0]=='geofail'): continue
        n2,G,K,maxT,T,side,M,ell=r
        ratio=Fr(maxT,1)/K if K>0 else Fr(0)
        slack=K-maxT
        if slack<0: nviol+=1; print("  VIOLATION",g6,"N",n2,"G",G,"K",K,"maxT",maxT)
        if ratio>best_ratio[0]: best_ratio=(ratio,(g6,n2,G,K,maxT))
        if maxT>best_maxT[0]: best_maxT=(maxT,(g6,n2,G,K))
        if slack<min_slack[0]: min_slack=(slack,(g6,n2,G,K,maxT))
    print(f"N={nn} graphs_tested={len(out)} nviol={nviol}")
    print(f"   max ratio={float(best_ratio[0]):.4f} at {best_ratio[1]}")
    print(f"   max maxT={best_maxT[0]} at {best_maxT[1]}")
    print(f"   min slack(K-maxT)={min_slack[0]} at {min_slack[1]}",flush=True)
