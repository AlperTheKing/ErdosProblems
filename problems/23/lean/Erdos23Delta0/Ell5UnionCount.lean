import Mathlib

/-!
# Small union counting for the ell=5 geodesic-union lemma

The graph-theoretic part of T6 is: two distinct length-4 paths with the same
endpoints cannot differ in exactly one edge each.  This file isolates the pure
finite-set arithmetic reduction used by that argument.
-/

namespace Erdos23Delta0
namespace Ell5UnionCount

open Finset

variable {β : Type*} [DecidableEq β]

/-- If two distinct 4-element sets have union of size at most 5, then their
intersection has size exactly 3. -/
theorem inter_card_eq_three_of_four_four_union_le_five {A B : Finset β}
    (hA : A.card = 4) (hB : B.card = 4) (hne : A ≠ B) (hU : (A ∪ B).card ≤ 5) :
    (A ∩ B).card = 3 := by
  have hsum := Finset.card_union_add_card_inter A B
  have hIle : (A ∩ B).card ≤ 4 := by
    calc (A ∩ B).card ≤ A.card := Finset.card_le_card Finset.inter_subset_left
      _ = 4 := hA
  have hIlt : (A ∩ B).card < 4 := by
    by_contra hnot
    have hI4 : (A ∩ B).card = 4 := by omega
    have hIA : A ∩ B = A := by
      exact Finset.eq_of_subset_of_card_le Finset.inter_subset_left (by omega)
    have hIB : A ∩ B = B := by
      exact Finset.eq_of_subset_of_card_le Finset.inter_subset_right (by omega)
    exact hne (hIA.symm.trans hIB)
  have hIge : 3 ≤ (A ∩ B).card := by
    omega
  omega

/-- Contrapositive-friendly form: if two 4-element sets are distinct and their
intersection does not have size 3, then their union has size at least 6. -/
theorem union_card_ge_six_of_inter_ne_three {A B : Finset β}
    (hA : A.card = 4) (hB : B.card = 4) (hne : A ≠ B)
    (hI : (A ∩ B).card ≠ 3) :
    6 ≤ (A ∪ B).card := by
  by_contra hnot
  have hU : (A ∪ B).card ≤ 5 := by omega
  exact hI (inter_card_eq_three_of_four_four_union_le_five hA hB hne hU)

/-- If a 4-element set meets another set in exactly three elements, then
its complement relative to the other set is a singleton. -/
theorem sdiff_card_one_of_four_inter_three {A B : Finset β}
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

/-- If two finite sets differ from their intersection by one singleton each,
then an even total predicate count on the two sets descends to an even predicate
count on the two singleton differences. -/
theorem even_singletons_of_even_sum {A B : Finset β} {eP eQ : β} (f : β → Nat)
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

#print axioms inter_card_eq_three_of_four_four_union_le_five
#print axioms union_card_ge_six_of_inter_ne_three
#print axioms sdiff_card_one_of_four_inter_three
#print axioms even_singletons_of_even_sum

end Ell5UnionCount
end Erdos23Delta0
