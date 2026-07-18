import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Independence

/-!
Wave 1c for WOWII Conjecture 141: girth bound from a tree path.

For an induced tree `T = G.induce (s : Set α)`, a vertex `z ∉ s` with two
distinct neighbours `a, b ∈ s`, and ANY path `p` in `T` from (the subtype
point over) `a` to (the subtype point over) `b`, we have
`G.girth ≤ p.length + 2`: map `p` into `G`, append the edge `b–z`, and close
the cycle with the edge `z–a`.
-/

namespace SimpleGraph

variable {α : Type*} {G : SimpleGraph α}

/-- Mapping a path of an induced tree into `G` and closing it up through an
outside vertex `z` adjacent to both endpoints produces a cycle of length
`p.length + 2`, so the girth is at most `p.length + 2`. -/
lemma IsTree.girth_le_length_add_two_of_two_adj
    {s : Finset α}
    (_hT : (G.induce (s : Set α)).IsTree)
    {z a b : α}
    (hz : z ∉ s) (ha : a ∈ s) (hb : b ∈ s)
    (hab : a ≠ b) (hza : G.Adj z a) (hzb : G.Adj z b)
    (p : (G.induce (s : Set α)).Walk ⟨a, Finset.mem_coe.mpr ha⟩ ⟨b, Finset.mem_coe.mpr hb⟩)
    (hp : p.IsPath) :
    G.girth ≤ p.length + 2 := by
  let e : G.induce (s : Set α) ↪g G := SimpleGraph.Embedding.induce _
  let q : G.Walk a b := p.map e.toHom
  have hq : q.IsPath := by
    dsimp [q]
    exact (Walk.map_isPath_iff_of_injective e.injective).2 hp
  have hq_length : q.length = p.length := by simp [q]
  have hq_s : ∀ w ∈ q.support, w ∈ s := by
    intro w hw
    dsimp [q] at hw
    rw [Walk.support_map] at hw
    obtain ⟨w', hw', rfl⟩ := List.mem_map.mp hw
    exact w'.property
  have hzq : z ∉ q.support := fun hzmem => hz (hq_s z hzmem)
  let r : G.Walk a z := q.concat hzb.symm
  have hr : r.IsPath := hq.concat hzq hzb.symm
  have hclose : s(z, a) ∉ r.edges := by
    intro he
    dsimp [r] at he
    simp only [Walk.edges_concat, List.concat_eq_append, List.mem_append, List.mem_singleton] at he
    rcases he with he | he
    · exact hzq (q.fst_mem_support_of_mem_edges he)
    · simp only [Sym2.eq, Sym2.rel_iff', Prod.mk.injEq, Prod.swap_prod_mk] at he
      rcases he with ⟨hzb', haz⟩ | ⟨_, hab'⟩
      · exact hza.ne haz.symm
      · exact hab hab'
  let c : G.Walk z z := r.cons hza
  have hc : c.IsCycle := by
    dsimp [c]
    exact (Walk.cons_isCycle_iff r hza).2 ⟨hr, hclose⟩
  have hclen : c.length = q.length + 2 := by simp [c, r]
  have hg := G.girth_le_length hc
  omega

end SimpleGraph
