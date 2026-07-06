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

## Charge-cert COMPLETENESS verdict (GPT-Pro MAIN, 2026-07-07 reply; Claude-gated)
DECISIVE. Two meanings of "complete":
1. With a FREE rational residual R, the linear charge cert is TRIVIALLY complete whenever the
   target is true: set a_Q=0, R = 25eta - lengthSurplus; the checker verifies R>=0 directly.
   SOUND, but this is a DIRECT exact certificate of the final aggregation inequality — NOT a proof
   extracted from the LRS/GERSH mechanism. It degenerates into checking the final target directly.
2. As a genuine question — "is 25eta - Sum(ell^2-25) >= 0 always a LINEAR consequence of ONLY the
   row-GERSH slacks (N+eta - rowSum(Q) >= 0) with nonneg coefficients?" — the answer is NO. The row
   slacks are linear in rowSum; the target is a length-surplus (quadratic) expression. From those
   slacks ALONE one gets at most the WEAKER implication Gamma <= N(N+eta), NOT Gamma <= N^2.
   Claude's satisfiability concern was CORRECT.

THE FIX (typed residual dictionary): the residual must NOT be a free rational; it must be a typed
dictionary, each kind BOUND to a specific proven quantity and checked nonneg:
  inductive LengthChargeResidualKind | raw | lrs | cauchy | bankReserve | custom (id:Nat)
  structure LengthChargeResidual where kind; value
  checkLengthChargeResidual: match kind with
    | raw         => decide (0 <= value)                                  -- finite-instance direct only
    | lrs         => decide (value = [LRS quantity]) && decide (0 <= value)
    | cauchy      => decide (value = [Cauchy/SOS quantity]) && decide (0 <= value)
    | bankReserve => decide (value = [exact Row/Gamma reserve residual from LRS->bank proof]) && decide (0 <= value)
    | custom id   => checkCustomLengthResidual ...
KEY MATH POINT (verbatim-faithful): "LRS plus plain Cauchy alone is not enough; the real proof must
contribute an additional nonnegative reserve residual." The token-bank RESERVE residual is the
missing piece; its formula depends on the final LRS->bank proof.

RECOMMENDATION TO CODEX: change the emitter to emit not just row-slack coefficients but ALSO the LRS
residual coefficient(s), Cauchy/SOS residual coefficient(s), and the bank-reserve residual(s); raw
residual only for a final finite-instance direct certificate, not as the universal proof mechanism.

ACCEPTABILITY: keeping the simple/raw cert IS acceptable if the proof architecture is explicitly
"certified-per-instance final aggregation," NOT a compiled LRS aggregation theorem. Given the /goal
(universal, compiled M6 provider; anti-fake-progress gate), MAIN would NOT rely on raw-residual-only
as the universal story.

## Claude honest-status delta (2026-07-07)
- My 14th-increment LengthSurplusChargeCert is SOUND (soundness unconditional: R>=0 + identity =>
  target>=0 => Gamma<=N^2) but, with a free residual, degenerate-capable (per-instance target check).
- COMPILED (this session, 15th increment): the typed-residual upgrade (LengthChargeResidualKind +
  ResidualFormulas carrier + checkLengthChargeResidual + checkLengthChargeResidual_nonneg +
  LengthSurplusChargeCertV2 + checkLengthSurplusChargeCertV2 + lengthSurplus_le_25eta_of_chargeV2 +
  gammaUpper_from_chargeCertV2). Forces each residual NAMED (lrs/cauchy/bankReserve) and nonneg; raw
  reserved for finite instances. Soundness stays unconditional.
