GAP#1 DEFINITIVE HANDOFF — THE BALANCED-NEUTRAL ELL=5 LENS LEMMA (Erdos #23, delta=0)
Date: 2026-07-08. Audience: Codex (independent formalizer/tester). This document is standalone: every claim carries a file path, an exact theorem name, or an exact numeric fact. Setting: reduced triangle-free Gamma-minimal MAXIMUM cut; ell=5 atoms = monochromatic (bad) edges whose blue geodesics have length 4; E_short(S) = union of all shortest-geodesic cut edges of atoms in S; target chain: Ell5SupportExpansion (|S| <= |E_short(S)|) => Gamma <= N^2 => beta <= N^2/25.

HARD RULES (unchanged): (1) never re-prove a compiled theorem — the compiled surface is Distances.lean, MaxCutVertexIneq.lean, PathRigidity.lean, Ell5CSReduction.lean, Ell5AtomBase.lean, Ell5AtomGraph.lean, Ell5GraphBridge.lean, Ell5SupportFinset.lean, NeutralLensLedger.lean, RelaxedCutCover.lean, RelaxedCoverSkeleton.lean, BankedCutDominationCore.lean, and now Ell5LensStatement.lean, all under E:/Projects/ErdosProblems/problems/23/lean/Erdos23Delta0/; (2) no invented APIs — every referenced declaration must exist in those files (new defs allowed, built from existing ones); (3) the binding case is COUNTERFACTUAL (a deficient cage has Gamma > N^2, existing in no real graph) — reason deductively; exact rational arithmetic for anything checkable; (4) never re-tread a dead-end row (section 3 table below, and the table in E:/Projects/ErdosProblems/problems/23/writeup/GAP1_SHORTESTSUPPORTEXPANSION_ESCALATION.md).

================================================================================
SECTION 1 — THE STATEMENT (final, compiled, verified)
================================================================================

STATUS: COMPILED GREEN and INDEPENDENTLY RE-VERIFIED (two separate rebuilds, the last after the documentation fixes below).
- File: E:/Projects/ErdosProblems/problems/23/lean/Erdos23Delta0/Ell5LensStatement.lean
- Build recipe: python E:/Projects/ErdosProblems/tmp/claude_build_ell5lensstatement.py (builds against cached oleans in tmp/claude_lean_o_base_v1). Latest run: rc=0, 62.4 s, zero `error:` in log tmp/claude_ell5lensstatement_err.txt.
- All 16 in-file `#print axioms` probes report a subset of {propext, Classical.choice, Quot.sound}. No `sorry`/`admit`/`axiom`/`native_decide` anywhere in the module or its import chain.
- Declaration audit: all 14 external project declarations used were checked against the real source files; zero signature mismatches (argument orders, explicit/implicit G, instance requirements all exact).

Fixes applied relative to the first draft (documentation only; re-compiled green after each):
1. The header claim "EXACTLY ONE named open Prop" was an overstatement: the module carries TWO unproven named Props — `ImpureBalancedNeutralLens_book_or_ledgerSep` (the crux) and `PureLensLedgerSeparation` (informally proven, awaiting cage-model encoding). Header and crux docstring corrected.
2. A WARNING block was added to the crux Prop's docstring recording the 24-vertex counterexample (section 3 below): bare Ell5SupportExpansion under triangle-free + max-cut + Gamma-min alone is FALSE in real graphs; bank terms are necessary.

Semantic caveats (not compile defects; keep in mind when testing):
- `LensReducible` and the cage `C` are fully decoupled from `G` (abstract gamma-type per the NeutralLensLedger connection contract). A degenerate instantiation (gamma = Unit, Balance = 0) makes `hCneg` unsatisfiable, so the capstone is then vacuous, never false. All graph-to-ledger content is deferred to the future cage-model instantiation (section 5, task T8).
- The lens-certificate fields `shares`, `bornEll0/1`, `shoreConn`, `coShoreConn`, `doorSigB` are not consumed by any wiring theorem in this module (only `doorSigM` + `badNe` feed the derived facts). The wiring theorems are logically valid; the lens geometry constrains only the future proofs of the two open Props. Do not read `minimal_violator_contradiction` as using the lens geometry.
- `Ell5GraphBridge` is imported but only as a transitive dependency of Ell5SupportFinset. Harmless.

FULL MODULE TEXT (verbatim, as on disk and compiled):

