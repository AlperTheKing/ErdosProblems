import Erdos23Delta0.Gamma.ActiveScopedMinimumExchange
import Erdos23Delta0.Gamma.CheckedC5BaseTransfer

/-!
# Active-scoped matching with corrected common-blue terminals

The R29 guardrail falsifies the narrower active-scoped source relation.  Its
28-unit deficient shore is repaired by the corrected common-blue terminal
already checked in `CheckedC5BaseTransfer`.

This file makes that monotone relation extension and its finite Hall
equivalence explicit.  It does not assert universal matching existence and it
does not construct the still-missing terminal-to-token or FullBank adapter.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CommonBlueExtendedMatching

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open ActiveScopedMinimumExchange

/-- Repackage a free source and destination owner as the literal corrected
common-blue terminal checked by `CheckedC5BaseTransfer`. -/
def commonBlueTerminalData
    {G : GraphData} {bads : List BadEdgeData} {omega : RowChoice bads}
    (owner : Fin G.n) (s : FreeHalf G omega) :
    CheckedC5BaseTransfer.TerminalData where
  sourceX := s.sourceX.1
  sourceY := s.sourceY.1
  owner := owner.1

/-- A free source is common-blue eligible for an owner exactly when the
production corrected terminal predicate holds on the literal graph and cut. -/
def CommonBlueOwner
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (owner : Fin G.n) (s : FreeHalf G omega) : Prop :=
  (commonBlueTerminalData owner s).Valid G c

noncomputable instance commonBlueOwnerDecidable
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads} :
    DecidableRel (CommonBlueOwner G c (omega := omega)) := by
  intro owner s
  unfold CommonBlueOwner
  infer_instance

/-- The corrected relation keeps every old source arc and adds common-blue
arcs, while preserving the active half-zero reservation exactly. -/
def ExtendedAvailable
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (d : Demand G c omega) (s : FreeHalf G omega) : Prop :=
  (EligibleOwner G c (demandOwner d) s ∨
      CommonBlueOwner G c (demandOwner d) s) ∧
    ¬ScopedReserved G c omega s

noncomputable instance extendedAvailableDecidable
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads} :
    DecidableRel (ExtendedAvailable G c (omega := omega)) :=
  fun _ _ => Classical.propDecidable _

/-- Injective matching for the corrected source relation. -/
structure Matching
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) where
  assign : Demand G c omega → FreeHalf G omega
  injective : Function.Injective assign
  available : ∀ d, ExtendedAvailable G c d (assign d)

/-- Literal finite Hall inequalities for the corrected relation. -/
def HallCondition
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Prop :=
  ∀ A : Finset (Demand G c omega),
    A.card ≤
      (Finset.univ.filter fun s : FreeHalf G omega =>
        ∃ d ∈ A, ExtendedAvailable G c d s).card

/-- Exact finite Hall equivalence for the corrected relation. -/
theorem matching_nonempty_iff_hall
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) :
    Nonempty (Matching G c omega) ↔ HallCondition G c omega := by
  let r := ExtendedAvailable G c (omega := omega)
  have hHall := Fintype.all_card_le_filter_rel_iff_exists_injective r
  constructor
  · rintro ⟨M⟩
    apply hHall.mpr
    exact ⟨M.assign, M.injective, M.available⟩
  · intro h
    rcases hHall.mp h with ⟨assign, hinj, hrel⟩
    exact ⟨⟨assign, hinj, hrel⟩⟩

/-! ## Bank-scale demand

`ResidualSourceTokenization` atomizes one endpoint need into 25 microcopies,
whereas the exploratory active-scoped relation above uses one copy.  The
following type is the exact finite matching target at that production scale.
-/

/-- Collision halves plus 25 microcopies of every residual endpoint need. -/
abbrev MicroDemand
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Type :=
  ActiveCollisionHalf G c omega ⊕ (ActiveHitNeed G c omega × Fin 25)

noncomputable instance microDemandFintype
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) :
    Fintype (MicroDemand G c omega) := by
  unfold MicroDemand
  infer_instance

noncomputable instance microDemandDecidableEq
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) :
    DecidableEq (MicroDemand G c omega) :=
  Classical.decEq _

def microDemandOwner
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads} :
    MicroDemand G c omega → Fin G.n
  | Sum.inl d => d.1.owner
  | Sum.inr h => h.1.1

/-- Corrected source relation at the 25-microcopy endpoint scale. -/
def MicroAvailable
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (d : MicroDemand G c omega) (s : FreeHalf G omega) : Prop :=
  (EligibleOwner G c (microDemandOwner d) s ∨
      CommonBlueOwner G c (microDemandOwner d) s) ∧
    ¬ScopedReserved G c omega s

noncomputable instance microAvailableDecidable
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads} :
    DecidableRel (MicroAvailable G c (omega := omega)) :=
  fun _ _ => Classical.propDecidable _

/-- Injective matching at the exact residual-source microcopy scale. -/
structure MicroMatching
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) where
  assign : MicroDemand G c omega → FreeHalf G omega
  injective : Function.Injective assign
  available : ∀ d, MicroAvailable G c d (assign d)

def MicroHallCondition
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Prop :=
  ∀ A : Finset (MicroDemand G c omega),
    A.card ≤
      (Finset.univ.filter fun s : FreeHalf G omega =>
        ∃ d ∈ A, MicroAvailable G c d s).card

/-- Exact finite Hall equivalence at the production microcopy scale. -/
theorem microMatching_nonempty_iff_hall
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) :
    Nonempty (MicroMatching G c omega) ↔ MicroHallCondition G c omega := by
  let r := MicroAvailable G c (omega := omega)
  have hHall := Fintype.all_card_le_filter_rel_iff_exists_injective r
  constructor
  · rintro ⟨M⟩
    apply hHall.mpr
    exact ⟨M.assign, M.injective, M.available⟩
  · intro h
    rcases hHall.mp h with ⟨assign, hinj, hrel⟩
    exact ⟨⟨assign, hinj, hrel⟩⟩

theorem available_implies_extended
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    {d : Demand G c omega} {s : FreeHalf G omega}
    (h : ActiveScopedMinimumExchange.Available G c d s) :
    ExtendedAvailable G c d s := by
  exact ⟨Or.inl h.1, h.2⟩

/-- The extension is monotone: every old matching remains a corrected
matching. -/
def matchingOfActiveScoped
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (M : ActiveScopedMinimumExchange.Matching G c omega) :
    Matching G c omega where
  assign := M.assign
  injective := M.injective
  available := fun d => available_implies_extended (M.available d)

/-- A common-blue relation edge replays through the kernel Boolean terminal
checker. -/
theorem commonBlue_check_eq_true
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    {owner : Fin G.n} {s : FreeHalf G omega}
    (h : CommonBlueOwner G c owner s) :
    (commonBlueTerminalData owner s).check G c = true := by
  exact (CheckedC5BaseTransfer.TerminalData.check_eq_true_iff
    G c (commonBlueTerminalData owner s)).2 h

/-- Every new relation edge has nonnegative adjusted switch surplus after the
two owner edges are reserved. -/
theorem commonBlue_adjustedSurplus_nonneg
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    {owner : Fin G.n} {s : FreeHalf G omega}
    (h : CommonBlueOwner G c owner s) :
    0 ≤ (commonBlueTerminalData owner s).adjustedSurplus G c := by
  exact CheckedC5BaseTransfer.TerminalData.adjustedSurplus_nonneg h

end CommonBlueExtendedMatching
end Gamma
end Erdos23Delta0
