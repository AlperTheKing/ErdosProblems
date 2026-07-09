# WALL ATTACK — GPT-Pro reply 3 (2026-07-09, thread 6a4f4bd6, RELAYED VERBATIM BY USER)

*Question asked (reply-8 retask): W2 rootBlockClosureSeparable_of_minimalFullClosure full proof — (a) escape-chain
invariant precise, (b) proper_if_multiple + where defect-one/footprint-connectivity enter, (c) the four
contradiction outlets mapped to the ten facts, (d) W3 derivation skeleton.*

**[CLAUDE GATE HEADER:**
- **W2-AS-STATED IS FALSE at the abstraction level** — 2-quotient-component counterexample, EXACT-VERIFIED by
  my gate `_claude_w2_ce_gate.py` (closure laws exhaustive, closed-shore inventory, Def(full)=2>0 minimal
  closed deficient, blockClosed fails, 2 disjoint legal roots, crossing step verified). A closure step CAN
  cross from one legal root block to another while the legal sink neighborhoods remain disjoint — the missing
  implication "crossing ⟹ legal components merge" is NOT a consequence of the ten footprint predicates + W1 +
  ordinary cage legality.
- **CRITICAL CAVEAT (mine): the CE is ABSTRACT** — an arbitrary extensive/monotone/idempotent closure operator.
  Whether the REAL forced-ℓ=5-escape closure on real cages admits such a crossing is OPEN and is now the
  decisive question. The route regresses to hypotheses until grounded in the CONCRETE cage model
  (ForcedEll5EscapeStep) — grounding demanded in the next retask; my census falsifier search follows.
- **Tension resolved cleanly**: footprint graph (atoms/short supports) ≠ legal-incidence graph (ports/bank
  sinks). Connected footprint prevents a SUPPORT-side decomposition, not a BANK-SINK-side one. Adopted.
- **New wall dependency list (of record)**: W1 NoUnbankableExposedPorts + ROOT-LOCALITY
  (`EscapeClosureRespectsLegalRoots`, or weaker-for-Hall `PositiveRootBlockClosedExtraction`) +
  `ClosedWeightedHallCompleteness` + `closedRootCut_violates_D1_of_weightedDeficiency` (closed-cut exchange
  identity) + (B) finite-Farkas iff. The four-outlet route additionally needs `firstRootCrossing_outlet`
  (genuine support-geometry theorem; requires the concrete ForcedEll5EscapeStep).
- **Compiled by me on receipt**: `ClosedShoreExtraction.lean` — abstract escape-quotient structure +
  ClosedPortSet/MinimalClosedDeficient + `minimalClosedDeficient_has_unique_root_of_positiveExtraction`
  (unique-root from PositiveRootBlockClosedExtraction + my compiled uncrossing). W3's
  `strictRestrictedDual_gives_weightedRoutingFailure` is pure bookkeeping — next Lean increment.**]

---

## VERBATIM REPLY (user relay)

The requested W2 theorem is false at the stated abstraction level. The failure is not in the Hall algebra; it
is exactly in the missing implication

```text
forced full-escape closure step crossing from one quotient piece to another
⇒ legal-incidence root neighborhoods merge.
```

That implication is not a consequence of the ten footprint predicates, W1, or ordinary cage legality unless
cage legality contains a stronger root-locality of forced escapes axiom.

# 1. Exact W2 counterexample

Satisfies: fullClosure extensive/monotone/idempotent; NoUnbankableExposedPorts; banked sinks only; minimal
closed Hall deficiency; two disjoint legal root neighborhoods — but `blockClosed` fails.

```text
QComp = {A, B};  Port = {pA, pB};  Sink = {sA, sB}
Legal arcs: pA--sA, pB--sB (no cross arcs);  kind(sA)=kind(sB)=door
cap(sA)=cap(sB)=1;  L(pA)=3, L(pB)=1
cl(U) = if A ∈ U then {A,B} else U      (extensive, monotone, idempotent)
exposed(U) = {pA | A ∈ U} ∪ {pB | B ∈ U}
Closed shores: ∅, {B}, {A,B} with exposures ∅, {pB}, {pA,pB}
Def(∅)=0; Def({pB}) = 1−1 = 0; Def({pA,pB}) = 4−2 = 2 > 0
⟹ {pA,pB} is a minimal closed deficient port set with TWO disjoint legal roots
   ({pA}--{sA}, {pB}--{sB}), yet NO closed shore has exposure {pA} — blockClosed FALSE.
The closure step {A} ↦ {A,B} adds pB whose legal neighborhood {sB} is disjoint from {sA}:
the two legal components do NOT merge.
```

