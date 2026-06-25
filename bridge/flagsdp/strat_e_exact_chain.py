#!/usr/bin/env python3
"""STRATEGY E -- EXACT CHAIN test for Gamma <= N^2 via cycle-degree (6).

We test the candidate UPPER-bound chain (the dual of the packing proof):
Choose for each bad edge e its shortest odd cycle C_e (length ell_e). Let
   D_e := sum_{v in C_e} d(v)   (degree-mass on the cycle).
Cycle-degree ineq (6):   D_e <= N(ell_e - 1)/2.                          (*)

We want Gamma = sum_e ell_e^2 <= N^2. Strategy: find non-negative multipliers
so that summing (*) gives it.

CANDIDATE 1 (per-edge): on C5[q] every cycle is a 5-cycle with D_e=2N
(EQUALITY in (6): 2N = N*4/2). And ell_e=5. So ell_e^2 = 25 and D_e=2N=2N.
Ratio ell_e^2 / D_e = 25/(2N). Summed over q^2 edges: Gamma = 25 q^2 = N^2 and
sum D_e = 2N q^2 = 2N * N^2/25 ... = 2 N^3/25. Doesn't directly give N^2.

CANDIDATE 2 (the WINDING-AREA isoperimetric form). On C5[q] the q^2 shortest
cycles, with the load(v)=#cycles through v, satisfy load(v)=4 q^2/... let's
just measure: we want a per-VERTEX budget.  The cleanest unifier seen:
   Gamma = sum ell^2,  and  sum_e ell_e * (deg-on-cycle avg) ...

THE REAL TEST HERE: brute-force search, over ALL triangle-free graphs N<=9,
for the TIGHTEST linear combination
   Gamma  <=  alpha * (sum_e D_e)  +  beta * e(G)  +  gamma * N * (sum_e ell_e)
that holds with equality at C5[q] and stays <= N^2.  We FIT alpha,beta,gamma on
C5[1..4] and the odd cycles, then CHECK the inequality (<=N^2) on all small
triangle-free graphs. If a clean rational (alpha,beta,gamma) works -> candidate
identity found; if it fails on some graph -> that graph is the obstruction.
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
                if side[u]!=side[v]: adjB[u].add(v); adjB[v].add(u)
                else: M.append((u,v))
    return side, adjB, M


def bfs_dist(N, adjB, src):
    d=[-1]*N; d[src]=0; dq=deque([src])
    while dq:
        x=dq.popleft()
        for w in adjB[x]:
            if d[w]<0: d[w]=d[x]+1; dq.append(w)
    return d


def shortest_path(N, adjB, u, v):
    prev={u:None}; dq=deque([u])
    while dq:
        x=dq.popleft()
        if x==v: break
        for w in adjB[x]:
            if w not in prev: prev[w]=x; dq.append(w)
    path=[]; cur=v
    while cur is not None: path.append(cur); cur=prev[cur]
    return path


def feats(N, adj):
    """Return (Gamma, N^2, sumD, eG, N*sum_ell, beta) -- features for fitting."""
    side, adjB, M = cut_structure(N, adj)
    deg=[len(adj[v]) for v in range(N)]
    eG=sum(deg)//2
    ells=[]; sumD=0
    for (u,v) in M:
        d=bfs_dist(N,adjB,u); ell=d[v]+1; ells.append(ell)
        path=shortest_path(N,adjB,u,v)
        sumD+=sum(deg[w] for w in path)
    Gamma=sum(l*l for l in ells)
    return Gamma, N*N, float(sumD), float(eG), float(N*sum(ells)), len(M)


def run():
    def cycle(L):
        A=[0]*L
        for i in range(L):
            A[i]|=1<<((i+1)%L); A[(i+1)%L]|=1<<i
        return L,A
    # Fit on tight instances
    fitset=[(*c5n(1),"C5[1]"),(*c5n(2),"C5[2]"),(*c5n(3),"C5[3]"),(*c5n(4),"C5[4]"),
            (*cycle(5),"C5"),(*cycle(7),"C7"),(*cycle(9),"C9"),(*cycle(11),"C11")]
    print("=== Fit features at tight families (want combo = N^2) ===", flush=True)
    rows=[]
    for (N,A,label) in fitset:
        adj=adjset(N,A)
        G,N2,sumD,eG,Nsl,beta=feats(N,adj)
        rows.append((label,N,G,N2,sumD,eG,Nsl,beta))
        print(f"  {label:8s} N={N:2d} Gamma={G:4d} N^2={N2:4d} sumD={sumD:6.0f} "
              f"eG={eG:4.0f} N*sumEll={Nsl:6.0f} beta={beta}", flush=True)
    # Observe: at C5[q], Gamma=N^2 and N*sumEll = N*5q^2 = 5q^2*5q=25q^3 != N^2=25q^2.
    # So N*sumEll grows like N^3; not the right feature. Print ratios.
    print("\n  Look for combo that equals N^2 at ALL tight rows.", flush=True)
    print("  At C5[q]: Gamma=N^2 already. At C_odd: Gamma=N^2 already.", flush=True)
    print("  => Gamma ITSELF equals N^2 at every tight family. The task is to", flush=True)
    print("     UPPER bound Gamma by N^2 elsewhere. Measure Gamma/N^2 max on small graphs:", flush=True)

    print("\n=== Max of Gamma/N^2 over triangle-free N<=9 (connected B only) ===", flush=True)
    for N in range(5,10):
        states=fe.enumerate_graphs(N, triangle_free=True)
        worst=0.0; worst_inst=None; cnt=0
        for (n,A) in states:
            adj=adjset(n,A)
            # connected-B filter
            side,adjB,M=cut_structure(n,adj)
            if not M: continue
            # check B connected on all n vertices
            seen=[False]*n; dq=deque([0]); seen[0]=True; nc=1
            while dq:
                x=dq.popleft()
                for w in adjB[x]:
                    if not seen[w]: seen[w]=True; nc+=1; dq.append(w)
            if nc!=n: continue
            G,N2,sumD,eG,Nsl,beta=feats(n,adj)
            r=G/N2; cnt+=1
            if r>worst: worst=r; worst_inst=(n,G,N2,beta)
        print(f"  N={N}: connectedB graphs={cnt}, max Gamma/N^2={worst:.4f} at {worst_inst}", flush=True)


if __name__ == "__main__":
    run()
