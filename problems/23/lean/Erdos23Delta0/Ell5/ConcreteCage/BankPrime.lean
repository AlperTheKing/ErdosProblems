import Erdos23Delta0.BankPrimeSplitOrRoot
import Erdos23Delta0.Ell5.ConcreteCage.PureLensSplit

/-!
# Bank-prime induction for concrete ell=5 cages

This module grounds the abstract bank-prime split-or-root induction in the
existing concrete cage ledger.  The violation defect is `Surplus - Bank`, the
negative of `Balance`.  A pure-lens cage split is a proper bank-conserving
split because surplus is additive while the two child banks spend at most the
parent bank.

This is the concrete **cage-ledger** defect.  No theorem in this module
identifies it with `PortHall.deficiencyQ`, whose left side depends on a
restricted-dual port load; that semantic bridge is a separate obligation.

The remaining graph-side obligation for this cage-ledger interface is the classifier
`PureSplitOrRoot`: every positive-defect concrete cage either admits such a
pure split or has a rooted witness killed by the rooted theorem.
-/

namespace Erdos23Delta0
namespace Ell5
namespace ConcreteCage

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} {c : Distances.Cut V}

/-- Cage-ledger defect carried by a concrete cage.  Calling this a Hall defect
requires an additional semantic agreement theorem with the routed-port model. -/
noncomputable def Defect (F : BankFrame (V := V))
    (C : AmbientCage G c) : ℚ :=
  C.Surplus - Bank F C

omit [DecidableEq V] in
theorem defect_eq_neg_balance (F : BankFrame (V := V))
    (C : AmbientCage G c) :
    Defect F C = -Balance F C := by
  simp [Defect, Balance]

theorem defect_le_surplus (F : BankFrame (V := V))
    (C : AmbientCage G c) :
    Defect F C ≤ C.Surplus := by
  unfold Defect
  linarith [bank_nonneg F C]

theorem surplus_pos_of_defect_pos (F : BankFrame (V := V))
    (C : AmbientCage G c) (hpos : 0 < Defect F C) :
    0 < C.Surplus :=
  lt_of_lt_of_le hpos (defect_le_surplus F C)

/-- A cage whose owned atoms all have length five is outside the positive-defect
domain of every split-or-root classifier.  This is independent of the legal
port incidence of the nonnegative bank terms. -/
theorem defect_nonpos_of_atoms_ell5 (F : BankFrame (V := V))
    (C : AmbientCage G c)
    (hell5 : ∀ a ∈ C.atoms, Distances.ell G c a.u a.v = 5) :
    Defect F C ≤ 0 := by
  rw [defect_eq_neg_balance]
  have hbal := balance_nonneg_of_atoms_ell5 F C hell5
  linarith

theorem exists_atom_not_ell5_of_defect_pos (F : BankFrame (V := V))
    (C : AmbientCage G c) (hpos : 0 < Defect F C) :
    ∃ a ∈ C.atoms, Distances.ell G c a.u a.v ≠ 5 := by
  by_contra h
  push_neg at h
  exact (not_lt_of_ge (defect_nonpos_of_atoms_ell5 F C h)) hpos

/-- Under the usual odd-cycle lower bound, every positive concrete defect
contains a genuinely long atom. -/
theorem exists_long_atom_of_defect_pos (F : BankFrame (V := V))
    (C : AmbientCage G c) (hpos : 0 < Defect F C)
    (hmin : ∀ a ∈ C.atoms, 5 ≤ Distances.ell G c a.u a.v) :
    ∃ a ∈ C.atoms, 5 < Distances.ell G c a.u a.v := by
  obtain ⟨a, ha, hne⟩ := exists_atom_not_ell5_of_defect_pos F C hpos
  exact ⟨a, ha, lt_of_le_of_ne (hmin a ha) (Ne.symm hne)⟩

private theorem verts_card_lt_of_proper {C D : AmbientCage G c}
    (h : ProperRelative C D) :
    D.verts.card < C.verts.card := by
  apply Finset.card_lt_card
  exact Finset.ssubset_iff_subset_ne.mpr ⟨h.verts_subset, h.verts_ne⟩

