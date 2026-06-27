# GPT-Pro round 4: cut-metric (Q) inequality target -- EXACT-REFUTED at n=8 (2026-06-26)

Thread c/6a3b8a74. Step-1 asked GPT to prove NRS (F>=2/25 => rho=0 => weighted C5) via the pentagonal/
cut-metric inequality on R=1-P. AUDITED + EXACT-TESTED (test_Q_inequality.py) BEFORE adopting.

## GPT round-4 verdict (honest)
The pentagonal cut-metric is the right DETECTOR of the obstruction but does NOT force rho=0 by itself.
Reason: S=W(P-alpha) is edge-degree regular (int S dy = rho), while pentagonal inequalities see S only
through its 5-cycle marginal (density of length-4 returns through each edge); the two marginals DECOUPLE,
and the n=8 hub-overlap witness is exactly where they decouple. Pentagonal exposes rho>0 as non-parallel
C5 overlap but does not kill it. Facet families identified: (OC), (PENT), (TOT) -- their joint equality
case = "every optimal cut restricts to a max cut on the sampled C5", tight at balanced C5 (P=1/5 cyclic,
3/5 diagonal). Integrated pentagonal surplus Pi_5(x1..x5)=prod W(x_i,x_{i+1}).

## Proposed closing target (Q) -- and its EXACT REFUTATION
GPT's "minimal cut-metric input": (Q)  F - 2/25 <= a(D - 2/5) - kappa*rho + E_pent,
  a "naturally" 1/5, kappa>0, E_pent<=0 (signed pentagonal facets, nonpositive by cut-metric validity),
  equality only at balanced C5. Then in band D<2/5 and rho>0 => RHS<0 => F<2/25 = NRS.
GPT also: "once F>=2/25 => tightness is proved, the collaborator's finite Gamma=N^2 => C5[q] rigidity
imports to graphons by compactness."

STEP-1 EXACT TEST (test_Q_inequality.py, Fractions): (Q) with a=1/5 is REFUTED as a universal band inequality.
Necessary condition (E_pent<=0 only hurts): margin m := a(D-2/5) - (F-2/25) >= kappa*rho > 0 wherever rho>0.
  C5:        m=0,        rho=0   (equality case, ok)
  C7:        m=4/245>0,  rho=0   (ok, slack)
  Petersen:  m=0,        rho=0   (a-term TIGHT, but rho=0 so no kappa*rho needed)
  n8 band-max: m=0,      rho=3/208>0   *** (Q) FAILS: m=0 but rho>0, no room for kappa*rho>0 ***
KEY PATTERN: C5, Petersen, AND n8 all satisfy F = D/5 EXACTLY (beta=e/5: 1/5, 3/15, 2/10); C7 has F<D/5.
So the a=1/5 a-term saturates on the entire F=D/5 family (=> a-term alone gives only the weak edge bound
beta<=e/5), and an additive -kappa*rho cannot sharpen to 2/25 where the a-term is already tight with rho>0.
n8 exact: F-2/25 = (1/5)(D-2/5) = -7/400, rho=3/208 (alpha*=2/13).

CAVEAT (stated to GPT in round 5): n8's rho is the AVERAGE slack at alpha*=min-edge-pressure; n8 is NOT a
joint-KKT maximizer (its slack kernel is irregular, rho_i in {0,1/52}). So (Q) MIGHT be intended only for
joint-KKT maximizers (regular rho), excluding n8 -- but then NRS is circular (need to know maximizer is
C5-type to apply it). Round-5 question to GPT: break the circularity, or give the corrected (Q) whose
equality set is EXACTLY {balanced C5}, not the F=D/5 family.

## Status
delta=0 OPEN. Round-4 sharpened the target to (Q) but (Q) as stated is refuted at n8; the overlap-tax cannot
be additive where the a-term saturates. The hard core remains the SAME rigidity (F>=2/25 => weighted C5 /
Step-2's Gamma=N^2 => C5[q]); no proof. No false closure -- exact test caught the flaw. Round 5 sent.
See [[erdos23-delta0-cut-pressure-rigidity]], [[erdos23-gamma-geodesic-peel-angle]], [[erdos23-agent-channel]].
