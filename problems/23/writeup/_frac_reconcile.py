"""Reconcile Codex's fractional-SPLIT failure witness (block 126): g6=J?AAFAwe_}?, side=11111010000, f=(1,6)."""
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side
from _stark1 import gmins

g6="J?AAFAwe_}?"; side=[1,1,1,1,1,0,1,0,0,0,0]
n,E=dec(g6)
adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)
# cut size, maxcut, Bconn, gamma
cutsz=sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
mc=max(sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v]) for s in maxcut_all(n,adj))
print(f"n={n} cutsize={cutsz} maxcut={mc} is_maxcut={cutsz==mc} Bconn={Bconn(n,adj,side)}")
st=struct_for_side(n,adj,side)
M,ell,T,mu,cyc=st
print(f"bad edges M={sorted(M)} ell={[ell[f] for f in sorted(M)]}")
Gamma=sum(ell[f]**2 for f in M); print(f"Gamma={Gamma}")
# S(v)
S=[F(0)]*n; pf={}
for g in M:
    Ps=cyc[g]; k=len(Ps); d={}
    for P in Ps:
        for v in P: d[v]=d.get(v,F(0))+F(1,k)
    pf[g]=d
    for v,pv in d.items(): S[v]+=pv
# A for f=(1,6)
f=(1,6) if (1,6) in M else (min(M),)  # ensure
for f in [(1,6)]:
    if f not in M:
        print(f"f={f} not in M; M has {sorted(M)}"); continue
    L=ell[f]; Ps=cyc[f]; d=pf[f]
    layer={}
    for P in Ps:
        for i,v in enumerate(P): layer[v]=i
    A=[F(0)]*L
    for v,pv in d.items(): A[layer[v]]+=pv*S[v]
    print(f"f={f} L={L} #geodesics={len(Ps)} A={[str(a) for a in A]} (floats {[round(float(a),4) for a in A]})")
    print(f"  ROWSUM=sum A = {sum(A)} = {round(float(sum(A)),4)} (N={n})")
    R=sum(A)-F(n); m=(L-1)//2
    Bs=[(sum(A[i] for i in range(t))+sum(A[i] for i in range(L-t,L)))-F(2*t*n,L) for t in range(1,m+1)]
    print(f"  R=ROWSUM-N={R}  B_t={[str(b) for b in Bs]}")
    print(f"  FRAC: min B_t={min(Bs)} <=0? {min(Bs)<=0};  max B_t={max(Bs)} >= R? {max(Bs)>=R}  -> FRAC {'HOLDS' if (R<=0 and min(Bs)<=0 and max(Bs)>=R) else 'FAILS'}")
# is it gamma-min? + does ANY gamma-min cut satisfy fractional SPLIT for ALL its bad edges (selected-cut)?
adj2,cuts=gmins(n,E)
print(f"gmins: {len(cuts)} gamma-min connected-B max cuts; is this side among them? {side in cuts}")
def frac_ok_cut(s):
    st=struct_for_side(n,adj2,s)
    if st is None: return None
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    for f in M:
        L=ell[f]; Ps=cyc[f]; d=pf[f]; layer={}
        for P in Ps:
            for i,v in enumerate(P): layer[v]=i
        A=[F(0)]*L
        for v,pv in d.items(): A[layer[v]]+=pv*S[v]
        R=sum(A)-F(n); m=(L-1)//2
        Bs=[(sum(A[i] for i in range(t))+sum(A[i] for i in range(L-t,L)))-F(2*t*n,L) for t in range(1,m+1)]
        if not (R<=0 and min(Bs)<=0 and max(Bs)>=R): return False
    return True
good=[i for i,s in enumerate(cuts) if frac_ok_cut(s)]
print(f"gamma-min cuts where fractional SPLIT holds for ALL bad edges: {len(good)}/{len(cuts)} (indices {good})")
print(f"=> SPLIT is a SELECTED-cut certificate" if good else "=> NO gamma-min cut satisfies SPLIT -- genuinely non-universal")
