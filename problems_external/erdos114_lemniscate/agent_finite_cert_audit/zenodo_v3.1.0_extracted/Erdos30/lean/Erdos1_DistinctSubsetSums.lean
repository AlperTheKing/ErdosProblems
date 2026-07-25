/-
  Erdős Problem #1 — Distinct Subset Sums (Elementary Upper Bound)

  Classical problem (Erdős, $500 prize): if A ⊆ {1, ..., N} has distinct
  subset sums (all 2^|A| sums ∑_{a∈S} a for S ⊆ A are distinct), how
  large can |A| be?

  Erdős conjectured |A| ≤ log₂(N) + O(1). The best known bounds are
  log₂(N) + (1/2) log₂ log₂(N) + O(1) (Dubroff–Fox–Xu 2021 style).

  This file proves the elementary warm-up bound:
      2^|A| ≤ |A|·N + 1
  which gives |A| ≤ log₂(N) + log₂ log₂(N) + O(1).

  **Proof (elementary):** The map S ↦ ∑_{a∈S} a is injective on the
  powerset of A (by hypothesis), so
      |image| = |A.powerset| = 2^|A|.
  Each subset sum lies in [0, |A|·N] (since every a ≤ N and |S| ≤ |A|),
  so the image sits inside Finset.range(|A|·N + 1). Therefore
      2^|A| = |image| ≤ |A|·N + 1.

  This is the "subset sum injection" recipe — distinct from Pattern 1
  (fiberwise partition). It complements the B_h[g] file family.

  Lean version: leanprover/lean4:v4.24.0
  Mathlib version: f897ebcf72cd16f89ab4577d0c826cd14afaafc7
-/

import Mathlib

open Finset

namespace Erdos.DistinctSubsetSums

/-- **Distinct subset sums predicate.**

A has distinct subset sums iff the subset-sum map S ↦ ∑_{a∈S} a is
injective on the powerset of A. -/
def HasDistinctSubsetSums (A : Finset ℕ) : Prop :=
  Set.InjOn (fun s : Finset ℕ => s.sum id) ↑A.powerset

/-- **MAIN THEOREM: Elementary distinct-subset-sums bound.**

If A ⊆ [0, N] has distinct subset sums, then 2^|A| ≤ |A|·N + 1.

This gives the classical elementary upper bound |A| ≤ log₂(|A|·N + 1). -/
theorem distinct_subset_sum_bound (A : Finset ℕ) (N : ℕ)
    (hD : HasDistinctSubsetSums A)
    (hA : A ⊆ Finset.range (N + 1)) :
    2 ^ A.card ≤ A.card * N + 1 := by
  -- Step 1: |powerset A| = 2^|A|
  have h_pow : A.powerset.card = 2 ^ A.card := Finset.card_powerset A
  -- Step 2: every subset sum lies in range(|A|·N + 1)
  have h_sub : ∀ s ∈ A.powerset, s.sum id ∈ Finset.range (A.card * N + 1) := by
    intro s hs
    rw [Finset.mem_powerset] at hs
    rw [Finset.mem_range]
    have h_each : ∀ a ∈ s, a ≤ N := by
      intro a ha
      have haA : a ∈ A := hs ha
      have := Finset.mem_range.mp (hA haA)
      omega
    have h_card_le : s.card ≤ A.card := Finset.card_le_card hs
    calc s.sum id
        ≤ ∑ _a ∈ s, N := Finset.sum_le_sum (fun a ha => h_each a ha)
      _ = s.card * N := by rw [Finset.sum_const, smul_eq_mul]
      _ ≤ A.card * N := Nat.mul_le_mul_right N h_card_le
      _ < A.card * N + 1 := by omega
  -- Step 3: injectivity ⇒ |image| = |powerset|
  have h_img_card :
      (A.powerset.image (fun s : Finset ℕ => s.sum id)).card = A.powerset.card :=
    Finset.card_image_of_injOn hD
  -- Step 4: image ⊆ range(|A|·N + 1)
  have h_img_sub :
      A.powerset.image (fun s : Finset ℕ => s.sum id) ⊆
        Finset.range (A.card * N + 1) := by
    intro x hx
    rw [Finset.mem_image] at hx
    obtain ⟨s, hs, heq⟩ := hx
    rw [← heq]
    exact h_sub s hs
  -- Step 5: combine
  have h_card_le :
      (A.powerset.image (fun s : Finset ℕ => s.sum id)).card ≤
        (Finset.range (A.card * N + 1)).card :=
    Finset.card_le_card h_img_sub
  rw [Finset.card_range] at h_card_le
  rw [h_img_card, h_pow] at h_card_le
  exact h_card_le

/-- **Size bound corollary.**

The set-theoretic bound on |A|: since 2^|A| ≤ |A|·N + 1, we have
|A| ≤ log₂(|A|·N + 1). Stated as an explicit inequality in a form
useful for downstream comparison. -/
theorem distinct_subset_sum_pow_bound (A : Finset ℕ) (N : ℕ)
    (hD : HasDistinctSubsetSums A)
    (hA : A ⊆ Finset.range (N + 1)) :
    2 ^ A.card ≤ A.card * N + 1 :=
  distinct_subset_sum_bound A N hD hA

end Erdos.DistinctSubsetSums
