/-
  Erdos Problem #30 -- Shared Sidon Set Definition
  =================================================

  This file provides the canonical IsSidonSet definition used by all
  Erdos30_*.lean files. Centralizing the definition eliminates namespace
  duplication and enables cross-file theorem imports.

  **Lean version**: leanprover/lean4:v4.24.0
  **Mathlib version**: f897ebcf72cd16f89ab4577d0c826cd14afaafc7
-/

import Mathlib

open Finset Nat

namespace Erdos.Sidon

/-- A Sidon set (B₂ set): all pairwise sums a + b (a ≤ b) are distinct.
    Equivalently: if a₁ + b₁ = a₂ + b₂ with a₁ ≤ b₁ and a₂ ≤ b₂,
    then a₁ = a₂ and b₁ = b₂.
    Declared as `abbrev` for automatic unfolding across module boundaries. -/
abbrev IsSidonSet (A : Finset ℕ) : Prop :=
  ∀ a₁ ∈ A, ∀ b₁ ∈ A, ∀ a₂ ∈ A, ∀ b₂ ∈ A,
    a₁ ≤ b₁ → a₂ ≤ b₂ → a₁ + b₁ = a₂ + b₂ → (a₁ = a₂ ∧ b₁ = b₂)

end Erdos.Sidon

