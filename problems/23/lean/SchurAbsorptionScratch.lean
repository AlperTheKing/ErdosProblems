import Mathlib

/-!
Scratch algebra for the Schur absorption-Hall route.

The coefficient-free live frontier is the pointwise minority-shunt lemma:

  if `a o <= A - a o`, then `rho o >= 0`.

This implies the bare subset Absorption-Hall inequality.  The formerly tested
quantitative strengthening

  if `a o <= A - a o`, then `25 * rho o >= A - 2 * a o`.

is retained below only as an algebra lemma; its graph-theoretic hypothesis is
false on larger C5 blowups.  Here `a o` is the overload of one Schur terminal,
`A` is total overload on `O`, and `rho o` is the Schur row-shunt.
-/

namespace Erdos23
namespace SchurAbsorption

open Finset

/--
Pointwise coefficient-free minority shunt implies subset bare
absorption-Hall.

If a nonempty subset `X` has total overload at most half of `A`, and all
members of `X` have nonnegative overload, then every member is individually a
minority vertex.  Summing the pointwise nonnegative row-shunt bound gives
`rho(X) >= 0`.
-/
theorem pointwise_bare_minority_implies_subset
    {ι : Type*} [DecidableEq ι]
    (X : Finset ι) (a rho : ι → ℚ) (A : ℚ)
    (ha_nonneg : ∀ i, i ∈ X → 0 ≤ a i)
    (hminorX : X.sum a ≤ A - X.sum a)
    (hpoint :
      ∀ i, i ∈ X → a i ≤ A - a i → 0 ≤ rho i) :
    0 ≤ X.sum rho := by
  classical
  let s : ℚ := X.sum a
  have htwo_s : 2 * s ≤ A := by
    dsimp [s]
    linarith
  have hminor_each : ∀ i, i ∈ X → a i ≤ A - a i := by
    intro i hi
    have htail_nonneg : 0 ≤ (X.erase i).sum a := by
      exact Finset.sum_nonneg (fun j hj => ha_nonneg j (Finset.mem_of_mem_erase hj))
    have hs_decomp : s = (X.erase i).sum a + a i := by
      dsimp [s]
      rw [← Finset.sum_erase_add _ _ hi]
    have hai_le_s : a i ≤ s := by
      linarith
    have htwo_ai : 2 * a i ≤ A := by
      linarith
    linarith
  exact Finset.sum_nonneg (fun i hi => hpoint i hi (hminor_each i hi))

/--
Pointwise minority-current implies subset quantitative absorption-Hall.

If a nonempty subset `X` has total overload at most half of `A`, and all
members of `X` have nonnegative overload, then every member is individually a
minority vertex.  Summing the pointwise current bound gives the subset bound.
-/
theorem pointwise_minority_implies_subset
    {ι : Type*} [DecidableEq ι]
    (X : Finset ι) (a rho : ι → ℚ) (A : ℚ)
    (hX : X.Nonempty)
    (ha_nonneg : ∀ i, i ∈ X → 0 ≤ a i)
    (hA_nonneg : 0 ≤ A)
    (hminorX : X.sum a ≤ A - X.sum a)
    (hpoint :
      ∀ i, i ∈ X → a i ≤ A - a i →
        25 * rho i ≥ A - 2 * a i) :
    25 * X.sum rho ≥ A - 2 * X.sum a := by
  classical
  let s : ℚ := X.sum a
  have htwo_s : 2 * s ≤ A := by
    dsimp [s]
    linarith
  have hminor_each : ∀ i, i ∈ X → a i ≤ A - a i := by
    intro i hi
    have htail_nonneg : 0 ≤ (X.erase i).sum a := by
      exact Finset.sum_nonneg (fun j hj => ha_nonneg j (Finset.mem_of_mem_erase hj))
    have hs_decomp : s = (X.erase i).sum a + a i := by
      dsimp [s]
      rw [← Finset.sum_erase_add _ _ hi]
    have hai_le_s : a i ≤ s := by
      linarith
    have htwo_ai : 2 * a i ≤ A := by
      linarith
    linarith
  have hsum_point :
      X.sum (fun i => A - 2 * a i) ≤ X.sum (fun i => 25 * rho i) := by
    exact Finset.sum_le_sum (fun i hi => hpoint i hi (hminor_each i hi))
  have hsubset :
      (X.card : ℚ) * A - 2 * X.sum a
        ≤ 25 * X.sum rho := by
    calc
      (X.card : ℚ) * A - 2 * X.sum a
          = X.sum (fun i => A - 2 * a i) := by
              rw [Finset.sum_sub_distrib]
              simp [mul_comm]
              rw [← Finset.sum_mul]
      _ ≤ X.sum (fun i => 25 * rho i) := hsum_point
      _ = 25 * X.sum rho := by
              rw [← Finset.mul_sum]
  have hcard_pos_nat : 0 < X.card := Finset.card_pos.mpr hX
  have hcard_ge_one : (1 : ℚ) ≤ X.card := by
    exact_mod_cast Nat.succ_le_of_lt hcard_pos_nat
  have hA_le_cardA : A ≤ (X.card : ℚ) * A := by
    nlinarith
  linarith

end SchurAbsorption
end Erdos23
