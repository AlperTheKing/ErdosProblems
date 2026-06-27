#!/usr/bin/env python3
"""PREFIX-AGGREGATE angle for the GPI.

Goal: take the LOCAL per-peel prefix-defect transport lemma and try to SUM it over a
fractional routing to obtain the GLOBAL vertex-load bound T_x(v) <= N + (N^2 - Gamma).

We do NOT try to prove anything here; we test, on the triangle-free census, the exact
identities that an aggregation argument would need, and locate where they break.

Background facts re-derived numerically:
  - For a bad edge e=uv, h_e = d_B(u,v)+1 = |P| for any shortest B-geodesic P (odd cycle e+P).
  - sum_e h_e^2 = Gamma.
  - The GPI primal: exists routing x_{e,P}>=0, sum_P x_{e,P}=1, with vertex load
        T_x(v) = sum_{e,P: v in P} h_e x_{e,P} <= N + (N^2 - Gamma).
  - sum_v T_x(v) = sum_e h_e * |P_e under x| = sum_e h_e * h_e = Gamma  (every shortest geo has h_e
        vertices, regardless of which one is chosen). So sum_v T_x(v) = Gamma EXACTLY for ANY routing.

CONSEQUENCE (the "free" half of aggregation): since sum_v T_x(v) = Gamma <= N^2 (if we already
knew Gamma<=N^2), the AVERAGE vertex load is Gamma/N <= N. The vertex-load THEOREM asks for the
MAX load <= N + (N^2-Gamma) = N + N*(N - Gamma/N). I.e. max load minus average load
        max_v T_x(v) - Gamma/N  <=  N + N^2 - Gamma - Gamma/N.
The whole difficulty is the SPREAD of the load, not its sum.  We probe the spread.

Tests per census graph (with its min-Gamma max-cut):
  (A) sum_v T_x(v) == Gamma  for the LP-opt routing  (sanity; must hold for any routing).
  (B) the LP optimum tau* and whether tau* <= N + (N^2-Gamma).
  (C) the PREFIX-AGGREGATE quantity: define for the LP routing and each vertex v the
      'prefix-charge' that the transport lemma would assign, and see whether summing the
      transport inequalities reproduces a per-vertex bound. Concretely we test the candidate
      master inequality the angle hopes for:
        for every v,   T_x(v) <= avg + (N^2 - Gamma) * (something <=1)
      by measuring excess(v) = T_x(v) - Gamma/N and the budget N^2 - Gamma.
"""
import sys, numpy as np
from scipy.optimize import linprog
from itertools import combinations
import flag_engine as FE
from mycielskian_check import edges_of, gamma_min_cut, all_shortest_geos

def to_setadj(n, A):
    return [set(j for j in range(n) if (A[i]>>j)&1) for i in range(n)]

def build(n, adj):
    E = edges_of(adj)
    res, mc = gamma_min_cut(n, adj, E)
    if res is None: return None
    side, G, M = res
    return side, G, M

def lp_routing(N, adj, side, G, M):
    paths=[]; pe=[]; he=[]; edge_paths=[]
    for ei,(u,v) in enumerate(M):
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None
        h=len(geos[0]); he.append(h); idxs=[]
        for P in geos:
            idxs.append(len(paths)); paths.append(P); pe.append(ei)
        edge_paths.append(idxs)
    nvar=len(paths)+1; tau=len(paths)
    c=np.zeros(nvar); c[tau]=1.0
    Aeq=np.zeros((len(M),nvar)); beq=np.ones(len(M))
    for ei,idxs in enumerate(edge_paths):
        for k in idxs: Aeq[ei,k]=1.0
    Aub=np.zeros((N,nvar)); bub=np.zeros(N)
    for k,P in enumerate(paths):
        w=he[pe[k]]
        for v in P: Aub[v,k]+=w
    for v in range(N): Aub[v,tau]=-1.0
    res=linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq,
                bounds=[(0,None)]*len(paths)+[(0,None)], method="highs")
    if not res.success: return None
    x=res.x[:len(paths)]
    Tv=Aub[:,:len(paths)].dot(x)
    return res.fun, Tv, paths, pe, he, x

def main():
    Nmax = int(sys.argv[1]) if len(sys.argv)>1 else 10
    worst_gap = -1e9; worst=None
    nchk=0; viol=0
    # also track the SPREAD relation: max_v T - Gamma/N  vs  N + N^2 - Gamma - Gamma/N
    max_spread_ratio = -1e9
    for N in range(5, Nmax+1):
        for (nn, A) in FE.enumerate_graphs(N, triangle_free=True):
            adj = to_setadj(N, A)
            b = build(N, adj)
            if b is None: continue
            side,G,M = b
            if not M: continue
            r = lp_routing(N, adj, side, G, M)
            if r is None: continue
            tau, Tv, paths, pe, he, x = r
            nchk += 1
            K = N + (N*N - G)
            # (A) sum_v Tv == Gamma
            assert abs(Tv.sum() - G) < 1e-6, (Tv.sum(), G)
            # (B) tau <= K
            if tau > K + 1e-6: viol += 1
            gap = K - tau
            if gap < worst_gap or worst is None:
                pass
            # spread relation
            avg = G/N
            lhs = Tv.max() - avg
            rhs = N + N*N - G - avg
            if rhs > 1e-12:
                ratio = lhs/rhs
                if ratio > max_spread_ratio:
                    max_spread_ratio = ratio; worst=(N,G,tau,K,Tv.max())
    print(f"census N<=  {Nmax}: graphs-with-bad-edges checked = {nchk}, tau*>K violations = {viol}")
    print(f"  max spread ratio  (max_v T - Gamma/N)/(N + N^2 - Gamma - Gamma/N) = {max_spread_ratio:.6f}")
    print(f"  worst-spread witness (N,Gamma,tau*,K,maxT) = {worst}")

if __name__=="__main__":
    main()
