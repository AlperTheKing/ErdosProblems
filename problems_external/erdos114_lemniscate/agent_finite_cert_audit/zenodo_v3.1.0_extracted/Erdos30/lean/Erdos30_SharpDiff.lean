/-
  Erdős Problem #30 — Sharp Sidon Difference Bound

  **Theorem (sharp form):** For a Sidon set A ⊆ [0, N],
      |A|·(|A| - 1) ≤ 2N.

  This is the PMF-aligned close-packing form: it encodes the λ_max(W→∞) ∼ √N
  scaling for the Sidon transfer matrix, and is a factor-2 improvement over
  the sum-counting bound |A|·(|A|-1) ≤ 2g(2N+1) = 4N+2 at g=1
  (proved in `Erdos755_DifferenceCount`).

  **Proof:** Sidon ⇒ the map (a,b) ↦ a - b on the strict upper triangle
  {(a,b) ∈ A×A : b < a} is injective into [1, N]. The strict upper triangle
  has |A|·(|A|-1)/2 elements, hence |A|·(|A|-1)/2 ≤ N.

  Lean version: leanprover/lean4:v4.24.0
  Mathlib version: f897ebcf72cd16f89ab4577d0c826cd14afaafc7
-/

import Mathlib
import Erdos30_Sidon_Defs

open Finset

namespace Erdos.Sidon.SharpDiff

open Erdos.Sidon

/-- The strict upper triangle of A × A: pairs (a, b) with b < a. -/
def strictUpper (A : Finset ℕ) : Finset (ℕ × ℕ) :=
  (A ×ˢ A).filter (fun p => p.2 < p.1)

/-- **Sidon ⇒ differences on the strict upper triangle are injective.** -/
lemma diff_injOn_strictUpper (A : Finset ℕ) (hS : IsSidonSet A) :
    Set.InjOn (fun p : ℕ × ℕ => p.1 - p.2) ↑(strictUpper A) := by
  intro p hp q hq hpq
  simp only [strictUpper, Finset.coe_filter, Finset.mem_coe, Finset.mem_product,
    Set.mem_setOf_eq] at hp hq
  obtain ⟨⟨hp1, hp2⟩, hplt⟩ := hp
  obtain ⟨⟨hq1, hq2⟩, hqlt⟩ := hq
  -- p.1 - p.2 = q.1 - q.2 with p.2 < p.1 and q.2 < q.1
  -- Convert to sum form: p.1 + q.2 = q.1 + p.2
  have hsum : p.2 + q.1 = q.2 + p.1 := by
    simp only at hpq
    have hp_sub : p.1 - p.2 + p.2 = p.1 := Nat.sub_add_cancel (le_of_lt hplt)
    have hq_sub : q.1 - q.2 + q.2 = q.1 := Nat.sub_add_cancel (le_of_lt hqlt)
    omega
  -- Apply Sidon: (p.2, q.1) and (q.2, p.1) both ordered with sum equal
  have hp2_le : p.2 ≤ q.1 ∨ q.1 ≤ p.2 := le_or_lt p.2 q.1 |>.imp id le_of_lt
  -- IsSidonSet requires a₁ ≤ b₁ and a₂ ≤ b₂. Reorder as needed.
  -- Case split on ordering
  rcases le_total p.2 q.1 with h1 | h1
  · rcases le_total q.2 p.1 with h2 | h2
    · -- a₁=p.2, b₁=q.1, a₂=q.2, b₂=p.1. Sidon ⇒ p.2=q.2 ∧ q.1=p.1
      obtain ⟨ha, hb⟩ := hS p.2 hp2 q.1 hq1 q.2 hq2 p.1 hp1 h1 h2 hsum
      exact Prod.ext hb.symm ha
    · -- h1: p.2 ≤ q.1, h2: p.1 ≤ q.2. Rearrange Sidon on p.1+q.2 = p.2+q.1.
      have hsum' : p.1 + q.2 = p.2 + q.1 := by omega
      obtain ⟨ha, _⟩ := hS p.1 hp1 q.2 hq2 p.2 hp2 q.1 hq1 h2 h1 hsum'
      -- ha : p.1 = p.2, contradicting hplt
      omega
  · rcases le_total q.2 p.1 with h2 | h2
    · -- h1: q.1 ≤ p.2, h2: q.2 ≤ p.1. Rearrange Sidon on q.2+p.1 = q.1+p.2.
      have hsum' : q.2 + p.1 = q.1 + p.2 := by omega
      obtain ⟨ha, _⟩ := hS q.2 hq2 p.1 hp1 q.1 hq1 p.2 hp2 h2 h1 hsum'
      -- ha : q.2 = q.1, contradicting hqlt
      omega
    · have hsum' : q.1 + p.2 = p.1 + q.2 := by omega
      -- a₁=q.1, b₁=p.2, a₂=p.1, b₂=q.2. Sidon ⇒ q.1=p.1 ∧ p.2=q.2
      obtain ⟨ha, hb⟩ := hS q.1 hq1 p.2 hp2 p.1 hp1 q.2 hq2 h1 h2 hsum'
      exact Prod.ext ha.symm hb

