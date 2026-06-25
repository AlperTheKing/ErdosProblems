#!/usr/bin/env python3
# THE DECISIVE TEST of the (Sync) reduction's internal consistency.
#
# The coherent-P5 lemma is: for a SINGLE coherent (A,F),  25|F| <= n_A^2  (else improving switch).
# Equivalently the lemma PROVES  25|F| <= n_A^2  for every coherent block (assuming CD holds, which it does
# at a max cut). [The "improving switch => contradiction" IS the proof that 25|F| <= n_A^2.]
#
# So the coherent-P5 lemma is a per-block bound:  for all coherent (A,F):  25|F| <= n_A^2.   (BLOCK)
#
# (Sync) wants: 25|M| > N^2 => exists coherent (A,F) with 25|F| > n_A^2.
# But (BLOCK) says NO coherent (A,F) EVER has 25|F| > n_A^2 (when CD holds).
# THEREFORE: if (Sync) were true, its conclusion (exists (A,F): 25|F|>n_A^2) DIRECTLY CONTRADICTS (BLOCK).
# The only escape: the hypothesis 25|M|>N^2 must be FALSE. i.e.
#   (Sync) + (BLOCK)  =>  25|M| <= N^2.
# This is logically fine as a proof-by-contradiction. BUT it means (Sync) can NEVER be witnessed: the (A,F)
# it promises provably does not exist by (BLOCK). So proving (Sync) cannot proceed by exhibiting (A,F);
# it must derive a contradiction from 25|M|>N^2 by OTHER means -- i.e. (Sync) is NOT a lemma about
# constructing local witnesses at all. The "local witness on budget n_A" framing is vacuous.
#
# We verify (BLOCK) directly: over all tri-free graphs (CD holds at max cut), max over coherent (A,F) of
# 25|F| - n_A^2 is <= 0 (we already saw =0 only at C5 single-edge). This shows the coherent-P5 lemma's
# conclusion is exactly the n_A=N, F=M extremal -- i.e. the block bound at the FULL graph IS the theorem,
# and there is no intermediate local regime. CONFIRMS: (Sync) is the theorem, not a reduction of it.
#
# We also test the CONVERSE worry: maybe the lemma is meant with INEQUALITY (3) q<=a_0 a_4 being the binding
# one, allowing a slack. Test whether the 5 pair-product CD inequalities (a_i a_{i+1} >= q) actually HOLD at
# a max cut for the FULL-graph layering -- if even ONE fails for the natural A, the lemma's hypothesis-set
# is itself never satisfiable, again confirming vacuity.

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
def bfs_dist(N, adjB, src):
    dist={s:0 for s in src}; dq=deque(src)
    while dq:
        u=dq.popleft()
        for v in adjB[u]:
            if v not in dist: dist[v]=dist[u]+1; dq.append(v)
    return dist

def block_check(N, adj, side):
    """For every coherent (A,F): is 25|F| <= n_A^2? Also for the FULL layering from a SINGLE source set A,
    do the 5 pair-product inequalities a_i a_{i+1} >= |F| all hold?"""
    M=[(u,v) for u in range(N) for v in adj[u] if v>u and side[u]==side[v]]
    adjB=[set() for _ in range(N)]
    for u in range(N):
        for v in adj[u]:
            if side[u]!=side[v]: adjB[u].add(v)
    max_excess=-10**9; viol_block=0; pairprod_satisfiable=0; total_A=0
    for amask in range(1,1<<N):
        A=[u for u in range(N) if (amask>>u)&1]; Aset=set(A)
        dist=bfs_dist(N,adjB,A)
        F=0
        for (u,v) in M:
            if u in Aset and dist.get(v,99)==4: F+=1
            elif v in Aset and dist.get(u,99)==4: F+=1
        if F==0: continue
        total_A+=1
        a=[sum(1 for x in range(N) if dist.get(x,99)==i) for i in range(5)]
        nA=sum(a)
        excess=25*F - nA*nA
        if excess>max_excess: max_excess=excess
        if excess>0: viol_block+=1
        # do all 5 pair-products meet/exceed F?  (a0a1)(a1a2)(a2a3)(a3a4)(a4a0)>=F each
        pairs=[a[0]*a[1],a[1]*a[2],a[2]*a[3],a[3]*a[4],a[4]*a[0]]
        if all(p>=F for p in pairs): pairprod_satisfiable+=1
    return max_excess, viol_block, total_A, pairprod_satisfiable

def run(Ns):
    for N in Ns:
        states=fe.enumerate_graphs(N, triangle_free=True)
        gmax=-10**9; gviol=0; gtotA=0; gpp=0
        for (n,A) in states:
            adj=adjset(n,A); edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
            if not edges: continue
            mc,side=maxcut(n,adj)
            if not any(side[u]==side[v] for (u,v) in edges): continue
            mx,vb,tA,pp=block_check(n,adj,side)
            gmax=max(gmax,mx); gviol+=vb; gtotA+=tA; gpp+=pp
        print(f"N={N}: over ALL coherent (A,F): max(25|F|-n_A^2)={gmax} (BLOCK violations={gviol}); "
              f"#coherent-A={gtotA}, #where all 5 pair-products>=|F| (lemma hypothesis satisfiable)={gpp}",
              flush=True)

if __name__=="__main__":
    run([5,6,7,8])
