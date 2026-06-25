#!/usr/bin/env python3
"""STRATEGY E -- the C5 TRANSFER / WINDING double-count, made exact.

GOAL: an identity   Gamma  =  <something C5/winding>  <=  N^2,  tight at C5[q]
that is NOT a self-tight certificate (it is computed from B's shortest-path
geometry, not from an LP whose optimum is Gamma).

KEY GEOMETRIC FACT (the "C5 winding" of a bad edge).  Fix the max cut, B
connected. For a bad edge e=uv with ell(e)=d_B(u,v)+1, its shortest odd cycle
C_e winds once around an odd loop; assign to each ORIENTED B-edge a "winding
1-form" omega valued in R, and to the bad edge the closing value. The point of
C5: the regular pentagon assigns to each step the angle 2pi/5, so a length-5
loop closes with total angle 2pi (winding number 1).

THE EXACT IDENTITY WE TEST (the "winding-number = 1" double count):
  For each bad edge e, define its winding contribution  w(e) = ell(e).
  Gamma = sum w(e)^2.  The claim is a CAUCHY-SCHWARZ between the bad edges and
  the VERTICES, where the pairing is the "how many bad-edge cycles pass near v".

  Define, for each bad edge e and vertex v, the indicator  chi_e(v) = 1 if v lies
  on a chosen shortest odd cycle C_e (length ell_e). Then:
     sum_e ell_e   = sum_e |C_e| - 0  =  sum_v deg_C(v)  where deg_C(v)=#cycles thru v.
  Cycle-degree ineq (6): for each cycle, sum_{v in C_e} d(v) <= N(ell_e -1)/2.
  These give the nu*<=N^2/25 LOWER bound. We want the UPPER bound on Gamma.

  The NEW idea (winding tiling): instead of one shortest cycle per bad edge,
  use the FULL B-METRIC. Define the vertex potential as the C5-EIGENVECTOR
  PAIR (cos,sin of the winding) obtained by the natural circular layout of B.
  Then test the SHARP isoperimetric identity:
     Gamma  =  sum_e ell_e^2  ?<=?  N * (sum_e ell_e)  / (avg layer multiplicity)
  Equivalent forms tested below; we hunt for the one tight at BOTH C5[q] and C_odd.
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


def gamma_struct(N, adj):
    side, adjB, M = cut_structure(N, adj)
    ells=[]
    for (u,v) in M:
        d=bfs_dist(N,adjB,u); ells.append(d[v]+1)
    return sum(l*l for l in ells), M, ells, adjB, side


# ---------------------------------------------------------------------------
# THE KEY DOUBLE COUNT. We test several "winding pairings" P(e,v) >= 0 with
#     sum_v P(e,v) = ell_e        (each bad edge's winding mass = ell_e)
# and want  sum_e P(e,v)  <=  (N/5)*? ... such that Cauchy gives Gamma<=N^2.
#
# Candidate A (uniform-on-cycle):  P(e,v)=1 if v in shortest C_e else 0; mass=ell_e.
#   Then load(v)=sum_e P(e,v); Cauchy: Gamma = sum ell_e^2 = sum_e (sum_v P)^2.
#   We need  (sum_e ell_e)^2 <= (#bad) * Gamma is wrong direction.
#   Instead use the VERTEX side: sum_v load(v) = sum_e ell_e =: S1.
#                                sum_v load(v)^2 =: Q.
#   Cauchy across bad edges with cycle-degree gives nu*. For Gamma we need the
#   dual pairing.  We just MEASURE load distribution to find the right normaliser.
# ---------------------------------------------------------------------------

def shortest_cycle(N, adjB, u, v):
    prev={u:None}; dq=deque([u])
    while dq:
        x=dq.popleft()
        if x==v: break
        for w in adjB[x]:
            if w not in prev:
                prev[w]=x; dq.append(w)
    path=[]; cur=v
    while cur is not None: path.append(cur); cur=prev[cur]
    return path  # vertices u..v (B-path); cycle = path + bad edge


def load_analysis(N, adj):
    G, M, ells, adjB, side = gamma_struct(N, adj)
    load=[0.0]*N  # how many bad-edge shortest cycles pass through v
    for (u,v) in M:
        path=shortest_cycle(N,adjB,u,v)
        for w in path: load[w]+=1.0
    S1=sum(ells)                 # = sum over v of load(v)
    Q=sum(x*x for x in load)     # sum load^2
    maxload=max(load) if load else 0
    return G, M, ells, S1, Q, maxload, load


def run():
    def cycle(L):
        A=[0]*L
        for i in range(L):
            A[i]|=1<<((i+1)%L); A[(i+1)%L]|=1<<i
        return L,A
    named=[(*c5n(1),"C5[1]"),(*c5n(2),"C5[2]"),(*c5n(3),"C5[3]"),(*c5n(4),"C5[4]"),
           (*petersen(),"Petersen"),(*gpt_k23(),"K23-N13"),(*theta46(),"theta46"),
           (*cycle(5),"C5"),(*cycle(7),"C7"),(*cycle(9),"C9")]
    print("=== Strategy E transfer/load: Gamma, S1=sum ell, Q=sum load^2, maxload ===", flush=True)
    print(f"{'name':10s} {'N':>3s} {'Gamma':>6s} {'S1':>5s} {'Q':>7s} {'maxld':>6s} "
          f"{'G/N2':>6s} {'S1/N':>6s} {'Gamma/(N*S1/?)':>10s}", flush=True)
    for (N,A,label) in named:
        adj=adjset(N,A)
        G, M, ells, S1, Q, ml, load = load_analysis(N,adj)
        # tightness probe: at C5[q], S1 = q^2*5? no: q^2 bad edges, each ell=5 ->
        # but cycles share vertices. measure.
        print(f"{label:10s} {N:>3d} {G:>6d} {S1:>5.0f} {Q:>7.1f} {ml:>6.1f} "
              f"{G/(N*N):>6.3f} {S1/N:>6.2f} {G/(N*S1/5) if S1>0 else 0:>10.3f}", flush=True)
    print("\nAt C5[q]: each bad edge cycle is a 5-cycle; check S1, load uniformity.", flush=True)


if __name__ == "__main__":
    run()
