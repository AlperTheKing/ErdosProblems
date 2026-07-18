import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Independence

/-!
Overlap lemma for WOWII Conjecture 141 (wave1c): on a path in an induced tree,
at most `3` vertices lie in the closed neighborhood of a fixed vertex `v`.

Route: a `G`-edge between two vertices of `s` is an edge of the induced tree;
in a tree the unique path between adjacent vertices is the single edge, so
(i) two neighbors of `v` on the path force `v` itself onto the path, and
(ii) once `v` is on the path, each neighbor of `v` on the path contributes the
edge to `v` as an edge of the path.  A path has at most two edges incident to
any fixed vertex, giving the bound `2 + 1 = 3`.
-/

namespace SimpleGraph

section PathHelpers

variable {β : Type*} {H : SimpleGraph β}

/-- In a path, at most one edge is incident to the first vertex. -/
private lemma path_start_unique_edge {a b u₁ u₂ : β} {p : H.Walk a b}
    (hp : p.IsPath) (h₁ : s(a, u₁) ∈ p.edges) (h₂ : s(a, u₂) ∈ p.edges) :
    u₁ = u₂ := by
  cases p with
  | nil => simp at h₁
  | @cons _ c _ h q =>
      rw [Walk.cons_isPath_iff] at hp
      have key : ∀ u : β, s(a, u) ∈ (Walk.cons h q).edges → u = c := by
        intro u hu
        rw [Walk.edges_cons, List.mem_cons] at hu
        rcases hu with heq | hmem
        · rcases Sym2.eq_iff.mp heq with ⟨-, huc⟩ | ⟨hac, -⟩
          · exact huc
          · exact absurd hac h.ne
        · exact absurd (Walk.fst_mem_support_of_mem_edges q hmem) hp.2
      rw [key u₁ h₁, key u₂ h₂]

/-- In a path, at most two edges are incident to any fixed vertex `w`: among
any three vertices joined to `w` by edges of the path, two coincide. -/
private lemma path_incident_edges_le_two {a b w u₁ u₂ u₃ : β} {p : H.Walk a b}
    (hp : p.IsPath) (h₁ : s(w, u₁) ∈ p.edges) (h₂ : s(w, u₂) ∈ p.edges)
    (h₃ : s(w, u₃) ∈ p.edges) :
    u₁ = u₂ ∨ u₁ = u₃ ∨ u₂ = u₃ := by
  induction p with
  | nil => simp at h₁
  | @cons x c y h q ih =>
      by_cases hwx : w = x
      · subst hwx
        exact Or.inl (path_start_unique_edge hp h₁ h₂)
      · rw [Walk.cons_isPath_iff] at hp
        have key : ∀ u : β, s(w, u) ∈ (Walk.cons h q).edges →
            (u = x ∧ w = c) ∨ s(w, u) ∈ q.edges := by
          intro u hu
          rw [Walk.edges_cons, List.mem_cons] at hu
          rcases hu with heq | hmem
          · rcases Sym2.eq_iff.mp heq with ⟨hwx', -⟩ | ⟨hwc, hux⟩
            · exact absurd hwx' hwx
            · exact Or.inl ⟨hux, hwc⟩
          · exact Or.inr hmem
        rcases key u₁ h₁ with ⟨hu₁, hwc⟩ | m₁
        · rcases key u₂ h₂ with ⟨hu₂, -⟩ | m₂
          · exact Or.inl (hu₁.trans hu₂.symm)
          · rcases key u₃ h₃ with ⟨hu₃, -⟩ | m₃
            · exact Or.inr (Or.inl (hu₁.trans hu₃.symm))
            · subst hwc
              exact Or.inr (Or.inr (path_start_unique_edge hp.1 m₂ m₃))
        · rcases key u₂ h₂ with ⟨hu₂, hwc⟩ | m₂
          · rcases key u₃ h₃ with ⟨hu₃, -⟩ | m₃
            · exact Or.inr (Or.inr (hu₂.trans hu₃.symm))
            · subst hwc
              exact Or.inr (Or.inl (path_start_unique_edge hp.1 m₁ m₃))
          · rcases key u₃ h₃ with ⟨-, hwc⟩ | m₃
            · subst hwc
              exact Or.inl (path_start_unique_edge hp.1 m₁ m₂)
            · exact ih hp.1 m₁ m₂ m₃

