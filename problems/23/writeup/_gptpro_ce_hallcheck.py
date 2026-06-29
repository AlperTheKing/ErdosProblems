"""Does plain INTERVAL HALL (demand<=cap) and the BUCKET FLOW survive at N=26 on gamma-min, even though the
unique/fan split (UNIQUE-BASE) died? Determines if the Hall framework is salvageable or fully census-blind."""
from fractions import Fraction as F
from collections import deque
from _satzmu_conn import struct_for_side
from _stark1 import gmins

n=26
E=[]
for i in range(12): E.append((i,i+1))
det=[0,13,14,15,16,17,18,19,20,21,22,23,24,25,12]
for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
E += [(0,4),(4,8),(8,12),(0,12)]
E=sorted(set(E))
adj2,cuts=gmins(n,E)

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

ih_fail=0; bf_infeas=0; urows=0
for s in cuts:
    st=struct_for_side(n,adj2,s)
    if st is None: continue
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    for f in M:
        if len(cyc[f])!=1: continue
        urows+=1
        P=cyc[f][0]; L=len(P); pos={x:i for i,x in enumerate(P)}; Pset=set(P)
        dvec=[S[v]-1 for v in P]
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj2[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cd={}
        for v in rest: cd.setdefault(find(v),set()).add(v)
        comps=[]
        for r,C in cd.items():
            A=set(pos[x] for u in C for x in adj2[u] if x in Pset and s[u]!=s[x])
            if A: comps.append((min(A),max(A),len(C)))
        # interval Hall: demand<=cap for all [a,b]
        for a in range(L):
            for b in range(a,L):
                dem=sum(dvec[i] for i in range(a,b+1))
                cap=sum(c for (lo,hi,c) in comps if not (hi<a or lo>b))
                if dem>cap: ih_fail+=1
        # bucket flow feasibility
        dem=[];
        for g in M:
            if g==f: continue
            k=len(cyc[g]); uniq=(k==1)
            for Q in cyc[g]:
                hit=sorted(pos[v] for v in Q if v in Pset)
                if not hit: continue
                dem.append((F(len(hit),k),(hit[0],hit[-1]),uniq))
        if dem:
            buckets=[]
            for (lo,hi,cp) in comps:
                bl=hi-lo+1; buckets.append((bl,lo,hi,0))
                if cp-bl>0: buckets.append((cp-bl,lo,hi,1))
            nd=len(dem); nb=len(buckets); Nn=2+nd+nb
            cap=[[F(0)]*Nn for _ in range(Nn)]; total=F(0)
            for i,(d,_,_) in enumerate(dem): cap[0][2+i]=d; total+=d
            for j,(bc,_,_,_) in enumerate(buckets): cap[2+nd+j][1]=bc
            BIG=total+1
            for i,(d,(r,sm),uq) in enumerate(dem):
                for j,(bc,lo,hi,kind) in enumerate(buckets):
                    if hi<r or lo>sm: continue
                    if kind==1 and uq: continue
                    cap[2+i][2+nd+j]=BIG
            if maxflow(cap,0,1,Nn)!=total: bf_infeas+=1
print(f"N=26 gamma-min: unique-rows={urows}")
print(f"  INTERVAL HALL (demand<=cap) failures: {ih_fail}  <- {'DEAD at N=26' if ih_fail else 'HOLDS'}")
print(f"  BUCKET FLOW infeasible rows:          {bf_infeas}  <- {'DEAD at N=26' if bf_infeas else 'HOLDS'}")
print("(UPO itself = 0 violations on gamma-min, established. So if interval Hall/bucket-flow DEAD but UPO holds,")
print(" the entire Hall/flow certificate framework is census-blind; UPO needs a direct proof not via these.)")
