from pathlib import Path
p = Path('problems/23/lean/Erdos23Delta0/Ell5UnionCount.lean')
s = p.read_text(encoding='utf-8')
needle = '''#print axioms inter_card_eq_three_of_four_four_union_le_five
#print axioms union_card_ge_six_of_inter_ne_three
#print axioms sdiff_card_one_of_four_inter_three
'''
insert = '''/-- If two finite sets differ from their intersection by one singleton each,
then an even total predicate count on the two sets descends to an even predicate
count on the two singleton differences. -/
theorem even_singletons_of_even_sum {A B : Finset β} {eP eQ : β} (f : β → Nat)
    (hAp : A \\ B = {eP}) (hBq : B \\ A = {eQ})
    (hEven : Even ((∑ e ∈ A, f e) + (∑ e ∈ B, f e))) :
    Even (f eP + f eQ) := by
  let C : Nat := ∑ e ∈ A ∩ B, f e
  have hAminus : A \\ (A ∩ B) = {eP} := by
    calc
      A \\ (A ∩ B) = A \\ B := by
        ext x
        by_cases hxA : x ∈ A <;> by_cases hxB : x ∈ B <;> simp [hxA, hxB]
      _ = {eP} := hAp
  have hBminus : B \\ (A ∩ B) = {eQ} := by
    calc
      B \\ (A ∩ B) = B \\ A := by
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
'''
if needle not in s:
    raise SystemExit('needle not found')
p.write_text(s.replace(needle, insert), encoding='utf-8')
