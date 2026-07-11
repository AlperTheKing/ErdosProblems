# WALL ATTACK — R29: 2928 descends (20611→7101, exact best-of-728); BUT Hamming-one descent
# FALSIFIED in general — 2,943-vtx strict local-min cage (gap 28, all 459,004 replacements ascend)
# (GPT-5.6 Pro, 2026-07-11)

**[CLAUDE GATE HEADER — BOTH claims queued for my/Codex/workflow gates; claimed SHAs
57a3ab46… (2928 best-descent) and 00186166… (2943 CE):**
- **2928 RESOLVED**: score 20611 (hubs 3·6651 + leaf 200 + circuit path 458); best Hamming-one
  replacement = reroute atom (3,29) through the graft: Q = (3, 56, 2763, cR, 29) — turns 3 graft I-edges
  into row edges, deactivates r/cR/leaf subtree, new score 7101 (Δ = 13510); exhaustive: only 728
  candidate rows touch the attachment tree; minimum 7101 attained by 26 choices. So the theorem-of-record
  SURVIVED there.
- **2943 COUNTEREXAMPLE (kills Hamming-one form as stated)**: same t=26 traffic block but TWO separated
  selectors q_L/q_R (left/right lock regions disjoint) ⟹ NO cross route ⟹ all 676 double-star atoms have
  UNIQUE rows; stable 6-edge cable r-a, a-m, cL-zL, zL-a, cR-zR, zR-a (a, zL, zR put in selected union by
  3 private C5s) keeps hubs in ONE 2775-vtx active component but creates no new length-4 rows. N=2943,
  |E|=8422, |B|=7039 (maxcut EXACT by 5-class decomposition 4110+2704+12+207+6), Γ = 34575 min; row
  histogram: 707 rigid atoms (676 double-star + 28 circuit + 3 cable-seed) + 676 selector atoms with 680
  rows each. Scoped Hall: W = hubs, demand 19953 (incl 3 HitNeed), reach 17325 + 2600 = 19925, **gap 28**.
  Score 30811 (hubs 19953 + 52 leaves 10400 + circuit 458). EVERY nontrivial replacement is a selector
  replacement; each has Q∖P ≠ ∅ and any new vertex v (previously in exactly one row) gains diagonal
  collision n(v,v) = 2 ⟹ ≥ +2 halves; positive-score vertices all stay active (≥18 of 26 lock arms per
  leaf survive; cable/circuit untouched) ⟹ min over all 459,004 replacements = **30813** (sharp witness
  given) > 30811. Lean falsifier shape realHallFailureHasScopedScoreOneRowDescent_false given.
- **GPT's OWN CLOSING**: the smallest unrefuted statement = UNBOUNDED simultaneous trade
  (¬Hall ⟹ ∃ ω′ with lower score, no Hamming radius); "any surviving descent proof must coordinate
  several selector rows at once."
- **MY RECONCILIATION (critical)**: the compiled minimum-to-Hall wrapper needs descent only AT GLOBAL
  MINIMIZERS. The 2943 tuple is a strict LOCAL minimum — the wrapper survives IF the GLOBAL minimizer of
  the scoped score passes Hall (Codex census: 0 failing minimizers through FULL N=12). Key open question
  on 2943: do JOINT selector trades restructure I_ω enough to split the active component (deactivating
  hubs ⟹ score collapse below 30811)? If yes, 2943 is consistent with the global-minimizer form and only
  the Hamming-one shortcut died. THE STATEMENT OF RECORD becomes: **no Hall-failing tuple is a global
  scoped-score minimizer** (equivalently the unbounded-descent form).
- DEAD-LIST ADDITION (pending gate): Hamming-one scoped-score descent (RealHallFailureHasScopedScore-
  OneRowDescent as stated).
- NEXT: (i) GATE 2943 (Codex TOP lane + my workflow verify stage + my own gate next tick); (ii) on 2943
  compute the GLOBAL selector-trade landscape (is 30811 globally minimal? does some multi-row trade
  deactivate the hubs?) — this decides whether the global-minimizer route survives; (iii) R30 after gate
  data.**]
