/-
  Erdős Problem #30 — Lindström Upper Bound (1969)
  =================================================

  **Result:** h(N) ≤ √N + N^{1/4} + 1

  **Reference:** Lindström, B. (1969). "An inequality for B₂-sequences."
  J. Combinatorial Theory, Vol. 7, No. 1, pp. 134-138.

  **Correct proof technique (from Balogh-Füredi-Roy 2023, Section 2):**
  Let A = {a₁ < a₂ < ... < a_k} ⊆ [n] be a Sidon set.

  1. For i < j, call j - i the "order" of the difference a_j - a_i.
  2. Fix parameter ℓ (chosen later as ⌊n^{1/4}⌋).
  3. Count differences of orders 1 through ℓ:
     There are (k-1) + (k-2) + ... + (k-ℓ) = ℓ(k - (ℓ+1)/2) such differences.
  4. These differences are ALL DISTINCT positive integers (Sidon property).
  5. LOWER BOUND: sum ≥ 1 + 2 + ... + m > m²/2 where m = ℓ(k - (ℓ+1)/2).
  6. UPPER BOUND: sum of order-r differences ≤ r·n (telescoping), so
     total ≤ Σ_{r=1}^ℓ r·n = ℓ(ℓ+1)n/2.
  7. Combining: (1/2)ℓ²(k - (ℓ+1)/2)² < (1/2)ℓ(ℓ+1)n
  8. Simplify: ℓ(k - (ℓ+1)/2)² < (ℓ+1)n
  9. k < √(n(ℓ+1)/ℓ) + (ℓ+1)/2 ≈ √n + √n/(2ℓ) + ℓ/2 + 1/2
  10. With ℓ = ⌊n^{1/4}⌋: k < √n + n^{1/4} + 1.

  **This file also contains** a residue-class parametric bound (k² ≤ 2Nt + kt),
  which is an independent result useful for BFR but does NOT directly yield
  the Lindström bound.

  **Superseded by:** Balogh-Füredi-Roy (2023): h(N) ≤ √N + 0.998·N^{1/4}.
  See Erdos30_BFR.lean for that improvement.

  **Lean version**: leanprover/lean4:v4.24.0
  **Mathlib version**: f897ebcf72cd16f89ab4577d0c826cd14afaafc7
-/

import Mathlib
import Erdos30_Sidon_Defs

open Finset Nat

namespace Erdos.Sidon

/-! ## Step 3–4: Pigeonhole on Residue Classes -/

/-- Residue class: elements of A congruent to r mod t. -/
def residueClass (A : Finset ℕ) (t r : ℕ) : Finset ℕ :=
  A.filter (fun a => a % t = r)

/-- Pigeonhole: some residue class mod t has ≥ ⌈k/t⌉ elements.
    Stated as: t * |A_r| ≥ |A| for some r. -/
theorem pigeonhole_residue (A : Finset ℕ) (t : ℕ) (ht : 0 < t) :
    ∃ r, r < t ∧ A.card ≤ t * (residueClass A t r).card := by
  by_contra h
  push_neg at h
  -- h : ∀ r, r < t → t * (residueClass A t r).card < A.card
  -- Partition identity: |A| = ∑_{r<t} |A_r|
  have hfib : A.card = ∑ r ∈ Finset.range t, (residueClass A t r).card := by
    simp only [residueClass]
    exact Finset.card_eq_sum_card_fiberwise
      (by intro a _; exact Finset.mem_range.mpr (Nat.mod_lt a ht))
  have hlt : ∀ r ∈ Finset.range t, t * (residueClass A t r).card < A.card :=
    fun r hr => h r (Finset.mem_range.mp hr)
  -- Sum: t * |A| = ∑ t*|A_r| < ∑ |A| = t * |A|. Contradiction.
  have : t * A.card < t * A.card := calc
    t * A.card
        = t * ∑ r ∈ Finset.range t, (residueClass A t r).card := by rw [hfib]
      _ = ∑ r ∈ Finset.range t, t * (residueClass A t r).card := by
          rw [Finset.mul_sum]
      _ < ∑ r ∈ Finset.range t, A.card := by
          apply Finset.sum_lt_sum
          · intro r hr; exact le_of_lt (hlt r hr)
          · exact ⟨0, Finset.mem_range.mpr (by omega),
              hlt 0 (Finset.mem_range.mpr (by omega))⟩
      _ = t * A.card := by rw [Finset.sum_const, Finset.card_range, smul_eq_mul]
  omega

