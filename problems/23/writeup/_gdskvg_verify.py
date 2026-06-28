"""Exact verification of the user/GPT-Pro N=8 P1 counterexample GDSKVG, cut 01110110, bad edge f=23.
Checks: edges, triangle-free, max-cut + Gamma-minimal, p_f/S/A, ROWSUM-O holds, P1 fails on this cut/edge,
AND reconciliation: does GDSKVG have ANY SPLIT-good gamma-min cut? (must, else my census NO-GOOD-CUT=0 had a bug)."""
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn
from _stark1 import gmins
from _satzmu_conn import struct_for_side

g6="GDSKVG"
n,E=dec(g6)
Eset=set(tuple(sorted(e)) for e in E)
claimed=set(tuple(sorted((int(s[0]),int(s[1]) if len(s)==2 else int(s[1:])))) for s in [])
claimed={(0,3),(0,6),(0,7),(1,4),(1,7),(2,3),(2,7),(3,4),(4,5),(4,6),(5,7)}
print(f"g6={g6} N={n} |E|={len(E)}")
print(f"edges match claimed {{03,06,07,14,17,23,27,34,45,46,57}}: {Eset==claimed}")
print(f"  decoded edges: {sorted(Eset)}")
adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)
# triangle-free
tf=all(not (adj[a]&adj[b]) for a,b in E)
print(f"triangle-free: {tf}")

side=[0,1,1,1,0,1,1,0]  # 01110110
def cutsize(s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
mc=max(cutsize(s) for s in maxcut_all(n,adj))
print(f"cut 01110110: cutsize={cutsize(side)} maxcut={mc} is_maxcut={cutsize(side)==mc} Bconn={Bconn(n,adj,side)}")
st=struct_for_side(n,adj,side)
M,ell,T,mu,cyc=st
print(f"bad edges M={sorted(M)} ell={{f:ell[f] for f in sorted(M)}} Gamma={sum(ell[f]**2 for f in M)}")

# p_f, S
S=[F(0)]*n; pf={}
for g in M:
    Ps=cyc[g]; k=len(Ps); d={}
    for P in Ps:
        for v in P: d[v]=d.get(v,F(0))+F(1,k)
    pf[g]=d
    for v,pv in d.items(): S[v]+=pv
print(f"S(v) = {[str(S[v]) for v in range(n)]}")

f=(2,3)
L=ell[f]; Ps=cyc[f]; d=pf[f]; layer={}
for P in Ps:
    for i,v in enumerate(P): layer[v]=i
A=[F(0)]*L
for v,pv in d.items(): A[layer[v]]+=pv*S[v]
ROW=sum(A); R=ROW-F(n); m=(L-1)//2
Bs=[(sum(A[i] for i in range(t))+sum(A[i] for i in range(L-t,L)))-F(2*t*n,L) for t in range(1,m+1)]
print(f"f={f}: A={[str(a) for a in A]} ROWSUM={ROW}={float(ROW)} (N={n}) R={R}")
print(f"  B_t={[str(b) for b in Bs]}  P1 (exists t with R<=B_t<=0): {any(R<=b<=0 for b in Bs)}")
print(f"  ROWSUM-O holds (ROWSUM<=N): {ROW<=n}")

# RECONCILE: does GDSKVG have ANY SPLIT-good gamma-min cut?
def frac_ok_cut(s):
    st=struct_for_side(n,adj2,s)
    if st is None: return None
    M2,ell2,T2,mu2,cyc2=st
    S2=[F(0)]*n; pf2={}
    for g in M2:
        Ps=cyc2[g]; k=len(Ps); dd={}
        for P in Ps:
            for v in P: dd[v]=dd.get(v,F(0))+F(1,k)
        pf2[g]=dd
        for v,pv in dd.items(): S2[v]+=pv
    for ff in M2:
        L2=ell2[ff]; Ps=cyc2[ff]; dd=pf2[ff]; lay={}
        for P in Ps:
            for i,v in enumerate(P): lay[v]=i
        AA=[F(0)]*L2
        for v,pv in dd.items(): AA[lay[v]]+=pv*S2[v]
        R2=sum(AA)-F(n); mm=(L2-1)//2
        BB=[(sum(AA[i] for i in range(t))+sum(AA[i] for i in range(L2-t,L2)))-F(2*t*n,L2) for t in range(1,mm+1)]
        if not (R2<=0 and min(BB)<=0 and max(BB)>=R2): return False
    return True
adj2,cuts=gmins(n,E)
goods=[i for i,s in enumerate(cuts) if frac_ok_cut(s)]
print(f"\nRECONCILE: GDSKVG has {len(cuts)} gamma-min connected-B max cuts; SPLIT-good = {len(goods)}/{len(cuts)} (idx {goods})")
print(f"  this cut 01110110 in gamma-min set? {side in cuts}")
print(f"  => {'GDSKVG is a SPLIT-bad CUT but graph has a good cut (consistent with census NO-GOOD-CUT=0)' if goods else '*** NO-GOOD at N=8 -- census gate BUG! ***'}")
