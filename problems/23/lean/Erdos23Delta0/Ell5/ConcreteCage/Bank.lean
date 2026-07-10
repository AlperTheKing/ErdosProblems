import Erdos23Delta0.Ell5.ConcreteCage.Basic

/-!
# Concrete ell=5 cage bookkeeping: local bank terms

The bank is a finite list of nonnegative local caps, each carried by a
nonempty vertex support.  A term belongs to a cage exactly when its support is
contained in the cage vertex set.
-/

namespace Erdos23Delta0
namespace Ell5
namespace ConcreteCage

open Finset

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} {c : Distances.Cut V}

/-- The local bank sources used by the cage ledger. -/
inductive LocalBankKind where
  | door
  | vertexSlack
  | baseLeaf
  | prune
  deriving Repr

/-- A local nonnegative bank term with nonempty vertex support. -/
structure LocalBankTerm where
  kind : LocalBankKind
  support : Finset V
  support_nonempty : support.Nonempty
  cap : ℚ
  cap_nonneg : 0 ≤ cap

/-- A finite bank frame.  We use a list because terms contain proof fields, so a
`Finset LocalBankTerm` would add irrelevant equality obligations. -/
structure BankFrame where
  terms : List (LocalBankTerm (V := V))

/-- A bank term is available in a cage when its full local support is inside the
cage vertex set. -/
def termInCage (t : LocalBankTerm (V := V)) (C : AmbientCage G c) : Prop :=
  t.support ⊆ C.verts

/-- The contribution of a term to a cage bank. -/
noncomputable def termCapIn (t : LocalBankTerm (V := V)) (C : AmbientCage G c) : ℚ :=
  by
    classical
    exact if termInCage t C then t.cap else 0

/-- Bank value over a list of terms. -/
noncomputable def bankOn (ts : List (LocalBankTerm (V := V))) (C : AmbientCage G c) : ℚ :=
  ts.foldr (fun t acc => termCapIn t C + acc) 0

/-- Bank value of a frame in a cage. -/
noncomputable def Bank (F : BankFrame (V := V)) (C : AmbientCage G c) : ℚ :=
  bankOn F.terms C

/-- Concrete balance used by the pure-lens cage interface. -/
noncomputable def Balance (F : BankFrame (V := V)) (C : AmbientCage G c) : ℚ :=
  Bank F C - C.Surplus

theorem balance_eq_bank_sub_surplus (F : BankFrame (V := V)) (C : AmbientCage G c) :
    Balance F C = Bank F C - C.Surplus := rfl

theorem termCapIn_nonneg (t : LocalBankTerm (V := V)) (C : AmbientCage G c) :
    0 ≤ termCapIn t C := by
  classical
  unfold termCapIn
  by_cases h : termInCage t C
  · simpa [h] using t.cap_nonneg
  · simp [h]

theorem bankOn_nonneg (ts : List (LocalBankTerm (V := V))) (C : AmbientCage G c) :
    0 ≤ bankOn ts C := by
  induction ts with
  | nil => simp [bankOn]
  | cons t ts ih =>
      simpa [bankOn] using add_nonneg (termCapIn_nonneg t C) ih

theorem bank_nonneg (F : BankFrame (V := V)) (C : AmbientCage G c) :
    0 ≤ Bank F C :=
  bankOn_nonneg F.terms C

/-- A cage owning only length-five atoms has zero normalized surplus. -/
theorem surplus_eq_zero_of_atoms_ell5 (C : AmbientCage G c)
    (hell5 : ∀ a ∈ C.atoms, Distances.ell G c a.u a.v = 5) :
    C.Surplus = 0 := by
  classical
  unfold AmbientCage.Surplus
  exact Finset.sum_eq_zero fun a ha => atom_surplus_eq_zero_of_ell5 G c a (hell5 a ha)

/-- Pure length-five cages cannot be reduced minimal negative-balance cages,
regardless of how the nonnegative bank terms are incident to ports. -/
theorem balance_nonneg_of_atoms_ell5 (F : BankFrame (V := V)) (C : AmbientCage G c)
    (hell5 : ∀ a ∈ C.atoms, Distances.ell G c a.u a.v = 5) :
    0 ≤ Balance F C := by
  rw [balance_eq_bank_sub_surplus, surplus_eq_zero_of_atoms_ell5 C hell5, sub_zero]
  exact bank_nonneg F C

