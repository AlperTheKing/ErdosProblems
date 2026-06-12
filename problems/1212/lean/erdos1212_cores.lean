import Mathlib

/-!
# Erdős #1212 — machine-checked cores of the verified partial results (2026-06-10)

* `Erdos1212.right_neighbor_witness_free` / `left_neighbor_witness_free` /
  `vertical_neighbor_both_even` — the isolation lemma behind the No-Periodic-Certificate theorem.
* `Erdos1212.vertical_leg_valid` / `horizontal_leg_valid` — the L-path core of the
  Composite-Anchor reduction.
* `Erdos1212.walk_intermediate_value` — the winding step (±1-walks attain intermediate values).
-/

namespace Erdos1212

/-- A natural number is composite. -/
def Composite (n : ℕ) : Prop := 2 ≤ n ∧ ¬ n.Prime

/-! ## Isolation lemma -/

section Isolation

variable {P : Finset ℕ} {x y : ℕ}

/-- If every `p ∈ P` divides `x` and none divides `y`, the right neighbour `(x+1, y)` has no
prime of `P` dividing either coordinate. -/
theorem right_neighbor_witness_free (hP : ∀ p ∈ P, p.Prime)
    (hx : ∀ p ∈ P, p ∣ x) (hy : ∀ p ∈ P, ¬ p ∣ y) :
    ∀ p ∈ P, ¬ p ∣ (x + 1) ∧ ¬ p ∣ y := by
  intro p hp
  refine ⟨fun hdvd => ?_, hy p hp⟩
  have h1 : p ∣ 1 := by
    have h := Nat.dvd_sub hdvd (hx p hp)
    simpa using h
  have := (hP p hp).one_lt
  have := Nat.dvd_one.mp h1
  omega

/-- Left-neighbour version (for `x ≥ 1`). -/
theorem left_neighbor_witness_free (hP : ∀ p ∈ P, p.Prime) (hx1 : 1 ≤ x)
    (hx : ∀ p ∈ P, p ∣ x) (hy : ∀ p ∈ P, ¬ p ∣ y) :
    ∀ p ∈ P, ¬ p ∣ (x - 1) ∧ ¬ p ∣ y := by
  intro p hp
  refine ⟨fun hdvd => ?_, hy p hp⟩
  have h1 : p ∣ 1 := by
    have h := Nat.dvd_sub (hx p hp) hdvd
    have hx_sub : x - (x - 1) = 1 := by omega
    rwa [hx_sub] at h
  have := (hP p hp).one_lt
  have := Nat.dvd_one.mp h1
  omega

/-- Vertical neighbours of `(x, y)` are both-even when `2 ∣ x`, `2 ∤ y`. -/
theorem vertical_neighbor_both_even (h2x : 2 ∣ x) (h2y : ¬ 2 ∣ y) :
    (2 ∣ x ∧ 2 ∣ (y + 1)) ∧ (1 ≤ y → 2 ∣ x ∧ 2 ∣ (y - 1)) := by
  refine ⟨⟨h2x, by omega⟩, fun hy1 => ⟨h2x, by omega⟩⟩

end Isolation

/-! ## L-path lemma -/

section LPath

variable {a b c : ℕ}

/-- Vertical-leg vertices `(a, s)`, `b ≤ s ≤ c`, are valid #1212 vertices. -/
theorem vertical_leg_valid (ha : Composite a) (hb : 2 ≤ b)
    (hV : ∀ s, b ≤ s → s ≤ c → Nat.gcd a s = 1) :
    ∀ s, b ≤ s → s ≤ c →
      Nat.gcd a s = 1 ∧ 2 ≤ min a s ∧ (Composite a ∨ Composite s) ∧ ¬ (a.Prime ∧ s.Prime) := by
  intro s hs1 hs2
  refine ⟨hV s hs1 hs2, ?_, Or.inl ha, fun h => ha.2 h.1⟩
  have := ha.1
  omega

/-- Horizontal-leg vertices `(s, c)`, `a ≤ s ≤ b`, are valid #1212 vertices. -/
theorem horizontal_leg_valid (hc : Composite c) (ha2 : 2 ≤ a)
    (hH : ∀ s, a ≤ s → s ≤ b → Nat.gcd s c = 1) :
    ∀ s, a ≤ s → s ≤ b →
      Nat.gcd s c = 1 ∧ 2 ≤ min s c ∧ (Composite s ∨ Composite c) ∧ ¬ (s.Prime ∧ c.Prime) := by
  intro s hs1 hs2
  refine ⟨hH s hs1 hs2, ?_, Or.inr hc, fun h => hc.2 h.2⟩
  have := hc.1
  omega

end LPath

/-! ## Intermediate value for ±1-step walks -/

/-- Consecutive entries differ by at most 1. -/
def IsWalkX : List ℤ → Prop
  | [] => True
  | [_] => True
  | (u :: v :: rest) => (u - v).natAbs ≤ 1 ∧ IsWalkX (v :: rest)

/-- A ±1-step walk attains every value between its first and last entries. -/
theorem walk_intermediate_value :
    ∀ (l : List ℤ), IsWalkX l → ∀ x0 xe : ℤ, l.head? = some x0 → l.getLast? = some xe →
      ∀ t : ℤ, x0 ≤ t → t ≤ xe → t ∈ l := by
  intro l
  induction l with
  | nil => intro _ x0 xe h0 _ _ _ _; simp at h0
  | cons u rest ih =>
    intro hw x0 xe h0 he t ht0 hte
    simp only [List.head?_cons, Option.some.injEq] at h0
    subst h0
    cases rest with
    | nil =>
      simp only [List.getLast?_singleton, Option.some.injEq] at he
      subst he
      have : t = u := le_antisymm hte ht0
      simp [this]
    | cons v rest' =>
      obtain ⟨hstep, hw'⟩ := hw
      by_cases hcase : t ≤ u
      · have : t = u := le_antisymm hcase ht0
        simp [this]
      · push_neg at hcase
        have he' : (v :: rest').getLast? = some xe := by
          simpa [List.getLast?_cons_cons] using he
        have hv : v ≤ t := by omega
        have hmem : t ∈ (v :: rest') := ih hw' v xe (by simp) he' t hv hte
        exact List.mem_cons_of_mem u hmem

end Erdos1212
