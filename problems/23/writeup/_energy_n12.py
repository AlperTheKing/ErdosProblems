"""Exhaustive N=12 census: worst energy-bound ratio N*Sum(T-N)^2 / 9(N^2-Gamma)^2 (deficit>0 cases). Decisive 3rd
point for the trend (N=10:0.335, N=11:0.415). Climbing->1 = wall; plateau<1 = crude-provable. Exact Fractions."""
from fractions import Fraction as F
import subprocess
from census_GPI import dec, maxcut_all, gmin, geos, GENG

def ratio(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    deficit=n*n-G
    if deficit<=0: return None
    T=[F(0) for _ in range(n)]
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        if nf==0: return None
        sh=F(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=sh
    sq=sum((t-n)*(t-n) for t in T)
    return (F(n*sq,9*deficit*deficit), deficit, G)

out=subprocess.run([GENG,"-tc","12"],capture_output=True,text=True).stdout.split()
worst=F(0); wg=None; nt=0; viol=0
for g6 in out:
    n,E=dec(g6); r=ratio(n,E)
    if r is None: continue
    rt,d,G=r; nt+=1
    if rt>worst: worst=rt; wg=(g6,d,G,float(rt))
    if rt>1: viol+=1
print(f"N=12 EXHAUSTIVE: deficit>0 configs={nt} | WORST energy ratio={float(worst):.4f} @ {wg} | violations(ratio>1)={viol}")
print(f"TREND: N=10 -> 0.3355 ; N=11 -> 0.4147 ; N=12 -> {float(worst):.4f}")
