"""Independently verify Codex's N=12 no-good witness K??CE@A{?]Fc (block 131):
all gamma-min connected-B max cuts SPLIT-bad (0 good) BUT ROWSUM-O intact (rho(K)=max O-row-sum <= N).
This becomes the canonical false-certificate witness: selected-cut SPLIT is FALSE, ROWSUM-O TRUE."""
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn
from _stark1 import gmins
from _satzmu_conn import struct_for_side

g6="K??CE@A{?]Fc"
n,E=dec(g6)
adj=[set() for _ in range(n)]
for x,y in E: adj[x].add(y); adj[y].add(x)
print(f"g6={g6} N={n} |E|={len(E)}")

def rows(n, adj, s):
    """per bad edge: (f, L, ROWSUM, frac_split_ok). Also returns max O-row-sum (= rho-bound)."""
    st=struct_for_side(n,adj,s)
    if st is None: return None
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    out=[]
    for f in M:
        L=ell[f]; Ps=cyc[f]; d=pf[f]; layer={}
        for P in Ps:
            for i,v in enumerate(P): layer[v]=i
        A=[F(0)]*L
        for v,pv in d.items(): A[layer[v]]+=pv*S[v]
        ROW=sum(A); R=ROW-F(n); m=(L-1)//2
        Bs=[(sum(A[i] for i in range(t))+sum(A[i] for i in range(L-t,L)))-F(2*t*n,L) for t in range(1,m+1)]
        ok=(R<=0 and min(Bs)<=0 and max(Bs)>=R)
        out.append((f,L,ROW,R,ok))
    return out

adj2,cuts=gmins(n,E)
print(f"gamma-min connected-B max cuts: {len(cuts)}")
ngood=0; worst_rowsum=F(0); worst_loc=None; allrows_rowsumO=True
for ci,s in enumerate(cuts):
    rs=rows(n,adj2,s)
    good=all(r[4] for r in rs)
    if good: ngood+=1
    for (f,L,ROW,R,ok) in rs:
        if ROW>worst_rowsum: worst_rowsum=ROW; worst_loc=(ci,f,L)
        if ROW>n: allrows_rowsumO=False
    badrows=[(r[0],r[1],str(r[2]),str(r[3])) for r in rs if not r[4]]
    print(f"  cut {ci} side {''.join(map(str,s))}: bad-rows={len(badrows)}/{len(rs)} split-good={good}")
print(f"\nSPLIT-good cuts: {ngood}/{len(cuts)}  ==> {'NO-GOOD-CUT (selected-SPLIT FAILS)' if ngood==0 else 'has good cut'}")
print(f"max ROWSUM over all cuts/rows = {worst_rowsum} = {float(worst_rowsum):.5f}  (N={n}) at {worst_loc}")
print(f"ROWSUM-O margin = N - maxROWSUM = {F(n)-worst_rowsum} = {float(F(n)-worst_rowsum):.5f}")
print(f"ROWSUM-O holds on ALL cuts/rows: {allrows_rowsumO}  ==> {'certificate failure, NOT target failure' if allrows_rowsumO else 'TARGET ALSO FAILS (!)'}")
