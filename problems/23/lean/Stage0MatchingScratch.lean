import Mathlib

/-!
Scratch formalization for the stage-0 matching-dual cost atom.

This file is not the final Formal Conjectures target.  It isolates the
finite arithmetic behind the exchange statement used in the row single-miss
proof: if a minimum-cost used exit set cannot be improved by replacing `q`
with an unused exit `p`, then the used exit `q` has cost at most `p`.
-/

namespace Erdos23
namespace Stage0

theorem cost_le_of_no_improving_exchange {E : Type*} [DecidableEq E]
    (c : E → Nat) (used : Finset E) {p q : E}
    (hp : p ∉ used) (hq : q ∈ used)
    (hmin : used.sum c ≤ (insert p (used.erase q)).sum c) :
    c q ≤ c p := by
  have hp_erase : p ∉ used.erase q := by
    intro hp'
    exact hp (Finset.mem_of_mem_erase hp')
  rw [Finset.sum_insert hp_erase] at hmin
  rw [← Finset.sum_erase_add _ _ hq] at hmin
  omega

theorem card_add_one_le_of_subset_erase {α : Type*} [DecidableEq α]
    {A B : Finset α} {f : α}
    (hsub : A ⊆ B.erase f)
    (hfB : f ∈ B) :
    A.card + 1 ≤ B.card := by
  have hfA : f ∉ A := by
    intro hfA'
    have hfErase : f ∈ B.erase f := hsub hfA'
    simp at hfErase
  have hinsert : insert f A ⊆ B := by
    intro x hx
    rw [Finset.mem_insert] at hx
    rcases hx with rfl | hxA
    · exact hfB
    · exact Finset.mem_of_mem_erase (hsub hxA)
  have hcard : (insert f A).card = A.card + 1 := by
    simp [hfA]
  rw [← hcard]
  exact Finset.card_le_card hinsert

theorem rare_cost_strict_of_subset_erase {F : Type*} [DecidableEq F]
    {near far : Finset F} {f : F}
    (hsub : near ⊆ far.erase f)
    (hfFar : f ∈ far) :
    near.card + 1 ≤ far.card :=
  card_add_one_le_of_subset_erase hsub hfFar

theorem strict_cost_contradicts_no_improving_exchange {E : Type*} [DecidableEq E]
    (c : E → Nat) (used : Finset E) {p q : E}
    (hp : p ∉ used) (hq : q ∈ used)
    (hmin : used.sum c ≤ (insert p (used.erase q)).sum c)
    (hstrict : c p + 1 ≤ c q) :
    False := by
  have hle : c q ≤ c p := cost_le_of_no_improving_exchange c used hp hq hmin
  omega

theorem witness_inclusion_contradicts_no_improving_exchange
    {E F : Type*} [DecidableEq E] [DecidableEq F]
    (Wit : E → Finset F) (used : Finset E) {p q : E} {f : F}
    (hp : p ∉ used) (hq : q ∈ used)
    (hmin :
      used.sum (fun e => (Wit e).card) ≤
        (insert p (used.erase q)).sum (fun e => (Wit e).card))
    (hsub : Wit p ⊆ (Wit q).erase f)
    (hfFar : f ∈ Wit q) :
    False := by
  have hstrict : (Wit p).card + 1 ≤ (Wit q).card :=
    rare_cost_strict_of_subset_erase hsub hfFar
  exact strict_cost_contradicts_no_improving_exchange
    (fun e => (Wit e).card) used hp hq hmin hstrict

end Stage0
end Erdos23
