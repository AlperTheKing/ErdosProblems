import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import Mathlib.Combinatorics.SimpleGraph.Girth

open Classical

namespace SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α]

/-- Removing one vertex from a shortest cycle gives an induced tree. -/
theorem girth_sub_one_le_largestInducedTreeSize (G : SimpleGraph α)
    (hcyc : ¬ G.IsAcyclic) :
    G.girth - 1 ≤ largestInducedTreeSize G := by
  obtain ⟨v, c, hc, hc_length⟩ := G.exists_girth_eq_length.mpr hcyc
  let p := c.tail.dropLast
  let s : Finset α := p.support.toFinset
  have hthree : 3 ≤ G.girth := hc.three_le_length.trans_eq hc_length.symm
  have hc_tail_path : c.tail.IsPath := by
    rw [Walk.isPath_def, c.support_tail_of_not_nil hc.not_nil]
    exact hc.support_nodup
  have hp_path : p.IsPath := by
    exact Walk.isPath_of_isSubwalk (Walk.isSubwalk_take c.tail (c.tail.length - 1)) hc_tail_path
  have hp_length : p.length = G.girth - 2 := by
    dsimp [p, Walk.dropLast]
    rw [Walk.take_length, Nat.min_eq_left (Nat.sub_le _ _)]
    have hlen := c.length_tail_add_one hc.not_nil
    rw [← hc_length] at hlen
    omega
  have hs_card : s.card = G.girth - 1 := by
    dsimp [s]
    rw [List.toFinset_card_of_nodup hp_path.support_nodup, Walk.length_support, hp_length]
    omega
  have hp_tree : (G.induce (s : Set α)).IsTree := by
    constructor
    · have hs_set : (s : Set α) = {y : α | y ∈ p.support} := by
        ext y
        simp [s]
      rw [hs_set]
      exact p.connected_induce_support
    · intro x d hd
      let e : G.induce (s : Set α) ↪g G := SimpleGraph.Embedding.induce _
      let q : G.Walk (e x) (e x) := d.map e.toHom
      have hq : q.IsCycle := by
        dsimp [q]
        exact (Walk.map_isCycle_iff_of_injective e.injective).2 hd
      have hd_tail_path : d.tail.IsPath := by
        rw [Walk.isPath_def, d.support_tail_of_not_nil hd.not_nil]
        exact hd.support_nodup
      have hd_length_le : d.length ≤ Fintype.card (s : Set α) := by
        have hlt := hd_tail_path.length_lt
        have hlen := d.length_tail_add_one hd.not_nil
        omega
      have hq_length : q.length = d.length := by simp [q]
      have hg_le : G.girth ≤ q.length := G.girth_le_length hq
      have hs_type_card : Fintype.card (s : Set α) = s.card := by simp
      rw [hq_length] at hg_le
      rw [hs_type_card, hs_card] at hd_length_le
      omega
  have hbound : BddAbove {n : ℕ | ∃ t : Finset α,
      t.card = n ∧ (G.induce (t : Set α)).IsTree} := by
    refine ⟨Fintype.card α, ?_⟩
    rintro n ⟨t, rfl, _⟩
    exact Finset.card_le_univ t
  rw [largestInducedTreeSize]
  exact le_csSup hbound ⟨s, hs_card, hp_tree⟩

end SimpleGraph
