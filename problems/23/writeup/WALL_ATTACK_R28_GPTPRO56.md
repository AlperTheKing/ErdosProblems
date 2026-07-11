# WALL ATTACK — R28: 2,928-vtx REALIZABLE falsifier of (16)/killer-row/indicator-bound;
# weakest statement (scoped-score one-row descent) NOT settled on it — the decisive open check
# (GPT-5.6 Pro, 2026-07-11; converges with Codex's independent N11 2A+2S falsification)

**[CLAUDE GATE HEADER — construction + numbers recorded; MY independent gate QUEUED (large):**
- **CONSTRUCTION (N=2928, |B|=7025, |M|=1380, |E|=8405)**: t=26 double-star traffic block (hubs r,cL,cR;
  26+26 leaves; 676 rows ℓ-cL-r-cR-r′), 1352 lock arms + anchor (block maxcut 4110 by 16·27² table);
  selector vertex q + 676 selector C5 rows putting EVERY lock vertex into the selected union (blocks
  pattern 4); the verified 28/27 circuit at offset 2761 (minimal defect-one, SDRs); GRAFT = four I-edges
  r-56, 56-m, cL-m, cR-m (m = circuit midpoint) joining hubs to the circuit in ONE active component
  WITHOUT row co-occurrence. Maxcut 7025 EXACT (4 disjoint classes: 4110 + 676·4 + 207 + 4); Γ = 34500
  min; tri-free (checker: 0 triangles); row-count histogram NOT singleton (676 atoms with 1356 rows each).
- **VERDICT**: scoped Hall fails exactly — W = hubs: D(W) = 19950 vs Reach₄(W) = 17235 (sameFirst, after
  3 reservations) + 0 (commonBad) + 2600 (rowCompanion) + 0 (pattern 4 — anchor/lock attachments avoid
  hub companions) = 19835, **gap 115**; hfar holds (unique active atom f* = (2761,2765) at internal
  distance 12); **ZERO ρ=3 pairs** ⟹ outcome (i): scopedHallFailure_has_radiusThreeProducerBridge FALSE,
  alternatingProducerIndicatorBound FALSE, no ScopedInternalKillerRow (by the hfar normal form).
- **THE BLOCKED-SPLICE MECHANISM (14)**: all four graft edges uv have Comp_ω(u) ∩ Comp_ω(v) = ∅ — the
  splice input ("adjacent active vertices whose producer rows share a companion") does not exist across
  the cable; tri-freeness controls a splice only ONCE a shared companion exists; minimality controls only
  circuit-internal latent producers. First graph-REALIZABLE blocked-splice configuration.
- **NOT SETTLED (GPT verbatim)**: "It does not settle whether some other Hamming-one row replacement
  lowers obligationScore." ⟹ THE DECISIVE CHECK: does the 2928 cage admit a one-row scoped-score descent?
  (Double-star atoms have 1356 alternative rows each — rerouting one row off the hubs plausibly drops
  collision mass; must be computed exactly.) Codex's theorem-of-record
  RealHallFailureHasScopedScoreOneRowDescent (8224/8224 through FULL N12) is UNTOUCHED by R28 so far.
- Claimed SHAs: py c50dc4f9…, json 0665ff9c… Lean falsifier statement shape given.
- RECONCILIATION: R28 (2928, hfar, ρ=3-free) + Codex (2 × N11 2A+2S) independently kill R25/R26-strong;
  survivor chain = ScopedAbsorbingInternalRow (422/422) ⊃ scoped-score one-row descent (8224/8224 N≤12).
  DEAD-LIST ADDITIONS: radius-3/(16); ≥3A internal killer; alternatingProducerIndicatorBound.
- NEXT: (i) Codex = run the descent gate on 2928 FIRST (mandatory fixture; rebuild from spec + SHAs);
  (ii) my independent 2928 gate next tick; (iii) R29 = prove-or-falsify the SURVIVING statement on 2928
  (if a descent exists, WHY always — the mechanism visibly differs from splices; if none, the route
  pivots again).**]
