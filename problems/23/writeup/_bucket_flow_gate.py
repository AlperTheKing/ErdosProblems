"""Exact-gate Codex's BASE/SURPLUS BUCKET FLOW (block 163), constructive strengthening of the packing flow.
Each off-path component C => base bucket (cap=spanlen=hi-lo+1) + surplus bucket (cap=|C|-spanlen, omit if 0).
Demand node per (g!=f, Q in cyc[g]) with Q cap P nonempty: demand=|Q cap P|/|cyc[g]|, interval(Q).
Routing: unique g (|cyc[g]|=1) -> base buckets only (span cap interval); fan g (|cyc[g]|>=2) -> base AND surplus
buckets (span cap interval). Claim: feasible (max flow == total demand) for every unique row. Exact max-flow.
Battery census N<=11 + structured + glued. Reports first infeasible row."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def maxflow(cap, src, snk, Nn):
    flow=F(0)
    while True:
        par=[-1]*Nn; par[src]=src; q=deque([src])
        while q:
            u=q.popleft()
            for v in range(Nn):
                if par[v]==-1 and cap[u][v]>0:
                    par[v]=u; q.append(v)
        if par[snk]==-1: break
        v=snk; b=None
        while v!=src:
            u=par[v]; b=cap[u][v] if b is None else min(b,cap[u][v]); v=u
        v=snk
        while v!=src:
            u=par[v]; cap[u][v]-=b; cap[v][u]+=b; v=u
        flow+=b
    return flow

def row_feasible(n, adj, s):
    st=struct_for_side(n,adj,s)
    if st is None: return 0,0,None
    M,ell,T,mu,cyc=st
    urows=0; infeas=0; firstbad=None
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
        comps=[]
        for root,C in cdict.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: comps.append((min(A),max(A),len(C)))
        # demand nodes
        dem=[]  # (demand, interval, isunique)
        for g in M:
            if g==f: continue
            k=len(cyc[g]); uniq=(k==1)
            for Q in cyc[g]:
                hit=sorted(pos[v] for v in Q if v in Pset)
                if not hit: continue
                dem.append((F(len(hit),k),(hit[0],hit[-1]),uniq))
        if not dem: continue
        urows+=1
        nd=len(dem)
        # buckets: base per comp, surplus per comp(if>0)
        buckets=[]  # (cap, lo, hi, kind)  kind 0=base 1=surplus
        for (lo,hi,cp) in comps:
            bl=hi-lo+1; buckets.append((bl,lo,hi,0))
            sp=cp-bl
            if sp>0: buckets.append((sp,lo,hi,1))
        nb=len(buckets)
        # nodes: 0 src, 1 snk, 2..2+nd-1 demands, 2+nd.. buckets
        Nn=2+nd+nb; cap=[[F(0)]*Nn for _ in range(Nn)]
        total=F(0)
        for i,(d,_,_) in enumerate(dem): cap[0][2+i]=d; total+=d
        for j,(bc,_,_,_) in enumerate(buckets): cap[2+nd+j][1]=bc
        BIG=total+1
        for i,(d,(r,smax),uniq) in enumerate(dem):
            for j,(bc,lo,hi,kind) in enumerate(buckets):
                if hi<r or lo>smax: continue  # span must intersect interval
                if kind==1 and uniq: continue  # unique forbidden from surplus
                cap[2+i][2+nd+j]=BIG
        fl=maxflow(cap,0,1,Nn)
        if fl!=total:
            infeas+=1
            if firstbad is None: firstbad=(''.join(map(str,s)),f,P_f,[(str(d),iv,u) for (d,iv,u) in dem],comps)
    return urows, infeas, firstbad

if __name__=="__main__":
    print("=== BASE/SURPLUS BUCKET FLOW feasibility gate (block 163, exact max-flow) ===",flush=True)
    first=[None]
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        U=Inf=0
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts:
                u,inf,fb=row_feasible(n,adj,s); U+=u; Inf+=inf
                if fb and first[0] is None: first[0]=(g6,)+fb
        print(f"  census N={nn}: unique-rows={U} INFEASIBLE={Inf}",flush=True)
        if first[0]: break
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [structured/glued]:",flush=True)
    for name,n,E in extra:
        adj,cuts=gmins(n,E); U=Inf=0
        for s in cuts:
            u,inf,fb=row_feasible(n,adj,s); U+=u; Inf+=inf
            if fb and first[0] is None: first[0]=(name,)+fb
        print(f"    {name}: unique-rows={U} INFEASIBLE={Inf}",flush=True)
    print(f"\n  === {'FIRST INFEASIBLE: '+str(first[0]) if first[0] else 'ALL FEASIBLE (base/surplus bucket flow feasible => unique-geo forbidden from surplus still routes; direct UPO)'} ===",flush=True)
