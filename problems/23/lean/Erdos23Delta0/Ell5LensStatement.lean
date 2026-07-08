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
