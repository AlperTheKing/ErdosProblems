"""Exact-gate Codex's GEODESIC-INTERVAL PACKING FLOW (block 151), the superposition certificate.
For unique f with path P_f and off-path components C (span, cap=|C|): demand node per (g!=f, Q in cyc(g)) with
Q cap P_f nonempty, interval [r,s], demand = |Q cap P_f| / |cyc(g)|; routes to C iff span(C) cap [r,s] != empty.
Claim: bipartite rational flow (source->demand cap=demand, demand->comp if span meets interval, comp->sink
cap=|C|) is FEASIBLE (max flow == total demand). EXACT max-flow via BFS-augmenting with Fraction.
Battery: census N<=11 + K??CB@OBDOAp + K??CE@A{?]Fc + glued islands. Reports first infeasible row."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def maxflow_feasible(demands, comps, edges, total):
    # nodes: 0=src, 1=sink, 2..2+nd-1 = demand, 2+nd.. = comp
    nd=len(demands); nc=len(comps); N=2+nd+nc
    cap=[[F(0)]*N for _ in range(N)]
    for i,d in enumerate(demands): cap[0][2+i]=d
    for j,c in enumerate(comps): cap[2+nd+j][1]=c
    BIG=total+1
    for (i,j) in edges: cap[2+i][2+nd+j]=BIG
    flow=F(0)
    while True:
        par=[-1]*N; par[0]=0; q=deque([0])
        while q:
            u=q.popleft()
            for v in range(N):
                if par[v]==-1 and cap[u][v]>0:
                    par[v]=u; q.append(v)
                    if v==1: break
            if par[1]!=-1: break
        if par[1]==-1: break
        # bottleneck
        v=1; b=None
        while v!=0:
            u=par[v]; b=cap[u][v] if b is None else min(b,cap[u][v]); v=u
        v=1
        while v!=0:
            u=par[v]; cap[u][v]-=b; cap[v][u]+=b; v=u
        flow+=b
    return flow==total

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
        compinfo=[]
        for root,C in cdict.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: compinfo.append((min(A),max(A),len(C)))
        comps=[c for (lo,hi,c) in compinfo]
        demands=[]; intervals=[]
        for g in M:
            if g==f: continue
            k=len(cyc[g])
            for Q in cyc[g]:
                hit=sorted(pos[v] for v in Q if v in Pset)
                if not hit: continue
                demands.append(F(len(hit),k)); intervals.append((hit[0],hit[-1]))
        edges=[]
        for i,(r,smax) in enumerate(intervals):
            for j,(lo,hi,c) in enumerate(compinfo):
                if not (hi<r or lo>smax): edges.append((i,j))
        urows+=1
        total=sum(demands)
        if not maxflow_feasible(demands, comps, edges, total):
            infeas+=1
            if firstbad is None: firstbad=(''.join(map(str,s)),f,P_f,[str(d) for d in demands],intervals,compinfo)
    return urows, infeas, firstbad

if __name__=="__main__":
    print("=== GEODESIC-INTERVAL PACKING FLOW feasibility gate (exact max-flow) ===",flush=True)
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
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),
           ("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [structured/glued]: name cuts unique-rows INFEASIBLE",flush=True)
    for name,n,E in extra:
        adj,cuts=gmins(n,E); U=Inf=0
        for s in cuts:
            u,inf,fb=row_feasible(n,adj,s); U+=u; Inf+=inf
            if fb and first[0] is None: first[0]=(name,)+fb
        print(f"    {name}: cuts={len(cuts)} unique-rows={U} INFEASIBLE={Inf}",flush=True)
    print(f"\n=== {'FIRST INFEASIBLE: '+str(first[0]) if first[0] else 'ALL FEASIBLE (geodesic-interval packing flow feasible on battery => superposition holds)'} ===",flush=True)
