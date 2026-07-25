/-
  Erdős Problem #30 — Ordered-Element Combinatorial Infrastructure
  ================================================================

  Local, axiom-free combinatorics on the increasing enumeration of a
  `Finset ℕ`. Originally extracted from
  `scratch/Erdos30_IntervalOccupancyTarget.lean` once it stabilized.

  What this file gives the rest of the Erdős portfolio:

  * `intervalSlice`, `intervalLength`, `intervalOccupancyDiscrepancy` —
    division-free integer vocabulary for prefix / interval counting.
  * `DenseSidonAtScale`, `IsMacroscopicInterval`,
    `IsMacroscopicInitialSegment` — deficiency-parameterized packages for
    dense Sidon rigidity statements.
  * `orderedElements`, `orderedElement` and the sorted-list lemmas about
    them.
  * `ordered_prefix_card_target` — the combinatorial bridge
    `|A ∩ [0, aᵢ]| = i + 1`. This is the identity that turns an ordered-
    element bound into a quantile / prefix-count statement.

  Zero axioms. Zero imports from external-theorem interfaces. Eligible for
  `COMPILED` status in D1 on its own.

  **Lean version**: leanprover/lean4:v4.24.0
  **Mathlib version**: f897ebcf72cd16f89ab4577d0c826cd14afaafc7
-/

import Mathlib
import Erdos30_Sidon_Defs

open Finset Nat

namespace Erdos.Sidon

/-! ### Interval counting vocabulary -/

/-- Elements of `A` that lie in the interval `[u, v]`. -/
def intervalSlice (A : Finset ℕ) (u v : ℕ) : Finset ℕ :=
  A.filter (fun a => u ≤ a ∧ a ≤ v)

/-- Cardinality of the integer interval `[u, v]`. When `u ≤ v`, this is `v + 1 - u`. -/
def intervalLength (u v : ℕ) : ℕ :=
  v + 1 - u

/-- Scaled occupancy discrepancy of `A` on `[u, v]`.

`intervalSlice.card * n` is compared against `A.card * intervalLength`; this
avoids division and keeps the statement in natural-number arithmetic, with the
absolute value taken afterwards in `ℤ`.
-/
def intervalOccupancyDiscrepancy (A : Finset ℕ) (n u v : ℕ) : ℤ :=
  ((intervalSlice A u v).card : ℤ) * n - (A.card : ℤ) * intervalLength u v

/-! ### Deficiency-parameterized packages -/

/-- Dense finite Sidon package at deficiency `L` from the `sqrt n` scale. -/
def DenseSidonAtScale (A : Finset ℕ) (n L : ℕ) : Prop :=
  IsSidonSet A ∧ A ⊆ Finset.range (n + 1) ∧ A.card + L = Nat.sqrt n

/-- Macroscopic interval condition: length at least a quarter of the ambient range.

This exact threshold is a placeholder for the first formal target. If the proof
works, the ratio can be sharpened later by amendment rather than by changing the
shape of the statement.
-/
def IsMacroscopicInterval (n u v : ℕ) : Prop :=
  u ≤ v ∧ v ≤ n ∧ 4 * intervalLength u v ≥ n

/-- Macroscopic initial-segment condition for `[0, t]`. -/
def IsMacroscopicInitialSegment (n t : ℕ) : Prop :=
  t ≤ n ∧ 4 * (t + 1) ≥ n

/-! ### Ordered enumeration of a `Finset ℕ` -/

/-- The increasing list of elements of `A`. -/
def orderedElements (A : Finset ℕ) : List ℕ :=
  A.sort (· ≤ ·)

/-- The `i`-th element of `A` in increasing order. -/
def orderedElement (A : Finset ℕ) (i : Fin A.card) : ℕ :=
  (orderedElements A).get ⟨i.1, by simpa [orderedElements] using i.2⟩

/-- The sorted enumeration is weakly increasing. -/
theorem orderedElements_sorted_le (A : Finset ℕ) :
    List.Sorted (· ≤ ·) (orderedElements A) := by
  simpa [orderedElements] using Finset.sort_sorted (· ≤ ·) A

/-- Alias for `orderedElements_sorted_le` kept for naming compatibility. -/
theorem orderedElements_sorted (A : Finset ℕ) :
    List.Sorted (· ≤ ·) (orderedElements A) := by
  exact orderedElements_sorted_le A

/-- The sorted enumeration is strictly increasing because the finset has no duplicates. -/
theorem orderedElements_sorted_lt (A : Finset ℕ) :
    List.Sorted (· < ·) (orderedElements A) := by
  simpa [orderedElements] using Finset.sort_sorted_lt A

/-- The sorted enumeration has the expected length. -/
theorem length_orderedElements (A : Finset ℕ) :
    (orderedElements A).length = A.card := by
  simpa [orderedElements] using (Finset.length_sort (· ≤ ·) (s := A))

/-- Every indexed ordered element is genuinely an element of the finset. -/
theorem orderedElement_mem (A : Finset ℕ) (i : Fin A.card) :
    orderedElement A i ∈ A := by
  have hmemList : orderedElement A i ∈ orderedElements A := by
    unfold orderedElement
    exact List.get_mem _ _
  exact (Finset.mem_sort (· ≤ ·)).mp hmemList

/-- The `i`-th ordered element lies in the prefix of length `i+1`. -/
theorem orderedElement_mem_take (A : Finset ℕ) (i : Fin A.card) :
    orderedElement A i ∈ (orderedElements A).take (i.1 + 1) := by
  apply List.mem_iff_getElem.mpr
  refine ⟨i.1, ?_, ?_⟩
  · simpa [List.length_take, orderedElements] using Nat.lt_succ_self i.1
  · simpa [orderedElement]