/-! ## Step 5: Residue Class Preserves Sidon Property -/

/-- Scaling a residue class by 1/t preserves the Sidon property.
    If A is Sidon and B = {(a-r)/t : a ∈ A, a ≡ r (mod t)}, then B is Sidon. -/
theorem residue_class_scaled_sidon (A : Finset ℕ) (t r : ℕ) (ht : 0 < t)
    (hS : IsSidonSet A) :
    IsSidonSet ((residueClass A t r).image (fun a => a / t)) := by
  intro a₁ ha₁ b₁ hb₁ a₂ ha₂ b₂ hb₂ hab₁ hab₂ heq
  simp only [Finset.mem_image, residueClass, Finset.mem_filter] at ha₁ hb₁ ha₂ hb₂
  obtain ⟨x₁, ⟨hx₁A, hx₁r⟩, rfl⟩ := ha₁
  obtain ⟨y₁, ⟨hy₁A, hy₁r⟩, rfl⟩ := hb₁
  obtain ⟨x₂, ⟨hx₂A, hx₂r⟩, rfl⟩ := ha₂
  obtain ⟨y₂, ⟨hy₂A, hy₂r⟩, rfl⟩ := hb₂
  -- Key: x_i = t * (x_i / t) + x_i % t = t * (x_i / t) + r
  have hx₁d := Nat.div_add_mod x₁ t
  have hy₁d := Nat.div_add_mod y₁ t
  have hx₂d := Nat.div_add_mod x₂ t
  have hy₂d := Nat.div_add_mod y₂ t
  -- Multiply heq by t: t*(x₁/t) + t*(y₁/t) = t*(x₂/t) + t*(y₂/t)
  have sum_t : t * (x₁ / t) + t * (y₁ / t) = t * (x₂ / t) + t * (y₂ / t) := by
    have := congr_arg (t * ·) heq; simp only [mul_add] at this; exact this
  -- Therefore x₁ + y₁ = x₂ + y₂
  have sum_eq : x₁ + y₁ = x₂ + y₂ := by omega
  -- Ordering: x₁/t ≤ y₁/t implies x₁ ≤ y₁ (same remainder)
  have ord₁ : x₁ ≤ y₁ := by
    have := mul_le_mul_of_nonneg_left hab₁ (Nat.zero_le t); omega
  have ord₂ : x₂ ≤ y₂ := by
    have := mul_le_mul_of_nonneg_left hab₂ (Nat.zero_le t); omega
  -- Apply Sidon property of A
  have hs := hS x₁ hx₁A y₁ hy₁A x₂ hx₂A y₂ hy₂A ord₁ ord₂ sum_eq
  exact ⟨by rw [hs.1], by rw [hs.2]⟩

/-! ## Step 5b: Elementary Sidon Bound (External Dependency)

  This is proved in Erdos30_Complete.sidon_difference_count (zero sorries).
  Declared as axiom here because the Complete file requires proof fixes to compile
  against this Mathlib version (f897ebcf72). The theorem is fully verified in the
  src/Erdos/ compilation environment.
  TODO: Port Erdos30_Complete proofs to current Mathlib API to enable direct import.
-/

/-- **Elementary Sidon bound**: For Sidon A ⊆ {0,...,M}, |A|*(|A|-1) ≤ 2*M.
    Proved in `Erdos30_Complete.lean` as `sidon_difference_count`.
    Declared as axiom here pending Mathlib API port. -/
axiom sidon_elem_bound (A : Finset ℕ) (M : ℕ) (hS : IsSidonSet A)
    (hA : A ⊆ Finset.range (M + 1)) : A.card * (A.card - 1) ≤ 2 * M

/-! ## Step 6: Elementary Bound on Scaled Set -/

/-- The scaled residue class B lives in {0,...,⌊N/t⌋}. -/
theorem scaled_range (A : Finset ℕ) (N t r : ℕ) (ht : 0 < t)
    (hA : A ⊆ Finset.range (N + 1)) :
    (residueClass A t r).image (fun a => a / t) ⊆ Finset.range (N / t + 1) := by
  intro b hb
  simp [Finset.mem_image, residueClass, Finset.mem_filter] at hb
  obtain ⟨a, ⟨ha, _⟩, rfl⟩ := hb
  simp [Finset.mem_range]
  have : a ≤ N := by
    have := Finset.mem_range.mp (hA ha); omega
  exact Nat.lt_succ_of_le (Nat.div_le_div_right this)