```lean
import Mathlib
import Erdos23Delta0.Distances
import Erdos23Delta0.MaxCutVertexIneq
import Erdos23Delta0.Ell5CSReduction
import Erdos23Delta0.Ell5AtomBase
import Erdos23Delta0.Ell5GraphBridge
import Erdos23Delta0.Ell5SupportFinset
import Erdos23Delta0.NeutralLensLedger

/-!
# The balanced-neutral ell=5 lens: STATEMENT module (2026-07-08)

Gap#1 of Erdős #23 δ=0 is `Ell5SupportExpansion` (`|S| ≤ |E_short(S)|` for every ell=5 atom set `S`),
whose sole open local content is the lineage lemma `BalancedNeutralTheta_book_or_reducible`. This module
gives that lemma a COMPILABLE statement surface at the `blueGraph`/`Ell5Atom` level, built strictly from
the already-compiled declarations:

* **(a) definitions** — `SharedSupportPair` (two atoms with distinct bad edges and intersecting
  multi-geodesic supports), `BalancedNeutralLens` (shore `W` with exact 2+2 door signature
  `δ_B(W) = {d0,d1}`, `δ_M(W) = {e,f}`, born-door ell=5 Γ-neutrality after the `W`-flip, shore/co-shore
  blue connectivity), `ownedAtoms` / `Straddles` / `IsPureLens` / `IsImpureLens` (STRONG purity =
  no-escaping-atom, per the 2026-07-08 ledger-separation arc);
* **(b) the dichotomy statements** — the PURE case as a separate named Prop
  (`PureLensLedgerSeparation`, informally proven in GAP1_LEDGER_SEPARATION_GPTPRO.md but pending the
  cage-model encoding) and the IMPURE case as the open crux Prop. NOTE: the module carries TWO
  unproven named Props — `PureLensLedgerSeparation` (informally proven, awaiting cage-model encoding)
  and the crux:

  >>> `ImpureBalancedNeutralLens_book_or_ledgerSep` — THE OPEN CRUX PROP (gap#1) <<<

* **(c) wiring theorems (PROVEN here, axiom-clean)** — the dichotomy assembly and
  `lens_dichotomy_kills_minimal_violator`: dichotomy + `NeutralLensLedger.no_ledgerSep_in_minNeg` +
  `Ell5CSReduction.c5book_support_expansion` + `MaxCutVertexIneq.deltaM_card_le_deltaB_card` refute a
  minimal Hall violator, plus the capstone `minimal_violator_contradiction`.

`sorry` does not occur; the open mathematics is carried by the two named Prop hypotheses.
No new axioms; expected axiom set `{propext, Classical.choice, Quot.sound}` for every theorem here.
-/

namespace Erdos23Delta0
namespace Ell5LensStatement

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ## Bridge glue: the two cut vocabularies (`Distances.Cut` vs `MaxCutVertexIneq` booleans)

`Distances.blueGraph` speaks graph adjacency; `MaxCutVertexIneq.deltaB/deltaM` speak `edgeCut`/`edgeBoundary`
booleans on `s := c.side`. These lemmas identify them (flagged as the missing glue fact of the API audit). -/

section Bridge

variable (G : SimpleGraph V) (c : Distances.Cut V)

/-- Definitional adjacency of the blue graph. -/
theorem blueGraph_adj_iff (u v : V) :
    (Distances.blueGraph G c).Adj u v ↔ G.Adj u v ∧ c.side u ≠ c.side v :=
  Iff.rfl

/-- `edgeCut` on a two-vertex edge is the crossing predicate of the cut. -/
theorem edgeCut_eq_true_iff (u v : V) :
    MaxCutVertexIneq.edgeCut c.side s(u, v) = true ↔ c.side u ≠ c.side v := by
  cases hu : c.side u <;> cases hv : c.side v <;>
    simp [MaxCutVertexIneq.edgeCut, MaxCutVertexIneq.edgeBool, Sym2.lift_mk, hu, hv]

/-- `edgeCut = false` on a two-vertex edge is monochromaticity (badness). -/
theorem edgeCut_eq_false_iff (u v : V) :
    MaxCutVertexIneq.edgeCut c.side s(u, v) = false ↔ c.side u = c.side v := by
  cases hu : c.side u <;> cases hv : c.side v <;>
    simp [MaxCutVertexIneq.edgeCut, MaxCutVertexIneq.edgeBool, Sym2.lift_mk, hu, hv]

/-- `edgeBoundary` on a two-vertex edge holds iff exactly one endpoint lies in `U`. -/
theorem edgeBoundary_eq_true_iff (U : Finset V) (u v : V) :
    MaxCutVertexIneq.edgeBoundary U s(u, v) = true ↔ ¬ ((u ∈ U) ↔ (v ∈ U)) := by
  by_cases hu : u ∈ U <;> by_cases hv : v ∈ U <;>
    simp [MaxCutVertexIneq.edgeBoundary, MaxCutVertexIneq.edgeBool, MaxCutVertexIneq.memBool,
      Sym2.lift_mk, hu, hv]

/-- Membership in `deltaM` unpacked: a graph edge, monochromatic, crossing the vertex boundary of `U`. -/
theorem mem_deltaM_iff [Fintype G.edgeSet] (s : V → Bool) (U : Finset V) (e : Sym2 V) :
    e ∈ MaxCutVertexIneq.deltaM G s U ↔
      e ∈ G.edgeFinset ∧ MaxCutVertexIneq.edgeCut s e = false ∧
        MaxCutVertexIneq.edgeBoundary U e = true := by
  unfold MaxCutVertexIneq.deltaM
  rw [Finset.mem_filter]
  cases hc : MaxCutVertexIneq.edgeCut s e <;>
    cases hb : MaxCutVertexIneq.edgeBoundary U e <;> simp [hc, hb]

/-- Membership in `deltaB` unpacked: a graph edge, cut (bichromatic), crossing the vertex boundary of `U`. -/
theorem mem_deltaB_iff [Fintype G.edgeSet] (s : V → Bool) (U : Finset V) (e : Sym2 V) :
    e ∈ MaxCutVertexIneq.deltaB G s U ↔
      e ∈ G.edgeFinset ∧ MaxCutVertexIneq.edgeCut s e = true ∧
        MaxCutVertexIneq.edgeBoundary U e = true := by
  unfold MaxCutVertexIneq.deltaB
  rw [Finset.mem_filter]
  cases hc : MaxCutVertexIneq.edgeCut s e <;>
    cases hb : MaxCutVertexIneq.edgeBoundary U e <;> simp [hc, hb]

/-- The blue edge finset is exactly the cut graph edges (the flagged (B).4 glue fact). -/
theorem mem_blueGraph_edgeFinset [Fintype G.edgeSet]
    [Fintype (Distances.blueGraph G c).edgeSet] (e : Sym2 V) :
    e ∈ (Distances.blueGraph G c).edgeFinset ↔
      e ∈ G.edgeFinset ∧ MaxCutVertexIneq.edgeCut c.side e = true := by
  refine Sym2.inductionOn e fun u v => ?_
  rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeFinset,
    SimpleGraph.mem_edgeSet, SimpleGraph.mem_edgeSet, edgeCut_eq_true_iff]
  exact Iff.rfl

/-- Row length 5 is blue distance 4 (`ell = dist + 1`). -/
theorem ell_eq_five_iff_dist_eq_four (u v : V) :
    Distances.ell G c u v = 5 ↔ (Distances.blueGraph G c).dist u v = 4 := by
  unfold Distances.ell
  omega

end Bridge

/-! ## (a) The shared-support pair, the lens, and ownership -/

/-- **A shared-support pair (theta/lens pair):** two ell=5 atoms of `H` with DISTINCT bad edges, both
    geodesic-tight (`dist = 4`, so the carried length-4 geodesic is shortest and `ell = 5` at the blue level),
    whose FULL multi-geodesic supports `P_e` intersect. This is the sharing witness manufactured by
    `Ell5CSReduction.minimal_hall_obstruction_no_private_edge` inside a minimal Hall violator. -/
structure SharedSupportPair (H : SimpleGraph V) where
  a : Ell5AtomBase.Ell5Atom H
  b : Ell5AtomBase.Ell5Atom H
  badNe : s(a.u, a.v) ≠ s(b.u, b.v)
  distA : H.dist a.u a.v = 4
  distB : H.dist b.u b.v = 4
  shares : (Ell5SupportFinset.geodesicSupport H a.u a.v ∩
      Ell5SupportFinset.geodesicSupport H b.u b.v).Nonempty

/-- Each atom's canonical 4-edge support sits in its full multi-geodesic support. -/
theorem SharedSupportPair.supportA_subset {H : SimpleGraph V} (pair : SharedSupportPair H) :
    pair.a.support ⊆ Ell5SupportFinset.geodesicSupport H pair.a.u pair.a.v :=
  Ell5SupportFinset.atom_support_subset_geodesicSupport pair.a pair.distA

theorem SharedSupportPair.supportB_subset {H : SimpleGraph V} (pair : SharedSupportPair H) :
    pair.b.support ⊆ Ell5SupportFinset.geodesicSupport H pair.b.u pair.b.v :=
  Ell5SupportFinset.atom_support_subset_geodesicSupport pair.b pair.distB

/-- The cut obtained by flipping the shore `W` (the recut `B ↦ B^W`). -/
def flippedCut (c : Distances.Cut V) (W : Finset V) : Distances.Cut V :=
  ⟨MaxCutVertexIneq.flipCut c.side W⟩

/-- **The balanced neutral lens certificate** for a shared-support pair, at the compiled
    `deltaB`/`deltaM` door vocabulary (doors = blue boundary EDGES, per the audited edge reading):

    * `W` — the lens shore;
    * exact door signature: `δ_B(W) = {s(x0,y0), s(x1,y1)}` (the two doors `d0 ≠ d1`) and
      `δ_M(W) = {bad a, bad b}` (the two old rows; in particular NO other bad edge crosses `W` — LS3);
    * balancedness `|δ_B(W)| = |δ_M(W)| = 2` is DERIVED below (`deltaB_card`, `deltaM_card`), so the
      `W`-flip preserves cut size (`MaxCutVertexIneq.cutVal_flip_add_deltaB_card`);
    * Γ-neutrality: after flipping `W` the two born doors are ell=5 rows (`5²+5² → 5²+5²`, ΔΓ = 0),
      carried by `bornEll0`/`bornEll1` at the genuine `Distances.ell` of the flipped cut;
    * connectivity of shore and co-shore in the blue graph (LS2). -/
structure BalancedNeutralLens (G : SimpleGraph V) [Fintype G.edgeSet] (c : Distances.Cut V)
    (pair : SharedSupportPair (Distances.blueGraph G c)) where
  W : Finset V
  x0 : V
  y0 : V
  x1 : V
  y1 : V
  doorsNe : s(x0, y0) ≠ s(x1, y1)
  doorSigB : MaxCutVertexIneq.deltaB G c.side W = {s(x0, y0), s(x1, y1)}
  doorSigM : MaxCutVertexIneq.deltaM G c.side W =
      {s(pair.a.u, pair.a.v), s(pair.b.u, pair.b.v)}
  bornEll0 : Distances.ell G (flippedCut c W) x0 y0 = 5
  bornEll1 : Distances.ell G (flippedCut c W) x1 y1 = 5
  shoreConn : ((Distances.blueGraph G c).induce (W : Set V)).Connected
  coShoreConn : ((Distances.blueGraph G c).induce ((Wᶜ : Finset V) : Set V)).Connected

namespace BalancedNeutralLens

variable {G : SimpleGraph V} [Fintype G.edgeSet] {c : Distances.Cut V}
variable {pair : SharedSupportPair (Distances.blueGraph G c)}

/-- Balanced, cut side: exactly two doors. -/
theorem deltaB_card (lens : BalancedNeutralLens G c pair) :
    (MaxCutVertexIneq.deltaB G c.side lens.W).card = 2 := by
  rw [lens.doorSigB]
  exact Finset.card_pair lens.doorsNe

/-- Balanced, bad side: exactly two boundary bad edges (the pair's rows). -/
theorem deltaM_card (lens : BalancedNeutralLens G c pair) :
    (MaxCutVertexIneq.deltaM G c.side lens.W).card = 2 := by
  rw [lens.doorSigM]
  exact Finset.card_pair pair.badNe

/-- **Balanced:** `|δ_M(W)| = |δ_B(W)|`, so the `W`-flip preserves the cut value. -/
theorem balanced (lens : BalancedNeutralLens G c pair) :
    (MaxCutVertexIneq.deltaM G c.side lens.W).card
      = (MaxCutVertexIneq.deltaB G c.side lens.W).card := by
  rw [lens.deltaM_card, lens.deltaB_card]

theorem badA_mem_deltaM (lens : BalancedNeutralLens G c pair) :
    s(pair.a.u, pair.a.v) ∈ MaxCutVertexIneq.deltaM G c.side lens.W := by
  rw [lens.doorSigM]
  exact Finset.mem_insert_self _ _

theorem badB_mem_deltaM (lens : BalancedNeutralLens G c pair) :
    s(pair.b.u, pair.b.v) ∈ MaxCutVertexIneq.deltaM G c.side lens.W := by
  rw [lens.doorSigM]
  exact Finset.mem_insert_of_mem (Finset.mem_singleton_self _)

/-- The pair's first bad edge is a genuine `G`-edge (recovered from the door signature — the compiled
    `Ell5Atom` does not carry adjacency; the lens certificate does, via `δ_M`). -/
theorem pairA_adj (lens : BalancedNeutralLens G c pair) : G.Adj pair.a.u pair.a.v := by
  have h := (mem_deltaM_iff G c.side lens.W s(pair.a.u, pair.a.v)).mp lens.badA_mem_deltaM
  have h1 := h.1
  rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet] at h1
  exact h1

theorem pairB_adj (lens : BalancedNeutralLens G c pair) : G.Adj pair.b.u pair.b.v := by
  have h := (mem_deltaM_iff G c.side lens.W s(pair.b.u, pair.b.v)).mp lens.badB_mem_deltaM
  have h1 := h.1
  rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet] at h1
  exact h1

/-- The pair's first row is monochromatic (bad) — likewise recovered from `δ_M`. -/
theorem pairA_bad (lens : BalancedNeutralLens G c pair) :
    c.side pair.a.u = c.side pair.a.v := by
  have h := (mem_deltaM_iff G c.side lens.W s(pair.a.u, pair.a.v)).mp lens.badA_mem_deltaM
  exact (edgeCut_eq_false_iff c pair.a.u pair.a.v).mp h.2.1

theorem pairB_bad (lens : BalancedNeutralLens G c pair) :
    c.side pair.b.u = c.side pair.b.v := by
  have h := (mem_deltaM_iff G c.side lens.W s(pair.b.u, pair.b.v)).mp lens.badB_mem_deltaM
  exact (edgeCut_eq_false_iff c pair.b.u pair.b.v).mp h.2.1

end BalancedNeutralLens

open Classical in
/-- **Atoms owned by the shore `W`** (strong/interior ownership): atoms of `S` whose FULL multi-geodesic
    support lies inside `W`'s induced edge set `W.sym2` (both endpoints of every support edge in `W`).
    Under this reading the boundary pair `e, f` is NOT owned (their geodesics use door-adjacent border
    edges), matching the ledger arc's "owned strictly inside". -/
noncomputable def ownedAtoms (H : SimpleGraph V) (S : Finset (Ell5AtomBase.Ell5Atom H))
    (W : Finset V) : Finset (Ell5AtomBase.Ell5Atom H) :=
  S.filter fun h => Ell5SupportFinset.geodesicSupport H h.u h.v ⊆ W.sym2

/-- **A straddling (escaping-candidate) atom:** its multi-geodesic support meets the interior edge set of
    `W` yet is not contained in it — the support crosses the lens in a non-boundary way. This is the exact
    pattern of the verified 11-vertex max-cut escaping atom (`_claude_verify_maxcut_escaping.py`). -/
def Straddles (H : SimpleGraph V) (W : Finset V) (h : Ell5AtomBase.Ell5Atom H) : Prop :=
  (∃ e ∈ Ell5SupportFinset.geodesicSupport H h.u h.v, e ∈ W.sym2) ∧
    ¬ Ell5SupportFinset.geodesicSupport H h.u h.v ⊆ W.sym2

/-- **Pure lens, STRONG sense (= NoEscapingAtom).** (i) every atom owned by `W` is one of the pair, and
    (ii) no atom of `S` other than the pair straddles `W`. The weak reading "no extra owned atoms" is
    NOT sufficient for the ledger split LS4 (the 11-vtx escaping pattern has no extra owned atom yet is
    not ledger-separating); strong purity is what the pure-case reducibility proof consumes. -/
def IsPureLens (G : SimpleGraph V) [Fintype G.edgeSet] (c : Distances.Cut V)
    (S : Finset (Ell5AtomBase.Ell5Atom (Distances.blueGraph G c)))
    (pair : SharedSupportPair (Distances.blueGraph G c))
    (lens : BalancedNeutralLens G c pair) : Prop :=
  (∀ h ∈ ownedAtoms (Distances.blueGraph G c) S lens.W, h = pair.a ∨ h = pair.b) ∧
    ∀ h ∈ S, s(h.u, h.v) ≠ s(pair.a.u, pair.a.v) → s(h.u, h.v) ≠ s(pair.b.u, pair.b.v) →
      ¬ Straddles (Distances.blueGraph G c) lens.W h

/-- Impure lens: the negation (some non-pair atom is owned or straddles — the escaping-atom regime). -/
def IsImpureLens (G : SimpleGraph V) [Fintype G.edgeSet] (c : Distances.Cut V)
    (S : Finset (Ell5AtomBase.Ell5Atom (Distances.blueGraph G c)))
    (pair : SharedSupportPair (Distances.blueGraph G c))
    (lens : BalancedNeutralLens G c pair) : Prop :=
  ¬ IsPureLens G c S pair lens

/-! ## (b) The dichotomy statements -/

/-- **The book branch, in the exact shape `c5book_support_expansion` consumes:** a flip set `U` whose
    boundary bad edges cover `S` (`hcross`) and whose boundary cut edges all lie in `E_short(S)`
    (`hclosed`, the closed-book boundary property). Under `IsMaxCut`, this yields `|S| ≤ |E_short(S)|`
    (see `lens_dichotomy_kills_minimal_violator`). -/
def C5BookWitness (G : SimpleGraph V) [Fintype G.edgeSet] (c : Distances.Cut V)
    (S : Finset (Ell5AtomBase.Ell5Atom (Distances.blueGraph G c))) : Prop :=
  ∃ U : Finset V,
    S.card ≤ (MaxCutVertexIneq.deltaM G c.side U).card ∧
      MaxCutVertexIneq.deltaB G c.side U ⊆ Ell5SupportFinset.Eshort (Distances.blueGraph G c) S

/-- **The reducible branch:** some instantiation of the abstract cage ledger is ledger-separating
    (the connection-contract shape (b) of `NeutralLensLedger`). -/
def LensReducible {γ : Type*} (Balance : γ → ℚ) (Proper : γ → Prop) (C : γ) : Prop :=
  ∃ W C' rem, NeutralLensLedger.LedgerSep Balance Proper C W C' rem

set_option linter.unusedVariables false in
/-- **PURE case (separate lemma statement).** A pure (no-escaping-atom) balanced-neutral lens is
    ledger-separating. Informally PROVEN (GAP1_LEDGER_SEPARATION_GPTPRO.md items LS1–LS5: purity
    discharges LS4, lens connectivity gives LS1–LS2, door signature gives LS3, additive prune split gives
    LS5) — but its Lean proof needs the concrete cage-model instantiation of `γ, Balance, Proper`, which
    does not exist yet; hence a named Prop, NOT the open crux. NOTE the `cProper` caveat: validity of the
    pruned complement `C'` (max-cut of the induced subgraph) is a real obligation inside this Prop. -/
