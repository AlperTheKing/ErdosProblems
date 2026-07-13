import Erdos23Delta0.Ell5.ConcreteCage.BankPrime

namespace Erdos23Delta0
namespace Ell5
namespace ConcreteCage

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} {c : Distances.Cut V}

/-- For an all-length-five ambient cage, the strong atom split is automatic
at every vertex restriction: the zero-surplus alternative covers straddlers,
and nonempty full support prevents double ownership. -/
theorem strongPureLensAtomSplit_of_all_ell5
    (C : AmbientCage G c) (U : Finset V)
    (hell5 : forall a, a ∈ C.atoms -> Distances.ell G c a.u a.v = 5) :
    StrongPureLensAtomSplit C U := by
  classical
  refine
    { noDouble := ?_
      coverOrZero := ?_ }
  · intro a ha hboth
    have hdist : (Distances.blueGraph G c).dist a.u a.v = 4 := by
      exact (Ell5LensStatement.Bridge.ell_eq_five_iff_dist_eq_four G c a.u a.v).mp
        (hell5 a ha)
    obtain ⟨e, he⟩ := atomEdgeSupport_nonempty_of_dist4 a hdist
    have heU := hboth.1 he
    have heC := hboth.2 he
    revert heU heC
    refine Sym2.inductionOn e ?_
    intro x y heU heC
    rw [Finset.mk_mem_sym2_iff] at heU heC
    exact (Finset.mem_sdiff.mp heC.1).2 heU.1
  · intro a ha
    exact Or.inr (Or.inr (atom_surplus_eq_zero_of_ell5 G c a (hell5 a ha)))

/-- Complementary concrete restrictions retain any local bank term on at most
one side. This is the termwise single-owner statement behind bank superadditivity. -/
theorem term_singleOwner_restrict_restrictCompl
    (F : BankFrame (V := V)) (C : AmbientCage G c) (U : Finset V) :
    forall t, t ∈ F.terms ->
      not (termInCage t (restrict C U) and termInCage t (restrictCompl C U)) := by
  intro t ht hboth
  obtain ⟨x, hx⟩ := t.support_nonempty
  have hxU : x ∈ U := hboth.1 hx
  have hxC : x ∈ C.verts \ U := hboth.2 hx
  exact (Finset.mem_sdiff.mp hxC).2 hxU

/-- The existing bank theorem then gives the exact parent/children inequality
for complementary restrictions. -/
theorem bank_restrict_add_le_parent
    (F : BankFrame (V := V)) (C : AmbientCage G c) (U : Finset V)
    (hU : U ⊆ C.verts) :
    Bank F (restrict C U) + Bank F (restrictCompl C U) ≤ Bank F C := by
  apply bank_add_le_of_disjoint_subcages F
  · intro t ht hterm x hx
    exact hU (hterm hx)
  · intro t ht hterm x hx
    exact (Finset.mem_sdiff.mp (hterm hx)).1
  · refine Finset.disjoint_left.mpr ?_
    intro x hxU hxC
    exact (Finset.mem_sdiff.mp hxC).2 hxU

/-- Consequently an all-length-five ambient cage cannot satisfy the negative
balance half of the current concrete MinNeg contract. -/
theorem not_balance_neg_of_all_ell5
    (F : BankFrame (V := V)) (C : AmbientCage G c)
    (hell5 : forall a, a ∈ C.atoms -> Distances.ell G c a.u a.v = 5) :
    not (Balance F C < 0) := by
  exact not_lt_of_ge (balance_nonneg_of_atoms_ell5 F C hell5)

end ConcreteCage
end Ell5
end Erdos23Delta0
