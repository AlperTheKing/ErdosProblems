/-
Erdős #23 δ=0 — Bank0 algebra (reconciled plan L7 + L8, the PROVEN pieces).
L7 finish: five cyclic class-product dominations m ≤ nᵢ·nᵢ₊₁ give 25m ≤ (Σnᵢ)².
Proof route avoiding quintic AM-GM: per pair, √m ≤ √(nᵢnᵢ₊₁) ≤ (nᵢ+nᵢ₊₁)/2
(two-variable AM-GM); summing the five gives 5√m ≤ Σnᵢ; squaring finishes.
L8 block summing: Σ aₖ² ≤ (Σ aₖ)² for nonnegative lists (disjoint bank blocks).
The graph-side inputs (template cuts m ≤ eᵢ, hom-structure eᵢ ≤ nᵢnᵢ₊₁) enter as
hypotheses; this module is the pure arithmetic spine.
-/

import Mathlib

namespace Erdos23Delta0
namespace Bank0Algebra

/-- Two-variable step: m ≤ a·b with everything nonnegative gives √m ≤ (a+b)/2. -/
theorem sqrt_le_half_add (m a b : ℝ) (_hm : 0 ≤ m) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (h : m ≤ a * b) : Real.sqrt m ≤ (a + b) / 2 := by
  have hsq : m ≤ ((a + b) / 2) ^ 2 := by nlinarith [sq_nonneg (a - b)]
  have h1 : Real.sqrt m ≤ Real.sqrt (((a + b) / 2) ^ 2) := Real.sqrt_le_sqrt hsq
  have h2 : Real.sqrt (((a + b) / 2) ^ 2) = (a + b) / 2 := by
    rw [Real.sqrt_sq (by linarith)]
  linarith [h1, h2.le, h2.ge]

/-- THE BANK-BLOCK AM-GM (L7 finish / L8 per-block): five cyclic products
    dominating m give 25·m ≤ (n₀+n₁+n₂+n₃+n₄)². -/
theorem bank_amgm (m n0 n1 n2 n3 n4 : ℝ)
    (hm : 0 ≤ m) (h0 : 0 ≤ n0) (h1 : 0 ≤ n1) (h2 : 0 ≤ n2) (h3 : 0 ≤ n3)
    (h4 : 0 ≤ n4)
    (p0 : m ≤ n0 * n1) (p1 : m ≤ n1 * n2) (p2 : m ≤ n2 * n3)
    (p3 : m ≤ n3 * n4) (p4 : m ≤ n4 * n0) :
    25 * m ≤ (n0 + n1 + n2 + n3 + n4) ^ 2 := by
  have s0 := sqrt_le_half_add m n0 n1 hm h0 h1 p0
  have s1 := sqrt_le_half_add m n1 n2 hm h1 h2 p1
  have s2 := sqrt_le_half_add m n2 n3 hm h2 h3 p2
  have s3 := sqrt_le_half_add m n3 n4 hm h3 h4 p3
  have s4 := sqrt_le_half_add m n4 n0 hm h4 h0 p4
  have hsum : 5 * Real.sqrt m ≤ n0 + n1 + n2 + n3 + n4 := by linarith
  have hs : 0 ≤ Real.sqrt m := Real.sqrt_nonneg m
  have hsq : (5 * Real.sqrt m) ^ 2 ≤ (n0 + n1 + n2 + n3 + n4) ^ 2 := by
    have hns : 0 ≤ 5 * Real.sqrt m := by linarith
    nlinarith [hsum, hns]
  have hval : (5 * Real.sqrt m) ^ 2 = 25 * m := by
    have := Real.sq_sqrt hm
    nlinarith [this]
  linarith [hsq, hval.le, hval.ge]

