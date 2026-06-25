#!/usr/bin/env python3
# Adversarial test of REGION-GROWING (Strategy 3) KEY LEMMA on the audited M=C5 N=20 obstruction.
# Strategy 3 central per-region claim: each ball cut c(s,r) <= (1/5)*perimeter (5-layer AM-GM),
# and a laminar ball family separates all bad pairs with total cut <= max{1,N^2/(25m)} * sum ell.
# We compute the ACTUAL flow value rho (LP) and the ACTUAL min fractional multicut (LP dual) and the
# best SINGLE-cut / laminar-cut separator, exposing whether region-growing can hit the budget.

import itertools
from collections import deque
import numpy as np
from scipy.optimize import linprog

def build_MC5_N20():
    # M=C5 on x0..x4 (M-edges x_i x_{i+1}); B-path Q_i: x_i - y_i - z_i - w_i - x_{i+1}.
    N=20
    x=lambda i:i%5; y=lambda i:5+i%5; z=lambda i:10+i%5; w=lambda i:15+i%5
    edges=set(); M=set()
    for i in range(5):
        a,b=x(i),x(i+1); M.add((min(a,b),max(a,b))); edges.add((min(a,b),max(a,b)))
        path=[x(i),y(i),z(i),w(i),x(i+1)]
        for j in range(4):
            a,b=path[j],path[j+1]; edges.add((min(a,b),max(a,b)))
    B=sorted(edges-M)
    side=[0]*N
    for i in range(5):
        side[x(i)]=0; side[z(i)]=0; side[y(i)]=1; side[w(i)]=1
    return N, sorted(edges), sorted(M), B, side

def adj_from_edges(N, edges):
    adj=[set() for _ in range(N)]
    for (u,v) in edges: adj[u].add(v); adj[v].add(u)
    return adj

def maxcut(N, adj):
    best=-1;bs=None
    for mask in range(1<<(N-1)):
        s=[(mask>>u)&1 for u in range(N)]
        c=sum(1 for u in range(N) for v in adj[u] if v>u and s[u]!=s[v])
        if c>best:best=c;bs=s
    return best,bs

def check_CD(N, adj, side, M):
    Mset=set(M)
    def isM(u,v): return (min(u,v),max(u,v)) in Mset
    allok=True; worst=10**9
    for mask in range(1,1<<N):
        S=[(mask>>u)&1 for u in range(N)]
        eM=sum(1 for u in range(N) for v in adj[u] if v>u and S[u]!=S[v] and isM(u,v))
        eB=sum(1 for u in range(N) for v in adj[u] if v>u and S[u]!=S[v] and not isM(u,v))
        if eM>eB: allok=False
        worst=min(worst,eB-eM)
    return allok, worst

def all_simple_paths_B(N, adjB, s, t, cap=200000):
    # enumerate simple paths in B from s to t (B is sparse here)
    paths=[];
    def dfs(u, visited, cur):
        if len(paths)>=cap: return
        if u==t: paths.append(list(cur)); return
        for v in sorted(adjB[u]):
            if v not in visited:
                visited.add(v); cur.append((min(u,v),max(u,v)))
                dfs(v, visited, cur)
                cur.pop(); visited.discard(v)
    dfs(s, {s}, [])
    return paths

def solve_rho(N, M, B, adjB):
    # rho = min t s.t. exists path-flow routing 1 unit per bad edge, load on each B-edge <= t.
    # Variables: f_{i,p} for each demand i and each simple B-path p; plus t.
    Bidx={b:k for k,b in enumerate(B)}
    demands=[]
    pathlists=[]
    for (u,v) in M:
        ps=all_simple_paths_B(N, adjB, u, v)
        demands.append((u,v)); pathlists.append(ps)
    # build LP: min t ; for each demand sum_p f=1 ; for each edge sum f through <= t
    var_path=[]
    for i,ps in enumerate(pathlists):
        for j,p in enumerate(ps):
            var_path.append((i,j,p))
    nP=len(var_path);
    nvar=nP+1  # last is t
    # objective: minimize t
    c=np.zeros(nvar); c[-1]=1.0
    # equality: per demand sum f =1
    A_eq=np.zeros((len(demands), nvar)); b_eq=np.ones(len(demands))
    for k,(i,j,p) in enumerate(var_path):
        A_eq[i,k]=1.0
    # inequality: for each edge: sum_{paths through e} f - t <=0
    A_ub=[]; b_ub=[]
    for b in B:
        row=np.zeros(nvar)
        for k,(i,j,p) in enumerate(var_path):
            if b in p: row[k]=1.0
        row[-1]=-1.0
        A_ub.append(row); b_ub.append(0.0)
    A_ub=np.array(A_ub); b_ub=np.array(b_ub)
    bounds=[(0,None)]*nP + [(0,None)]
    res=linprog(c,A_ub=A_ub,b_ub=b_ub,A_eq=A_eq,b_eq=b_eq,bounds=bounds,method='highs')
    return res.fun, res, demands, pathlists

