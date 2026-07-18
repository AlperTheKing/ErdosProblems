import FormalConjectures.WrittenOnTheWallII.GraphConjecture314
import Mathlib.Combinatorics.SimpleGraph.Acyclic
import Mathlib.Combinatorics.SimpleGraph.Circulant
import Mathlib.Combinatorics.SimpleGraph.Bipartite

/-!
# Direct-route lemmas for WOWII Conjecture 314

This scratch module formalizes the induced-`P₅` exclusion (route lemma `L0`)
and reusable total-domination facts without changing the target conjecture.
-/

open Classical

namespace WOWII314.FormalCandidates

open SimpleGraph

lemma pathGraph_five_isTree : (pathGraph 5).IsTree := by
  rw [isTree_iff_connected_and_card]
  constructor
  · simpa using pathGraph_connected 4
  · have hedge : (pathGraph 5).edgeFinset =
        {s(0, 1), s(1, 2), s(2, 3), s(3, 4)} := by
      ext e
      induction e using Sym2.inductionOn with
      | _ u v =>
          fin_cases u <;> fin_cases v <;> simp [pathGraph_adj]
    rw [Nat.card_eq_fintype_card, ← edgeFinset_card, hedge]
    norm_num [Nat.card_eq_fintype_card, Finset.card_insert_eq_ite, Sym2.eq_iff, Fin.ext_iff]

lemma pathGraph_five_degree_le_two (v : Fin 5) :
    (pathGraph 5).degree v ≤ 2 := by
  fin_cases v
  · unfold SimpleGraph.degree
    change ((pathGraph 5).neighborFinset (0 : Fin 5)).card ≤ 2
    rw [show (pathGraph 5).neighborFinset (0 : Fin 5) = {1} by
      ext w
      fin_cases w <;> simp [pathGraph_adj]]
    decide
  · unfold SimpleGraph.degree
    change ((pathGraph 5).neighborFinset (1 : Fin 5)).card ≤ 2
    rw [show (pathGraph 5).neighborFinset (1 : Fin 5) = {0, 2} by
      ext w
      fin_cases w <;> simp [pathGraph_adj]]
    decide
  · unfold SimpleGraph.degree
    change ((pathGraph 5).neighborFinset (2 : Fin 5)).card ≤ 2
    rw [show (pathGraph 5).neighborFinset (2 : Fin 5) = {1, 3} by
      ext w
      fin_cases w <;> simp [pathGraph_adj]]
    decide
  · unfold SimpleGraph.degree
    change ((pathGraph 5).neighborFinset (3 : Fin 5)).card ≤ 2
    rw [show (pathGraph 5).neighborFinset (3 : Fin 5) = {2, 4} by
      ext w
      fin_cases w <;> simp [pathGraph_adj]]
    decide
  · unfold SimpleGraph.degree
    change ((pathGraph 5).neighborFinset (4 : Fin 5)).card ≤ 2
    rw [show (pathGraph 5).neighborFinset (4 : Fin 5) = {3} by
      ext w
      fin_cases w <;> simp [pathGraph_adj]]
    decide

noncomputable def embeddingRangeIso {V W : Type*} [Fintype V] [DecidableEq W]
    {H : SimpleGraph V}
    {G : SimpleGraph W} (e : H ↪g G) : H ≃g G.induce (Set.range e) where
  toEquiv := e.toEmbedding.toEquivRange
  map_rel_iff' := by
    intro a b
    exact e.map_adj_iff


open WrittenOnTheWallII.GraphConjecture314