/-- Any element in the suffix past position `i` is strictly larger than the `i`-th ordered element. -/
theorem orderedElement_lt_of_mem_drop (A : Finset ℕ) (i : Fin A.card) {y : ℕ}
    (hy : y ∈ (orderedElements A).drop (i.1 + 1)) :
    orderedElement A i < y := by
  have hs : List.Sorted (· < ·) (orderedElements A) := orderedElements_sorted_lt A
  have hx : orderedElement A i ∈ (orderedElements A).take (i.1 + 1) := orderedElement_mem_take A i
  exact hs.rel_of_mem_take_of_mem_drop hx hy

/-! ### Combinatorial bridge to prefix counting -/

/-- Trivial prefix-discrepancy bound.

This is the local sanity anchor for `intervalOccupancyDiscrepancy` on initial
segments. It is not asymptotically sharp, but it gives a fully axiom-free floor
above which any genuine rigidity theorem must improve.
-/
theorem prefix_discrepancy_trivial (A : Finset ℕ) (n t : ℕ) :
    Int.natAbs (intervalOccupancyDiscrepancy A n 0 t)
      ≤ (intervalSlice A 0 t).card * n + A.card * (t + 1) := by
  rw [intervalOccupancyDiscrepancy, intervalLength]
  have hleft :
      Int.natAbs (((intervalSlice A 0 t).card : ℤ) * n) =
        (intervalSlice A 0 t).card * n := by
    simpa using Int.natAbs_ofNat ((intervalSlice A 0 t).card * n)
  have hright :
      Int.natAbs (-((A.card : ℤ) * (t + 1))) =
        A.card * (t + 1) := by
    rw [Int.natAbs_neg]
    simpa using Int.natAbs_ofNat (A.card * (t + 1))
  calc
    Int.natAbs (((intervalSlice A 0 t).card : ℤ) * n - (A.card : ℤ) * (t + 1))
      ≤ Int.natAbs (((intervalSlice A 0 t).card : ℤ) * n) +
          Int.natAbs (-((A.card : ℤ) * (t + 1))) := by
            simpa [sub_eq_add_neg] using
              Int.natAbs_add_le (((intervalSlice A 0 t).card : ℤ) * n)
                (-((A.card : ℤ) * (t + 1)))
    _ = (intervalSlice A 0 t).card * n + A.card * (t + 1) := by
      simp [hleft, hright]

/-- The initial segment cut at the `i`-th ordered element has exactly `i+1` points.

This is the identity that turns an ordered-element bound into a quantile /
prefix-count statement: if a theorem controls `aᵢ` in terms of `i + 1`, this
lemma rewrites `i + 1` as `|A ∩ [0, aᵢ]|` without approximation.

Proof structure:
1. `orderedElements_sorted_le` / `_lt`,
2. finset nodup / sorted-list uniqueness,
3. `intervalSlice A 0 (orderedElement A i)` matches the prefix of the sorted
   enumeration cut at `orderedElement A i`.
-/
theorem ordered_prefix_card_target (A : Finset ℕ) (i : Fin A.card) :
    (intervalSlice A 0 (orderedElement A i)).card = i.1 + 1
    := by
  let l := orderedElements A
  let a := orderedElement A i
  let p : ℕ → Bool := fun x => decide (x ≤ a)
  have hEqFinset : (l.filter p).toFinset = intervalSlice A 0 a := by
    ext x
    simp [l, a, p, intervalSlice, orderedElements]
  have hcardFilter : (l.filter p).length = i.1 + 1 := by
    have hsplit := List.take_append_drop (i.1 + 1) l
    rw [← List.countP_eq_length_filter, ← hsplit, List.countP_append]
    have hprefix : (List.take (i.1 + 1) l).countP p = (List.take (i.1 + 1) l).length := by
      rw [List.countP_eq_length]
      intro x hx
      obtain ⟨j, hj, rfl⟩ := List.mem_iff_getElem.mp hx
      have hja : j < i.1 + 1 := by
        exact (by simpa [List.length_take, l, orderedElements] using hj : j < i.1 + 1 ∧ j < A.card).1
      have hji : j ≤ i.1 := Nat.lt_succ_iff.mp hja
      have hs : List.Sorted (· ≤ ·) l := by
        simpa [l, orderedElements] using orderedElements_sorted_le A
      have hjl : j < l.length := lt_of_lt_of_le hja (Nat.succ_le_of_lt (by simpa [l, orderedElements] using i.2))
      have hile : i.1 < l.length := by simpa [l, orderedElements] using i.2
      have hmono : l.get ⟨j, hjl⟩ ≤ l.get ⟨i.1, hile⟩ := by
        exact hs.rel_get_of_le hji
      simpa [p, a, orderedElement, l] using hmono
    have hsuffix : (List.drop (i.1 + 1) l).countP p = 0 := by
      rw [List.countP_eq_zero]
      intro x hx
      have hlt : a < x := by
        simpa [l, a] using orderedElement_lt_of_mem_drop A i hx
      simp [p, Nat.not_le_of_lt hlt]
    rw [hprefix, hsuffix, List.length_take]
    simp [l, orderedElements, Nat.succ_le_of_lt i.2]
  have hnodup : (l.filter p).Nodup := (Finset.sort_nodup (· ≤ ·) A).filter _
  have hcardToFinset : ((l.filter p).toFinset).card = (l.filter p).length := by
    nth_rewrite 1 [← List.toFinset_eq hnodup]
    simp
  calc
    (intervalSlice A 0 a).card = ((l.filter p).toFinset).card := by rw [← hEqFinset]
    _ = (l.filter p).length := hcardToFinset
    _ = i.1 + 1 := hcardFilter

end Erdos.Sidon
