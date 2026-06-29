"""Exact-gate Codex's POINTWISE UNIQUE-BASE (block 164): for unique-geo f with path P, every position i:
  uload(i) = #{bad edges g!=f, len(cyc[g])=1, cyc[g][0] contains x_i}   (unique geodesics through x_i)
  cover(i) = #{off-path B-component C : lo(C) <= i <= hi(C)}            (component spans covering i)
Claim: uload(i) <= cover(i). Implies UNIQUE-BASE (U(I)=sum_I uload <= sum_I cover = sum_C |span cap I| <= base(I)).
Battery census N<=11 + structured + glued + Mycielskians. Exact (integers). Reports first i with uload>cover."""
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
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cdict={}
        for v in rest: cdict.setdefault(find(v),set()).add(v)
        spans=[]
        for root,C in cdict.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: spans.append((min(A),max(A)))
        # unique-g geodesics through each position
        uload=[0]*L
        for g in M:
            if g==f or len(cyc[g])!=1: continue
            Q=cyc[g][0]
            for v in Q:
                if v in Pset: uload[pos[v]]+=1
        for i in range(L):
            cover=sum(1 for (lo,hi) in spans if lo<=i<=hi)
            acc['pos']+=1
            if uload[i]>cover:
                acc['viol']+=1
                if first[0] is None:
                    contribs=[g for g in M if g!=f and len(cyc[g])==1 and P_f[i] in cyc[g][0]]
                    first[0]=(name,''.join(map(str,s)),f,P_f,i,uload[i],cover,spans,contribs)

if __name__=="__main__":
    print("=== POINTWISE UNIQUE-BASE gate (block 164): uload(i) <= cover(i) (exact) ===",flush=True)
    first=[None]; acc={'pos':0,'viol':0}
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        p0=acc['pos']; v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: row_scan(n,adj,s,g6,first,acc)
        print(f"  census N={nn}: positions={acc['pos']-p0} VIOL(uload>cover)={acc['viol']-v0}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("M(C7)",)+mycielski(7,Cn(7)),("M(Grotzsch)N23",)+mycielski(*mycielski(5,Cn(5))),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [structured/glued/Myc]:",flush=True)
    for name,n,E in extra:
        p0=acc['pos']; v0=acc['viol']; adj,cuts=gmins(n,E)
        for s in cuts: row_scan(n,adj,s,name,first,acc)
        print(f"    {name}: positions={acc['pos']-p0} VIOL={acc['viol']-v0}",flush=True)
    print(f"\n  TOTAL positions={acc['pos']} VIOL={acc['viol']}",flush=True)
    print(f"  === {'FIRST VIOLATION: '+str(first[0]) if first[0] else 'POINTWISE UNIQUE-BASE holds (uload<=cover) => UNIQUE-BASE'} ===",flush=True)