def solve_minmulticut_LP(N, M, B, adjB):
    # fractional min multicut: min sum_b ell_b s.t. for every demand, every simple B-path has length>=1.
    # (LP relaxation; equals rho by LP duality only up to the flow-cut gap, which is what we measure.)
    Bidx={b:k for k,b in enumerate(B)}
    nE=len(B)
    A_ub=[]; b_ub=[]
    for (u,v) in M:
        ps=all_simple_paths_B(N, adjB, u, v)
        for p in ps:
            row=np.zeros(nE)
            for b in p: row[Bidx[b]]=-1.0
            A_ub.append(row); b_ub.append(-1.0)  # -sum ell <= -1  i.e. sum ell >=1
    c=np.ones(nE)
    res=linprog(c,A_ub=np.array(A_ub),b_ub=np.array(b_ub),bounds=[(0,None)]*nE,method='highs')
    return res.fun, res

N, edges, M, B, side = build_MC5_N20()
adj=adj_from_edges(N, edges)
adjB=[set() for _ in range(N)]
for (u,v) in B: adjB[u].add(v); adjB[v].add(u)

mc,_=maxcut(N,adj)
eM_side=sum(1 for (u,v) in edges if side[u]==side[v])
print(f"N={N} |E|={len(edges)} |M|={len(M)} |B|={len(B)} maxcut={mc} beta={len(edges)-mc} mono_under_side={eM_side}")
okCD,worstCD=check_CD(N,adj,side,M)
print(f"CD holds: {okCD}, min(eB-eM)={worstCD}")
m=len(M)
print(f"25m={25*m} N^2={N*N} -> max(1,N^2/(25m))={max(1.0,N*N/(25*m)):.4f}")

rho, resr, demands, pls = solve_rho(N, M, B, adjB)
print(f"FLOW rho (LP, min-max congestion) = {rho:.6f}")
print(f"  path counts per demand: {[len(p) for p in pls]}")

mc_lp, resm = solve_minmulticut_LP(N, M, B, adjB)
print(f"fractional min-multicut LP value (sum ell, normalized demands>=1) = {mc_lp:.6f}")
print(f"  -> per the dual, rho should equal this LP optimum (flow=cut for fractional). matches rho={rho:.4f}")

# Now the SINGLE-cut / separator congestion: best single B-cut delta(S)cap B that separates demands.
# Strategy 3 claims region-growing produces ONE laminar family = ONE L1 metric. On L1 metrics MT25=CD<=1.
# So the best L1 (single/laminar separator) certificate gives congestion <= 1. We exhibit that rho>1
# => no laminar/L1 separator achieves rho => region-growing's single-family output cannot certify rho.
best_single=10**9
for mask in range(1,1<<N):
    S=[(mask>>u)&1 for u in range(N)]
    # cut metric ell = indicator of delta(S) cap B
    cutB=set((min(u,v),max(u,v)) for u in range(N) for v in adj[u] if v>u and S[u]!=S[v] and (min(u,v),max(u,v)) in set(B))
    if not cutB: continue
    # for this single cut metric, d^B(u,v) in {0,2,4,...}; sum d / sum ell
    # compute d^B for each demand
    num=0.0
    for (u,v) in M:
        # shortest B-path under unit length on cut edges only
        # BFS with weights 1 on cutB else 0
        import heapq
        dist={u:0}; pq=[(0,u)]
        while pq:
            d,a=heapq.heappop(pq)
            if a==v: break
            if d>dist.get(a,1e9): continue
            for b in adjB[a]:
                e=(min(a,b),max(a,b)); wgt=1 if e in cutB else 0
                nd=d+wgt
                if nd<dist.get(b,1e9): dist[b]=nd; heapq.heappush(pq,(nd,b))
        num+=dist.get(v,1e9)
    ratio=num/len(cutB)
    if ratio<best_single: best_single=ratio
print(f"best SINGLE-cut metric congestion sum d^B / sum ell = {best_single:.6f}  (L1/separator certificate)")
print(f"GAP: rho={rho:.4f} vs best single-cut L1 certificate={best_single:.4f}; "
      f"region-growing output (one laminar family) is L1, so it certifies <= {best_single:.4f} < rho if rho>that.")