/-- Cardinality of the strict upper triangle: |A|·(|A| - 1) / 2 — but it's
    easier to state `2 · |strictUpper A| = |A|·(|A| - 1)` to avoid Nat division. -/
lemma strictUpper_card_double (A : Finset ℕ) :
    2 * (strictUpper A).card = A.card * (A.card - 1) := by
  -- A.offDiag = strictUpper A ∪ strictLower A (disjoint), each of size |A|(|A|-1)/2.
  -- Use offDiag_card = |A|² - |A| and the involution swap.
  have h_off : A.offDiag.card = A.card * A.card - A.card := A.offDiag_card
  -- Define strictLower = swap-image of strictUpper
  have h_swap : A.offDiag = strictUpper A ∪ (strictUpper A).image Prod.swap := by
    ext ⟨x, y⟩
    simp only [Finset.mem_offDiag, strictUpper, Finset.mem_union, Finset.mem_filter,
      Finset.mem_product, Finset.mem_image, Prod.swap, Prod.mk.injEq]
    constructor
    · rintro ⟨hx, hy, hne⟩
      rcases lt_or_gt_of_ne hne with h | h
      · right; exact ⟨(y, x), ⟨⟨hy, hx⟩, h⟩, rfl, rfl⟩
      · left; exact ⟨⟨hx, hy⟩, h⟩
    · rintro (⟨⟨hx, hy⟩, hlt⟩ | ⟨⟨a, b⟩, ⟨⟨ha, hb⟩, hlt⟩, hax, hby⟩)
      · exact ⟨hx, hy, ne_of_gt hlt⟩
      · subst hax; subst hby
        exact ⟨hb, ha, ne_of_lt hlt⟩
  have h_disj : Disjoint (strictUpper A) ((strictUpper A).image Prod.swap) := by
    rw [Finset.disjoint_left]
    intro ⟨x, y⟩ h1 h2
    simp only [strictUpper, Finset.mem_filter, Finset.mem_product] at h1
    simp only [Finset.mem_image, strictUpper, Finset.mem_filter, Finset.mem_product,
      Prod.swap, Prod.mk.injEq] at h2
    obtain ⟨_, hlt1⟩ := h1
    obtain ⟨⟨a, b⟩, ⟨_, hlt2⟩, hax, hby⟩ := h2
    subst hax; subst hby
    omega
  have h_img_card : ((strictUpper A).image Prod.swap).card = (strictUpper A).card := by
    apply Finset.card_image_of_injective
    intro ⟨a, b⟩ ⟨c, d⟩ h
    simp [Prod.swap, Prod.mk.injEq] at h
    ext <;> tauto
  have h_off_card :
      A.offDiag.card = (strictUpper A).card + ((strictUpper A).image Prod.swap).card := by
    rw [h_swap]; exact Finset.card_union_of_disjoint h_disj
  rw [h_img_card] at h_off_card
  rw [h_off] at h_off_card
  -- h_off_card : A.card * A.card - A.card = (strictUpper A).card + (strictUpper A).card
  -- Goal: 2 * (strictUpper A).card = A.card * (A.card - 1)
  rw [Nat.mul_sub_one]
  omega

/-- **MAIN THEOREM: Sharp Sidon difference bound.**

For a Sidon set A ⊆ [0, N], |A|·(|A| - 1) ≤ 2N.

This is a factor-2 improvement over the sum-counting bound |A|(|A|-1) ≤ 4N+2
and matches the PMF close-packing density prediction λ_max(W→∞) ∼ √N. -/
theorem sidon_sharp_diff_bound (A : Finset ℕ) (N : ℕ)
    (hS : IsSidonSet A)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card * (A.card - 1) ≤ 2 * N := by
  -- Step 1: differences on strictUpper are injective
  have h_inj := diff_injOn_strictUpper A hS
  -- Step 2: image of differences lies in Finset.Icc 1 N
  have h_img_sub :
      (strictUpper A).image (fun p : ℕ × ℕ => p.1 - p.2) ⊆ Finset.Icc 1 N := by
    intro d hd
    simp only [Finset.mem_image] at hd
    obtain ⟨p, hp, heq⟩ := hd
    simp only [strictUpper, Finset.mem_filter, Finset.mem_product] at hp
    obtain ⟨⟨hp1, hp2⟩, hplt⟩ := hp
    have hp1_le : p.1 ≤ N := by
      have := Finset.mem_range.mp (hA hp1); omega
    rw [Finset.mem_Icc]
    constructor
    · omega
    · omega
  -- Step 3: |image| = |strictUpper|
  have h_img_card :
      ((strictUpper A).image (fun p : ℕ × ℕ => p.1 - p.2)).card =
        (strictUpper A).card :=
    Finset.card_image_of_injOn h_inj
  -- Step 4: |image| ≤ |Icc 1 N| = N
  have h_card_le :
      ((strictUpper A).image (fun p : ℕ × ℕ => p.1 - p.2)).card ≤ N := by
    calc _ ≤ (Finset.Icc 1 N).card := Finset.card_le_card h_img_sub
      _ = N := by rw [Nat.card_Icc]; omega
  -- Step 5: combine with doubling identity
  rw [h_img_card] at h_card_le
  have := strictUpper_card_double A
  omega

end Erdos.Sidon.SharpDiff
