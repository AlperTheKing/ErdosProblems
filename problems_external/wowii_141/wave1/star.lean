import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Independence

/-!
Star branch for WOWII Conjecture 141: an independent set in a neighbourhood
plus its centre induces a tree, so `indepNeighborsCard G v + 1 ≤
largestInducedTreeSize G`.  Skeleton of the main theorem with the girth ≥ 6
branch left open (gate-dependent).
-/

namespace SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α] {G : SimpleGraph α}

/-- Extract an explicit independent neighbour set witnessing `indepNeighborsCard`. -/
lemma exists_indepSet_finset_neighbors (G : SimpleGraph α) (v : α) :
    ∃ S : Finset α, (∀ s ∈ S, G.Adj v s) ∧ G.IsIndepSet (S : Set α) ∧
      S.card = indepNeighborsCard G v := by
  classical
  obtain ⟨s, hs⟩ := (G.induce (G.neighborSet v)).exists_isNIndepSet_indepNum
  refine ⟨s.image Subtype.val, ?_, ?_, ?_⟩
  · intro x hx
    obtain ⟨y, _, rfl⟩ := Finset.mem_image.mp hx
    exact y.property
  · intro x hx y hy hxy
    obtain ⟨x', hx', rfl⟩ := Finset.mem_image.mp (Finset.mem_coe.mp hx)
    obtain ⟨y', hy', rfl⟩ := Finset.mem_image.mp (Finset.mem_coe.mp hy)
    exact hs.1 hx' hy' (fun h => hxy (congrArg Subtype.val h))
  · rw [Finset.card_image_of_injective _ Subtype.val_injective]
    exact hs.2

omit [Fintype α] in
/-- A vertex together with an independent set of its neighbours induces a star,
hence a tree. -/
lemma isTree_induce_insert_indepSet_neighbors (v : α) (S : Finset α) :
    (∀ s ∈ S, G.Adj v s) → G.IsIndepSet (S : Set α) →
    (G.induce ((insert v S : Finset α) : Set α)).IsTree := by
  classical
  induction S using Finset.induction_on with
  | empty =>
      intro _ _
      have hset : ((insert v (∅ : Finset α) : Finset α) : Set α) = {v} := by simp
      rw [hset]
      letI : Nonempty ↥({v} : Set α) := ⟨⟨v, by simp⟩⟩
      letI : Subsingleton ↥({v} : Set α) := ⟨fun a b => by
        apply Subtype.ext
        have ha : (a : α) = v := by simpa only [Set.mem_singleton_iff] using a.property
        have hb : (b : α) = v := by simpa only [Set.mem_singleton_iff] using b.property
        exact ha.trans hb.symm⟩
      exact IsTree.of_subsingleton
  | @insert s S₀ hs ih =>
      intro hadj hind
      have hadj₀ : ∀ x ∈ S₀, G.Adj v x := fun x hx =>
        hadj x (Finset.mem_insert_of_mem hx)
      have hind₀ : G.IsIndepSet (S₀ : Set α) :=
        hind.mono (Finset.coe_subset.mpr (Finset.subset_insert s S₀))
      have hT := ih hadj₀ hind₀
      have hsv : s ≠ v := (hadj s (Finset.mem_insert_self s S₀)).ne'
      have hzs : s ∉ insert v S₀ := by
        simp only [Finset.mem_insert, not_or]
        exact ⟨hsv, hs⟩
      have hza : G.Adj s v := (hadj s (Finset.mem_insert_self s S₀)).symm
      have huniq : ∀ ⦃b : α⦄, b ∈ insert v S₀ → G.Adj s b → b = v := by
        intro b hb hsb
        rcases Finset.mem_insert.mp hb with rfl | hbS₀
        · rfl
        · exfalso
          have hsS : s ∈ ((insert s S₀ : Finset α) : Set α) := by simp
          have hbS : b ∈ ((insert s S₀ : Finset α) : Set α) := by
            simp only [Finset.coe_insert, Set.mem_insert_iff, Finset.mem_coe]
            exact Or.inr hbS₀
          have hne : s ≠ b := fun h => hs (h ▸ hbS₀)
          exact hind hsS hbS hne hsb
      have hT' := hT.induce_insert_of_unique_adj hzs (Finset.mem_insert_self v S₀) hza huniq
      have hcomm : (insert v (insert s S₀) : Finset α) = insert s (insert v S₀) :=
        Finset.insert_comm v s S₀
      rw [hcomm]
      exact hT'

/-- The star bound: `indepNeighborsCard G v + 1 ≤ largestInducedTreeSize G`. -/
lemma indepNeighborsCard_add_one_le_largestInducedTreeSize (G : SimpleGraph α) (v : α) :
    indepNeighborsCard G v + 1 ≤ largestInducedTreeSize G := by
  classical
  obtain ⟨S, hadj, hind, hcard⟩ := exists_indepSet_finset_neighbors G v
  have hvS : v ∉ S := fun hv => G.irrefl (hadj v hv)
  have hT := isTree_induce_insert_indepSet_neighbors v S hadj hind
  have hbound := card_le_largestInducedTreeSize hT
  rwa [Finset.card_insert_of_notMem hvS, hcard] at hbound