/-- ℚ-level corollary (the consumers carry ℚ/ℤ counts). -/
theorem bank_amgm_rat (m n0 n1 n2 n3 n4 : ℚ)
    (hm : 0 ≤ m) (h0 : 0 ≤ n0) (h1 : 0 ≤ n1) (h2 : 0 ≤ n2) (h3 : 0 ≤ n3)
    (h4 : 0 ≤ n4)
    (p0 : m ≤ n0 * n1) (p1 : m ≤ n1 * n2) (p2 : m ≤ n2 * n3)
    (p3 : m ≤ n3 * n4) (p4 : m ≤ n4 * n0) :
    25 * m ≤ (n0 + n1 + n2 + n3 + n4) ^ 2 := by
  have hr := bank_amgm (m : ℝ) n0 n1 n2 n3 n4
    (by exact_mod_cast hm) (by exact_mod_cast h0) (by exact_mod_cast h1)
    (by exact_mod_cast h2) (by exact_mod_cast h3) (by exact_mod_cast h4)
    (by exact_mod_cast p0) (by exact_mod_cast p1) (by exact_mod_cast p2)
    (by exact_mod_cast p3) (by exact_mod_cast p4)
  exact_mod_cast hr

/-- Template chaining: max-cut template inequality m ≤ eᵢ and hom-structure
    bound eᵢ ≤ nᵢ·nᵢ₊₁ give the product domination (the L7 interface). -/
theorem template_chain (m e n n' : ℚ) (h1 : m ≤ e) (h2 : e ≤ n * n') :
    m ≤ n * n' := le_trans h1 h2

/-- L8 block summing: for nonnegative block sizes, Σ aₖ² ≤ (Σ aₖ)². -/
theorem sum_sq_le_sq_sum : ∀ l : List ℚ, (∀ x ∈ l, 0 ≤ x) →
    (l.map (· ^ 2)).sum ≤ l.sum ^ 2
  | [], _ => by simp
  | a :: l, h => by
      have ha := h a (List.mem_cons_self ..)
      have hl : ∀ x ∈ l, 0 ≤ x := fun x hx => h x (List.mem_cons_of_mem _ hx)
      have ih := sum_sq_le_sq_sum l hl
      have hls : 0 ≤ l.sum := List.sum_nonneg hl
      simp only [List.map_cons, List.sum_cons]
      nlinarith [ih, ha, hls]

/-- Per-block banks sum: blocks (mₖ, sₖ) with 25·mₖ ≤ sₖ² give
    25·Σmₖ ≤ Σsₖ². -/
theorem sum_bank_le : ∀ blocks : List (ℚ × ℚ),
    (∀ p ∈ blocks, 25 * p.1 ≤ p.2 ^ 2) →
    25 * (blocks.map Prod.fst).sum ≤ (blocks.map (fun p => p.2 ^ 2)).sum
  | [], _ => by simp
  | p :: ps, h => by
      have hp := h p (List.mem_cons_self ..)
      have ih := sum_bank_le ps (fun q hq => h q (List.mem_cons_of_mem _ hq))
      simp only [List.map_cons, List.sum_cons]
      linarith

/-- L8 assembly: per-block banks 25·mₖ ≤ sₖ² plus disjointness (Σsₖ ≤ N)
    give the global bank 25·Σmₖ ≤ N². -/
theorem blocks_to_global (blocks : List (ℚ × ℚ)) (N : ℚ)
    (hs : ∀ p ∈ blocks, 0 ≤ p.2)
    (hper : ∀ p ∈ blocks, 25 * p.1 ≤ p.2 ^ 2)
    (hN : (blocks.map Prod.snd).sum ≤ N) (hN0 : 0 ≤ N) :
    25 * (blocks.map Prod.fst).sum ≤ N ^ 2 := by
  have h1 := sum_bank_le blocks hper
  have h2 : (blocks.map (fun p => p.2 ^ 2)).sum ≤ (blocks.map Prod.snd).sum ^ 2 := by
    have := sum_sq_le_sq_sum (blocks.map Prod.snd)
      (fun x hx => by
        obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hx
        exact hs p hp)
    rw [List.map_map] at this
    exact this
  have h3 : (blocks.map Prod.snd).sum ^ 2 ≤ N ^ 2 := by
    have hss : 0 ≤ (blocks.map Prod.snd).sum :=
      List.sum_nonneg (fun x hx => by
        obtain ⟨p, hp, rfl⟩ := List.mem_map.mp hx
        exact hs p hp)
    nlinarith
  linarith

end Bank0Algebra
end Erdos23Delta0
