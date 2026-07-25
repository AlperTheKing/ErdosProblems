/-
  Erdős Problem #30 — Balogh-Füredi-Roy Upper Bound (2021/2023)
  ==============================================================

  **Result:** h(N) ≤ √N + 0.998·N^{1/4} for sufficiently large N.
  This is the CURRENT BEST upper bound for Sidon sets (as of 2026).

  **Reference:** Balogh, J., Füredi, Z., Roy, S. (2023).
  "An upper bound on the size of Sidon sets."
  American Mathematical Monthly, 130(5), 437-445.
  arXiv: 2103.15850

  **Proof technique:** Combines Erdős-Turán counting (Section 2) with
  Lindström's residue class argument (Section 3), then plays them against
  each other via Cauchy-Schwarz (Section 4) to extract the 0.998 coefficient.

  **Key insight:** The Erdős-Turán and Lindström proofs have complementary
  slack terms. When one proof is tight, the other has slack, and vice versa.
  By combining them, the coefficient improves from 1 to 0.998.

  **Proof is entirely elementary:** No probability, no analysis — just
  double counting, Cauchy-Schwarz, and finite inequalities.
  The paper is ~4 pages of core argument (Sections 2-4).

  **Lean version**: leanprover/lean4:v4.24.0
  **Mathlib version**: f897ebcf72cd16f89ab4577d0c826cd14afaafc7
-/

import Mathlib
import Erdos30_Sidon_Defs
import Erdos30_Lindstrom

open Finset Nat

namespace Erdos.Sidon

/-! ## Section 2: Erdős-Turán Counting (Sum Distinctness)

  For Sidon A = {a₁ < a₂ < ... < a_k} ⊆ {1,...,n}:
  - All k(k+1)/2 sums a_i + a_j (i ≤ j) are distinct
  - They lie in {2,...,2n}
  - So: k(k+1)/2 ≤ 2n - 1

  This is the starting point (already proved in Sidon_SumCount_Fix.lean).
  The BFR paper then looks at WHERE these sums land more carefully.
-/

-- Lemma 2.1 (Erdős-Turán): number of distinct sums equals k(k+1)/2.
-- Already proved as sidon_sum_count in Sidon_SumCount_Fix.lean.

