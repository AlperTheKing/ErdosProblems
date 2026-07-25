/-
  Erdős Problem #755 — Higher-Order Specializations (h = 4, 5, 6)

  Direct specializations of the general B_h[g] bound
      |A|^h ≤ h! · g · (hN + 1)
  (proved in `Erdos755_BhG_General`) to h = 4, 5, 6.

  Specializations:
    h=4, g=1:  |A|^4 ≤ 24 · (4N+1) = 96N + 24
    h=5, g=1:  |A|^5 ≤ 120 · (5N+1) = 600N + 120
    h=6, g=1:  |A|^6 ≤ 720 · (6N+1) = 4320N + 720

  All follow trivially from `bhg_sum_count` with h substituted.

  Lean version: leanprover/lean4:v4.24.0
  Mathlib version: f897ebcf72cd16f89ab4577d0c826cd14afaafc7
-/

import Mathlib
import Erdos755_BhG_General

open Finset Nat

namespace Erdos.BhG.HigherOrder

open Erdos.BhG.General

/-- **B_4 Sidon bound.** |A|^4 ≤ 96N + 24 for B_4[1] sets in [0, N]. -/
theorem b4_sidon_bound (A : Finset ℕ) (N : ℕ)
    (hS : IsBhGSet A 4 1)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card ^ 4 ≤ 96 * N + 24 := by
  have := bhg_sum_count A N 4 1 hS hA
  simp [Nat.factorial] at this
  omega

/-- **B_5 Sidon bound.** |A|^5 ≤ 600N + 120 for B_5[1] sets in [0, N]. -/
theorem b5_sidon_bound (A : Finset ℕ) (N : ℕ)
    (hS : IsBhGSet A 5 1)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card ^ 5 ≤ 600 * N + 120 := by
  have := bhg_sum_count A N 5 1 hS hA
  simp [Nat.factorial] at this
  omega

/-- **B_6 Sidon bound.** |A|^6 ≤ 4320N + 720 for B_6[1] sets in [0, N]. -/
theorem b6_sidon_bound (A : Finset ℕ) (N : ℕ)
    (hS : IsBhGSet A 6 1)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card ^ 6 ≤ 4320 * N + 720 := by
  have := bhg_sum_count A N 6 1 hS hA
  simp [Nat.factorial] at this
  omega

/-- **General B_h[1] Sidon form.** |A|^h ≤ h! · (hN + 1). -/
theorem bh_sidon_bound (A : Finset ℕ) (N h : ℕ)
    (hS : IsBhGSet A h 1)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card ^ h ≤ h.factorial * (h * N + 1) := by
  have := bhg_sum_count A N h 1 hS hA
  simpa using this

end Erdos.BhG.HigherOrder
