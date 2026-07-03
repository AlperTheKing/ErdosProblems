/-
Erdős #23 δ=0 — Branch-A Interface (per LEAN_BRANCHA_BLUEPRINT_GPTPRO.md, order step 1).
Numeric assembly cores, all ℚ-arithmetic with combinatorial inputs as hypotheses:
  • strongActive5_implies_gersh : I − N ≤ (2/3)η ⟹ I ≤ N + η   (β_P ≤ 1 from A1);
  • a1_5mask_absorption : the five 4-mask average closes ODL-X for N ≥ 10;
  • netDW_assembly : C5-RS + uniform width ⟹ the row-sum GERSH bound
    (Σ max(sᵢ,τ) = 5τ + Σ(sᵢ−τ)₊ with 5τ = N − 25η/N).
-/

import Mathlib

namespace Erdos23Delta0
namespace BranchA

/-- Abstract per-row numeric data. -/
structure RowData where
  N : ℚ
  eta : ℚ
  I : ℚ

/-- The GERSH row bound. -/
def GershBound (R : RowData) : Prop := R.I ≤ R.N + R.eta

/-- The strong active-5 leaf (from A1 with β = 2/3). -/
def StrongActive5Bound (R : RowData) : Prop := R.I - R.N ≤ (2:ℚ)/3 * R.eta

theorem strongActive5_implies_gersh (R : RowData) (heta : 0 ≤ R.eta)
    (h : StrongActive5Bound R) : GershBound R := by
  unfold StrongActive5Bound at h
  unfold GershBound
  linarith

/-- A1-5mask absorption arithmetic: for N ≥ 10, summing the five 4-mask bounds
    (each ≤ (25/N + 7/30)η, coordinates counted 4×) closes the full-mask ODL-X. -/
theorem a1_5mask_absorption (N X eta : ℚ) (hN : 10 ≤ N) (heta : 0 ≤ eta)
    (h : 4*X ≤ 5*(25/N + 7/30)*eta) : X ≤ (1 + 25/N)*eta := by
  have hNpos : (0:ℚ) < N := by linarith
  have hy : (25:ℚ)/N ≤ 25/10 :=
    div_le_div_of_nonneg_left (by norm_num) (by norm_num) hN
  have key : 5*(25/N + 7/30) ≤ 4*(1 + 25/N) := by linarith
  have key2 : 5*(25/N + 7/30)*eta ≤ 4*((1 + 25/N)*eta) := by
    have := mul_le_mul_of_nonneg_right key heta
    linarith
  linarith

/-- max(a, b) = b + max(a − b, 0). -/
theorem max_shift (a b : ℚ) : max a b = b + max (a - b) 0 := by
  rcases le_total a b with h | h
  · rw [max_eq_right h, max_eq_right (by linarith : a - b ≤ 0)]
    ring
  · rw [max_eq_left h, max_eq_left (by linarith : (0:ℚ) ≤ a - b)]
    ring

/-- net-DW′ assembly: with uniform width (5τ = N − 25η/N) and the C5-RS bound
    Σ(sᵢ−τ)₊ ≤ (1 + 25/N)η, the width-clamped row sum satisfies GERSH. -/
theorem netDW_assembly (N eta tau : ℚ) (s : Fin 5 → ℚ)
    (htau : 5*tau = N - 25*eta/N)
    (hrs : (∑ i, max (s i - tau) 0) ≤ (1 + 25/N)*eta) :
    (∑ i, max (s i) tau) ≤ N + eta := by
  have hsum : (∑ i, max (s i) tau) =
      5*tau + ∑ i, max (s i - tau) 0 := by
    have h1 : (∑ i, max (s i) tau) =
        ∑ i, (tau + max (s i - tau) 0) := by
      exact Finset.sum_congr rfl (fun i _ => max_shift (s i) tau)
    rw [h1, Finset.sum_add_distrib]
    simp [Finset.card_univ]
  rw [hsum, htau]
  have hexp : (1 + 25/N)*eta = eta + 25*eta/N := by
    rw [add_mul, one_mul, div_mul_eq_mul_div]
  linarith [hrs]

end BranchA
end Erdos23Delta0