- STILL CERTIFIED-PER-INSTANCE, NOT COMPILED-UNIVERSAL: the named residual VALUES (lrsVal/cauchyVal/
  bankReserveVal) and their nonnegativity are supplied per-instance by the exact-verified LRS
  certificate (task #16). A fully compiled universal aggregation would additionally require compiled
  Lean theorems `0 <= bankReserveVal G c rows` (the token-charging reserve nonneg) — the deepest
  remaining M6 obligation, currently discharged by exact-verified artifact rather than compiled proof.
  THIS IS THE HONEST BOUNDARY between "certified" and "compiled" for the single deepest aggregation node.


## Bank-reserve residual — TWO-SOURCE decisive verdict (MAIN + SIBLING independent, 2026-07-07 ~09:15)

BOTH GPT-Pro threads, independently, reached the SAME conclusion. Claude-gated.

### The verdict (both agree)
- There is NO non-tautological closed-form `R_bank = bankReserveVal(G,c,rows)` depending only on the
  scalars {N, m, eta, ell(f), ROWSUM(f)}. The bank reserve is a CERTIFICATE-LEVEL object, not a scalar
  function of row lengths/maxima. Setting bankReserveVal = 25eta - lengthSurplus is sound but tautological
  (a direct target certificate, not a compiled consequence of LRS).
- CURRENT STATE: CERTIFIED PER-INSTANCE, not compiled-universal. The compiled soundness
  `checkLengthSurplusChargeCertV2 = true => lengthSurplusGD <= 25 eta` is real; but the EXISTENCE of a
  valid V2 certificate for every triangle-free Gamma-minimal max cut is NOT a compiled theorem unless the
  token-charge construction is formalized.

### The precise obstruction (SIBLING, sharp)
Per-row GERSH gives ROWSUM(f) <= N+eta. From these ALONE the strongest uniform scalar aggregation is
`Gamma <= N(N+eta)`, NOT `Gamma <= N^2`. The missing gap is EXACTLY `N*eta`. It cannot be recovered from
the row-GERSH slacks alone: every slack term has the form `(N+eta) - ROWSUM(f)` and any nonnegative
combination carries a positive eta coefficient, so no nonneg combo removes the residual `N*eta`. The
token-charge witness is what absorbs that gap. (This is the same fact that made the original CertGraph
two-field design `Gamma <= sum rowSum <= N^2` unsatisfiable.)

### The token-charge certificate structure (SIBLING explicit — matches MAIN's BankReserveTokenCert)
The exact LRS/token artifact contains, per instance:
- token set T(f) for each bad edge f, with |T(f)| = ell(f)^2 - 25
- row-GERSH charge weights c(t,g) >= 0 assigning token t to the row-slack of bad edge g
- LRS residual atoms r_a^LRS >= 0 ; Cauchy residual atoms r_b^Cau >= 0 ; bank residual atoms r_c^bank >= 0
- the EXACT identity:
    25*eta - sum_f (ell(f)^2 - 25)
      = sum_a r_a^LRS + sum_b r_b^Cau + sum_c r_c^bank + sum_g C(g) * ((N+eta) - ROWSUM(g)),
    with C(g) = sum_t c(t,g) >= 0.
Then R_bank = sum_c r_c^bank; its nonnegativity is a FINITE CERTIFICATE (sum of emitted nonneg atoms), NOT
a scalar formula. Cross-check (SIBLING): any claimed scalar R_bank must expand as the sum of emitted
nonneg bank atoms in this identity, else it is not the residual used by the proof.

### Claude reconciliation with the committed Lean V2
`checkLengthSurplusChargeCertV2` ALREADY realizes this structure: its `residuals` list = the lrs/cauchy/bank
atoms (each checked >= 0 by the typed kind), and its `coeffs` list = the charge coefficients C(g) (each
checked >= 0), with the identity `25 eta - lengthSurplus = residualValues.sum + ratDot coeffs rowGershSlacks`.
=> V2 is the CORRECT per-instance token-charge certificate CHECKER; its soundness is compiled; two
independent derivations validate the structure. The token MAP c(t,g) (with |T(f)|=ell^2-25) is finer data
that would make the checker verify the map itself, but the aggregation BOUND needs only nonneg atoms +
charge coeffs + the identity, which V2 has.

### THE remaining gap (deepest node, precisely scoped)
Compiled-universal aggregation requires a Lean EXISTENCE theorem: for every triangle-free Gamma-minimal
max cut, a valid token-charge certificate EXISTS. That is the token-charge CONSTRUCTION (combinatorial
heart), NOT yet formalized. Options: (a) certified-per-instance (Codex emits the atoms+coeffs per graph; I
exact-verify V2) — consistent with the charts/cones architecture but "data" not "compiled lemma" for M6;
(b) formalize the token-charge construction as a compiled Lean theorem `Sum(ell^2-25) <= 25 eta` from GERSH
bounds + tri-free + max-cut. Which is feasible = the decisive open design question routed back to MAIN.
NOT a falsifier (the aggregation is TRUE; task#16 LRS proven); a scoped formalization obligation.


## M6 GERSH-aggregation node — DEFINITIVE classification (GPT-Pro MAIN, 2026-07-07; Claude-gated)

MAIN's decisive verdict on the token-charge EXISTENCE construction (the compiled-vs-certified determinant):

### Classification (document this as the honest status of the deepest node)
- **Soundness: COMPILED Lean theorem.** `checkLengthSurplusChargeCertV2 = true  =>  Sum_f (ell(f)^2-25) <= 25*eta`.
  (Committed in GammaAggregation.lean; axioms clean.)
- **Completeness: CERTIFIED PER-INSTANCE** by emitted token-charge certificates (Codex emits the atoms +
  charge coefficients per graph; Claude exact-verifies the identity + nonnegativity via V2).
- **Universal construction: OPEN.** Would require a graph-generic Hall / max-flow / uncrossing theorem
  proving the CANONICAL token network always admits a feasible nonnegative charge. That theorem is exactly
  the missing combinatorial content; it is NOT a consequence of LRS + Cauchy + row-GERSH alone.

### Why LRS + Cauchy are insufficient (MAIN, precise)
Compiled LRS gives `v^T v ... <= Gamma*(N+eta) ...`; Cauchy gives `Gamma^2 <= N * v^T v ...`; together only
`Gamma <= N(N+eta)`. That is weaker than `Gamma <= N^2`; the missing amount is precisely the bank reserve
`= N*eta`. The bank reserve is not a scalar formula — it is the positive remainder produced by the token-
charge construction.

### The compiled-universal Lean shape (MAIN)
    structure CanonicalTokenNetwork (G : GraphData) (c : CutData) (rows : RowDB) : Type where
      tokens : List Token ; rowSlackSinks : List RowId ; residualAtoms : List ResidualAtom
      edges : List TokenEdge ; capacities : List ...
    def canonicalTokenNetwork (G) (c) (rows) (hRows : RowDBFactsGeneral G c rows)
        (hMax : IsMaxCut G c) (hGamma : GammaMinimalConnected G c) : CanonicalTokenNetwork G c rows := ...
    theorem canonicalTokenNetwork_feasible ... -- HARD: the network always has a feasible nonneg charge
The successful c(t,g) / atom choices are currently INSTANCE-SENSITIVE (the emitted cert records them for
that instance); a compiled theorem must prove a canonical RULE always finds them. That rule is not yet
specified.

### Is it non-finitary? NO (MAIN)
Not in principle: the graph is finite and a canonical max-flow/Hall construction COULD be formalized. But
it is not currently graph-generic — the emitted token certificates are finite and checkable, yet their
support/decomposition are instance-dependent. Correct classification: FINITE AND EXACTLY CHECKABLE PER
INSTANCE, not yet compiled-universal without a new Hall/token-network theorem. NOT a falsifier.

### Consequence for the /goal
- Conjunct-3 (M6 via compiled lemmas, never data volume): the aggregation SOUNDNESS is a compiled lemma;
  its UNIVERSAL completeness is currently certified-per-instance (emitted token certs), which the strict
  anti-fake-progress reading treats as data, not a compiled lemma. To fully satisfy, build the
  CanonicalTokenNetwork + canonicalTokenNetwork_feasible Hall theorem (finite, formalizable-in-principle,
  not yet specified). This is the single deepest remaining Lean obligation for a fully-compiled proof.
- SIBLING is attempting the canonical charging invariant constructively — if it produces the canonical
  rule, that is the missing specification MAIN names; then build the Lean network + feasibility theorem.


## Token-charge = a GLOBAL Hall condition (GPT-Pro SIBLING constructive attempt, 2026-07-07; Claude-gated)

SIBLING attempted the canonical token-charge construction directly and hit — and precisely named — a real
GLOBAL DUALITY WALL. This corroborates MAIN's existence verdict from an independent (constructive) angle.

### Finding (verbatim-faithful)
"A clean graph-generic LOCAL token charge does NOT exist in the form requested. The construction hits a
real global duality wall. The obstruction is not the definition of the tokens (that part is canonical);
the obstruction is the step that must prove the chosen token-to-bank assignment has enough GLOBAL CAPACITY.
That step is a Hall/Farkas dual statement over the whole row/cut incidence structure. It is NOT forced by a
finite local rule from triangle-freeness, max-cut, Gamma-minimality, and per-row GERSH alone."

### Canonical token model (the part that IS canonical)
For each bad edge f, L(f)=ell(f); excess to charge = L(f)^2 - 25. Canonical rational token model via row
incidences: p_f(v) = sum_{Q in cyc(f)} Pr(v in Q). Then sum_v p_f(v) = L(f), so L(f)^2 = sum_{u,v} p_f(u)p_f(v);
the length-square mass of f is the rational measure mu_f(u,v)=p_f(u)p_f(v) on ordered vertex pairs, and
Gamma = sum_f L(f)^2 = sum_{u,v} sum_f mu_f(u,v).

### The Hall condition = the true bank-reserve statement
Let T = multiset of excess tokens (union over f of the L(f)^2-25 row-pair tokens + base tokens), and B the
global bank of size N^2-25m = 25 eta. A generic charging lemma needs an ordering with a running occupied
bank B_k, |B_k|>=k. Equivalently, the HALL CONDITION  |S| <= |Gamma(S)|  for every token subset S ⊆ T,
where Gamma(S) = bank units reachable by the charging rule. THIS HALL CONDITION IS THE TRUE BANK-RESERVE
STATEMENT. Local facts certify only PIECES: triangle-freeness prevents certain row lenses/shortcut
triangles; max-cut gives switch slacks sigma(S)>=0; Gamma-minimality gives neutral switch refinements
(K(S)>=0 when sigma(S)=0); row realization semantics gives the p_f / row-sum identities. NONE of these
local facts gives the Hall condition itself — it is global.

### The strongest HONEST would-be lemma = my committed V2
SIBLING's "TokenCharge Farkas Lemma": for the RowDB of a B-connected Gamma-minimal maximum cut, IF the token
artifact emits C(g)>=0 and residual atoms r_lrs,r_cau,r_bank>=0 with the exact identity
  25 eta - sum_f(ell^2-25) = sum r_lrs + sum r_cau + sum r_bank + sum_g C(g)*((N+eta)-ROWSUM(g)),
THEN sum(ell^2-25) <= 25 eta. R_bank = sum_c r_c^bank, nonnegativity checked atom-by-atom.
=> This is EXACTLY the committed `lengthSurplus_le_25eta_of_chargeV2` (checkLengthSurplusChargeCertV2).
SIBLING confirms it is the strongest HONEST compiled lemma; the universal existence of the emitted
coefficients is the global Hall condition, per-instance-certified.

### DEFINITIVE terminal characterization (3 independent derivations agree)
The GERSH aggregation deepest node: SOUNDNESS compiled (V2 = TokenCharge Farkas Lemma). COMPLETENESS
certified per-instance (emitted token certs = per-instance Hall witnesses). UNIVERSAL = a global Hall/Farkas
feasibility theorem (|S|<=|Gamma(S)| for all token subsets), FINITE but NOT local (no rule from tri-free +
max-cut + Gamma-min + GERSH), currently unspecified/unbuilt. NOT a falsifier (theorem true; task#16 LRS
proven; per-instance certs valid). Open question relayed to MAIN: does the PROVEN LRS family (task#16)
already constitute a compiled-universal establishment of this Hall condition, or is it itself a per-instance
certificate family?