/-! ## Section 3: Set Systems Bound (Lindström-style)

  For each sum s = a_i + a_j, define the "depth" y_s = number of ways
  to express s as a sum of two elements of A (which is 1 for non-diagonal,
  since A is Sidon — but the paper works with a generalized framework).

  The key is to analyze the distribution of sums across intervals,
  using a parameter v (analogous to Lindström's t).

  Let d = k(k+1)/(2v) be the average number of sums per interval of length v.
  Then: ∑(d - y_i)² can be bounded from both sides.
-/

/-- The set of distinct pairwise sums a+b (a ≤ b) from A. -/
def distinctSums (A : Finset ℕ) : Finset ℕ :=
  ((A ×ˢ A).filter (fun p => p.1 ≤ p.2)).image (fun p => p.1 + p.2)

/-- For a Sidon set, |distinctSums| = k(k+1)/2. -/
theorem card_distinctSums_sidon (A : Finset ℕ) (hS : IsSidonSet A) :
    (distinctSums A).card = A.card * (A.card + 1) / 2 := by
  -- Step 1: The sum map is injective on ordered pairs (from Sidon property)
  have h_inj : Set.InjOn (fun p : ℕ × ℕ => p.1 + p.2)
      ↑((A ×ˢ A).filter (fun p => p.1 ≤ p.2)) := by
    intro ⟨a₁, b₁⟩ h₁ ⟨a₂, b₂⟩ h₂ heq
    simp only [Finset.mem_coe, Finset.mem_filter, Finset.mem_product] at h₁ h₂
    have := hS a₁ h₁.1.1 b₁ h₁.1.2 a₂ h₂.1.1 b₂ h₂.1.2 h₁.2 h₂.2 heq
    exact Prod.ext this.1 this.2
  -- Step 2: |image| = |source| (injectivity) = k(k+1)/2 (counting)
  unfold distinctSums
  rw [Finset.card_image_of_injOn h_inj]
  -- Counting: |{(a,b) ∈ A×A : a ≤ b}| = k(k+1)/2
  -- Decompose filter(≤) = filter(<) ∪ filter(=)
  have h_le_eq : (A ×ˢ A).filter (fun p : ℕ × ℕ => p.1 ≤ p.2) =
      ((A ×ˢ A).filter (fun p : ℕ × ℕ => p.1 < p.2)) ∪
      ((A ×ˢ A).filter (fun p : ℕ × ℕ => p.1 = p.2)) := by
    ext ⟨a, b⟩
    simp only [Finset.mem_filter, Finset.mem_product, Finset.mem_union]
    constructor
    · intro ⟨⟨ha, hb⟩, hab⟩
      rcases Nat.eq_or_lt_of_le hab with rfl | h
      · right; exact ⟨⟨ha, hb⟩, rfl⟩
      · left; exact ⟨⟨ha, hb⟩, h⟩
    · rintro (⟨⟨ha, hb⟩, h⟩ | ⟨⟨ha, hb⟩, rfl⟩)
      · exact ⟨⟨ha, hb⟩, le_of_lt h⟩
      · exact ⟨⟨ha, hb⟩, le_refl _⟩
  have h_le_disj : Disjoint
      ((A ×ˢ A).filter (fun p : ℕ × ℕ => p.1 < p.2))
      ((A ×ˢ A).filter (fun p : ℕ × ℕ => p.1 = p.2)) :=
    Finset.disjoint_filter.mpr (fun ⟨a, b⟩ _ h1 h2 => absurd h2 (Nat.ne_of_lt h1))
  rw [h_le_eq, Finset.card_union_of_disjoint h_le_disj]
  -- |filter(=)| = k (diagonal)
  have h_diag : ((A ×ˢ A).filter (fun p : ℕ × ℕ => p.1 = p.2)).card = A.card :=
    A.diag_card
  rw [h_diag]
  -- Now need: |filter(<)| + k = k*(k+1)/2
  -- Compute |filter(<)| via offDiag partition + swap bijection
  have h_filter_eq : (A ×ˢ A).filter (fun p : ℕ × ℕ => p.1 < p.2) =
      A.offDiag.filter (fun p : ℕ × ℕ => p.1 < p.2) := by
    ext ⟨a, b⟩
    simp only [Finset.mem_filter, Finset.mem_product, Finset.mem_offDiag]
    constructor
    · intro ⟨⟨ha, hb⟩, hab⟩; exact ⟨⟨ha, hb, Nat.ne_of_lt hab⟩, hab⟩
    · intro ⟨⟨ha, hb, _⟩, hab⟩; exact ⟨⟨ha, hb⟩, hab⟩
  rw [h_filter_eq]
  -- Partition offDiag into filter(<) ∪ filter(>)
  have h_union : A.offDiag =
      A.offDiag.filter (fun p : ℕ × ℕ => p.1 < p.2) ∪
      A.offDiag.filter (fun p : ℕ × ℕ => p.2 < p.1) := by
    ext ⟨a, b⟩
    simp only [Finset.mem_offDiag, Finset.mem_union, Finset.mem_filter]
    constructor
    · intro ⟨ha, hb, hab⟩
      rcases lt_or_gt_of_ne hab with h | h
      · left; exact ⟨⟨ha, hb, hab⟩, h⟩
      · right; exact ⟨⟨ha, hb, hab⟩, h⟩
    · rintro (⟨h, _⟩ | ⟨h, _⟩) <;> exact h
  have h_disj : Disjoint
      (A.offDiag.filter (fun p : ℕ × ℕ => p.1 < p.2))
      (A.offDiag.filter (fun p : ℕ × ℕ => p.2 < p.1)) :=
    Finset.disjoint_filter.mpr (fun ⟨a, b⟩ _ h1 h2 => absurd h1 (not_lt.mpr (le_of_lt h2)))
  -- Swap bijection: |filter(>)| = |filter(<)|
  have h_swap : (A.offDiag.filter (fun p : ℕ × ℕ => p.2 < p.1)).card =
      (A.offDiag.filter (fun p : ℕ × ℕ => p.1 < p.2)).card :=
    Finset.card_bij' (fun p _ => (p.2, p.1)) (fun p _ => (p.2, p.1))
      (fun ⟨a, b⟩ h => by
        simp only [Finset.mem_filter, Finset.mem_offDiag] at h ⊢
        exact ⟨⟨h.1.2.1, h.1.1, Ne.symm h.1.2.2⟩, h.2⟩)
      (fun ⟨a, b⟩ h => by
        simp only [Finset.mem_filter, Finset.mem_offDiag] at h ⊢
        exact ⟨⟨h.1.2.1, h.1.1, Ne.symm h.1.2.2⟩, h.2⟩)
      (fun _ _ => rfl) (fun _ _ => rfl)
  -- Combine: 2 * |filter(<)| = |offDiag| = k*(k-1)
  have h_card : A.offDiag.card =
      (A.offDiag.filter (fun p : ℕ × ℕ => p.1 < p.2)).card +
      (A.offDiag.filter (fun p : ℕ × ℕ => p.2 < p.1)).card := by
    rw [← Finset.card_union_of_disjoint h_disj, ← h_union]
  rw [h_swap] at h_card
  have h_mul_sub : A.card * (A.card - 1) = A.card * A.card - A.card := by
    cases A.card with
    | zero => simp
    | succ n =>
      simp only [Nat.succ_sub_one]
      rw [show (n + 1) * (n + 1) = (n + 1) * n + (n + 1) from by ring, Nat.add_sub_cancel]
  have h_offDiag_eq : A.offDiag.card = A.card * (A.card - 1) :=
    A.offDiag_card.trans h_mul_sub.symm
  have h_2c : 2 * (A.offDiag.filter (fun p : ℕ × ℕ => p.1 < p.2)).card =
      A.card * (A.card - 1) := by linarith
  -- Final algebra: k*(k-1)/2 + k = k*(k+1)/2
  have h_lt_card : (A.offDiag.filter (fun p : ℕ × ℕ => p.1 < p.2)).card =
      A.card * (A.card - 1) / 2 := by
    have : A.card * (A.card - 1) / 2 =
        (A.offDiag.filter (fun p : ℕ × ℕ => p.1 < p.2)).card := by
      rw [← h_2c]; exact Nat.mul_div_cancel_left _ (by omega)
    exact this.symm
  rw [h_lt_card]
  -- Goal: k*(k-1)/2 + k = k*(k+1)/2
  have h_kk1 : A.card * (A.card + 1) = A.card * (A.card - 1) + 2 * A.card := by
    cases A.card with
    | zero => simp
    | succ n => simp only [Nat.succ_sub_one]; ring
  rw [h_kk1, show 2 * A.card = A.card * 2 from by ring,
      Nat.add_mul_div_right _ _ (by omega : (0:ℕ) < 2)]

/-- If `A ⊆ {0, ..., N}`, then every ordered Sidon sum lies in `{0, ..., 2N}`. -/
theorem distinctSums_subset_range (A : Finset ℕ) (N : ℕ)
    (hA : A ⊆ Finset.range (N + 1)) :
    distinctSums A ⊆ Finset.range (2 * N + 1) := by
  intro s hs
  simp only [distinctSums, Finset.mem_image, Finset.mem_filter, Finset.mem_product] at hs
  obtain ⟨⟨a, b⟩, ⟨⟨ha, hb⟩, _⟩, rfl⟩ := hs
  have haN : a ≤ N := by
    have := Finset.mem_range.mp (hA ha)
    omega
  have hbN : b ≤ N := by
    have := Finset.mem_range.mp (hA hb)
    omega
  exact Finset.mem_range.mpr (by omega)

/-- The Erdős-Turán counting bound recovered from `distinctSums`. -/
theorem erdos_turan_counting_bound (A : Finset ℕ) (N : ℕ)
    (hS : IsSidonSet A) (hA : A ⊆ Finset.range (N + 1)) :
    A.card * (A.card + 1) / 2 ≤ 2 * N + 1 := by
  rw [← card_distinctSums_sidon A hS]
  simpa using Finset.card_le_card (distinctSums_subset_range A N hA)

/-! ## Section 3: Sidon translate families

  The Ruzsa/Johnson proof studies the shifted family `A, A+1, ..., A+(m-1)`.
  The key Sidon-specific input is that two distinct shifts intersect in at most
  one point.
-/

/-- Translate `A` by `i`. -/
def shifted (A : Finset ℕ) (i : ℕ) : Finset ℕ :=
  A.image (fun a => a + i)

/-- Translation preserves cardinality. -/
theorem card_shifted (A : Finset ℕ) (i : ℕ) :
    (shifted A i).card = A.card := by
  unfold shifted
  have h_inj : Function.Injective (fun a : ℕ => a + i) := by
    intro a b h
    exact Nat.add_right_cancel h
  exact Finset.card_image_of_injective A h_inj

/-- If `A ⊆ {0, ..., N}` and `i < m`, then `A + i ⊆ {0, ..., N + m}`. -/
theorem shifted_subset_range (A : Finset ℕ) (N i m : ℕ)
    (hA : A ⊆ Finset.range (N + 1)) (hi : i < m) :
    shifted A i ⊆ Finset.range (N + m + 1) := by
  intro x hx
  simp only [shifted, Finset.mem_image] at hx
  obtain ⟨a, ha, rfl⟩ := hx
  have haN : a ≤ N := by
    have := Finset.mem_range.mp (hA ha)
    omega
  exact Finset.mem_range.mpr (by omega)

/-- Distinct translates of a Sidon set intersect in at most one point. -/
theorem shifted_inter_card_le_one (A : Finset ℕ)
    (hS : IsSidonSet A) {i j : ℕ} (hij : i ≠ j) :
    ((shifted A i) ∩ (shifted A j)).card ≤ 1 := by
  refine Finset.card_le_one.mpr ?_
  intro x hx y hy
  simp only [Finset.mem_inter, shifted, Finset.mem_image] at hx hy
  obtain ⟨a, ha, hax⟩ := hx.1
  obtain ⟨b, hb, hbx⟩ := hx.2
  obtain ⟨c, hc, hcy⟩ := hy.1
  obtain ⟨d, hd, hdy⟩ := hy.2
  rcases lt_or_gt_of_ne hij with hij_lt | hij_gt
  · have hab_lt : b < a := by
      omega
    have hdc_lt : d < c := by
      omega
    have hdiff : a - b = c - d := by
      omega
    obtain ⟨hbd, hac⟩ :=
      sidon_distinct_differences A hS b hb a ha d hd c hc hab_lt hdc_lt hdiff
    omega
  · have hba_lt : a < b := by
      omega
    have hcd_lt : c < d := by
      omega
    have hdiff : b - a = d - c := by
      omega
    obtain ⟨hac, hbd⟩ :=
      sidon_distinct_differences A hS a ha b hb c hc d hd hba_lt hcd_lt hdiff
    omega

/-! ## Section 4: Cauchy-Schwarz Combination

  **Lemma 4.1 (Cauchy-Schwarz):**
  For real numbers y₁,...,y_v and a subset X ⊆ {1,...,v}:
    ∑_{i ∈ [v]} (d - y_i)² ≥ |X|·(d - d_X)² + ∑_{x ∈ X} y_x² - |X|·d_X²
  where d_X = (∑_{x ∈ X} y_x)/|X|.

  This is the KEY lemma that connects Sections 2 and 3.
  By choosing X appropriately (intervals where sums are dense vs. sparse),
  the slack from one section compensates the other.
-/

/-- Cauchy-Schwarz variance decomposition (BFR Lemma 4.1).
    This is a standard inequality but its application to Sidon sets is novel. -/
theorem bfr_cauchy_schwarz {v : ℕ} (y : Fin v → ℝ) (d : ℝ) (X : Finset (Fin v))
    (d_X : ℝ) (hd_X : d_X * X.card = ∑ x ∈ X, y x) :
    ∑ i, (d - y i) ^ 2 ≥
      X.card * (d - d_X) ^ 2 + ∑ x ∈ X, (y x) ^ 2 - X.card * d_X ^ 2 := by
  -- Step 1: ∑_all ≥ ∑_X (drop non-negative complement terms)
  have h_ge : ∑ x ∈ X, (d - y x) ^ 2 ≤ ∑ i, (d - y i) ^ 2 :=
    Finset.sum_le_sum_of_subset_of_nonneg (Finset.subset_univ X)
      (fun _ _ _ => sq_nonneg _)
  -- Step 2: ∑_X (d-y)² = RHS (algebraic identity using hd_X)
  suffices h_eq : ∑ x ∈ X, (d - y x) ^ 2 =
      ↑X.card * (d - d_X) ^ 2 + ∑ x ∈ X, (y x) ^ 2 - ↑X.card * d_X ^ 2 by linarith
  -- Both sides equal |X|·d² - 2·d·∑_X(y) + ∑_X(y²)
  -- LHS expansion
  have h_congr : ∀ x ∈ X, (d - y x) ^ 2 = d ^ 2 - 2 * d * y x + (y x) ^ 2 :=
    fun x _ => by ring
  rw [Finset.sum_congr rfl h_congr, Finset.sum_add_distrib, Finset.sum_sub_distrib,
      Finset.sum_const, nsmul_eq_mul, ← Finset.mul_sum]
  -- RHS expansion using hd_X
  have h_rhs : ↑X.card * (d - d_X) ^ 2 + ∑ x ∈ X, (y x) ^ 2 - ↑X.card * d_X ^ 2 =
      ↑X.card * d ^ 2 - 2 * d * (d_X * ↑X.card) + ∑ x ∈ X, (y x) ^ 2 := by ring
  rw [h_rhs, hd_X]

/-! ## Main Theorem: The 0.998 Coefficient

  The BFR proof (Sections 2-4) proceeds by contradiction:
  Assume k > √n + 0.998·n^{1/4}. Then:

  **Section 2 (Erdős-Turán with slack):** The k(k+1)/2 distinct sums distribute
  across intervals. Inequality (2.4) bounds the "discrepancy" ∑(rₓ² - d₂|X|)
  with a slack term C measuring large deviations K(A).

  **Section 3 (Set systems bound, Theorem 3.1):** For parameter m > 0 and the
  representation function over the sumset range [2N]:
    k²·m ≤ (2N+m-1)·(m+k-1)
  This provides a complementary constraint to Section 2.

  **Section 4 (Cauchy-Schwarz combination, Claims 4.1-4.3):** Case analysis on
  the defect, K(A), and slack C. The slack terms from Sections 2 and 3 are
  complementary — when one is tight, the other has slack. The combination via
  Cauchy-Schwarz yields coefficient 63/64 ≈ 0.984 < 0.998.

  The 0.998 statement has slack over the paper's 63/64 result, which absorbs
  Nat.sqrt rounding losses at N ≥ 10^12.
-/

/-- **BFR Core Bound (Theorem 1.1, combined form).**
    For Sidon A ⊆ {0,...,N} with N ≥ 10^12:
      1000·(|A|-1) ≤ 1000·⌊√N⌋ + 998·⌊⁴√N⌋

    This is the numerical heart of the BFR theorem. Closing this axiom requires
    the full 4-page combination argument (Sections 2-4 of BFR 2023):

    **Proved scaffolding (available in this file + Erdos30_Lindstrom.lean):**
    - `card_distinctSums_sidon` — Section 2: |distinctSums| = k(k+1)/2
    - `lindstrom_parametric` — Section 3 (residue class form): k² ≤ 2Nt + kt
    - `bfr_cauchy_schwarz` — Section 4 lemma: variance decomposition

    **Still needed to close this axiom (~10-15 lemmas):**
    1. Interval decomposition: partition {2,...,2N} into intervals of length v
    2. Per-interval sum counts y_i and representation numbers r_x
    3. Discrepancy bound (2.4) with slack term C
    4. Set systems bound: k²m ≤ (2N+m-1)(m+k-1)
    5. Claims 4.1-4.3: case analysis on defect/K(A)/slack
    6. Optimization of parameters v and m
    7. Numerical resolution: 63/64 < 0.998 with Nat.sqrt rounding at N ≥ 10^12

    **Note:** BFR proves the stronger coefficient 63/64 ≈ 0.984. The 0.998
    statement has slack that absorbs Nat.sqrt rounding losses (≤ 2 units)
    at N ≥ 10^12 where ⁴√N ≥ 1000.

    **Reference:** Balogh-Füredi-Roy (2023), Theorem 1.1.
    arXiv: 2103.15850, Amer. Math. Monthly 130(5), 437-445. -/
axiom bfr_core_bound (A : Finset ℕ) (N : ℕ) (hS : IsSidonSet A)
    (hA : A ⊆ Finset.range (N + 1)) (hN : N ≥ 10^12) :
    1000 * (A.card - 1) ≤ 1000 * Nat.sqrt N + 998 * Nat.sqrt (Nat.sqrt N)

/-- **Balogh-Füredi-Roy Theorem (2023).**
  For a Sidon set A ⊆ {0,...,N} with N ≥ 10^12:
    |A| ≤ √N + 0.998·⁴√N + 1

  Stated in integer form: 1000·|A| ≤ 1000·⌊√N⌋ + 998·⌊⁴√N⌋ + 1000.
  Proved from `bfr_core_bound` via ℕ arithmetic. -/
theorem bfr_bound (A : Finset ℕ) (N : ℕ) (hS : IsSidonSet A)
    (hA : A ⊆ Finset.range (N + 1)) (hN : N ≥ 10^12) :
    1000 * A.card ≤ 1000 * Nat.sqrt N + 998 * Nat.sqrt (Nat.sqrt N) + 1000 := by
  have h := bfr_core_bound A N hS hA hN
  omega

/-! ## Proof Architecture

  ```
  card_distinctSums_sidon ───────────┐
  (Section 2: Erdős-Turán counting)  │
                                     │
  lindstrom_parametric ──────────────┤
  (Section 3: residue class bound)   │
                                     ├──→ bfr_core_bound (AXIOM) ──→ bfr_bound ✓
  bfr_cauchy_schwarz ────────────────┤    (Sections 2-4 combination)
  (Lemma 4.1: variance decomp.)     │
                                     │
  [interval analysis — NOT YET] ─────┘
  [set systems bound — NOT YET]
  [Claims 4.1-4.3 — NOT YET]
  ```

  **Current status:**
  - 3 theorems PROVED (card_distinctSums_sidon, bfr_cauchy_schwarz, bfr_bound)
  - 1 axiom (bfr_core_bound — requires full BFR Sections 2-4 combination)
  - lindstrom_parametric proved in Erdos30_Lindstrom.lean

  **Formalization feasibility:** HIGH.
  - Paper is 4 pages of elementary combinatorics
  - No probability, no analysis beyond Cauchy-Schwarz
  - All lemmas are finite sums / counting arguments
  - Main difficulty: bookkeeping of interval decomposition indices
  - Estimated effort: 10-15 new lemmas (each tractable)

  **This would be the FIRST formal verification of the current best Sidon bound.**
  Publishable in a formalization venue (ITP, CPP).
-/

end Erdos.Sidon
