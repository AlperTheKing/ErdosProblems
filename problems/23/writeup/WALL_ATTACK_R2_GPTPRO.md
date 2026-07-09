# WALL ATTACK — GPT-Pro reply 2 (2026-07-09, thread 6a4f4bd6, RELAYED VERBATIM BY USER)

*Question asked (reply-7 retask): Phase-3 closure lemma full proof — (a) precise uncrossing incl sink-cap
double-count, (b) trichotomy exhaustiveness / scattered sinks, (c) THE PATCH RISK (short_coeff saturation),
(d) extra hypotheses beyond the ten.*

**[CLAUDE GATE HEADER — verdicts on receipt:**
- **ROUTE CORRECTION, not wall damage: "I did not find a wall falsifier. I did find two exact falsifiers to
  the proof route as previously phrased."** Both falsifiers EXACT-VERIFIED by me
  (`_claude_porthall_uncross_gate.py`):
  * Falsifier 1 (closure-minimality): 2-port/2-sink instance — P={p1} inclusion-minimal deficient (Def=1>0),
    full-escape closure exposes p2 with zero load and its own root neighborhood; closed set has Def=−99≤0.
    Kills "minimal deficient + closure" as stated AND kills ClosurePreservesDeficiency-as-automatic.
  * Falsifier 2 (add-only patch): saturated short edge (coeff exactly 1) + any ε>0 on a new cut using it →
    1+ε>1. **Confirms exactly my flagged patch-risk (c) — add-only Phase 4 is DEAD.**
- The uncrossing ALGEBRA is sound (my hand-check + exact random gate + compiled): deficiency Def(P) =
  load(P) − cap(legalNbr(P)) is SUPERMODULAR; ADDITIVE on components with disjoint legal sink neighborhoods;
  exact overlap identity Def(P1∪P2) = Def(P1)+Def(P2)+Cap(N(P1)∩N(P2)) for disjoint ports. "Independent root
  neighborhoods" MUST mean disjoint legal sink neighborhoods (else the intersection-capacity term hides
  deficiency). Minimal deficient ⟹ ONE legal component. **I compiled all of this as PortHallUncrossing.lean
  (full proofs, no sorry) same-tick.**
- THE WALL IS SHARPENED to three named obligations + one infrastructure iff (recommended route drops the
  patch machinery entirely):
  * (W1) `NoUnbankableExposedPorts` — every exposed port of a closed shore has ≥1 legal banked sink; NOT
    implied by the ten structural facts (they never mention the legal sink relation); likely graph-derivable
    from cage-legality; else must be ADDED to the obstruction checker.
  * (W2) `RootBlockClosureSeparable` — root blocks of a closed shore are themselves proper closed quotient
    shores (closure of a block cannot cross into another root block without an escape chain joining their
    legal components). **THE genuine combinatorial theorem** — where defect-one, no-private-edge, support
    sizes {4,≥6}, no-size-5, pair-union ≥5, footprint-connected, full-escape-closure, reduced-min-neg-balance,
    cage-legality must be used (`rootBlockClosureSeparable_of_minimalFullClosure`).
  * (W3) `noStrictRestrictedDual_rootedEscape` — no strict RESTRICTED dual over allowed cuts
    (singleton ∪ quotientClosed ∪ bankRootedClosure); the new hard wall theorem; uses the closure lemma;
    never mutates a θ, so short-edge saturation cannot break it.
  * (B) `dualSqueeze_exists_iff_no_restrictedStrict` — FINITE RATIONAL FARKAS for the restricted LP.
    NOTE (mine): the compiled `dualCert_iff_not_bankedCutDomination` is δ-elimination ONLY — this full
    LP-duality iff is genuinely new infrastructure (Fourier–Motzkin over ℚ, or ℝ-separation + ℚ-transfer).
    Codex-lane candidate.
  * Corrected minimality predicate: `MinimalClosedDeficient` (closed port sets = exposed ports of closed
    shores), NOT `InclusionMinimalDeficient`.
- Chain: W1 + W2 + W3 (+B) ⟹ RootedEscapeSqueeze_exists_wall ⟹ (compiled Layer B + extractor)
  FullBankRelaxedCoverBundle_exists.
- Naming hazard for implementers: the reply reuses `Q` both as `abbrev Q := Rat` and as
  `Q : EscapeQuotientData O`; and `L : I.Port → Q` collides with load notation — rename on implementation.**]

---

## VERBATIM REPLY (user relay)