omit [DecidableEq α] in
/-- The independence number of a neighbourhood is at most the degree. -/
lemma indepNeighborsCard_le_degree (G : SimpleGraph α) [DecidableRel G.Adj] (v : α) :
    indepNeighborsCard G v ≤ G.degree v := by
  classical
  obtain ⟨s, hs⟩ := (G.induce (G.neighborSet v)).exists_isNIndepSet_indepNum
  calc indepNeighborsCard G v = s.card := hs.2.symm
    _ ≤ Fintype.card (G.neighborSet v) := Finset.card_le_univ s
    _ = G.degree v := by
        rw [← G.card_neighborSet_eq_degree]

omit [Fintype α] in
/-- Attaching a family of pairwise nonadjacent leaves, each seeing the tree only
in the single vertex `v`, preserves being an induced tree. -/
lemma IsTree.induce_union_leaves {s : Finset α} {v : α}
    (hT : (G.induce (s : Set α)).IsTree) (hv : v ∈ s) (W : Finset α) :
    (∀ w ∈ W, G.Adj v w) → (∀ w ∈ W, w ∉ s) →
    (∀ w ∈ W, ∀ ⦃b : α⦄, b ∈ s → G.Adj w b → b = v) →
    G.IsIndepSet (W : Set α) →
    (G.induce ((s ∪ W : Finset α) : Set α)).IsTree := by
  classical
  induction W using Finset.induction_on with
  | empty =>
      intro _ _ _ _
      rw [Finset.union_empty]
      exact hT
  | @insert w W₀ hw ih =>
      intro hadj hout huniq hind
      have hT₀ := ih (fun x hx => hadj x (Finset.mem_insert_of_mem hx))
        (fun x hx => hout x (Finset.mem_insert_of_mem hx))
        (fun x hx => huniq x (Finset.mem_insert_of_mem hx))
        (hind.mono (Finset.coe_subset.mpr (Finset.subset_insert w W₀)))
      have hwmem : w ∈ insert w W₀ := Finset.mem_insert_self w W₀
      have hzs : w ∉ s ∪ W₀ := by
        simp only [Finset.mem_union, not_or]
        exact ⟨hout w hwmem, hw⟩
      have hva : v ∈ s ∪ W₀ := Finset.mem_union_left _ hv
      have hza : G.Adj w v := (hadj w hwmem).symm
      have huniq' : ∀ ⦃b : α⦄, b ∈ s ∪ W₀ → G.Adj w b → b = v := by
        intro b hb hwb
        rcases Finset.mem_union.mp hb with hbs | hbW₀
        · exact huniq w hwmem hbs hwb
        · exfalso
          have hwS : w ∈ ((insert w W₀ : Finset α) : Set α) := by simp
          have hbS : b ∈ ((insert w W₀ : Finset α) : Set α) := by
            simp only [Finset.coe_insert, Set.mem_insert_iff, Finset.mem_coe]
            exact Or.inr hbW₀
          have hne : w ≠ b := fun h => hw (h ▸ hbW₀)
          exact hind hwS hbS hne hwb
      have hT' := hT₀.induce_insert_of_unique_adj hzs hva hza huniq'
      have hcomm : (s ∪ insert w W₀ : Finset α) = insert w (s ∪ W₀) := by
        ext x
        simp [Finset.mem_union, Finset.mem_insert]
      rw [hcomm]
      exact hT'

/-- Skeleton of Conjecture 141 with the girth ≥ 6 branch left open. -/
theorem conjecture141_skeleton (G : SimpleGraph α) [DecidableRel G.Adj] [Nontrivial α]
    (h : G.Connected) :
    (G.girth / 2 : ℤ) - 1 + ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
    (largestInducedTreeSize G : ℤ) := by
  classical
  obtain ⟨v, -, hv⟩ :=
    Finset.exists_mem_eq_sup (Finset.univ : Finset α) Finset.univ_nonempty
      (indepNeighborsCard G)
  have hstar : Finset.univ.sup (indepNeighborsCard G) + 1 ≤ largestInducedTreeSize G := by
    rw [hv]
    exact indepNeighborsCard_add_one_le_largestInducedTreeSize G v
  by_cases hcyc : G.IsAcyclic
  · have hg0 : G.girth = 0 := hcyc.girth_eq_zero
    rw [hg0]
    push_cast
    omega
  · have hg3 : 3 ≤ G.girth := three_le_girth hcyc
    rcases Nat.lt_or_ge G.girth 6 with hg5 | hg6
    · omega
    · -- girth ≥ 6 branch: star + geodesic construction (gate-dependent)
      sorry

end SimpleGraph
