import Erdos23Delta0.Gamma.CheckedSelectedSupportSoundness

namespace Erdos23Delta0
namespace Gamma
namespace SelectedSupportBoundaryExposure

open CertGraph
open MinimumDemandRowSelection
open SelectedSupportActivePartition
open CheckedSelectedSupportSoundness

noncomputable section

def crossesProp (S : List Nat) (e : Nat × Nat) : Prop :=
  crossesSet S e = true

def supportBoundary (omega : RowChoice bads) (S : List Nat) :
    Finset (Nat × Nat) := by
  classical
  exact (selectedSupport omega).toFinset.filter (crossesProp S)

def activeBoundary (G : GraphData) (c : CutData)
    (omega : RowChoice bads) (S : List Nat) : Finset (Nat × Nat) := by
  classical
  exact (activeEdges G c omega).toFinset.filter (crossesProp S)

def internalBlueBoundary (G : GraphData) (c : CutData)
    (omega : RowChoice bads) (S : List Nat) : Finset (Nat × Nat) := by
  classical
  exact (G.edges.filter (internalBlueb G c omega)).toFinset.filter
    (crossesProp S)

def outsideBlueBoundary (G : GraphData) (c : CutData)
    (omega : RowChoice bads) (S : List Nat) : Finset (Nat × Nat) := by
  classical
  exact G.edges.toFinset.filter fun e =>
    blueb G c e.1 e.2 = true ∧ crossesProp S e ∧
      ¬ (e.1 ∈ selectedVertices omega ∧ e.2 ∈ selectedVertices omega)

def blueBoundary (G : GraphData) (c : CutData) (S : List Nat) :
    Finset (Nat × Nat) := by
  classical
  exact G.edges.toFinset.filter fun e =>
    blueb G c e.1 e.2 = true ∧ crossesProp S e

theorem active_disjoint_support
    (G : GraphData) (c : CutData) (omega : RowChoice bads)
    (hG : checkGraph G = true) :
    Disjoint (activeEdges G c omega).toFinset
      (selectedSupport omega).toFinset := by
  classical
  rw [Finset.disjoint_left]
  intro e hactive hsupport
  have hactiveList : e ∈ activeEdges G c omega := List.mem_toFinset.mp hactive
  have hsupportList : e ∈ selectedSupport omega := List.mem_toFinset.mp hsupport
  unfold activeEdges at hactiveList
  rcases List.mem_filter.mp hactiveList with ⟨heG, hpred⟩
  have hnorm := normEdge_eq_self_of_checkGraph hG heG
  rw [hnorm] at hpred
  simp [hsupportList] at hpred

theorem active_union_support_eq_internal
    (G : GraphData) (c : CutData) (omega : RowChoice bads)
    (hG : checkGraph G = true) (hBads : AllBadsChecked G c bads) :
    (activeEdges G c omega).toFinset ∪ (selectedSupport omega).toFinset =
      (G.edges.filter (internalBlueb G c omega)).toFinset := by
  classical
  ext e
  constructor
  · intro h
    rcases Finset.mem_union.mp h with hactive | hsupport
    · have hactiveList : e ∈ activeEdges G c omega :=
        List.mem_toFinset.mp hactive
      unfold activeEdges at hactiveList
      rcases List.mem_filter.mp hactiveList with ⟨heG, hpred⟩
      simp only [Bool.and_eq_true] at hpred
      exact List.mem_toFinset.mpr
        (List.mem_filter.mpr ⟨heG, by
          simpa [internalBlueb, Bool.and_eq_true] using hpred.1⟩)
    · have hsupportList : e ∈ selectedSupport omega :=
        List.mem_toFinset.mp hsupport
      have hsound :=
        selectedSupport_sound_of_allBadsChecked hBads omega e hsupportList
      exact List.mem_toFinset.mpr (List.mem_filter.mpr hsound)
  · intro h
    have hinternal := List.mem_filter.mp (List.mem_toFinset.mp h)
    by_cases hsupport : e ∈ selectedSupport omega
    · exact Finset.mem_union_right _ (List.mem_toFinset.mpr hsupport)
    · apply Finset.mem_union_left
      apply List.mem_toFinset.mpr
      unfold activeEdges
      apply List.mem_filter.mpr
      refine ⟨hinternal.1, ?_⟩
      have hnorm := normEdge_eq_self_of_checkGraph hG hinternal.1
      simp only [internalBlueb, Bool.and_eq_true] at hinternal
      simp [hinternal.2.1.1, hinternal.2.1.2, hinternal.2.2,
        hnorm, hsupport]

theorem internal_boundary_eq_active_union_support
    (G : GraphData) (c : CutData) (omega : RowChoice bads) (S : List Nat)
    (hG : checkGraph G = true) (hBads : AllBadsChecked G c bads) :
    internalBlueBoundary G c omega S =
      activeBoundary G c omega S ∪ supportBoundary omega S := by
  classical
  unfold internalBlueBoundary activeBoundary supportBoundary
  rw [← Finset.filter_union]
  rw [active_union_support_eq_internal G c omega hG hBads]

