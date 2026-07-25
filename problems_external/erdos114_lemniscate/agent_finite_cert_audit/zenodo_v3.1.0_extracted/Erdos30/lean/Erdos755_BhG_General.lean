/-
  Erdős Problem #755 — General B_h[g] Sum-Counting Bound

  Theorem: For a B_h[g] set A ⊆ [0, N] (ordered form, every sum has
  at most h!·g ordered h-tuple representations),
      |A|^h ≤ h! · g · (h·N + 1).

  This is the FULL general theorem covering the entire #755 problem
  at the elementary sum-counting level. Specializations:
    - h=2: |A|² ≤ 2g(2N+1)                  (`Erdos755_BhG.b2g_sum_count`)
    - h=3: |A|³ ≤ 6g(3N+1)                   (`Erdos755_B3G.b3g_sum_count`)
    - h=2, g=1: Sidon, |A|² ≤ 2(2N+1) = 4N+2 (classical Halberstam–Roth)

  Proof architecture: Pattern 1 (Finset.card_eq_sum_card_fiberwise).
  - |A^h| = |A|^h via `Fintype.card_piFinset_const`.
  - Every h-tuple (a_1, ..., a_h) with each a_i ∈ A ⊆ [0, N] has
    sum in [0, hN], hence in Finset.range (hN + 1).
  - Fiberwise partition by sum; each fiber has ≤ h!·g elements by hypothesis.
  - Total: |A|^h ≤ (hN+1) · h!·g.

  Lean version: leanprover/lean4:v4.24.0
  Mathlib version: f897ebcf72cd16f89ab4577d0c826cd14afaafc7
-/

import Mathlib

open Finset Nat
open scoped BigOperators

namespace Erdos.BhG.General

/-- **General ordered B_h[g] predicate.**

A is B_h[g] iff every sum s has at most h!·g ordered h-tuple representations
in A^h (equivalently, at most g *unordered* representations). -/
abbrev IsBhGSet (A : Finset ℕ) (h g : ℕ) : Prop :=
  ∀ s : ℕ,
    ((Fintype.piFinset (fun _ : Fin h => A)).filter
      (fun f : Fin h → ℕ => ∑ i, f i = s)).card ≤ h.factorial * g

/-- **MAIN THEOREM: General Sum-Counting Bound for B_h[g]**

For a B_h[g] set A ⊆ Finset.range (N + 1),
    |A|^h ≤ h! · g · (hN + 1). -/
theorem bhg_sum_count (A : Finset ℕ) (N h g : ℕ)
    (hS : IsBhGSet A h g)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card ^ h ≤ h.factorial * g * (h * N + 1) := by
  -- Step 1: |A^h| = |A|^h
  have h_pow :
      A.card ^ h = (Fintype.piFinset (fun _ : Fin h => A)).card := by
    rw [Fintype.card_piFinset_const]
  rw [h_pow]
  -- Step 2: Every h-tuple has sum in range(hN+1)
  have h_sum_range :
      ∀ f ∈ Fintype.piFinset (fun _ : Fin h => A),
        ∑ i, f i ∈ Finset.range (h * N + 1) := by
    intro f hf
    rw [Fintype.mem_piFinset] at hf
    have h_each : ∀ i : Fin h, f i ≤ N := fun i => by
      have := Finset.mem_range.mp (hA (hf i))
      omega
    rw [Finset.mem_range]
    calc ∑ i, f i
        ≤ ∑ _i : Fin h, N := Finset.sum_le_sum (fun i _ => h_each i)
      _ = h * N := by
          rw [Finset.sum_const, Finset.card_univ, Fintype.card_fin, smul_eq_mul]
      _ < h * N + 1 := by omega
  -- Step 3: fiberwise partition
  have h_sum_eq :
      (Fintype.piFinset (fun _ : Fin h => A)).card =
        ∑ s ∈ Finset.range (h * N + 1),
          ((Fintype.piFinset (fun _ : Fin h => A)).filter
            (fun f : Fin h → ℕ => ∑ i, f i = s)).card :=
    Finset.card_eq_sum_card_fiberwise h_sum_range
  -- Step 4 + 5: combine
  rw [h_sum_eq]
  calc ∑ s ∈ Finset.range (h * N + 1),
          ((Fintype.piFinset (fun _ : Fin h => A)).filter
            (fun f : Fin h → ℕ => ∑ i, f i = s)).card
      ≤ ∑ _s ∈ Finset.range (h * N + 1), h.factorial * g :=
        Finset.sum_le_sum (fun s _ => hS s)
    _ = (h * N + 1) * (h.factorial * g) := by
        rw [Finset.sum_const, Finset.card_range, smul_eq_mul]
    _ = h.factorial * g * (h * N + 1) := by ring

/-- **Sidon (h=2, g=1) specialization recovered.** -/
theorem bhg_sidon (A : Finset ℕ) (N : ℕ)
    (hS : IsBhGSet A 2 1)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card ^ 2 ≤ 4 * N + 2 := by
  have := bhg_sum_count A N 2 1 hS hA
  simp [Nat.factorial] at this
  omega

/-- **B_3 (h=3, g=1) specialization.** -/
theorem bhg_b3_sidon (A : Finset ℕ) (N : ℕ)
    (hS : IsBhGSet A 3 1)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card ^ 3 ≤ 18 * N + 6 := by
  have := bhg_sum_count A N 3 1 hS hA
  simp [Nat.factorial] at this
  omega

end Erdos.BhG.General
