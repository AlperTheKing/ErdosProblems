#!/usr/bin/env python3
"""STRATEGY E -- the decisive form: WINDING-INTERVAL PARTITION of the vertex set.

UNIFYING the two tight families.
  C5[q]:  q^2 bad edges, each ell=5, N=5q, Gamma=N^2.   (many short windings)
  C_odd:  1 bad edge, ell=N, Gamma=N^2.                 (one long winding)
The common structure: Gamma = N^2 means the bad edges' windings, of total
"length" measured correctly, EXACTLY fill a budget of N^2.

CLAIM TO TEST (the Cauchy-Schwarz / winding-partition identity):
  There is an assignment of a NON-NEGATIVE WEIGHT g_e to each bad edge with
     (i)  sum_e g_e  =  N          (the windings partition the vertex budget)
     (ii) g_e  >=  ell_e^2 / N      ... no; rather
  the SHARP statement that unifies both is:
     Gamma = sum_e ell_e^2  <=  N * max_e ell_e   ??  (false: C5[q] gives N*5 < N^2)
  so NOT a single max. The right one is a CAUCHY between {ell_e} and a
  PARTITION {n_e} of N with ell_e <= n_e:
     Gamma = sum ell_e^2 <= sum ell_e * n_e <= (max ell/n ratio) ...

TEST: is there a fractional assignment of vertices to bad edges, x_{e,v}>=0,
  with  sum_e x_{e,v} <= 1  (each vertex used <= once)  and
        sum_v x_{e,v} = ell_e  (each bad edge gets ell_e vertices)
  i.e. a fractional ell_e-matching of bad edges to vertices?  If YES then
        sum_e ell_e <= N   (count vertices)   -- LINEAR, too weak.
For the QUADRATIC Gamma we need each bad edge to claim ell_e vertices in a way
that the claimed sets are "spread" so that Cauchy gives the square.

THE ACTUAL WORKING IDENTITY (cycle-degree dual). The proved nu*<=N^2/25 uses:
   for shortest odd cycle C (len L):  sum_{v in C} d(v) <= N(L-1)/2.   (6)
Equivalently each cycle's vertices carry total degree <= N(L-1)/2, i.e. the
average degree on the cycle is <= N(L-1)/(2L) < N/2. The C5-blowup saturates
this. We now build the GAMMA UPPER bound as the EXACT DUAL of (6):

  Assign to bad edge e the "degree-mass"  D_e = sum_{v in C_e} d(v).
  Cycle-degree (6):  D_e <= N(ell_e-1)/2.
  Double count of degree:  sum_e (mult) ... we test  sum_e D_e  and relate to
  edges e(G), then to N^2 via handshake sum d = 2e.

This file MEASURES D_e, sum_e D_e, sum d(v)=2e, and the ratio that would give
Gamma<=N^2, to pin the exact constant chain.
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
            if w not in prev:
                prev[w]=x; dq.append(w)
    path=[]; cur=v
    while cur is not None: path.append(cur); cur=prev[cur]
    return path


def analysis(N, adj):
    side, adjB, M = cut_structure(N, adj)
    deg=[len(adj[v]) for v in range(N)]
    twoE=sum(deg)
    ells=[]; Ds=[]
    for (u,v) in M:
        d=bfs_dist(N,adjB,u); ell=d[v]+1; ells.append(ell)
        path=shortest_path(N,adjB,u,v)
        Ds.append(sum(deg[w] for w in path))
    Gamma=sum(l*l for l in ells)
    sumD=sum(Ds)
    # cycle-degree bound RHS per edge:
    sumRHS=sum(N*(l-1)/2 for l in ells)
    return Gamma, ells, Ds, sumD, sumRHS, twoE, M


def run():
    def cycle(L):
        A=[0]*L
        for i in range(L):
            A[i]|=1<<((i+1)%L); A[(i+1)%L]|=1<<i
        return L,A
    named=[(*c5n(1),"C5[1]"),(*c5n(2),"C5[2]"),(*c5n(3),"C5[3]"),(*c5n(4),"C5[4]"),
           (*petersen(),"Petersen"),(*gpt_k23(),"K23-N13"),(*theta46(),"theta46"),
           (*cycle(5),"C5"),(*cycle(7),"C7"),(*cycle(9),"C9")]
    print("=== Strategy E winding-partition / cycle-degree dual ===", flush=True)
    print(f"{'name':10s} {'N':>3s} {'Gamma':>6s} {'sumD':>5s} {'sumRHS':>7s} {'2E':>4s} "
          f"{'G/N2':>6s} {'sumD/2E':>7s}", flush=True)
    for (N,A,label) in named:
        adj=adjset(N,A)
        Gamma, ells, Ds, sumD, sumRHS, twoE, M = analysis(N,adj)
        print(f"{label:10s} {N:>3d} {Gamma:>6d} {sumD:>5.0f} {sumRHS:>7.1f} {twoE:>4d} "
              f"{Gamma/(N*N):>6.3f} {sumD/twoE if twoE else 0:>7.3f}", flush=True)


if __name__ == "__main__":
    run()
