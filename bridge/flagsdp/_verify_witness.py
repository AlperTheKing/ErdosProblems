#!/usr/bin/env python3
"""Test uniform-routing GPI claim (B) and SC claim (A) on the named witnesses:
C5[q] (q=1..4), M(Petersen) N=21, M(Grotzsch) N=23.
"""
import numpy as np
from mycielskian_check import (gamma_min_cut, all_shortest_geos, mycielskian,
                                edges_of)

def loads_uniform(N, adj, side, M):
    T = np.zeros(N)
    for (u, v) in M:
        geos = all_shortest_geos(N, adj, side, u, v)
        if not geos:
            return None
        h = len(geos[0]); w = h / len(geos)
        for P in geos:
            for x in P:
                T[x] += w
    return T

def report(name, N, adj, side=None, M=None, G=None):
    if side is None:
        E = edges_of(adj)
        res, mc = gamma_min_cut(N, adj, E)
        if res is None:
            print(name + ": no cut found"); return
        side, G, M = res
    T = loads_uniform(N, adj, side, M)
    if T is None:
        print(name + ": geodesic build failed"); return
    K = N + (N*N - G); mean = G/N
    E_unif = float((T*T).sum())
    RHS_SC = mean*mean*N + (N/(N-1))*(K-mean)**2
    mA = RHS_SC - E_unif
    mB = T.max() - K
    print("%s: N=%d beta=%d Gamma=%d N^2=%d K=%d maxT=%.4f sumT=%.2f" %
          (name, N, len(M), G, N*N, K, T.max(), T.sum()))
    print("    (A) SC margin RHS_SC-E_unif = %.5f  %s" % (mA, "OK" if mA>=-1e-6 else "FAIL"))
    print("    (B) GPI margin maxT-K       = %.5f  %s" % (mB, "OK" if mB<=1e-6 else "FAIL"))

def C5q(q):
    N = 5*q
    part = [v//q for v in range(N)]
    adj = [set() for _ in range(N)]
    for u in range(N):
        for v in range(N):
            if u != v and (part[u]-part[v]) % 5 in (1, 4):
                adj[u].add(v)
    E = edges_of(adj)
    res, mc = gamma_min_cut(N, adj, E, cap=2000000)
    return N, adj, res

for q in range(1, 5):
    N, adj, res = C5q(q)
    if res is None:
        print("C5[%d]: no cut" % q); continue
    side, G, M = res
    report("C5[%d]" % q, N, adj, side, M, G)

pet_adj = [set() for _ in range(10)]
for i in range(5):
    for (a, b) in [(i, (i+1) % 5), (5+i, 5+(i+2) % 5), (i, 5+i)]:
        pet_adj[a].add(b); pet_adj[b].add(a)
Np, ap = mycielskian(10, edges_of(pet_adj))
report("M(Petersen)", Np, ap)

C5e = [(i, (i+1) % 5) for i in range(5)]
gN, ga = mycielskian(5, C5e)
gN2, ga2 = mycielskian(11, edges_of(ga))
report("M(Grotzsch)", gN2, ga2)
