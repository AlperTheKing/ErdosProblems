import Erdos23Delta0.Gamma.SelectedSupportBoundaryExposure
import Erdos23Delta0.Gamma.SoftCapOwnerShoreOverload

/-!
# Outside-boundary P1 injection

If `S` lies in the selected vertex set, every outside blue boundary edge has
exactly one selected endpoint: its endpoint in `S`.  Orienting the edge from
that endpoint to the other one gives a distinct zero-pair base on the P1
owner shore.
-/

namespace Erdos23Delta0
namespace Gamma
namespace OutsideBoundaryP1Injection

open CertGraph
open MinimumDemandRowSelection
open CheckedSelectedSupportSoundness
open SelectedSupportBoundaryExposure
open SoftCapOwnerShoreOverload

noncomputable section

/-- A selected row containing both endpoints would put both in
`selectedVertices`. -/
theorem pairCount_eq_zero_of_endpoint_not_selected
    {bads : List BadEdgeData} (omega : RowChoice bads) (x y : Nat)
    (hnot : x ∉ selectedVertices omega ∨ y ∉ selectedVertices omega) :
    pairCount omega x y = 0 := by
  by_contra hne
  have hpos : 0 < pairCount omega x y := Nat.pos_of_ne_zero hne
  unfold pairCount at hpos
  have hfilter :
      ((selectedRows omega).filter fun row =>
        decide (x ∈ row.verts ∧ y ∈ row.verts)) ≠ [] :=
    List.ne_nil_of_length_pos hpos
  rcases List.exists_mem_of_ne_nil _ hfilter with ⟨row, hrowFilter⟩
  have hrowParts := List.mem_filter.mp hrowFilter
  have hxy : x ∈ row.verts ∧ y ∈ row.verts :=
    of_decide_eq_true hrowParts.2
  have hxSelected : x ∈ selectedVertices omega :=
    mem_selectedVertices_of_mem_selectedRow hrowParts.1 hxy.1
  have hySelected : y ∈ selectedVertices omega :=
    mem_selectedVertices_of_mem_selectedRow hrowParts.1 hxy.2
  exact hnot.elim (fun hx => hx hxSelected) (fun hy => hy hySelected)

/-- The owner shore consisting of the in-range vertices represented in `S`. -/
def selectedInsideShore (G : GraphData) (S : List Nat) :
    Finset (Fin G.n) :=
  Finset.univ.filter fun v => v.1 ∈ S

abbrev OutsideBoundaryEdge
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads) (S : List Nat) : Type :=
  ↥(outsideBlueBoundary G c omega S)

def boundaryInsideEndpoint (S : List Nat) (e : Nat × Nat) : Nat :=
  if e.1 ∈ S then e.1 else e.2

def boundaryOutsideEndpoint (S : List Nat) (e : Nat × Nat) : Nat :=
  if e.1 ∈ S then e.2 else e.1

private theorem boundaryInsideEndpoint_mem
    {S : List Nat} {e : Nat × Nat} (hcross : crossesProp S e) :
    boundaryInsideEndpoint S e ∈ S := by
  by_cases hleft : e.1 ∈ S
  · simp [boundaryInsideEndpoint, hleft]
  · have hright : e.2 ∈ S := by
      unfold crossesProp crossesSet at hcross
      simpa [hleft] using hcross
    simp [boundaryInsideEndpoint, hleft, hright]

private theorem boundaryEndpoints_lt
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) {omega : RowChoice bads} {S : List Nat}
    (e : OutsideBoundaryEdge G c omega S) :
    boundaryInsideEndpoint S e.1 < G.n ∧
      boundaryOutsideEndpoint S e.1 < G.n := by
  classical
  have heG : e.1 ∈ G.edges :=
    List.mem_toFinset.mp (Finset.mem_filter.mp e.2).1
  have hrange := checkGraph_edge_range G hG e.1 heG
  by_cases hleft : e.1.1 ∈ S
  · simp [boundaryInsideEndpoint, boundaryOutsideEndpoint, hleft,
      Nat.lt_trans hrange.1 hrange.2, hrange.2]
  · simp [boundaryInsideEndpoint, boundaryOutsideEndpoint, hleft,
      Nat.lt_trans hrange.1 hrange.2, hrange.2]

def outsideBoundaryInside
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) {omega : RowChoice bads} {S : List Nat}
    (e : OutsideBoundaryEdge G c omega S) : Fin G.n :=
  ⟨boundaryInsideEndpoint S e.1, (boundaryEndpoints_lt hG e).1⟩

def outsideBoundaryOutside
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) {omega : RowChoice bads} {S : List Nat}
    (e : OutsideBoundaryEdge G c omega S) : Fin G.n :=
  ⟨boundaryOutsideEndpoint S e.1, (boundaryEndpoints_lt hG e).2⟩

private theorem outsideBoundaryInside_mem_shore
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) {omega : RowChoice bads} {S : List Nat}
    (e : OutsideBoundaryEdge G c omega S) :
    outsideBoundaryInside hG e ∈ selectedInsideShore G S := by
  classical
  have hcross : crossesProp S e.1 :=
    (Finset.mem_filter.mp e.2).2.2.1
  simp [selectedInsideShore, outsideBoundaryInside,
    boundaryInsideEndpoint_mem hcross]

