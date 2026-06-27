# GPT-Pro round 5: right invariant Theta=F-D/5, corrected (Gamma-budget) unifying both routes (2026-06-26)

Thread c/6a3b8a74. Step-1 sent the exact (Q)-refutation (a=1/5 impossible: C5/Petersen/n8 all on F=D/5, n8 has
rho>0 yet margin 0). GPT round-5 response. AUDITED + calibration-table checked.

## Verdict
My refutation is DECISIVE; (Q) is false as a universal band inequality, structurally (not a normalization
accident). Repair is NOT a>1/5 (wrong direction: for D<2/5 any supporting line F-2/25<=a(D-2/5) is compatible
with the whole F=D/5 family only if a<=1/5).

## The right invariant: Theta := F - D/5  (tax the excess over the F=D/5 face, NOT raw rho)
Raw rho is positive on harmless low-F configs (incl. n8). Using F=alpha*D+rho:  Theta = rho - (1/5 - alpha)D.
n8 EXACTLY explained: D=5/16, alpha=2/13, rho=3/208, and (1/5-alpha)D = (3/65)(5/16) = 3/208 = rho => Theta=0.
So n8 sits ON the F=D/5 face (Theta=0) despite rho>0 -- which is why raw rho was the wrong tax.
VERIFIED (calibration table): Theta=0 on {C5,Petersen,n8,C5[2]} (the F=D/5 family); C7 Theta<0; band
Mycielskians ABOVE the face: M(Petersen) Theta=+0.00907, M(Grotzsch) Theta=+0.00681.

## Non-circular logic (scope = joint fixed-density KKT maximizers only)
For each band density d0, M(d0)=sup F over triangle-free with int W=d0. A band counterexample => a maximizer
(after compactness regularization) with F>=2/25 => satisfies joint KKT + weighted-regular slack => apply the
structural inequality => contradiction. C5-type is ONLY the equality-case consequence AFTER the inequality
rules out the band. Equality analysis: pentagonal equality forces P=1/5+2C_W => weighted C5-blowup; then
F=2 min_i w_i w_{i+1}=2/25 with sum w_i=1 forces all w_i=1/5 => balanced C5. Excludes Petersen/n8 (they have
D<2/5, live on the auxiliary F=D/5 face which is strictly below 2/25 in the band).

## Corrected import of the finite Gamma evidence -- (Gamma-budget) [UNIFIES BOTH ROUTES]
NOT -kappa*rho (wrong tax). Correct shape:
   (Gamma-budget)   F - D/5 + c*Delta_Gamma  <=  eta*(2/5 - D),   eta < 2/25, c>0,
where Delta_Gamma = the normalized NON-PARALLEL-OVERLAP Gamma-deficit (Step-2's quantity, the OVERLAP part of
N^2-Gamma, NOT the total deficit). Couples my Theta=F-D/5 (cut-pressure) with Step-2's Delta_Gamma (peel/overlap)
against the density-gap budget (2/5-D). Equality only at balanced C5. The d_mono=2beta/N^2 transfer is NOT the
issue; the band-inequality SHAPE is.

## Status (still OPEN; this is a reformulation, not a proof)
(Gamma-budget)/(EIF) is unproven -- it is the rigidity, now correctly formulated in (Theta, Delta_Gamma). Right
invariant + non-circular logic + correct equality set are the round-5 gains. To exact-test (Gamma-budget) and
calibrate (c,eta) I need Step-2's precise Delta_Gamma normalization (overlap-only). Calibration data staged
(test points: Theta, 2/5-D, total deficit). Relayed to Step-2. (Q) is dead; the rigidity stands.
See [[erdos23-delta0-cut-pressure-rigidity]], [[erdos23-gamma-geodesic-peel-angle]], [[erdos23-agent-channel]].