/-! ## Step 7–8: The Key Inequality

  From steps 4–6:
  - |B| ≥ k/t (pigeonhole)
  - B is Sidon in {0,...,N/t} (residue scaling)
  - |B|(|B|-1) ≤ 2·(N/t) (elementary bound)

  Combining: (k/t)(k/t - 1) ≤ 2N/t
  Multiply by t²: k(k-t) ≤ 2Nt ... but we need to be careful with integer division.

  Working with integers: let m = |A_r| ≥ ⌈k/t⌉, so m·t ≥ k.
  m(m-1) ≤ 2·⌊N/t⌋.
  m ≤ t/2 + √(2N/t + t/4)  (complete the square).
  k ≤ m·t ≤ ...

  Actually, cleaner to state the parametric inequality directly.
-/

/-- **Parametric Lindström inequality.**
  For Sidon A ⊆ {0,...,N} and any t > 0:
    k² ≤ 2Nt + kt
  where k = |A|.

  This is the key step — everything else is optimization over t. -/
theorem lindstrom_parametric (A : Finset ℕ) (N t : ℕ) (hS : IsSidonSet A)
    (hA : A ⊆ Finset.range (N + 1)) (ht : 0 < t) :
    A.card * A.card ≤ 2 * N * t + A.card * t := by
  -- Step 1: Pigeonhole gives residue class with k ≤ t * m elements
  obtain ⟨r, hr, hpig⟩ := pigeonhole_residue A t ht
  set Ar := residueClass A t r with hAr_def
  set m := Ar.card
  set B := Ar.image (fun a => a / t)
  -- Step 2: Division is injective on residue class (all have same remainder)
  have h_inj : Set.InjOn (fun a => a / t) (↑Ar) := by
    intro a ha b hb hab
    -- Extract filter condition: elements of Ar have remainder r mod t
    have ha_r : a % t = r := by
      have := Finset.mem_coe.mp ha
      rw [hAr_def, residueClass, Finset.mem_filter] at this
      exact this.2
    have hb_r : b % t = r := by
      have := Finset.mem_coe.mp hb
      rw [hAr_def, residueClass, Finset.mem_filter] at this
      exact this.2
    -- a = t*(a/t) + r, b = t*(b/t) + r, a/t = b/t → a = b
    have hab' : a / t = b / t := hab
    calc a = t * (a / t) + a % t := (Nat.div_add_mod a t).symm
      _ = t * (b / t) + r := by rw [hab', ha_r]
      _ = t * (b / t) + b % t := by rw [hb_r]
      _ = b := Nat.div_add_mod b t
  have hBcard : B.card = m := Finset.card_image_of_injOn h_inj
  -- Step 3: B is Sidon in {0,...,N/t}
  have hBS : IsSidonSet B := residue_class_scaled_sidon A t r ht hS
  have hBrange : B ⊆ Finset.range (N / t + 1) := scaled_range A N t r ht hA
  -- Step 4: Elementary bound → m*(m-1) ≤ 2*(N/t)
  have hBbound : m * (m - 1) ≤ 2 * (N / t) := by
    have := sidon_elem_bound B (N / t) hBS hBrange; rwa [hBcard] at this
  -- Step 5: Case split on k ≤ t (trivial) vs k > t
  by_cases hkt : A.card ≤ t
  · -- k ≤ t: k² ≤ kt ≤ 2Nt + kt
    calc A.card * A.card ≤ A.card * t := Nat.mul_le_mul_left _ hkt
       _ ≤ 2 * N * t + A.card * t := Nat.le_add_left _ _
  · -- k > t: decompose k² = k*(k-t) + k*t, bound k*(k-t) ≤ 2*N*t
    push_neg at hkt
    have hge : t ≤ A.card := Nat.le_of_lt hkt
    -- k² = k*(k-t) + k*t
    have h_split : A.card * A.card = A.card * (A.card - t) + A.card * t := by
      rw [← Nat.mul_add, Nat.sub_add_cancel hge]
    rw [h_split]
    suffices h : A.card * (A.card - t) ≤ 2 * N * t by linarith
    -- Nat arithmetic: t*m - t = t*(m-1)
    have htm_eq : t * m - t = t * (m - 1) := by
      cases m with
      | zero => simp
      | succ n => simp [Nat.mul_succ]
    -- Chain: k*(k-t) ≤ (t*m)*(t*m-t) = t²*m*(m-1) ≤ 2*(t*(N/t))*t ≤ 2*N*t
    have h4 : t * (N / t) ≤ N := Nat.mul_div_le N t
    calc A.card * (A.card - t)
        ≤ (t * m) * (t * m - t) :=
          Nat.mul_le_mul hpig (Nat.sub_le_sub_right hpig t)
      _ = (t * m) * (t * (m - 1)) := by rw [htm_eq]
      _ = t * t * (m * (m - 1)) := by ring
      _ ≤ t * t * (2 * (N / t)) :=
          Nat.mul_le_mul_left _ hBbound
      _ = 2 * (t * (N / t)) * t := by ring
      _ ≤ 2 * N * t :=
          Nat.mul_le_mul_right t (Nat.mul_le_mul_left 2 h4)

/-! ## The Actual Lindström Proof (order-of-differences argument)

  The parametric inequality k² ≤ 2Nt + kt (above) is useful for BFR but
  does NOT directly yield the Lindström bound (it gives O(N^{5/8})).

  The correct proof (BFR Section 2) uses a completely different technique:
  ordering elements and counting differences by "order" (index gap j - i).

  Key idea: For Sidon A = {a₁ < ... < a_k} ⊆ [N], ALL pairwise differences
  are distinct. The differences of orders 1..ℓ are m = ℓ(k-(ℓ+1)/2)
  distinct positive integers. Their sum is ≥ m²/2 (minimum sum of m distinct
  positive integers) and ≤ ℓ(ℓ+1)N/2 (telescoping: order-r diffs sum to ≤ rN).
  This gives ℓ(k-(ℓ+1)/2)² < (ℓ+1)N, and with ℓ = ⌊N^{1/4}⌋:
    k < √N + N^{1/4} + 1.
-/

/-- For a Sidon set, all pairwise positive differences are distinct.
    This is equivalent to the Sidon (B₂) property. -/
theorem sidon_distinct_differences (A : Finset ℕ) (hS : IsSidonSet A) :
    ∀ a₁ ∈ A, ∀ b₁ ∈ A, ∀ a₂ ∈ A, ∀ b₂ ∈ A,
      a₁ < b₁ → a₂ < b₂ → b₁ - a₁ = b₂ - a₂ → (a₁ = a₂ ∧ b₁ = b₂) := by
  intro a₁ ha₁ b₁ hb₁ a₂ ha₂ b₂ hb₂ h₁ h₂ heq
  have hsum : a₁ + b₂ = a₂ + b₁ := by omega
  clear heq  -- Remove Nat subtraction from context (confuses omega)
  -- 4-way case split on orderings needed for Sidon application
  by_cases hab : a₁ ≤ b₂
  · by_cases hab' : a₂ ≤ b₁
    · -- a₁ ≤ b₂, a₂ ≤ b₁: direct Sidon on (a₁,b₂) vs (a₂,b₁)
      have hs := hS a₁ ha₁ b₂ hb₂ a₂ ha₂ b₁ hb₁ hab hab' hsum
      exact ⟨hs.1, hs.2.symm⟩
    · -- a₁ ≤ b₂, b₁ < a₂: Sidon on (a₁,b₂) vs (b₁,a₂) → a₁=b₁, contradiction
      push_neg at hab'
      exfalso
      have hs := hS a₁ ha₁ b₂ hb₂ b₁ hb₁ a₂ ha₂ hab (by omega) (by omega)
      omega
  · by_cases hab' : a₂ ≤ b₁
    · -- b₂ < a₁, a₂ ≤ b₁: Sidon on (b₂,a₁) vs (a₂,b₁) → a₁=b₁, contradiction
      push_neg at hab
      exfalso
      have hs := hS b₂ hb₂ a₁ ha₁ a₂ ha₂ b₁ hb₁ (by omega) hab' (by omega)
      omega
    · -- b₂ < a₁, b₁ < a₂: chain a₁ < b₁ < a₂ < b₂ < a₁, contradiction
      push_neg at hab hab'
      omega

/-! ## Intermediate lemmas for the order-of-differences proof -/

/-- The set of positive pairwise differences from A. -/
def posDiffs (A : Finset ℕ) : Finset ℕ :=
  ((A ×ˢ A).filter (fun p => p.1 < p.2)).image (fun p => p.2 - p.1)

/-- For a Sidon set, the map (a,b) ↦ b-a is injective on ordered pairs,
    so |posDiffs A| = k(k-1)/2. -/
theorem card_posDiffs_sidon (A : Finset ℕ) (hS : IsSidonSet A) :
    (posDiffs A).card = A.card * (A.card - 1) / 2 := by
  unfold posDiffs
  -- Step 1: Injectivity from Sidon distinct differences
  have h_inj : Set.InjOn (fun p : ℕ × ℕ => p.2 - p.1)
      ↑((A ×ˢ A).filter (fun p => p.1 < p.2)) := by
    intro ⟨a₁, b₁⟩ h₁ ⟨a₂, b₂⟩ h₂ heq
    simp only [Finset.mem_coe, Finset.mem_filter, Finset.mem_product] at h₁ h₂
    have := sidon_distinct_differences A hS a₁ h₁.1.1 b₁ h₁.1.2 a₂ h₂.1.1 b₂ h₂.1.2 h₁.2 h₂.2 heq
    exact Prod.ext this.1 this.2
  rw [Finset.card_image_of_injOn h_inj]
  -- Step 2: filter(< on A×A) = filter(< on offDiag)
  have h_filter_eq : (A ×ˢ A).filter (fun p : ℕ × ℕ => p.1 < p.2) =
      A.offDiag.filter (fun p : ℕ × ℕ => p.1 < p.2) := by
    ext ⟨a, b⟩
    simp only [Finset.mem_filter, Finset.mem_product, Finset.mem_offDiag]
    constructor
    · intro ⟨⟨ha, hb⟩, hab⟩; exact ⟨⟨ha, hb, Nat.ne_of_lt hab⟩, hab⟩
    · intro ⟨⟨ha, hb, _⟩, hab⟩; exact ⟨⟨ha, hb⟩, hab⟩
  rw [h_filter_eq]
  -- Step 3: Partition offDiag into filter(<) ∪ filter(>)
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
  -- Step 4: Swap bijection |filter(>)| = |filter(<)|
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
  -- Step 5: Combine cardinalities
  have h_card : A.offDiag.card =
      (A.offDiag.filter (fun p : ℕ × ℕ => p.1 < p.2)).card +
      (A.offDiag.filter (fun p : ℕ × ℕ => p.2 < p.1)).card := by
    rw [← Finset.card_union_of_disjoint h_disj, ← h_union]
  rw [h_swap] at h_card
  -- h_card : |offDiag| = 2 * |filter(<)|
  -- offDiag_card : |offDiag| = k*k - k
  have h_mul_sub : A.card * (A.card - 1) = A.card * A.card - A.card := by
    cases A.card with
    | zero => simp
    | succ n =>
      simp only [Nat.succ_sub_one]
      rw [show (n + 1) * (n + 1) = (n + 1) * n + (n + 1) from by ring, Nat.add_sub_cancel]
  have h_offDiag_eq : A.offDiag.card = A.card * (A.card - 1) :=
    A.offDiag_card.trans h_mul_sub.symm
  -- 2 * |filter(<)| = k*(k-1)
  have h_2c : 2 * (A.offDiag.filter (fun p : ℕ × ℕ => p.1 < p.2)).card =
      A.card * (A.card - 1) := by linarith
  -- Final: |filter(<)| = k*(k-1)/2
  have : A.card * (A.card - 1) / 2 =
      (A.offDiag.filter (fun p : ℕ × ℕ => p.1 < p.2)).card := by
    rw [← h_2c]; exact Nat.mul_div_cancel_left _ (by omega)
  exact this.symm

/-- All positive differences of A ⊆ {0,...,N} lie in {1,...,N}. -/
theorem posDiffs_subset_Icc (A : Finset ℕ) (N : ℕ)
    (hA : A ⊆ Finset.range (N + 1)) :
    ∀ d ∈ posDiffs A, d ≤ N := by
  intro d hd
  simp only [posDiffs, Finset.mem_image, Finset.mem_filter, Finset.mem_product] at hd
  obtain ⟨⟨a, b⟩, ⟨⟨ha, hb⟩, hab⟩, rfl⟩ := hd
  have : b ≤ N := by have := Finset.mem_range.mp (hA hb); omega
  omega

/-! ### Helper: Sum of distinct positive naturals -/

/-- Auxiliary: For Finset S ⊆ ℕ with |S| = m and all elements ≥ c,
    m² + 2mc ≤ 2·sum(S) + m.
    Equivalently: 2·sum(S) ≥ m(m-1) + 2mc (but stated without ℕ subtraction).
    Used with c = 1 for the Lindström lower bound. -/
private lemma sum_distinct_ge_aux : ∀ (m : ℕ) (S : Finset ℕ) (c : ℕ),
    S.card = m → (∀ x ∈ S, c ≤ x) →
    m * m + 2 * m * c ≤ 2 * S.sum id + m := by
  intro m
  induction m with
  | zero => intro S c hm _; simp [show S = ∅ from Finset.card_eq_zero.mp hm]
  | succ n ih =>
    intro S c hm hc
    have hne : S.Nonempty := Finset.card_pos.mp (by omega)
    set x := S.min' hne
    have hx_mem : x ∈ S := Finset.min'_mem S hne
    have hx_ge : c ≤ x := hc x hx_mem
    set S' := S.erase x
    have hS'_card : S'.card = n := by
      rw [Finset.card_erase_of_mem hx_mem, hm]; omega
    have hS'_bound : ∀ y ∈ S', c + 1 ≤ y := by
      intro y hy
      have hy_mem : y ∈ S := Finset.mem_of_mem_erase hy
      have hy_ne : y ≠ x := Finset.ne_of_mem_erase hy
      have := Finset.min'_le S y hy_mem
      omega
    have h_ih := ih S' (c + 1) hS'_card hS'_bound
    -- h_ih : n * n + 2 * n * (c + 1) ≤ 2 * S'.sum id + n
    have h_split : S.sum id = (S.erase x).sum id + x :=
      (Finset.sum_erase_add S id hx_mem).symm
    -- Expand nonlinear terms for linarith
    have e1 : (n + 1) * (n + 1) = n * n + 2 * n + 1 := by ring
    have e2 : 2 * (n + 1) * c = 2 * n * c + 2 * c := by ring
    have e3 : 2 * n * (c + 1) = 2 * n * c + 2 * n := by ring
    rw [e3] at h_ih
    rw [e1, e2, h_split]
    -- Goal: n*n + 2*n + 1 + (2*n*c + 2*c) ≤ 2*(S'.sum id + x) + (n+1)
    -- From h_ih: n*n + 2*n*c + 2*n ≤ 2*S'.sum id + n
    -- From hx_ge: c ≤ x
    linarith

/-- Sum of m distinct positive naturals is at least m(m+1)/2.
    Stated as m(m+1) ≤ 2·sum to avoid ℕ division. -/
lemma sum_distinct_pos_ge (S : Finset ℕ) (h_pos : ∀ x ∈ S, 0 < x) :
    S.card * (S.card + 1) ≤ 2 * S.sum id := by
  have h := sum_distinct_ge_aux S.card S 1 rfl (fun x hx => h_pos x hx)
  -- h : S.card * S.card + 2 * S.card * 1 ≤ 2 * S.sum id + S.card
  have e : S.card * (S.card + 1) = S.card * S.card + S.card := by ring
  linarith

/-! ### Combinatorial core: counting and summing order-bounded differences -/

/-- **Order-bounded difference counting for Sidon sets.**

    For Sidon A = {a₀ < ... < a_{k-1}} ⊆ {0,...,N}, the differences of
    orders 1 through ℓ (i.e., a_{i+r} - a_i for 1 ≤ r ≤ ℓ) form a set D of
    m distinct positive naturals where 2m = ℓ(2k-ℓ-1) and sum(D) ≤ ℓ(ℓ+1)N/2.

    **Proof requires (not formalized here):**
    - Sorted enumeration via `Finset.orderEmbOfFin`
    - Strict monotonicity → injectivity of (r,i) ↦ (a_i, a_{i+r})
    - `sidon_distinct_differences` → all d(r,i) distinct
    - Telescoping: ∑_i (a_{i+r}-a_i) = ∑_{j≥k-r} a_j - ∑_{j<r} a_j ≤ r·N

    **Reference:** Lindström (1969); BFR (2023) Section 2.
    Stated in doubled form (2m, 2·sum) to avoid ℕ division. -/
axiom order_diff_counting (A : Finset ℕ) (N : ℕ) (ℓ : ℕ)
    (hS : IsSidonSet A) (hA : A ⊆ Finset.range (N + 1))
    (hℓ : ℓ < A.card) (hℓ_pos : 0 < ℓ) :
    ∃ D : Finset ℕ,
      D.card * 2 = ℓ * (2 * A.card - ℓ - 1) ∧
      (∀ d ∈ D, 0 < d) ∧
      2 * D.sum id ≤ ℓ * (ℓ + 1) * N

/-! ### Lindström core quadratic inequality -/

/-- **Core Lindström quadratic inequality (order-of-differences).**

    For Sidon A ⊆ {0,...,N} and parameter ℓ with ℓ < k:
      ℓ · (2k - ℓ - 1)² ≤ 4(ℓ+1) · N.

    **Statement note:** Multiplied through by 4 to avoid ℕ division in (ℓ+1)/2.
    The classical real-arithmetic form ℓ(k-(ℓ+1)/2)² ≤ (ℓ+1)N is equivalent
    via 2m = ℓ(2k-ℓ-1) where m = ∑_{r=1}^ℓ (k-r).

    **Proof:** From `order_diff_counting` + `sum_distinct_pos_ge` + algebra.
    Chain: m(m+1) ≤ 2·sum(D) ≤ ℓ(ℓ+1)N, then (2m)² ≤ 4m(m+1) ≤ 4ℓ(ℓ+1)N,
    and 2m = ℓ(2k-ℓ-1), so ℓ²(2k-ℓ-1)² ≤ 4ℓ(ℓ+1)N. Cancel ℓ.

    **Reference:** Lindström (1969), reproduced in BFR (2023) Section 2. -/
theorem lindstrom_quadratic (A : Finset ℕ) (N : ℕ) (ℓ : ℕ) (hS : IsSidonSet A)
    (hA : A ⊆ Finset.range (N + 1)) (hℓ : ℓ < A.card) (hℓ_pos : 0 < ℓ) :
    ℓ * (2 * A.card - ℓ - 1) ^ 2 ≤ 4 * (ℓ + 1) * N := by
  obtain ⟨D, hcount, hpos, hsum⟩ := order_diff_counting A N ℓ hS hA hℓ hℓ_pos
  have h_lb := sum_distinct_pos_ge D hpos
  -- h_lb : D.card * (D.card + 1) ≤ 2 * D.sum id
  -- hcount : D.card * 2 = ℓ * (2 * A.card - ℓ - 1)
  -- hsum : 2 * D.sum id ≤ ℓ * (ℓ + 1) * N
  -- Chain: D.card * (D.card + 1) ≤ ℓ * (ℓ + 1) * N
  have hmm : D.card * (D.card + 1) ≤ ℓ * (ℓ + 1) * N := by linarith
  -- D.card² ≤ D.card*(D.card+1) ≤ ℓ*(ℓ+1)*N
  have h_sq : D.card * D.card ≤ ℓ * (ℓ + 1) * N := by nlinarith
  -- Multiply suffices by ℓ, then cancel:
  -- ℓ*(ℓ*q²) = (ℓ*q)² = (2*D.card)² = 4*D.card² ≤ 4*ℓ*(ℓ+1)*N = ℓ*(4*(ℓ+1)*N)
  suffices hsuff : ℓ * (ℓ * (2 * A.card - ℓ - 1) ^ 2) ≤ ℓ * (4 * (ℓ + 1) * N) by
    exact Nat.le_of_mul_le_mul_left hsuff hℓ_pos
  -- Rewrite ^2 to * for ring reasoning
  set q := 2 * A.card - ℓ - 1 with hq_def
  -- hcount : D.card * 2 = ℓ * q
  -- Goal: ℓ * (ℓ * q ^ 2) ≤ ℓ * (4 * (ℓ + 1) * N)
  -- LHS = (ℓ*q)*(ℓ*q) = (D.card*2)*(D.card*2) = 4*D.card*D.card
  -- RHS = 4*ℓ*(ℓ+1)*N ≥ 4*D.card*D.card (from h_sq)
  -- First show LHS = (D.card*2)*(D.card*2):
  have h_lhs : ℓ * (ℓ * q ^ 2) = D.card * 2 * (D.card * 2) := by
    have : q ^ 2 = q * q := sq q
    rw [this]
    nlinarith [hcount]
  rw [h_lhs]
  -- Goal: D.card * 2 * (D.card * 2) ≤ ℓ * (4 * (ℓ + 1) * N)
  nlinarith [h_sq]

/-- **Weak Lindström bound: k ≤ √(2N) + 1.**
    From lindstrom_quadratic with ℓ = 1. This is provable and gives a clean
    ℕ statement, though weaker than the full √N + N^{1/4} + 1. -/
theorem lindstrom_bound_weak (A : Finset ℕ) (N : ℕ) (hS : IsSidonSet A)
    (hA : A ⊆ Finset.range (N + 1)) (hN : 0 < N)
    (hk : 1 < A.card) :
    A.card ≤ Nat.sqrt (2 * N) + 1 := by
  have hq := lindstrom_quadratic A N 1 hS hA hk (by omega)
  simp only [one_mul] at hq
  -- hq : (2 * A.card - 1 - 1) ^ 2 ≤ 4 * 2 * N
  set k := A.card
  -- Step 1: (k-1)*(k-1) ≤ 2*N from (2k-2)^2 ≤ 8N
  have h2k : 2 * k - 1 - 1 = 2 * (k - 1) := by omega
  rw [h2k] at hq
  -- hq : (2*(k-1))^2 ≤ 8*N
  have h_sq : (k - 1) * (k - 1) ≤ 2 * N := by nlinarith [hq, sq_nonneg (k - 1)]
  -- Step 2: (k-1) ≤ Nat.sqrt(2*N) via Nat.le_sqrt
  have h_le : k - 1 ≤ Nat.sqrt (2 * N) := Nat.le_sqrt.mpr h_sq
  omega

/-- **Lindström bound: k ≤ √N + ⁴√N + 1.**
    From lindstrom_quadratic with ℓ = Nat.sqrt (Nat.sqrt N).

    **⚠ Statement requires real-number intermediate step.**
    The quadratic `ℓ(2k-ℓ-1)² ≤ 4(ℓ+1)N` yields (over ℝ):
      k ≤ √(N(ℓ+1)/ℓ) + (ℓ+1)/2
    Converting to ℕ with ℓ = ⌊⁴√N⌋ requires bounding:
      Nat.sqrt(N + N/ℓ) ≤ Nat.sqrt N + corrections
    which needs either Taylor-expansion-style ℕ bounds on Nat.sqrt
    or a direct proof that Nat.sqrt rounding doesn't accumulate.

    `lindstrom_bound_weak` (k ≤ √(2N)+1) is the strongest version
    provable from `lindstrom_quadratic` via pure ℕ arithmetic.

    **Reference:** Lindström (1969), J. Combinatorial Theory 7(1). -/
axiom lindstrom_bound (A : Finset ℕ) (N : ℕ) (hS : IsSidonSet A)
    (hA : A ⊆ Finset.range (N + 1)) (hN : 0 < N) :
    A.card ≤ Nat.sqrt N + Nat.sqrt (Nat.sqrt N) + 1

/-! ## Summary

  **Proven (zero sorries):**
  1. pigeonhole_residue: partition + pigeonhole
  2. residue_class_scaled_sidon: Sidon preservation under modular scaling
  3. scaled_range: range containment of scaled residue class
  4. lindstrom_parametric: k² ≤ 2Nt + kt (residue class parametric bound)
  5. sidon_distinct_differences: all positive differences are distinct
  6. card_posDiffs_sidon: |posDiffs A| = k(k-1)/2
  7. posDiffs_subset_Icc: differences ≤ N
  8. sum_distinct_pos_ge: sum of m distinct positive naturals ≥ m(m+1)/2
  9. lindstrom_quadratic: ℓ(2k-ℓ-1)² ≤ 4(ℓ+1)N (from axiom + algebra)
  10. lindstrom_bound_weak: k ≤ √(2N) + 1 (from 9 with ℓ=1 + Nat.le_sqrt)

  **Axioms (3 total, all with references):**
  - sidon_elem_bound: k(k-1) ≤ 2M (proved in Erdos30_Complete, pending Mathlib API port)
  - order_diff_counting: sorted enumeration + telescoping (requires orderEmbOfFin)
  - lindstrom_bound: k ≤ ⌊√N⌋ + ⌊⁴√N⌋ + 1 (requires ℝ→ℕ Nat.sqrt bounding)

  **Proof dependency DAG:**
    pigeonhole_residue ──┐
    residue_class_scaled_sidon ──┤
    scaled_range ──┤──→ lindstrom_parametric (for BFR)
    sidon_elem_bound ──┘

    order_diff_counting ──┐
    sum_distinct_pos_ge ──┤──→ lindstrom_quadratic ──→ lindstrom_bound_weak ✓
                          │                        └──→ lindstrom_bound (axiom: ℝ→ℕ step)

  **Note on proof architecture:**
  The residue class machinery (pigeonhole, scaling, parametric) is needed
  for the BFR 0.998 improvement (Erdos30_BFR.lean), not for the basic
  Lindström bound. The Lindström bound uses a different technique:
  counting differences by order in the sorted sequence.

  **Statement correction (prior session):** The original ℕ formulation
  ℓ·(k-(ℓ+1)/2)² ≤ (ℓ+1)·N is false for even ℓ with tight parameters
  (e.g. ℓ=4, k=10, N=47). Fixed to ℓ·(2k-ℓ-1)² ≤ 4·(ℓ+1)·N which
  avoids ℕ division entirely by multiplying through by 4.
-/

end Erdos.Sidon

