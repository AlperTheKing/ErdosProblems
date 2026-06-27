#!/usr/bin/env python3
"""INDEPENDENT verification-gate reimplementation of Step-2's condition-(iii) marginal-loss reduction
(their verify_ML.py / ml_sweep.py -- MY OWN code, no flagsdp import). Cross-validates:
  (iii)  L(C) = mu(C) - Delta(C) <= 2hN - h^2   for the MIN-OVERSHOOT shortest-geodesic peel
  (A')   A(C) = sum_{f in F(C)} ell(f)        <= 2(N-h)
  (LEP)  H(C) = sum_{f in F(C)} (ell(f)^2 - h*ell(f))_+ <= Delta(C)
where h=|C|, mu = incident-bad-edge mass (ell^2), Delta = survivor distance-growth, F(C)=incident bad edges
minus the peeled edge, ov(C)=L-(2hN-h^2), min-overshoot = argmin ov. Definitions from Step-2 channel 15:40,
matched against the C5[q] anchor. Checks: tight at C5[q]; 0 fails at Gamma>=N^2; report any violation."""
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
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]; best=-1;cuts=[]
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
def bdist_restr(adj,side,s,t,banned):
    # B-distance s->t using cut edges, vertices not in banned
    if s in banned or t in banned: return -1
    d={s:0};q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if v not in banned and side[u]!=side[v] and v not in d:
                d[v]=d[u]+1; q.append(v)
    return d.get(t,-1)
def geos(adj,side,s,t):
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
    P=[]
    def rec(v,acc):
        if v==s:P.append([s]+acc[::-1]);return
        for p in pred[v]:rec(p,acc+[v])
    rec(t,[]);return P
def gmin(n,adj,cuts):
    best=None
    for side in cuts:
        if not Bconn(n,adj,side):continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M:continue
        G=0;ok=True;ell={}
        for (u,v) in M:
            d=bdist_restr(adj,side,u,v,set())
            if d<0:ok=False;break
            ell[(u,v)]=d+1;G+=(d+1)**2
        if ok and (best is None or G<best[1]):best=(side,G,M,ell)
    return best
def min_overshoot_peel(n,adj,side,M,ell):
    bestov=None;bestC=None;bestdata=None
    for (u,v) in M:
        for path in geos(adj,side,u,v):
            Cset=set(path);h=len(path);banned=Cset
            incident=[f for f in M if f[0] in Cset or f[1] in Cset]
            mu=sum(ell[f]**2 for f in incident)
            survivors=[f for f in M if f[0] not in Cset and f[1] not in Cset]
            Delta=0;valid=True
            for (a,b) in survivors:
                dd=bdist_restr(adj,side,a,b,banned)
                if dd<0: valid=False;break   # survivor disconnected -> invalid peel (skip)
                Delta+=(dd+1)**2-ell[(a,b)]**2
            if not valid: continue
            L=mu-Delta; bound=2*h*n-h*h; ov=L-bound
            if bestov is None or ov<bestov:
                bestov=ov;bestC=path
                F=[f for f in incident if f!=(u,v)]
                A=sum(ell[f] for f in F)
                H=sum(max(0,ell[f]**2-h*ell[f]) for f in F)
                bestdata=dict(h=h,mu=mu,Delta=Delta,L=L,bound=bound,ov=ov,A=A,Abound=2*(n-h),H=H)
    return bestdata
def check(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E:adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    d=min_overshoot_peel(n,adj,side,M,ell)
    if d is None: return ('nopeel',G,n)
    iii = d['L']<=d['bound']; Ap = d['A']<=d['Abound']; lep = d['H']<=d['Delta']
    tight = (d['L']==d['bound'] and d['A']==d['Abound'] and d['H']==0 and d['Delta']==0)
    return (G,n,iii,Ap,lep,tight,d)
def blow(t):
    n=5*t;E=[]
    for i in range(5):
        for a in range(t):
            for b in range(t):E.append((i*t+a,((i+1)%5)*t+b))
    return n,E
print("=== independent (iii)/(A')/(LEP) min-overshoot verification (cross-check Step-2 verify_ML.py) ===")
print("--- C5[q] equality anchor (expect TIGHT: L=bound, A=2(N-h), H=0=Delta) ---")
for q in (2,3,4):
    r=check(*blow(q)); G,n,iii,Ap,lep,tight,d=r
    print(f"  C5[{q}] N={n}: Gamma={G}=N^2? {G==n*n} | (iii){iii} (A'){Ap} (LEP){lep} | L={d['L']} bound={d['bound']} A={d['A']} Abound={d['Abound']} H={d['H']} Delta={d['Delta']} | TIGHT={tight}")
print("--- census N<=10: fails at Gamma>=N^2 (should be 0); count Gamma<N^2 fails (expected, sub-tight) ---")
for nn in range(5,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    f_ge=0; f_lt=0; ntot=0; tight_ct=0
    for g6 in out:
        n,E=dec(g6); r=check(n,E)
        if r is None or r[0]=='nopeel': continue
        G,n2,iii,Ap,lep,tight,d=r; ntot+=1
        ok=iii and Ap and lep
        if not ok:
            if G>=n2*n2: f_ge+=1
            else: f_lt+=1
        if tight: tight_ct+=1
    print(f"  N={nn}: configs={ntot} | (iii/A'/LEP) fails at Gamma>=N^2 = {f_ge} (MUST be 0) | fails at Gamma<N^2 = {f_lt} | tight(C5[q]-type)={tight_ct}",flush=True)
print("\nIf C5[q] all TIGHT and Gamma>=N^2 fails=0 across census => Step-2's verify_ML.py INDEPENDENTLY CONFIRMED.")
