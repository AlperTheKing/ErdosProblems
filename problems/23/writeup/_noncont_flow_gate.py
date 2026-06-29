"""Exact-gate Codex's constructive FLOW certificate for Part A (block 177). For unique f, non-P-contained g!=f:
position demand load_i = sum over non-contained g, geodesics Q through x_i, of 1/|cyc(g)|. Off-path components C
(span [lo,hi], cap |C|). Bipartite flow: source->position i (cap load_i), position i->component C iff lo<=i<=hi,
C->sink (cap |C|). Feasible iff max flow == sum_i load_i. Battery: census N<=11 gamma-min + k-chord non-gamma +
glued. Exact Fraction max-flow. Reports first infeasible row."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def maxflow(cap,src,snk,Nn):
    flow=F(0)
    while True:
        par=[-1]*Nn; par[src]=src; q=deque([src])
        while q:
            u=q.popleft()
            for v in range(Nn):
                if par[v]==-1 and cap[u][v]>0: par[v]=u; q.append(v)
        if par[snk]==-1: break
        v=snk; b=None
        while v!=src: u=par[v]; b=cap[u][v] if b is None else min(b,cap[u][v]); v=u
        v=snk
        while v!=src: u=par[v]; cap[u][v]-=b; cap[v][u]+=b; v=u
        flow+=b
    return flow

def kchord(k, clen=4):
    pend=clen*k; E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for j in range(k): E.append((clen*j, clen*j+clen))
    E.append((0,pend))
    return pend+1+nint, sorted(set((min(a,b),max(a,b)) for a,b in E))

def check_cut(n,adj,s,name,acc):
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        load=[F(0)]*L
        for g in M:
            if g==f: continue
            if any(set(Q)<=Pset for Q in cyc[g]): continue  # P-contained skip
            d=pf[g]
            for v,pv in d.items():
                if v in Pset: load[pos[v]]+=pv
        if all(x==0 for x in load): continue
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cd={}
        for v in rest: cd.setdefault(find(v),set()).add(v)
        comps=[]
        for r,C in cd.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: comps.append((min(A),max(A),len(C)))
        posidx=[i for i in range(L) if load[i]>0]; nc=len(comps); npn=len(posidx)
        Nn=2+npn+nc; capm=[[F(0)]*Nn for _ in range(Nn)]; total=F(0)
        for j,i in enumerate(posidx): capm[0][2+j]=load[i]; total+=load[i]
        for jc,(lo,hi,c) in enumerate(comps): capm[2+npn+jc][1]=c
        BIG=total+1
        for j,i in enumerate(posidx):
            for jc,(lo,hi,c) in enumerate(comps):
                if lo<=i<=hi: capm[2+j][2+npn+jc]=BIG
        acc['rows']+=1
        if maxflow(capm,0,1,Nn)!=total:
            acc['infeas']+=1
            if acc['first'] is None: acc['first']=(name,''.join(map(str,s)),f,[str(x) for x in load],comps)

if __name__=="__main__":
    print("=== Part-A constructive FLOW certificate (block 177, exact max-flow) ===",flush=True)
    acc={'rows':0,'infeas':0,'first':None}
    for clen in (4,6):
        for k in (3,6,9):
            n,E=kchord(k,clen); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            s=[v%2 for v in range(n)]; r0=acc['rows']; i0=acc['infeas']
            check_cut(n,adj,s,f"k{k}c{clen}",acc)
            print(f"  kchord k={k} clen={clen} N={n} parity: rows-with-noncont={acc['rows']-r0} INFEASIBLE={acc['infeas']-i0}",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        r0=acc['rows']; i0=acc['infeas']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: check_cut(n,adj,s,g6,acc)
        print(f"  census N={nn} gamma-min: rows={acc['rows']-r0} INFEASIBLE={acc['infeas']-i0}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    for name,(nn,E) in [("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]:
        adj,cuts=gmins(nn,E); r0=acc['rows']; i0=acc['infeas']
        for s in cuts: check_cut(nn,adj,s,name,acc)
        print(f"  {name} N={nn}: rows={acc['rows']-r0} INFEASIBLE={acc['infeas']-i0}",flush=True)
    print(f"\n  TOTAL rows-with-noncont-demand={acc['rows']} INFEASIBLE={acc['infeas']}",flush=True)
    print(f"  === {'INFEASIBLE: '+str(acc['first']) if acc['first'] else 'Part-A flow feasible everywhere: noncontained demand routes to detour components (constructive proof route valid)'} ===",flush=True)
