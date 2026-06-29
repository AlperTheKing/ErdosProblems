"""Exact-gate Codex's interval SURPLUS formulation (block 160). Using proved span-capacity (surplus(C)=
|C|-spanlen(C)>=0): for every path interval I=[a,b], demand(I)=sum_{[a,b]}d_i, base(I)=sum_{C:span cap I}
spanlen(C), surplus(I)=sum_{C:span cap I}surplus(C). Interval Hall = demand<=base+surplus; SPLIT form:
max(0,demand-base) <= surplus. Report worst ratio (demand-base)/surplus, witness, #active components at worst,
and any VIOLATION (overrun>surplus). Battery census N<=11 + structured + glued. Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def row_scan(n, adj, s, name, acc):
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        dvec=[S[P_f[i]]-1 for i in range(L)]
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cdict={}
        for v in rest: cdict.setdefault(find(v),set()).add(v)
        comps=[]
        for root,C in cdict.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: comps.append((min(A),max(A),len(C)))  # lo,hi,cap
        for a in range(L):
            for b in range(a,L):
                demand=sum(dvec[i] for i in range(a,b+1))
                active=[(lo,hi,cap) for (lo,hi,cap) in comps if not (hi<a or lo>b)]
                base=sum(hi-lo+1 for (lo,hi,cap) in active)
                surplus=sum(cap-(hi-lo+1) for (lo,hi,cap) in active)
                overrun=demand-base
                if overrun>0:
                    acc['overrun']+=1
                    if overrun>surplus:
                        acc['viol']+=1
                        if acc['firstviol'] is None: acc['firstviol']=(name,''.join(map(str,s)),f,(a,b),str(demand),base,surplus,active)
                    else:
                        ratio=overrun/surplus if surplus>0 else F(10**9)
                        if acc['worst'] is None or ratio>acc['worst'][0]:
                            acc['worst']=(ratio, name, f, (a,b), str(demand), base, surplus, len(active), active)

if __name__=="__main__":
    print("=== INTERVAL SURPLUS formulation gate (block 160): max(0,demand-base)<=surplus (exact) ===",flush=True)
    acc={'overrun':0,'viol':0,'worst':None,'firstviol':None}
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        o0=acc['overrun']; v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: row_scan(n,adj,s,g6,acc)
        print(f"  census N={nn}: positive-overrun={acc['overrun']-o0} VIOL(overrun>surplus)={acc['viol']-v0}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [structured/glued]:",flush=True)
    for name,n,E in extra:
        o0=acc['overrun']; v0=acc['viol']; adj,cuts=gmins(n,E)
        for s in cuts: row_scan(n,adj,s,name,acc)
        print(f"    {name}: positive-overrun={acc['overrun']-o0} VIOL={acc['viol']-v0}",flush=True)
    print(f"\n  TOTAL positive-overrun={acc['overrun']} VIOL={acc['viol']}",flush=True)
    if acc['worst']:
        w=acc['worst']
        print(f"  WORST ratio (demand-base)/surplus = {w[0]} = {float(w[0]):.4f} at {w[1]} f={w[2]} I={w[3]} demand={w[4]} base={w[5]} surplus={w[6]} #active-components={w[7]}",flush=True)
    print(f"  === {'VIOLATION: '+str(acc['firstviol']) if acc['firstviol'] else 'NO VIOLATION (max(0,demand-base)<=surplus everywhere; worst ratio<1 => interval Hall holds with surplus margin)'} ===",flush=True)
