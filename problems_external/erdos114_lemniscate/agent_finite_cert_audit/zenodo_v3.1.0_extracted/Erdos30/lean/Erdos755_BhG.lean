/-
  Erdős Problem #755 — B_h[g] Sequences: Sum-Counting Density Bound for B_2[g]

  Theorem: For a B_2[g] set A ⊆ [0, N], |A|² ≤ 2·g·(2N+1).

  Definition (ordered): A is B_2[g] iff every sum s has at most 2g ordered
  representations as (a,b) ∈ A×A with a+b = s. This is the "ordered" form
  of the classical unordered B_h[g] definition (unordered ≤ g ⟹ ordered ≤ 2g),
  chosen here to streamline sum-counting.

  Sidon (g=1) specialization: ≤ 2 ordered reps per sum, matching the
  classical Sidon definition via unordered uniqueness.

  Proof sketch (sum counting):
    |A×A| = k² decomposes by sum s ∈ [0, 2N]. Each fiber has ≤ 2g elements.
    Therefore k² ≤ 2g(2N+1).

  Morphism note (PHYS-QC-001 quasicrystal bridge):
    This generalizes Erdős #30 (Sidon = B_2[1]). PMF transfer-matrix
    experiments (EXP 2026-04-16) show α ≈ 1.02 for B_2[2] at W ≤ 25,
    matching the Sidon slope and supporting the putative morphism.

  Lean version: leanprover/lean4:v4.24.0
  Mathlib version: f897ebcf72cd16f89ab4577d0c826cd14afaafc7
-/

import Mathlib

open Finset Nat

namespace Erdos.B2G

/-- A B_2[g] set (ordered form): every sum s has at most 2g ordered
    pair representations in A × A.
    Declared as `abbrev` for automatic unfolding across module boundaries. -/
abbrev IsB2GSet (A : Finset ℕ) (g : ℕ) : Prop :=
  ∀ s : ℕ, ((A ×ˢ A).filter (fun p : ℕ × ℕ => p.1 + p.2 = s)).card ≤ 2 * g

/--
  **MAIN THEOREM: Sum-Counting Density Bound for B_2[g]**

  For a B_2[g] set A ⊆ Finset.range (N + 1), the cardinality satisfies:
      |A|² ≤ 2 · g · (2N + 1)

  Proof Strategy:
  1. |A × A| = |A|²                                       (product cardinality)
  2. Every (a,b) ∈ A × A has a+b ∈ Finset.range (2N+1)     (range bound)
  3. |A × A| = Σ_{s ∈ range(2N+1)} |{(a,b) : a+b = s}|     (fiberwise partition)
  4. Each fiber has card ≤ 2g                              (B_2[g] hypothesis)
  5. Σ ≤ (2N+1) · 2g = 2·g·(2N+1)                          (constant bound)
-/
theorem b2g_sum_count (A : Finset ℕ) (N g : ℕ)
    (hS : IsB2GSet A g)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card ^ 2 ≤ 2 * g * (2 * N + 1) := by
  -- Step 1: Reframe k² as |A × A|
  have h_sq : A.card ^ 2 = (A ×ˢ A).card := by
    rw [Finset.card_product, sq]
  rw [h_sq]
  -- Step 2: Every (a,b) ∈ A × A has sum in Finset.range (2N + 1)
  have h_sum_range : ∀ p ∈ A ×ˢ A, p.1 + p.2 ∈ Finset.range (2 * N + 1) := by
    intro p hp
    rw [Finset.mem_product] at hp
    have ha := Finset.mem_range.mp (hA hp.1)
    have hb := Finset.mem_range.mp (hA hp.2)
    rw [Finset.mem_range]
    omega
  -- Step 3: |A × A| = Σ_s |fiber at s|
  have h_sum_eq :
      (A ×ˢ A).card =
        ∑ s ∈ Finset.range (2 * N + 1),
          ((A ×ˢ A).filter (fun p : ℕ × ℕ => p.1 + p.2 = s)).card := by
    exact Finset.card_eq_sum_card_fiberwise h_sum_range
  -- Step 4 + 5: Combine via sum bound
  rw [h_sum_eq]
  calc ∑ s ∈ Finset.range (2 * N + 1),
          ((A ×ˢ A).filter (fun p : ℕ × ℕ => p.1 + p.2 = s)).card
      ≤ ∑ _s ∈ Finset.range (2 * N + 1), 2 * g :=
        Finset.sum_le_sum (fun s _ => hS s)
    _ = (2 * N + 1) * (2 * g) := by
        rw [Finset.sum_const, Finset.card_range, smul_eq_mul]
    _ = 2 * g * (2 * N + 1) := by ring

/--
  **Corollary:** For a B_2[g] set A ⊆ [0, N], |A| ≤ ⌈√(2g(2N+1))⌉.
  Stated as the square bound (cleaner for omega). -/
theorem b2g_card_sq_bound (A : Finset ℕ) (N g : ℕ)
    (hS : IsB2GSet A g)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card * A.card ≤ 2 * g * (2 * N + 1) := by
  have h := b2g_sum_count A N g hS hA
  have : A.card ^ 2 = A.card * A.card := sq A.card
  omega

/--
  **Sidon specialization:** Sidon sets are B_2[1] in the ordered-form
  convention (each sum has ≤ 2 ordered representations: (a,b) and (b,a)).

  This gives |A|² ≤ 4N + 2 for Sidon A ⊆ [0, N], weaker than the
  difference-counting bound |A|(|A|-1) ≤ 2N from `Erdos30_difference_counting`
  but derived via the B_2[g] framework. -/
theorem sidon_via_b2g (A : Finset ℕ) (N : ℕ)
    (hS : IsB2GSet A 1)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card ^ 2 ≤ 4 * N + 2 := by
  have := b2g_sum_count A N 1 hS hA
  omega

end Erdos.B2G