lemma largestInducedPathSize_ge_five_of_embedding
    {α : Type*} [Fintype α] [DecidableEq α]
    (G : SimpleGraph α) [DecidableRel G.Adj]
    (e : pathGraph 5 ↪g G) :
    5 ≤ largestInducedPathSize G := by
  let s : Finset α := Finset.univ.map e.toEmbedding
  have hs_card : s.card = 5 := by
    simp [s]
  have hs_coe : (s : Set α) = Set.range e := by
    ext x
    simp [s]
  have hs_tree : (G.induce (s : Set α)).IsTree := by
    rw [hs_coe]
    exact (embeddingRangeIso e).isTree_iff.mp pathGraph_five_isTree
  have hs_degree :
      ∀ v : (s : Set α), (G.induce (s : Set α)).degree v ≤ 2 := by
    let f : pathGraph 5 ≃g G.induce (s : Set α) := by
      rw [hs_coe]
      exact embeddingRangeIso e
    intro v
    calc
      (G.induce (s : Set α)).degree v =
          (pathGraph 5).degree (f.symm v) := by
            simpa [f] using f.degree_eq (f.symm v)
      _ ≤ 2 := pathGraph_five_degree_le_two (f.symm v)
  unfold largestInducedPathSize
  apply le_csSup
  · refine ⟨Fintype.card α, ?_⟩
    rintro n ⟨t, ht_card, _, _⟩
    simpa [← ht_card] using t.card_le_univ
  · exact ⟨s, hs_card, hs_tree, hs_degree⟩

lemma L0_no_induced_pathGraph_five
    {α : Type*} [Fintype α] [DecidableEq α]
    (G : SimpleGraph α) [DecidableRel G.Adj]
    (hPath : largestInducedPathSize G ≤ 4) :
    ¬SimpleGraph.IsIndContained (pathGraph 5) G := by
  rintro ⟨e⟩
  have hfive := largestInducedPathSize_ge_five_of_embedding G e
  omega


lemma minimalTDS_erase_not_total
    {α : Type*} [Fintype α] [DecidableEq α]
    {G : SimpleGraph α} [DecidableRel G.Adj]
    {S : Finset α} (hS : IsMinimalTotalDominatingSet G S)
    {v : α} (hv : v ∈ S) :
    ¬IsTotalDominatingSet G (S.erase v) :=
  hS.2 _ (Finset.erase_ssubset hv)

lemma minimalTDS_exists_private_neighbor
    {α : Type*} [Fintype α] [DecidableEq α]
    {G : SimpleGraph α} [DecidableRel G.Adj]
    {S : Finset α} (hS : IsMinimalTotalDominatingSet G S)
    {v : α} (hv : v ∈ S) :
    ∃ x : α, G.Adj x v ∧ ∀ w ∈ S, G.Adj x w → w = v := by
  have hnot := minimalTDS_erase_not_total hS hv
  unfold IsTotalDominatingSet at hnot
  push_neg at hnot
  obtain ⟨x, hx⟩ := hnot
  obtain ⟨w, hwS, hxw⟩ := hS.1 x
  have hwv : w = v := by
    by_contra hwne
    exact (hx w (Finset.mem_erase.mpr ⟨hwne, hwS⟩)) hxw
  subst w
  refine ⟨x, hxw, ?_⟩
  intro y hyS hxy
  by_contra hyne
  exact (hx y (Finset.mem_erase.mpr ⟨hyne, hyS⟩)) hxy

lemma minimalTDS_not_both_of_same_open_neighborhood
    {α : Type*} [Fintype α] [DecidableEq α]
    {G : SimpleGraph α} [DecidableRel G.Adj]
    {S : Finset α} (hS : IsMinimalTotalDominatingSet G S)
    {u v : α} (hu : u ∈ S) (hv : v ∈ S) (hne : u ≠ v)
    (htwin : ∀ x : α, G.Adj x u ↔ G.Adj x v) :
    False := by
  apply minimalTDS_erase_not_total hS hv
  intro x
  obtain ⟨w, hwS, hxw⟩ := hS.1 x
  by_cases hwv : w = v
  · subst w
    exact ⟨u, Finset.mem_erase.mpr ⟨hne, hu⟩, (htwin x).mpr hxw⟩
  · exact ⟨w, Finset.mem_erase.mpr ⟨hwv, hwS⟩, hxw⟩


lemma minimalTDS_not_both_of_neighborSet_subset
    {α : Type*} [Fintype α] [DecidableEq α]
    {G : SimpleGraph α} [DecidableRel G.Adj]
    {S : Finset α} (hS : IsMinimalTotalDominatingSet G S)
    {u v : α} (hu : u ∈ S) (hv : v ∈ S) (hne : u ≠ v)
    (hsub : G.neighborSet u ⊆ G.neighborSet v) :
    False := by
  apply minimalTDS_erase_not_total hS hu
  intro x
  obtain ⟨w, hwS, hxw⟩ := hS.1 x
  by_cases hwu : w = u
  · subst w
    exact ⟨v, Finset.mem_erase.mpr ⟨hne.symm, hv⟩, (hsub hxw.symm).symm⟩
  · exact ⟨w, Finset.mem_erase.mpr ⟨hwu, hwS⟩, hxw⟩

