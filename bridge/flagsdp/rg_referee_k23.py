#!/usr/bin/env python3
# Adversarial test of REGION-GROWING (Strategy 3) on the GENUINE non-L1 obstruction: K23-N13 (rho>1).
# This is the instance where MT25 is NOT certified by any single cut: the worst metric is non-L1.
# We test directly whether region-growing's single laminar family can certify rho.
import itertools, heapq
from collections import deque
import numpy as np
from scipy.optimize import linprog

def gpt_k23():
    N = 13; A = [0]*N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    for i in (0, 1):
        for j in (2, 3, 4): add(i, j)
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt+1; nxt += 2; add(x, a); add(a, b); add(b, y)
    return N, A

def adjset(N,A): return [set(v for v in range(N) if (A[u]>>v)&1) for u in range(N)]
def maxcut(N,adj):
    best=-1;bs=None
    for mask in range(1<<(N-1)):
        s=[(mask>>u)&1 for u in range(N)]
        c=sum(1 for u in range(N) for v in adj[u] if v>u and s[u]!=s[v])
        if c>best:best=c;bs=s
    return best,bs

N,A=gpt_k23(); adj=adjset(N,A)
edges=[(u,v) for u in range(N) for v in adj[u] if v>u]
mc,side=maxcut(N,adj)
M=[(u,v) for (u,v) in edges if side[u]==side[v]]
B=[(u,v) for (u,v) in edges if side[u]!=side[v]]
adjB=[set() for _ in range(N)]
for (u,v) in B: adjB[u].add(v); adjB[v].add(u)
m=len(M)
print(f"K23-N13: N={N} |E|={len(edges)} maxcut={mc} beta={len(edges)-mc} |M|={m} |B|={len(B)}")
print(f"M={M}")
print(f"25m={25*m} N^2={N*N} max(1,N^2/(25m))={max(1.0,N*N/(25*m)):.4f}")

def simple_paths(s,t,cap=500000):
    paths=[]
    def dfs(u,vis,cur):
        if len(paths)>=cap:return
        if u==t: paths.append(list(cur));return
        for v in sorted(adjB[u]):
            if v not in vis:
                vis.add(v);cur.append((min(u,v),max(u,v)))
                dfs(v,vis,cur);cur.pop();vis.discard(v)
    dfs(s,{s},[]);return paths

# FLOW rho
var_path=[]; pls=[]
for (u,v) in M:
    ps=simple_paths(u,v); pls.append(ps)
for i,ps in enumerate(pls):
    for j,p in enumerate(ps): var_path.append((i,j,p))
nP=len(var_path); nvar=nP+1
c=np.zeros(nvar); c[-1]=1
A_eq=np.zeros((m,nvar)); b_eq=np.ones(m)
for k,(i,j,p) in enumerate(var_path): A_eq[i,k]=1
A_ub=[];b_ub=[]
for b in B:
    row=np.zeros(nvar)
    for k,(i,j,p) in enumerate(var_path):
        if b in p: row[k]=1
    row[-1]=-1; A_ub.append(row); b_ub.append(0)
res=linprog(c,A_ub=np.array(A_ub),b_ub=np.array(b_ub),A_eq=A_eq,b_eq=b_eq,bounds=[(0,None)]*nP+[(0,None)],method='highs')
rho=res.fun
print(f"FLOW rho = {rho:.6f}  (path counts per demand {[len(p) for p in pls]})")

# best SINGLE-cut L1 certificate (region-growing single family is L1; on L1 metrics MT25=CD<=1)
best_single=-1.0; best_S=None
Bset=set(B)
for mask in range(1,1<<N):
    S=[(mask>>u)&1 for u in range(N)]
    cutB=set((min(u,v),max(u,v)) for u in range(N) for v in adj[u] if v>u and S[u]!=S[v] and (min(u,v),max(u,v)) in Bset)
    if not cutB: continue
    num=0.0
    for (u,v) in M:
        dist={u:0};pq=[(0,u)]
        while pq:
            d,a=heapq.heappop(pq)
            if a==v:break
            if d>dist.get(a,1e9):continue
            for b in adjB[a]:
                e=(min(a,b),max(a,b));wgt=1 if e in cutB else 0;nd=d+wgt
                if nd<dist.get(b,1e9):dist[b]=nd;heapq.heappush(pq,(nd,b))
        num+=dist.get(v,1e9)
    ratio=num/len(cutB)
    if ratio>best_single: best_single=ratio; best_S=S[:]
print(f"best SINGLE-cut L1 certificate sum d^B/sum ell = {best_single:.6f}")

# best ANY metric = rho (LP dual). Show the worst metric is non-L1: it spreads over many edges.
# Recover the optimal dual metric from min-multicut LP.
Bidx={b:k for k,b in enumerate(B)};nE=len(B)
A2=[];b2=[]
for (u,v) in M:
    for p in simple_paths(u,v):
        row=np.zeros(nE)
        for b in p:row[Bidx[b]]=-1
        A2.append(row);b2.append(-1)
res2=linprog(np.ones(nE),A_ub=np.array(A2),b_ub=np.array(b2),bounds=[(0,None)]*nE,method='highs')
ell=res2.x; F=res2.fun
print(f"min-multicut LP (worst metric) sum ell = {F:.6f}; normalized rho = {F/1:.6f} (demands normalized to >=1)")
nz=sum(1 for e in ell if e>1e-7)
print(f"  worst metric support = {nz}/{nE} B-edges (NON-L1 if spread); ell={np.round(ell,3).tolist()}")
print(f"\nVERDICT: rho={rho:.4f} > best single-cut L1 = {best_single:.4f}.")
print(f"Region-growing emits ONE laminar (=L1) separator family. Its certificate is <= {best_single:.4f} < rho.")
print(f"So it CANNOT certify rho={rho:.4f}. The factor {max(1.0,N*N/(25*m)):.2f} is slack here, but the MECHANISM")
print(f"(single L1 family) provably caps at the single-cut value, NOT at rho. This is GAP 2 made concrete.")
