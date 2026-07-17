import FormalConjectures.Util.ProblemImports

/-!
# Arithmetic assembly for WOWII Conjecture 143

This verifies the denominator-free case split used in the informal proof.
-/

theorem conjecture143_of_case_bounds
    (t g σ : ℕ)
    (hg : 3 ≤ g)
    (hσ : 0 < σ)
    (hlarge : 2 ≤ σ → g - 1 ≤ t)
    (hleaf : σ = 1 → g + 1 ≤ t) :
    (g : ℝ) + 1 ≤ (t : ℝ) * (σ : ℝ) := by
  have hnat : g + 1 ≤ t * σ := by
    by_cases hσ1 : σ = 1
    · simpa [hσ1] using hleaf hσ1
    · have hσ2 : 2 ≤ σ := by omega
      calc
        g + 1 ≤ 2 * (g - 1) := by omega
        _ ≤ 2 * t := Nat.mul_le_mul_left 2 (hlarge hσ2)
        _ = t * 2 := Nat.mul_comm 2 t
        _ ≤ t * σ := Nat.mul_le_mul_left t hσ2
  exact_mod_cast hnat
