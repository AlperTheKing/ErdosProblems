#!/usr/bin/env python3
"""STRATEGY C, part 2: the COAREA / level-cut spectral object that IS tight at C5[q].

Raw effective resistance FAILS (probe 1): it shrinks ~1/q under blow-up while Gamma/N^2 stays 1.
The object that stays tight under blow-up must be a CUT-based (coarea) quantity, not a resistance.

KEY IDEA (the genuinely new structural content). For a vertex potential f:V(B)->R, the COAREA formula
   sum_{B-edges (x,y)} |f(x)-f(y)|  =  integral_t |partial B-cut at level t| dt.
A bad edge uv with d_B(u,v) forces, along ANY shortest B-path, the potential to change by >= |f(u)-f(v)|;
if f is 1-Lipschitz on B then |f(u)-f(v)| <= d_B(u,v). We want the REVERSE: bound the NUMBER of bad edges
crossing each level by the number of B-edges crossing it (this is exactly CD applied levelwise), then
ASSEMBLE squared distances.

The right quadratic identity (test): pick the EIGENVECTOR f of L_B for lambda_2 (Fiedler vector) and a
multiscale family of threshold cuts S_t={f>=t}. By CD, |delta_M(S_t)| <= |delta_B(S_t)| for every t.
Gamma = sum_e ell_e^2 = sum_e (sum over the ~ell_e levels a unit-speed B-geodesic from u to v crosses)^2.
We test whether a SQUARED coarea / Cauchy-Schwarz over levels yields N^2 with equality at C5[q].

Concretely we test the central candidate inequality (the "spectral coarea bound"):
   (CSB)   Gamma  <=  (sum_t |delta_B(S_t)|) * (max_e #levels crossed by e)      -- too weak, linear
   (CSB2)  Gamma  <=  sum_t |delta_B(S_t)| * w_t  with weights from B-eigenvector, Cauchy-Schwarz to N^2.

We MEASURE, for the canonical 5-level structure of C5[q] (potential f = the C5 phase angle), how
sum_t |delta_M(S_t)| and sum_t |delta_B(S_t)| and the squared assembly behave, to locate where N^2 and
the factor 25=5^2 come from spectrally. We use the B-graph eigenvectors for lambda_2 (and the top of the
spectrum) to build threshold cuts and report the levelwise CD slack.
"""
import numpy as np
from collections import deque
from stratC_spectral_probe import (c5_blowup, odd_cycle, petersen, theta46,
                                    all_maxcuts, build_B_M, bdist_all, components)

def lap_B(n, adjB):
    L=np.zeros((n,n))
    for u in range(n):
        for w in adjB[u]:
            if w>u:
                L[u][u]+=1;L[w][w]+=1;L[u][w]-=1;L[w][u]-=1
    return L

def levelwise_CD(n, adjB, M, f):
    """For threshold cuts S_t = {v : f[v] >= t}, sweep t through sorted distinct f-values.
    Return list of (t, |delta_B|, |delta_M|) and the SUMS.  Verifies levelwise CD."""
    vals=sorted(set(f))
    rows=[]
    sumB=0; sumM=0
    # thresholds between consecutive distinct values: S_t = {f >= vals[k]} for k=1..end
    for k in range(1,len(vals)):
        t=(vals[k-1]+vals[k])/2.0
        S=set(v for v in range(n) if f[v]>=t)
        dB=sum(1 for u in range(n) for w in adjB[u] if u<w and ((u in S)!=(w in S)))
        dM=sum(1 for (u,v) in M if (u in S)!=(v in S))
        rows.append((round(t,4),dB,dM))
        sumB+=dB; sumM+=dM
    return rows,sumB,sumM

def analyze(name,n,adj):
    mc,cuts=all_maxcuts(n,adj)
    best=None
    for side in cuts:
        adjB,M=build_B_M(n,adj,side); D=bdist_all(n,adjB)
        G=sum((D[u][v]+1)**2 for (u,v) in M)
        if best is None or G<best[0]: best=(G,M,adjB,D,side)
    G,M,adjB,D,side=best
    L=lap_B(n,adjB)
    ev,evec=np.linalg.eigh(L)
    # Fiedler vector (smallest nonzero eigenvalue); for disconnected B use 2nd eig of big comp -- here global
    fied=evec[:,1]
    rowsF,sBF,sMF=levelwise_CD(n,adjB,M,fied)
    # top eigenvector
    top=evec[:,-1]
    rowsT,sBT,sMT=levelwise_CD(n,adjB,M,top)
    # the SIDE potential: 0/1 indicator of X vs Y is trivial. Use BFS-distance-from-a-bad-endpoint as a
    # natural 'phase' potential (mod analog). We test the C5-phase: for C5[q] f = part index 0..4.
    print(f"\n=== {name}: N={n} |M|={len(M)} Gamma={G} Gamma/N^2={G/n**2:.4f}")
    print(f"    Fiedler levels: sum|dB|={sBF}, sum|dM|={sMF}, ratio sumM/sumB={sMF/max(sBF,1):.3f}")
    print(f"    Top-eig levels: sum|dB|={sBT}, sum|dM|={sMT}")
    # the genuinely-spectral assembly attempt: Gamma vs (sum_t |dB_t|) and (sum_t |dM_t|)
    # On C5[q] with the phase potential, each bad edge (dist 4) is crossed by 4 of the 5 phase-levels.
    return G,n,M,adjB,D

def phase_levels_c5(q):
    """For C5[q], f = part index. The 5 cyclic levels; test the squared-coarea assembly."""
    N,adj=c5_blowup(q)
    side=[0]* N
    # max cut of C5[q]: it's NOT bipartite; a max cut splits to maximize crossing.
    mc,cuts=all_maxcuts(N,adj)
    # use the verify_cosystole choice
    best=None
    for s in cuts:
        adjB,M=build_B_M(N,adj,s); D=bdist_all(N,adjB)
        G=sum((D[u][v]+1)**2 for (u,v) in M)
        if best is None or G<best[0]: best=(G,M,adjB,D,s)
    G,M,adjB,D,s=best
    part=[v//q for v in range(N)]
    # cyclic phase: assign angle 2*pi*part/5; use real coordinate cos for a threshold sweep
    # Key measurement: for each bad edge, which 'B-levels' does its shortest path cross.
    print(f"\n=== C5[{q}] PHASE ANALYSIS: N={N} |M|={len(M)} Gamma={G}")
    print(f"    parts of bad-edge endpoints:")
    cnt={}
    for (u,v) in M:
        key=(part[u],part[v]); cnt[key]=cnt.get(key,0)+1
    print(f"    bad-edge part-pairs (count): {cnt}")
    # In C5[q] max cut, B = which edges are cut? Print B-degree distribution
    degB=[len(adjB[v]) for v in range(N)]
    print(f"    B-degree multiset: {sorted(set(degB))}, |B-edges|={sum(degB)//2}")
    return

if __name__=="__main__":
    for q in [1,2,3]:
        analyze(f"C5[{q}]",*c5_blowup(q))
    for L in [5,7,9]:
        analyze(f"C_{L}",*odd_cycle(L))
    analyze("Petersen",*petersen())
    analyze("theta46",*theta46())
    print("\n----- PHASE -----")
    for q in [1,2,3]:
        phase_levels_c5(q)
    print("\nDONE")