The Phase-3 lemma as I stated it is not correct as written. The Hall uncrossing part is true, but only for a port set that is already closed under the same root decomposition used by the cut. Otherwise full-escape closure can add extra exposed root neighborhoods carrying zero load, and minimality of the original deficient port set does not split them.
So the right move is:

1. keep the Hall uncrossing lemma, with the exact deficiency functional below;
2. replace "minimal deficient port set" by minimal closed deficient port set, or add a theorem saying Hall deficiency is preserved by full-escape closure;
3. abandon the add-only patch step, because it is false when short edges are saturated;
4. use either an exchange patch certificate or, cleaner, a direct restricted-Farkas separation layer.
I did not find a wall falsifier. I did find two exact falsifiers to the proof route as previously phrased: one for closure-minimality and one for add-only patching.

# 1. The exact uncrossing functional

For a fixed port load `L : I.Port → Rat` define the legal sink neighborhood, capacity, load, and deficiency:

```lean
namespace Erdos23Delta0.Wall.PortHall

def legalNbr (P : Finset I.Port) : Finset I.Sink :=
  Finset.univ.filter (fun s : I.Sink => ∃ p ∈ P, I.legal p s)

def capQ (T : Finset I.Sink) : Q := ∑ s in T, I.cap s
def loadQ (L : I.Port → Q) (P : Finset I.Port) : Q := ∑ p in P, L p
def deficiencyQ (L : I.Port → Q) (P : Finset I.Port) : Q :=
  loadQ I L P - capQ I (legalNbr I P)

def HallDeficient (L : I.Port → Q) (P : Finset I.Port) : Prop :=
  0 < deficiencyQ I L P

def InclusionMinimalDeficient (L : I.Port → Q) (P : Finset I.Port) : Prop :=
  HallDeficient I L P
  ∧ ∀ P' : Finset I.Port, P' ⊂ P → deficiencyQ I L P' ≤ 0
```

Basic identities: `legalNbr_union` (legalNbr (P∪Q) = legalNbr P ∪ legalNbr Q), `legalNbr_inter_subset`,
`capQ_mono` (nonneg caps), `capQ_submodular_on_legalNbr`
(cap N(P∪Q) + cap N(P∩Q) ≤ cap N(P) + cap N(Q), via union-exactness + inter-subset + modular sum
cap(A)+cap(B) = cap(A∪B)+cap(A∩B)), `deficiencyQ_supermodular`
(Def P + Def Q ≤ Def(P∪Q) + Def(P∩Q); load modular, capacity-neighborhood submodular),
`deficiencyQ_disjoint_neighbor_split` (disjoint ports + DISJOINT legal neighborhoods ⟹
Def(P₁∪P₂) = Def(P₁) + Def(P₂)).

If neighborhoods overlap, the exact formula is (disjoint P₁,P₂):

```text
Def(P₁ ∪ P₂) = Def(P₁) + Def(P₂) + Cap(N(P₁) ∩ N(P₂))
```

Therefore overlap cannot be ignored — it can hide positive deficiency in the intersection-capacity term. So
"independent root neighborhoods" must mean disjoint legal sink neighborhoods, or they must be merged into one
root neighborhood.

# 2. Minimal deficient sets are connected in the legal incidence graph

`LegalComponentPartition I P`: finite index K; ports : K → Finset Port, sinks : K → Finset Sink;
ports_subset (∀k, ports k ⊆ P); ports/sinks pairwise disjoint; ports_cover (⋃ = P); sinks_cover
(⋃ = legalNbr P); sinks_eq_nbr (∀k, sinks k = legalNbr (ports k)); nonempty_ports.

```lean
theorem minimal_deficient_has_one_legal_component
    (hcap) (L) (P) (hmin : InclusionMinimalDeficient I L P)
    (D : LegalComponentPartition I P) : Fintype.card D.K = 1
-- Def(P) = Σ k, Def(P_k) (disjoint sink blocks ⟹ no bank capacity counted twice);
-- Def(P) > 0 ⟹ some Def(P_k) > 0; ≥2 components ⟹ P_k ⊂ P contradicting inclusion-minimality.
```

This proves the uncrossing claim precisely.

# 3. The closure version needs "closed deficient," not merely "deficient"

"Take a minimal deficient port set P, close its quotient shore, then split multiple exposed root
neighborhoods" is FALSE as stated. Exact abstract failure:

