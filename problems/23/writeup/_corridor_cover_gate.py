"""Exact-gate Codex's PER-GEODESIC corridor-capacity sublemma (block 148):
for unique-geo f with path P_f, every bad edge g != f, every geodesic Q in cyc(g): let [r,s] = contiguous
interval of P_f-positions hit by Q (skip if Q cap P_f empty). Then
   |Q cap P_f| <= sum_{C: span(C) cap [r,s] != empty} cap(C).
Independent reimpl. Battery: census N<=11 + structured + glued. Exact Fraction (counts are integers here).
Reports first violation."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def row_cover_ok(n, adj, s, name, first):
    st=struct_for_side(n,adj,s)
    if st is None: return 0,0
    M,ell,T,mu,cyc=st
    urows=0; fails=0
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
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
        urows+=1
        for g in M:
            if g==f: continue   # claim is for g != f
            for Q in cyc[g]:
                hit=sorted(pos[v] for v in Q if v in Pset)
                if not hit: continue
                r,smax=hit[0],hit[-1]
                lhs=len(hit)  # |Q cap P_f|
                rhs=sum(c for (lo,hi,c) in compinfo if not (hi<r or lo>smax))  # span cap [r,s] nonempty
                if lhs>rhs:
                    fails+=1
                    if first[0] is None: first[0]=(name,''.join(map(str,s)),f,g,Q,P_f,(r,smax),lhs,rhs)
    return urows,fails

def run(name,n,E,first):
    adj,cuts=gmins(n,E); U=Fl=0
    for s in cuts:
        u,f=row_cover_ok(n,adj,s,name,first); U+=u; Fl+=f
    return name,len(cuts),U,Fl

if __name__=="__main__":
    print("=== PER-GEODESIC corridor-capacity sublemma gate (exact) ===",flush=True)
    first=[None]
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        U=Fl=0
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts:
                u,f=row_cover_ok(n,adj,s,g6,first); U+=u; Fl+=f
        print(f"  census N={nn}: unique-rows={U} COVER-FAIL={Fl}",flush=True)
        if first[0]: break
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),
           ("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [structured/glued]: name cuts unique-rows COVER-FAIL",flush=True)
    for it in extra:
        print("   ",run(*it,first),flush=True)
    print(f"\n=== {'FIRST VIOLATION: '+str(first[0]) if first[0] else 'NO VIOLATION (per-geodesic corridor capacity holds on battery)'} ===",flush=True)
