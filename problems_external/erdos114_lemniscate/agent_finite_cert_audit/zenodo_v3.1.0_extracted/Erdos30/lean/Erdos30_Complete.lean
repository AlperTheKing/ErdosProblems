/-
  Erdős Problem #30 — Elementary Sidon Set Cardinality Bound

  Theorem: For a Sidon set A ⊆ [N], |A| * (|A| - 1) ≤ 2N

  Proof sketch (difference counting):
    A Sidon set A has all pairwise sums a+b (a ≤ b) distinct.
    Equivalently, all pairwise differences a-b (a ≠ b) are distinct.
    For ordered pairs (a,b) with a > b, the difference a-b ∈ {1,...,N}.
    There are k(k-1)/2 such pairs (where k = |A|).
    By injectivity, k(k-1)/2 ≤ N, so k(k-1) ≤ 2N.

  Note: The equivalence between distinct sums and distinct differences
  follows from: a₁+b₁ = a₂+b₂ iff a₁-a₂ = b₂-b₁.

  Lean version: leanprover/lean4:v4.24.0
  Mathlib version: f897ebcf72cd16f89ab4577d0c826cd14afaafc7
-/

import Mathlib
import Erdos30_Sidon_Defs

open Finset Nat

namespace Erdos.Sidon

/-- Core Lemma: Difference Injectivity
    In a Sidon set, if a₁ > b₁ and a₂ > b₂ and a₁ - b₁ = a₂ - b₂,
    then a₁ = a₂ and b₁ = b₂. -/
theorem sidon_diff_injective (A : Finset ℕ)
    (hS : IsSidonSet A)
    (a₁ b₁ a₂ b₂ : ℕ)
    (ha₁ : a₁ ∈ A) (hb₁ : b₁ ∈ A) (ha₂ : a₂ ∈ A) (hb₂ : b₂ ∈ A)
    (hlt₁ : b₁ < a₁) (hlt₂ : b₂ < a₂)
    (heq : a₁ - b₁ = a₂ - b₂) :
    a₁ = a₂ ∧ b₁ = b₂ := by
  -- From a₁ - b₁ = a₂ - b₂ (in ℕ), we get a₁ + b₂ = a₂ + b₁
  have h_sum : a₁ + b₂ = a₂ + b₁ := by omega
  -- Case split on orderings
  by_cases h1 : b₂ ≤ a₁
  · by_cases h2 : b₁ ≤ a₂
    · -- Apply Sidon to (b₂, a₁) and (b₁, a₂): returns b₂ = b₁ ∧ a₁ = a₂
      have h_sidon := hS b₂ hb₂ a₁ ha₁ b₁ hb₁ a₂ ha₂ h1 h2 (by omega)
      exact ⟨h_sidon.right, h_sidon.left.symm⟩
    · -- Apply Sidon to (b₂, a₁) and (a₂, b₁)
      push_neg at h2
      have h_sidon := hS b₂ hb₂ a₁ ha₁ a₂ ha₂ b₁ hb₁ h1 (Nat.le_of_lt h2) (by omega)
      -- Returns a₂ = b₂ ∧ a₁ = b₁, but we need a₁ = a₂ ∧ b₁ = b₂
      exact ⟨h_sidon.right.symm, h_sidon.left.symm⟩
  · push_neg at h1
    by_cases h2 : b₁ ≤ a₂
    · -- Apply Sidon to (a₁, b₂) and (b₁, a₂)
      have h_sidon := hS a₁ ha₁ b₂ hb₂ b₁ hb₁ a₂ ha₂ (Nat.le_of_lt h1) h2 (by omega)
      -- Returns a₁ = b₁ ∧ b₂ = a₂, but we need a₁ = a₂ ∧ b₁ = b₂
      exact ⟨h_sidon.right.symm, h_sidon.left.symm⟩
    · -- Apply Sidon to (a₁, b₂) and (a₂, b₁)
      push_neg at h2
      have h_sidon := hS a₁ ha₁ b₂ hb₂ a₂ ha₂ b₁ hb₁ (Nat.le_of_lt h1) (Nat.le_of_lt h2) (by omega)
      -- Returns a₁ = a₂ ∧ b₂ = b₁
      exact ⟨h_sidon.left, h_sidon.right.symm⟩

/--
  **MAIN THEOREM 1: Difference-Counting Bound**

  For a Sidon set A ⊆ Finset.range (N + 1), the cardinality satisfies:
    A.card * (A.card - 1) ≤ 2 * N

  Proof Strategy:
  1. Count ordered pairs (a, b) with a, b ∈ A and b < a
  2. There are |A|(|A|-1)/2 such pairs
  3. The map (a,b) ↦ a - b is injective by Sidon property
  4. Each difference lies in {1,...,N}
  5. By pigeonhole: |A|(|A|-1)/2 ≤ N, so |A|(|A|-1) ≤ 2N

  Corollary: |A|² ≤ 2N + |A|, so |A| ≤ √(2N) + O(1)