private theorem outsideBoundaryOutside_not_selected
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) {omega : RowChoice bads} {S : List Nat}
    (hS : ∀ v ∈ S, v ∈ selectedVertices omega)
    (e : OutsideBoundaryEdge G c omega S) :
    (outsideBoundaryOutside hG e).1 ∉ selectedVertices omega := by
  classical
  rcases (Finset.mem_filter.mp e.2).2 with
    ⟨_hblue, hcross, hnotBoth⟩
  by_cases hleft : e.1.1 ∈ S
  · have hleftSelected : e.1.1 ∈ selectedVertices omega := hS _ hleft
    have hrightNot : e.1.2 ∉ selectedVertices omega := by
      intro hrightSelected
      exact hnotBoth ⟨hleftSelected, hrightSelected⟩
    simpa [outsideBoundaryOutside, boundaryOutsideEndpoint, hleft] using
      hrightNot
  · have hright : e.1.2 ∈ S := by
      unfold crossesProp crossesSet at hcross
      simpa [hleft] using hcross
    have hrightSelected : e.1.2 ∈ selectedVertices omega := hS _ hright
    have hleftNot : e.1.1 ∉ selectedVertices omega := by
      intro hleftSelected
      exact hnotBoth ⟨hleftSelected, hrightSelected⟩
    simpa [outsideBoundaryOutside, boundaryOutsideEndpoint, hleft] using
      hleftNot

private theorem normEdge_outsideBoundaryEndpoints
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) {omega : RowChoice bads} {S : List Nat}
    (e : OutsideBoundaryEdge G c omega S) :
    normEdge (outsideBoundaryInside hG e).1
        (outsideBoundaryOutside hG e).1 = e.1 := by
  classical
  have heG : e.1 ∈ G.edges :=
    List.mem_toFinset.mp (Finset.mem_filter.mp e.2).1
  have hnorm := normEdge_eq_self_of_checkGraph hG heG
  by_cases hleft : e.1.1 ∈ S
  · simpa [outsideBoundaryInside, outsideBoundaryOutside,
      boundaryInsideEndpoint, boundaryOutsideEndpoint, hleft] using hnorm
  · have hnormReverse : normEdge e.1.2 e.1.1 = e.1 := by
      rw [normEdge_comm]
      exact hnorm
    simpa [outsideBoundaryInside, outsideBoundaryOutside,
      boundaryInsideEndpoint, boundaryOutsideEndpoint, hleft] using
      hnormReverse

/-- Orient an outside boundary edge from its selected endpoint in `S` to its
unselected endpoint.  Normalization of graph edges makes this orientation
injective even when it reverses the literal edge. -/
def outsideBoundaryP1Injection
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (omega : RowChoice bads) (S : List Nat)
    (hS : ∀ v ∈ S, v ∈ selectedVertices omega) :
    OutsideBoundaryEdge G c omega S ↪
      ShoreZeroBase G omega (selectedInsideShore G S) where
  toFun e :=
    ⟨(outsideBoundaryInside hG e, outsideBoundaryOutside hG e),
      outsideBoundaryInside_mem_shore hG e,
      pairCount_eq_zero_of_endpoint_not_selected omega
        (outsideBoundaryInside hG e).1 (outsideBoundaryOutside hG e).1
        (Or.inr (outsideBoundaryOutside_not_selected hG hS e))⟩
  inj' := by
    intro e f hef
    apply Subtype.ext
    have hpairs :
        ((outsideBoundaryInside hG e).1,
            (outsideBoundaryOutside hG e).1) =
          ((outsideBoundaryInside hG f).1,
            (outsideBoundaryOutside hG f).1) := by
      simpa using congrArg
        (fun p : ShoreZeroBase G omega (selectedInsideShore G S) =>
          (p.1.1.1, p.1.2.1)) hef
    calc
      e.1 = normEdge (outsideBoundaryInside hG e).1
          (outsideBoundaryOutside hG e).1 :=
        (normEdge_outsideBoundaryEndpoints hG e).symm
      _ = normEdge (outsideBoundaryInside hG f).1
          (outsideBoundaryOutside hG f).1 := by
        exact congrArg (fun p : Nat × Nat => normEdge p.1 p.2) hpairs
      _ = f.1 := normEdge_outsideBoundaryEndpoints hG f

theorem outsideBoundaryP1Injection_injective
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (omega : RowChoice bads) (S : List Nat)
    (hS : ∀ v ∈ S, v ∈ selectedVertices omega) :
    Function.Injective
      (outsideBoundaryP1Injection (c := c) hG omega S hS) :=
  (outsideBoundaryP1Injection (c := c) hG omega S hS).injective

/-- Outside blue exposure from a selected set consumes at most one P1
zero-pair source base per edge. -/
theorem outsideBlueBoundary_card_le_shoreZeroBaseUnits
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    (hG : checkGraph G = true) (omega : RowChoice bads) (S : List Nat)
    (hS : ∀ v ∈ S, v ∈ selectedVertices omega) :
    (outsideBlueBoundary G c omega S).card ≤
      shoreZeroBaseUnits G omega (selectedInsideShore G S) := by
  calc
    (outsideBlueBoundary G c omega S).card =
        Fintype.card (OutsideBoundaryEdge G c omega S) := by simp
    _ ≤ Fintype.card
          (ShoreZeroBase G omega (selectedInsideShore G S)) :=
      Fintype.card_le_of_injective
        (outsideBoundaryP1Injection (c := c) hG omega S hS)
        (outsideBoundaryP1Injection (c := c) hG omega S hS).injective
    _ = shoreZeroBaseUnits G omega (selectedInsideShore G S) :=
      shoreZeroBase_card G omega (selectedInsideShore G S)

#print axioms pairCount_eq_zero_of_endpoint_not_selected
#print axioms outsideBoundaryP1Injection_injective
#print axioms outsideBlueBoundary_card_le_shoreZeroBaseUnits

end

end OutsideBoundaryP1Injection
end Gamma
end Erdos23Delta0
