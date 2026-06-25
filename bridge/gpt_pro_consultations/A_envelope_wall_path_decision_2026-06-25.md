# GPT Pro consult (DRAFT, pending LP plateau): sound U_8 envelope walls — which path to close #23 band?

chat 6a3b5aba (continue). Status to send once combined+C5diag plateau is known.

## What is now SETTLED (sound, audited)
1. **Fixed-cut deficit cert is NOT graphon-soundly repairable.** Re-derived with your type-balance (3)+(4)
   full-coverage: balanced k=7-only delta'=+7.04e-3, mixed +2.72e-4, both >> 6.17e-5. The "1.6e-7" was the
   UNBALANCED LP value (not graphon-sound). => agent-1 must NOT publish the order-9 deficit cert as-is.
2. **d_mono(W) <= U_8(W) is PROVEN + VALIDATED (factor 1).** Proof: for fixed anchors z_1..z_8 the policy
   "color v by sigma_R(profile_R(v))" is a consistent global coloring => d_mono <= E_anchors[mono under sigma]
   for any fixed sigma; min over sigma decomposes per-R independently (each R = distinct anchor-realization
   event, no conflict) => d_mono <= sum_R min_c L_{R,c} = U_8. Validated on 6 real triangle-free graphs:
   C5 ratio 1.000 (TIGHT), C7 1.002, C9 1.127, P5 inf(d_mono=0), C5uC5 1.016, Petersen 1.013; worst U_8-d_mono=-1.4e-17.
3. So the SOUND closure criterion is: max over the order-9/10 band relaxation of (U_8 - 2/25) <= 0.

## What the sound envelope LP gives (the WALL)
- k=7 per-root envelope (order-9, 107 T7 types complete cover) walls at **eta = +6.06e-4** (honest graphon-sound
  order-9 number; the old +4.3e-5 used the UNSOUND individual-cut deficit bound).
- COMBINED k7 (order-9, x=Dq) + k8 (U_8 order-10, nR=410 per-R MaxCut envelope) + C5-diagonal, validity rows only
  (deficit EXCLUDED): eta = 4.49e-3 -> 3.10 -> 2.38 -> 1.87 -> 1.38e-3 over it0..4, decelerating (ratios ~0.69,
  0.77,0.78,0.74). Iter cost grew to ~556s so I stopped at it4; extrapolated PLATEAU in the **~3-6e-4** range.
- C5-diagonal tangent cuts (gam.q >= (pC5.x)^2): essentially INACTIVE (fired once at it4; c=pC5.x ~ 0.011 constant so
  c^2 ~ 1.2e-4 trivially satisfied) -- the looseness is NOT in the C5 direction.

## STEP-1 IMPLICATION (sharp thresholds)
Base case a(5n)<=n^2: integer rounding needs delta < 2/(25 n^2). Largest base case N=180 (n=36) => delta < 6.17e-5;
N=30 => delta < 2.2e-3. The SOUND order-9 envelope (delta=6.06e-4) recovers only N<=55 (n<=11); the old "6.07e-5
closes N<=180" was the UNSOUND deficit bound. The combined order-9/10 envelope (walls ~3-6e-4) STILL does not reach
6.17e-5 => N<=180 base cases are NOT soundly recovered at order 9/10. (And the band requires eta<=0, also not reached.)

## KEY DIAGNOSIS
Real BAND graphons (d_edge in [0.2486,0.3197]) have U_8 <= ~0.06 with margin (Petersen d_edge=0.3 -> U_8=0.0608;
the extremal C5 has U_8=0.08 but d_edge=0.4 = the TAIL, OUTSIDE the band). So U_8 <= 2/25 holds on REAL band
graphons; the residual eta>0 is RELAXATION LOOSENESS (pseudo-graphons in the order-9/10 moment relaxation), not
a failure of U_8. The wall is the order-9/10 resolution limit (cf. the order-9 SDP P2 wall; order-11 infeasible at n=10).

## DECISION REQUESTED (pick the path; I'll execute + audit)
(A) Keep tightening the q-relaxation at order 9/10 with more SOUND constraints until eta<=0. If so, WHICH give the
    most cut per unit work: full order-10 moment-PSD localizers on q (rank-one separation), more C5-family diagonal
    (t(C5⊔K1), t(C7) diagonals), or kK1/independent-set localizers? Is there a reason to expect order-9/10 CAN
    close the band soundly, or is the P2-type looseness fundamental here too?
(B) Accept that sound flag methods at order 9/10 cap at d_mono <= 2/25 + ~1e-3, and PIVOT to the cut-geometry route
    (triangle-free beta <= N^2/25 via max-cut geometry; Gamma=sum ell^2 <= N^2 invariant; reduced to the single
    open "Sync" block->general lemma needing electrical-flow congestion). Is that the better bet for the EXACT 2/25,
    and what is the fastest attack on the Sync lemma?
(C) Something else (a hybrid: use U_8 to certify the band EXCEPT a small neighborhood of C5, handle C5-neighborhood
    by the cut-geometry/stability argument)?

My lean: (A) if you can name 1-2 specific tighteners likely to close; else (B)/(C). Your call per our standing rule.
