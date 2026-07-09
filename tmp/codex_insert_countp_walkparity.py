from pathlib import Path
p = Path('problems/23/lean/Erdos23Delta0/WalkParity.lean')
s = p.read_text(encoding='utf-8')
needle = '''#print axioms even_countP_edges_iff_walk
#print axioms even_countP_edges_closed
#print axioms sym2_eq_of_even_two_nonloop
'''
insert = '''/-- For a nodup list, `countP` is the corresponding `0/1` sum over the
associated finset. -/
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

#print axioms even_countP_edges_iff_walk
#print axioms even_countP_edges_closed
#print axioms sym2_eq_of_even_two_nonloop
#print axioms List.countP_eq_sum_toFinset_of_nodup
'''
if needle not in s:
    raise SystemExit('needle not found')
p.write_text(s.replace(needle, insert), encoding='utf-8')
