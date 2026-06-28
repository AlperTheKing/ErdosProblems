"""HARD-GATE test of the selected-cut fractional SPLIT + switch-repair radius (Codex block 128).
Census N<=11 already cleared (NO-GOOD-CUT=0, bad cuts repair radius<=2). This extends the gate to the
gadgets that killed prior certs: larger Mycielskians (M(Petersen) N=21, M(Grotzsch) N=23, M(C7) N=15)
and bridged glued islands. For each instance: enumerate ALL gamma-min connected-B max cuts, check the
fractional all-t SPLIT per cut, and for every SPLIT-bad cut find the min Hamming distance to a SPLIT-good
gamma-min cut (the switch-repair radius). FAIL = a graph with NO good cut. Exact Fraction throughout."""
from fractions import Fraction as F
from _stark1 import gmins
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn, union_disjoint, add_edges

def frac_ok_cut(n, adj, s):
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

def ham(a,b): return sum(1 for x,y in zip(a,b) if x!=y)

def test(name,n,E):
    adj,cuts=gmins(n,E)
    if not cuts:
        print(f"  {name}: N={n} no gamma-min connected-B cut (skip)",flush=True); return None
    good=[]; bad=[]
    for s in cuts:
        r=frac_ok_cut(n,adj,s)
        (good if r else bad).append(s)
    if not good:
        print(f"  {name}: N={n} cuts={len(cuts)} *** NO-GOOD-CUT -- SELECTED-CUT SPLIT FAILS ***",flush=True)
        return ('FAIL',name,n)
    # switch-repair radius for each bad cut
    radii=[min(ham(b,g) for g in good) for b in bad]
    mr=max(radii) if radii else 0
    print(f"  {name}: N={n} cuts={len(cuts)} good={len(good)} bad={len(bad)} max-switch-radius={mr}",flush=True)
    return ('OK',name,n,mr,len(bad))

if __name__=="__main__":
    print("=== HARD-GATE selected-cut fractional SPLIT + switch-repair (exact) ===",flush=True)
    inst=[]
    inst.append(("Grotzsch=M(C5)", *mycielski(5,Cn(5))))            # N=11 (in census, sanity)
    inst.append(("M(C7)",          *mycielski(7,Cn(7))))            # N=15
    inst.append(("M(C9)",          *mycielski(9,Cn(9))))            # N=19
    inst.append(("M(Petersen)",    *mycielski(10,[(0,1),(1,2),(2,3),(3,4),(4,0),(0,5),(1,6),(2,7),(3,8),(4,9),(5,7),(7,9),(9,6),(6,8),(8,5)])))  # N=21
    inst.append(("M(Grotzsch)",    *mycielski(*mycielski(5,Cn(5)))))# N=23
    # bridged glued islands (triangle-free: single bridge between two tri-free comps)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]
        return n, E+[(u, n1+v)]
    inst.append(("C5|brg|M(C7)",   *bridge((5,Cn(5)), mycielski(7,Cn(7)), 0, 0)))   # N=20
    inst.append(("C7|brg|Grotzsch",*bridge((7,Cn(7)), mycielski(5,Cn(5)), 0, 0)))   # N=18
    inst.append(("M(C7)|brg|M(C7)",*bridge(mycielski(7,Cn(7)), mycielski(7,Cn(7)), 14, 14)))  # N=30 (apex bridge)
    fails=[]; maxr=0
    for it in inst:
        res=test(*it)
        if res and res[0]=='FAIL': fails.append(res)
        elif res and res[0]=='OK': maxr=max(maxr,res[3])
    print(f"\n=== SUMMARY: hard-gate FAILS={len(fails)} max-switch-radius-overall={maxr} ===",flush=True)
    if fails:
        for f in fails: print("   FAIL:",f)
    else:
        print("   selected-cut fractional SPLIT holds on ALL hard instances; switch-repair radius bounded.",flush=True)
