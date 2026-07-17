import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Degrees
import Mathlib.Data.Set.Finite.Lemmas

/-!
Cycle certificates from an induced tree plus an outside vertex with two neighbors
in the tree, for Graffiti.pc / Written on the Wall II Conjecture 143.
-/

namespace SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α] {G : SimpleGraph α}

omit [Fintype α] [DecidableEq α] in
/-- From an induced tree on `s` and a vertex `z ∉ s` with two distinct neighbors
`a, b ∈ s`, produce the tree path `q` from `a` to `b` together with the cycle `c`
obtained by closing it up through `z`. -/
private lemma exists_cycle_data {s : Finset α} (hT : (G.induce (s : Set α)).IsTree)
    {z a b : α} (hz : z ∉ s) (ha : a ∈ s) (hb : b ∈ s) (hab : a ≠ b)
    (hza : G.Adj z a) (hzb : G.Adj z b) :
    ∃ (q : G.Walk a b) (c : G.Walk b b), q.IsPath ∧ c.IsCycle ∧
      (∀ w ∈ q.support, w ∈ s) ∧ c.length = q.length + 2 ∧
      (∀ w ∈ q.support, w ∈ c.support) := by
  obtain ⟨p, hp, -⟩ := hT.existsUnique_path ⟨a, by simpa using ha⟩ ⟨b, by simpa using hb⟩
  let e : G.induce (s : Set α) ↪g G := Embedding.induce _
  let q : G.Walk a b := p.map e.toHom
  have hq : q.IsPath := (Walk.map_isPath_iff_of_injective e.injective).2 hp
  have hqs : ∀ w ∈ q.support, w ∈ s := by
    intro w hw
    dsimp [q] at hw
    rw [Walk.support_map] at hw
    obtain ⟨w', _, rfl⟩ := List.mem_map.mp hw
    exact w'.property
  have hzq : z ∉ q.support := fun h => hz (hqs z h)
  have hw1 : (Walk.cons hza q).IsPath := hq.cons hzq
  let P : G.Path z b := ⟨Walk.cons hza q, hw1⟩
  have he : s(b, z) ∉ (P : G.Walk z b).edges := by
    intro hmem
    rw [Walk.edges_cons, List.mem_cons] at hmem
    rcases hmem with heq | hmem
    · rw [Sym2.eq_iff] at heq
      rcases heq with ⟨hbz, -⟩ | ⟨hba, -⟩
      · exact hz (hbz ▸ hb)
      · exact hab hba.symm
    · exact hzq (Walk.snd_mem_support_of_mem_edges q hmem)
  have hc : (Walk.cons hzb.symm (P : G.Walk z b)).IsCycle := Path.cons_isCycle P hzb.symm he
  refine ⟨q, Walk.cons hzb.symm (P : G.Walk z b), hq, hc, hqs, by simp [P], ?_⟩
  intro w hw
  rw [Walk.support_cons]
  exact List.mem_cons_of_mem _ (by rw [Walk.support_cons]; exact List.mem_cons_of_mem _ hw)

omit [Fintype α] in
/-- Attaching an outside vertex with two neighbors of an induced tree on `s`
creates a cycle of length at most `s.card + 1`, so the girth is at most that. -/
lemma IsTree.girth_le_card_add_one_of_two_adj
    {s : Finset α} (hT : (G.induce (s : Set α)).IsTree) {z a b : α}
    (hz : z ∉ s) (ha : a ∈ s) (hb : b ∈ s) (hab : a ≠ b)
    (hza : G.Adj z a) (hzb : G.Adj z b) :
    G.girth ≤ s.card + 1 := by
  obtain ⟨q, c, hq, hc, hqs, hlen, -⟩ := exists_cycle_data hT hz ha hb hab hza hzb
  have hg : G.girth ≤ c.length := G.girth_le_length hc
  have hsub : q.support.toFinset ⊆ s := fun w hw => hqs w (List.mem_toFinset.mp hw)
  have hcard : q.support.toFinset.card = q.length + 1 := by
    rw [List.toFinset_card_of_nodup hq.support_nodup, Walk.length_support]
  have hle : q.length + 1 ≤ s.card := hcard ▸ Finset.card_le_card hsub
  omega

/-- A vertex of degree one cannot lie on a cycle. -/
private lemma Walk.IsCycle.notMem_support_of_degree_eq_one [DecidableRel G.Adj]
    {v x : α} {c : G.Walk v v} (hc : c.IsCycle) (hx : G.degree x = 1) :
    x ∉ c.support := by
  intro hxc
  let r : G.Walk x x := c.rotate hxc
  have hr : r.IsCycle := hc.rotate hxc
  have hadj_snd : G.Adj x r.snd := r.adj_snd hr.not_nil
  have hadj_pen : G.Adj x r.penultimate := (r.adj_penultimate hr.not_nil).symm
  obtain ⟨u, -, huniq⟩ := degree_eq_one_iff_existsUnique_adj.mp hx
  exact hr.snd_ne_penultimate ((huniq _ hadj_snd).trans (huniq _ hadj_pen).symm)

/-- If the induced tree on `s` contains two leaves of `G` and an outside vertex has
two neighbors in `s`, then the girth is strictly less than `s.card`. -/
lemma IsTree.girth_add_one_le_card_of_two_leaves_of_two_adj
    [DecidableRel G.Adj] {s : Finset α} (hT : (G.induce (s : Set α)).IsTree)
    {x y z a b : α} (hxs : x ∈ s) (hys : y ∈ s) (hxy : x ≠ y)
    (hx : G.degree x = 1) (hy : G.degree y = 1)
    (hz : z ∉ s) (ha : a ∈ s) (hb : b ∈ s) (hab : a ≠ b)
    (hza : G.Adj z a) (hzb : G.Adj z b) :
    G.girth + 1 ≤ s.card := by
  obtain ⟨q, c, hq, hc, hqs, hlen, hsub⟩ := exists_cycle_data hT hz ha hb hab hza hzb
  have hg : G.girth ≤ c.length := G.girth_le_length hc
  have hxq : x ∉ q.support := fun h => hc.notMem_support_of_degree_eq_one hx (hsub x h)
  have hyq : y ∉ q.support := fun h => hc.notMem_support_of_degree_eq_one hy (hsub y h)
  have htcard : q.support.toFinset.card = q.length + 1 := by
    rw [List.toFinset_card_of_nodup hq.support_nodup, Walk.length_support]
  have hyt : y ∉ q.support.toFinset := by simpa using hyq
  have hxyt : x ∉ insert y q.support.toFinset := by
    simp only [Finset.mem_insert, not_or]
    exact ⟨hxy, by simpa using hxq⟩
  have hsubset : insert x (insert y q.support.toFinset) ⊆ s := by
    intro w hw
    rcases Finset.mem_insert.mp hw with rfl | hw
    · exact hxs
    rcases Finset.mem_insert.mp hw with rfl | hw
    · exact hys
    · exact hqs w (List.mem_toFinset.mp hw)
  have hcard2 : (insert x (insert y q.support.toFinset)).card = q.length + 3 := by
    rw [Finset.card_insert_of_notMem hxyt, Finset.card_insert_of_notMem hyt, htcard]
  have hle : q.length + 3 ≤ s.card := hcard2 ▸ Finset.card_le_card hsubset
  omega

end SimpleGraph
