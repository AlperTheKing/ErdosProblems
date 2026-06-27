from fractions import Fraction as F
from census_GPI import dec, maxcut_all, gmin, geos
import subprocess
from census_GPI import GENG

def mycielski(n, E):
    # vertices 0..n-1 = copies u_i; n..2n-1 = shadows w_i; 2n = apex z
    adj=[set() for _ in range(2*n+1)]
    Eg=[(min(a,b),max(a,b)) for a,b in E]
    z=2*n
    for a,b in Eg:
        adj[a].add(b); adj[b].add(a)           # u_a u_b
        adj[a].add(n+b); adj[n+b].add(a)       # u_a w_b
        adj[b].add(n+a); adj[n+a].add(b)       # u_b w_a
    for i in range(n):
        adj[i+n].add(z); adj[z].add(i+n)       # w_i z
    EE=[(u,v) for u in range(2*n+1) for v in adj[u] if v>u]
    return 2*n+1, EE

def uniform_split_maxload(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    T=[F(0) for _ in range(n)]
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        if nf==0: return ('disc',)
        share=F(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=share
    K=n+(n*n-G); mx=max(T)
    return (G,n,K,mx)

# Petersen (std), Grotzsch = Mycielskian(C5)
petersen=[(0,1),(1,2),(2,3),(3,4),(4,0),(0,5),(1,6),(2,7),(3,8),(4,9),(5,7),(7,9),(9,6),(6,8),(8,5)]
c5=[(0,1),(1,2),(2,3),(3,4),(4,0)]
nG,EG=mycielski(5,c5)   # Grotzsch N=11
print("=== uniform-split on Grotzsch (N=11) and the Mycielskians (routing-choice-essential cases) ===")
for name,(n,E) in [("Grotzsch",(nG,EG))]:
    res=uniform_split_maxload(n,E)
    if res and res[0]!='disc':
        G,n2,K,mx=res; print(f"  {name}: N={n2} Gamma={G} K={K} | uniform-split maxT={mx} ({float(mx):.3f}) | <=K? {mx<=K}")
    else: print(f"  {name}: {res}")
for name, base in [("M(Petersen)",(10,petersen)), ("M(Grotzsch)",(nG,EG))]:
    n,E = mycielski(*base)
    res=uniform_split_maxload(n,E)
    if res is None: print(f"  {name}: no gmin (maxcut may not be connected-B)"); continue
    if res[0]=='disc': print(f"  {name}: disconnected geodesic"); continue
    G,n2,K,mx=res
    print(f"  {name}: N={n2} Gamma={G} K={K} | uniform-split maxT={mx} ({float(mx):.3f}) | <=K? {mx<=K}")

print("\n=== uniform-split full census N=11 ===")
out=subprocess.run([GENG,"-tc","11"],capture_output=True,text=True).stdout.split()
viol=0; ntot=0; worst=F(-10**9); wg=None
for g6 in out:
    n,E=dec(g6); res=uniform_split_maxload(n,E)
    if res is None or res[0]=='disc': continue
    G,n2,K,mx=res; ntot+=1; gap=mx-K
    if gap>worst: worst=gap; wg=(g6,G,float(mx),K)
    if mx>K: viol+=1
print(f"  N=11: configs={ntot} | violations(maxT>K)={viol} | worst(maxT-K)={float(worst):.3f} @ {wg}")
