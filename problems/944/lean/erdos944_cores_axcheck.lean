import Mathlib

/-!
# Erdős #944 / Dirac k=4 — machine-checked cores of the rigidity package (2026-06-10)

* `Erdos944.singleton_edge_critical` — Lemma 1.1 core: if a proper-away-from-`v` 3-colouring `φ`
  gives colour `c` to exactly one neighbour `u` of `v`, then `φ[v ↦ c]` is proper on every edge
  except `uv`. (Hence in a 4-vertex-critical graph, such an edge `uv` is critical.)
* `Erdos944.cut_matrix_classification` — Theorem 4.3 core: among all 3×3 ℕ-matrices with entry sum
  6 (row-major lists in `comps 9 6`, completeness by `mem_comps`), exactly 21 have all six
  permutation-diagonal sums ≥ 2. Up to row/column permutation these are the five canonical types
  with row sums (6,0,0), (3,3,0), (4,1,1), (2,2,2)×2 (canonicalization checked separately in
  Python; the count and the membership certificate are what is machine-checked here).
  `Erdos944.matrix_mem_classification` bridges the genuine matrix form (sum over `Fin 3`,
  `∀ π : Equiv.Perm (Fin 3)` diagonal bound) to the enumerated list.
* `Erdos944.turan_count_shore` — Theorem 5.1 numeric core: for 2 ≤ a ≤ 7, ⌊a²/3⌋ < 3a − 3.
-/

namespace Erdos944

/-! ## Lemma 1.1 core -/

/-- If `φ` properly colours all edges not incident to `v` and exactly one neighbour `u` of `v` has
colour `c`, then the extension of `φ` to `v` by `c` is proper on every edge except `uv`. -/
theorem singleton_edge_critical {V : Type*} [DecidableEq V]
    (adj : V → V → Prop) (hsym : ∀ {a b}, adj a b → adj b a) (hirr : ∀ a, ¬ adj a a)
    (v u : V) (φ : V → Fin 3) (c : Fin 3)
    (huniq : ∀ w, adj v w → φ w = c → w = u)
    (hproper : ∀ a b, adj a b → a ≠ v → b ≠ v → φ a ≠ φ b) :
    ∀ a b, adj a b → ¬(a = v ∧ b = u) → ¬(a = u ∧ b = v) →
      Function.update φ v c a ≠ Function.update φ v c b := by
  intro a b hab hnab hnba
  by_cases hav : a = v
  · by_cases hbv : b = v
    · exact absurd hab (by rw [hav, hbv]; exact hirr v)
    · have hb : adj v b := by rw [← hav]; exact hab
      have hbc : φ b ≠ c := fun h => hnab ⟨hav, huniq b hb h⟩
      rw [hav, Function.update_self, Function.update_of_ne hbv]
      exact fun h => hbc h.symm
  · by_cases hbv : b = v
    · have ha : adj v a := hsym (by rw [← hbv]; exact hab)
      have hac : φ a ≠ c := fun h => hnba ⟨huniq a ha h, hbv⟩
      rw [hbv, Function.update_of_ne hav, Function.update_self]
      exact hac
    · rw [Function.update_of_ne hav, Function.update_of_ne hbv]
      exact hproper a b hab hav hbv

/-! ## Theorem 4.3 core: the 6-cut matrix classification -/

/-- All length-`k` lists of naturals with sum `n` (weak compositions of `n` into `k` parts). -/
def comps : ℕ → ℕ → List (List ℕ)
  | 0, 0 => [[]]
  | 0, _ + 1 => []
  | k + 1, n => (List.range (n + 1)).flatMap fun a => (comps k (n - a)).map (a :: ·)

/-- Completeness of the enumeration: `comps k n` contains exactly the length-`k` sum-`n` lists. -/
theorem mem_comps : ∀ k n l, l ∈ comps k n ↔ l.length = k ∧ l.sum = n := by
  intro k
  induction k with
  | zero =>
    intro n l
    match n with
    | 0 =>
      simp only [comps, List.mem_singleton]
      constructor
      · rintro rfl; exact ⟨rfl, rfl⟩
      · rintro ⟨hl, -⟩; exact List.length_eq_zero_iff.mp hl
    | m + 1 =>
      simp only [comps, List.not_mem_nil, false_iff, not_and]
      intro hl
      rw [List.length_eq_zero_iff.mp hl]
      simp
  | succ k ih =>
    intro n l
    simp only [comps, List.mem_flatMap, List.mem_map, List.mem_range]
    constructor
    · rintro ⟨a, ha, l', hl', rfl⟩
      obtain ⟨hlen, hsum⟩ := (ih (n - a) l').mp hl'
      refine ⟨by simp [hlen], ?_⟩
      simp only [List.sum_cons, hsum]
      omega
    · rintro ⟨hlen, hsum⟩
      match l with
      | [] => simp at hlen
      | a :: l' =>
        simp only [List.sum_cons] at hsum
        simp only [List.length_cons, Nat.add_left_inj] at hlen
        exact ⟨a, by omega, l', (ih (n - a) l').mpr ⟨hlen, by omega⟩, rfl⟩

