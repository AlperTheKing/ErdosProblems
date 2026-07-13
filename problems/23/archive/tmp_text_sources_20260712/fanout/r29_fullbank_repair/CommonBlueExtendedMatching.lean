import Erdos23Delta0.Gamma.ActiveScopedMinimumExchange
import Erdos23Delta0.Gamma.CheckedC5BaseTransfer

namespace Erdos23Delta0
namespace Gamma
namespace R29FullBankRepair

open CertGraph
open MinimumDemandRowSelection
open CanonicalCollisionHall
open ActiveScopedMinimumExchange

attribute [local instance] Classical.propDecidable

/-- Repackage one FreeHalf and its destination owner as the literal checked
common-blue C5-base terminal already present in production. -/
def commonBlueTerminalData
    {G : GraphData} {bads : List BadEdgeData}
    {omega : RowChoice bads}
    (owner : Fin G.n) (s : FreeHalf G omega) :
    CheckedC5BaseTransfer.TerminalData where
  sourceX := s.sourceX.1
  sourceY := s.sourceY.1
  owner := owner.1

/-- Existing graph-derived common-blue terminal eligibility. -/
def CommonBlueOwner
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (owner : Fin G.n) (s : FreeHalf G omega) : Prop :=
  (commonBlueTerminalData owner s).Valid G c

instance commonBlueOwnerDecidable
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} {omega : RowChoice bads} :
    DecidableRel (CommonBlueOwner G c (omega := omega)) := by
  intro owner s
  unfold CommonBlueOwner
  infer_instance

/-- Monotone repair: retain the auxiliary relation and add the already checked
common-blue terminal, while retaining exactly the same reserved-source rule. -/
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
    DecidableRel (ExtendedAvailable G c (omega := omega)) := by
  intro d s
  unfold ExtendedAvailable
  infer_instance

structure ExtendedMatching
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) where
  assign : Demand G c omega -> FreeHalf G omega
  injective : Function.Injective assign
  available : forall d, ExtendedAvailable G c d (assign d)

def ExtendedHallCondition
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) : Prop :=
  forall A : Finset (Demand G c omega),
    A.card <=
      (Finset.univ.filter fun s : FreeHalf G omega =>
        exists d, d ∈ A ∧ ExtendedAvailable G c d s).card

theorem extendedMatching_nonempty_iff_hall
    (G : GraphData) (c : CutData)
    {bads : List BadEdgeData} (omega : RowChoice bads) :
    Nonempty (ExtendedMatching G c omega) ↔
      ExtendedHallCondition G c omega := by
  let relation := ExtendedAvailable G c (omega := omega)
  have hHall := Fintype.all_card_le_filter_rel_iff_exists_injective relation
  constructor
  · rintro ⟨M⟩
    apply hHall.mpr
    exact ⟨M.assign, M.injective, M.available⟩
  · intro h
    rcases hHall.mp h with ⟨assign, hinjective, havailable⟩
    exact ⟨⟨assign, hinjective, havailable⟩⟩

theorem available_implies_extended
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    {d : Demand G c omega} {s : FreeHalf G omega}
    (h : ActiveScopedMinimumExchange.Available G c d s) :
    ExtendedAvailable G c d s := by
  exact And.intro (Or.inl h.1) h.2

/-- Adding common-blue arcs cannot invalidate any previously passing fixture. -/
def extendedMatching_of_matching
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    (M : ActiveScopedMinimumExchange.Matching G c omega) :
    ExtendedMatching G c omega where
  assign := M.assign
  injective := M.injective
  available := fun d => available_implies_extended (M.available d)

/-- Every new relation edge carries the exact production terminal predicate,
so its adjusted two-edge-reserved switch surplus is nonnegative. -/
theorem commonBlue_adjustedSurplus_nonneg
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData} {omega : RowChoice bads}
    {owner : Fin G.n} {s : FreeHalf G omega}
    (h : CommonBlueOwner G c owner s) :
    0 <= (commonBlueTerminalData owner s).adjustedSurplus G c := by
  exact CheckedC5BaseTransfer.TerminalData.adjustedSurplus_nonneg h

end R29FullBankRepair
end Gamma
end Erdos23Delta0

#print axioms Erdos23Delta0.Gamma.R29FullBankRepair.available_implies_extended
#print axioms Erdos23Delta0.Gamma.R29FullBankRepair.extendedMatching_of_matching
#print axioms Erdos23Delta0.Gamma.R29FullBankRepair.extendedMatching_nonempty_iff_hall
#print axioms Erdos23Delta0.Gamma.R29FullBankRepair.commonBlue_adjustedSurplus_nonneg
