import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import Mathlib.Combinatorics.SimpleGraph.Connectivity.Subgraph
import Mathlib.Combinatorics.SimpleGraph.Girth

/-!
# Lemma M attach machinery for WOWII Conjecture 144 (and 142)

Contents:

* `SimpleGraph.IsTree.induce_union_of_unique_bridge` (**attach primitive**):
  if disjoint vertex sets `S`, `T` both induce trees and there is exactly one
  edge of `G` between `S` and `T`, then `S ∪ T` induces a tree.
* `SimpleGraph.mem_foldr_union`: membership in the fold-union of a list of finsets.
* `SimpleGraph.isTree_induce_union_foldr_of_unique_bridges` (**Lemma M fold**):
  a base induced tree `P` plus a list of pairwise disjoint, pairwise
  non-adjacent induced trees, each sending exactly one edge into `P`, unions to
  an induced tree of cardinality `|P| + Σ|Fᵢ|`.
* `SimpleGraph.card_add_sum_le_largestInducedTreeSize_of_unique_bridges`
  (**Lemma M consumer**): from such data,
  `|P| + Σ|Fᵢ| ≤ largestInducedTreeSize G`.
* `SimpleGraph.exists_induced_tree_finset_card_girth_sub_one`
  (**cycle-side supplier**): a cyclic graph has an induced tree finset of
  cardinality `girth − 1` (a shortest cycle minus one vertex).
* `SimpleGraph.girth_sub_one_add_sum_le_largestInducedTreeSize` (**Lemma M**):
  composition of the supplier with the consumer:
  `girth − 1 + Σ|Fᵢ| ≤ largestInducedTreeSize G`.

"Exactly one edge between `S` and `T`" is modelled as:
`∃ a ∈ S, ∃ b ∈ T, G.Adj a b ∧ ∀ a' ∈ S, ∀ b' ∈ T, G.Adj a' b' → a' = a ∧ b' = b`.
-/

namespace SimpleGraph

variable {α : Type*} {G : SimpleGraph α}

section Attach

variable [DecidableEq α]

/-- **Attach primitive** (Lemma M, step): if `S` and `T` are disjoint finsets,
both induce trees in `G`, and there is exactly one edge of `G` between `S` and
`T` (namely `a-b` with `a ∈ S`, `b ∈ T`), then `S ∪ T` induces a tree.

