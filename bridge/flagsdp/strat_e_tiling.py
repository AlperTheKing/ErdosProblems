#!/usr/bin/env python3
"""STRATEGY E -- the WINDING-TILING double count (the real candidate identity).

DISCOVERY from strat_e_winding.py: on C5[q], for EVERY bad edge the shortest
B-path has length 4 (ell=5) and these q^2 paths, together with the bad edges,
TILE the graph as q^2 disjoint... no -- they overlap, but the B-EDGE TOTAL
satisfies sum_{uv in M}(ell-1) = eB exactly (each B-edge carries total path-load
matching its capacity). That is the LINEAR coarea equality. Gamma is the
QUADRATIC refinement.

THE IDENTITY WE WANT (C5 double count). Consider the bipartite B-graph and a
"winding height" h: V -> Z/5 such that:
  - every B-edge changes h by +-1 (mod 5)   [exists iff G->C5 hom-like layering]
  - every bad edge uv has h_u = h_v + 0?  -> on C5[q], bad edge connects same
    class, so SAME C5-vertex; its odd cycle winds once around Z/5.

We test a SHARPER, signature-free quadratic bound built directly from
CUT-DOMINATION (CD) + the shortest-path STRUCTURE, NOT from an LP/SDP:

  CD shell inequality.  Fix a bad edge e0=u0v0 with length ell0. Root B-BFS at
  u0; let A_i = {w : d_B(u0,w)=i} be the shells. The cut delta_B(union_{j<=i} A_j)
  >= delta_M(...) by CD. We measure the per-bad-edge "winding area"
        area(e) = sum over its shortest cycle C_e of (shell crossings)
  and test  Gamma = sum ell^2  ==  2 * (total directed area swept)  <= N^2  by
  an isoperimetric (Loomis-Whitney style) inequality on the cut function.

CONCRETELY, the candidate is the LAYER-AREA identity:
  For the connected B-graph, define f_i = |{v : d_B(u0,v)=i}| (layer sizes from a
  root). Then sum_i f_i = N and (cycle of length ell uses 2 vertices per layer up
  to layer (ell-1)/2). The product f_i f_{i+1} >= q (CD) gives, via AM-GM, the
  single-block 25q <= N^2. We test the GLOBAL winding-area version:

      Gamma  <=  ( sum_i sqrt(f_i f_{i+1}) )^2   <=  ... <= N^2 ?

We compute both sides on all instances to see if the middle quantity
S2 := (sum_i sqrt(f_i f_{i+1}))^2 sits between Gamma and N^2 with equality at C5[q].
"""
import math
import numpy as np
from collections import deque
from strat_e_probe import adjset, maxcut, petersen, c5n, gpt_k23, theta46
import flag_engine as fe


def cut_structure(N, adj):
    mc, side = maxcut(N, adj)
    adjB=[set() for _ in range(N)]; M=[]
    for u in range(N):
        for v in adj[u]:
            if v>u:
                if side[u]!=side[v]:
                    adjB[u].add(v); adjB[v].add(u)
                else:
                    M.append((u,v))
    return side, adjB, M


def bfs_dist(N, adjB, src):
    d=[-1]*N; d[src]=0; dq=deque([src])
    while dq:
        x=dq.popleft()
        for w in adjB[x]:
            if d[w]<0:
                d[w]=d[x]+1; dq.append(w)
    return d


def gamma_struct(N, adj):
    side, adjB, M = cut_structure(N, adj)
    ells=[]
    for (u,v) in M:
        d=bfs_dist(N,adjB,u); ells.append(d[v]+1)
    return sum(l*l for l in ells), M, ells, adjB, side


def b_components(N, adjB):
    seen=[False]*N; comps=[]
    for s in range(N):
        # only include vertices that touch B; isolated-in-B singletons still a comp
        if not seen[s]:
            comp=[]; dq=deque([s]); seen[s]=True
            while dq:
                x=dq.popleft(); comp.append(x)
                for w in adjB[x]:
                    if not seen[w]:
                        seen[w]=True; dq.append(w)
            comps.append(comp)
    return comps


def winding_area_candidate(N, adj):
    """For each B-component, root BFS at the endpoint of the longest bad edge;
    compute layer sizes f_i and the AM-GM-style middle quantity. Aggregate over
    components and compare to Gamma and N^2."""
    G, M, ells, adjB, side = gamma_struct(N, adj)
    comps = b_components(N, adjB)
    # map vertex -> comp index
    cidx={}
    for i,c in enumerate(comps):
        for v in c: cidx[v]=i
    total_mid = 0.0
    per_comp=[]
    for ci, comp in enumerate(comps):
        compset=set(comp)
        # bad edges in this comp
        badc=[(u,v) for (u,v) in M if u in compset]
        if not badc:
            per_comp.append((len(comp),0,0.0)); continue
        # root at endpoint of a longest bad edge
        best=None
        for (u,v) in badc:
            d=bfs_dist(N,adjB,u)
            if best is None or d[v]>best[2]:
                best=(u,v,d[v])
        root=best[0]
        d=bfs_dist(N,adjB,root)
        maxlayer=max(d[w] for w in comp if d[w]>=0)
        f=[0]*(maxlayer+1)
        for w in comp:
            if d[w]>=0: f[d[w]]+=1
        # middle quantity: (sum_i sqrt(f_i f_{i+1}))^2  -- the "winding circumference"
        s=sum(math.sqrt(f[i]*f[i+1]) for i in range(maxlayer))
        mid=s*s
        total_mid+=mid
        per_comp.append((len(comp), sum(l*l for (u,v) in badc for l in [bfs_dist(N,adjB,u)[v]+1]), mid))
    return G, total_mid, per_comp


def run():
    def cycle(L):
        A=[0]*L
        for i in range(L):
            A[i]|=1<<((i+1)%L); A[(i+1)%L]|=1<<i
        return L,A
    named=[(*c5n(1),"C5[1]"),(*c5n(2),"C5[2]"),(*c5n(3),"C5[3]"),(*c5n(4),"C5[4]"),
           (*petersen(),"Petersen"),(*gpt_k23(),"K23-N13"),(*theta46(),"theta46"),
           (*cycle(5),"C5"),(*cycle(7),"C7"),(*cycle(9),"C9"),(*cycle(11),"C11")]
    print("=== Strategy E winding-tiling: Gamma <= S2 <= N^2 candidate ===", flush=True)
    print(f"{'name':10s} {'N':>3s} {'Gamma':>6s} {'S2(mid)':>9s} {'N^2':>5s}  "
          f"{'G<=S2':>6s} {'S2<=N2':>7s}", flush=True)
    for (N,A,label) in named:
        adj=adjset(N,A)
        G, S2, per = winding_area_candidate(N,adj)
        ok1 = "OK" if G<=S2+1e-6 else "FAIL"
        ok2 = "OK" if S2<=N*N+1e-6 else "FAIL"
        print(f"{label:10s} {N:>3d} {G:>6d} {S2:>9.3f} {N*N:>5d}  {ok1:>6s} {ok2:>7s}", flush=True)


if __name__ == "__main__":
    run()
