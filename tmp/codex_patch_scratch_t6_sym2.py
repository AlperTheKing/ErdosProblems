from pathlib import Path
p = Path('tmp/scratch_t6_full.lean')
s = p.read_text(encoding='utf-8')
old = '''  rcases Sym2.exists_rep eP with ⟨a,b,rfl⟩
  rcases Sym2.exists_rep eQ with ⟨c,d,rfl⟩
  have hab : a ≠ b := by
    intro hab
    subst hab
    have : Sym2.IsDiag s(b,b) := by simp [Sym2.isDiag_iff_proj_eq]
    exact (G.not_isDiag_of_mem_edgeSet (SimpleGraph.Walk.edges_subset_edgeSet p (by simpa [A] using hePmemA))) this
  have heq : s(a,b) = s(c,d) := sym2_eq_of_even_two_nonloop hab hpar
  subst heq
  exact hePnotB heQmemB
'''
new = '''  induction eP using Sym2.ind with
  | _ a b =>
    induction eQ using Sym2.ind with
    | _ c d =>
      have hab : a ≠ b := by
        intro hab
        subst hab
        have hePedge : s(b,b) ∈ p.edges := by simpa [A] using hePmemA
        have hnotdiag := G.not_isDiag_of_mem_edgeSet (SimpleGraph.Walk.edges_subset_edgeSet p hePedge)
        exact hnotdiag (by simp)
      have heq : s(a,b) = s(c,d) := sym2_eq_of_even_two_nonloop hab hpar
      rw [← heq] at heQmemB
      exact hePnotB heQmemB
'''
if old not in s:
    raise SystemExit('old block not found')
p.write_text(s.replace(old, new), encoding='utf-8')
