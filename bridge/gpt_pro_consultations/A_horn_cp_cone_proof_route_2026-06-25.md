# GPT Pro: PRIMARY proof route = order-10 conic certificate; new tool = ROOTED HORN (C5) inequality (CP cone)

chat 6a3b5aba. Pursue both; the order-10 conic cert is the PRIMARY theorem route. No clean elementary proof of
U_8<=2/25 on the band seen (may be strictly stronger than the conjecture; 6 examples don't exclude band graphons
with U_8>2/25 but d_mono<=2/25). BCL medium interval still the published open region (Jan 2026).

## THE ANALYTIC HANDLE = rooted COMPLETE POSITIVITY; first inequality = rooted Horn (C5)
Real graphon: P_R = E_z[1_R p(z)p(z)^T], p_A(z)>=0  => P_R is COMPLETELY POSITIVE (CP), not just PSD. PSD+entrywise>=0
(doubly-nonneg DNN) is only the first relaxation. First exact inequality beyond PSD:
  H_R(A_0..A_4) = sum_{i,j=0..4} P_R(A_i,A_j) - 4 sum_{i=0..4} P_R(A_i,A_{i+1}) >= 0   (indices mod 5)   [Horn-R]
Proof: pointwise (sum_i x_i)^2 >= 4 sum_i x_i x_{i+1} for x_i>=0 (Motzkin-Straus / C5); average over roots.
LINEAR in q, graphon-SOUND, NOT implied by P_R>=0 + entrywise>=0, aligned with the odd-cycle obstruction, distinct
from the unsound cp_cache localizers.

### FIRST CONCRETE COMPUTATION (now):
  h_min = min_{R, A_0..A_4} H_R(A_0..A_4)/Pr(R).
Generate candidates from HIGH-WEIGHT 5-CYCLES in the profile edge matrix w_R (cycles carrying frustrated mass in the
optimal profile MaxCut), not arbitrary 5-tuples. If h_min<0, add all materially violated Horn rows. Tests DNN vs CP.

### Eventual analytic cert (Stab-U8):
  2/25 - U_8(W) >= lambda(2/5 - d_edge(W)) + sum_{R,A} alpha_{R,A} H_R(A) + sum_j SOS_j(W), all coeffs nonneg rational.
Would prove the band + explain equality only at C5 density (2/5).

## EXACT CERTIFICATION FEASIBLE (route a): rationalize PSD dual -> exact rank-1 cuts + one integer identity.
Y_R>=0 (numeric dual) -> factor Y_R ~ sum_j y y^T -> rationalize y->c -> Y'_R=sum c c^T exactly rational PSD ->
<Y'_R,P_R(q)> = sum_j c^T P_R(q) c >= 0 graphon-sound (no numerical eigenvalue claim).
Full cert: 2/25 - m = sum_i lambda_i(valid row_i) + sum_{R,j} c_{R,j}^T P_R(q) c_{R,j} + sum_J s_J q_J, lambda,s>=0 rational.
Workflow: rationalize duals+Cholesky; recompute 12172 coeffs exactly; residuals->s_J; slightly weaken objective; clear
denominators; verify ONE integer identity. Large for exact OPT but fine for exact VERIFICATION (streaming over 12172
cols). Strict band margin makes rationalization much easier than a true-optimum-zero cert.

## The persistent -0.50 Gram violation: projection-cut outer-approx NOT converging to PSD-feasible. TWO cases:
  (a) accumulated valid cuts force eta<=0 => ALREADY A PROOF (final pseudo-state need NOT satisfy all PSD; a finite set
      of sound rank-1/projection inequalities with upper bound <=0 suffices).
  (b) eta stays positive => cutting-plane does NOT determine the true PSD optimum; need actual block LMIs or compressed
      subspace LMIs V_R^T P_R(q) V_R >= 0. eta-descent useful but can't justify a positive STOP.

## PROBABILITY (GPT): N<=180 HIGH; full band via U_8+(8,9) alone ~1/4; full band after (6,8)+rooted CP/Horn ~1/2;
## short human-only analytic U_8<=2/25 LOWER than the computer-assisted conic cert.

## EXECUTION ORDER:
1. Continue the fast projection-cut run; if it crosses eta=0, rationalize immediately.
2. In PARALLEL, run a genuine compressed/full (8,9) SDP WITHOUT the redundant k=7 leg.
3. At its PSD-feasible optimizer, separate rooted Horn inequalities [Horn-R].
4. If still positive, activate (6,8) pair-flag blocks.
5. Use the numerical dual to search for the stability identity (Stab-U8).
THE single analytic computation to begin NOW: h_min = min over R, 5-tuples of [sum_{i,j}P_R(A_i,A_j) - 4 sum_i P_R(A_i,A_{i+1})]/Pr(R).
