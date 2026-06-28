"""Are the DISCONNECTED-K-SELFCAP violating cuts gamma-min? Check isl5+gad15 br[(0,0)] N=20:
compute all connected maxcuts + their Gamma, the gamma-min value, and whether the SELFCAP-violating cuts are gamma-min.
Also check the loads() (gamma-min) cut directly for a SELFCAP violation. Exact."""
from fractions import Fraction as F
from _h import maxcut_all, Bconn, bdist_restr, loads
from _satzmu_conn import struct_for_side, kcomponents
from _bdef_construct import Cn, union_disjoint, mycielski

g15=mycielski(7,Cn(7))
n,E=union_disjoint((5,Cn(5)),g15); E=E+[(0,5)]   # isl5+gad15 br[(0,0)]
adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)

def gamma_of(side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    G=0
    for (u,v) in M:
        d=bdist_restr(adj,side,u,v)
        if d<0: return None
        G+=(d+1)**2
    return G

def selfcap_viol(side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    comp,find=kcomponents(n,cyc)
    pos=[[v for v in vs if T[v]>0] for root,vs in comp.items()]
    pos=[c for c in pos if c]
    if len(pos)<2: return ('single', None)
    for C in pos:
        for v in C:
            if T[v]>len(C): return ('VIOL', (sorted(C),len(C),v,float(T[v])))
    return ('ok-multi', None)

cuts=[s for s in maxcut_all(n,adj) if Bconn(n,adj,s)]
cand=[(s,gamma_of(s)) for s in cuts]
cand=[(s,g) for s,g in cand if g is not None]
gm=min(g for _,g in cand)
print(f"N={n}: #connected maxcuts(M!=empty)={len(cand)}, gamma-min Gamma={gm}")
nviol_gmin=0; nviol_nongmin=0; nmulti_gmin=0
for s,g in cand:
    r=selfcap_viol(s)
    isg = (g==gm)
    if r[0]=='VIOL':
        if isg: nviol_gmin+=1
        else: nviol_nongmin+=1
    if r[0] in ('VIOL','ok-multi') and isg: nmulti_gmin+=1
print(f"  SELFCAP violations among GAMMA-MIN cuts: {nviol_gmin}")
print(f"  SELFCAP violations among NON-gamma-min cuts: {nviol_nongmin}")
print(f"  multi-component gamma-min cuts: {nmulti_gmin}")
# loads() gamma-min cut
info=loads(n,E)
if info:
    r=selfcap_viol(info['side'])
    print(f"  loads() gamma-min cut: Gamma={float(info['G'])}, SELFCAP={r[0]}"+(f" {r[1]}" if r[1] else ""))
    print(f"     O={[v for v in range(n) if info['T'][v]>n]}")
