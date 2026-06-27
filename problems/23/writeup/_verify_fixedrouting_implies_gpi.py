"""EXACT-verify the elementary chain: a FIXED routing x with max_v T_x(v)<=K implies GPI for ALL phi.
For each witness: build uniform-split routing x, T_x(v), maxT; then for many random phi>=0 check
  sum_f ell(f) m_phi(f)  <=  sum_v phi(v) T_x(v)  <=  maxT * sum phi  <=  K * sum phi.
If the FIRST inequality (the only nontrivial one) holds always, the reduction GPI <= (fixed routing max-load) is confirmed."""
from fractions import Fraction as F
import random
from census_GPI import dec, maxcut_all, gmin, geos, blow

def build(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    cyc={f:geos(adj,side,f[0],f[1]) for f in M}   # shortest cycles (vertex-lists) per bad edge
    # uniform-split routing x_{f,C}=1/n_f ; vertex load T_x(v)
    T=[F(0)]*n; T=[F(0) for _ in range(n)]
    for f in M:
        nf=len(cyc[f]); share=F(ell[f],nf)
        for P in cyc[f]:
            for v in P: T[v]+=share
    K=n+(n*n-G)
    return adj,side,G,M,ell,cyc,T,K

def check(name,n,E,trials=400):
    b=build(n,E)
    if b is None: print(f"  {name}: no gmin"); return
    adj,side,G,M,ell,cyc,T,K=b
    maxT=max(T)
    rng=random.Random(7)
    bad=0; worst_ratio=F(0)
    for _ in range(trials):
        phi=[F(rng.randint(0,6)) for _ in range(n)]
        sphi=sum(phi)
        if sphi==0: continue
        lhs=sum(ell[f]*min(sum(phi[v] for v in P) for P in cyc[f]) for f in M)  # sum ell*m_phi
        mid=sum(phi[v]*T[v] for v in range(n))                                   # sum phi*T_x
        # the only nontrivial inequality: lhs <= mid
        if lhs>mid: bad+=1
        # also confirm GPI itself: lhs <= K*sphi
        if F(lhs,1) > K*sphi: worst_ratio=max(worst_ratio, F(lhs,sphi))
    print(f"  {name:7} N={n} Gamma={G} K={K} maxT={maxT}({float(maxT):.2f}) maxT<=K? {maxT<=K} | "
          f"lhs<=sum(phi*T) FAILS in {bad}/{trials} (MUST be 0) | GPI lhs<=K*sphi violations: {'0' if worst_ratio==0 else worst_ratio}")

print("=== verify: fixed uniform-split routing with maxT<=K implies GPI (sum ell*m_phi <= sum phi*T_x <= K*sum phi) ===")
for q in (2,3): check(f"C5[{q}]",*blow(q))
check("n8",*dec("G?\x60F\x60w"))
check("N11a",*dec("J?BD@g]Qvo?")); check("N11b",*dec("J?AAD@ON@[?")); check("N11c",*dec("J?AAD@WM_{?"))
print("If lhs<=sum(phi*T) holds 0 failures AND maxT<=K => GPI proved for these graphs by the EXPLICIT uniform-split routing.")