-/
theorem sidon_difference_count (A : Finset ℕ) (N : ℕ)
    (hS : IsSidonSet A)
    (hA : A ⊆ Finset.range (N + 1)) :
    A.card * (A.card - 1) ≤ 2 * N := by
  -- Define pairs (a,b) with a > b
  set pairs := Finset.filter (fun p : ℕ × ℕ => p.2 < p.1) (A ×ˢ A)
  set diff_map := fun (p : ℕ × ℕ) => p.1 - p.2

  -- Step 1: Difference map is injective
  have h_inj : Set.InjOn diff_map (↑pairs) := by
    intro ⟨a₁, b₁⟩ h₁ ⟨a₂, b₂⟩ h₂ heq
    rw [Finset.mem_coe, Finset.mem_filter, Finset.mem_product] at h₁ h₂
    have := sidon_diff_injective A hS a₁ b₁ a₂ b₂ h₁.1.1 h₁.1.2 h₂.1.1 h₂.1.2 h₁.2 h₂.2 heq
    exact Prod.ext this.1 this.2

  -- Step 2: Image is bounded by {1,...,N}
  have h_range : Finset.image diff_map pairs ⊆ Finset.Icc 1 N := by
    intro d hd
    simp [Finset.mem_image, Finset.mem_filter, Finset.mem_product] at hd
    obtain ⟨⟨a, b⟩, ⟨ha, hb, hlt⟩, rfl⟩ := hd
    simp [Finset.mem_Icc]
    constructor
    · omega
    · have : a ≤ N := by
        have := Finset.mem_range.mp (hA ha)
        omega
      omega

  -- Step 3: Card image ≤ N
  have h_card_img : (Finset.image diff_map pairs).card ≤ N := by
    have := Finset.card_le_card h_range
    simp at this
    exact this

  -- Step 4: Card image = card pairs (by injectivity)
  have : (Finset.image diff_map pairs).card = pairs.card :=
    Finset.card_image_of_injOn h_inj

  -- Step 5: Card pairs = |A|(|A|-1)/2
  have h_pairs : pairs.card = A.card * (A.card - 1) / 2 := by
    -- Pairs with a > b correspond to 2-element subsets of A
    have : pairs.card = (Finset.powersetCard 2 A).card := by
      refine Finset.card_bij (fun p _ => {p.1, p.2}) ?_ ?_ ?_
      · intro ⟨a, b⟩ hp
        simp [Finset.mem_filter, Finset.mem_product] at hp
        rw [Finset.mem_powersetCard]
        refine ⟨?_, ?_⟩
        · intro x hx
          simp [Finset.mem_insert, Finset.mem_singleton] at hx
          cases hx with
          | inl h => exact h ▸ hp.1
          | inr h => exact h ▸ hp.2.1
        · rw [Finset.card_pair]
          exact Nat.ne_of_gt hp.2.2
      · intro ⟨a₁, b₁⟩ h₁ ⟨a₂, b₂⟩ h₂ heq
        simp [Finset.mem_filter, Finset.mem_product] at h₁ h₂
        have h₁lt := h₁.2.2
        have h₂lt := h₂.2.2
        suffices a₁ = a₂ ∧ b₁ = b₂ from Prod.ext this.1 this.2
        have ha : a₁ ∈ ({a₂, b₂} : Finset ℕ) := heq ▸ mem_insert_self a₁ _
        simp only [mem_insert, mem_singleton] at ha
        rcases ha with rfl | rfl
        · refine ⟨rfl, ?_⟩
          have hb : b₁ ∈ ({a₂, b₂} : Finset ℕ) :=
            heq ▸ mem_insert.mpr (Or.inr (mem_singleton_self b₁))
          simp only [mem_insert, mem_singleton] at hb
          rcases hb with rfl | rfl
          · omega
          · rfl
        · exfalso
          have ha₂ : a₂ ∈ ({b₂, b₁} : Finset ℕ) := heq.symm ▸ mem_insert_self a₂ _
          simp only [mem_insert, mem_singleton] at ha₂
          rcases ha₂ with rfl | rfl <;> omega
      · intro s hs
        rw [Finset.mem_powersetCard] at hs
        obtain ⟨hsub, hcard⟩ := hs
        rw [Finset.card_eq_two] at hcard
        obtain ⟨x, y, hxy, rfl⟩ := hcard
        cases Nat.lt_or_gt_of_ne hxy with
        | inl hlt =>
          exact ⟨(y, x), by simp [Finset.mem_filter, Finset.mem_product, hsub, hlt,
            Finset.pair_comm], by simp [Finset.pair_comm]⟩
        | inr hgt =>
          exact ⟨(x, y), by simp [Finset.mem_filter, Finset.mem_product, hsub, hgt], rfl⟩
    rw [this, Finset.card_powersetCard, Nat.choose_two_right]

  -- Step 6: Combine
  have h_div : A.card * (A.card - 1) / 2 ≤ N := by rw [← h_pairs, ← this]; exact h_card_img
  have h_even : Even (A.card * (A.card - 1)) := by
    rcases Nat.even_or_odd A.card with ⟨m, hm⟩ | ⟨m, hm⟩
    · exact ⟨m * (A.card - 1), by rw [hm]; ring⟩
    · exact ⟨A.card * m, by rw [hm]; omega⟩
  obtain ⟨k, hk⟩ := h_even
  rw [hk] at h_div
  rw [hk]
  omega

end Erdos.Sidon
