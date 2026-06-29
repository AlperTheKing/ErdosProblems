"""Characterize WHERE the UPO position-flow Hall condition binds (proof aid for Codex's fractional Hall).
For each unique-geo row, compute Hall slack = min over position-sets I of [ sum_{C:span cap I}|C| - sum_{i in I}d_i ],
the binding I (argmin), and whether binding I is a contiguous interval. Report tight (slack=0) cases + structure.
Census N<=11 + nested/glued. Exact Fraction."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def row_binding(n, adj, s):
    st=struct_for_side(n,adj,s)
    if st is None: return []
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
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        d=[S[P_f[i]]-1 for i in range(L)]
        rest=[v for v in range(n) if v not in Pset]
        par={v:v for v in rest}
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
        best=None
        for r in range(1,L+1):
            for I in itertools.combinations(range(L),r):
                lhs=sum(d[i] for i in I)
                rhs=sum(c for (lo,hi,c) in compinfo if any(lo<=i<=hi for i in I))
                slack=rhs-lhs
                if best is None or slack<best[0]: best=(slack,I)
        slack,I=best
        is_interval = (len(I)<=1) or (list(I)==list(range(I[0],I[0]+len(I))))
        out.append((slack, I, L, is_interval))
    return out

if __name__=="__main__":
    print("=== UPO Hall BINDING characterization (exact) ===",flush=True)
    tight_total=0; binding_interval_when_tight=0; tight_examples=[]
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        minslack=None; tight=0; ti=0
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts:
                for (slack,I,L,isint) in row_binding(n,adj,s):
                    if minslack is None or slack<minslack: minslack=slack
                    if slack==0:
                        tight+=1
                        if isint: ti+=1
        print(f"  census N={nn}: min-Hall-slack={minslack} tight(slack0)-rows={tight} of-which-binding-I-interval={ti}",flush=True)
        tight_total+=tight; binding_interval_when_tight+=ti
    # structured
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    for name,(nn,E) in [("K??CB@OBDOAp",dec("K??CB@OBDOAp")),("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]:
        adj,cuts=gmins(nn,E); ms=None; tt=0; ii=0
        for s in cuts:
            for (slack,I,L,isint) in row_binding(nn,adj,s):
                if ms is None or slack<ms: ms=slack
                if slack==0: tt+=1; ii+=isint
        print(f"  {name}: min-slack={ms} tight-rows={tt} binding-interval={ii}",flush=True)
    print(f"\n=== tight rows total={tight_total}, binding-I is contiguous interval in {binding_interval_when_tight}/{tight_total} ===",flush=True)