Connectedness comes from `connected_induce_union`; acyclicity holds because a
cycle in the union would either live inside `S` or inside `T` (contradicting
tree-ness) or cross between the two sides at least twice, forcing the unique
bridge edge to repeat on a trail. -/
lemma IsTree.induce_union_of_unique_bridge {S T : Finset α} {a b : α}
    (hS : (G.induce (S : Set α)).IsTree) (hT : (G.induce (T : Set α)).IsTree)
    (hST : Disjoint S T) (ha : a ∈ S) (hb : b ∈ T) (hab : G.Adj a b)
    (huniq : ∀ a' ∈ S, ∀ b' ∈ T, G.Adj a' b' → a' = a ∧ b' = b) :
    (G.induce ((S ∪ T : Finset α) : Set α)).IsTree := by
  classical
  constructor
  · -- connectedness: glue the two preconnected pieces along the bridge edge
    have hconn := connected_induce_union (v := a) (w := b)
      (s := (S : Set α)) (t := (T : Set α))
      hS.isConnected.preconnected hT.isConnected.preconnected
      (Finset.mem_coe.mpr ha) (Finset.mem_coe.mpr hb) hab
    rw [Finset.coe_union]
    exact hconn
  · -- acyclicity
    intro x c hc
    let e : G.induce ((S ∪ T : Finset α) : Set α) ↪g G := Embedding.induce _
    let q : G.Walk (e x) (e x) := c.map e.toHom
    have hq : q.IsCycle := (Walk.map_isCycle_iff_of_injective e.injective).2 hc
    have hq_mem : ∀ w ∈ q.support, w ∈ S ∪ T := by
      intro w hw
      dsimp [q] at hw
      rw [Walk.support_map] at hw
      obtain ⟨w', _, rfl⟩ := List.mem_map.mp hw
      exact Finset.mem_coe.mp w'.property
    by_cases hallS : ∀ w ∈ q.support, w ∈ (S : Set α)
    · -- the cycle lives inside `S`: lift it into `G.induce S`
      let qi := q.induce (S : Set α) hallS
      have hqi : qi.IsCycle := by
        apply (Walk.map_isCycle_iff_of_injective
          (f := (Embedding.induce (G := G) (S : Set α)).toHom)
          (Embedding.induce (G := G) (S : Set α)).injective).mp
        rw [show qi.map (Embedding.induce (G := G) (S : Set α)).toHom = q from
          Walk.map_induce q hallS]
        exact hq
      exact hS.IsAcyclic qi hqi
    · by_cases hallT : ∀ w ∈ q.support, w ∈ (T : Set α)
      · -- the cycle lives inside `T`: lift it into `G.induce T`
        let qi := q.induce (T : Set α) hallT
        have hqi : qi.IsCycle := by
          apply (Walk.map_isCycle_iff_of_injective
            (f := (Embedding.induce (G := G) (T : Set α)).toHom)
            (Embedding.induce (G := G) (T : Set α)).injective).mp
          rw [show qi.map (Embedding.induce (G := G) (T : Set α)).toHom = q from
            Walk.map_induce q hallT]
          exact hq
        exact hT.IsAcyclic qi hqi
      · -- mixed cycle: it crosses the (unique) bridge in both directions
        push_neg at hallS hallT
        obtain ⟨w₀, hw₀q, hw₀S⟩ := hallS
        obtain ⟨u₀, hu₀q, hu₀T⟩ := hallT
        have hu₀S : u₀ ∈ (S : Set α) := by
          rcases Finset.mem_union.mp (hq_mem u₀ hu₀q) with h | h
          · exact Finset.mem_coe.mpr h
          · exact absurd (Finset.mem_coe.mpr h) hu₀T
        let q' : G.Walk u₀ u₀ := q.rotate hu₀q
        have hq' : q'.IsCycle := hq.rotate hu₀q
        have hw₀q' : w₀ ∈ q'.support := (q.mem_support_rotate_iff hu₀q).mpr hw₀q
        have hq'_mem : ∀ w ∈ q'.support, w ∈ S ∪ T := fun w hw =>
          hq_mem w ((q.mem_support_rotate_iff hu₀q).mp hw)
        -- S → T crossing on the way out, T → S crossing on the way back
        obtain ⟨d₁, hd₁mem, hd₁fst, hd₁snd⟩ :=
          (q'.takeUntil w₀ hw₀q').exists_boundary_dart (S : Set α) hu₀S hw₀S
        obtain ⟨d₂, hd₂mem, hd₂fst, hd₂snd⟩ :=
          (q'.dropUntil w₀ hw₀q').exists_boundary_dart ((S : Set α)ᶜ)
            hw₀S (fun hmem => hmem hu₀S)
        have hd₁darts : d₁ ∈ q'.darts := q'.darts_takeUntil_subset hw₀q' hd₁mem
        have hd₂darts : d₂ ∈ q'.darts := q'.darts_dropUntil_subset hw₀q' hd₂mem
        have hd₁S : d₁.fst ∈ S := Finset.mem_coe.mp hd₁fst
        have hd₁T : d₁.snd ∈ T := by
          rcases Finset.mem_union.mp
            (hq'_mem _ (q'.dart_snd_mem_support_of_mem_darts hd₁darts)) with h | h
          · exact absurd (Finset.mem_coe.mpr h) hd₁snd
          · exact h
        have hd₂T : d₂.fst ∈ T := by
          rcases Finset.mem_union.mp
            (hq'_mem _ (q'.dart_fst_mem_support_of_mem_darts hd₂darts)) with h | h
          · exact absurd (Finset.mem_coe.mpr h) hd₂fst
          · exact h
        have hd₂S : d₂.snd ∈ S := by
          have h := hd₂snd
          simp only [Set.mem_compl_iff, not_not, Finset.mem_coe] at h
          exact h
        obtain ⟨h1a, h1b⟩ := huniq d₁.fst hd₁S d₁.snd hd₁T d₁.adj
        obtain ⟨h2a, h2b⟩ := huniq d₂.snd hd₂S d₂.fst hd₂T d₂.adj.symm
        have hedge : d₁.edge = d₂.edge := by
          have e1 : d₁.edge = s(d₁.fst, d₁.snd) := rfl
          have e2 : d₂.edge = s(d₂.fst, d₂.snd) := rfl
          rw [e1, e2, h1a, h1b, h2a, h2b]
          exact Sym2.eq_swap
        have hnodup : (q'.darts.map Dart.edge).Nodup := hq'.isTrail.edges_nodup
        have hd12 : d₁ = d₂ := List.inj_on_of_nodup_map hnodup hd₁darts hd₂darts hedge
        have hba : a = b := by rw [← h1a, hd12, h2b]
        rw [hba] at ha
        exact Finset.disjoint_left.mp hST ha hb

end Attach

section Fold

variable [DecidableEq α]

/-- Membership in the fold-union of a list of finsets. -/
lemma mem_foldr_union {L : List (Finset α)} {x : α} :
    x ∈ L.foldr (· ∪ ·) ∅ ↔ ∃ F ∈ L, x ∈ F := by
  induction L with
  | nil => simp
  | cons F L ih =>
      simp only [List.foldr_cons, Finset.mem_union, ih, List.mem_cons]
      constructor
      · rintro (h | ⟨F', hF', hx⟩)
        · exact ⟨F, Or.inl rfl, h⟩
        · exact ⟨F', Or.inr hF', hx⟩
      · rintro ⟨F', rfl | hF', hx⟩
        · exact Or.inl hx
        · exact Or.inr ⟨F', hF', hx⟩

/-- **Lemma M fold**: a base induced tree `P` together with a list `L` of
induced trees that are pairwise disjoint, pairwise non-adjacent, disjoint from
`P`, and each sending exactly one edge into `P`, unions to an induced tree on
`|P| + Σ_{F ∈ L} |F|` vertices. -/
theorem isTree_induce_union_foldr_of_unique_bridges {P : Finset α}
    (hP : (G.induce (P : Set α)).IsTree) :
    ∀ L : List (Finset α),
      (∀ F ∈ L, (G.induce (F : Set α)).IsTree) →
      (∀ F ∈ L, Disjoint P F) →
      (∀ F ∈ L, ∃ a ∈ F, ∃ b ∈ P, G.Adj a b ∧
        ∀ a' ∈ F, ∀ b' ∈ P, G.Adj a' b' → a' = a ∧ b' = b) →
      L.Pairwise (fun F F' => Disjoint F F' ∧ ∀ x ∈ F, ∀ y ∈ F', ¬ G.Adj x y) →
      (G.induce ((P ∪ L.foldr (· ∪ ·) ∅ : Finset α) : Set α)).IsTree ∧
        (P ∪ L.foldr (· ∪ ·) ∅).card = P.card + (L.map Finset.card).sum := by
  intro L
  induction L with
  | nil =>
      intro _ _ _ _
      have hPe : (P ∪ ([] : List (Finset α)).foldr (· ∪ ·) ∅ : Finset α) = P := by
        simp
      rw [hPe]
      exact ⟨hP, by simp⟩
  | cons F L ih =>
      intro htrees hdisjP hbridge hpair
      obtain ⟨hpairF, hpairL⟩ := List.pairwise_cons.mp hpair
      obtain ⟨hA, hAcard⟩ := ih
        (fun F' hF' => htrees F' (List.mem_cons_of_mem _ hF'))
        (fun F' hF' => hdisjP F' (List.mem_cons_of_mem _ hF'))
        (fun F' hF' => hbridge F' (List.mem_cons_of_mem _ hF'))
        hpairL
      set A : Finset α := P ∪ L.foldr (· ∪ ·) ∅ with hAdef
      obtain ⟨a, haF, b, hbP, hadj, huniq⟩ := hbridge F (by simp)
      have hdisjAF : Disjoint A F := by
        rw [hAdef, Finset.disjoint_union_left]
        refine ⟨hdisjP F (by simp), ?_⟩
        rw [Finset.disjoint_left]
        intro x hx
        obtain ⟨F', hF', hxF'⟩ := mem_foldr_union.mp hx
        exact fun hxF => Finset.disjoint_left.mp (hpairF F' hF').1 hxF hxF'
      have hbA : b ∈ A := by
        rw [hAdef]
        exact Finset.mem_union_left _ hbP
      have huniq' : ∀ s' ∈ A, ∀ t' ∈ F, G.Adj s' t' → s' = b ∧ t' = a := by
        intro s' hs' t' ht' hadj'
        rw [hAdef] at hs'
        rcases Finset.mem_union.mp hs' with hsP | hsL
        · obtain ⟨h1, h2⟩ := huniq t' ht' s' hsP hadj'.symm
          exact ⟨h2, h1⟩
        · obtain ⟨F', hF', hsF'⟩ := mem_foldr_union.mp hsL
          exact absurd hadj'.symm ((hpairF F' hF').2 t' ht' s' hsF')
      have hTree : (G.induce ((A ∪ F : Finset α) : Set α)).IsTree :=
        hA.induce_union_of_unique_bridge (htrees F (by simp)) hdisjAF hbA haF
          hadj.symm huniq'
      have hset : (P ∪ (F :: L).foldr (· ∪ ·) ∅ : Finset α) = A ∪ F := by
        rw [hAdef]
        ext x
        simp only [List.foldr_cons, Finset.mem_union]
        tauto
      have hcardAF : (A ∪ F).card = A.card + F.card :=
        Finset.card_union_of_disjoint hdisjAF
      constructor
      · rw [hset]
        exact hTree
      · rw [hset, hcardAF, hAcard]
        simp only [List.map_cons, List.sum_cons]
        omega

