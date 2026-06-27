"""
BIASED PENTAGONAL FACET test.

The cut metric R = 1 - P (P = geodesic agreement) lives on PAIRS. The pentagonal (hypermetric)
inequality is a facet of the cut polytope; for the C5 class-metric the TIGHT facet vector is
b=(+1,-1,+1) on three CONSECUTIVE classes (Q_b=0), NOT the naive (1,1,1,-1,-1).

We want a facet of the form, for each bad edge e and the 5 'class slots' s=0..4 of its geodesic
(slot 0=u side V4? ... we use the actual geodesic vertex positions), a vertex-toll bound:

   m_phi(e)  <=  alpha * sum_{v on SOME canonical geodesic} phi(v)   ??? -- no single geodesic works
   m_phi(e)  =   MIN over geodesics, so any upper facet must use a CONVEX combination / the min itself.

The honest reformulation: GPI is a MIN-COST-FLOW / transportation duality. The pentagonal facet can only
enter as a LOWER bound on sum_v phi(v) (the RHS), giving:
   sum_v phi(v) >= (cut-metric energy of phi)   and we need  sum_e h_e m_phi(e) <= K * (that energy).

TEST the SHARPEST cut-metric lower bound the pentagonal facet yields, and whether
   sum_e h_e m_phi(e)  <=  K * Energy_pent(phi)   with  Energy_pent(phi) <= sum_v phi(v).
If Energy_pent < sum phi but still >= LHS/K everywhere, the facet is the bridge. If LHS/K can EXCEED
Energy_pent, the biased pentagonal facet is NOT strong enough (the crux).

Concretely on a graph: define, per bad edge e with geodesic vertex-set support, the 'pentagonal energy'
contribution. Lacking the general facet, we test the NECESSARY consequence the angle must satisfy:
   the dual-optimal phi* of the LP is a NONNEGATIVE combination of pentagonal-tight cut indicators.
We solve the LP, get phi*, and check whether phi* is supported as a cut-metric (0/1-valued up to scaling),
which is what the pentagonal/cut-metric story predicts for the EXTREMAL dual.
"""
import sys, numpy as np
sys.path.insert(0,'.')
from scipy.optimize import linprog
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of
from flag_engine import enumerate_graphs

def solve_dual(N,adj,side,Gam,M):
    paths=[]; pe=[]; he=[]; edge_paths=[]
    for ei,e in enumerate(M):
        geos=all_shortest_geos(N,adj,side,*e); h=len(geos[0]); he.append(h); idxs=[]
        for P in geos: idxs.append(len(paths)); paths.append(P); pe.append(ei)
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
    res=linprog(c,A_ub=Aub,b_ub=bub,A_eq=Aeq,b_eq=beq,bounds=[(0,None)]*len(paths)+[(0,None)],method="highs")
    phi=-res.ineqlin.marginals
    return res.fun, phi

N=int(sys.argv[1]) if len(sys.argv)>1 else 9
n01=0; nfrac=0; tight=0; total=0
examples_frac=[]
for nn,A in enumerate_graphs(N, triangle_free=True):
    adj=[set(j for j in range(N) if (A[i]>>j)&1) for i in range(N)]; E=edges_of(adj)
    r,mc=gamma_min_cut(N,adj,E)
    if r is None: continue
    side,Gam,M=r
    if not M: continue
    K=N+N*N-Gam; total+=1
    tau,phi=solve_dual(N,adj,side,Gam,M)
    if abs(tau-K)<1e-6 or (N*N-Gam==0 and abs(tau-N)<1e-6): tight+=1
    # is phi* a (scaled) cut? i.e. nonzero entries all equal?
    nz=phi[phi>1e-7]
    if nz.size==0: continue
    if (nz.max()-nz.min())<1e-6*max(1,nz.max()):
        n01+=1
    else:
        nfrac+=1
        if len(examples_frac)<5:
            examples_frac.append((sorted(set(round(x,4) for x in nz)), Gam, sorted(E)))
print(f"N={N}: graphs-with-bad-edges={total}; LP-tight(tau==K or ==N at deficit0)={tight}")
print(f"  dual phi* is a SCALED CUT (all nonzero equal): {n01}/{total}")
print(f"  dual phi* has MULTIPLE distinct levels (NOT a single cut): {nfrac}/{total}")
for ex in examples_frac:
    print("   frac-level example: nz-levels", ex[0], "Gamma", ex[1])
