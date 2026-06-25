#!/usr/bin/env python3
"""STRATEGY C, part 3: pin down the EXACT spectral assembly that gives Gamma <= N^2 and tightness at C5[q].

Findings so far:
 - raw effective resistance R_eff is the WRONG object (shrinks ~1/q under blow-up).
 - Fiedler-vector threshold sweep has levelwise CD TIGHT (sumM=sumB) at C5[q] and C_L, loose elsewhere.

Now: relate Gamma to a SQUARED spectral form.  The candidate identity we test:

  For potential f on V(B) and the bad-edge quadratic energy E_M(f)=sum_{uv in M}(f(u)-f(v))^2 and the
  B-energy E_B(f)=sum_{B-edges xy}(f(x)-f(y))^2 = f^T L_B f:

   (R-form) sum_{uv in M}(f(u)-f(v))^2  <=  rho(f) * f^T L_B f       (CD-type, levelwise)
  and       (d_B(u,v))^2  <=  d_B(u,v) * sum over geodesic edges (1)^2  -- triangle/Cauchy on the path.

  The cleaner route: a RAYLEIGH inequality.  Take f = Fiedler vector, lambda2 = f^T L_B f / (f^T f).
  On C5[q], all bad edges have the same (f(u)-f(v))^2; we want to see the factor 25 emerge as
  (something)^2 from the C5 eigenstructure (lambda2(C5)=2-2cos(2pi/5), eigenvector phase gap = 4pi/5).

We compute, for C5[q] and the tight cycles, the exact quantities:
   E_M(f)/E_B(f)   for f=Fiedler,
   E_M(f) and (f(u)-f(v)) for bad edges,
   and we test the SQUARED-DISTANCE assembly via the Cauchy-Schwarz chain that the proof needs:
     ell_e = 1 + d_B(u,v),  d_B(u,v) = min #B-edges on a u-v path.
     For the harmonic potential h_e that is the unit-resistance flow potential, (f(u)-f(v)) relates to R_eff.
   We instead test the DUAL coarea-square:  Gamma = sum_e ell_e^2 and the level sweep gives
     sum_e ell_e = sum_e (1 + #levels a geodesic crosses).  We verify the EXACT bookkeeping:
        sum_{uv in M} d_B(u,v)  =  sum_t |delta_M-geodesic crossings at level t|.
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

def get_bestcut(n,adj):
    mc,cuts=all_maxcuts(n,adj); best=None
    for s in cuts:
        adjB,M=build_B_M(n,adj,s); D=bdist_all(n,adjB)
        G=sum((D[u][v]+1)**2 for (u,v) in M)
        if best is None or G<best[0]: best=(G,M,adjB,D,s)
    return best

def rayleigh_report(name,n,adj):
    G,M,adjB,D,s=get_bestcut(n,adj)
    L=lap_B(n,adjB)
    ev,evec=np.linalg.eigh(L)
    f=evec[:,1]   # Fiedler
    EB=float(f@L@f)
    EM=sum((f[u]-f[v])**2 for (u,v) in M)
    lam2=ev[1]
    # bad-edge gaps
    gaps=[abs(f[u]-f[v]) for (u,v) in M]
    nB=sum(len(adjB[v]) for v in range(n))//2
    print(f"\n=== {name}: N={n} |M|={len(M)} Gamma={G} |B|={nB}")
    print(f"    lambda2(L_B)={lam2:.5f}  E_B(Fiedler)={EB:.5f}  E_M(Fiedler)={EM:.5f}  E_M/E_B={EM/EB:.5f}")
    print(f"    sum d_B(M)={sum(D[u][v] for (u,v) in M)}  sum ell(M)={sum(D[u][v]+1 for (u,v) in M)}")
    # the level-cut budget identity: along Fiedler sweep, sum_t |dB_t| = total variation of f rounded.
    return G,n,EM,EB,lam2

def assembly_c5(q):
    """For C5[q] verify EXACTLY where N^2 and 25 come from.
       B of C5[q] under its max cut: report structure + the 'phase' eigenvector decomposition."""
    N,adj=c5_blowup(q)
    G,M,adjB,D,s=get_bestcut(N,adj)
    L=lap_B(N,adjB)
    ev,evec=np.linalg.eigh(L)
    # C5[q] B has a 5-fold cyclic structure; the two Fiedler eigenvectors realize the C5 phase.
    lam2=ev[1]; lam3=ev[2]
    print(f"\n--- C5[{q}] assembly: N={N} |M|={len(M)}=q^2 Gamma={G}=N^2  q={q}")
    print(f"    lambda2=lambda3={lam2:.5f},{lam3:.5f} (C5 phase pair); 2-2cos(2pi/5)*?= {2-2*np.cos(2*np.pi/5):.5f}")
    # the 5 'parts' have B-degree pattern; show that B = complete bipartite blow-up of a PATH P5 (the max cut
    # cuts 4 of the 5 C5-edges; one C5-edge becomes monochromatic => B is the blow-up of P5, M=blow-up of the
    # 5th edge). Confirm:
    part=[v//q for v in range(N)]
    # which part-pairs are B-edges vs M-edges
    Bpairs=set(); Mpairs=set()
    for u in range(N):
        for w in adjB[u]:
            if w>u: Bpairs.add(tuple(sorted((part[u],part[w]))))
    for (u,v) in M: Mpairs.add(tuple(sorted((part[u],part[v]))))
    print(f"    B part-pairs={sorted(Bpairs)}  M part-pairs={sorted(Mpairs)}")
    print(f"    => B is the blow-up of a PATH on 5 parts; M = blow-up of the closing edge => 'open C5'")
    # so the bad edges form a complete bipartite block between the two END parts of the P5 blow-up,
    # at B-distance 4. The single-block AM-GM (module 4) is EXACTLY this. Confirm shells a_i = q each:
    sizes=[part.count(i) for i in range(5)]
    print(f"    part sizes a_0..a_4 = {sizes}  (sum={sum(sizes)}=N)  => 5-shell layered, each=q")
    print(f"    AM-GM: 25*q = {25*q} <= (sum/5*5)... N^2={N*N}; m=q^2={q*q}=N^2/25 EXACT")
    return

if __name__=="__main__":
    for q in [1,2,3,4]:
        rayleigh_report(f"C5[{q}]",*c5_blowup(q))
    for L in [5,7,9,11]:
        rayleigh_report(f"C_{L}",*odd_cycle(L))
    rayleigh_report("Petersen",*petersen())
    rayleigh_report("theta46",*theta46())
    print("\n===== EXACT C5[q] ASSEMBLY =====")
    for q in [1,2,3,4]:
        assembly_c5(q)
    print("\nDONE")