# 2. What W2 needs: root-local forced escape

The missing fact is a compatibility condition between the full-escape closure relation and the legal sink
relation — not one of the ten footprint facts. One-step closure data:

```lean
structure EscapeClosureStepData (O) (Q : EscapeQuotientData O) where
  oneStep : Finset Q.QComp → Finset Q.QComp → Prop
  oneStep_extends : ∀ V W, oneStep V W → V ⊂ W
  closure_generated : ∀ V, Q.fullClosure V = sInf {W | ReflTransGen oneStep V W ∧ maximal}
```

Root-locality (relative to a closed ambient shore U and the legal-root decomposition of exposedPorts U):

```lean
structure EscapeClosureRespectsLegalRoots (O) (Q) (Step) : Prop where
  no_hidden_exposure_inside_closed :
    ∀ U V, Q.fullClosure U = U → V ⊆ U → Q.exposedPorts V ⊆ Q.exposedPorts U
  step_new_ports_legal_connected :          -- THE CRITICAL FIELD
    ∀ U V W (closed U) (V ⊆ U) (W ⊆ U) (Step.oneStep V W),
      ∀ p ∈ Q.exposedPorts W, p ∉ Q.exposedPorts V →
        ∃ q ∈ Q.exposedPorts V, ∃ s : O.BankSink, O.LegalSinkPort p s ∧ O.LegalSinkPort q s
  exposure_persistent_along_steps :
    ∀ U V W ..., Q.exposedPorts V ⊆ Q.exposedPorts W
  root_seed_exists :
    ∀ U (closed) (D : RootNeighborhoodDecomposition (exposedPorts U)) (r),
      ∃ V ⊆ U, Q.exposedPorts V = D.ports r
```

`step_new_ports_legal_connected`: a newly exposed port created by ONE forced ℓ=5 escape step shares a legal
bank sink with an already-exposed port (stays in the same legal-incidence component). W1 only says "every
exposed port has SOME legal sink" — strictly weaker (does not put the new sink in the old root neighborhood).

# 3. Correct W2 theorem under root-local forced escape

`rootBlockClosureSeparable_of_rootLocalEscape (Q) (Step) (hRootLocal) : RootBlockClosureSeparable O Q` —
blockClosed via root_seed_exists + Ur := fullClosure V₀ (closed by idempotence, ⊆ U by monotonicity+U closed) +
induction over the finite closure sequence: new ports share a legal sink with old ⟹ same legal component ⟹
stay in D.ports r; persistence handles old ports. proper_if_multiple follows from the decomposition ALONE
(two nonempty disjoint blocks covering exposedPorts U).

**Where defect-one and footprint-connectedness enter**: NOT in proper_if_multiple — only in proving the missing
root-local escape theorem from graph geometry. Two different graphs: support/footprint graph (atoms + short
supports, connected by support overlap) vs legal-incidence graph (exposed off-support ports + bank sinks). A
connected footprint does not imply one legal root component — two support regions can be connected through
short-edge geometry while their exposed ports route to disjoint door/slack sinks (exactly what the CE models).
Footprint connectedness prevents a support-side decomposition; it does not prevent a bank-sink-side one.

# 4. The four "first escape edge" outlets are not derivable yet

The claim "first closure edge leaving a root block produces private-short-edge / size-5 support /
pair-union<5 / proper full-closure Hall violator" needs a forced escape step carrying a short-edge/support
certificate. `FirstRootCrossing` data (V, W, e : ShortEdge; stepLabel : O.ForcedEll5EscapeStep e V W;
before_inside_root; after_crosses_root) and the needed graph theorem:

```lean
theorem firstRootCrossing_outlet (X : FirstRootCrossing O Q Step U D r) :
    O.PrivateShortEdge X.e ∨ O.supportSize X.e = 5
    ∨ (∃ f ≠ X.e, O.supportUnionSize X.e f < 5) ∨ O.ProperFullClosureHallViolator
-- genuine support-geometry theorem; requires the CONCRETE definition of ForcedEll5EscapeStep
```

