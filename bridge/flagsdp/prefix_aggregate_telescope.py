#!/usr/bin/env python3
"""Does the prefix-transport lemma AGGREGATE to a per-vertex congestion bound?

The prefix-defect transport lemma (PROVED, local per peel C of bad edge e, per CD-obstruction S):
    e^sig(C\P_i, S) + e^sig(P_i, R\S) >= eta(S)        for 0<=i<h-1,  P_i = {v_0..v_i}.
where e^sig(A,D)=e_B(A,D)-e_M(A,D), R=V\C, eta(S)=delta_M[R](S)-delta_B[R](S).

The vertex-load theorem wants: for the (uniform or LP) routing, T(v) <= N + (N^2-Gamma).

AGGREGATION ATTEMPT under test.  Fix a vertex v.  T(v) = sum_{e,P : v in P} h_e x_{e,P}.
For each geodesic P=v_0..v_{h-1} through v, v=v_j for some position j; the prefix P_{j-1} ends
just before v.  The transport lemma at prefix i=j-1 bounds a *signed boundary* crossing.  The hope:
SUM over all (e,P) routed and the position of v of the transport inequality, weighted by h_e x_{e,P},
recovers an upper bound on T(v) because the signed boundary terms telescope to a bounded quantity
(<= N-ish) while the eta terms are absorbed by the deficit budget N^2-Gamma.

What we MEASURE per graph (LP routing), to see whether the telescope closes:
  For each vertex v, and the WHOLE-V obstruction is not allowed (R excludes C). We instead pick,
  per bad edge e, its max-obstruction S_e (as in prefix_transport_verify). Then we form the
  aggregated lower bound
       LB(v) := sum_{e,P routed, v in P at pos j} h_e x_{e,P} * [ transport_{e}(j-1) ]
  and the aggregated eta-budget
       EB    := sum_e ( max_P x_{e,P} ... )  -- the total eta mass.
  We compare the realized T(v) to  Gamma/N + (signed-boundary slack).  KEY DIAGNOSTIC: compute,
  for each v, the quantity
       Q(v) := sum_{e,P routed: v in P} h_e x_{e,P} * sig_into_v
  where sig_into_v = (e_B - e_M) from the rest of the graph into v along the routing, and test
  whether sum_v of the POSITIVE part of (T(v)-avg) is controlled by the total deficit (N^2-Gamma).

  Concretely we test the candidate AGGREGATE MASTER INEQUALITY:
       sum_v max(0, T(v) - N)   <=   N^2 - Gamma        (call it AMI)
  This is IMPLIED by the vertex-load theorem (each term <= N^2-Gamma and ... actually it's weaker:
  if every T(v)<=N+(N^2-Gamma) AND sum T(v)=Gamma, then sum_v max(0,T(v)-N) <= sum_v(T(v)) ... ).
  AMI is the natural target of an aggregation: 'total overload above the average-cap N is paid for
  by the total deficit.'  If AMI holds on the census it is a genuine weaker-but-useful congestion
  inequality (the partial bridge). If it FAILS, that pinpoints the non-cancellation.
"""
import sys, numpy as np
from scipy.optimize import linprog
import flag_engine as FE
from mycielskian_check import edges_of, gamma_min_cut, all_shortest_geos

def to_setadj(n, A):
    return [set(j for j in range(n) if (A[i]>>j)&1) for i in range(n)]

def build(n, adj):
    E = edges_of(adj)
    res, mc = gamma_min_cut(n, adj, E)
    if res is None: return None
    return res  # side,G,M

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
    return res.fun, Tv

def uniform_routing(N, adj, side, G, M):
    """uniform split over shortest geos -> vertex load Tv."""
    Tv=np.zeros(N)
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None
        h=len(geos[0]); w=h/len(geos)
        for P in geos:
            for x in P: Tv[x]+=h*(1.0/len(geos))
    return Tv

def main():
    Nmax = int(sys.argv[1]) if len(sys.argv)>1 else 10
    nchk=0
    worst_lp=( -1e9,None); worst_unif=(-1e9,None)
    for N in range(5, Nmax+1):
        for (nn, A) in FE.enumerate_graphs(N, triangle_free=True):
            adj = to_setadj(N, A)
            b = build(N, adj)
            if b is None: continue
            side,G,M = b
            if not M: continue
            deficit = N*N - G
            # LP routing AMI
            r = lp_routing(N, adj, side, G, M)
            if r is not None:
                tau, Tv = r
                ami_lp = np.maximum(0.0, Tv - N).sum()
                slack = deficit - ami_lp
                if -slack > worst_lp[0]:
                    worst_lp = (-slack, (N,G,deficit,round(ami_lp,4),round(Tv.max(),4)))
            # uniform routing AMI
            Tu = uniform_routing(N, adj, side, G, M)
            if Tu is not None:
                ami_u = np.maximum(0.0, Tu - N).sum()
                slack_u = deficit - ami_u
                if -slack_u > worst_unif[0]:
                    worst_unif = (-slack_u, (N,G,deficit,round(ami_u,4),round(Tu.max(),4)))
            nchk+=1
    print(f"census N<={Nmax}: graphs checked={nchk}")
    print(f"  AMI (LP routing):      worst (deficit - sum max(0,T-N))  most-negative = {-worst_lp[0]:.4f}")
    print(f"     witness (N,Gamma,deficit,AMI,maxT) = {worst_lp[1]}   [AMI holds iff >=0]")
    print(f"  AMI (uniform routing): worst (deficit - sum max(0,T-N))  most-negative = {-worst_unif[0]:.4f}")
    print(f"     witness (N,Gamma,deficit,AMI,maxT) = {worst_unif[1]}   [AMI holds iff >=0]")

if __name__=="__main__":
    main()