lemma L4_minimalTDS_card_eq_two_of_nested_bipartition
    {α : Type*} [Fintype α] [DecidableEq α]
    {G : SimpleGraph α} [DecidableRel G.Adj]
    {X : Set α}
    (hbip : G.IsBipartiteWith X Xᶜ)
    (hX : X.Nonempty) (hY : Xᶜ.Nonempty)
    (hNestX : ∀ {u v : α}, u ∈ X → v ∈ X →
      G.neighborSet u ⊆ G.neighborSet v ∨
      G.neighborSet v ⊆ G.neighborSet u)
    (hNestY : ∀ {u v : α}, u ∉ X → v ∉ X →
      G.neighborSet u ⊆ G.neighborSet v ∨
      G.neighborSet v ⊆ G.neighborSet u)
    {S : Finset α} (hS : IsMinimalTotalDominatingSet G S) :
    S.card = 2 := by
  have hSX_nonempty : (S.filter fun z => z ∈ X).Nonempty := by
    obtain ⟨y, hy⟩ := hY
    obtain ⟨w, hwS, hyw⟩ := hS.1 y
    refine ⟨w, Finset.mem_filter.mpr ⟨hwS, ?_⟩⟩
    exact hbip.mem_of_mem_adj' hy hyw.symm
  have hSY_nonempty : (S.filter fun z => z ∉ X).Nonempty := by
    obtain ⟨x, hx⟩ := hX
    obtain ⟨w, hwS, hxw⟩ := hS.1 x
    refine ⟨w, Finset.mem_filter.mpr ⟨hwS, ?_⟩⟩
    simpa only [Set.mem_compl_iff] using hbip.mem_of_mem_adj hx hxw
  have hSX_le : (S.filter fun z => z ∈ X).card ≤ 1 := by
    rw [Finset.card_le_one_iff]
    intro u v hu hv
    simp only [Finset.mem_filter] at hu hv
    by_contra hne
    rcases hNestX hu.2 hv.2 with huv | hvu
    · exact minimalTDS_not_both_of_neighborSet_subset hS hu.1 hv.1 hne huv
    · exact minimalTDS_not_both_of_neighborSet_subset hS hv.1 hu.1
        (fun h => hne h.symm) hvu
  have hSY_le : (S.filter fun z => z ∉ X).card ≤ 1 := by
    rw [Finset.card_le_one_iff]
    intro u v hu hv
    simp only [Finset.mem_filter] at hu hv
    by_contra hne
    rcases hNestY hu.2 hv.2 with huv | hvu
    · exact minimalTDS_not_both_of_neighborSet_subset hS hu.1 hv.1 hne huv
    · exact minimalTDS_not_both_of_neighborSet_subset hS hv.1 hu.1
        (fun h => hne h.symm) hvu
  have hSX_card : (S.filter fun z => z ∈ X).card = 1 := by
    have hpos := Finset.card_pos.mpr hSX_nonempty
    omega
  have hSY_card : (S.filter fun z => z ∉ X).card = 1 := by
    have hpos := Finset.card_pos.mpr hSY_nonempty
    omega
  have hsplit :=
    Finset.card_filter_add_card_filter_not (s := S) (fun z : α => z ∈ X)
  omega


def c5ConsecutiveTriple (m : Fin 5) : Finset (Fin 5) :=
  {m + 1, m + 2, m + 3}

lemma c5ConsecutiveTriple_isTotalDominatingSet (m : Fin 5) :
    IsTotalDominatingSet (cycleGraph 5) (c5ConsecutiveTriple m) := by
  unfold IsTotalDominatingSet c5ConsecutiveTriple
  fin_cases m <;> intro x <;> fin_cases x <;> decide

lemma c5ConsecutiveTriple_ssubset_compl_singleton (m : Fin 5) :
    c5ConsecutiveTriple m ⊂ ({m} : Finset (Fin 5))ᶜ := by
  fin_cases m <;> decide


