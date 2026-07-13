import Erdos23Delta0.Gamma.CrossStateOppositeCorner
import Erdos23Delta0.CertGraph

/-!
# Literal GraphData adapter for signed cut uncrossing

This identifies the generic rational weighted-cut functional with the actual
`GraphData` switch loss `dB-dM`.  Consequently a real `IsMaxCut` supplies the
nonnegativity premise of cross-state opposite-corner uncrossing.
-/

namespace Erdos23Delta0
namespace Gamma
namespace GraphDataSignedCut

open scoped BigOperators
open CertGraph
open MaxCutVertexIneq
open CanonicalTightCorner
open CrossStateOppositeCorner

def edgeSym (e : Nat × Nat) : Sym2 Nat := s(e.1, e.2)

def signedEdgeWeight (G : GraphData) (c : CutData)
    (e : Nat × Nat) : ℚ :=
  if blueb G c e.1 e.2 then 1 else -1

def cutLossQ (G : GraphData) (c : CutData) (X : Finset Nat) : ℚ :=
  weightedCut G.edges.toFinset edgeSym (signedEdgeWeight G c) X

def oppositeCornerQ (G : GraphData) (c : CutData)
    (X Y : Finset Nat) : ℚ :=
  weightedBetween G.edges.toFinset edgeSym (signedEdgeWeight G c)
    (X \ Y) (Y \ X)

@[simp] theorem edgeBoundary_edgeSym (X : Finset Nat) (e : Nat × Nat) :
    edgeBoundary X (edgeSym e) = crossesSet X.toList e := by
  rcases e with ⟨u, v⟩
  by_cases hu : u ∈ X <;> by_cases hv : v ∈ X <;>
    simp [edgeSym, edgeBoundary, edgeBool, memBool, crossesSet,
      Sym2.lift_mk, hu, hv]

private theorem signed_sum_eq_filter_lengths
    {α : Type*} [DecidableEq α]
    (blue bad boundary : α → Bool) :
    ∀ edges : List α, edges.Nodup →
      (∀ e ∈ edges, blue e = !bad e) →
      (∑ e ∈ edges.toFinset,
          if boundary e then (if blue e then (1 : ℚ) else -1) else 0) =
        ((edges.filter fun e => blue e && boundary e).length : ℚ) -
        ((edges.filter fun e => bad e && boundary e).length : ℚ)
  | [], _, _ => by simp
  | a :: rest, hnodup, hsplit => by
      have haSplit := hsplit a (List.mem_cons_self ..)
      have hrestSplit : ∀ e ∈ rest, blue e = !bad e := by
        intro e he
        exact hsplit e (List.mem_cons_of_mem a he)
      have hrestNodup := (List.nodup_cons.mp hnodup).2
      have haNotMem : a ∉ rest.toFinset := by
        simpa using (List.nodup_cons.mp hnodup).1
      rw [List.toFinset_cons, Finset.sum_insert haNotMem,
        signed_sum_eq_filter_lengths blue bad boundary rest
          hrestNodup hrestSplit]
      cases hblue : blue a <;> cases hbad : bad a <;>
        cases hboundary : boundary a <;>
          simp [hblue, hbad, hboundary] at haSplit ⊢ <;> ring

private theorem graph_edge_blue_not_bad
    (G : GraphData) (c : CutData) (hG : checkGraph G = true) :
    ∀ e ∈ G.edges,
      blueb G c e.1 e.2 = !badb G c e.1 e.2 := by
  intro e he
  unfold checkGraph at hG
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hG
  have hedge := hG.1 e he
  unfold checkEdge at hedge
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hedge
  have hne : e.1 ≠ e.2 := Nat.ne_of_lt hedge.1
  have hadj : adjb G e.1 e.2 = true := by
    unfold adjb normEdge
    simp [hne, hedge.1, he]
  unfold blueb badb
  rw [hadj]
  cases hs1 : sideb c e.1 <;> cases hs2 : sideb c e.2 <;>
    simp [hs1, hs2]

theorem cutLossQ_eq_counts
    (G : GraphData) (c : CutData) (hG : checkGraph G = true)
    (X : Finset Nat) :
    cutLossQ G c X = (dB G c X.toList : ℚ) - (dM G c X.toList : ℚ) := by
  unfold cutLossQ weightedCut signedEdgeWeight dB dM
  simp_rw [edgeBoundary_edgeSym]
  exact signed_sum_eq_filter_lengths
    (fun e => blueb G c e.1 e.2)
    (fun e => badb G c e.1 e.2)
    (fun e => crossesSet X.toList e)
    G.edges
    (by
      have hparts := hG
      unfold checkGraph at hparts
      simp only [Bool.and_eq_true, decide_eq_true_eq] at hparts
      exact hparts.2)
    (graph_edge_blue_not_bad G c hG)

theorem cutLossQ_nonnegative_of_isMaxCut
    (G : GraphData) (c : CutData) (hG : checkGraph G = true)
    (hmax : IsMaxCut G c) (X : Finset Nat) :
    0 ≤ cutLossQ G c X := by
  rw [cutLossQ_eq_counts G c hG X]
  have hs := sigmaNonneg_of_badCount_min G c hG hmax.valid hmax.min_bad X.toList
  unfold sigma at hs
  exact_mod_cast hs

/-- The actual maximum cut forbids strict opposite-corner overweight for any
two graph-only masks, even if they were extracted in different trace states. -/
theorem not_overweight_of_isMaxCut
    (G : GraphData) (c : CutData) (hG : checkGraph G = true)
    (hmax : IsMaxCut G c) (X Y : Finset Nat) :
    ¬(cutLossQ G c X + cutLossQ G c Y <
      2 * oppositeCornerQ G c X Y) := by
  exact not_overweight_of_cut_nonnegative
    G.edges.toFinset edgeSym (signedEdgeWeight G c)
    (cutLossQ_nonnegative_of_isMaxCut G c hG hmax) X Y

#print axioms cutLossQ_eq_counts
#print axioms cutLossQ_nonnegative_of_isMaxCut
#print axioms not_overweight_of_isMaxCut

end GraphDataSignedCut
end Gamma
end Erdos23Delta0
