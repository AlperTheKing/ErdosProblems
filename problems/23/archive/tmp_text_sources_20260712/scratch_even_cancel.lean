import Mathlib

namespace Erdos23Delta0
namespace ScratchEvenCancel

open Finset

variable {α : Type*} [DecidableEq α]

theorem even_singletons_of_even_sum {A B : Finset α} {eP eQ : α} (f : α → Nat)
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
    simp [C] at hsumA0
    exact hsumA0.symm
  have hsumB0 := Finset.sum_sdiff (f := f) (Finset.inter_subset_right : A ∩ B ⊆ B)
  have hsumB : (∑ e ∈ B, f e) = f eQ + C := by
    rw [hBminus] at hsumB0
    simp [C] at hsumB0
    exact hsumB0.symm
  rw [hsumA, hsumB] at hEven
  have hcalc : (f eP + C) + (f eQ + C) = (f eP + f eQ) + 2 * C := by omega
  rw [hcalc] at hEven
  rcases hEven with ⟨k, hk⟩
  use k - C
  omega

#print axioms even_singletons_of_even_sum

end ScratchEvenCancel
end Erdos23Delta0
