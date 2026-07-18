import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree

namespace SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α]

/-- A path shorter than the girth by at least one has no ambient chord, so its
support induces a tree. -/
lemma Walk.induce_support_isTree_of_isPath_of_card_lt_girth
    {G : SimpleGraph α} {u v : α} (p : G.Walk u v) (hp : p.IsPath)
    (hlen : p.length + 1 < G.girth) :
    (G.induce (p.support.toFinset : Set α)).IsTree := by
  constructor
  · have hs : (p.support.toFinset : Set α) = {x : α | x ∈ p.support} := by
      ext x
      simp
    rw [hs]
    exact p.connected_induce_support
  · intro x d hd
    let e : G.induce (p.support.toFinset : Set α) ↪g G :=
      SimpleGraph.Embedding.induce _
    let q : G.Walk (e x) (e x) := d.map e.toHom
    have hq : q.IsCycle := by
      dsimp [q]
      exact (Walk.map_isCycle_iff_of_injective e.injective).2 hd
    have hd_tail_path : d.tail.IsPath := by
      rw [Walk.isPath_def, d.support_tail_of_not_nil hd.not_nil]
      exact hd.support_nodup
    have hd_length_le : d.length ≤ Fintype.card (p.support.toFinset : Set α) := by
      have hlt := hd_tail_path.length_lt
      have hlen' := d.length_tail_add_one hd.not_nil
      omega
    have hq_length : q.length = d.length := by
      simp [q]
    have hg_le : G.girth ≤ q.length := G.girth_le_length hq
    have hs_type_card :
        Fintype.card (p.support.toFinset : Set α) = p.support.toFinset.card := by
      rw [← Nat.card_eq_fintype_card, Nat.card_coe_set_eq, Set.ncard_coe_finset]
    have hp_card : p.support.toFinset.card = p.length + 1 := by
      rw [List.toFinset_card_of_nodup hp.support_nodup, p.length_support]
    rw [hq_length] at hg_le
    rw [hs_type_card, hp_card] at hd_length_le
    omega

end SimpleGraph
