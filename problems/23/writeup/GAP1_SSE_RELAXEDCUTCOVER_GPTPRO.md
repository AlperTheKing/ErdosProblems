# gap#1 SSE direct attack — GPT-Pro reply 1 (Fable-5 era): RELAXED CUT-COVER + EXTERNAL-SLACK BANK

*Harvested 2026-07-08 from MAIN thread (chatgpt.com/c/6a4c8b1a-439c-83eb-8f49-427107d01d61), reply to the Fable-5
retask (ASK A falsifier-first + ASK B angle-pick). Verbatim content, ASCII-sanitized (unicode math folded to ASCII;
`[...]` marks reconstructed seam text from overlapping window pulls). Claude verification notes inline as `[CLAUDE: ...]`.*

## Strategic verdict

The remaining theorem should now be attacked as a **minimal Hall obstruction + external-slack discharging** problem.
The failed cut-cover route required off-support congestion = 0 — too strong, dead. The live route is the relaxed
version: off-support congestion is allowed, but it must be paid by the full bank: Door + vertexSlack + C5/base +
Prune. This is the exact bridge between maximum-cutness and the row-subset Hall inequality.

## ASK A — falsifier-first construction attempts (all die the same way)

A deficient violator needs: triangle-free; maximum cut B; reduced minimal-negative-balance cage C; full escape
closure D=C; ell=5 row set S, |S| >= 6; |S| > |E_short(S)|; and no legal full-bank certificate paying the defect.

- **Attempt 1 (endpoint sunflower):** many ell=5 rows share a small central P4 corridor. For U={x_i}:
  |delta_M(U)|=|Y|, |delta_B(U)|=1 unless x_i has >= |Y| cut-neighbors; adding those cut-neighbors either puts many
  more cut edges into the legal support or creates external slack that must be banked. **Dies at: max-cut vertex
  inequality.**
- **Attempt 2 (dummy cut-edges to force max-cutness):** the dummy cut edges either (1) enter shortest supports —
  |E_short| grows, Hall repaired — or (2) stay outside E_short and become exactly the external slack/bank edges
  paying the defect; they also add structure and tend to destroy negative reserve. **Dies at: external slack edges
  ARE the bank.**
- **Attempt 3 (keep all cut edges inside support):** layered C5-book-like constructions — more rows => more endpoint
  cut-neighborhoods => |E_short(S)| grows at least as fast as |S|. Support expansion restored.
- **Attempt 4 (balanced neutral lens with escaping atoms):** the 11-vtx max-cut escaping-atom example is NOT
  deficient (Gamma=75 < N^2=121). Adding ell=5 atoms to create Hall pressure produces: a proper ledger separator,
  OR extra off-support cut edges paying the defect, OR support-union expansion.

**Surviving abstract falsifier must be:** a minimal full-closure ell=5 support hypergraph with |S|>|E_short(S)|,
max-cut external slack present but NOT legally bankable, and no proper ledger separator. That is the precise object
to search for.

**The repeated obstruction:** every attempted Hall-deficient support produces a max-cut compensating cut-edge
surplus OUTSIDE the support. That is not an accident — it is exactly the theorem to prove:
**Hall defect <= external full-bank capacity.** This is the proof skeleton.

## ASK B — primary recommendation: angle (3), corrected = RELAXED cut-cover

### 1. Normalized ell=5 setting
Atom demand = 1, cut-edge capacity = 1 (after dividing by 25). F = E_short(S). Target |S| <= |F|.
Assume def(S) := |S| - |F| > 0.

### 2. Relaxed cut-cover certificate
Finite family of vertex sets U with rational weights lambda_U >= 0 satisfying:
- **Row coverage:** for each row e in S: sum_{U separates endpoints(e)} lambda_U >= 1.
- **In-support congestion:** for each cut edge c in F: sum_{U : c in delta_B(U)} lambda_U <= 1.
- **Off-support load:** for c notin F: r(c) = sum_{U : c in delta_B(U)} lambda_U, UNCONSTRAINED.

Summing max-cut inequalities:
```
|S| <= sum_U lambda_U |delta_M(U)|          [each covered row is monochromatic, separated => in delta_M(U)]
    <= sum_U lambda_U |delta_B(U)|          [compiled MaxCutVertexIneq, weighted]
     = sum_{c in F} congestion(c) + sum_{c notin F} r(c)
    <= |F| + sum_{c notin F} r(c)
==> def(S) <= sum_{c notin F} r(c) = externalLoad.
```
[CLAUDE: verified the chain — row coverage gives |S| <= sum_e sum_{U sep e} lambda_U <= sum_U lambda_U |delta_M(U)|
since a separated monochromatic edge lies in delta_M(U) and delta_M can only be bigger; the rest is edge-side
re-summation + congestion <= 1. SOUND, Lean-formalizable over the compiled deltaM_card_le_deltaB_card.]

