#!/usr/bin/env python3
"""Analyze the N=11 mass-bound overshoots: for each connected-B config where SOME shortest bad-geodesic C
has mass(M_C) > 2|C|N-|C|^2, check whether a SAFE geodesic EXISTS (some C with mass(M_C) <= bound).
If a safe peel exists everywhere, Step-2's induction survives (choose the safe peel). If some config has
ALL geodesics overshooting, that is a genuine no-safe-peel obstruction = a real gap in (iii)."""
import subprocess
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
def analyze(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    res=gamma_min_cut(n,adj,maxcut_all(n,adj))
    if res is None: return None
    side,G,M,ell=res
    slacks=[]
    for (u,v) in M:
        for C in shortest_geos(n,adj,side,u,v):
            Cset=set(C);Cl=len(C)
            mass=sum(ell[(a,b)]**2 for (a,b) in M if (a in Cset or b in Cset))
            slacks.append(2*Cl*n-Cl*Cl-mass)
    if not slacks: return None
    return G, min(slacks), max(slacks), len([s for s in slacks if s<0]), len(slacks)

n=11
out=subprocess.run([GENG,"-tc",str(n)],capture_output=True,text=True).stdout.split()
overshoot=[]
for g6 in out:
    nn,E=dec(g6); r=analyze(nn,E)
    if r is None: continue
    G,mn,mx,nneg,ntot=r
    if mn<0:
        overshoot.append((g6,G,mn,mx,nneg,ntot))
print(f"N=11: {len(overshoot)} configs with >=1 overshooting geodesic (mass>bound). For each, does a SAFE geodesic exist (max slack>=0)?")
allsafe=0; nosafe=0
for g6,G,mn,mx,nneg,ntot in overshoot:
    safe = mx>=0
    allsafe += safe; nosafe += (not safe)
    print(f"  g6={g6} Gamma={G} | worst slack={mn} best slack={mx} | overshoot geodesics={nneg}/{ntot} | SAFE PEEL EXISTS={safe}")
print(f"\nSUMMARY: {len(overshoot)} overshoot configs; SAFE peel exists in {allsafe}; NO safe peel in {nosafe}.")
print("If nosafe=0 => every overshoot config still has a safe shortest-geodesic peel => Step-2 induction survives")
print("(the bound holds for the CHOSEN safe peel; overshoot is only on non-chosen geodesics).")
print("If nosafe>0 => GENUINE no-safe-peel obstruction at N=11 => (iii) needs the D*/master mechanism, not just shortest-geodesic mass.")
