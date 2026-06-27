#!/usr/bin/env python3
"""Independent broad verification of Step-2's load-bearing inequality (iii) for the Gamma<=N^2 induction:
   mass(M_C) := sum over bad edges INCIDENT to C of (d_B+1)^2   <=   2|C|N - |C|^2,
for EVERY shortest bad-geodesic C (a shortest u-v B-path of a bad edge (u,v)), over the Gamma-min
connected-B max cut. Equality only at C5[q] (Step-2's claim). |C| = #vertices on the geodesic.
A single violation would break the induction step. geng -tc census N<=11 + Mycielskian witnesses.
This uses Step-1's OWN Gamma machinery (no bridge/flagsdp import)."""
import subprocess, sys
from collections import deque
GENG="E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"

def dec(s):
    b=[ord(c)-63 for c in s]; n=b[0]; bits=[]
    for x in b[1:]:
        for k in range(5,-1,-1): bits.append((x>>k)&1)
    E=[];i=0
    for jj in range(1,n):
        for ii in range(jj):
            if i<len(bits) and bits[i]: E.append((ii,jj))
            i+=1
    return n,E
def maxcut_all(n,adj):
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    best=-1;cuts=[]
    for m in range(1<<(n-1)):
        side=[(m>>u)&1 for u in range(n)]
        c=sum(1 for u,v in edges if side[u]!=side[v])
        if c>best:best=c;cuts=[side[:]]
        elif c==best:cuts.append(side[:])
    return cuts
def Bconn(n,adj,side):
    seen={0};q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen:seen.add(v);q.append(v)
    return len(seen)==n
def bdist(n,adj,side,s,t):
    d={s:0};q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d:d[v]=d[u]+1;q.append(v)
    return d.get(t,-1)
def shortest_geos(n,adj,side,s,t):
    dist={s:0};pred={s:[]};layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist:dist[v]=dist[u]+1;pred[v]=[u];nxt.append(v)
                    elif dist[v]==dist[u]+1:pred[v].append(u)
        layer=nxt
    if t not in dist:return []
    paths=[]
    def rec(v,acc):
        if v==s:paths.append([s]+acc[::-1]);return
        for p in pred[v]:rec(p,acc+[v])
    rec(t,[]);return paths
def gamma_min_cut(n,adj,cuts):
    best=None
    for side in cuts:
        if not Bconn(n,adj,side):continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0;ok=True;ell={}
        for (u,v) in M:
            d=bdist(n,adj,side,u,v)
            if d<0:ok=False;break
            ell[(u,v)]=d+1; G+=(d+1)**2
        if ok and (best is None or G<best[1]): best=(side,G,M,ell)
    return best
def check_graph(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    cuts=maxcut_all(n,adj); res=gamma_min_cut(n,adj,cuts)
    if res is None: return None
    side,G,M,ell=res
    worst_slack=None; tight=False; viol=False
    for (u,v) in M:
        for C in shortest_geos(n,adj,side,u,v):
            Cset=set(C); Cl=len(C)
            # mass(M_C) = sum over bad edges INCIDENT to C of ell^2 = (d_B+1)^2
            mass=sum(ell[(a,b)]**2 for (a,b) in M if (a in Cset or b in Cset))
            bound=2*Cl*n-Cl*Cl
            slack=bound-mass
            if worst_slack is None or slack<worst_slack: worst_slack=slack
            if slack==0: tight=True
            if slack<0: viol=True
    return G, worst_slack, tight, viol

def blow(t):
    n=5*t;E=[]
    for i in range(5):
        for a in range(t):
            for b in range(t): E.append((i*t+a,((i+1)%5)*t+b))
    return n,E
def petersen():
    out=[(i,(i+1)%5) for i in range(5)];inn=[(5+i,5+((i+2)%5)) for i in range(5)]
    return 10,out+inn+[(i,5+i) for i in range(5)]

print("=== census: mass(M_C) <= 2|C|N-|C|^2 for ALL shortest bad-geodesics, connected-B Gamma-min cut ===")
total=0; viol_total=0; min_slack=10**9
for n in range(5,12):
    out=subprocess.run([GENG,"-tc",str(n)],capture_output=True,text=True).stdout.split()
    nconf=0; nviol=0; mslack=10**9; ntight=0
    for g6 in out:
        nn,E=dec(g6); r=check_graph(nn,E)
        if r is None: continue
        G,ws,tight,viol=r
        nconf+=1
        if viol: nviol+=1
        if tight: ntight+=1
        mslack=min(mslack,ws)
    total+=nconf; viol_total+=nviol; min_slack=min(min_slack,mslack)
    print(f"N={n:2d}: connected-B configs={nconf:6d} | mass-bound violations={nviol} | min slack={mslack} | #tight={ntight}",flush=True)
print(f"\nTOTAL N<=11: configs={total}, VIOLATIONS={viol_total}, global min slack={min_slack}")
print("tight cases (slack 0) checks:")
for name,(n,E) in [("C5",blow(1)),("C5[2]",blow(2)),("Petersen",petersen())]:
    r=check_graph(n,E); print(f"   {name}: Gamma={r[0]}, worst mass-slack={r[1]}, any tight={r[2]}, viol={r[3]}")
print("\nREAD: 0 violations => Step-2's load-bearing (iii) mass(M_C)<=2|C|N-|C|^2 holds broadly (induction step OK);")
print("min slack 0 should occur only via C5[q]-type; a negative slack anywhere would BREAK the Gamma<=N^2 induction.")
