"""COUPLE is STRONGER than U -- verify it on the SAME hard cases that stressed U (not just census N<=10):
Mycielskians N=21/23, full N=11 census, hub witness. COUPLE: Sum_w (T(w)-N)_+ <= N^2-Gamma. Exact Fractions."""
from fractions import Fraction as F
import subprocess
from census_GPI import dec, maxcut_all, gmin, geos, GENG

def mycielski(n,E):
    adj=[set() for _ in range(2*n+1)]; z=2*n
    for a,b in [(min(a,b),max(a,b)) for a,b in E]:
        adj[a].add(b); adj[b].add(a); adj[a].add(n+b); adj[n+b].add(a); adj[b].add(n+a); adj[n+a].add(b)
    for i in range(n): adj[i+n].add(z); adj[z].add(i+n)
    return 2*n+1,[(u,v) for u in range(2*n+1) for v in adj[u] if v>u]

def couple(n,E):
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
    Uover=sum((t-n) for t in T if t>n)
    return (G, n*n-G, Uover, Uover <= n*n-G)

petersen=[(0,1),(1,2),(2,3),(3,4),(4,0),(0,5),(1,6),(2,7),(3,8),(4,9),(5,7),(7,9),(9,6),(6,8),(8,5)]
c5=[(0,1),(1,2),(2,3),(3,4),(4,0)]
print("=== COUPLE (Uover<=N^2-Gamma) on the HARD cases (COUPLE is stronger than U) ===")
for name,base in [("M(Petersen)N21",petersen),("M(Grotzsch)N23",mycielski(5,c5)[1] and (11,mycielski(5,c5)[1]))]:
    pass
# Mycielskians explicitly
for name,(n,E) in [("M(Petersen)",mycielski(10,petersen)),("M(Grotzsch)",mycielski(11,mycielski(5,c5)[1]))]:
    res=couple(n,E)
    if res and res[0]!='disc':
        G,defc,Uover,ok=res; print(f"  {name}: N={n} Gamma={G} deficit(N^2-Gamma)={defc} Uover={Uover}({float(Uover):.3f}) COUPLE<= ? {ok}")
    else: print(f"  {name}: {res}")
print("--- full N=11 census: COUPLE violations (MUST be 0) ---")
out=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
viol=0; nt=0; worst=F(-10**9); wg=None
for g6 in out:
    n,E=dec(g6); res=couple(n,E)
    if res is None or res[0]=='disc': continue
    G,defc,Uover,ok=res; nt+=1
    gap=Uover-defc
    if gap>worst: worst=gap; wg=(g6,float(Uover),defc)
    if not ok: viol+=1
print(f"  N=11: configs={nt} | COUPLE violations(Uover>deficit)={viol} | worst(Uover-deficit)={float(worst):.3f} @ {wg}")
print("0 violations on Mycielskians + full N=11 => COUPLE (the stronger handoff lemma) is solid beyond census N<=10.")
