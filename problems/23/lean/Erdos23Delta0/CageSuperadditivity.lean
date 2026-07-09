import Mathlib

/-!
# Component-decomposition assembly arithmetic (2026-07-08)

The GERSH bound `Γ ≤ N²` is proved per B-connected component and summed. The rows partition by component, so
`Γ = Σ_components Γ_i`, and the per-component bound is `Γ_i = Σ_{rows in comp i} ℓ² ≤ N_i²` (this is gap#1, applied to
each component). The ASSEMBLY step — combining the per-component bounds into the global bound — is the arithmetic fact
`Σ_i N_i² ≤ (Σ_i N_i)² = N²` for nonnegative `N_i`. That arithmetic is NOT gated on gap#1; it is the superadditivity of
squares, proved here. Together with the (gap#1-gated) per-component bounds it gives
`Γ = Σ Γ_i ≤ Σ N_i² ≤ (Σ N_i)² = N²`.

Axiom-clean (`{propext, Classical.choice, Quot.sound}`); No forbidden proof shortcuts.
-/

namespace Erdos23Delta0
namespace CageSuperadditivity

open Finset

/-- **Superadditivity of squares.** For nonnegative reals, `Σ aᵢ² ≤ (Σ aᵢ)²`. (The off-diagonal cross terms of the
    expanded square are nonnegative, so the diagonal `Σ aᵢ²` is dominated by the full double sum `(Σ aᵢ)²`.) -/
theorem sum_sq_le_sq_sum {ι : Type*} (s : Finset ι) (a : ι → ℚ) (h : ∀ i ∈ s, 0 ≤ a i) :
    ∑ i ∈ s, (a i) ^ 2 ≤ (∑ i ∈ s, a i) ^ 2 := by
  have key : (∑ i ∈ s, a i) ^ 2 = ∑ i ∈ s, ∑ j ∈ s, a i * a j := by
    rw [pow_two, Finset.sum_mul_sum]
  rw [key]
  apply Finset.sum_le_sum
  intro i hi
  rw [pow_two]
  exact Finset.single_le_sum (f := fun j => a i * a j)
    (fun j hj => mul_nonneg (h i hi) (h j hj)) hi

/-- **Component-decomposition assembly.** If `Γ = Σ_i Γ_i` (rows partition by component) and each component satisfies
    the per-component bound `Γ_i ≤ N_i²` (gap#1 per component) with `N_i ≥ 0` and `Σ_i N_i = N` (the components
    partition the vertices), then `Γ ≤ N²`. This is the non-gated glue that lifts per-component gap#1 to the global
    Γ ≤ N². -/
theorem gamma_le_Nsq_of_components {ι : Type*} (s : Finset ι) (Γ : ι → ℚ) (N : ι → ℚ)
    (Ntot Γtot : ℚ)
    (hΓtot : Γtot = ∑ i ∈ s, Γ i)
    (hNtot : Ntot = ∑ i ∈ s, N i)
    (hNnonneg : ∀ i ∈ s, 0 ≤ N i)
    (hcomp : ∀ i ∈ s, Γ i ≤ (N i) ^ 2) :
    Γtot ≤ Ntot ^ 2 := by
  calc Γtot = ∑ i ∈ s, Γ i := hΓtot
    _ ≤ ∑ i ∈ s, (N i) ^ 2 := Finset.sum_le_sum hcomp
    _ ≤ (∑ i ∈ s, N i) ^ 2 := sum_sq_le_sq_sum s N hNnonneg
    _ = Ntot ^ 2 := by rw [hNtot]

/-- **`Γ ≥ 25·m`.** In a triangle-free graph every bad-edge row length is `ℓ ≥ 5`, so each `ℓ² ≥ 25` and
    `Γ = Σ ℓ² ≥ 25·(#bad edges)`. This is the mathematical content of the `GammaBetaFacts.gammaLower` interface field,
    discharged from `ℓ ≥ 5` (non-gated). -/
theorem sum_sq_ge_25_mul_card {ι : Type*} (s : Finset ι) (ell : ι → ℚ) (h : ∀ i ∈ s, 5 ≤ ell i) :
    25 * (s.card : ℚ) ≤ ∑ i ∈ s, (ell i) ^ 2 := by
  have hpt : ∀ i ∈ s, (25 : ℚ) ≤ (ell i) ^ 2 := by
    intro i hi; nlinarith [h i hi, sq_nonneg (ell i - 5)]
  calc 25 * (s.card : ℚ) = ∑ _i ∈ s, (25 : ℚ) := by
        rw [Finset.sum_const, nsmul_eq_mul]; ring
    _ ≤ ∑ i ∈ s, (ell i) ^ 2 := Finset.sum_le_sum hpt

/-- **`badCount ≤ N²/25` from `ℓ ≥ 5` and `Γ ≤ N²`** (non-gated arithmetic core of the final bound). With each row
    length `ℓ ≥ 5` and `Γ = Σ ℓ² ≤ N²`, the number of bad edges satisfies `m ≤ N²/25`. For a maximum cut `β = m`, so
    this is exactly `β ≤ N²/25` once the (gap#1-gated) `Γ ≤ N²` is supplied. -/
theorem card_le_Nsq_div_25 {ι : Type*} (s : Finset ι) (ell : ι → ℚ) (Nq : ℚ)
    (hell : ∀ i ∈ s, 5 ≤ ell i)
    (hgamma : ∑ i ∈ s, (ell i) ^ 2 ≤ Nq ^ 2) :
    (s.card : ℚ) ≤ Nq ^ 2 / 25 := by
  have h25 : 25 * (s.card : ℚ) ≤ Nq ^ 2 := le_trans (sum_sq_ge_25_mul_card s ell hell) hgamma
  linarith


end CageSuperadditivity
end Erdos23Delta0
