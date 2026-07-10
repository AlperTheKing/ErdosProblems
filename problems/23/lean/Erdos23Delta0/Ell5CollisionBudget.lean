import Mathlib
import Erdos23Delta0.Ell5SupportFinset

/-!
# Collision budget for one-path-per-atom selections

This module records the exact finite counting step in the active-component
Hall attack. It deliberately separates the deterministic collision count
from the averaging argument used to choose one shortest row per bad edge.
-/

namespace Erdos23Delta0
namespace Ell5CollisionBudget

open Finset BigOperators

variable {V A Ω : Type*}
  [Fintype V] [DecidableEq V] [DecidableEq A]

/-- Atoms whose selected five-vertex row contains `v`. -/
def through (atoms : Finset A) (path : A → Finset V) (v : V) : Finset A :=
  atoms.filter fun a => v ∈ path a

/-- Union of all selected rows passing through `v`. -/
def fanUnion (atoms : Finset A) (path : A → Finset V) (v : V) : Finset V :=
  (through atoms path v).biUnion path

/-- Duplicate-slot count, embedded in `ℤ` to avoid truncated subtraction. -/
def collisionZ (atoms : Finset A) (path : A → Finset V) (v : V) : ℤ :=
  5 * (through atoms path v).card - (fanUnion atoms path v).card

/-- Per-path disjointness from `W` propagates to the whole fan union. -/
theorem disjoint_fanUnion
    (atoms : Finset A) (path : A → Finset V) (v : V) (W : Finset V)
    (hdisj : ∀ a ∈ atoms, v ∈ path a → Disjoint W (path a)) :
    Disjoint W (fanUnion atoms path v) := by
  rw [Finset.disjoint_left]
  intro x hxW hxFan
  rw [fanUnion, Finset.mem_biUnion] at hxFan
  obtain ⟨a, ha, hxa⟩ := hxFan
  have ha' := Finset.mem_filter.mp ha
  exact (Finset.disjoint_left.mp (hdisj a ha'.1 ha'.2)) hxW hxa

/-- The collision count pays every vertex in a disjoint neighbor set. This is
the pointwise inequality later averaged over all one-row-per-bad-edge choices. -/
theorem collisionZ_ge
    (atoms : Finset A) (path : A → Finset V) (v : V) (W : Finset V)
    (hdisj : Disjoint W (fanUnion atoms path v)) :
    (5 * (through atoms path v).card : ℤ) + W.card - Fintype.card V
      ≤ collisionZ atoms path v := by
  have hsub : W ∪ fanUnion atoms path v ⊆ (Finset.univ : Finset V) :=
    fun _ _ => Finset.mem_univ _
  have hcard := Finset.card_le_card hsub
  rw [Finset.card_union_of_disjoint hdisj, Finset.card_univ] at hcard
  unfold collisionZ
  omega

/-- Five-vertex selected rows make the duplicate-slot count nonnegative. -/
theorem collisionZ_nonneg
    (atoms : Finset A) (path : A → Finset V) (v : V)
    (hfive : ∀ a ∈ atoms, (path a).card = 5) :
    0 ≤ collisionZ atoms path v := by
  have hcard :
      (fanUnion atoms path v).card ≤ 5 * (through atoms path v).card := by
    calc
      (fanUnion atoms path v).card
          ≤ ∑ a ∈ through atoms path v, (path a).card := by
              exact Finset.card_biUnion_le
      _ = ∑ _a ∈ through atoms path v, 5 := by
            apply Finset.sum_congr rfl
            intro a ha
            exact hfive a (Finset.mem_filter.mp ha).1
      _ = 5 * (through atoms path v).card := by
            simp [mul_comm]
  unfold collisionZ
  omega

/-- A finite average lower bound has a deterministic witness. This is the
denominator-free selection step used after summing collision counts over all
tuples of shortest-row choices. -/
theorem exists_ge_of_card_mul_le_sum
    [Fintype Ω] [Nonempty Ω] (score : Ω → ℚ) (lower : ℚ)
    (havg : (Fintype.card Ω : ℚ) * lower ≤ ∑ ω, score ω) :
    ∃ ω, lower ≤ score ω := by
  by_contra h
  push_neg at h
  have hlt : (∑ ω, score ω) < ∑ _ω : Ω, lower := by
    exact Finset.sum_lt_sum_of_nonempty Finset.univ_nonempty
      (fun ω _ => h ω)
  have hconst : (∑ _ω : Ω, lower) = (Fintype.card Ω : ℚ) * lower := by
    simp [mul_comm]
  rw [hconst] at hlt
  exact (not_lt_of_ge havg) hlt

end Ell5CollisionBudget
end Erdos23Delta0
