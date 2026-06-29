"""Verify Codex's block-147 witness J??E@_ibE? f=(6,8): min_all at non-interval (positive), and confirm the
CONDITIONAL uncrossing is vacuous here (no h(I)<=0). Refutes my over-strong 'min_interval=min_all'."""
import itertools
from fractions import Fraction as F
from _h import dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
g6="J??E@_ibE?"; s=[1,1,1,1,1,1,0,0,0,0,0]
n,E=dec(g6); adj,cuts=gmins(n,E)
st=None
for cut in cuts:
    if list(cut)==s: st=struct_for_side(n,adj,cut); break
if st is None: st=struct_for_side(n,adj,s)
M,ell,T,mu,cyc=st
S=[F(0)]*n; pf={}
for g in M:
    Ps=cyc[g]; k=len(Ps); d={}
    for P in Ps:
        for v in P: d[v]=d.get(v,F(0))+F(1,k)
    pf[g]=d
    for v,pv in d.items(): S[v]+=pv
f=(6,8); P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
d=[S[P_f[i]]-1 for i in range(L)]
rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
def find(x):
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
for u in rest:
    for w in adj[u]:
        if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
comps={}
for v in rest: comps.setdefault(find(v),set()).add(v)
compinfo=[]
for root,C in comps.items():
    A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
    if A: compinfo.append((min(A),max(A),len(C)))
def h(I): return sum(c for (lo,hi,c) in compinfo if any(lo<=i<=hi for i in I))-sum(d[i] for i in I)
print(f"P_f={P_f} d={[str(x) for x in d]} comps={compinfo}")
allmins=[]; gmin=None
for r in range(1,L+1):
    for I in itertools.combinations(range(L),r):
        hv=h(I)
        if gmin is None or hv<gmin: gmin=hv; allmins=[(I,str(hv))]
        elif hv==gmin: allmins.append((I,str(hv)))
hmin_int=min(h(range(a,b+1)) for a in range(L) for b in range(a,L))
print(f"min_all={gmin} argmins={allmins}  min_interval={hmin_int}")
neg=[(I,str(h(I))) for r in range(1,L+1) for I in itertools.combinations(range(L),r) if h(I)<=0]
print(f"sets with h(I)<=0: {len(neg)} -> {'VACUOUS (no h<=0, conditional trivially holds)' if not neg else neg[:3]}")
