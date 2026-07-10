import Erdos23Delta0.Ell5.ConcreteCage.Enumeration

/-!
# Proper-shore splits for all-length-five concrete cages

For an ambient cage whose owned atoms all have length five, every vertex shore
is a strong pure atom split: an atom cannot be supported on both complementary
shores, while any straddling atom has zero normalized surplus.  Complementary
restrictions also retain each nonempty-support local bank term on at most one
side, giving the existing bank-superadditivity inequality.

These statements concern `ConcreteCage.Balance = Bank - Surplus`.  They do not
identify port-Hall deficiency, a banked-wall LP objective, or any other notion
of `MinNeg` with `ConcreteCage.Balance`; that semantic bridge remains separate.
-/

namespace Erdos23Delta0
namespace Ell5
namespace ConcreteCage

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} {c : Distances.Cut V}

/-- If every owned atom has length five, every vertex shore gives a strong pure
atom split.  Double ownership is excluded using nonempty full geodesic support;
the remaining atoms satisfy the zero-surplus branch. -/
theorem strongPureLensAtomSplit_of_all_ell5
    (C : AmbientCage G c) (U : Finset V)
    (hell5 : ∀ a ∈ C.atoms, Distances.ell G c a.u a.v = 5) :
    StrongPureLensAtomSplit C U := by
  classical
  refine
    { noDouble := ?_
      coverOrZero := ?_ }
  · intro a ha hboth
    have hdist : (Distances.blueGraph G c).dist a.u a.v = 4 :=
      (Ell5LensStatement.ell_eq_five_iff_dist_eq_four G c a.u a.v).mp
        (hell5 a ha)
    obtain ⟨e, he⟩ := atomEdgeSupport_nonempty_of_dist4 a hdist
    have heU := hboth.1 he
    have heCompl := hboth.2 he
    revert heU heCompl
    refine Sym2.inductionOn e ?_
    intro x y heU heCompl
    rw [Finset.mk_mem_sym2_iff] at heU heCompl
    exact (Finset.mem_sdiff.mp heCompl.1).2 heU.1
  · intro a ha
    exact Or.inr (Or.inr (atom_surplus_eq_zero_of_ell5 G c a (hell5 a ha)))

/-- A nonempty-support local bank term is retained by at most one of a shore
restriction and its ambient complement restriction. -/
theorem term_single_owner_of_restrict_compl
    (t : LocalBankTerm (V := V)) (C : AmbientCage G c) (U : Finset V) :
    ¬ (termInCage t (restrict C U) ∧ termInCage t (restrictCompl C U)) := by
  intro hboth
  obtain ⟨x, hx⟩ := t.support_nonempty
  have hxU : x ∈ U := hboth.1 hx
  have hxCompl : x ∈ C.verts \ U := hboth.2 hx
  exact (Finset.mem_sdiff.mp hxCompl).2 hxU

/-- Complementary restrictions spend no local bank term twice and every child
term is inherited from the parent, so their bank sum is at most the parent
bank. -/
theorem bank_add_le_restrict_compl
    (F : BankFrame (V := V)) (C : AmbientCage G c) (U : Finset V)
    (hU : U ⊆ C.verts) :
    Bank F (restrict C U) + Bank F (restrictCompl C U) ≤ Bank F C := by
  apply bank_add_le_of_disjoint_subcages F
  · intro t _ hterm x hx
    exact hU (hterm hx)
  · intro t _ hterm x hx
    exact (Finset.mem_sdiff.mp (hterm hx)).1
  · exact restrict_disjoint_restrictCompl C U

/-- Once both complementary restrictions are proper shores, all-length-five
purity supplies the compiled concrete pure-lens cage split. -/
theorem pureLensCageSplit_of_all_ell5_proper_shores
    (F : BankFrame (V := V)) (C : AmbientCage G c) (U : Finset V)
    (hell5 : ∀ a ∈ C.atoms, Distances.ell G c a.u a.v = 5)
    (hLeft : ProperRelative C (restrict C U))
    (hRight : ProperRelative C (restrictCompl C U)) :
    Ell5PureLensCageInterface.PureLensCageSplit
      (Bank F) AmbientCage.Surplus (Balance F) (ProperRelative C)
      C (restrict C U) (restrictCompl C U) :=
  concretePureLensCageSplit F C U hLeft hRight
    (strongPureLensAtomSplit_of_all_ell5 C U hell5)
    (restrict_disjoint_restrictCompl C U)

/-- An ambient cage owning only length-five atoms cannot have negative
`ConcreteCage.Balance`.  This does not apply to port-Hall `MinNeg` without an
additional semantic agreement theorem. -/
theorem not_balance_neg_of_all_ell5
    (F : BankFrame (V := V)) (C : AmbientCage G c)
    (hell5 : ∀ a ∈ C.atoms, Distances.ell G c a.u a.v = 5) :
    ¬ Balance F C < 0 :=
  not_lt_of_ge (balance_nonneg_of_atoms_ell5 F C hell5)

end ConcreteCage
end Ell5
end Erdos23Delta0
