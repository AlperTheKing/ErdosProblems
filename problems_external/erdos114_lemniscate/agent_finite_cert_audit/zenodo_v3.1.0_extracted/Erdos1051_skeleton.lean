-- Erdős Problem #1051 — Lean 4 Skeleton
-- Kenneth A. Mendoza, MendozaLab, April 2026
-- Shadow Numberverse Approach
--
-- STATUS: Skeleton / sorry-bearing. Full formalization pending.
-- Reference: arXiv:2601.21442 (Barreto-Kang-Kim-Kovač-Zhang 2026)
--            Kevin Barreto's Lean 4 formalization of Aletheia's proof.
--
-- PROBLEM:
--   Let a : ℕ → ℕ be strictly increasing with liminf_{n→∞} a(n)^{1/2^n} > 1.
--   Then ∑ 1/(a(n) * a(n+1)) is irrational.

import Mathlib.Topology.Algebra.Order.LiminfLimsup
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Data.Real.Irrational
import Mathlib.NumberTheory.Bernoulli

/-!
## Mahler's Irrationality Criterion

The key lemma: if S = ∑ zₙ is a series of positive rationals,
and Dₙ is a common denominator of z₁,...,zₙ, and Dₙ * rₙ → 0
along some subsequence, then S is irrational.
-/

-- The Mahler criterion (sorry-bearing stub)
lemma mahler_irrationality_criterion
    (z : ℕ → ℚ)
    (hz_pos : ∀ n, 0 < z n)
    (S : ℝ)
    (hS : HasSum (fun n => (z n : ℝ)) S)
    (D : ℕ → ℕ)
    (hD_clears : ∀ N n, n ≤ N → (D N : ℚ) * z n ∈ Set.range (Nat.cast : ℕ → ℚ))
    (hDr_to_zero : Filter.Tendsto
        (fun N => (D N : ℝ) * ∑' n, if N < n then (z n : ℝ) else 0)
        Filter.atTop (nhds 0)) :
    Irrational S := by
  sorry

/-!
## Main Theorem: Erdős #1051

Statement: if a : ℕ → ℕ is strictly increasing and
  liminf_{n→∞} a(n)^(1/2^n) > 1,
then ∑_{n=1}^∞ 1/(a(n) * a(n+1)) is irrational.
-/

-- Growth condition: liminf a(n)^{1/2^n} > 1
def HasDoubleExpGrowth (a : ℕ → ℕ) : Prop :=
  ∃ ρ : ℝ, ρ > 1 ∧ ∃ N₀ : ℕ, ∀ n ≥ N₀, ρ ^ (2 ^ n : ℝ) ≤ (a n : ℝ)

-- The series ∑ 1/(a(n) * a(n+1))
noncomputable def erdos1051_series (a : ℕ → ℕ) : ℝ :=
  ∑' n, 1 / ((a n : ℝ) * (a (n + 1) : ℝ))

-- MAIN THEOREM (sorry-bearing skeleton)
theorem erdos1051
    (a : ℕ → ℕ)
    (ha_strict_mono : StrictMono a)
    (ha_growth : HasDoubleExpGrowth a) :
    Irrational (erdos1051_series a) := by
  -- Step 1: Extract ρ > 1 and N₀ from growth hypothesis
  obtain ⟨ρ, hρ, N₀, haN₀⟩ := ha_growth
  -- Step 2: The series converges (double-exponential denominators)
  have hconv : Summable (fun n => 1 / ((a n : ℝ) * (a (n + 1) : ℝ))) := by
    sorry
  -- Step 3: Apply Mahler's criterion with D_N = ∏_{k=1}^{N+1} a_k
  apply mahler_irrationality_criterion
  · -- zₙ > 0
    intro n
    simp [erdos1051_series]
    sorry
  · -- series sums to erdos1051_series a
    exact hconv.hasSum
  · -- D_N clears denominators z_1,...,z_N
    sorry
  · -- D_N * r_N → 0 along peak subsequence
    -- Key: at "peak" indices Q where a_{Q+1} > (a_Q)^φ (roughly),
    -- the ratio (∏_{k≤Q+1} a_k) / (a_{Q+1} * a_{Q+2}) → 0
    -- This uses the identity φ² = φ + 1 (golden ratio characteristic equation)
    sorry

/-!
## Notes on the proof structure

The full proof (see Barreto's Lean 4 formalization, and [BKK+26]) proceeds:

1. PEAK LEMMA: Since limsup a_n^{1/φ^n} = ∞ (which follows from
   liminf a_n^{1/2^n} > 1, as 2/φ > 1), there exist infinitely many
   "local peak" indices Q where:
     a_{Q+1} ≥ (max_{k≤Q} a_k)^{1+δ}   for some δ > 0.

2. TAIL BOUND at peak Q:
     r_Q ≤ C / (a_{Q+1} * a_{Q+2}) ≤ C / a_{Q+1}^{1+φ-ε}
   (since a_{Q+2} ≥ a_{Q+1}^{φ-ε} at peak indices by the golden ratio eq.)

3. PREFACTOR BOUND:
     D_Q = ∏_{k=1}^{Q+1} a_k ≤ a_{Q+1}^{Q+1} / (something)
   but at peak indices, a_{Q+1} dominates all previous terms, so:
     D_Q ≤ a_{Q+1}^{1+1/(Q^2+1)}   (roughly)

4. PRODUCT D_Q * r_Q ≤ a_{Q+1}^{1+1/(Q^2+1)} * C/a_{Q+1}^{1+φ-ε}
                     = C * a_{Q+1}^{-φ+ε+1/(Q^2+1)} → 0
   since φ > 1 and ε, 1/(Q^2+1) can be made < φ-1.

The exact version uses the polynomial identity for φ: φ^2 = φ + 1,
which encodes the precise balance between D_N and r_N.
-/