```text
Ports: p₁, p₂;  Sinks: s₁, s₂;  Legal arcs: p₁--s₁, p₂--s₂
Capacities: cap(s₁) = 0, cap(s₂) = 100;  Loads: L(p₁) = 1, L(p₂) = 0
P = {p₁}: Def(P) = 1 − 0 = 1 > 0, inclusion-minimal deficient.
Suppose full-escape closure exposes both ports: ExposedPorts(closure(P)) = {p₁, p₂} —
two independent root neighborhoods {p₁}--{s₁}, {p₂}--{s₂}, but P does not split into two nonempty
deficient subsets. The second neighborhood was created by closure and carries zero load.
```

Corrected inputs — Option 1 (cleaner): work with closed port sets:

```lean
structure ClosedPortSet (Q : EscapeQuotientData O) (P : Finset I.Port) : Prop where
  shore : Finset Q.QComp
  closed : Q.fullClosure shore = shore
  exposed_eq : Q.exposedPorts shore = P

def MinimalClosedDeficient (Q) (L) (P) : Prop :=
  ClosedPortSet Q P ∧ HallDeficient I L P
  ∧ ∀ P', ClosedPortSet Q P' → P' ⊂ P → deficiencyQ I L P' ≤ 0
```

Option 2 (`ClosurePreservesDeficiency`) is strong and NOT automatic.

# 4. Root-neighborhood trichotomy

Exhaustive only after ruling out unbankable exposed ports. Required predicate:

```lean
def NoUnbankableExposedPorts (O) (Q : EscapeQuotientData O) : Prop :=
  ∀ U : Finset Q.QComp, Q.fullClosure U = U →
    ∀ p ∈ Q.exposedPorts U, ∃ s : O.BankSink, O.LegalSinkPort p s
```

NOT implied by the cardinal facts (|S|≥9, defect-one, no-private, support {4,≥6}, no-5, pair-union ≥5,
footprint connected) — those never mention the legal sink relation. If not already part of cage-legality it
must be added.

Root neighborhoods = canonically the legal-incidence components (`RootNeighborhoodDecomposition`: disjoint
port blocks + disjoint sink blocks with sinks r = legalNbr (ports r), root = least sink, all sink kinds
banked). This removes the "scattered sinks" case — scattered sinks form their own legal component. Trichotomy
(E=∅ ∨ card=1 ∨ ≥2) = finite cardinal arithmetic.

For a minimal CLOSED deficient set, the ≥2 case is impossible IF root blocks are themselves closed — that
separability is the real geometric content:

```lean
structure RootBlockClosureSeparable (O) (Q : EscapeQuotientData O) where
  blockClosed : ∀ U closed, ∀ D : RootNeighborhoodDecomposition (exposedPorts U), ∀ r,
    ∃ Ur, Q.fullClosure Ur = Ur ∧ Q.exposedPorts Ur = D.ports r ∧ D.ports r ⊆ Q.exposedPorts U
  proper_if_multiple : ∀ U hU D r, 2 ≤ card D.Root → ∀ Ur closed exposed-eq,
    Q.exposedPorts Ur ⊂ Q.exposedPorts U
```

With that, `minimalClosedDeficient_has_unique_root_neighborhood` is fully provable (Def additive over the
disjoint root blocks; some block deficient; separability makes it a PROPER CLOSED deficient subset —
contradiction with MinimalClosedDeficient). The corrected Phase-3 theorem then produces: P=∅ ⟹ γ-free
QuotientClosedCut; else unique root ⟹ BankRootedClosureCut (all exposed ports route into the single root
neighborhood; kinds banked). **The important correction is MinimalClosedDeficient, not merely
InclusionMinimalDeficient.**

# 5. What must be derived from graph structure

The Hall algebra uses NO graph facts. The graph facts are needed for exactly two bridge theorems:
5.1 `noUnbankableExposedPorts_of_cageLegality` (hard/definitional depending on APIs — every off-support port
exposed by a closed shore is legally incident to ≥1 door/vertexSlack/C5Base/prune sink; not implied by
support counts).
5.2 `rootBlockClosureSeparable_of_minimalFullClosure` — **THIS is the genuine Phase-3 combinatorial theorem.**
Proof content: (1) each root component determines a quotient subshore Ur; (2) full-escape closure of Ur does
not cross into the other root block — otherwise an escape chain joins the two legal components,
contradicting independence of their legal sink neighborhoods; (3) Ur proper when ≥2 roots; (4) if Ur failed
to be closed, the first closure edge leaving Ur would produce a private short edge / a size-5 support / a
pair-union < 5 / a proper full-closure Hall violator — contradicting the hypotheses. Not finite-sum
bookkeeping; the actual structural proof obligation.

