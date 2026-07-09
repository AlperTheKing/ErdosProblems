from pathlib import Path
p = Path('problems/23/lean/Erdos23Delta0/WalkParity.lean')
s = p.read_text(encoding='utf-8')
needle = '''#print axioms even_countP_edges_iff_walk
#print axioms even_countP_edges_closed
'''
insert = '''/-- If two non-loop unordered edges are the only possible contributors to an
even incidence count at every vertex, then they are the same edge. This is the
local Sym2 form used after canceling paired edge occurrences in a closed walk. -/
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

#print axioms even_countP_edges_iff_walk
#print axioms even_countP_edges_closed
#print axioms sym2_eq_of_even_two_nonloop
'''
if needle not in s:
    raise SystemExit('needle not found')
p.write_text(s.replace(needle, insert), encoding='utf-8')
