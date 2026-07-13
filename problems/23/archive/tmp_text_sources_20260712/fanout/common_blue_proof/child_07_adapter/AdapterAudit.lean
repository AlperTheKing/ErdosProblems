import Mathlib

namespace Child07AdapterAudit

/-- A one-copy matching gives only the unscaled cardinal bound. -/
theorem card_le_of_embedding {A B : Type*} [Fintype A] [Fintype B]
    (f : A ↪ B) : Fintype.card A ≤ Fintype.card B :=
  Fintype.card_le_of_injective f f.injective

/-- What a supplied matching really constructs: two source microcopies for
both debit and slot.  This is exact for debits, but only 2/25 of a slot. -/
def liftMatchingTwoScale {Debit Slot Source : Type*}
    (f : (Debit ⊕ Slot) ↪ Source) :
    ((Debit × Fin 2) ⊕ (Slot × Fin 2)) ↪ (Source × Fin 2) where
  toFun
    | Sum.inl d => (f (Sum.inl d.1), d.2)
    | Sum.inr s => (f (Sum.inr s.1), s.2)
  inj' := by
    intro x y h
    rcases x with d | s <;> rcases y with d' | s'
    · simp only [Prod.mk.injEq] at h
      obtain ⟨h₁, h₂⟩ := h
      have := f.injective h₁
      simp only [Sum.inl.injEq] at this
      exact congrArg Sum.inl (Prod.ext this h₂)
    · simp only [Prod.mk.injEq] at h
      cases f.injective h.1
    · simp only [Prod.mk.injEq] at h
      cases f.injective h.1
    · simp only [Prod.mk.injEq] at h
      obtain ⟨h₁, h₂⟩ := h
      have := f.injective h₁
      simp only [Sum.inr.injEq] at this
      exact congrArg Sum.inr (Prod.ext this h₂)

/-- At tight one-copy scale, the production 25-copy budget holds exactly
when there are no slots. -/
theorem tight_budget_iff_no_slots (debit slot : Nat) :
    2 * debit + 25 * slot ≤ 2 * (debit + slot) ↔ slot = 0 := by
  omega

/-- Smallest cardinal countermodel: a perfect one-copy matching exists, but
one debit plus one slot cannot enter one source's two microcopies. -/
theorem tiny_matching_but_no_residual_embedding :
    Nonempty ((Fin 1 ⊕ Fin 1) ↪ Fin 2) ∧
      IsEmpty (((Fin 1 × Fin 2) ⊕ (Fin 1 × Fin 25)) ↪ (Fin 2 × Fin 2)) := by
  constructor
  · exact Function.Embedding.nonempty_of_card_le (by decide)
  · constructor
    intro f
    have h := Fintype.card_le_of_injective f f.injective
    norm_num at h

/-- Exact R29 repair arithmetic: 28 matched collision debits use the two
microcopies of 28 sources and leave no capacity for even one bank slot. -/
theorem r29_repair_keys_cannot_also_fund_one_slot :
    ¬ (2 * 28 + 25 * 1 ≤ 2 * 28) := by norm_num

/-- The purely cardinal part of the missing provider is sufficient for the
raw residual embedding.  Component preservation is a separate field of Data. -/
theorem raw_residual_embedding_of_budget
    {Debit Slot Source : Type*} [Fintype Debit] [Fintype Slot] [Fintype Source]
    (h : 2 * Fintype.card Debit + 25 * Fintype.card Slot ≤
      2 * Fintype.card Source) :
    Nonempty (((Debit × Fin 2) ⊕ (Slot × Fin 25)) ↪ (Source × Fin 2)) :=
  Function.Embedding.nonempty_of_card_le (by
    simpa [Nat.mul_comm, Nat.mul_left_comm, Nat.mul_assoc] using h)

#print axioms card_le_of_embedding
#print axioms liftMatchingTwoScale
#print axioms tight_budget_iff_no_slots
#print axioms tiny_matching_but_no_residual_embedding
#print axioms r29_repair_keys_cannot_also_fund_one_slot
#print axioms raw_residual_embedding_of_budget

end Child07AdapterAudit


