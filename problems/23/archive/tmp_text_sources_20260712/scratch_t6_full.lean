import Mathlib

namespace Erdos23Delta0
namespace ScratchT6Full

open SimpleGraph Finset

variable {V : Type*} [DecidableEq V] {G : SimpleGraph V} {u v : V}

-- copied helper: closed-walk incidence parity
theorem even_countP_edges_iff_walk {u v : V} {p : G.Walk u v} (x : V) :
    Even (p.edges.countP fun e => x ∈ e) ↔ u ≠ v → x ≠ u ∧ x ≠ v := by
  induction p with
  | nil => simp
  | cons huv p ih =>
    simp only [List.countP_cons, Ne, SimpleGraph.Walk.edges_cons, Sym2.mem_iff]
    split_ifs with h
    · rw [decide_eq_true_eq] at h
      obtain (rfl | rfl) := h
      · rw [Nat.even_add_one, ih]
        simp only [huv.ne, imp_false, Ne, not_false_iff, true_and, not_forall,
          Classical.not_not, exists_prop, not_true, false_and,
          and_iff_right_iff_imp]
        rintro rfl rfl
        exact G.loopless _ huv
      · have := huv.ne
        grind
    · grind

theorem even_countP_edges_closed {u : V} (p : G.Walk u u) (x : V) :
    Even (p.edges.countP fun e => x ∈ e) := by
  rw [even_countP_edges_iff_walk]
  intro h
  exact False.elim (h rfl)

theorem sym2_eq_of_even_two_nonloop {a b c d : V}
    (hab : a ≠ b)
    (hpar : ∀ x : V,
      Even ((if x ∈ s(a,b) then 1 else 0) + (if x ∈ s(c,d) then 1 else 0))) :
    s(a,b) = s(c,d) := by
  have ha : a ∈ s(c,d) := by
    by_contra ha
    have h := hpar a
    simp [Sym2.mem_iff, hab, ha] at h
  have hb : b ∈ s(c,d) := by
    by_contra hb
    have h := hpar b
    simp [Sym2.mem_iff, hab.symm, hb] at h
  rw [Sym2.eq_iff]
  rw [Sym2.mem_iff] at ha hb
  grind

theorem List.countP_eq_sum_toFinset_of_nodup {α : Type*} [DecidableEq α]
    (l : List α) (P : α → Prop) [DecidablePred P] (hn : l.Nodup) :
    l.countP P = ∑ x ∈ l.toFinset, if P x then 1 else 0 := by
  induction l with
  | nil => simp
  | cons a t ih =>
    rw [List.nodup_cons] at hn
    have ht := hn.2
    have hnot : a ∉ t.toFinset := by simpa using hn.1
    rw [List.countP_cons, List.toFinset_cons, Finset.sum_insert hnot, ih ht]
    by_cases hP : P a <;> simp [hP] <;> omega

-- copied finite-set helpers
theorem sdiff_card_one_of_four_inter_three {β : Type*} [DecidableEq β] {A B : Finset β}
    (hA : A.card = 4) (hI : (A ∩ B).card = 3) :
    (A \ B).card = 1 := by
  have hEq : A \ B = A \ (A ∩ B) := by
    ext x
    simp
  have hInter : (A ∩ B) ∩ A = A ∩ B := by
    ext x
    simp [and_comm]
  rw [hEq, Finset.card_sdiff, hInter]
  omega

theorem even_singletons_of_even_sum {β : Type*} [DecidableEq β]
    {A B : Finset β} {eP eQ : β} (f : β → Nat)
    (hAp : A \ B = {eP}) (hBq : B \ A = {eQ})
    (hEven : Even ((∑ e ∈ A, f e) + (∑ e ∈ B, f e))) :
    Even (f eP + f eQ) := by
  let C : Nat := ∑ e ∈ A ∩ B, f e
  have hAminus : A \ (A ∩ B) = {eP} := by
    calc
      A \ (A ∩ B) = A \ B := by
        ext x
        by_cases hxA : x ∈ A <;> by_cases hxB : x ∈ B <;> simp [hxA, hxB]
      _ = {eP} := hAp
  have hBminus : B \ (A ∩ B) = {eQ} := by
    calc
      B \ (A ∩ B) = B \ A := by
        ext x
        by_cases hxA : x ∈ A <;> by_cases hxB : x ∈ B <;> simp [hxA, hxB]
      _ = {eQ} := hBq
  have hsumA0 := Finset.sum_sdiff (f := f) (Finset.inter_subset_left : A ∩ B ⊆ A)
  have hsumA : (∑ e ∈ A, f e) = f eP + C := by
    rw [hAminus] at hsumA0
    simp at hsumA0
    exact hsumA0.symm
  have hsumB0 := Finset.sum_sdiff (f := f) (Finset.inter_subset_right : A ∩ B ⊆ B)
  have hsumB : (∑ e ∈ B, f e) = f eQ + C := by
    rw [hBminus] at hsumB0
    simp at hsumB0
    exact hsumB0.symm
  rw [hsumA, hsumB] at hEven
  have hcalc : (f eP + C) + (f eQ + C) = (f eP + f eQ) + 2 * C := by omega
  rw [hcalc] at hEven
  rcases hEven with ⟨k, hk⟩
  use k - C
  omega