So the Hall defect is exactly paid by external cut-edge slack. **This fixes the failed cut-cover route** (which
demanded r = 0; atom (5,9) killed it).

### 3. Full-bank assignment of external slack
Route each off-support load 25*r(c) to legal sinks: q(c,sink) >= 0, sum_sink q(c,sink) = 25*r(c),
sum_c q(c,sink) <= cap(sink). Legal sinks: **Door** cap 25*sigma; **VertexSlack v** cap = available part of
max(0, N - T(v)) (c may use v only if incident/available per rowDB); **Base/C5** independent base-density tokens;
**Prune** cap = Balance(D) of strict proper descendants. If the assignment exists, the defect is absorbed WITHOUT
the top cage's eta_C.

### 4. Lean-ready chain
- 4.1 `maxcut_weighted_cut_sum`: sum_U lambda_U |deltaM(U)| <= sum_U lambda_U |deltaB(U)| (multiply compiled
  unweighted ineq by lambda_U >= 0, sum).
- 4.2 `RelaxedCutCoverCert` (cuts : Array VertexSet, lambda : Array Rat) + checker (coverage >= 1, congestion <= 1)
  + `relaxedCutCover_defect_bound`: check + max-cut ==> (|S| - |E_short(S)| : Rat) <= sum externalLoad.
- 4.3 `ExternalSlackBankCert` (flows) + checker (per-edge routing exact, per-sink cap, q >= 0, sinks legal) +
  `externalSlackBank_sound`: 25 * sum externalLoad <= DoorCap + VertexSlackCap + BaseDensityCap + PruneCap.
- 4.4 `ell5_hall_absorbed_by_relaxed_cutcover`: both checks + max cut ==>
  25|S| <= 25|E_short(S)| + DoorCap + VertexSlackCap + BaseDensityCap + PruneCap.

### 5. Why better than the dead routes
mQ/T^2 too strong (sunflowers); C1P false; strict cut-cover required separating cuts using only support edges;
relaxed cut-cover exactly matches maximum-cutness — support congestion handles E_short, off-support congestion
becomes full-bank slack. The correct Farkas/discharging formulation.

### 6. THE remaining open core (single theorem)
```
theorem Ell5FullBankRelaxedCover_exists
    (rowDB : RowDB) (C : TerminalCage) (S : RowSet)
    (hMin : MinimalNegBalance rowDB C) (hReduced : ReducedShell rowDB C)
    (hFullClosure : FullEscapingClosure rowDB C S)
    (hS : S subseteq Ell5Atoms rowDB C) :
    exists cover bank,
      checkRelaxedCutCover rowDB S cover = true /\ checkExternalSlackBank rowDB S cover bank = true
```
A certificate-construction theorem with exact algebra. Everything else is algebraic soundness.

### 7. Gating recipe
For every candidate S: solve the relaxed cut-cover LP (coverage >= 1, support congestion <= 1, MINIMIZE external
load) over a cut family (all quotient cuts + endpoint/ball/lens cuts; escalate to all vertex sets if needed); then
solve the external-slack assignment LP into legal bank tokens. Both pass => emit certificates. A TRUE obstruction =
no relaxed cover + bank certificate — not merely Hall defect.

### 8. Counter-schema (decisive abstract falsifier, sharpened)
1. ell=5 row set S with support Hall defect; 2. EVERY relaxed cut-cover of S creates external loads that cannot be
assigned to legal full-bank sinks; 3. no proper ledger-separating subcage; 4. no base leaf; 5. max-cut inequalities
hold; 6. Balance(C) < 0. "Much sharper than before."

## Final answer (GPT-Pro)
Primary = angle (3) as relaxed cut-covers + external slack charged to the full bank; matches the compiled max-cut
capacity lemma; Lean-checkable certificate route. **The one theorem: `Ell5FullBankRelaxedCover_exists`.**

## [CLAUDE next actions]
1. EXACT LP GATE (falsifier-first annotation): census Gamma-min max cuts + C5[t] + odd cycles + 11-vtx
   counterpattern — per component, S = all ell=5 atoms, cut family = singletons + endpoint pairs + balls +
   quotients; solve exact rational LP min externalLoad; check 25*minLoad vs legal bank caps. Overflow on a real
   tight config = diagnostic that the existence proof MUST use the obstruction hypothesis (not route-death — real
   graphs never have defect); fit everywhere = consistency annotation.
2. LEAN: formalize 4.1 (weighted sum, direct from MaxCutVertexIneq) + the 4.2 defect-bound soundness as the next
   axiom-clean increment (abstract Finset/Rat level first, rowDB later).
3. Retask GPT-Pro on the existence proof for structured cut families (quotient+ball) vs the counter-schema search.
