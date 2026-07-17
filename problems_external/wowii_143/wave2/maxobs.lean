import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Degrees
import Mathlib.Data.Set.Finite.Lemmas

namespace SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α] {G : SimpleGraph α}

omit [DecidableEq α] in
/-- If the subgraph induced on all vertices is a tree, the graph is acyclic. -/
lemma isAcyclic_of_induce_finset_univ_isTree
    (h : (G.induce ((Finset.univ : Finset α) : Set α)).IsTree) : G.IsAcyclic := by
  rw [Finset.coe_univ] at h
  intro v c hc
  let f := (induceUnivIso G).symm
  exact h.IsAcyclic (c.map f.toHom)
    ((Walk.map_isCycle_iff_of_injective f.toEmbedding.injective).2 hc)

omit [DecidableEq α] in
/-- A nonempty proper vertex set in a connected graph has an edge across its boundary.

Note: named with a prime because `SimpleGraph.Connected.exists_adj_finset_compl` (identical
statement) was added to `FormalConjecturesForMathlib...LargestInducedTree` by a parallel
session mid-wave; redeclaring the same fully-qualified name is impossible. -/
lemma Connected.exists_adj_finset_compl'
    (hG : G.Connected) {s : Finset α} (hne : s.Nonempty) (hsu : s ≠ Finset.univ) :
    ∃ z ∉ s, ∃ a ∈ s, G.Adj z a := by
  obtain ⟨u, hu⟩ := hne
  have hzex : ∃ z : α, z ∉ s := by
    by_contra hn
    push_neg at hn
    exact hsu (Finset.eq_univ_of_forall hn)
  obtain ⟨z, hz⟩ := hzex
  obtain ⟨p⟩ := hG u z
  obtain ⟨d, _, hd_in, hd_out⟩ :=
    p.exists_boundary_dart (s : Set α) (by simpa) (by simpa)
  exact ⟨d.snd, by simpa using hd_out, d.fst, by simpa using hd_in, d.adj.symm⟩

/-- A boundary vertex of a maximum-cardinality induced tree containing `r` has two
distinct neighbors in the tree. -/
lemma exists_two_adj_of_max_card_induced_tree_superset
    {r s : Finset α} (hG : G.Connected) (hrs : r ⊆ s)
    (hT : (G.induce (s : Set α)).IsTree)
    (hmax : ∀ t : Finset α, r ⊆ t → (G.induce (t : Set α)).IsTree → t.card ≤ s.card)
    (hsu : s ≠ Finset.univ) :
    ∃ z ∉ s, ∃ a ∈ s, ∃ b ∈ s, a ≠ b ∧ G.Adj z a ∧ G.Adj z b := by
  have hne : s.Nonempty := by
    obtain ⟨⟨x, hx⟩⟩ := hT.isConnected.nonempty
    exact ⟨x, by simpa using hx⟩
  obtain ⟨z, hz, a, ha, hza⟩ := hG.exists_adj_finset_compl' hne hsu
  by_cases hex : ∃ b ∈ s, b ≠ a ∧ G.Adj z b
  · obtain ⟨b, hb, hba, hzb⟩ := hex
    exact ⟨z, hz, a, ha, b, hb, hba.symm, hza, hzb⟩
  · have huniq : ∀ ⦃b : α⦄, b ∈ s → G.Adj z b → b = a := by
      intro b hb hzb
      by_contra hba
      exact hex ⟨b, hb, hba, hzb⟩
    have hT' := hT.induce_insert_of_unique_adj hz ha hza huniq
    have hrs' : r ⊆ insert z s := fun v hv => Finset.mem_insert_of_mem (hrs hv)
    have hle := hmax (insert z s) hrs' hT'
    have hcard := Finset.card_insert_of_notMem hz
    omega

end SimpleGraph
