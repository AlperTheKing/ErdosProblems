"""Exact-gate Codex's UPO POSITION-FLOW certificate (block 143). For each unique-geodesic bad edge f with
path P_f=(x_0..x_{ell-1}): d_i = S(x_i)-1 (S=sum_g p_g). Cut graph B = cross edges. Components C of B - V(P_f);
A(C)=path positions attached to C via a B-edge; span(C)=[min A(C),max A(C)]; cap(C)=|C|. Hall feasibility:
for every position set I, sum_{i in I} d_i <= sum_{C: span(C) cap I != empty} |C|. If holds for all unique rows,
proves UPO (sum_i S(x_i)=ell+sum d_i <= ell+(N-ell)=N). Independent reimpl as cross-check of Codex's scanner.
Battery: census N<=11 + structured + glued islands + blow-ups. Exact Fraction. Reports first Hall violation."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def hall_ok(n, adj, s, side_str, name, first):
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
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}
        Pset=set(P_f); urows+=1
        d=[S[P_f[i]]-1 for i in range(L)]  # demands
        # components of B - V(P_f): cross-edge adjacency among off-path vertices
        rest=[v for v in range(n) if v not in Pset]
        par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w in Pset: continue
                if s[u]!=s[w]:  # B-edge (cross)
                    par[find(u)]=find(w)
        comps={}
        for v in rest: comps.setdefault(find(v),set()).add(v)
        # spans + caps
        compinfo=[]
        for root,C in comps.items():
            A=set()
            for u in C:
                for x in adj[u]:
                    if x in Pset and s[u]!=s[x]: A.add(pos[x])
            if not A: continue
            compinfo.append((min(A),max(A),len(C)))
        # Hall over all I subset of positions
        viol=None
        for r in range(1,L+1):
            for I in itertools.combinations(range(L),r):
                Iset=set(I)
                lhs=sum(d[i] for i in I)
                rhs=sum(c for (lo,hi,c) in compinfo if any(lo<=i<=hi for i in I))
                if lhs>rhs:
                    viol=(I, str(lhs), rhs); break
            if viol: break
        if viol is not None:
            fails+=1
            if first[0] is None:
                first[0]=(name, side_str, f, P_f, [str(x) for x in d], compinfo, viol)
    return urows, fails

def run(name,n,E,first):
    adj,cuts=gmins(n,E); U=Fl=0
    for s in cuts:
        u,f=hall_ok(n,adj,s,''.join(map(str,s)),name,first); U+=u; Fl+=f
    return name,len(cuts),U,Fl

if __name__=="__main__":
    print("=== UPO POSITION-FLOW Hall certificate gate (exact) ===",flush=True)
    first=[None]
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        U=Fl=0
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts:
                u,f=hall_ok(n,adj,s,g6,g6,first); U+=u; Fl+=f
        print(f"  census N={nn}: unique-rows={U} HALL-FAIL={Fl}",flush=True)
        if first[0]: break
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),
           ("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("GDSKVG",)+dec("GDSKVG"),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [structured/glued]: name cuts unique-rows HALL-FAIL",flush=True)
    for it in extra:
        print("   ",run(*it,first),flush=True)
    print(f"\n=== {'FIRST HALL VIOLATION: '+str(first[0]) if first[0] else 'NO VIOLATION (UPO position-flow certificate holds on battery)'} ===",flush=True)
