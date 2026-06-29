"""Exact-gate Codex's COMPONENT SPAN-CAPACITY lemma (block 159): for each off-path B-component C of a unique-geo
row, with attachment span [lo,hi] and cap=|C|:  cap >= hi - lo + 1.
PROOF (audited): C connected => B-walk x_lo -(B-edge)- u ...(d_C edges in C)... w -(B-edge)- x_hi has length
d_C(u,w)+2 where u,w are attachment vertices for lo,hi. By P uniqueness this walk != hi-lo (=> 2nd f-geodesic)
and !< hi-lo (P shortest); B bipartite => walk same parity as hi-lo => walk >= hi-lo+2 => d_C >= hi-lo =>
cap >= d_C+1 >= hi-lo+1. Gate confirms + also reports the surplus cap-(hi-lo+1) distribution.
Battery: census N<=11 + structured + glued + Mycielskians. Exact (integer)."""
import subprocess
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def row_scan(n, adj, s, name, first, acc):
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cdict={}
        for v in rest: cdict.setdefault(find(v),set()).add(v)
        for root,C in cdict.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if not A: continue
            lo,hi=min(A),max(A); cap=len(C); acc['comps']+=1
            surplus=cap-(hi-lo+1)
            acc['surplus'].setdefault(surplus,0); acc['surplus'][surplus]+=1
            if cap < hi-lo+1:
                acc['viol']+=1
                if first[0] is None: first[0]=(name,''.join(map(str,s)),f,P_f,sorted(C),sorted(A),lo,hi,cap)

if __name__=="__main__":
    print("=== COMPONENT SPAN-CAPACITY lemma gate: cap >= hi-lo+1 (block 159, exact) ===",flush=True)
    first=[None]; acc={'comps':0,'viol':0,'surplus':{}}
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        c0=acc['comps']; v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: row_scan(n,adj,s,g6,first,acc)
        print(f"  census N={nn}: components={acc['comps']-c0} VIOL(cap<hi-lo+1)={acc['viol']-v0}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("M(C7)",)+mycielski(7,Cn(7)),("M(Grotzsch)N23",)+mycielski(*mycielski(5,Cn(5))),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [structured/glued/Myc]:",flush=True)
    for name,n,E in extra:
        c0=acc['comps']; v0=acc['viol']; adj,cuts=gmins(n,E)
        for s in cuts: row_scan(n,adj,s,name,first,acc)
        print(f"    {name}: components={acc['comps']-c0} VIOL={acc['viol']-v0}",flush=True)
    print(f"\n  TOTAL components={acc['comps']} VIOL={acc['viol']}",flush=True)
    print(f"  surplus cap-(hi-lo+1) distribution: {dict(sorted(acc['surplus'].items()))}",flush=True)
    print(f"  === {'FIRST VIOLATION: '+str(first[0]) if first[0] else 'cap >= hi-lo+1 holds for ALL components (span-capacity lemma confirmed)'} ===",flush=True)