/-- A path visiting `a` and `b` contains a subpath between `a` and `b` (in one
of the two directions) whose support and edges lie in the original path. -/
private lemma exists_subpath_between {x y a b : β} {p : H.Walk x y} (hp : p.IsPath)
    (ha : a ∈ p.support) (hb : b ∈ p.support) :
    (∃ q : H.Walk a b, q.IsPath ∧ q.support ⊆ p.support ∧ q.edges ⊆ p.edges) ∨
    (∃ q : H.Walk b a, q.IsPath ∧ q.support ⊆ p.support ∧ q.edges ⊆ p.edges) := by
  classical
  by_cases hbt : b ∈ (p.takeUntil a ha).support
  · exact Or.inr ⟨(p.takeUntil a ha).dropUntil b hbt, (hp.takeUntil ha).dropUntil hbt,
      List.Subset.trans ((p.takeUntil a ha).support_dropUntil_subset hbt)
        (p.support_takeUntil_subset ha),
      List.Subset.trans ((p.takeUntil a ha).edges_dropUntil_subset hbt)
        (p.edges_takeUntil_subset ha)⟩
  · have hbd : b ∈ (p.dropUntil a ha).support := by
      have h2 : b ∈ ((p.takeUntil a ha).append (p.dropUntil a ha)).support := by
        rw [p.take_spec ha]
        exact hb
      rcases (Walk.mem_support_append_iff _ _).mp h2 with hcase | hcase
      · exact absurd hcase hbt
      · exact hcase
    exact Or.inl ⟨(p.dropUntil a ha).takeUntil b hbd, (hp.dropUntil ha).takeUntil hbd,
      List.Subset.trans ((p.dropUntil a ha).support_takeUntil_subset hbd)
        (p.support_dropUntil_subset ha),
      List.Subset.trans ((p.dropUntil a ha).edges_takeUntil_subset hbd)
        (p.edges_dropUntil_subset ha)⟩

/-- In a tree, the unique path between two adjacent vertices is the single edge. -/
private lemma tree_isPath_eq_cons_nil (hH : H.IsTree) {a b : β} (hab : H.Adj a b)
    {q : H.Walk a b} (hq : q.IsPath) :
    q = Walk.cons hab Walk.nil := by
  obtain ⟨P, -, huniq⟩ := hH.existsUnique_path a b
  exact (huniq q hq).trans
    (huniq (Walk.cons hab Walk.nil) (Walk.IsPath.nil.cons (by simp [hab.ne]))).symm

