import Erdos23Delta0.Gamma.CheckedCollisionDefectTrade

namespace R33TradeInstantiationProbe

open Erdos23Delta0.Gamma.CheckedCollisionDefectTrade

inductive RowState where
  | old
  | new
deriving DecidableEq

abbrev Obligation := Fin 1
abbrev SourceBase := Fin 1
abbrev Comp := Unit

def collisionData : Data RowState Obligation SourceBase Comp where
  obligations := fun _ => Finset.univ
  component := fun _ _ => ()
  sourceRealized := fun state _ _ => state = .new

def oldMatching : CoherentPartialMatching collisionData .old :=
  CoherentPartialMatching.empty collisionData .old

def newMatching : CoherentPartialMatching collisionData .new where
  matched := Finset.univ
  matched_subset := by
    intro d _
    change d ∈ (Finset.univ : Finset Obligation)
    exact Finset.mem_univ d
  assign :=
    { toFun := fun _ => (0, 0)
      inj' := fun _ _ _ => Subsingleton.elim _ _ }
  source_realized := by
    intro
    rfl
  base_component_coherent := by
    intro _ _ _
    rfl

theorem every_old_matching_unmatched_one
    (M : CoherentPartialMatching collisionData .old) :
    M.unmatchedCount = 1 := by
  have hmatched : M.matched = ∅ := by
    apply Finset.eq_empty_iff_forall_notMem.mpr
    intro d hd
    let x : {d // d ∈ M.matched} := ⟨d, hd⟩
    exact RowState.noConfusion (M.source_realized x)
  simp [CoherentPartialMatching.unmatchedCount,
    CoherentPartialMatching.unmatched, collisionData, hmatched]

theorem old_defect_eq_one : collisionData.collisionDefect .old = 1 := by
  obtain ⟨M, hM⟩ :=
    collisionData.exists_matching_realizing_collisionDefect .old
  rw [hM, every_old_matching_unmatched_one M]

theorem new_matching_unmatched_zero : newMatching.unmatchedCount = 0 := by
  rw [CoherentPartialMatching.unmatchedCount_eq_card_sub_matched]
  simp [newMatching, collisionData]

theorem new_defect_eq_zero : collisionData.collisionDefect .new = 0 :=
  (collisionData.collisionDefect_eq_zero_iff_exists_total .new).2
    ⟨newMatching, rfl⟩

def trade : CheckedCollisionDefectTrade collisionData (fun _ => True) Unit
    (fun fromState toState _ => fromState = .old ∧ toState = .new) .old where
  old_state_realized := trivial
  newState := .new
  new_state_realized := trivial
  rowChange := ()
  row_change_realized := ⟨rfl, rfl⟩
  oldMatching := oldMatching
  old_defect_eq_unmatched := by
    rw [old_defect_eq_one,
      every_old_matching_unmatched_one oldMatching]
  newMatching := newMatching
  fewer_unmatched := by
    rw [new_matching_unmatched_zero,
      every_old_matching_unmatched_one oldMatching]
    norm_num

theorem tiny_defect_lt :
    collisionData.collisionDefect .new <
      collisionData.collisionDefect .old :=
  defect_lt trade

#print axioms old_defect_eq_one
#print axioms new_defect_eq_zero
#print axioms tiny_defect_lt

end R33TradeInstantiationProbe