def PureLensLedgerSeparation {γ : Type*} (Balance : γ → ℚ) (Proper : γ → Prop) (C : γ)
    (G : SimpleGraph V) [Fintype G.edgeSet] (c : Distances.Cut V)
    (S : Finset (Ell5AtomBase.Ell5Atom (Distances.blueGraph G c)))
    (pair : SharedSupportPair (Distances.blueGraph G c))
    (lens : BalancedNeutralLens G c pair) : Prop :=
  IsPureLens G c S pair lens → LensReducible Balance Proper C

set_option linter.unusedVariables false in
/-- >>> **THE OPEN CRUX PROP (gap#1).** <<<

    **IMPURE case** of the balanced-neutral lens dichotomy (lineage:
    `BalancedNeutralTheta_book_or_reducible`, impure part; dual form `BankedCutDomination`; equivalently
    the escape-closure dichotomy's FULL branch obligation): an impure lens (some escaping/owned non-pair
    atom) in the given configuration yields EITHER a closed C5-book witness (the flip set feeding
    `c5book_support_expansion`) OR a ledger-separating prunable subcage (e.g. the proper escape closure).
    All local shortcuts to it are refuted (Γ-decrease: the lens is Γ-neutral; maximality lever: the 11-vtx
    escaping atom survives at a genuine max cut; deficiency/reducedness: scalar, create no separator).
    The binding case is COUNTERFACTUAL (a deficient cage has `Γ > N²`, existing in no real graph).

    WARNING (2026-07-08 verification): bare `Ell5SupportExpansion` — `|S| ≤ |E_short(S)|` under
    triangle-free + max-cut + Γ-min ALONE — is FALSE in real graphs: a 24-vertex triangle-free graph
    with unique (hence Γ-minimal) maximum cut realizes the m=9 double-star pattern with `|S| = 9 >
    8 = |E_short(S)|` (`problems/23/writeup/_claude_v3_refute24_doublestar_realized.py`, exhaustive
    2^23). Any proof of this Prop must therefore route the full/absorption branch through the BANKED
    form (door/vertex-slack/base/prune caps): the bank terms are NECESSARY, not decorative. -/
def ImpureBalancedNeutralLens_book_or_ledgerSep {γ : Type*}
    (Balance : γ → ℚ) (Proper : γ → Prop) (C : γ)
    (G : SimpleGraph V) [Fintype G.edgeSet] (c : Distances.Cut V)
    (S : Finset (Ell5AtomBase.Ell5Atom (Distances.blueGraph G c)))
    (pair : SharedSupportPair (Distances.blueGraph G c))
    (lens : BalancedNeutralLens G c pair) : Prop :=
  IsImpureLens G c S pair lens →
    C5BookWitness G c S ∨ LensReducible Balance Proper C

set_option linter.unusedVariables false in
/-- **The full dichotomy** (lineage `BalancedNeutralLens_book_or_reducible`): the lens configuration is
    book (C5-book witness) or reducible (ledger-separating). Assembled from the pure statement + the one
    open impure Prop by `dichotomy_of_pure_and_impure`. -/
def BalancedNeutralLens_book_or_reducible {γ : Type*}
    (Balance : γ → ℚ) (Proper : γ → Prop) (C : γ)
    (G : SimpleGraph V) [Fintype G.edgeSet] (c : Distances.Cut V)
    (S : Finset (Ell5AtomBase.Ell5Atom (Distances.blueGraph G c)))
    (pair : SharedSupportPair (Distances.blueGraph G c))
    (lens : BalancedNeutralLens G c pair) : Prop :=
  C5BookWitness G c S ∨ LensReducible Balance Proper C

/-! ## (c) Wiring theorems (proven; the compiled algebra closes everything but the two named Props) -/

section Wiring

variable {γ : Type*} (Balance : γ → ℚ) (Proper : γ → Prop) (C : γ)
variable (G : SimpleGraph V) [Fintype G.edgeSet] (c : Distances.Cut V)
variable (S : Finset (Ell5AtomBase.Ell5Atom (Distances.blueGraph G c)))
variable (pair : SharedSupportPair (Distances.blueGraph G c))
variable (lens : BalancedNeutralLens G c pair)

/-- **Pure lens is impossible in a minimal-negative cage** (wiring of the pure statement into the
    compiled balance-sign-agnostic minimality lever). -/
theorem pure_lens_impossible_in_minNeg
    (hCneg : Balance C < 0)
    (hMin : ∀ D, Proper D → 0 ≤ Balance D)
    (hpure : IsPureLens G c S pair lens)
    (hPureSep : PureLensLedgerSeparation Balance Proper C G c S pair lens) :
    False := by
  obtain ⟨W', C', rem, hLS⟩ := hPureSep hpure
  exact NeutralLensLedger.no_ledgerSep_in_minNeg Balance Proper C W' C' rem hCneg hMin hLS

/-- **Dichotomy assembly:** pure statement + the one open impure Prop ⟹ the full dichotomy. -/
theorem dichotomy_of_pure_and_impure
    (hPureSep : PureLensLedgerSeparation Balance Proper C G c S pair lens)
    (hImpure : ImpureBalancedNeutralLens_book_or_ledgerSep Balance Proper C G c S pair lens) :
    BalancedNeutralLens_book_or_reducible Balance Proper C G c S pair lens := by
  by_cases hp : IsPureLens G c S pair lens
  · exact Or.inr (hPureSep hp)
  · exact hImpure hp

/-- **The wiring theorem:** the dichotomy, the compiled minimality lever
    (`NeutralLensLedger.no_ledgerSep_in_minNeg`), the compiled book chain
    (`Ell5CSReduction.c5book_support_expansion`) and the compiled max-cut capacity
    (`MaxCutVertexIneq.deltaM_card_le_deltaB_card`) refute a minimal Hall violator
    (`hviol : |E_short(S)| < |S|`) inside a minimal-negative cage at a maximum cut. -/
theorem lens_dichotomy_kills_minimal_violator
    (hmax : MaxCutVertexIneq.IsMaxCut G c.side)
    (hCneg : Balance C < 0)
    (hMin : ∀ D, Proper D → 0 ≤ Balance D)
    (hviol : (Ell5SupportFinset.Eshort (Distances.blueGraph G c) S).card < S.card)
    (hDich : BalancedNeutralLens_book_or_reducible Balance Proper C G c S pair lens) :
    False := by
  unfold BalancedNeutralLens_book_or_reducible C5BookWitness LensReducible at hDich
  rcases hDich with ⟨U, hcross, hclosed⟩ | ⟨W', C', rem, hLS⟩
  · have hmc := MaxCutVertexIneq.deltaM_card_le_deltaB_card G c.side U hmax
    have hexp := Ell5CSReduction.c5book_support_expansion S
      (MaxCutVertexIneq.deltaM G c.side U) (MaxCutVertexIneq.deltaB G c.side U)
      (Ell5SupportFinset.Eshort (Distances.blueGraph G c) S) hcross hmc hclosed
    omega
  · exact NeutralLensLedger.no_ledgerSep_in_minNeg Balance Proper C W' C' rem hCneg hMin hLS

/-- **Capstone:** at a maximum cut of a minimal-negative cage, a minimal violator carrying a
    balanced-neutral lens is contradictory, GIVEN the pure statement and the one open impure Prop.
    Everything else is compiled. -/
theorem minimal_violator_contradiction
    (hmax : MaxCutVertexIneq.IsMaxCut G c.side)
    (hCneg : Balance C < 0)
    (hMin : ∀ D, Proper D → 0 ≤ Balance D)
    (hviol : (Ell5SupportFinset.Eshort (Distances.blueGraph G c) S).card < S.card)
    (hPureSep : PureLensLedgerSeparation Balance Proper C G c S pair lens)
    (hImpure : ImpureBalancedNeutralLens_book_or_ledgerSep Balance Proper C G c S pair lens) :
    False :=
  lens_dichotomy_kills_minimal_violator Balance Proper C G c S pair lens hmax hCneg hMin hviol
    (dichotomy_of_pure_and_impure Balance Proper C G c S pair lens hPureSep hImpure)

end Wiring

#print axioms blueGraph_adj_iff
#print axioms edgeCut_eq_true_iff
#print axioms edgeCut_eq_false_iff
#print axioms edgeBoundary_eq_true_iff
#print axioms mem_deltaM_iff
#print axioms mem_deltaB_iff
#print axioms mem_blueGraph_edgeFinset
#print axioms ell_eq_five_iff_dist_eq_four
#print axioms SharedSupportPair.supportA_subset
#print axioms BalancedNeutralLens.balanced
#print axioms BalancedNeutralLens.pairA_adj
#print axioms BalancedNeutralLens.pairA_bad
#print axioms pure_lens_impossible_in_minNeg
#print axioms dichotomy_of_pure_and_impure
#print axioms lens_dichotomy_kills_minimal_violator
#print axioms minimal_violator_contradiction

/-!
## External declarations used (audit list)

From `Erdos23Delta0.Distances`: `Cut` (field `side`), `blueGraph`, `ell`.
From `Erdos23Delta0.MaxCutVertexIneq`: `edgeCut`, `edgeBool`, `edgeBoundary`, `memBool`, `flipCut`,
  `deltaB`, `deltaM`, `IsMaxCut`, `deltaM_card_le_deltaB_card`.
From `Erdos23Delta0.Ell5AtomBase`: `Ell5Atom` (fields `u`, `v`, `geo`, `isPath`, `len4`),
  `Ell5Atom.support`.
From `Erdos23Delta0.Ell5SupportFinset`: `geodesicSupport`, `Eshort`,
  `atom_support_subset_geodesicSupport`.
From `Erdos23Delta0.Ell5CSReduction`: `c5book_support_expansion`.
From `Erdos23Delta0.NeutralLensLedger`: `LedgerSep`, `no_ledgerSep_in_minNeg`.
From Mathlib: `SimpleGraph` (`Adj`, `edgeSet`, `edgeFinset`, `mem_edgeSet`, `mem_edgeFinset`, `dist`,
  `induce`, `Connected`), `Sym2` (`s(·,·)`, `Sym2.lift_mk`, `Sym2.inductionOn`), `Finset` (`filter`,
  `mem_filter`, `card_pair`, `mem_insert_self`, `mem_insert_of_mem`, `mem_singleton_self`, `sym2`,
  complement `ᶜ`, `Nonempty`, `∩`), `ℚ`.

Open Props (the ONLY unproven content, carried as named hypotheses — no `sorry` anywhere):
  1. `ImpureBalancedNeutralLens_book_or_ledgerSep`  — THE gap#1 crux.
  2. `PureLensLedgerSeparation` — informally proven; awaits the cage-model encoding of
     `γ / Balance / Proper` (including the `cProper` validity obligation).
-/

end Ell5LensStatement
end Erdos23Delta0
```

================================================================================
SECTION 2 — PURE CASE: verified proof plan with per-step status
================================================================================

Target: a PURE balanced-neutral lens W (strong purity = no atom h other than e,f straddles W in ownership OR support) in a reduced MinimalNegBalance cage C yields a `NeutralLensLedger.LedgerSep`, hence `False` by the compiled `no_ledgerSep_in_minNeg`. Design trick that makes it compile cheaply: define `rem := Balance C - Balance C' - Balance W`, so `pruneIdentity` is `by ring` and ALL content concentrates in `remNonneg` = (surplus exact additivity under purity) + (bank superadditivity).

Steps, each with exact statement and status:

S1 (NEW LEMMA, dischargeable now). ell = 5 exactly for the boundary pair:
```lean
theorem ell_eq_five_of_ell5Atom {V : Type*} [DecidableEq V] (G : SimpleGraph V)
    (c : Distances.Cut V) (htf : G.CliqueFree 3)
    (a : Ell5AtomBase.Ell5Atom (Distances.blueGraph G c))
    (hadj : G.Adj a.u a.v) (hbad : c.side a.u = c.side a.v) :
    Distances.ell G c a.u a.v = 5
```
Proof recipe: upper bound `(blueGraph G c).dist a.u a.v ≤ 4` from `SimpleGraph.dist_le a.geo` rewritten by `a.len4`; lower bound `5 ≤ ell` from the compiled `Distances.badEdge_ell_ge_five G c htf hadj hbad a.geo.reachable`; unfold `Distances.ell`; `omega`. Status: compiles-with-a-short-proof; no new graph fact.

S2 (NEW LEMMA, pure Finset/rational algebra, no graph input). Surplus exact additivity under strong purity:
```lean
theorem surplus_split {α : Type*} [DecidableEq α] (ellQ : α → ℚ)
    (AC AW AC' : Finset α) (e f : α)
    (hef : e ≠ f)
    (hpart : AC = (AW ∪ AC') ∪ {e, f})
    (hWC' : Disjoint AW AC')
    (heW : e ∉ AW) (heC' : e ∉ AC') (hfW : f ∉ AW) (hfC' : f ∉ AC')
    (helle : ellQ e = 5) (hellf : ellQ f = 5) :
    ∑ h ∈ AC, (ellQ h ^ 2 - 25)
      = (∑ h ∈ AW, (ellQ h ^ 2 - 25)) + ∑ h ∈ AC', (ellQ h ^ 2 - 25)
```
Recipe: `subst`, `Finset.sum_union` twice (disjointness from the non-membership hypotheses), `Finset.sum_pair hef`, boundary term (25-25)+(25-25)=0, `ring`/`linarith`. The hypotheses `hpart ... hfC'` ARE the Lean form of the LS4 atom classification (no straddler) — they are the definition of purity, supplied as hypotheses, not proof obligations. Status: compiles-now with routine tactics.

S3 (NEW LEMMA, pure rational). LedgerSep assembly:
```lean
theorem pure_lens_ledgerSep {γ : Type*} (Bank Surplus Balance : γ → ℚ) (Proper : γ → Prop)
    (C W C' : γ)
    (hBalance : ∀ D, Balance D = Bank D - Surplus D)
    (hWProper : Proper W) (hC'Proper : Proper C')
    (hSurplusSplit : Surplus C = Surplus W + Surplus C')
    (hBankSuper : Bank W + Bank C' ≤ Bank C) :
    NeutralLensLedger.LedgerSep Balance Proper C W C' (Balance C - Balance C' - Balance W) := by
  refine ⟨hWProper, hC'Proper, ?_, by ring⟩
  have hC := hBalance C; have hW := hBalance W; have hC' := hBalance C'
  linarith
```
Note: NO sign hypothesis on Balance W — that is the entire point of the compiled balance-sign-agnostic lever. Status: compiles-now.

S4 (ZERO new work). Contradiction: `no_pure_lens_in_minNeg` = one application of the compiled `NeutralLensLedger.no_ledgerSep_in_minNeg` to the S3 output under `hCneg`/`hMin`. Status: compiles-now.

S5 (ZERO new work). Dichotomy wrappers: for the book_or_reducible form instantiate the compiled `NeutralLensLedger.book_of_book_or_ledgerSep`; for the closure form use `no_balanced_neutral_lens_of_dichotomy` with left disjunct `⟨W, C', Balance C - Balance C' - Balance W, pure_lens_ledgerSep ...⟩`. Status: compiles-now.

Graph-level obligations feeding S4's hypotheses (the honest ledger):

G2 (THE ONLY genuinely new graph LEMMA needed; medium-easy, Mathlib-implementable). Prune-invariance of blue distance:
```lean
theorem dist_eq_of_le_of_geodesic_sub {V : Type*} (K H : SimpleGraph V) (hle : K ≤ H)
    (u v : V) (p : K.Walk u v)
    (hlen : (p.mapLe hle).length = H.dist u v) :
    K.dist u v = H.dist u v
```
(`Walk.mapLe` and `Walk.length_map` exist in Mathlib.) `≤` from `SimpleGraph.dist_le p` + `hlen`; `≥` since every K-walk maps to an H-walk of equal length. This is where "no escaping atom" is CONSUMED: strong purity supplies the geodesic p living in the pruned blue graph K, making each cage's own Surplus equal to the shared-ellQ Surplus of S2. The verified 11-vertex escaping atom h = p-q is exactly what violates this hypothesis (its inside geodesic dies on pruning).

G3 (DESIGN CONTRACT, not provable until `Bank` is a Lean def). Bank superadditivity `Bank W + Bank C' ≤ Bank C`. Contract: `Bank D` must be a `Finset.sum` of NONNEGATIVE local terms over disjoint local objects (25-per-door tokens, per-vertex slack `max 0 (N - T v)`, base-density tokens, descendant balances — the legal-bank dictionary; NEVER the cage's own reserve `η_C = N²/25 - m`, which would beg the conjecture). Then superadditivity is free via `Finset.sum_union` + `Finset.sum_le_sum_of_subset_of_nonneg`, with the slack realized exactly by the two doors' tokens (rem = 50 > 0 in the door normalization). If a future `Bank` def is not term-monotone in this sense, the pure-case proof fails with it — carry the contract as a structure field (e.g. `bankSuperadd : SplitData C W C' → Bank W + Bank C' ≤ Bank C`) in the cage model.

G1 (DESIGN DECISION, forced by an exact witness). `Proper` semantics: `Proper` MUST mean "nonempty proper-support prunable descendant carrying the AMBIENT cut restricted" (with the lens certificate's LS2 connectivity). The alternative — `Proper` requires the restricted cut to be a MAXIMUM cut of the induced subgraph — is FALSE in general: exact n=14 witness, C' = {0,1,3,4,5,6,7} has induced cut 6 but induced max cut 7 (GAP1_LEDGER_SEPARATION_GPTPRO.md lines 72-79). Consequence: `hMin` (MinimalNegBalance) must quantify over the SAME ambient-restricted `Proper` — this coherence is where the global max-cut condition re-enters, and it is a modeling obligation on the unformalized rowDB/cage layer, not on this proof.

Summary: S1-S5 are implementable today against the compiled surface with no `sorry`; G2 is the single new graph proof; G1/G3 are obligations on the future cage model, carried as structure fields.

================================================================================
SECTION 3 — IMPURE CASE: what is established, what survives, what is dead
================================================================================

All facts below were established with exact integer/rational arithmetic and then independently re-verified with fresh code (re-implementations, not re-runs). Scripts (rerunnable): problems/23/writeup/_claude_d3_census.py, _claude_d3_local_obstruction.py, _claude_d3_witness_stats.py, _claude_d3_realize_doublestar.py, _claude_v3_census_recheck.py, _claude_v3_localobs_recheck.py, _claude_v3_refute24_doublestar_realized.py; census data _claude_d3_census_out_n9_10.json.

3a. CONFIRMED STRUCTURAL FACTS (double-checked)
- D3.1 Support-size dichotomy: |P_e| = 4 (unique geodesic edge set) or |P_e| ≥ 6; |P_e| = 5 is IMPOSSIBLE. Proof uses ONLY bipartiteness of the blue graph (two distinct length-4 geodesics have symmetric difference of even degree everywhere, hence containing a cycle, hence ≥ 4 edges in a bipartite graph; |P∪Q| = (4+4+|PΔQ|)/2 ≥ 6). Census: 0 size-5 supports over ALL maximum cuts of ALL connected triangle-free graphs N ≤ 10 (11,563 graphs, 23,449 max cuts — both counts independently reproduced exactly).
- D3.2 Connected footprint: for a minimal Hall violator S, E_short(S) is connected (pure Finset splitting argument; sound).
- D3.3 |S| = 6 impossible, by hand: minimal violator has |E_short| = 5 (compiled `minimal_hall_obstruction_no_private_edge`), so every support has size ≤ 5, hence exactly 4 by D3.1, i.e. one 4-edge path; a path's edge set determines its bad edge (compiled `PathRigidity.edges_determine_badedge`); 6 distinct atoms would need 6 distinct 4-subsets of a 5-set but C(5,4) = 5. Fully Lean-ready.
- LocalObstruction exhaustion (complete geng enumerations, aborted = 0): m = 6, 7, 8 EMPTY, so every minimal Hall violator has |S| ≥ 9. m = 9 has a UNIQUE footprint (g6 `H???FaM`): the double-star-with-bridge {l1,l2,l3}-u, u-w, w-v, v-{r1,r2,r3} (8 edges), with S = K_{3,3} = {(l_i, r_j)}, all geodesics l_i-u-w-v-r_j. m = 10: 56 atom-sets / 3 footprints (confirmed exactly). m = 11: 2,958 / 17 and m = 12: 50,123 / 177 (single-sourced, NOT independently re-enumerated — treat as unverified counts).
- All witness atom-sets violate the Cauchy-Schwarz scalar m·Q ≤ T² (m = 9: T = 36, Q = 216, mQ = 1944 > 1296 = T²; confirmed for all m = 9 and m = 10 witnesses). The LocalObstruction catalogue is precisely the finite failure-mode list of the open scalar hypothesis in `Ell5CSReduction.card_support_ge_of_mQ_le_Tsq`.
- Per-edge multiplicity: any constant bound is FALSE — C5[t] blow-ups have μ = t² (μ = 4 witness at N = 10 is exactly C5[2], g6 `I?rFf__{N?`, byte-identical in both codes); C5[t] has Hall slack exactly 4 (|E_short| = 4|S|, verified t = 2, 3 at genuine exhaustive max cuts). Pigeonhole residue: a minimal violator forces some edge with μ ≥ 5, but μ alone does not discriminate books from violators.
- Hall violations at N ≤ 10: ZERO at all 23,449 max cuts (Gamma-min not even needed at that size).

3b. THE DECISIVE COUNTEREXAMPLE (kills bare SSE in real graphs)
24-vertex triangle-free graph, 71 edges (script _claude_v3_refute24_doublestar_realized.py; construction: K_{3,3} cluster l = {0,1,2}, r = {3,4,5}, waist u = 6, w = 7, v = 8, edges l-u, u-w, w-v, v-r; anchor web = 6-layer chain of complete 3x3 bipartite links l-aL-zL-m-zR-aR-r with aL = 9-11, zL = 12-14, m = 15-17, zR = 18-20, aR = 21-23; web l-to-r paths have length 6, parity-compatible, no alternate length-4 geodesics). Exhaustively verified (two independent 2^23 max-cut codes, byte-identical):
- true max cut = 62 = |E| - 9, UNIQUE (hence trivially Gamma-minimal);
- bad set = exactly the 9 cluster edges, each ell = 5, all with unique geodesic l-u-w-v-r (|P_e| = 4);
- E_short(S) = the 8 double-star edges, so |S| = 9 > 8 = |E_short(S)| — a Hall VIOLATION at a genuine Gamma-min maximum cut, all in one component.
Consequences:
- Bare Ell5SupportExpansion (hypotheses: triangle-free + max-cut + Gamma-min + K2-component only) is FALSE. Do not attempt to state or prove it in that form — it is unprovable.
- `NoDoubleStarNine` with hypotheses IsMaxCut + Gamma-min is FALSE (the m = 9 pattern IS realizable).
- No contradiction with anything compiled: `c5book_support_expansion` does not apply there because `hclosed` fails (delta_B({l1,l2,l3}) contains 9 web edges outside E_short); `minimal_hall_obstruction_no_private_edge` is satisfied (|S| = |E_short| + 1, no private edge).
- The BANKED form (25|S| ≤ 25|E_short(S)| + DoorCap + VertexSlackCap + BaseDensityCap + PruneCap) is NOT refuted: the example has 12 door edges at {l1,l2,l3} alone against a deficit of only 25 — the bank absorbs it easily. The counterexample proves the bank terms are NECESSARY.
- Census caveat: no violation exists at N ≤ 10; the minimum violating vertex count is somewhere in 11..24 (untested in between).

3c. SHARPEST SURVIVING LEMMA CANDIDATES (safe to formalize)
1. `geodesics_union_ge_six` (D3.1): for two distinct length-4 path edge sets between the same endpoints in a graph all of whose closed walks are even (or, concretely, in `Distances.blueGraph G c` using `blue_walk_parity`), `6 ≤ (p.edges.toFinset ∪ q.edges.toFinset).card`.
2. `no_minimal_violator_le_six` (D3.3, hand proof) and, computationally extendable, `no_minimal_violator_le_eight` (m = 7, 8 empty — finite decidable checks over ≤ 53 graphs).
3. `footprint_connected` (D3.2) in the abstract Erow style of `minimal_hall_obstruction_no_private_edge`.
None of these touch the wall; all lift the compiled base case |S| ≤ 5 toward |S| ≥ 9 for any violator.

3d. DEAD ENDS — DO NOT RE-TREAD (additions to the standing table in GAP1_SHORTESTSUPPORTEXPANSION_ESCALATION.md)
- Gamma-decrease elimination of the lens: FALSE (the balanced ell=5 theta is Gamma-NEUTRAL, 25+25 to 25+25).
- "Escaping atom implies improving flip" (maximality lever): FALSE — 11-vertex escaping atom at a genuine Gamma-minimal maximum cut (cut 12 = true max), the atom keeps ell = 5 via an alternate outside geodesic (_claude_verify_maxcut_escaping.py, 2^11 exhaustive). The compiled `not_isMaxCut_of_improving_flip` itself stands.
- "Deficiency + minimality force a proper escape closure": FALSE — deficiency is scalar, creates no separator; D = C is realized at a max cut (_claude_escape_closure.py).
- Constant per-edge multiplicity bound at Gamma-min max cuts: FALSE (C5[t], μ = t²).
- Odd-cycle anchor rigidity: FALSE (a bad edge slides along an odd cycle at zero cut cost).
- Bare SSE / NoDoubleStarNine at max-cut + Gamma-min: FALSE (the 24-vertex counterexample, 3b).
- m·Q ≤ T² as a sufficient scalar: fails on every LocalObstruction witness (it is sufficient-not-necessary in the other direction; the catalogue is its failure list).

================================================================================
SECTION 4 — THE HONEST REMAINDER
================================================================================

Exactly ONE crux Prop is open:

  `Erdos23Delta0.Ell5LensStatement.ImpureBalancedNeutralLens_book_or_ledgerSep`
  (an impure balanced-neutral lens yields a C5-book witness OR a ledger-separating prunable subcage)

plus ONE bookkeeping Prop whose mathematics is done but whose Lean proof awaits infrastructure:

  `Erdos23Delta0.Ell5LensStatement.PureLensLedgerSeparation`
  (section 2's S1-S5 + G2 close it once the cage model supplies gamma/Balance/Proper/Bank with contracts G1/G3).

Relations of the crux to the two equivalent frames:

(i) Escape-closure dichotomy. Let D = the escaping closure of the lens shore W (least superset closed under absorbing every atom whose support straddles it). PROPER branch (D strictly smaller than the cage): D is ledger-separating, killed by the compiled `no_ledgerSep_in_minNeg` — this is the `LensReducible` disjunct. FULL branch (D = whole cage): the only remaining contradiction is `0 ≤ Balance C` (FullBankHall), consumed by the compiled `no_balanced_neutral_lens_of_dichotomy`. All shortcuts forcing properness are refuted (section 3d), and the full branch is REAL (11-vertex pattern has D = C). The section-3b counterexample now pins the full branch further: `0 ≤ Balance C` cannot be established via bare support expansion; it must be established in the BANKED currency (DoorCap + VertexSlackCap + C5BaseCap + PruneCap; never the cage's own reserve).

(ii) Dual form. The full branch's banked inequality is exactly `BankedCutDominationCore.BankedCutDomination S F O J K sep dB inc kap` (compiled Prop), and by the compiled finite LP duality over ℚ (`dualCert_iff_not_bankedCutDomination`) its failure is equivalent to an explicit rational dual certificate `IsDualCert`. So the crux has a fully compiled REFUTATION INTERFACE: any candidate proof can be stress-tested by searching for dual certificates on concrete instances (the 24-vertex graph is the first mandatory test article — a correct banked statement must HOLD there, i.e. admit no dual certificate). The compiled primal tooling for the positive direction is `RelaxedCutCover.relaxed_cutcover_defect_bound` / `hall_absorbed_of_bank` / `expansion_of_zero_load` and `RelaxedCoverSkeleton.alpha_paid_or_in_closure`, with `hmcap` discharged per cut by `deltaM_card_le_deltaB_card` (sep k := rows separated by U_k, dB k := deltaB G c.side (U k)).

The binding case remains COUNTERFACTUAL: the hypotheses `hCneg : Balance C < 0` place the cage in a regime (Gamma > N²) that no real triangle-free graph attains. The 24-vertex example is a real graph and correspondingly NOT deficient (Gamma = 225 far below 62²) — it refutes only the un-banked statement, not the ledger-level chain. Empirical calibration: honest probability that the crux's mathematics closes ~50%; full Lean ~12-20%.

================================================================================
SECTION 5 — CODEX TASK LIST (ordered; each item: statement, difficulty, modules touched)
================================================================================

T1. Surface audit of Ell5LensStatement.lean. Rebuild via `python tmp/claude_build_ell5lensstatement.py`; confirm rc = 0, zero `error:`, 16/16 axiom probes clean; cross-check every external declaration in the audit list against source. Difficulty: trivial (verification only). Touches: all nine imported modules, read-only.

T2. `ell_eq_five_of_ell5Atom` (S1). Statement in section 2. Difficulty: easy (dist_le + badEdge_ell_ge_five + omega). Touches: Distances.lean, Ell5AtomBase.lean (read-only); new lemma in a new or existing Ell5 module.

T3. `surplus_split` (S2). Statement in section 2. Difficulty: easy (Finset.sum_union x2, sum_pair, ring). Touches: nothing project-specific (pure Mathlib); place beside NeutralLensLedger.

T4. `pure_lens_ledgerSep` + `no_pure_lens_in_minNeg` (S3 + S4). Statements in section 2. Difficulty: easy (refine + linarith; one application of compiled no_ledgerSep_in_minNeg). Touches: NeutralLensLedger.lean (read-only).

T5. `dist_eq_of_le_of_geodesic_sub` (G2). Statement in section 2. Difficulty: medium-easy (Mathlib Walk.mapLe, Walk.length_map, SimpleGraph.dist_le, Reachable.exists_walk_length_eq_dist). Touches: pure Mathlib; consumed later by the cage model bridge.

T6. `geodesics_union_ge_six` (D3.1). Candidate statement:
```lean
theorem geodesics_union_ge_six {V} [DecidableEq V] {G : SimpleGraph V} {u v : V}
    (p q : G.Walk u v) (hp : p.IsPath) (hq : q.IsPath)
    (hlp : p.length = 4) (hlq : q.length = 4)
    (hbip : ∀ w : G.Walk u u, Even w.length)
    (hne : p.edges.toFinset ≠ q.edges.toFinset) :
    6 ≤ (p.edges.toFinset ∪ q.edges.toFinset).card
```
plus a blueGraph instantiation discharging `hbip` from `Distances.blue_walk_parity`. Difficulty: medium (the symmetric-difference/parity argument needs some walk combinatorics; alternatively a direct case analysis on how two 4-paths with the same endpoints can overlap). Touches: Distances.lean, Ell5CSReduction.lean (geodesic_len4_card_edges), Ell5SupportFinset.lean.

T7. `no_minimal_violator_le_six` then `le_eight`. m = 6 by hand: D3.1 (T6) + compiled `edges_determine_badedge` + `minimal_hall_obstruction_no_private_edge` + C(5,4) = 5 counting. Difficulty: medium. m = 7, 8: currently computational (finite decidable checks over ≤ 53 footprint graphs) — attempt only if a clean abstract argument emerges; do not build a `decide`-monster. Touches: Ell5CSReduction.lean, PathRigidity.lean, Ell5SupportFinset.lean.

T8. Cage-model design module (the load-bearing infrastructure). Define the concrete gamma-type (component/rowDB cage), `Balance := Bank - Surplus`, `Proper` with the G1 semantics (AMBIENT-restricted prunable descendant; explicitly NOT induced-max-cut — record the n = 14 witness as a negative test), `Bank` as a nonnegative-local-term Finset.sum satisfying the G3 superadditivity contract as a structure field, and `Surplus` via T2/T5 so that `hSurplusSplit` follows from strong purity. Deliverable: `PureLensLedgerSeparation` proven for this instantiation (closing open Prop #2). Difficulty: hard (design, not proof; every choice constrained by G1/G3 and by the "never the cage's own reserve" rule). Touches: NeutralLensLedger.lean, Ell5LensStatement.lean, new module.

T9. The crux (`ImpureBalancedNeutralLens_book_or_ledgerSep`). Route through the banked frame ONLY (section 4): primal via RelaxedCutCover/RelaxedCoverSkeleton with `hmcap` from `deltaM_card_le_deltaB_card`; adversarial testing via `BankedCutDominationCore.dualCert_iff_not_bankedCutDomination`. MANDATORY test articles before trusting any candidate statement: (a) the 24-vertex graph of section 3b (bare-SSE killer — a correct banked statement must hold there with exact rational slack), (b) the 11-vertex max-cut escaping-atom pattern, (c) C5[t] blow-ups t = 2, 3 (tight, slack exactly 4). Never re-tread a section-3d dead-end row. Difficulty: OPEN — this is gap#1 itself. Touches: everything.

T10 (parallel, optional). Negative regression gates in Python (not Lean): keep _claude_v3_refute24_doublestar_realized.py and _claude_verify_maxcut_escaping.py runnable as permanent falsifiers; any proposed strengthening of the crux hypotheses must first pass both. Difficulty: trivial. Touches: problems/23/writeup/ scripts only.

Files index (absolute): statement module E:/Projects/ErdosProblems/problems/23/lean/Erdos23Delta0/Ell5LensStatement.lean; compiled base modules in the same directory; build script E:/Projects/ErdosProblems/tmp/claude_build_ell5lensstatement.py; build log E:/Projects/ErdosProblems/tmp/claude_ell5lensstatement_err.txt; olean cache E:/Projects/ErdosProblems/tmp/claude_lean_o_base_v1/; informal archives E:/Projects/ErdosProblems/problems/23/writeup/GAP1_LEDGER_SEPARATION_GPTPRO.md, GAP1_SSE_RELAXEDCUTCOVER_GPTPRO.md, GAP1_SHORTESTSUPPORTEXPANSION_ESCALATION.md (dead-end table), GAP1_FULLSUPPORT_REDUCTION_GPTPRO.md; verification scripts listed in section 3; state E:/Projects/ErdosProblems/LOOP_STATE.md.