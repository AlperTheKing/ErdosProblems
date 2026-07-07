# O14 STRUCTURAL CHART-COVER (module 29) — GPT-Pro MAIN, 2026-07-07 (17755c in-thread; extract full at build time)

The coverage/assembly theorem conjunct-1 requires, designed STRUCTURAL (not census) — discharges the
"residual infinite obligation" risk flagged as the at-risk node. Split into TWO parts:

## 29A: O14.EQODL1Classifier.lean  (compiled structural classifier, NO emitted data)
- `namespace O14.EQODL1Classifier`; `abbrev ChartCount : Nat := 108`.
- KEY: the classifier is a DECISION TREE over STRUCTURAL ROW DESCRIPTORS, NOT an array of graph instances.
  This is what makes coverage structural rather than a finite census.
- `def natLtB / natEqB (a b : Nat) : Bool` + `natLtB_sound / natEqB_sound`.
- `section StructuralClassifier`: predicate True exactly for equal-length L=5 EQODL1 row instances;
  classifies each EQODL1 instance to one of the 108 canonical charts by structure.
- `ClassifierComplete` = a THEOREM OF CODE (not a certificate field): the decision tree is TOTAL/exhaustive
  over the EQODL1 descriptor space, so EVERY instance maps to some chart. (This is the census-free guarantee.)

## 29B: O14.EQODL1CoverCert  (emitted 108-slot all-or-nothing cover checker)
- `checkEQODL1CoverCert = true` checks the 108 structural charts are ALL present exactly once (all-or-nothing).
- FINAL SOUNDNESS: `ClassifierComplete` (∀ EQODL1 instance mapped to a chart) + `checkEQODL1CoverCert = true`
  ⟹ the ODL goal (ODLFull.CoreODLGoal) holds for an ARBITRARY EQODL1 instance — via PolyCert.ConeCert.sound
  routing each chart's cert. Discharges into module 30 O14.ChartCoverToODLFull → 44 O14.O14ODLFull.

## STATUS / NOTES (Claude)
- Buildable NOW: 29A classifier + ClassifierComplete + 29B checker TYPE (no 108 data needed for the TYPES).
  The 108-slot emitted DATA (which chart each instance routes to) is module 42/43 (108-gated).
- The hard content = proving ClassifierComplete TOTAL over the descriptor space (exhaustive case split). This is
  where "structural not census" lives — must NOT enumerate instances.
- Real API: env-based PolyCert (ConeCert.sound), ODLFull.CoreODLGoal (green). Rat not Q, Nat+bound not Fin.
- Full 18k Lean skeleton in MAIN thread (https://chatgpt.com/c/6a4c8b1a-439c-83eb-8f49-427107d01d61) — extract at build time.
- Priority per audit CONJUNCT4_OBLIGATION_AUDIT_20260707.md: coverage is gap #5; aggregation integration (#1),
  M6 existence (#2), Branch-A leaves (#3), Branch-B stack (#4) rank higher.
