from pathlib import Path
p = Path('problems/23/lean/Erdos23Delta0/Ell5UnionCount.lean')
s = p.read_text(encoding='utf-8')
needle = '''#print axioms inter_card_eq_three_of_four_four_union_le_five
#print axioms union_card_ge_six_of_inter_ne_three
'''
insert = '''/-- If a 4-element set meets another set in exactly three elements, then
its complement relative to the other set is a singleton. -/
theorem sdiff_card_one_of_four_inter_three {A B : Finset β}
    (hA : A.card = 4) (hI : (A ∩ B).card = 3) :
    (A \\ B).card = 1 := by
  have hEq : A \\ B = A \\ (A ∩ B) := by
    ext x
    simp
  have hInter : (A ∩ B) ∩ A = A ∩ B := by
    ext x
    simp [and_comm]
  rw [hEq, Finset.card_sdiff, hInter]
  omega

#print axioms inter_card_eq_three_of_four_four_union_le_five
#print axioms union_card_ge_six_of_inter_ne_three
#print axioms sdiff_card_one_of_four_inter_three
'''
if needle not in s:
    raise SystemExit('needle not found')
p.write_text(s.replace(needle, insert), encoding='utf-8')
