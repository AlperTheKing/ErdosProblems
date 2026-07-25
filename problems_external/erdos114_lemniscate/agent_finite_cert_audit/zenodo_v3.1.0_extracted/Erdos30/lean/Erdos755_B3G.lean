/-
  Erdős Problem #755 — Extension: B_3[g] Sum-Counting Bound

  Theorem: For a B_3[g] set A ⊆ [0, N],
    |A|³ ≤ 6 · g · (3N + 1).

  Definition (ordered B_3[g]): A is B_3[g] iff every sum s has at most
  6g = 3!·g ordered triple representations (a,b,c) ∈ A × A × A with
  a + b + c = s. The 3! factor accounts for ordered vs unordered triples.

  Proof: |A × A × A| = |A|³ partitions by sum s ∈ [0, 3N]. Each fiber
  has ≤ 6g elements. Therefore |A|³ ≤ 6g(3N+1).

  This is the direct extension of `Erdos755_BhG.b2g_sum_count` from h=2
  to h=3, using the same Pattern 1 recipe (Finset.card_eq_sum_card_fiberwise).

  Lean version: leanprover/lean4:v4.24.0
  Mathlib version: f897ebcf72cd16f89ab4577d0c826cd14afaafc7
-/

import Mathlib

open Finset Nat

namespace Erdos.B3G

/-- A B_3[g] set (ordered form): every sum s has at most 6g = 3!·g ordered
    triple representations in A × A × A. -/
abbrev IsB3GSet (A : Finset ℕ) (g : ℕ) : Prop :=
  ∀ s : ℕ,
    (((A ×ˢ A) ×ˢ A).filter (fun p : (ℕ × ℕ) × ℕ => p.1.1 + p.1.2 + p.2 = s)).card ≤ 6 * g

/-- **MAIN THEOREM: Sum-Counting Density Bound for B_3[g]**

For a B_3[g] set A ⊆ Finset.range (N + 1),
    |A|³ ≤ 6 · g · (3N + 1).

Corollary: |A| = O((gN)^{1/3}), matching the conjectured order of
magnitude for B_h[g] sets up to constants. -/
theorem b3g_sum_count (A : Finset ℕ) (N g : ℕ)
    (hS : IsB3GSet A g)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card ^ 3 ≤ 6 * g * (3 * N + 1) := by
  -- Step 1: |A × A × A| = |A|³
  have h_cube : A.card ^ 3 = ((A ×ˢ A) ×ˢ A).card := by
    rw [Finset.card_product, Finset.card_product]; ring
  rw [h_cube]
  -- Step 2: Every (a,b,c) has sum in range(3N+1)
  have h_sum_range :
      ∀ p ∈ (A ×ˢ A) ×ˢ A, p.1.1 + p.1.2 + p.2 ∈ Finset.range (3 * N + 1) := by
    intro p hp
    rw [Finset.mem_product, Finset.mem_product] at hp
    have ha := Finset.mem_range.mp (hA hp.1.1)
    have hb := Finset.mem_range.mp (hA hp.1.2)
    have hc := Finset.mem_range.mp (hA hp.2)
    rw [Finset.mem_range]; omega
  -- Step 3: fiberwise partition
  have h_sum_eq :
      ((A ×ˢ A) ×ˢ A).card =
        ∑ s ∈ Finset.range (3 * N + 1),
          (((A ×ˢ A) ×ˢ A).filter
            (fun p : (ℕ × ℕ) × ℕ => p.1.1 + p.1.2 + p.2 = s)).card :=
    Finset.card_eq_sum_card_fiberwise h_sum_range
  -- Step 4 + 5: combine via sum bound
  rw [h_sum_eq]
  calc ∑ s ∈ Finset.range (3 * N + 1),
          (((A ×ˢ A) ×ˢ A).filter
            (fun p : (ℕ × ℕ) × ℕ => p.1.1 + p.1.2 + p.2 = s)).card
      ≤ ∑ _s ∈ Finset.range (3 * N + 1), 6 * g :=
        Finset.sum_le_sum (fun s _ => hS s)
    _ = (3 * N + 1) * (6 * g) := by
        rw [Finset.sum_const, Finset.card_range, smul_eq_mul]
    _ = 6 * g * (3 * N + 1) := by ring

/-- **Cube bound (cleaner for omega).** -/
theorem b3g_card_cube_bound (A : Finset ℕ) (N g : ℕ)
    (hS : IsB3GSet A g)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card * A.card * A.card ≤ 6 * g * (3 * N + 1) := by
  have h := b3g_sum_count A N g hS hA
  have h_eq : A.card ^ 3 = A.card * A.card * A.card := by ring
  omega

/-- **B_3[1] specialization (Sidon-like B_3 set):**

For a B_3[1] set A ⊆ [0, N], |A|³ ≤ 6(3N + 1) = 18N + 6. -/
theorem b3_sidon_bound (A : Finset ℕ) (N : ℕ)
    (hS : IsB3GSet A 1)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card ^ 3 ≤ 18 * N + 6 := by
  have := b3g_sum_count A N 1 hS hA
  omega

end Erdos.B3G
