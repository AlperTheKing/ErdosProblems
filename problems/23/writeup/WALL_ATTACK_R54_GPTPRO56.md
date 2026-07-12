# WALL ATTACK — R54: CONDITIONAL PROOF OF LexMinSoftcapRigidityOrGlobalC5 — the whole program
# reduces to ONE graph lemma: neutralProtectionFork_hasSimultaneousState (fork synchronization)
# (GPT-5.6 Pro, 2026-07-12; 14,908 ch — full conditional Lean proof skeleton written)

**[CLAUDE GATE HEADER — structure verified by inspection; all steps are checker-shaped; no numerics to gate
beyond the corpus filter (consistent with my/Codex gated fixtures):**
- **FROZEN STATEMENT**: LexMinSoftcap ω = collision-min + defect-min-on-face (lex). Target dichotomy:
  groupedHallDefect ω = 0 ∨ ∃ label : V → Fin 5, checkGlobalC5 = true. **CONSUMER WRITTEN**:
  erdos23_of_LexMinSoftcapRigidityOrGlobalC5 — left branch via SoftEdgeCapGraphAdapter.toCheckedTwoCover +
  CheckedSoftCollisionTwoCover.bound; right via CertGraph.globalC5_bound. 25|M| ≤ N² either way.
- **PROVEN-SHAPE CHAIN** (each a finite checker or compiled-consumer construction):
  (2) positiveGroupedDefect_hasUnitCore — least unmatched obligation + residual alternating closure in the
  grouped network ⟹ |O_K| = cap(S_K) + 1 (unit-defect core; direct consumer of
  MinimumCollisionGlobalHallReduction).
  (3) buildNeutralProtectionSinkSCC — closure under matched-source moves + NEUTRAL protection absorptions
  (collision-minimality forces C(ω′) = C(ω); defect-minimality forces Δ(ω′) = Δ; better-exposing detours
  would contradict minimality) ⟹ finite sink SCC K of neutral states.
  (4) CheckedProtectionQuotient Q_K (blocks = protection segments mod carried/absorption equivalence;
  edges = row/detour adjacency; recomputed, no assumed API).
  (5) neutralProtectionQuotient_minDegree_two — a leaf block yields an unreserved P1/P4 unit (augments —
  impossible in sink SCC) or a used source (expands closure) or a neutral absorption (expands SCC) ⟹ no
  leaves. [= the formal use of "outside detours pay through P1".]
  (7) protectionCycle_length_ge_five (rows map to 5 distinct successive blocks) +
  protectionCycle_length_le_five (q > 5 ⟹ two boundary segments of a row window absorb ⟹ two-prefix gate
  gives σ(S) = −1 ⟹ contradicts max cut).
  (8) protectionCycle_five_to_globalC5 — orientation index = the label; checker verifies consecutive-class
  blue edges + wrap-class bad edges. FINITE CHECKER, not a stability estimate.
  (9) Full conditional Lean proof of the dichotomy given hsync (by_cases + core + SCC + quotient +
  minDeg/maxDeg + connected_twoRegular_toCycle + q=5 + labeling) — WRITTEN OUT.
- **THE ONE UNRESOLVED LEMMA (max-degree ≤ 2)**: neutralProtectionFork_hasSimultaneousState — two distinct
  independent protection branches P ≠ R at one block B of a sink SCC must be SIMULTANEOUSLY absorbed in
  some state (then checkedTwoProtectionPrefixSwitch_sound gives σ = −1 ⟹ contradiction). "Collision and
  defect minimality only say both branches are neutral; they do NOT imply the two row choices can be
  selected simultaneously. The abstract paired-obligation rotors exploit exactly this mutual-exclusion
  loophole." Equivalent global form: positiveLexMinProtectionQuotient_isCycle.
- **K≤3 additive extraction NOT justified** (unit core's alternating closure has unbounded diameter;
  C5[3] six-row trade is the warning) — the correct object is the global neutral SCC, not a bounded core.
- **CORPUS FILTER**: C5[3] (secondary minimizer flows 84/84 ⟹ left branch), N≤12 census (0 failing
  C-min tuples ⟹ left), N=78 rotor (defect 0), t5 support hits (scope-vacuous / fail extension gate ⟹
  never instantiate). NO canonical fixture exercises the positive-defect branch yet.
- **FALSIFIER FORMATS**: (i) dichotomy CE = canonical cage + all C*-tuples' grouped flows + Δ* > 0 + proof
  no Fin-5 label passes checkGlobalC5; (ii) sync-lemma CE = "EXCLUSIVE PROTECTION FORK": sink SCC + quotient
  + block with two independent branches + proof no state absorbs both + all transitions preserve (C*,Δ*) +
  no augmenting source. "This is the exact shape still not found."
- NEXT: R55 = attack the sync lemma (sent); Codex lanes = compile the R54 stack (unit core / SCC / quotient
  / minDeg / cycle-to-C5 — all proven-shape) + engine hunt for the exclusive-fork falsifier (small models
  first: does ANY canonical graph realize a fork?); my mask-diff feeds CheckedTwoProtectionPrefixSwitch.**]


## VERBATIM FULL TEXT (unfiltered innerText capture; unicode-true; Lean blocks exact)
### [slice 1 of 2 follows in the committed file via _r54_verbatim.txt]