/-- All six permutation-diagonal sums of the 3×3 matrix `[a,b,c; d,e,f; g,h,i]` are ≥ 2. -/
def diagOK : List ℕ → Bool
  | [a, b, c, d, e, f, g, h, i] =>
    decide (2 ≤ a + e + i) && decide (2 ≤ a + f + h) && decide (2 ≤ b + d + i) &&
    decide (2 ≤ b + f + g) && decide (2 ≤ c + d + h) && decide (2 ≤ c + e + g)
  | _ => false

set_option maxRecDepth 100000 in
/-- Exactly 21 of the 3003 sum-6 3×3 ℕ-matrices have all six permutation-diagonal sums ≥ 2. -/
theorem cut_matrix_classification : ((comps 9 6).filter diagOK).length = 21 := by decide

/-- Matrix form of Theorem 4.3 membership: any 3×3 ℕ-matrix with total sum 6 whose permutation
diagonals all have sum ≥ 2 appears (row-major) in the 21-element enumeration of
`cut_matrix_classification`. -/
theorem matrix_mem_classification (m : Fin 3 → Fin 3 → ℕ)
    (hsum : ∑ i : Fin 3, ∑ j : Fin 3, m i j = 6)
    (hdiag : ∀ π : Equiv.Perm (Fin 3), 2 ≤ ∑ i : Fin 3, m i (π i)) :
    [m 0 0, m 0 1, m 0 2, m 1 0, m 1 1, m 1 2, m 2 0, m 2 1, m 2 2] ∈
      (comps 9 6).filter diagOK := by
  have d1 : 2 ≤ m 0 0 + m 1 1 + m 2 2 := by
    simpa [Fin.sum_univ_three] using hdiag 1
  have d2 : 2 ≤ m 0 0 + m 1 2 + m 2 1 := by
    simpa [Fin.sum_univ_three, Equiv.swap_apply_def] using hdiag (Equiv.swap 1 2)
  have d3 : 2 ≤ m 0 1 + m 1 0 + m 2 2 := by
    simpa [Fin.sum_univ_three, Equiv.swap_apply_def] using hdiag (Equiv.swap 0 1)
  have d4 : 2 ≤ m 0 1 + m 1 2 + m 2 0 := by
    simpa [Fin.sum_univ_three, Equiv.Perm.mul_apply, Equiv.swap_apply_def] using
      hdiag (Equiv.swap 0 1 * Equiv.swap 1 2)
  have d5 : 2 ≤ m 0 2 + m 1 0 + m 2 1 := by
    simpa [Fin.sum_univ_three, Equiv.Perm.mul_apply, Equiv.swap_apply_def] using
      hdiag (Equiv.swap 1 2 * Equiv.swap 0 1)
  have d6 : 2 ≤ m 0 2 + m 1 1 + m 2 0 := by
    simpa [Fin.sum_univ_three, Equiv.swap_apply_def] using hdiag (Equiv.swap 0 2)
  rw [List.mem_filter]
  constructor
  · rw [mem_comps]
    refine ⟨rfl, ?_⟩
    have hs : m 0 0 + m 0 1 + m 0 2 + (m 1 0 + m 1 1 + m 1 2) + (m 2 0 + m 2 1 + m 2 2) = 6 := by
      simpa [Fin.sum_univ_three] using hsum
    simp only [List.sum_cons, List.sum_nil]
    omega
  · simp only [diagOK, Bool.and_eq_true, decide_eq_true_eq]
    omega

/-! ## Theorem 5.1 numeric core -/

theorem turan_count_shore : ∀ a : ℕ, 2 ≤ a → a ≤ 7 → a ^ 2 / 3 < 3 * a - 3 := by
  intro a h2 h7
  interval_cases a <;> norm_num

end Erdos944

#print axioms Erdos944.singleton_edge_critical
#print axioms Erdos944.mem_comps
#print axioms Erdos944.cut_matrix_classification
#print axioms Erdos944.matrix_mem_classification
#print axioms Erdos944.turan_count_shore