theorem internal_boundary_card
    (G : GraphData) (c : CutData) (omega : RowChoice bads) (S : List Nat)
    (hG : checkGraph G = true) (hBads : AllBadsChecked G c bads) :
    (internalBlueBoundary G c omega S).card =
      (activeBoundary G c omega S).card + (supportBoundary omega S).card := by
  classical
  rw [internal_boundary_eq_active_union_support G c omega S hG hBads]
  apply Finset.card_union_of_disjoint
  rw [Finset.disjoint_left]
  intro e ha hs
  have ha0 : e ∈ (activeEdges G c omega).toFinset :=
    (Finset.mem_filter.mp ha).1
  have hs0 : e ∈ (selectedSupport omega).toFinset :=
    (Finset.mem_filter.mp hs).1
  exact (Finset.disjoint_left.mp
    (active_disjoint_support G c omega hG)) ha0 hs0

theorem blue_boundary_eq_internal_union_outside
    (G : GraphData) (c : CutData) (omega : RowChoice bads) (S : List Nat) :
    blueBoundary G c S =
      internalBlueBoundary G c omega S ∪ outsideBlueBoundary G c omega S := by
  classical
  ext e
  constructor
  · intro h
    rcases Finset.mem_filter.mp h with ⟨heG, hblue, hcross⟩
    by_cases hboth :
        e.1 ∈ selectedVertices omega ∧ e.2 ∈ selectedVertices omega
    · apply Finset.mem_union_left
      apply Finset.mem_filter.mpr
      refine ⟨?_, hcross⟩
      apply List.mem_toFinset.mpr
      apply List.mem_filter.mpr
      refine ⟨List.mem_toFinset.mp heG, ?_⟩
      simp [internalBlueb, hboth.1, hboth.2, hblue]
    · apply Finset.mem_union_right
      exact Finset.mem_filter.mpr ⟨heG, hblue, hcross, hboth⟩
  · intro h
    rcases Finset.mem_union.mp h with hi | ho
    · rcases Finset.mem_filter.mp hi with ⟨hiBase, hiCross⟩
      rcases List.mem_filter.mp (List.mem_toFinset.mp hiBase) with
        ⟨heG, hiInternal⟩
      simp only [internalBlueb, Bool.and_eq_true] at hiInternal
      exact Finset.mem_filter.mpr
        ⟨List.mem_toFinset.mpr heG, hiInternal.2, hiCross⟩
    · rcases Finset.mem_filter.mp ho with ⟨heG, hblue, hcross, _⟩
      exact Finset.mem_filter.mpr ⟨heG, hblue, hcross⟩
theorem internal_disjoint_outside
    (G : GraphData) (c : CutData) (omega : RowChoice bads) (S : List Nat) :
    Disjoint (internalBlueBoundary G c omega S)
      (outsideBlueBoundary G c omega S) := by
  classical
  rw [Finset.disjoint_left]
  intro e hi ho
  have hiBase := (Finset.mem_filter.mp hi).1
  have hiList := List.mem_toFinset.mp hiBase
  have hiInternal := (List.mem_filter.mp hiList).2
  simp only [internalBlueb, Bool.and_eq_true] at hiInternal
  have hsel1 : e.1 ∈ selectedVertices omega :=
    of_decide_eq_true hiInternal.1.1
  have hsel2 : e.2 ∈ selectedVertices omega :=
    of_decide_eq_true hiInternal.1.2
  have hoPred := (Finset.mem_filter.mp ho).2
  exact hoPred.2.2 ⟨hsel1, hsel2⟩
theorem dB_eq_support_add_exposure
    (G : GraphData) (c : CutData) (omega : RowChoice bads) (S : List Nat)
    (hG : checkGraph G = true) (hBads : AllBadsChecked G c bads) :
    dB G c S =
      (supportBoundary omega S).card + (activeBoundary G c omega S).card +
        (outsideBlueBoundary G c omega S).card := by
  classical
  have hblueCard : (blueBoundary G c S).card = dB G c S := by
    unfold blueBoundary dB
    rw [← List.toFinset_card_of_nodup
      ((checkGraph_edges_nodup G hG).filter _)]
    congr 1
    ext e
    simp [crossesProp, Bool.and_eq_true]
  rw [← hblueCard, blue_boundary_eq_internal_union_outside]
  rw [Finset.card_union_of_disjoint (internal_disjoint_outside G c omega S)]
  rw [internal_boundary_card G c omega S hG hBads]
  omega

theorem support_deficit_le_exposure
    (G : GraphData) (c : CutData) (omega : RowChoice bads) (S : List Nat)
    (hG : checkGraph G = true) (hBads : AllBadsChecked G c bads)
    (hSigma : 0 ≤ sigma G c S) :
    dM G c S ≤
      (supportBoundary omega S).card + (activeBoundary G c omega S).card +
        (outsideBlueBoundary G c omega S).card := by
  rw [← dB_eq_support_add_exposure G c omega S hG hBads]
  unfold sigma at hSigma
  omega

#print axioms dB_eq_support_add_exposure
#print axioms support_deficit_le_exposure

end

end SelectedSupportBoundaryExposure
end Gamma
end Erdos23Delta0
