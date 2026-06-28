"""Augmented hard-gate (answers Codex block 129 ASK): Codex V(C) defect + max-ell present, exact.
V(C)=sum_f max(0, R(f)-max_t B_t(f)); report V-min over gamma-min cuts, all-cut-SPLIT-good count,
and the longest geodesic length present (to check whether ell>5 rows occur and stay good)."""
from fractions import Fraction as F
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn, union_disjoint

def rows_and_defect(n, adj, s):
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
    ells=[]; V=F(0); okall=True
    for f in M:
        L=ell[f]; Ps=cyc[f]; d=pf[f]; layer={}
        for P in Ps:
            for i,v in enumerate(P): layer[v]=i
        A=[F(0)]*L
        for v,pv in d.items(): A[layer[v]]+=pv*S[v]
        R=sum(A)-F(n); m=(L-1)//2
        Bs=[(sum(A[i] for i in range(t))+sum(A[i] for i in range(L-t,L)))-F(2*t*n,L) for t in range(1,m+1)]
        ells.append(L)
        V+=max(F(0), R-max(Bs))
        if not (R<=0 and min(Bs)<=0 and max(Bs)>=R): okall=False
    return ells,V,okall

def test(name,n,E):
    adj,cuts=gmins(n,E)
    if not cuts: print(f"  {name}: N={n} no gamma-min cut"); return
    Vs=[]; maxell=0; allok=0
    for s in cuts:
        ells,V,okall=rows_and_defect(n,adj,s)
        Vs.append(V); maxell=max(maxell,max(ells) if ells else 0)
        if okall: allok+=1
    print(f"  {name}: N={n} cuts={len(cuts)} V-min={Vs and min(Vs)} all-cut-SPLIT-good={allok}/{len(cuts)} max-ell={maxell}",flush=True)

def bridge(b1,b2,u,v):
    n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]

if __name__=="__main__":
    print("=== augmented hard-gate: Codex V(C) defect + max-ell present (exact) ===",flush=True)
    test("Grotzsch=M(C5)", *mycielski(5,Cn(5)))
    test("M(C7)",          *mycielski(7,Cn(7)))
    test("M(C9)",          *mycielski(9,Cn(9)))
    test("M(C11)",         *mycielski(11,Cn(11)))
    test("M(Petersen)",    *mycielski(10,[(0,1),(1,2),(2,3),(3,4),(4,0),(0,5),(1,6),(2,7),(3,8),(4,9),(5,7),(7,9),(9,6),(6,8),(8,5)]))
    test("M(Grotzsch)",    *mycielski(*mycielski(5,Cn(5))))
    test("C5|brg|M(C7)",   *bridge((5,Cn(5)), mycielski(7,Cn(7)), 0,0))
    test("C7|brg|Grotzsch",*bridge((7,Cn(7)), mycielski(5,Cn(5)), 0,0))
    test("C9|brg|C9",      *bridge((9,Cn(9)),(9,Cn(9)),0,0))
    test("C7|brg|C7",      *bridge((7,Cn(7)),(7,Cn(7)),0,0))
