import Mathlib

/-!
# Signed ordered-pair residual identity

For a fixed choice of one five-vertex row per bad edge, let n v z be the
number of chosen rows containing the ordered pair (v,z). A zero multiplicity
is a positive free-pair source; every copy beyond the first is a collision
debit. Pointwise, the free indicator minus the collision count is one minus
the multiplicity.

This module records the exact finite sum identity. It deliberately does not
turn collision debits into positive bank capacity.
-/

namespace Erdos23Delta0
namespace CollisionResidualIdentity

open scoped BigOperators

variable {V : Type*} [Fintype V]

/-- Number of ordered pairs unused by the selected rows. -/
def freeMass (n : V → V → Nat) : ℤ :=
  ∑ v : V, ∑ z : V, if n v z = 0 then 1 else 0

/-- Total multiplicity beyond the first copy of each ordered pair. -/
def collisionMass (n : V → V → Nat) : ℤ :=
  ∑ v : V, ∑ z : V, ((n v z - 1 : Nat) : ℤ)

theorem pointwise_signed_identity (k : Nat) :
    (if k = 0 then (1 : ℤ) else 0) - ((k - 1 : Nat) : ℤ) =
      1 - (k : ℤ) := by
  by_cases hk : k = 0
  · simp [hk]
  · have hk1 : 1 ≤ k := Nat.one_le_iff_ne_zero.mpr hk
    omega

/-- Free-source mass minus collision debit is ambient ordered-pair count
minus total selected-row multiplicity. -/
theorem free_sub_collision_eq
    (n : V → V → Nat) :
    freeMass n - collisionMass n =
      (Fintype.card V : ℤ) ^ 2 -
        ∑ v : V, ∑ z : V, (n v z : ℤ) := by
  unfold freeMass collisionMass
  calc
    (∑ v : V, ∑ z : V, if n v z = 0 then (1 : ℤ) else 0) -
          ∑ v : V, ∑ z : V, ((n v z - 1 : Nat) : ℤ) =
        ∑ v : V,
          ((∑ z : V, if n v z = 0 then (1 : ℤ) else 0) -
            ∑ z : V, ((n v z - 1 : Nat) : ℤ)) := by
      rw [Finset.sum_sub_distrib]
    _ = ∑ v : V, ∑ z : V,
          ((if n v z = 0 then (1 : ℤ) else 0) -
            ((n v z - 1 : Nat) : ℤ)) := by
      apply Finset.sum_congr rfl
      intro v _
      rw [Finset.sum_sub_distrib]
    _ = ∑ v : V, ∑ z : V, (1 - (n v z : ℤ)) := by
      apply Finset.sum_congr rfl
      intro v _
      apply Finset.sum_congr rfl
      intro z _
      exact pointwise_signed_identity (n v z)
    _ = (Fintype.card V : ℤ) ^ 2 -
          ∑ v : V, ∑ z : V, (n v z : ℤ) := by
      simp only [Finset.sum_sub_distrib, Finset.sum_const,
        Finset.card_univ, nsmul_eq_mul]
      ring

/-- If every selected five-vertex row contributes its 25 ordered pairs, the
signed mass is exactly the quadratic residual. -/
theorem free_sub_collision_eq_residual
    (n : V → V → Nat) (m : Nat)
    (htotal :
      (∑ v : V, ∑ z : V, (n v z : ℤ)) = 25 * (m : ℤ)) :
    freeMass n - collisionMass n =
      (Fintype.card V : ℤ) ^ 2 - 25 * (m : ℤ) := by
  rw [free_sub_collision_eq, htotal]

#print axioms pointwise_signed_identity
#print axioms free_sub_collision_eq
#print axioms free_sub_collision_eq_residual

end CollisionResidualIdentity
end Erdos23Delta0