private theorem not_termIn_both_of_disjoint (t : LocalBankTerm (V := V))
    {W C' : AmbientCage G c} (hdisj : Disjoint W.verts C'.verts) :
    ¬ (termInCage t W ∧ termInCage t C') := by
  intro h
  obtain ⟨v, hv⟩ := t.support_nonempty
  have hvW : v ∈ W.verts := h.1 hv
  have hvC : v ∈ C'.verts := h.2 hv
  exact (Finset.disjoint_left.mp hdisj) hvW hvC

private theorem term_contrib_le (t : LocalBankTerm (V := V))
    {C W C' : AmbientCage G c}
    (hWsub : termInCage t W → termInCage t C)
    (hCsub : termInCage t C' → termInCage t C)
    (hno : ¬ (termInCage t W ∧ termInCage t C')) :
    termCapIn t W + termCapIn t C' ≤ termCapIn t C := by
  classical
  unfold termCapIn
  by_cases hW : termInCage t W
  · by_cases hC' : termInCage t C'
    · exact (hno ⟨hW, hC'⟩).elim
    · have hC : termInCage t C := hWsub hW
      simp [hW, hC', hC]
  · by_cases hC' : termInCage t C'
    · have hC : termInCage t C := hCsub hC'
      simp [hW, hC', hC]
    · by_cases hC : termInCage t C
      · simpa [hW, hC', hC] using t.cap_nonneg
      · simp [hW, hC', hC]

private theorem bankOn_add_le (ts : List (LocalBankTerm (V := V)))
    {C W C' : AmbientCage G c}
    (hWsub : ∀ t ∈ ts, termInCage t W → termInCage t C)
    (hCsub : ∀ t ∈ ts, termInCage t C' → termInCage t C)
    (hno : ∀ t ∈ ts, ¬ (termInCage t W ∧ termInCage t C')) :
    bankOn ts W + bankOn ts C' ≤ bankOn ts C := by
  classical
  induction ts with
  | nil =>
      simp [bankOn]
  | cons t ts ih =>
      have hterm : (if termInCage t W then t.cap else 0) +
            (if termInCage t C' then t.cap else 0) ≤
          (if termInCage t C then t.cap else 0) :=
        term_contrib_le t
          (fun h => hWsub t (by simp) h)
          (fun h => hCsub t (by simp) h)
          (hno t (by simp))
      have htail : bankOn ts W + bankOn ts C' ≤ bankOn ts C := by
        apply ih
        · intro u hu hU
          exact hWsub u (by simp [hu]) hU
        · intro u hu hU
          exact hCsub u (by simp [hu]) hU
        · intro u hu
          exact hno u (by simp [hu])
      calc
        bankOn (t :: ts) W + bankOn (t :: ts) C'
            = (((if termInCage t W then t.cap else 0) +
                  (if termInCage t C' then t.cap else 0)) +
                (bankOn ts W + bankOn ts C')) := by
                simp [bankOn, termCapIn]
                ring
        _ ≤ (if termInCage t C then t.cap else 0) + bankOn ts C := by
                linarith
        _ = bankOn (t :: ts) C := by
                simp [bankOn, termCapIn]

/-- If two subcages are vertex-disjoint and every term they contain is also a
term of the ambient cage, then their bank values do not exceed the ambient
bank. -/
theorem bank_add_le_of_disjoint_subcages (F : BankFrame (V := V))
    {C W C' : AmbientCage G c}
    (hWsub : ∀ t ∈ F.terms, termInCage t W → termInCage t C)
    (hCsub : ∀ t ∈ F.terms, termInCage t C' → termInCage t C)
    (hdisj : Disjoint W.verts C'.verts) :
    Bank F W + Bank F C' ≤ Bank F C := by
  exact bankOn_add_le F.terms hWsub hCsub
    (fun t _ => not_termIn_both_of_disjoint t hdisj)

end ConcreteCage
end Ell5
end Erdos23Delta0