/-- A concrete pure-lens ledger split supplies exactly the proper split needed
by the abstract bank-prime induction. -/
noncomputable def properSplitOfPureLens (F : BankFrame (V := V))
    (C W C' : AmbientCage G c)
    (h : Ell5PureLensCageInterface.PureLensCageSplit
      (Bank F) AmbientCage.Surplus (Balance F) (ProperRelative C) C W C') :
    Wall.BankPrime.ProperSplit
      (AmbientCage G c) (fun D => D.verts.card) (Defect F) C where
  left := W
  right := C'
  left_rank := verts_card_lt_of_proper h.wProper
  right_rank := verts_card_lt_of_proper h.cProper
  defect_le := by
    unfold Defect
    linarith [h.surplusSplit, h.bankSuper]

/-- Concrete construction form using the already compiled T8 cage facts. -/
noncomputable def properSplitOfConcretePureLens (F : BankFrame (V := V))
    (C : AmbientCage G c) (U : Finset V)
    (hWProper : ProperRelative C (restrict C U))
    (hCProper : ProperRelative C (restrictCompl C U))
    (hStrong : StrongPureLensAtomSplit C U)
    (hDisj : Disjoint (restrict C U).verts (restrictCompl C U).verts) :
    Wall.BankPrime.ProperSplit
      (AmbientCage G c) (fun D => D.verts.card) (Defect F) C :=
  properSplitOfPureLens F C (restrict C U) (restrictCompl C U)
    (concretePureLensCageSplit F C U hWProper hCProper hStrong hDisj)

/-- Exact concrete provider target for the bank-prime route.  A positive
full-bank defect is either split by the existing pure-lens cage interface or
is already rooted. -/
def PureSplitOrRoot (F : BankFrame (V := V)) (RootWitness : Type*)
    (rootAt : AmbientCage G c → RootWitness → Prop) : Prop :=
  ∀ C, 0 < Defect F C →
    (∃ W C', Ell5PureLensCageInterface.PureLensCageSplit
      (Bank F) AmbientCage.Surplus (Balance F) (ProperRelative C) C W C') ∨
      ∃ r, rootAt C r

/-- The concrete classifier induces the abstract split-or-root classifier. -/
theorem splitOrRoot_of_pureSplitOrRoot
    (F : BankFrame (V := V)) (RootWitness : Type*)
    (rootAt : AmbientCage G c → RootWitness → Prop)
    (hclass : PureSplitOrRoot F RootWitness rootAt) :
    Wall.BankPrime.SplitOrRoot
      (AmbientCage G c) RootWitness (fun D => D.verts.card) (Defect F) rootAt := by
  intro C hpos
  rcases hclass C hpos with hsplit | hroot
  · rcases hsplit with ⟨W, C', h⟩
    exact Or.inl ⟨properSplitOfPureLens F C W C' h⟩
  · exact Or.inr hroot

/-- If every rooted witness is excluded, a concrete split-or-root classifier
proves nonnegative balance for every cage. -/
theorem balance_nonneg_of_pureSplitOrRoot
    (F : BankFrame (V := V)) (RootWitness : Type*)
    (rootAt : AmbientCage G c → RootWitness → Prop)
    (hclass : PureSplitOrRoot F RootWitness rootAt)
    (hroot : ∀ C r, rootAt C r → False) :
    ∀ C : AmbientCage G c, 0 ≤ Balance F C := by
  intro C
  have hdef : Defect F C ≤ 0 :=
    Wall.BankPrime.defect_nonpos_of_split_or_root
      (fun D : AmbientCage G c => D.verts.card) (Defect F) rootAt
      (splitOrRoot_of_pureSplitOrRoot F RootWitness rootAt hclass) hroot C
  rw [defect_eq_neg_balance] at hdef
  linarith

end ConcreteCage
end Ell5
end Erdos23Delta0
