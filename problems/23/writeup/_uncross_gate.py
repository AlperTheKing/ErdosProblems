"""Independently exact-gate Codex's CONDITIONAL INTERVAL UNCROSSING (block 146):
for each unique-geo bad edge f, with h(I)=sum_{C:span(C) cap I}cap(C) - sum_{i in I}d_i,
   if h(I) <= 0 for some position-set I, then SOME contiguous interval J has h(J) <= h(I).
Implies (interval-Hall => full Hall). Independent reimpl. Battery: census N<=11 + structured + glued.
Sound check: hmin_int = min over intervals of h; for every I with h(I)<=0, require hmin_int <= h(I).
Equivalently when min_all<=0, require min_all attained by an interval. Exact Fraction. Reports first violation."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def row_uncross_ok(n, adj, s, name, first):
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
        d=[S[P_f[i]]-1 for i in range(L)]
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
        def h(I):
            return sum(c for (lo,hi,c) in compinfo if any(lo<=i<=hi for i in I)) - sum(d[i] for i in I)
        # min over contiguous intervals
        hmin_int=None
        for a in range(L):
            for b in range(a,L):
                hv=h(range(a,b+1))
                if hmin_int is None or hv<hmin_int: hmin_int=hv
        urows+=1
        # check: every I with h(I)<=0 has hmin_int <= h(I)
        bad=None
        for r in range(1,L+1):
            for I in itertools.combinations(range(L),r):
                hv=h(I)
                if hv<=0 and hmin_int>hv:
                    bad=(I, str(hv), str(hmin_int)); break
            if bad: break
        if bad is not None:
            fails+=1
            if first[0] is None: first[0]=(name, ''.join(map(str,s)), f, P_f, [str(x) for x in d], compinfo, bad)
    return urows, fails

def run(name,n,E,first):
    adj,cuts=gmins(n,E); U=Fl=0
    for s in cuts:
        u,f=row_uncross_ok(n,adj,s,name,first); U+=u; Fl+=f
    return name,len(cuts),U,Fl

if __name__=="__main__":
    print("=== CONDITIONAL INTERVAL UNCROSSING gate (exact) ===",flush=True)
    first=[None]
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        U=Fl=0
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts:
                u,f=row_uncross_ok(n,adj,s,g6,first); U+=u; Fl+=f
        print(f"  census N={nn}: unique-rows={U} UNCROSS-FAIL={Fl}",flush=True)
        if first[0]: break
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),
           ("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [structured/glued]: name cuts unique-rows UNCROSS-FAIL",flush=True)
    for it in extra:
        print("   ",run(*it,first),flush=True)
    print(f"\n=== {'FIRST VIOLATION: '+str(first[0]) if first[0] else 'NO VIOLATION (conditional interval uncrossing holds => interval-Hall implies full Hall on battery)'} ===",flush=True)
