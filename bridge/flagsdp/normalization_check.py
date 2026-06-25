"""Pin down the EXACT normalization logic so it is non-circular.

Claim chain for a 2-conn edge-critical tri-free atom K (n vtx, tau=t):
  (Q) there is a min signature S and a uniform-over-geodesics routing of the t bad edges with
      max B-edge congestion rho <= n^2/(25 t)   AND   rho is achieved (rho>=... ).
  The routing assigns to each bad edge e a fractional family of odd cycles (geodesic + e), total weight 1
  per bad edge. Scale ALL weights by 1/rho': the scaled family is a feasible fractional odd-cycle packing
  (every edge load <= 1) of value t/rho', where rho' = max(rho_B, rho_M) and rho_M = max M-edge load.
  Each bad edge e carries total weight 1 on its own M-edge and 0 on other M-edges (private!), so rho_M=1.
  Hence rho' = max(1, rho_B). Value = t / max(1, rho_B).

  Want value >= 25 t^2 / n^2, i.e.  max(1, rho_B) <= n^2/(25t).
  This needs BOTH  rho_B <= n^2/(25t)  AND  1 <= n^2/(25t) i.e. t <= n^2/25.

  CIRCULARITY CHECK: 't<=n^2/25' is the theorem itself. So the congestion bound 'rho_B <= n^2/(25t)'
  must ALSO independently force t<=n^2/25, OR we get t<=n^2/25 for free another way.

  RESOLUTION: We do NOT need value >= 25t^2/n^2 as a separate fact. We directly get
     nu*(K) >= value = t / max(1, rho_B).
  Combined with the UNCONDITIONAL upper bound nu*(K) <= n^2/25 (Cauchy+cycle-degree, PROVED, no Guenin):
     t / max(1, rho_B) <= nu*(K) <= n^2/25.
  If rho_B <= 1:  t/1 = t <= n^2/25.  DONE (theorem).
  If rho_B > 1:   t/rho_B <= n^2/25  =>  t <= rho_B * n^2/25.  NOT directly t<=n^2/25 unless rho_B controlled.

  So the SHARP needed statement is exactly:  rho_B <= n^2/(25t)  on atoms. Then
     n^2/25 >= nu* >= t/max(1,rho_B) >= t/(n^2/(25t)) = 25t^2/n^2   (using rho_B<=n^2/25t and, when
     rho_B<1, max(1,rho_B)=1<=n^2/(25t) iff t<=n^2/25 -- still need this!).

  CLEANEST NON-CIRCULAR FORM: prove   t/max(1,rho_B) >= 25 t^2/n^2  is NOT what we want; instead just use
     nu*(K) >= t/max(1,rho_B)  AND  the SEPARATE clean inequality  max(1,rho_B) <= n^2/(25t)
  where the second is proved as TWO facts:
     (i) rho_B <= n^2/(25t)   [the congestion lemma]
     (ii) t <= n^2/25         [follows from (i) + nu*<=n^2/25 IF rho_B>=1 region is consistent]
  Actually (ii): from nu* >= t/max(1,rho_B) and nu*<=n^2/25: t <= max(1,rho_B)*n^2/25 <= (n^2/25t)*n^2/25.
     => 25 t^2 <= n^4/25 ... gives t <= n^2/25. YES non-circular!  Let me verify the algebra:
     t <= max(1,rho_B) * n^2/25. If rho_B<=n^2/(25t) then max(1,rho_B)<=max(1, n^2/(25t)).
       case t<=n^2/25: max=... need t<=n^2/25 -- assumed. circular in this case but TRIVIALLY the conclusion.
       case t>n^2/25: then n^2/(25t)<1 so max(1,rho_B)... rho_B<=n^2/25t<1 so max=1, giving t<=n^2/25,
                      CONTRADICTION with t>n^2/25. So case t>n^2/25 is IMPOSSIBLE given rho_B<=n^2/(25t).
  => rho_B <= n^2/(25t) ALONE forces t<=n^2/25 (the theorem). NON-CIRCULAR.

This module just re-verifies, on each atom, that rho_B(best sig) <= n^2/(25t), and prints the deduced
t <= n^2/25 with the slack, to confirm the logic end-to-end.
"""
import verify_D25_lemma16 as L
from test_qfc_atoms import rho_spread


def verify(builder, lab):
    N, A = builder
    r = rho_spread(N, A)
    if r is None:
        print(f"{lab}: bipartite"); return
    rho, t, NN = r
    cong_bound = NN*NN/(25.0*t)
    nu_upper = NN*NN/25.0
    val = t/max(1.0, rho)
    print(f"{lab}: n={NN} t={t} rho_B={rho:.4f}  rho_B<=n^2/25t={cong_bound:.4f}: {rho<=cong_bound+1e-7}")
    print(f"    nu* in [{val:.4f}, {nu_upper:.4f}]  => t={t} <= n^2/25={nu_upper:.4f}: {t<=nu_upper+1e-7} "
          f"(value 25t^2/n^2={25*t*t/(NN*NN):.4f})")


for b, lab in [(L.c5(), 'C5'), (L.c5n(2), 'C5[2]'), (L.petersen(), 'Petersen'),
               (L.gpt_k23(), 'K23-N13'), (L.c5n(3), 'C5[3]')]:
    verify(b, lab)
