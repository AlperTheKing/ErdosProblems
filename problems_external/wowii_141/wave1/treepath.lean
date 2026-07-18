import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Independence
import Mathlib.Combinatorics.SimpleGraph.Girth

/-!
Tree-path girth certificate for Graffiti.pc / WOWII Conjecture 141: given an
induced tree on `s`, an outside vertex `z` with two distinct neighbours
`a, b ∈ s`, and any path `p` from `a` to `b` inside the induced tree, mapping
`p` into `G` and closing it up through `z` yields a cycle of length
`p.length + 2`, so `G.girth ≤ p.length + 2`.
-/

namespace SimpleGraph

variable {α : Type*} {G : SimpleGraph α}

/-- If `z ∉ s` has two distinct neighbours `a, b ∈ s` and `p` is any path from
`a` to `b` in the induced tree on `s`, then closing `p` up through `z` gives a
cycle in `G` of length `p.length + 2`, hence `G.girth ≤ p.length + 2`. -/
lemma IsTree.girth_le_length_add_two_of_two_adj {s : Finset α} {z a b : α}
    (_hT : (G.induce (s : Set α)).IsTree)
    (hz : z ∉ s) (ha : a ∈ s) (hb : b ∈ s) (hab : a ≠ b)
    (hza : G.Adj z a) (hzb : G.Adj z b)
    (p : (G.induce (s : Set α)).Walk ⟨a, by simpa using ha⟩ ⟨b, by simpa using hb⟩)
    (hp : p.IsPath) :
    G.girth ≤ p.length + 2 := by
  classical
  let e : G.induce (s : Set α) ↪g G := Embedding.induce _
  let q : G.Walk a b := p.map e.toHom
  have hq : q.IsPath := (Walk.map_isPath_iff_of_injective e.injective).2 hp
  have hq_s : ∀ w ∈ q.support, w ∈ s := by
    intro w hw
    dsimp [q] at hw
    rw [Walk.support_map] at hw
    obtain ⟨w', _, rfl⟩ := List.mem_map.mp hw
    exact w'.property
  have hzq : z ∉ q.support := fun hzmem => hz (hq_s z hzmem)
  let r : G.Walk a z := q.concat hzb.symm
  have hr : r.IsPath := hq.concat hzq hzb.symm
  have hclose : s(z, a) ∉ r.edges := by
    intro he
    dsimp [r] at he
    simp only [Walk.edges_concat, List.concat_eq_append, List.mem_append,
      List.mem_singleton] at he
    rcases he with he | he
    · exact hzq (q.fst_mem_support_of_mem_edges he)
    · simp only [Sym2.eq, Sym2.rel_iff', Prod.mk.injEq, Prod.swap_prod_mk] at he
      rcases he with ⟨_, haz⟩ | ⟨_, hab'⟩
      · exact hza.ne haz.symm
      · exact hab hab'
  let c : G.Walk z z := r.cons hza
  have hc : c.IsCycle := by
    dsimp [c]
    exact (Walk.cons_isCycle_iff r hza).2 ⟨hr, hclose⟩
  have hg : G.girth ≤ c.length := G.girth_le_length hc
  have hclen : c.length = q.length + 2 := by simp [c, r]
  have hqlen : q.length = p.length := by simp [q]
  omega

end SimpleGraph
