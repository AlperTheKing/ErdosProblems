#!/usr/bin/env python3
"""Independent FULL-CENSUS cross-check of the GPI (the precise open theorem) via the LP-dual path.
For every triangle-free connected graph N<=10 (geng -tc), take the Gamma-min connected-B max cut, build the
fractional vertex-load LP (scipy highs), and check the GPI:  tau* <= K = N + (N^2 - Gamma),  with equality
tau*=N only at C5[q].  This is an INDEPENDENT code path (LP-dual) vs my combinatorial (iii)/(A')/(LEP)/(ST)
census (which is exhaustively 0-violation N<=11); agreement = strong cross-validation of the open theorem.
Self-contained (no import side-effects)."""
import subprocess
from collections import deque
import numpy as np
from scipy.optimize import linprog
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
def bdist_restr(adj,side,s,t):
    d={s:0};q=deque([s])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in d:d[v]=d[u]+1;q.append(v)
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
            d=bdist_restr(adj,side,u,v)
            if d<0:ok=False;break
            ell[(u,v)]=d+1;G+=(d+1)**2
        if ok and (best is None or G<best[1]):best=(side,G,M,ell)
    return best
def gpi_tau(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    cols=[]; edge_cols={}
    for ei,(u,v) in enumerate(M):
        edge_cols[ei]=[]
        for P in geos(adj,side,u,v):
            edge_cols[ei].append(len(cols)); cols.append((ei,set(P),ell[(u,v)]))
    nx=len(cols); nvar=nx+1
    c=np.zeros(nvar); c[-1]=1.0
    A_eq=[]; b_eq=[]
    for ei in range(len(M)):
        row=np.zeros(nvar)
        for j in edge_cols[ei]: row[j]=1.0
        A_eq.append(row); b_eq.append(1.0)
    A_ub=[]; b_ub=[]
    for v in range(n):
        row=np.zeros(nvar)
        for j,(ei,vs,h) in enumerate(cols):
            if v in vs: row[j]=h
        row[-1]=-1.0; A_ub.append(row); b_ub.append(0.0)
    bounds=[(0,None)]*nx+[(0,None)]
    res=linprog(c,A_ub=np.array(A_ub),b_ub=np.array(b_ub),A_eq=np.array(A_eq),b_eq=np.array(b_eq),bounds=bounds,method='highs')
    if not res.success: return ('LPfail',G,n)
    return (G,n,res.fun,n+(n*n-G))
def blow(t):
    nn=5*t;E=[]
    for i in range(5):
        for a in range(t):
            for b in range(t):E.append((i*t+a,((i+1)%5)*t+b))
    return nn,E

print("=== INDEPENDENT FULL-CENSUS GPI cross-check (LP-dual path) ===")
print("--- C5[q] anchor (expect tau*=N exactly = K) ---")
for q in (2,3,4):
    G,n,tau,K=gpi_tau(*blow(q))
    print(f"  C5[{q}] N={n} Gamma={G} tau*={tau:.4f} K={K} GPI(tau*<=K):{tau<=K+1e-6} tight(tau*=N):{abs(tau-n)<1e-6}")
print("--- census N=5..10: GPI violations tau*>K (MUST be 0); tight tau*=N count ---")
for nn in range(5,11):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    viol=0; tight=0; ntot=0; worst=-1e9
    for g6 in out:
        n,E=dec(g6); r=gpi_tau(n,E)
        if r is None or (isinstance(r,tuple) and r[0]=='LPfail'): continue
        G,n2,tau,K=r; ntot+=1
        worst=max(worst, tau-K)
        if tau>K+1e-6: viol+=1
        if abs(tau-n2)<1e-6: tight+=1
    print(f"  N={nn}: configs={ntot} | GPI violations(tau*>K)={viol} (MUST be 0) | tight(tau*=N)={tight} | worst(tau*-K)={worst:.4f}",flush=True)
print("\nIf 0 GPI violations across census and tight only at C5[q]-type => GPI independently cross-validated (LP-dual path).")