theorem geodesic_len4_card_edges {u v : V}
    (p : G.Walk u v) (hp : p.IsPath) (hlen : p.length = 4) :
    p.edges.toFinset.card = 4 := by
  rw [List.toFinset_card_of_nodup hp.edges_nodup, SimpleGraph.Walk.length_edges, hlen]

theorem no_three_common_edges_len4_same_endpoints
    (p q : G.Walk u v) (hp : p.IsPath) (hq : q.IsPath)
    (hlp : p.length = 4) (hlq : q.length = 4)
    (hne : p.edges.toFinset ≠ q.edges.toFinset) :
    (p.edges.toFinset ∩ q.edges.toFinset).card ≠ 3 := by
  intro h3
  let A : Finset (Sym2 V) := p.edges.toFinset
  let B : Finset (Sym2 V) := q.edges.toFinset
  have hA : A.card = 4 := geodesic_len4_card_edges p hp hlp
  have hB : B.card = 4 := geodesic_len4_card_edges q hq hlq
  have hApCard : (A \ B).card = 1 := sdiff_card_one_of_four_inter_three hA h3
  have hBqCard : (B \ A).card = 1 := by
    have h3' : (B ∩ A).card = 3 := by simpa [Finset.inter_comm] using h3
    exact sdiff_card_one_of_four_inter_three hB h3'
  obtain ⟨eP, hePsingle⟩ := Finset.card_eq_one.mp hApCard
  obtain ⟨eQ, heQsingle⟩ := Finset.card_eq_one.mp hBqCard
  have hePmemA : eP ∈ A := by
    have ht : eP ∈ A \ B := by rw [hePsingle]; simp
    rw [Finset.mem_sdiff] at ht
    exact ht.1
  have hePnotB : eP ∉ B := by
    have ht : eP ∈ A \ B := by rw [hePsingle]; simp
    rw [Finset.mem_sdiff] at ht
    exact ht.2
  have heQmemB : eQ ∈ B := by
    have ht : eQ ∈ B \ A := by rw [heQsingle]; simp
    rw [Finset.mem_sdiff] at ht
    exact ht.1
  have heQnotA : eQ ∉ A := by
    have ht : eQ ∈ B \ A := by rw [heQsingle]; simp
    rw [Finset.mem_sdiff] at ht
    exact ht.2
  have hEvenSums : ∀ x : V,
      Even ((∑ e ∈ A, if x ∈ e then 1 else 0) +
        (∑ e ∈ B, if x ∈ e then 1 else 0)) := by
    intro x
    have hclosed := even_countP_edges_closed (p.append q.reverse) x
    simp [SimpleGraph.Walk.edges_append, SimpleGraph.Walk.edges_reverse, List.countP_append] at hclosed
    rw [List.countP_eq_sum_toFinset_of_nodup p.edges (fun e => x ∈ e) hp.edges_nodup,
        List.countP_eq_sum_toFinset_of_nodup q.edges (fun e => x ∈ e) hq.edges_nodup] at hclosed
    simpa [A, B] using hclosed
  have hpar : ∀ x : V, Even ((if x ∈ eP then 1 else 0) + (if x ∈ eQ then 1 else 0)) := by
    intro x
    exact even_singletons_of_even_sum (fun e : Sym2 V => if x ∈ e then 1 else 0)
      hePsingle heQsingle (hEvenSums x)
  induction eP using Sym2.ind with
  | _ a b =>
    induction eQ using Sym2.ind with
    | _ c d =>
      have hab : a ≠ b := by
        intro hab
        subst hab
        have hePedge : s(a,a) ∈ p.edges := by simpa [A] using hePmemA
        have hnotdiag := G.not_isDiag_of_mem_edgeSet (SimpleGraph.Walk.edges_subset_edgeSet p hePedge)
        exact hnotdiag (by simp)
      have heq : s(a,b) = s(c,d) := sym2_eq_of_even_two_nonloop hab hpar
      rw [← heq] at heQmemB
      exact hePnotB heQmemB

#print axioms no_three_common_edges_len4_same_endpoints

end ScratchT6Full
end Erdos23Delta0
