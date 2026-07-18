import FormalConjecturesUtil

/-!
Scratch file for the main-theorem orchestration of WOWII 141.

The four `scratch_*` declarations below stand only for the already separately
proved path, broom, and star interfaces.  They let this file test witness
selection, the acyclic/cyclic split, and the final Nat/Int arithmetic in
isolation.  They are not intended for the submitted file.
-/

namespace WOWII141MainScratch

open Classical SimpleGraph

variable {α : Type*} [Fintype α] [DecidableEq α]

private axiom scratch_exists_indepSet_finset_neighbors
    (G : SimpleGraph α) (v : α) :
    ∃ I : Finset α, (∀ i ∈ I, G.Adj v i) ∧ G.IsIndepSet (I : Set α) ∧
      I.card = indepNeighborsCard G v

private axiom scratch_isTree_induce_insert_indepSet_neighbors
    {G : SimpleGraph α} (v : α) (I : Finset α)
    (hadj : ∀ i ∈ I, G.Adj v i) (hind : G.IsIndepSet (I : Set α)) :
    (G.induce ((insert v I : Finset α) : Set α)).IsTree

private axiom scratch_exists_isPath_length_eq_of_add_two_le_girth
    {G : SimpleGraph α} (hconn : G.Connected) (hcyc : ¬ G.IsAcyclic)
    (v : α) {r : ℕ} (hr : r + 2 ≤ G.girth) :
    ∃ w : α, ∃ p : G.Walk v w, p.IsPath ∧ p.length = r

private axiom scratch_broom_induced_tree
    {G : SimpleGraph α} {v z : α} {r : ℕ}
    (p : G.Walk v z) (hp : p.IsPath) (hlen : p.length = r)
    (hshort : r + 2 < G.girth) (I : Finset α)
    (hadj : ∀ i ∈ I, G.Adj v i) (hind : G.IsIndepSet (I : Set α)) :
    (G.induce ((I ∪ p.support.toFinset : Finset α) : Set α)).IsTree ∧
      I.card + r ≤ (I ∪ p.support.toFinset).card

omit [DecidableEq α] in
private lemma card_le_largestInducedTreeSize
    {G : SimpleGraph α} {s : Finset α}
    (hs : (G.induce (s : Set α)).IsTree) :
    s.card ≤ largestInducedTreeSize G := by
  unfold largestInducedTreeSize
  apply le_csSup
  · refine ⟨Fintype.card α, ?_⟩
    intro n hn
    obtain ⟨t, rfl, _⟩ := hn
    exact Finset.card_le_univ t
  · exact ⟨s, rfl, hs⟩

theorem main_orchestration (G : SimpleGraph α) [DecidableRel G.Adj]
    [Nontrivial α] (hconn : G.Connected) :
    (G.girth / 2 : ℤ) - 1 + ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  classical
  obtain ⟨v, -, hv⟩ :=
    Finset.exists_mem_eq_sup (Finset.univ : Finset α) Finset.univ_nonempty
      (indepNeighborsCard G)
  obtain ⟨I, hadj, hind, hIcard⟩ :=
    scratch_exists_indepSet_finset_neighbors G v
  have hvI : v ∉ I := fun hvI => G.irrefl (hadj v hvI)
  have hstarTree :
      (G.induce ((insert v I : Finset α) : Set α)).IsTree :=
    scratch_isTree_induce_insert_indepSet_neighbors v I hadj hind
  have hstarCard : I.card + 1 ≤ largestInducedTreeSize G := by
    have hbound := card_le_largestInducedTreeSize hstarTree
    rwa [Finset.card_insert_of_notMem hvI] at hbound
  have hsup : Finset.univ.sup (indepNeighborsCard G) = I.card := by
    exact hv.trans hIcard.symm
  by_cases hcyc : G.IsAcyclic
  · have hg0 : G.girth = 0 := hcyc.girth_eq_zero
    rw [hg0, hsup]
    omega
  · have hg3 : 3 ≤ G.girth := three_le_girth hcyc
    let r : ℕ := G.girth / 2 - 1
    have hr_le : r + 2 ≤ G.girth := by
      dsimp [r]
      omega
    have hr_lt : r + 2 < G.girth := by
      dsimp [r]
      omega
    obtain ⟨z, p, hp, hplen⟩ :=
      scratch_exists_isPath_length_eq_of_add_two_le_girth hconn hcyc v hr_le
    obtain ⟨hTree, hcard⟩ :=
      scratch_broom_induced_tree p hp hplen hr_lt I hadj hind
    have hlarge : (I ∪ p.support.toFinset).card ≤ largestInducedTreeSize G :=
      card_le_largestInducedTreeSize hTree
    have hnat : I.card + r ≤ largestInducedTreeSize G := hcard.trans hlarge
    rw [hsup]
    dsimp [r] at hnat
    omega

end WOWII141MainScratch