/-- Two path-vertices adjacent (in a tree) to a common vertex `v` force `v`
onto the path: the unique tree path between them is the two-edge path through
`v`, and the subpath of `p` between them must be that path. -/
private lemma tree_center_mem_support (hH : H.IsTree)
    {v a b x y : β} (hva : H.Adj v a) (hvb : H.Adj v b) (hab : a ≠ b)
    {p : H.Walk x y} (hp : p.IsPath) (hap : a ∈ p.support) (hbp : b ∈ p.support) :
    v ∈ p.support := by
  rcases exists_subpath_between hp hap hbp with ⟨q, hq, hqs, -⟩ | ⟨q, hq, hqs, -⟩
  · have hr : (Walk.cons hva.symm (Walk.cons hvb Walk.nil)).IsPath :=
      (Walk.IsPath.nil.cons (by simp [hvb.ne])).cons (by simp [hva.ne', hab])
    obtain ⟨P, -, huniq⟩ := hH.existsUnique_path a b
    have heq : q = Walk.cons hva.symm (Walk.cons hvb Walk.nil) :=
      (huniq q hq).trans (huniq _ hr).symm
    apply hqs
    rw [heq]
    simp
  · have hr : (Walk.cons hvb.symm (Walk.cons hva Walk.nil)).IsPath :=
      (Walk.IsPath.nil.cons (by simp [hva.ne])).cons (by simp [hvb.ne', hab.symm])
    obtain ⟨P, -, huniq⟩ := hH.existsUnique_path b a
    have heq : q = Walk.cons hvb.symm (Walk.cons hva Walk.nil) :=
      (huniq q hq).trans (huniq _ hr).symm
    apply hqs
    rw [heq]
    simp

/-- If `v` lies on a path in a tree and `a` is a path-vertex adjacent to `v`,
then the edge `s(v, a)` is an edge of the path: the subpath of `p` between `v`
and `a` is the unique tree path, which is the single edge. -/
private lemma tree_edge_mem_of_center_mem (hH : H.IsTree)
    {v a x y : β} (hva : H.Adj v a)
    {p : H.Walk x y} (hp : p.IsPath) (hvp : v ∈ p.support) (hap : a ∈ p.support) :
    s(v, a) ∈ p.edges := by
  rcases exists_subpath_between hp hvp hap with ⟨q, hq, -, hqe⟩ | ⟨q, hq, -, hqe⟩
  · have heq := tree_isPath_eq_cons_nil hH hva hq
    apply hqe
    rw [heq]
    simp
  · have heq := tree_isPath_eq_cons_nil hH hva.symm hq
    have hmem : s(a, v) ∈ p.edges := by
      apply hqe
      rw [heq]
      simp
    rwa [Sym2.eq_swap] at hmem

end PathHelpers

variable {α : Type*} [Fintype α] [DecidableEq α] {G : SimpleGraph α}

/-- **Overlap lemma**: on a path `p` in an induced tree on `s`, at most `3`
vertices lie in the closed neighborhood of a fixed vertex `v ∈ s`.  Here the
path support is read off in `α` via `Subtype.val`. -/
lemma IsTree.card_support_inter_closedNeighborFinset_le_three
    [DecidableRel G.Adj] {s : Finset α}
    (hT : (G.induce (s : Set α)).IsTree) {v : α} (hv : v ∈ s)
    {x y : ↥(s : Set α)} {p : (G.induce (s : Set α)).Walk x y} (hp : p.IsPath) :
    ((p.support.map Subtype.val).toFinset ∩ insert v (G.neighborFinset v)).card ≤ 3 := by
  classical
  have hvs : v ∈ (s : Set α) := Finset.mem_coe.mpr hv
  set W : Finset α := (p.support.map Subtype.val).toFinset with hW
  have hmemW : ∀ u : α, u ∈ W ↔ ∃ û : ↥(s : Set α), û ∈ p.support ∧ (û : α) = u := by
    intro u
    simp [hW]
  have hadj_of_mem : ∀ (û : ↥(s : Set α)) (u : α), (û : α) = u → u ∈ G.neighborFinset v →
      (G.induce (s : Set α)).Adj ⟨v, hvs⟩ û := by
    intro û u hûu hu
    rw [induce_adj]
    show G.Adj v (û : α)
    rw [hûu]
    exact (G.mem_neighborFinset v u).mp hu
  have hinter : (W ∩ G.neighborFinset v).card ≤ 2 := by
    by_cases hvW : v ∈ W
    · -- `v` lies on the path: each neighbor of `v` on the path yields an edge of
      -- `p` at `v`, and a path has at most two edges at a fixed vertex.
      have hv'p : (⟨v, hvs⟩ : ↥(s : Set α)) ∈ p.support := by
        obtain ⟨û, hûp, hûv⟩ := (hmemW v).mp hvW
        have hûeq : û = (⟨v, hvs⟩ : ↥(s : Set α)) := Subtype.ext hûv
        rwa [hûeq] at hûp
      by_contra hgt
      push_neg at hgt
      obtain ⟨u₁, u₂, u₃, h1, h2, h3, h12, h13, h23⟩ := Finset.two_lt_card_iff.mp hgt
      obtain ⟨û₁, hû₁p, hû₁⟩ := (hmemW u₁).mp (Finset.mem_inter.mp h1).1
      obtain ⟨û₂, hû₂p, hû₂⟩ := (hmemW u₂).mp (Finset.mem_inter.mp h2).1
      obtain ⟨û₃, hû₃p, hû₃⟩ := (hmemW u₃).mp (Finset.mem_inter.mp h3).1
      have e₁ := tree_edge_mem_of_center_mem hT
        (hadj_of_mem û₁ u₁ hû₁ (Finset.mem_inter.mp h1).2) hp hv'p hû₁p
      have e₂ := tree_edge_mem_of_center_mem hT
        (hadj_of_mem û₂ u₂ hû₂ (Finset.mem_inter.mp h2).2) hp hv'p hû₂p
      have e₃ := tree_edge_mem_of_center_mem hT
        (hadj_of_mem û₃ u₃ hû₃ (Finset.mem_inter.mp h3).2) hp hv'p hû₃p
      rcases path_incident_edges_le_two hp e₁ e₂ e₃ with h | h | h
      · exact h12 (by rw [← hû₁, ← hû₂, h])
      · exact h13 (by rw [← hû₁, ← hû₃, h])
      · exact h23 (by rw [← hû₂, ← hû₃, h])
    · -- `v` off the path: two distinct neighbors of `v` on the path would force
      -- `v` onto the path via the unique two-edge tree path through `v`.
      have hone : (W ∩ G.neighborFinset v).card ≤ 1 := by
        rw [Finset.card_le_one]
        intro u₁ hu₁ u₂ hu₂
        by_contra hne
        obtain ⟨û₁, hû₁p, hû₁⟩ := (hmemW u₁).mp (Finset.mem_inter.mp hu₁).1
        obtain ⟨û₂, hû₂p, hû₂⟩ := (hmemW u₂).mp (Finset.mem_inter.mp hu₂).1
        have hne' : û₁ ≠ û₂ := fun h => hne (by rw [← hû₁, ← hû₂, h])
        have hv'p := tree_center_mem_support hT
          (hadj_of_mem û₁ u₁ hû₁ (Finset.mem_inter.mp hu₁).2)
          (hadj_of_mem û₂ u₂ hû₂ (Finset.mem_inter.mp hu₂).2)
          hne' hp hû₁p hû₂p
        exact hvW ((hmemW v).mpr ⟨⟨v, hvs⟩, hv'p, rfl⟩)
      omega
  have hsub : W ∩ insert v (G.neighborFinset v) ⊆ insert v (W ∩ G.neighborFinset v) := by
    intro u hu
    rw [Finset.mem_inter, Finset.mem_insert] at hu
    rcases hu.2 with rfl | huN
    · exact Finset.mem_insert_self _ _
    · exact Finset.mem_insert_of_mem (Finset.mem_inter.mpr ⟨hu.1, huN⟩)
  calc (W ∩ insert v (G.neighborFinset v)).card
      ≤ (insert v (W ∩ G.neighborFinset v)).card := Finset.card_le_card hsub
    _ ≤ (W ∩ G.neighborFinset v).card + 1 := Finset.card_insert_le _ _
    _ ≤ 3 := by omega

end SimpleGraph
