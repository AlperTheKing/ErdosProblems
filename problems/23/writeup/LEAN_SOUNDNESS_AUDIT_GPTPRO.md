# Lean deductive-chain soundness audit (GPT-Pro MAIN, 2026-07-07) — Claude-verified

Adversarial audit of the compiled Lean skeleton (anti-fake-progress check). Transcribed faithfully +
Claude's direct code verification of the key finding.

## Executive verdict (MAIN)
"The compiled Lean skeleton is a GENUINE conditional proof skeleton, NOT a fake proof, provided the remaining
provider packages are instantiated by checker-sound artifacts. The main deductive chain is coherent:
BranchAInputs + BranchBInputs ⟹ row GERSH ⟹ Γ≤N² ⟹ β≤N²/25 ⟹ bipartization. I found NO CONTRADICTION in the
deductive flow, but I do see several points where a theorem can become VACUOUS if a provider field is left as
an arbitrary assumption rather than discharged by a checker or a real theorem. The biggest one is still the
Gamma/GERSH aggregation provider."

## Per-component soundness (all confirmed sound by MAIN)
- Branch A: η≥0, a1Proper, odlFull ⟹ C5RS ⟹ RowGershBound — sound (assuming XMask bound to actual rowSum).
- Branch B: 2ρ_L≤η, rowSum≤N+η/2−ρ_L ⟹ rowSum≤N+η — sound.
- LensGates: sound (oscResidualCloseCert_false proves actual False via triangle/shorterOdd/σ<0/νK<0; no hand-wave).
- OddCyclePacking: sound (with the nodup/disjointness repair; checkOddCyclePacking_sound sound).
- Bank0: sound.

## ⭐ BLOCKER 1 (CLAUDE-VERIFIED) — the GERSH aggregation is an ASSUMED PROVIDER, not compiled
MAIN: "If GammaBetaFacts.gammaUpper_of_all_rows_gersh is not compiled from the row/GERSH identities, the final
β bound rests on an arbitrary [assumption]. Precise target: ∀Q, RowGershBound(Q) ⟹ Γ(G,c)≤N². This is the one
skeleton-level theorem I would audit next."
CLAUDE CODE VERIFICATION (CertGraph.lean):
- gammaOfGD (3354) = (rows.rowList.map (fun Q => (Q.length:ℚ)^2)).sum   [= Γ = Σ ℓ(Q)²]
- totalRowSum (3358) = (rows.rowList.map (fun Q => rowSum G c rows Q)).sum
- RowDBGammaFacts (3363) has FIELDS: gamma_le_totalRowSum : Γ ≤ totalRowSum; totalRowSum_le_N2_of_gersh :
  (∀Q RowInDB → RowGershBound) → totalRowSum ≤ N².  Docstring: "the two summation facts of the archived
  GERSH → Γ ≤ N² reduction."
- gammaUpper_from_all_rows_gersh (3407) proves Γ≤N² := le_trans h.gamma_le_totalRowSum
  (h.totalRowSum_le_N2_of_gersh hGersh) — i.e. purely by le_trans of the TWO FIELDS.
- exists_good_cut_from_providers (3610): hRowsGamma : RowDBGammaFacts := hGammaSel.rowGammaFacts c hc hB —
  the RowDBGammaFacts (hence the two summation facts) is a FIELD of the ASSUMED GammaMinSelectionProvider.
=> CONFIRMED: the GERSH aggregation (gamma_le_totalRowSum + totalRowSum_le_N2_of_gersh) is currently an
ASSUMED PROVIDER (M6-level), NOT compiled from the token-charging / LRS identities. This is the biggest
remaining COMPILED-LEMMA obligation. Per the anti-fake-progress gate, M6 must advance via compiled lemmas.

## MAIN's full defect list (fields that must become checker-sound providers, not arbitrary)
1. Gamma/GERSH aggregation (MOST skeleton-critical — see BLOCKER 1).
2. RowDB/Gamma indexing bridge.
3. A1 six-cone bundle (Codex PMTS cones).
4. ODL full-mask leaf providers, esp. O14 EQ + SIB (Codex chart cover, 45/108 not enough).
5. Branch-B Bank-L / Banked-UPO providers.
6. SimpleGraphCertificatePackage existence for every finite triangle-free graph.
FIXES: (1) confirm BConnected convention (endpoint vs whole blue-graph connectedness); (2) Seed3 semantic
leaves need leaf-specific soundness (BUILT this session: coreODLGoal_of_coneCert etc.); (3) O14 incomplete.