Then `no_firstRootCrossing` (contradiction with the ten facts) is straightforward. The legal-sink-specific
fact consumed: "a forced ℓ=5 escape step that does not trigger one of the four support outlets must preserve
legal-root component membership" — belongs in cage legality or a new checker theorem. W1 alone is too weak.

# 5. Weaker separability sufficient for the unique-root conclusion

Full RootBlockClosureSeparable is stronger than necessary — enough to realize ONE positive-deficiency root
block:

```lean
def PositiveRootBlockClosedExtraction (O) (Q) : Prop :=
  ∀ L U (closed U) (D : RootNeighborhoodDecomposition (exposedPorts U)),
    0 < deficiencyQ (exposedPorts U) → 2 ≤ card D.Root →
      ∃ r Ur, closed Ur ∧ exposedPorts Ur = D.ports r ∧ D.ports r ⊂ exposedPorts U
        ∧ 0 < deficiencyQ (D.ports r)
```

Then unique-root follows from the compiled uncrossing algebra
(`minimalClosedDeficient_has_unique_root_of_positiveExtraction`: by_contra; card ≥ 1 from nonempty; extraction
gives a proper closed deficient block contradicting MinimalClosedDeficient). The §1 counterexample shows this
hypothesis is genuinely stronger than W1.

# 6. W3: exact derivation of noStrictRestrictedDual_rootedEscape

W3 needs W1 + W2-weak + a quantitative bridge. Four lemmas:

6.1 `SingletonAlmostSqueeze` (theta on singleton cuts, L p := Σ theta·cutPort, alpha_dominated, short_coeff≤1)
+ existence lemma `singletonAlmostSqueeze_exists` from the compiled singleton-domination arithmetic (no η).

6.2 `strictRestrictedDual_gives_weightedRoutingFailure` [BOOKKEEPING]: restricted D1 on singleton cuts +
strictness ⟹ Σ_p L p·γ p > Σ_s cap s·δ s (weighted routing failure).

6.3 `closedWeightedHallDeficient_of_weightedRoutingFailure` — needs NEW hypothesis
`ClosedWeightedHallCompleteness` (weighted deficiency representable by a full-escape-CLOSED shore; ordinary
Hall gives only an arbitrary deficient port set; the §1 CE shows closure can destroy the inference).

6.4 `closedRootCut_violates_D1_of_weightedDeficiency` — the CLOSED-CUT EXCHANGE IDENTITY:
cutAlpha(X) − cutBeta(X) − cutGamma(X) ≥ weightedDeficiency(U) > 0 for the quotient/bank-rooted cut X of a
weighted-deficient closed shore ⟹ restricted D1 fails on X. "Not implied by W2 — the exact quantitative use
of singleton domination plus quotient-cut arithmetic."

# 7. W3 theorem skeleton

Given hAllowed (singleton ∪ quotientClosed ∪ bankRootedClosure), hW1, hW2 = PositiveRootBlockClosedExtraction,
hClosedHall, hExchange, hGeom, α ≥ 0: suppose strict R. Build singleton almost-squeeze Z; get weighted routing
failure; get closed weighted-deficient shore U; CHOOSE U MINIMAL among closed weighted-deficient shores; build
legal decomposition D via W1; if ≥2 roots, hW2 extracts a proper closed deficient block contradicting
minimality; else unique root ⟹ `bankRootedClosureCut_of_uniqueRoot` gives allowed X; hExchange contradicts
R.d1_allowed X. (Quotient-closed cuts serve the γ-free part inside the completeness proof; the deficient
branch normally ends bank-rooted.)

# 8. Final dependency list

Ten facts + W1 do NOT prove W2. Extra needed: `EscapeClosureRespectsLegalRoots` (or weaker
`PositiveRootBlockClosedExtraction`). For W3 additionally: `ClosedWeightedHallCompleteness` +
`closedRootCut_violates_D1_of_weightedDeficiency`. No η anywhere; capacities = door/vertexSlack/C5Base/prune.

**Decisive point: W2 requires a legal-root compatibility theorem for forced ℓ=5 escape closure. The
two-component counterexample is the minimal obstruction: a closure step can cross from one legal root block
to another while the legal sink neighborhoods remain disjoint.**
