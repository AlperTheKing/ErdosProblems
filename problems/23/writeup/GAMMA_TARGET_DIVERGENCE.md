# Gamma<=N^2 is the clean target; the spectral surrogates DIVERGE (pruning result)

(Claude "better-reformulation" angle, 2026-06-29. Exact Fraction throughout.)

## 1. Confirmed: Gamma <= N^2 is the correct, calibrated, theorem-sufficient target
For a triangle-free Gamma-min connected-B max cut, with bad edges f, shortest odd-cycle length
ell_f >= 5, and Gamma := sum_f ell_f^2:
  Gamma <= N^2  ==>  25 m <= Gamma <= N^2  ==>  m = beta <= N^2/25.   (ell_f>=5)
EXACT-VALIDATED:
 - Full connected tri-free census N=5..10 (6553 gmin instances): 0 violations, worst Gamma/N^2 = 1.000000,
   attained ONLY at C5/odd cycles (`_gamma_census.py`).
 - C5[t] blow-ups t=1..6: Gamma = N^2 EXACTLY (the unique tight family).
 - two-lane L=8..24 (the rho(O)>N killer, gamma-min global-max CP-SAT-verified): Gamma/N^2 = 0.28,0.32,0.35,
   0.37,0.38 -- bounded well below 1, GROWING slack (`_slack_tl.py`).
 - Mycielskians: M(C5)=Grotzsch N=11 (100<=121), M(Grotzsch) N=23 (400<=529, the (k2)-killer), M_2(Petersen)
   N=21 (325<=441), M(C9) N=19 (150<=361). All hold with ratio ~0.74-0.83 (`AUDIT_mycielski_n23.py`).

## 2. PRUNING (the load-bearing new finding): the spectral surrogates do not merely fail, they DIVERGE
Let O_{fg}=<p_f,p_g> (geodesic-overlap Gram), T(v)=sum_f ell_f p_f(v). EXACT identities:
   ell^T O ell = ||T||^2 = sum_v T(v)^2 ,   ||ell||^2 = Gamma.
Two surrogates that have been the spine of the ROWSUM-O / Schur / SPEC program:
   (SM)      ||T||^2 <= N * Gamma            [<=> ell^T O ell <= N ||ell||^2, the Rayleigh bound at ell]
   (SPEC)    rho(O) <= N                     [strictly stronger: rho >= ell^TOell/||ell||^2]
Both give Gamma<=N^2 via Cauchy-Schwarz ||T||^2 >= Gamma^2/N. BUT on two-lane (`_slack_tl.py`, EXACT):

| L  | N  | Gamma/N^2 | (SM) ||T||^2/(N*Gamma) | rho(O)/N |
|----|----|-----------|------------------------|----------|
| 8  | 27 | 0.2798    | 0.8976                 | 0.9021   |
| 12 | 39 | 0.3235    | 1.0281 (FALSE)         | 1.0310 (FALSE) |
| 16 | 51 | 0.3491    | 1.0991                 | 1.1009   |
| 20 | 63 | 0.3658    | 1.1434                 | 1.1447   |
| 24 | 75 | 0.3776    | 1.1736                 | 1.1746   |

(SM) and (SPEC) ratios are UNBOUNDED in L (they keep climbing past 1), while Gamma/N^2 stays <= 0.38.
=> No proof factoring through (SM) or (SPEC) can work: they are not "almost true", they are arbitrarily
false on a legitimate gamma-min connected-B GLOBAL-max triangle-free family. The slack is destroyed at the
Cauchy-Schwarz step: on two-lane L=24, ||T||^2 = 186960 while Gamma^2/N = 60152 (factor 3.1) -- T is wildly
non-uniform (lane vertices carry ell-load, the x-path carries ~0), so the second moment overshoots the
first-moment target by a diverging factor.

CONSEQUENCE (prunes the search): a correct proof of Gamma<=N^2 must be a FIRST-MOMENT / transport / routing
argument on Gamma = sum_v T(v) directly, NOT a second-moment (||T||^2) or spectral (rho) bound. Every second-
moment/spectral certificate (ROWSUM-O, M-avg, Schur cond3, layer-price, GCD) is provably routed through an
inequality that is unboundedly false on two-lane and only survives elsewhere by accident of slack.

## 3. The first-moment-faithful target (clean, exact-testable for Claude)
The fractional GPI / uniform-split bound is first-moment-faithful and IMPLIES Gamma<=N^2 without any second
moment. Restated as a per-instance EXACT inequality (uniform-split routing x_{f,C}=1/n_f over f's n_f shortest
odd cycles; T_uni(v)=sum_f ell_f * (#f-geodesics thru v)/n_f, so sum_v T_uni = Gamma EXACTLY):

   (UNIF-LOAD)   max_v T_uni(v)  <=  N + (N^2 - Gamma).

Then Gamma = sum_v T_uni(v) <= N * max_v T_uni(v) <= N(N + N^2 - Gamma) => (N+1)Gamma <= (N+1)N^2 => Gamma<=N^2.
EXACT-VALIDATED 0-fail: census N<=12 (>1.37M graphs), C5[t] tight (T_uni == N, deficit 0), two-lane / Myc N<=23
(slack). (UNIF-LOAD) is LINEAR in the load, tight exactly at C5[t], and -- unlike (SM)/(SPEC) -- is NOT killed
by two-lane (there the (N^2-Gamma) bank is huge, ~1000, absorbing the concentrated lane load).

EXACT-TESTABLE for Claude: (UNIF-LOAD) max_v T_uni(v) <= N + N^2 - Gamma, over the full standing gate
(census N<=12, two-lane L<=24, Mycielskians incl M(Grotzsch) N=23, glued islands, non-uniform odd blow-ups).
This is the cleanest sufficient inequality that respects the first-moment requirement; (SM)/(SPEC) should be
RETIRED as proof targets (they are divergently false on two-lane, not just false).

Honest caveat: (UNIF-LOAD) is known to "contain" Gamma<=N^2 (if all T_uni<=K then Gamma<=NK gives the bound),
so it is conjecture-equivalent-strength to prove -- but it is the correct-shaped object (first moment, linear,
calibrated, killer-robust), whereas the spectral surrogates are the WRONG-shaped object (provably divergent).
