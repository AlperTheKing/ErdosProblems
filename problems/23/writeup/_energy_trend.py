"""DECISIVE: does the energy-bound worst ratio  N*Sum(T-N)^2 / 9(N^2-Gamma)^2  cap below 1 (crude proof => breakthrough)
or climb toward 1 (equivalent-strength => the wall)? Track worst ratio over HIGH-Gamma tri-free graphs N=12..18
(near-extremal = largest ratio). Random gen + reject to high Gamma/N^2. Exact Fractions."""
from fractions import Fraction as F
import random
from census_GPI import maxcut_all, gmin, geos

def rand_trifree(n,p,rng):
    adj=[set() for _ in range(n)]
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]; rng.shuffle(pairs)
    for (i,j) in pairs:
        if rng.random()<=p and adj[i].isdisjoint(adj[j]): adj[i].add(j); adj[j].add(i)
    seen={0};st=[0]
    while st:
        u=st.pop()
        for w in adj[u]:
            if w not in seen: seen.add(w);st.append(w)
    if len(seen)!=n: return None
    return n,[(u,v) for u in range(n) for v in adj[u] if v>u]

def ratio(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    if G < F(7,10)*n*n: return None  # only high-Gamma (near extremal)
    T=[F(0) for _ in range(n)]
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); nf=len(Ps)
        if nf==0: return None
        sh=F(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=sh
    deficit=n*n-G
    if deficit==0: return F(0)
    sq=sum((t-n)*(t-n) for t in T)
    return F(n*sq, 9*deficit*deficit)

rng=random.Random(7)
print("=== energy-bound worst ratio vs N over HIGH-Gamma graphs (cap<1 => breakthrough; ->1 => wall) ===")
for n in range(12,19):
    worst=F(0); cnt=0; tries=0; viol=0
    while cnt<400 and tries<60000:
        tries+=1
        g=rand_trifree(n, rng.uniform(0.28,0.45), rng)
        if g is None: continue
        rt=ratio(*g)
        if rt is None: continue
        cnt+=1
        if rt>worst: worst=rt
        if rt>1: viol+=1
    print(f"  N={n}: high-Gamma sampled={cnt} | WORST energy ratio={float(worst):.4f} | violations(ratio>1)={viol}",flush=True)
print("\nTrend of worst ratio: rising toward 1 = energy bound equiv-strength (wall); plateauing <1 = crude-provable (breakthrough).")
