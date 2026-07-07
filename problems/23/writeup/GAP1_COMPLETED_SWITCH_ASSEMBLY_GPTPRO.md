# GAP-#1 COMPLETED-SWITCH ASSEMBLY (GPT-Pro MAIN, 2026-07-07, relayed by user) — reduces gap #1 to R1-R4

Gap #1 (aggregation Γ<=N² == reserveResidual_nonneg == TerminalCageReserve) reduces, via the Γ-minimality
contradiction on a minimal-positive-debt zero-slack terminal cage C, to FOUR residual sublemmas:

- **R1 TerminalCage_K2Component_ExhaustiveAccounting**: the sign-atom K2-support-component partition (Xi(C) =
  atoms, edges = shared K2 support; components K2-disjoint) gives a DISJOINT old/new affected-bad-edge accounting
  for the simultaneous completed switch U_C: OldAff(C)=OldPass ⊔ ∪_β Old_β ⊔ ∪_α{e_α,f_α}, similarly NewAff.
  Rules out cross-component new bad edges. (K2-disjointness gives the partition but NOT this by itself.)
- **R2 PositiveDebtImpliesActiveTypeB**: a minimal-positive-debt zero-slack terminal cage has >=1 ACTIVE type-B
  5/7 core component (type-A baggage + passive have nonpositive square balance, so strict drop needs a type-B). |A|>0.
- **R3 CompletedSwitch_NoCrossGammaAccounting**: no uncharged cross-component new bad edge; no old bad edge double-
  counted; outside bad-edge contributions nonincreasing. (=> Γ(B)-Γ(B^U) >= GammaOldAff - GammaNewAff.)
- **R4 CompletedSwitch_DoorQuotientConnected**: simultaneous switch preserves B-connectivity. Cleanest = a checked
  SPANNING TREE T' of B^U_C (every T'-edge a cut edge after switch, T' spans V). Or door-quotient-connected proof.

## Assembly theorem (R1-R4 => gap #1)
CompletedSwitchAssembly: R1-R4 => exists U_C with sigma=0, B^U_C max cut (universal identity |B^U|-|B|=-sigma),
B^U_C connected (R4), and Γ(B^U_C) < Γ(B). Contradicts Γ-minimality => no min-positive-debt zero-slack cage =>
reserve = N²-Γ >= 0 => Γ <= N². CLOSES gap #1.

## The structured integer gate GPT-Pro proposes (per-cage, exact, rational-free)
Data: active atoms alpha (old lengths L_a, L_a+2; new length lnew_a <= L_a); passive matches p (new_p<=old_p);
type-A baggage beta (NewSq_beta <= OldSq_beta). Verify identity:
  GammaOldAff - GammaNewAff - sum_a (L_a+2)^2 = PassiveReserve + BaggageReserve + CoreReserve
  PassiveReserve = sum_p (old_p^2 - new_p^2) >= 0
  BaggageReserve = sum_beta (OldSq_beta - NewSq_beta) >= 0
  CoreReserve    = sum_a (L_a^2 - lnew_a^2) >= 0
Then Γ(B)-Γ(B^U_C) >= sum_a (L_a+2)^2 >= 49*|A| > 0  (EQODL1: L_a=5).

## ⚠ DISCREPANCY vs Claude's gate (CRITICAL - must reconcile before trusting)
Claude's _claude_multiatom_gammadrop_gate.py flips the FULL deficient-cap terminal-shadow set (Sset) and measures
the GLOBAL Γ drop: Γ(B)-Γ(B^U) = +24 (dG=-24) with one active L=5 core, on 42800/42800 switches. But GPT-Pro's
derivation predicts Γ(B)-Γ(B^U_C) >= 49*|A| = 49. Since 24 < 49, EITHER (a) GPT-Pro's "completed switch U_C" is a
DIFFERENT (smaller/canonical per-component) set than Claude's Sset flip - so the two measure different switches, OR
(b) GPT-Pro's ActiveDrop=(L+2)^2 bound is STILL too large for the global drop (the 25=49-24 gap would force a
reserve to be NEGATIVE, violating R3's nonincrease). RESOLUTION PENDING: Claude's distribution run (b0vy6ugez) reports
the dG and |Active(C)| distributions. If |Active|==1 always and dG==-24 always, GPT-Pro's multi-atom concern is moot
AND its 49-bound is wrong for the natural switch (only strict-decrease dG<0 holds). The 49-bound is UNVERIFIED /
suspect; only STRICT DECREASE (dG<0) is gate-validated. GPT-Pro must define U_C precisely so Claude can gate the
STRUCTURED identity (OldAff/NewAff/reserves), not just the global drop.

## STATUS: gap #1 = R1-R4 (all UNPROVEN residual sublemmas). Essential claim (strict decrease) validated 42800/0.
Quantitative 49-bound suspect (Claude gate: global drop 24). Next: reconcile U_C definition + gate the structured
per-atom identity. P(Lean) ~30-40 pending R1-R4 proofs.
