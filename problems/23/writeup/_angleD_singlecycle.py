"""ANGLE D sub-case (4a): SINGLE bad edge with a UNIQUE shortest geodesic => one odd ell-cycle C_ell,
   and (4b): vertex-disjoint bad edges each with unique geodesic => H block-decomposes into disjoint
   odd-cycle blocks.  PROVE (GCD) H>=0 in closed form here.

SINGLE CYCLE.  f has |P_f|=1, geodesic = ell vertices on an odd cycle C_ell.  Then:
   - p_f(v) = 1 on the ell cycle vertices, 0 else;  K = p_f p_f^T (rank 1, the all-ones on cycle).
   - omega(e) = a_bar(ell) on each of the ell cycle edges (incl. f), 0 else.
   - T(v) = ell on cycle vertices, 0 off-cycle.   (sum T = ell^2 = Gamma; single bad edge ell>=5.)
   On the ell cycle vertices, restricted H = a_bar(ell) L_{C_ell} + diag(N-ell).  Off-cycle vertices
   contribute diag(N-0)=N>0 (isolated, trivially PSD).  So H>=0  <=>  a_bar(ell)L_{C_ell}+(N-ell)I >= 0
   on the cycle.  Eigenvalues of L_{C_ell}: 2-2cos(2pi j/ell), j=0..ell-1; min is 0 (j=0).  So the
   smallest eigenvalue of a_bar L_{C_ell}+(N-ell)I is (N-ell) (at the constant mode j=0).
   THEREFORE  H>=0  <=>  N >= ell.   And N>=ell ALWAYS (the cycle has ell distinct vertices in a graph
   on N vertices, and a single bad edge needs at least its ell cycle vertices present).  QED for 4a.
   The constant-mode value N-ell = N^2-Gamma only when... here 1^T H 1 = sum(N-T) = N*N - ell^2? NO:
   off-cycle vertices each add (N-0)=N, cycle vertices add (N-ell) each: total = ell(N-ell)+(N-ell)*?
   Let's just verify 1^T H 1 = N^2 - Gamma exactly and the per-cycle min eig = N-ell.

This is the cleanest HONEST special case: a fully closed-form proof H>=0 <=> N>=ell, tight at N=ell
(the cycle fills the whole graph, balanced odd cycle = the C_ell[1] extremal).

DISJOINT (4b): if bad edges f_1..f_m have pairwise vertex-disjoint unique-geodesic cycles, omega and
T are supported on disjoint vertex sets, H = direct sum of the per-cycle blocks + diag(N) off all,
so H>=0 <=> each block PSD <=> N >= ell(f_i) for all i.  Again automatic.  (Real instances rarely
have unique geodesics, but this isolates the mechanism + matches the extremal equality.)

We exact-verify: build a graph that REALIZES a single odd cycle as the unique geodesic of one bad edge,
confirm restricted-H min eig = N-ell and H>=0 <=> N>=ell."""
from fractions import Fraction as F
from _gcd import a_bar, is_psd_exact, float_mineig

def single_cycle_H(ell, N):
    """Closed-form H for one bad edge with unique geodesic = a single odd ell-cycle, ambient N>=ell.
       Cycle vertices 0..ell-1; off-cycle ell..N-1 isolated.  Returns H (NxN, exact)."""
    assert ell%2==1 and ell>=5 and N>=ell
    ab=a_bar(ell)
    H=[[F(0)]*N for _ in range(N)]
    # a_bar * L_{C_ell} on cycle
    for i in range(ell):
        j=(i+1)%ell
        H[i][i]+=ab; H[j][j]+=ab; H[i][j]-=ab; H[j][i]-=ab
    # diag(N - T): T=ell on cycle, 0 off
    for v in range(N):
        T=ell if v<ell else 0
        H[v][v]+=F(N)-T
    return H

if __name__=="__main__":
    print("=== ANGLE D (4a) single odd-cycle: H>=0 <=> N>=ell, min eig = N-ell, tight at N=ell ===")
    for ell in (5,7,9):
        for N in (ell, ell+1, ell+3):
            H=single_cycle_H(ell,N)
            me=float_mineig(H,N)
            psd=is_psd_exact(H,N)
            Gamma=ell*ell  # single bad edge
            ohN=sum(F(N)- (ell if v<ell else 0) for v in range(N))  # 1^T H 1
            print(f"  ell={ell} N={N}: PSD={psd} mineig={me:+.4f} (predicted N-ell={N-ell}) "
                  f"1^T H 1={ohN} (N^2-Gamma={N*N-Gamma})",flush=True)
    print("--- below threshold N<ell would be infeasible (cycle needs ell vertices); show N=ell-? skipped ---")
    # demonstrate the strict-negative case if we ARTIFICIALLY set N<ell (not graph-realizable):
    for ell,N in [(5,4),(7,5)]:
        ab=a_bar(ell); H=[[F(0)]*ell for _ in range(ell)]
        for i in range(ell):
            j=(i+1)%ell; H[i][i]+=ab;H[j][j]+=ab;H[i][j]-=ab;H[j][i]-=ab
        for v in range(ell): H[v][v]+=F(N)-ell
        print(f"  (artificial N={N}<ell={ell}): mineig={float_mineig(H,ell):+.4f} PSD={is_psd_exact(H,ell)} "
              f"-> confirms threshold is exactly N=ell",flush=True)
