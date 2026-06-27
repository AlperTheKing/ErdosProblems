"""Test the ENERGY BOUND  N*Sum_w(T(w)-N)^2 <= 9(N^2-Gamma)^2  (=> (COUPLE) via Cauchy-Schwarz) on the HARD cases:
N=10,11 census + Mycielskians. It is STRONGER than (COUPLE) (CS lossy), so it could FAIL where (COUPLE) holds.
Also report the tightest ratio N*sq/(9 def^2) to see if the bound is tight near the extremal. Exact Fractions."""
from fractions import Fraction as F
import subprocess
from census_GPI import dec, maxcut_all, gmin, geos, GENG

def mycielski(n,E):
    adj=[set() for _ in range(2*n+1)]; z=2*n
    for a,b in [(min(a,b),max(a,b)) for a,b in E]:
        adj[a].add(b);adj[b].add(a);adj[a].add(n+b);adj[n+b].add(a);adj[b].add(n+a);adj[n+a].add(b)
    for i in range(n): adj[i+n].add(z);adj[z].add(i+n)
    return 2*n+1,[(u,v) for u in range(2*n+1) for v in adj[u] if v>u]

def energy(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    T=[F(0) for _ in range(n)]
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        if nf==0: return ('disc',)
        sh=F(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=sh
    deficit=n*n-G
    sq=sum((t-n)*(t-n) for t in T)
    lhs=n*sq; rhs=9*deficit*deficit
    return (G,n,deficit,lhs,rhs,lhs<=rhs)

c5=[(0,1),(1,2),(2,3),(3,4),(4,0)]
petersen=[(0,1),(1,2),(2,3),(3,4),(4,0),(0,5),(1,6),(2,7),(3,8),(4,9),(5,7),(7,9),(9,6),(6,8),(8,5)]
print("=== ENERGY BOUND N*Sum(T-N)^2 <= 9(N^2-Gamma)^2 on hard cases (stronger than COUPLE via CS) ===")
for name,(n,E) in [("M(Petersen)",mycielski(10,petersen)),("M(Grotzsch)",mycielski(11,mycielski(5,c5)[1]))]:
    res=energy(n,E)
    if res and res[0]!='disc':
        G,N,d,lhs,rhs,ok=res
        print(f"  {name}: N={N} deficit={d} | N*sq={float(lhs):.1f} 9def^2={rhs} | energy<=? {ok} | ratio={float(F(lhs,rhs)) if rhs>0 else 'def0':.4f}" if rhs>0 else f"  {name}: deficit=0 N*sq={float(lhs):.1f} (must be 0:{lhs==0})")
print("--- census N=10,11: energy-bound violations (if 0, energy bound is a VALID stronger reformulation) ---")
for nn in (10,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    viol=0; nt=0; worst=F(0); wg=None
    for g6 in out:
        n,E=dec(g6); res=energy(n,E)
        if res is None or res[0]=='disc': continue
        G,N,d,lhs,rhs,ok=res; nt+=1
        if not ok: viol+=1
        if rhs>0:
            ratio=F(lhs,rhs)
            if ratio>worst: worst=ratio; wg=(g6,d,float(ratio))
    print(f"  N={nn}: configs={nt} | energy-bound violations={viol} | worst ratio N*sq/9def^2={float(worst):.4f} @ {wg}",flush=True)
print("\n0 violations => energy bound holds; worst-ratio<1 confirms slack; ratio->1 near extremal = the hard (tight) regime.")