end Fold

section Consumer

variable [Fintype α] [DecidableEq α]

/-- **Lemma M consumer**: from a base induced tree `P` and a list of pairwise
disjoint, pairwise non-adjacent induced trees each sending exactly one edge
into `P`, one gets `|P| + Σ|Fᵢ| ≤ largestInducedTreeSize G`. -/
theorem card_add_sum_le_largestInducedTreeSize_of_unique_bridges {P : Finset α}
    (hP : (G.induce (P : Set α)).IsTree) (L : List (Finset α))
    (htrees : ∀ F ∈ L, (G.induce (F : Set α)).IsTree)
    (hdisjP : ∀ F ∈ L, Disjoint P F)
    (hbridge : ∀ F ∈ L, ∃ a ∈ F, ∃ b ∈ P, G.Adj a b ∧
        ∀ a' ∈ F, ∀ b' ∈ P, G.Adj a' b' → a' = a ∧ b' = b)
    (hpair : L.Pairwise (fun F F' => Disjoint F F' ∧ ∀ x ∈ F, ∀ y ∈ F', ¬ G.Adj x y)) :
    P.card + (L.map Finset.card).sum ≤ largestInducedTreeSize G := by
  obtain ⟨hT, hcard⟩ :=
    isTree_induce_union_foldr_of_unique_bridges hP L htrees hdisjP hbridge hpair
  have hle := card_le_largestInducedTreeSize hT
  omega

omit [Fintype α] in
/-- **Cycle-side supplier**: a connected cyclic graph contains an induced tree
finset of cardinality `girth − 1` — a shortest cycle minus one vertex.  This is
the witness-exposing version of `girth_sub_one_le_largestInducedTreeSize`. -/
theorem exists_induced_tree_finset_card_girth_sub_one (G : SimpleGraph α)
    (hcyc : ¬ G.IsAcyclic) :
    ∃ P : Finset α, P.card = G.girth - 1 ∧ (G.induce (P : Set α)).IsTree := by
  classical
  obtain ⟨v, c, hc, hc_length⟩ := G.exists_girth_eq_length.mpr hcyc
  let p := c.tail.dropLast
  let s : Finset α := p.support.toFinset
  have hthree : 3 ≤ G.girth := hc.three_le_length.trans_eq hc_length.symm
  have hc_tail_path : c.tail.IsPath := by
    rw [Walk.isPath_def, c.support_tail_of_not_nil hc.not_nil]
    exact hc.support_nodup
  have hp_path : p.IsPath := by
    exact Walk.isPath_of_isSubwalk
      (Walk.isSubwalk_take c.tail (c.tail.length - 1)) hc_tail_path
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
      have hq_length : q.length = d.length := by
        simp [q]
      have hg_le : G.girth ≤ q.length := G.girth_le_length hq
      have hs_type_card : Fintype.card (s : Set α) = s.card := by
        simp
      rw [hq_length] at hg_le
      rw [hs_type_card, hs_card] at hd_length_le
      omega
  exact ⟨s, hs_card, hp_tree⟩

/-- **Lemma M** (composition): in a cyclic graph there is an induced-tree base
`P` of cardinality `girth − 1` (a shortest cycle minus a vertex) such that any
list of pairwise disjoint, pairwise non-adjacent induced trees, each sending
exactly one edge into `P`, certifies
`girth − 1 + Σ|Fᵢ| ≤ largestInducedTreeSize G`. -/
theorem girth_sub_one_add_sum_le_largestInducedTreeSize (G : SimpleGraph α)
    (hcyc : ¬ G.IsAcyclic) :
    ∃ P : Finset α, P.card = G.girth - 1 ∧ (G.induce (P : Set α)).IsTree ∧
      ∀ L : List (Finset α),
        (∀ F ∈ L, (G.induce (F : Set α)).IsTree) →
        (∀ F ∈ L, Disjoint P F) →
        (∀ F ∈ L, ∃ a ∈ F, ∃ b ∈ P, G.Adj a b ∧
          ∀ a' ∈ F, ∀ b' ∈ P, G.Adj a' b' → a' = a ∧ b' = b) →
        L.Pairwise (fun F F' => Disjoint F F' ∧ ∀ x ∈ F, ∀ y ∈ F', ¬ G.Adj x y) →
        G.girth - 1 + (L.map Finset.card).sum ≤ largestInducedTreeSize G := by
  obtain ⟨P, hPcard, hPtree⟩ := exists_induced_tree_finset_card_girth_sub_one G hcyc
  refine ⟨P, hPcard, hPtree, ?_⟩
  intro L htrees hdisjP hbridge hpair
  have h := card_add_sum_le_largestInducedTreeSize_of_unique_bridges hPtree L
    htrees hdisjP hbridge hpair
  omega

end Consumer

end SimpleGraph

#print axioms SimpleGraph.IsTree.induce_union_of_unique_bridge
#print axioms SimpleGraph.isTree_induce_union_foldr_of_unique_bridges
#print axioms SimpleGraph.card_add_sum_le_largestInducedTreeSize_of_unique_bridges
#print axioms SimpleGraph.exists_induced_tree_finset_card_girth_sub_one
#print axioms SimpleGraph.girth_sub_one_add_sum_le_largestInducedTreeSize
