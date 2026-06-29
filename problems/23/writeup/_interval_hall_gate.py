"""Exact-gate Codex's RESTRICTED INTERVAL FLOW (block 152) = the INTERVAL HALL / corridor inequality.
Since all demand for target [a,b] routes to {C:span cap [a,b]}, feasibility <=> total demand <= cap, i.e.
for every unique f, every path-interval [a,b]:
   sum_{i in [a,b]} (S(x_i)-1)  <=  sum_{C: span(C) cap [a,b] != empty} |C|.
With conditional interval uncrossing (validated) => full UPO Hall => unique-path case. THE reduction target.
Battery: census N<=11 + K??CB@OBDOAp + glued. Exact Fraction. Reports first violation + the binding [a,b]."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def row_ok(n, adj, s, name, first):
    st=struct_for_side(n,adj,s)
    if st is None: return 0,0
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    urows=0; fails=0
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
        compinfo=[]
        for root,C in cdict.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: compinfo.append((min(A),max(A),len(C)))
        urows+=1
        for a in range(L):
            for b in range(a,L):
                lhs=sum(dvec[i] for i in range(a,b+1))
                rhs=sum(c for (lo,hi,c) in compinfo if not (hi<a or lo>b))
                if lhs>rhs:
                    fails+=1
                    if first[0] is None: first[0]=(name,''.join(map(str,s)),f,P_f,[str(x) for x in dvec],(a,b),str(lhs),rhs,compinfo)
    return urows, fails

def run(name,n,E,first):
    adj,cuts=gmins(n,E); U=Fl=0
    for s in cuts:
        u,f=row_ok(n,adj,s,name,first); U+=u; Fl+=f
    return name,len(cuts),U,Fl

if __name__=="__main__":
    print("=== INTERVAL HALL / corridor inequality gate (block 152, exact) ===",flush=True)
    first=[None]
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        U=Fl=0
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts:
                u,f=row_ok(n,adj,s,g6,first); U+=u; Fl+=f
        print(f"  census N={nn}: unique-rows={U} INTERVAL-HALL-FAIL={Fl}",flush=True)
        if first[0]: break
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),
           ("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [structured/glued]: name cuts unique-rows INTERVAL-HALL-FAIL",flush=True)
    for it in extra:
        print("   ",run(*it,first),flush=True)
    print(f"\n=== {'FIRST VIOLATION: '+str(first[0]) if first[0] else 'NO VIOLATION (interval Hall holds => with uncrossing, full UPO Hall on battery)'} ===",flush=True)