## Bottom line (MAIN, verbatim-faithful)
"The Lean skeleton is NOT fake. The main deductive chain is structurally sound. But the unconditional theorem
is not closed until [the 6 providers] are real, checker-sound providers rather than arbitrary fields... Among
these, the most skeleton-critical audit item is the Gamma aggregation / RowDB indexing bridge."

## Claude assessment (honest, anti-fake-progress)
The audit CONFIRMS the deductive skeleton is genuine (no contradiction; every checker-soundness theorem I
built this session is sound). It also CORRECTS any over-optimistic framing: the skeleton is genuine-CONDITIONAL,
NOT unconditional. The compiled portion is the DEDUCTIVE chain (package ⟹ β≤N²/25 ⟹ FC bridge, sorry-free,
axioms ⊆ {propext,Classical.choice,Quot.sound}). The PROVIDER fields — the GERSH aggregation (biggest), the A1
cones, the ODL leaf/O14 providers, the Branch-B ledgers, and the package-existence — are the M6/M7 obligations
that must be discharged by compiled lemmas + exact-verified certificate artifacts to reach the unconditional
theorem. The GERSH aggregation is the top priority: its math is the LRS certificate family (task #16, proven in
the N≤200 work: Σ T² ≤ Γ(N + N²/25 − m)); it must be COMPILED here to discharge the two summation-fact fields.
Routed to MAIN. NO falsifier — the aggregation is a true fact, just not yet compiled.

## CLAUDE DERIVATION 2026-07-07T06:45Z — the CORRECT aggregation is token-charging Σ(ℓ²−25)≤25η, NOT Σrowsum≤N²
Independent derivation from SIBLING's proven top-level statement (TOPLEVEL_DELTA0_ASSEMBLY): the GERSH
aggregation is  Σ_{f∈M} (ℓ(f)²−25) ≤ 25·η  under ∀f ROWSUM(f)≤N+η. Arithmetic:
  Σ(ℓ²−25) = Σℓ² − 25m = Γ − 25m ≤ 25η = 25·(N²−25m)/25 = N²−25m  ⟺  Γ ≤ N².  (clean, exact)
