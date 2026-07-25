/-
  Erdős Problem #166 — Sum-Free Sets (Elementary Upper Bound)

  A ⊆ ℕ is **sum-free** iff a + b ∉ A for all a, b ∈ A (allowing a = b).
  Classical elementary bound: if A ⊆ [1, N] is sum-free, then
      2 |A| ≤ N + 1.
  Tight: A = {⌈N/2⌉+1, ..., N} achieves |A| = ⌊N/2⌋.

  **Proof (elementary, shift-injection):**
  Let a = max A. Define φ : A → [0, a] by φ(x) = a - x. Then:
    1. φ is injective on A (since x, y ≤ a in ℕ-subtraction).
    2. φ(A) ∩ A = ∅. Indeed, if a - x = y ∈ A with x ∈ A, then
       x + y = a ∈ A, contradicting sum-free.
    3. A ⊆ [0, a] and φ(A) ⊆ [0, a].
  Therefore |A| + |φ(A)| ≤ a + 1, hence 2|A| ≤ a + 1 ≤ N + 1.

  Lean version: leanprover/lean4:v4.24.0
  Mathlib version: f897ebcf72cd16f89ab4577d0c826cd14afaafc7
-/

import Mathlib

open Finset

namespace Erdos.SumFree

/-- **Sum-free predicate.**

A ⊆ ℕ is sum-free iff a + b ∉ A for all a, b ∈ A. -/
abbrev IsSumFree (A : Finset ℕ) : Prop :=
  ∀ a ∈ A, ∀ b ∈ A, a + b ∉ A

/-- **MAIN THEOREM: Sum-free bound (elementary).**

If A ⊆ [1, N] is sum-free, then 2|A| ≤ N + 1.

(Hypothesis `hA_pos` excludes 0 from A so that the shift-injection is clean:
without it, 0 + 0 = 0 ∈ A would fail sum-free trivially if 0 ∈ A, so the
bound still holds but requires no hypothesis; we include it to match the
classical [1, N] setting.) -/
theorem sumfree_bound (A : Finset ℕ) (N : ℕ)
    (hSF : IsSumFree A)
    (hA : A ⊆ Finset.range (N + 1)) :
    2 * A.card ≤ N + 1 := by
  -- Case: A is empty
  by_cases hemp : A = ∅
  · subst hemp; simp
  -- Nonempty case: take max
  have hne : A.Nonempty := Finset.nonempty_iff_ne_empty.mpr hemp
  set a := A.max' hne with ha_def
  have ha_mem : a ∈ A := A.max'_mem hne
  have ha_le_N : a ≤ N := by
    have := Finset.mem_range.mp (hA ha_mem)
    omega
  have ha_max : ∀ x ∈ A, x ≤ a := fun x hx => A.le_max' x hx
  -- Define the shifted image A' = {a - x : x ∈ A}
  let shift : ℕ → ℕ := fun x => a - x
  -- Step 1: shift is injective on A
  have h_inj : Set.InjOn shift ↑A := by
    intro x hx y hy hxy
    simp only [shift] at hxy
    have hxa := ha_max x hx
    have hya := ha_max y hy
    omega
  -- Step 2: shifted image has the same cardinality
  have h_img_card : (A.image shift).card = A.card := Finset.card_image_of_injOn h_inj
  -- Step 3: shifted image is in range(a + 1)
  have h_img_sub : A.image shift ⊆ Finset.range (a + 1) := by
    intro y hy
    rw [Finset.mem_image] at hy
    obtain ⟨x, hx, heq⟩ := hy
    rw [Finset.mem_range]
    have : shift x ≤ a := by simp only [shift]; omega
    omega
  -- Step 4: A ⊆ range(a + 1)
  have h_A_sub : A ⊆ Finset.range (a + 1) := by
    intro x hx
    rw [Finset.mem_range]
    have := ha_max x hx
    omega
  -- Step 5: A and shift(A) are disjoint
  have h_disj : Disjoint A (A.image shift) := by
    rw [Finset.disjoint_left]
    intro y hy hy_img
    rw [Finset.mem_image] at hy_img
    obtain ⟨x, hx, heq⟩ := hy_img
    -- y = a - x, y ∈ A, x ∈ A.  Sum-free: x + y ∉ A.  But x + y = a ∈ A.
    have hxa := ha_max x hx
    have hxy_eq : x + y = a := by simp only [shift] at heq; omega
    have : x + y ∈ A := hxy_eq ▸ ha_mem
    exact hSF x hx y hy this
  -- Step 6: combine — |A| + |A| = |A ∪ shift(A)| ≤ a + 1
  have h_union_card :
      (A ∪ A.image shift).card = A.card + (A.image shift).card :=
    Finset.card_union_of_disjoint h_disj
  have h_union_sub : A ∪ A.image shift ⊆ Finset.range (a + 1) :=
    Finset.union_subset h_A_sub h_img_sub
  have h_union_card_le : (A ∪ A.image shift).card ≤ (Finset.range (a + 1)).card :=
    Finset.card_le_card h_union_sub
  rw [Finset.card_range] at h_union_card_le
  rw [h_union_card, h_img_card] at h_union_card_le
  -- 2|A| ≤ a + 1 ≤ N + 1
  omega

end Erdos.SumFree