lemma cycleGraph_five_pair_not_total (u v : Fin 5) :
    ¬IsTotalDominatingSet (cycleGraph 5) ({u, v} : Finset (Fin 5)) := by
  unfold IsTotalDominatingSet
  intro h
  fin_cases u <;> fin_cases v <;>
    first
    | have hz := h (0 : Fin 5)
      rcases hz with ⟨w, hw, hadj⟩
      fin_cases w <;> simp [cycleGraph_adj, Fin.ext_iff] at hw hadj
    | have hz := h (1 : Fin 5)
      rcases hz with ⟨w, hw, hadj⟩
      fin_cases w <;> simp [cycleGraph_adj, Fin.ext_iff] at hw hadj
    | have hz := h (2 : Fin 5)
      rcases hz with ⟨w, hw, hadj⟩
      fin_cases w <;> simp [cycleGraph_adj, Fin.ext_iff] at hw hadj
    | have hz := h (3 : Fin 5)
      rcases hz with ⟨w, hw, hadj⟩
      fin_cases w <;> simp [cycleGraph_adj, Fin.ext_iff] at hw hadj
    | have hz := h (4 : Fin 5)
      rcases hz with ⟨w, hw, hadj⟩
      fin_cases w <;> simp [cycleGraph_adj, Fin.ext_iff] at hw hadj


lemma cycleGraph_five_totalDominatingSet_card_ge_three
    (S : Finset (Fin 5))
    (hS : IsTotalDominatingSet (cycleGraph 5) S) :
    3 ≤ S.card := by
  by_contra hlt
  have hcard_le : S.card ≤ 2 := by omega
  have hcases : S.card = 0 ∨ S.card = 1 ∨ S.card = 2 := by omega
  rcases hcases with hzero | hone | htwo
  · have hSempty : S = ∅ := Finset.card_eq_zero.mp hzero
    obtain ⟨w, hw, _⟩ := hS (0 : Fin 5)
    simp [hSempty] at hw
  · obtain ⟨u, hSu⟩ := Finset.card_eq_one.mp hone
    rw [hSu] at hS
    obtain ⟨w, hw, huw⟩ := hS u
    simp only [Finset.mem_singleton] at hw
    subst w
    exact (cycleGraph 5).loopless u huw
  · obtain ⟨u, v, _, hSuv⟩ := Finset.card_eq_two.mp htwo
    rw [hSuv] at hS
    exact cycleGraph_five_pair_not_total u v hS

lemma cycleGraph_five_minimalTDS_card_three
    (S : Finset (Fin 5))
    (hS : IsMinimalTotalDominatingSet (cycleGraph 5) S) :
    S.card = 3 := by
  have hge := cycleGraph_five_totalDominatingSet_card_ge_three S hS.1
  have hle : S.card ≤ 5 := by
    simpa using S.card_le_univ
  by_contra hne
  have hge4 : 4 ≤ S.card := by omega
  have hcases : S.card = 4 ∨ S.card = 5 := by omega
  rcases hcases with hfour | hfive
  · have hcompl_card : Sᶜ.card = 1 := by
      simp [Finset.card_compl, hfour]
    obtain ⟨m, hm⟩ := Finset.card_eq_one.mp hcompl_card
    have hSeq : S = ({m} : Finset (Fin 5))ᶜ := by
      have h := congrArg (fun T : Finset (Fin 5) => Tᶜ) hm
      simpa using h
    have hstrict : c5ConsecutiveTriple m ⊂ S := by
      rw [hSeq]
      exact c5ConsecutiveTriple_ssubset_compl_singleton m
    exact (hS.2 _ hstrict) (c5ConsecutiveTriple_isTotalDominatingSet m)
  · have hSeq : S = Finset.univ :=
      Finset.eq_univ_of_card S (by simpa using hfive)
    have hstrict : c5ConsecutiveTriple (4 : Fin 5) ⊂ S := by
      rw [hSeq]
      decide
    exact (hS.2 _ hstrict)
      (c5ConsecutiveTriple_isTotalDominatingSet (4 : Fin 5))
end WOWII314.FormalCandidates
