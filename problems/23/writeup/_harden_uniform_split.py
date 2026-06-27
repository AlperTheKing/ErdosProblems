"""Hardening: random connected triangle-free graphs N=12..16 (beyond exhaustive census) -- does uniform-split
max-load stay <= K? Generate random tri-free graphs near the interesting density, exact-test maxT<=K."""
from fractions import Fraction as F
import random
from census_GPI import maxcut_all, gmin, geos

def rand_trifree(n, p, rng):
    adj=[set() for _ in range(n)]
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    rng.shuffle(pairs)
    for (i,j) in pairs:
        if rng.random()>p: continue
        # add ij if no common neighbor (keeps triangle-free)
        if adj[i].isdisjoint(adj[j]):
            adj[i].add(j); adj[j].add(i)
    # connected?
    seen={0}; st=[0]
    while st:
        u=st.pop()
        for w in adj[u]:
            if w not in seen: seen.add(w); st.append(w)
    if len(seen)!=n: return None
    E=[(u,v) for u in range(n) for v in adj[u] if v>u]
    return n,E

def maxT(n,E):
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
    K=n+(n*n-G)
    return (G,K,max(T))

rng=random.Random(2026)
print("=== hardening: random connected triangle-free N=12..16, uniform-split maxT<=K ===")
total=0; viol=0; worst=None
for n in range(12,17):
    cnt=0; tries=0
    while cnt<25 and tries<2000:
        tries+=1
        g=rand_trifree(n, rng.uniform(0.22,0.42), rng)
        if g is None: continue
        res=maxT(*g)
        if res is None or res[0]=='disc': continue
        G,K,mx=res; cnt+=1; total+=1
        gap=float(mx)-K
        if mx>K: viol+=1; print(f"   VIOLATION N={n} Gamma={G} K={K} maxT={mx}({float(mx):.2f}) g6edges={g[1]}")
        if worst is None or gap>worst[0]: worst=(gap,n,G,K,float(mx))
    print(f"  N={n}: tested={cnt} | violations so far={viol} | worst gap(maxT-K)={worst[0]:.3f} (N={worst[1]},Gamma={worst[2]},K={worst[3]},maxT={worst[4]:.2f})",flush=True)
print(f"\nTOTAL random tri-free tested N=12..16: {total} | uniform-split violations(maxT>K): {viol}")
print("0 violations => uniform-split max-load<=K holds beyond the census on random hard graphs (hardening passed).")