# 6. The add-only patch step is false

Exact rational counterexample to the patch mechanism: cuts Y,X; short f; useShort(Y,f)=useShort(X,f)=1;
theta(Y)=1, theta(X)=0. Current coefficient = 1 (saturated); adding any ε>0 to X gives 1+ε>1 — short
congestion fails immediately. Not a wall falsifier; a falsifier to the add-only patch proof.

Only valid patch form = EXCHANGE (`ExchangePatch`: theta' = theta + plus − minus; minus ≤ theta;
alpha_delta_nonneg; short_delta_nonpos; port_delta_routable with per-sink Σ rhoDelta ≤ 0). The exchange
arithmetic is bookkeeping (`exchangePatch_preserves_dualSqueeze`), but EXISTENCE
(`rootedExchangePatch_exists`) is another hard theorem (componentwise cut-submodularity
χδ(A∪B)+χδ(A∩B) ≤ χδ(A)+χδ(B); the closed quotient cut REPLACES rather than adds to the singleton cuts whose
boundary generated P). Without it the patch route is incomplete.

# 7. Cleaner fallback: direct restricted-Farkas separation (RECOMMENDED)

Replace Phase 4 by a direct finite LP separation theorem — avoids short-edge saturation entirely because it
solves for theta from scratch. `RestrictedDual Allowed alpha` (beta,gamma,delta ≥ 0; D1 only over Allowed
cuts; D2 on legal arcs) with `Strict` = totalBeta + totalDeltaCap < totalAlpha. Then FINITE RATIONAL FARKAS:

```lean
theorem dualSqueeze_exists_iff_no_restrictedStrict (Allowed) (d) (halpha) (hcap) :
    (∃ Z : I.DualSqueeze Allowed d, checked Z) ↔
    ¬ ∃ R : I.RestrictedDual Allowed d.alpha, R.Strict
-- primal vars theta_X ≥ 0 (Allowed X), rho_p_s ≥ 0 (legal p-s); constraints = the four squeeze families;
-- separator normalizes tau = 1; separator inequalities are exactly restricted D1 + D2; strict objective =
-- totalBeta_R + totalDeltaCap_R < totalAlpha_d.
```

The new hard wall statement becomes `noStrictRestrictedDual_rootedEscape` (hypotheses: Allowed ↔ singleton ∨
quotientClosed ∨ bankRootedClosure; NoUnbankableExposedPorts; RootBlockClosureSeparable; the ten geometry
facts; alpha ≥ 0) ⟹ no strict restricted dual. Layer A follows formally
(`RootedEscapeSqueeze_exists_wall` = checkDual_sound + the iff + noStrictRestrictedDual).

# 8. Required extra hypotheses

1. `NoUnbankableExposedPorts O Q` — likely graph-derivable from cage-legality; else add to the checker.
2. `RootBlockClosureSeparable O Q` — the genuine combinatorial closure theorem (graph-derivable from full
   escape closure + defect-one/no-private/support-size/pair-union/connected-footprint rigidity; NOT a formal
   consequence of the Hall algebra).
3. `MinimalClosedDeficient` (or `ClosurePreservesDeficiency`) — only if keeping the Hall-patching route; the
   original "minimal deficient P" version is FALSE.
4. `rootedExchangePatch_exists` — only if keeping the patch route; add-only patching is FALSE.
The direct restricted-Farkas route REMOVES extra hypotheses 3 and 4.

# 9. Final recommendation

Do not continue with add-only Phase 4. The wall should be sharpened to:

```text
RootBlockClosureSeparable + NoUnbankableExposedPorts
+ noStrictRestrictedDual over (singleton ∪ quotientClosed ∪ bankRootedClosure)
⇒ RootedEscapeSqueeze_exists_wall
⇒ FullBankRelaxedCoverBundle_exists
```

Fully proved part = the uncrossing algebra: Def(P) = L(P) − Cap(N(P)) is supermodular, additive on
independent legal root components; a minimal closed deficient port set has exactly one legal root
neighborhood; capacity handled exactly by disjointness of legal sink neighborhoods (overlapping
neighborhoods must be merged — the split inequality is false in the needed direction). The remaining hard
graph theorem is no longer vague: `rootBlockClosureSeparable_of_minimalFullClosure` — where defect-one,
no-private-edge, support sizes {4,≥6}, no size-5, pair-union ≥5, footprint connectedness, full escape
closure, reduced minimal negative balance, and cage legality must be used.
