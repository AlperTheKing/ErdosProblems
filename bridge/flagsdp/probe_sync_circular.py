#!/usr/bin/env python3
# Pin down the circularity: at the extremal C5[n], (Sync) is realized ONLY by A,F with n_A=N, F=M.
# So (Sync) with n_A<N (a STRICTLY LOCAL witness) is what would give slack. Test: does ANY graph admit a
# coherent (A,F) with n_A < N AND 25|F| close to n_A^2 (the "local concentration" (Sync) promises)?
#
# Critically: the coherent-P5 lemma applied to (A,F) yields a switch S (a prefix) with e_M(S)>e_B(S)
# ONLY IF 25|F| > n_A^2. We test whether on REAL graphs the BEST coherent ratio 25|F|/n_A^2 ever EXCEEDS
# 1 for n_A<N -- if it never does, then (Sync) for the relevant n_A<N regime has NO witness and the
# reduction "25|M|>N^2 => local 25|F|>n_A^2" has no mechanism beyond re-deriving the global bound.

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

def best_ratio(N, adj, side):
    M=[(u,v) for u in range(N) for v in adj[u] if v>u and side[u]==side[v]]
    adjB=[set() for _ in range(N)]
    for u in range(N):
        for v in adj[u]:
            if side[u]!=side[v]: adjB[u].add(v)
    best_local=-1.0; loc_info=None       # best 25|F|/n_A^2 over A with n_A < N
    best_any=-1.0; any_info=None
    for amask in range(1, 1<<N):
        A=[u for u in range(N) if (amask>>u)&1]
        Aset=set(A)
        dist=bfs_dist(N, adjB, A)
        F=0
        for (u,v) in M:
            if u in Aset and dist.get(v,99)==4: F+=1
            elif v in Aset and dist.get(u,99)==4: F+=1
        nA=sum(1 for x in range(N) if dist.get(x,99)<=4)
        if nA==0: continue
        r=25.0*F/(nA*nA)
        if r>best_any: best_any=r; any_info=(tuple(A),F,nA)
        if nA<N and r>best_local: best_local=r; loc_info=(tuple(A),F,nA)
    return best_local, loc_info, best_any, any_info, len(M)

def run(Ns):
    for N in Ns:
        states=fe.enumerate_graphs(N, triangle_free=True)
        worst_local=-1.0; wl_info=None; worst_any=-1.0; wa_info=None; n_local_exceed=0; tot=0
        for (n,A) in states:
            adj=adjset(n,A); edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
            if not edges: continue
            mc,side=maxcut(n,adj)
            M=[(u,v) for (u,v) in edges if side[u]==side[v]]
            if not M: continue
            tot+=1
            bl,li,ba,ai,m=best_ratio(n,adj,side)
            if bl>worst_local: worst_local=bl; wl_info=(n,m,li)
            if ba>worst_any: worst_any=ba; wa_info=(n,m,ai)
            if bl>1.0+1e-9: n_local_exceed+=1
        print(f"N={N}: {tot} graphs. max 25|F|/n_A^2 over n_A<N: {worst_local:.4f} (#>1: {n_local_exceed}) "
              f"at {wl_info}; max over ALL A: {worst_any:.4f} at {wa_info}", flush=True)

if __name__=="__main__":
    run([5,6,7,8])