This is the token-charging: each bad edge f contributes (ℓ(f)²−25) EXCESS tokens charged against the 25η slack.
MISMATCH WITH CertGraph: the CertGraph abstraction is  gamma_le_totalRowSum (Γ ≤ totalRowSum=Σ Q.rowSumQ) +
totalRowSum_le_N2_of_gersh ((∀Q rowSum≤N+η) → Σ rowSum ≤ N²). The correct proven aggregation is Σ(ℓ²−25)≤25η,
which does NOT obviously equal Σrowsum≤N² (naive Σrowsum ≤ m(N+η) = N³/25 > N² at extremal). So EITHER:
 (a) Q.rowSumQ is specially defined so Σ Q.rowSumQ encodes the token budget (then abstraction OK, but rowSumQ
     def must be checked), OR
 (b) the CertGraph two-field abstraction is INCORRECT and should be RESTATED to the clean token-charging form:
     replace totalRowSum_le_N2_of_gersh with  (∀Q RowGershBound) → Σ(ℓ²−25) ≤ 25η  [equivalently Γ ≤ N²],
     which IS the proven LRS/token-charging (task #16) and satisfiable.
RECOMMENDED FIX (pending MAIN): compile the aggregation directly as gammaUpper via Σ(ℓ²−25)≤25η ⟺ Γ≤N², using
the per-row excess-token charging map (the LRS certificate), NOT the Σrowsum≤N² field. This is satisfiable and
matches the proven math. MAIN resolving the satisfiability + formalization now.

## ⭐ RESOLUTION (MAIN, 2026-07-07) — DESIGN BUG CONFIRMED + CORRECTED FORM + Claude COMPILED the reduction
MAIN verdict (verbatim-faithful): "The two current fields gamma_le_totalRowSum / totalRowSum_le_N2_of_gersh are
NOT sound as literally typed if totalRowSum = Σ_Q rowSum(Q) over one row-object per bad edge. Your falsifier is
correct: rowSum(Q)≤N+η only gives Σ rowSum ≤ m(N+η), which can be much larger than N². The current
RowDBGammaFacts design is potentially unsatisfiable or mathematically wrong. THIS IS A DESIGN BUG. Do NOT keep
the current pair. The correct aggregation target is Σ_Q (ℓ(Q)²−25) ≤ 25η, i.e. Γ = 25m + Σ(ℓ²−25) ≤ 25m+25η=N²."
CORRECTED CertGraph design (MAIN):
- def lengthSurplusGD (rows) := Σ_Q (ℓ(Q)²−25).
- theorem sum_sq_eq_25_len_plus_surplus (l) : Σℓ² = 25·|l| + Σ(ℓ²−25) [list induction].
- theorem gamma_eq_25m_plus_surplus (hlen: |rowList|=badCount) : gammaOfGD = 25m + lengthSurplusGD.
- CORRECTED RowDBGammaFacts: DROP gamma_le_totalRowSum + totalRowSum_le_N2_of_gersh; ADD
  lengthSurplus_le_25eta_of_gersh : (∀Q RowInDB → RowGershBound) → lengthSurplusGD rows ≤ 25*etaQ G c.
  Keep rowList_length_eq_badCount, betaVal, beta_eq_badCount.
- theorem gammaUpper_from_lengthSurplus (h)(hGersh) : gammaOfGD ≤ N² [via gamma_eq_25m_plus_surplus +
  unfold etaQ + nlinarith].
- CORRECTED gammaBetaProvider_of_rowDB uses gammaLower_from_rows_length_ge_five + gammaUpper_from_lengthSurplus.
CLAUDE COMPILED the REDUCTION (commit 2c0cfebd5, GammaAggregation.lean, 13th green increment, axioms clean):
lengthSurplusGD + sum_sq_eq_25_len_plus_surplus + gamma_eq_25m_plus_surplus + gammaUpper_from_lengthSurplus
(coverage + lengthSurplus≤25η => Γ≤N², via etaQ ring + linarith). FIRST-TRY GREEN.
REMAINING aggregation obligation: (a) the token-charging lengthSurplusGD ≤ 25η from the per-row GERSH bounds +
the LRS charging map (task #16, PROVEN math; needs compiling as a provider — the ONE substantive assumed field);
(b) GRAFT the corrected RowDBGammaFacts into CertGraph (replace buggy pair, update gammaBetaProvider +
gammaUpper_from_all_rows_gersh) — assembly-time surgical fix, careful re downstream (heavy CertGraph rebuild).
=> The anti-fake-progress gate WORKED: caught an unsatisfiable "compiled aggregation" field, fixed the reduction.

## ⭐ AGGREGATION FIXED + COMPILED as CHARGE CERT (MAIN design + Claude build 3ed7f8b79) — anti-fake-progress WIN
MAIN gave the token-charging as a length-surplus CHARGE CERTIFICATE (Positivstellensatz), and the minimal graft.
CLAUDE BUILT it GREEN (GammaAggregation.lean, commit 3ed7f8b79, 14th increment, axioms clean, first-try):
- rowGershSlack Q := (N+η)−rowSum Q; rowGershSlackList; ratDot; lengthSurplusTarget := 25η−lengthSurplusGD.
- structure LengthSurplusChargeCert { coeffs : List ℚ, residual : ℚ }.
- checkLengthSurplusChargeCert := 0≤residual && coeffs.all(0≤·) && coeffs.length=rowList.length &&
  (lengthSurplusTarget = residual + ratDot coeffs rowGershSlackList)  [exact rational identity].
- ratDot_nonneg (induction) + lengthSurplus_le_25eta_of_charge (cert + per-row GERSH => lengthSurplus≤25η) +
  gammaUpper_from_chargeCert (coverage + cert + GERSH => Γ≤N²). ALL GREEN.
=> The deep GERSH aggregation is now a COMPILED PROVIDER consuming an EXACT-VERIFIABLE certificate (a_Q, R) —
the anti-fake-progress-compliant form. No longer an assumed/unsatisfiable field.
GRAFT PLAN (MAIN, minimal blast radius): replace RowDBGammaFacts buggy pair with the charge cert (or
lengthSurplus_le_25eta_of_gersh backed by it); rewire gammaUpper_from_all_rows_gersh -> gammaUpper_from_chargeCert;
update gammaBetaProvider_of_rowDB (gammaLower via length>=5, gammaUpper via charge cert). exists_good_cut_from_
providers: no logical change (type update). GoodCutData / Delta0CertBundles / A1ProperWrapper / ODLFull: NO CHANGE
(consume row GERSH + ODL, not Gamma internals). => heavy CertGraph rebuild but contained blast radius; DEFERRED
to a focused window (mechanical wiring).
REMAINING aggregation: (a) Codex emits the charge cert (a_Q coefficients + R residual) for real graphs from the
LRS reduction (task #16 proven math -> the exact linear-charge coefficients); I exact-verify via the checker.
(b) The CertGraph graft (wire in). CAVEAT (MAIN, truncated): does a valid (a_Q,R) charge cert ALWAYS exist
(completeness of the linear charge form)? — the LRS quadratic may need care; retasked MAIN.
