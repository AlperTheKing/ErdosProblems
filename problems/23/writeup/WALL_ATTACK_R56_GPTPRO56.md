# WALL ATTACK — R56: rotor exclusion via CROSS-STATE SIGNED-CUT UNCROSSING — branches need not
# coexist in one tuple; final obligation = "independent neutral branches are cross-state
# opposite-corner overweight" (possibly just an API-refactor audit) (GPT-5.6 Pro, 2026-07-12, 11,212 ch)

**[CLAUDE GATE HEADER — the four-corner identity (4) is MY early-campaign 16-case-verified identity;
uncrossing theorem shape matches the compiled BankedWallLP-era surface; no new numerics:**
- **NEGATIVE RESULTS FIRST**: the closed transport ledger telescopes to 0=0 (tautology — audit lemma
  closedDetourTransport_sum_eq_zero only); lex minimality adds no sign around the cycle.
- **THE MECHANISM**: cut loss λ(X) = |B∩δ(X)| − |M∩δ(X)| depends ONLY on the fixed graph+cut, never the
  tuple. Four-corner identity (4): λ(X) + λ(Y) = λ(X∩Y) + λ(X∪Y) + 2μ(X,Y) (μ = signed opposite-corner
  weight). ⟹ negativeSwitch_of_oppositeCorner_overweight: λ(X)+λ(Y) < 2μ(X,Y) ⟹ some S has λ(S) < 0 ⟹
  contradicts genuine max cut. TUPLE-INDEPENDENT.
- **STATE ERASURE**: each neutral branch exports a graph-only prefix payload
  (CheckedNeutralProtectionPrefix: block, prefix mask, branchSupport edges, exact prefix_loss, checker);
  checkCrossStateProtectionFork = same block ∧ distinct support ∧ decide(loss_P + loss_R < 2μ) — soundness
  immediate from (4). Row selection changes collision/eligibility/absorption LABELS, never edge kinds or
  λ/μ. ⟹ **noPositiveDefectSaturatedExclusiveForkRotor PROVED given hcross** (full Lean proof term
  written: extract the fork's two independent branches, apply overweight, uncross, contradict
  hmax.nonnegSwitchLoss).
- **THE AUDIT FORK (the decisive next step — CODE, not theory)**:
  OUTCOME A: the existing coexisting two-prefix checker reads only the two branch payloads + fixed graph ⟹
  compile coexistingTwoPrefix_stateErasure (factoring) ⟹ independentNeutralBranches_crossState_overweight
  follows ⟹ ROTOR EXCLUDED ⟹ **THE FULL R54 DICHOTOMY CLOSES** ("the remaining wall may collapse to an
  API refactor plus the exact uncrossing identity").
  OUTCOME B: it uses joint selected-support facts ⟹ remaining lemma = neutralBranch_prefixBoundary_invariant
  (the branch's prefix boundary certificate survives SCC transport independently of other selected rows) —
  "the first mathematical statement not already reduced to exact integer checking."
- **COUNTERMODEL SHAPE (if erasure fails)**: two neutral branches, no co-absorbing tuple, state-erased
  prefixes FAIL overweight (σ(P)+σ(R) ≥ 2Ω(P,R)), state-dependent boundary cancellations block the old
  checker, all first-divergence halves saturated. Export spec given (prefix masks, σ's, corner
  blue/bad counts, exact margin, per-branch boundary edges, first failed assertion after erasure).
  "No such real configuration is currently known."
- HYPOTHESIS ROLES: positive defect builds the rotor; the EXCLUSION uses only fork + max-cut geometry;
  B-conn/Γ-min/completeness/lex-min are upstream (rotor construction).
- NEXT: TOP = the audit (Codex + me): does the two-prefix/15-mask checker use joint selected-support
  masks? Then Outcome-A refactor or Outcome-B lemma; R57 waits for the audit verdict (falsifier-first:
  code speaks before more theory).**]
