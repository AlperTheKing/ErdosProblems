#!/usr/bin/env python3
# ADVERSARIAL REFEREE PROBE for the (Sync) strategy on Erdos #23 Step-2.
# We test the LOGICAL CHAIN, not just the target QFC25/MT25.
#
# Chain claimed:
#   25|M| > N^2  =(Sync)=>  exists (A,F): 25|F| > n_A^2
#                =(coherent-P5)=>  exists prefix S: e_M(S) > e_B(S)  => contradicts CD  => 25|M| <= N^2.
#
# CRUX: (Sync) hypothesis "25|M|>N^2" is FALSE for every triangle-free graph (it is the theorem).
# So (Sync) is vacuously true on all examples and can only be proven by a general argument.
# We measure, on REAL graphs (25|M|<=N^2), how much coherent local structure exists:
#   BEST(A,F) = max over A subset V, coherent F, of  25|F| - n_A^2.
# If even at the EXTREMAL graphs (C5[n], 25|M|=N^2) BEST is far below 0, then a "local witness whenever
# 25|M|>N^2" must rely on the global count N, i.e. (Sync) cannot be local -- a sign of circularity.

import itertools, math
import flag_engine as fe
from collections import deque

def adjset(N, A): return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]

def maxcut(N, adj):
    best=-1; bs=None
    for mask in range(1<<(N-1)):
        side=[(mask>>u)&1 for u in range(N)]
        c=sum(1 for u in range(N) for v in adj[u] if v>u and side[u]!=side[v])
        if c>best: best=c; bs=side
    return best, bs

def bfs_dist(N, adjB, src_set):
    dist={s:0 for s in src_set}; dq=deque(src_set)
    while dq:
        u=dq.popleft()
        for v in adjB[u]:
            if v not in dist: dist[v]=dist[u]+1; dq.append(v)
    return dist

def best_sync(N, adj, side):
    M=[(u,v) for u in range(N) for v in adj[u] if v>u and side[u]==side[v]]
    adjB=[set() for _ in range(N)]
    for u in range(N):
        for v in adj[u]:
            if side[u]!=side[v]: adjB[u].add(v)
    best=-10**9; bestinfo=None
    for amask in range(1, 1<<N):
        A=[u for u in range(N) if (amask>>u)&1]
        Aset=set(A)
        dist=bfs_dist(N, adjB, A)
        F=0
        for (u,v) in M:
            if u in Aset and dist.get(v,99)==4: F+=1
            elif v in Aset and dist.get(u,99)==4: F+=1
        nA=sum(1 for x in range(N) if dist.get(x,99)<=4)
        val=25*F - nA*nA
        if val>best: best=val; bestinfo=(tuple(A),F,nA)
    return best, bestinfo, len(M)

def c5n(k):
    N=5*k; A=[0]*N; part=lambda v: v//k
    for u in range(N):
        for v in range(u+1,N):
            if (part(u)-part(v))%5 in (1,4): A[u]|=1<<v; A[v]|=1<<u
    return N,A

def run_exhaustive(Ns):
    for N in Ns:
        states=fe.enumerate_graphs(N, triangle_free=True)
        cnt_pos_best=0; tot=0; max25mN2=-10**9; closest_best=-10**9; closest_info=None
        for (n,A) in states:
            adj=adjset(n,A); edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
            if not edges: continue
            mc,side=maxcut(n,adj)
            M=[(u,v) for (u,v) in edges if side[u]==side[v]]
            m=len(M)
            if m==0: continue
            tot+=1
            slack=25*m - n*n
            max25mN2=max(max25mN2, slack)
            b,info,_=best_sync(n,adj,side)
            if b>0: cnt_pos_best+=1
            if b>closest_best: closest_best=b; closest_info=(n,m,info)
        print(f"N={N}: {tot} graphs(M>0). max(25|M|-N^2)={max25mN2}. "
              f"#with coherent(A,F):25|F|>n_A^2: {cnt_pos_best}. "
              f"best 25|F|-n_A^2={closest_best} at (N,m,info)={closest_info}", flush=True)

def run_named():
    print("=== extremal / witness graphs ===", flush=True)
    for k in (1,2,3):
        N,A=c5n(k); adj=adjset(N,A); mc,side=maxcut(N,adj)
        M=[(u,v) for u in range(N) for v in adj[u] if v>u and side[u]==side[v]]
        m=len(M)
        if N<=20:
            b,info,_=best_sync(N,adj,side)
            print(f"C5[{k}]: N={N} m={m} 25m-N^2={25*m-N*N} best(25|F|-n_A^2)={b} info={info}", flush=True)

if __name__=="__main__":
    run_named()
    run_exhaustive([5,6,7,8])
