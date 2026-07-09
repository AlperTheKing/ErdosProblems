# O14 module-29 CONCRETE wiring — GPT-Pro design (2026-07-09, post-108/108)

*Reply to the concrete classifier/payload retask. HEADLINE: "Module 29 is now an engineering/transpilation
problem, not a mathematical open node" (verbatim closing line). RESEARCH remaining in module 29: NONE, provided
the chart payloads are Lean-checked. ASCII-sanitized; Claude annotations [C: ...].*

## Build order
`O14/EQODL1Shape.lean` → `O14/Generated/ChartKeys.lean` → `O14/Generated/Classifier.lean` →
`O14/Generated/ChartPayloads/Chart000..107.lean` → `O14/Generated/PayloadRegistry.lean` →
`O14/EQODL1ConcreteCover.lean` — consumed by the already-green `EQODL1CoverInterface`/`EQODL1LeafProvider`/
`ChartCoverToODLFull`.

## 1. Structural classifier
- **Instance type**: classify a CERTIFIED structural instance, not raw graphs. `EQODL1RawInst` (row + row_mem +
  isEQ) + `O14Shape` descriptor (kIdx/dIdx/seedShape/maskCode/orbitCode/routeCode/sigCode : Nat, DecidableEq) +
  `O14Shape.Valid` (bounds from generated `O14Bounds`, NOT hand-guessed — emit from the v108 manifest) +
  `EQODL1ShapeSound` (eq_len5, O14Closed, MaskSound, SeedSound, RouteSound, ScalarSound — the semantic bridge,
  supplied by the route tree / A1MaskSymmetry / Seed3 layers).
- **ChartKeys**: per-chart `domainNNN : O14Shape → Bool` boolean formulas over the descriptor fields (eq / in-list
  / range), generated from the manifest; prefer `inListNat` membership over nested conditionals.
- **Classifier**: `chartOfShape` = generated 108-way if-chain; theorems `chartOfShape_lt`, `chartOfShape_domain`
  (via generated `valid_shape_partition`: Valid ⟹ disjunction of domains), `ClassifierComplete` at instance level.
  All decidable-by-construction/generated case split. **This is finite structural normalization, NOT a census.**

## 2. Per-chart soundness — recommended payload shape
- **NOT external-SHA-only** ("excellent for CI/audit, not a Lean proof") and NOT a generic LP re-solver in Lean.
- **Transpile**: external exact verifier reduces each source_solution manifest to a compact ConeCert/arithmetic
  payload; Lean checks it with small exact-rational checkers; each chart module proves `EQODL1ChartSound i`.
- **Checker style**: chunked exact-rational accumulator lemmas (32 or 64 source records per chunk; per-chunk
  `chunkNNN_ok` by rfl/norm_num/ring_nf; combine into `cone_check : PolyCert.checkConeCert env target cert = true`).
  AVOID: native_decide, one giant norm_num over 1900 terms, one monolithic 108-chart file.
- **Sizes**: 108 charts × ~1700-1900 records ⟹ ~0.5-2.5 MB generated Lean per chart, 60-250 MB total; one module
  per chart compiling to its own .olean; registry imports oleans (light); `fin_cases` dispatcher over Fin 108.
- Dev fast path (`present := true` SHA-pinned) allowed for pipeline bring-up but NEVER final.

## 3. Emitter spec (per chart JSON)
chart_id, sha256, chart_key (field constraints as eq/in/range), target (CoreODLGoal NF + env), certificate
(ConeCert sources with NF + metadata, weights num/den, chunks with expected_nf, target_eq lhs/rhs), stats
(num_sources, max_den_bits). Generates: ChartKeys.lean (domains + bounds + O14ShapeAllowed), Classifier.lean
(chartOfShape + generated finite-case proofs), per-chart ChartNNN.lean (defs + chunk lemmas + cone_check +
chartSound), PayloadRegistry.lean (present + checkEQODL1CoverCert_true + chartSoundOf dispatcher over Fin 108).

## 4. Final cover module
`EQODL1ConcreteCover.lean`: `EQODL1_concrete_chart_sound` (registry dispatch at `chartOf I`) +
`coreODLGoal_of_EQODL1Inst` (ClassifierComplete + chartSoundOf ⟹ ODLFull.CoreODLGoal for the instance's row).

## 5-6. Honest remaining tasks + classification
- BOOKKEEPING (buildable now): O14Shape record, generated ChartKeys/classifier + proofs, registry, dispatcher,
  concrete cover theorem.
- CERTIFICATE TRANSPILATION: the 108 payload modules + chunked ConeCert proof terms + chartSoundNNN. [C: Codex
  lane — emitter implementation from the v108 ledger artifacts.]
- STRUCTURAL NORMALIZATION: EQODL1ShapeSound extraction from Seed3/O14 route data (uses A1MaskSymmetry,
  Seed3Door, route-tree semantics — all compiled). [C: design follow-up with MAIN when the transpiler lands.]
- **RESEARCH: none.**
