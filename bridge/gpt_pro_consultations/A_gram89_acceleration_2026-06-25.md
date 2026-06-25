# GPT Pro: accelerate the (8,9) Gram-PSD enforcement (path A finish)

chat 6a3b5aba. (8,9) audit confirmed GPT's diagnosis: witness min_R lambdahat=-0.5 (249/260 roots), C5/C7/Petersen PSD.

## Fastest (8,9) enforcement
- STOP top-4 only. Add ALL materially negative modes per active root R: those with lambda_i(P_R)/Pr(R) < -1e-7.
- ADD the single PROJECTION CUT (deepest Frobenius-norm separating hyperplane):
    P_{R,-} = sum_{lambda_i<0} lambda_i v_i v_i^T  (NSD negative part)
    cut:  <-P_{R,-}, P_R(q)> >= 0     (i.e. <M,P_R(q)>>=0 with M = -P_{R,-}, PSD)
  This captures ALL negative curvature in ONE cut.
- BETTER: compressed subspace LMI  V_R^T P_R(q) V_R >= 0  (V_R = accumulated neg eigenvectors) -- controls
  rotations/cross-terms, stronger than scalar v_i^T P_R v_i >= 0.
- BEST: a numerical SDP solver (cvxpy+Clarabel/SCS/MOSEK) with P_R(q)>=0 as block LMIs = the ORACLE for the true
  tightened optimum. For the EXACT cert: decompose the dual PSD multipliers into rank-one vectors, rationalize,
  insert c^T P_R(q) c >= 0 into the exact LP (numerical SDP does NOT enter the final proof).

## (6,8) blocks: PREBUILD now (matrix-free eig eval), do NOT activate until (8,9) is PSD-feasible:
  activate when  min_R lambda_min(P_R)/Pr(R) >= -1e-9  AND objective still positive, OR (8,9) outer-approx stalls
  with material PSD error. (The witness (6,8) violations may just duplicate its (8,9) failure.)

## PROTOCOL
1. Full k7+k8 envelope. 2. Complete (8,9) PSD enforcement (LMIs or all modes + projection cuts). 3. Continue until
   max_R [-lambda_min(P_R)/Pr(R)] < 1e-9 AND all U_8 gaps < tol. 4. Record converged eta_{8,9}. 5. Only then
   activate materially-violated (6,8) modes.
## INTERPRETATION of converged eta:
  eta_{8,9} <= 0           => CLOSE Step-2 (then rationalize to exact).
  0 < eta_{8,9} < 6.17e-5  => recover N<=180, but Step-2 (band) remains.
  eta_{8,9} > 6.17e-5      => immediately test (6,8).
  positive after (8,9)+(6,8) fully separated => order-10 has reached its CREDIBLE LIMIT -> pivot to (C) stability.
## Closure plausible (witness violates (8,9) by -0.5 on ~all roots; not incidental since U_8 is built from these
   profiles) but NOT guaranteed: P_R>=0 is only 2nd-order conditional realizability, not the full edge-conditioned
   profile law. The 0.78-ratio descent = cutting-plane zig-zag, NOT a positive plateau.
