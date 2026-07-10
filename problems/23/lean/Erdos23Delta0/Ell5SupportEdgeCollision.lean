import Mathlib

/-!
# Genuine support-edge collision budget

The vertex-pair collision count includes a degenerate self-fiber.  This module
records a cleaner count: repeated incidences on actual support edges.  Every
such repetition joins two selected rows on two distinct adjacent vertices.
-/

namespace Erdos23Delta0
namespace Ell5SupportEdgeCollision

open Finset BigOperators

variable {A E : Type*} [DecidableEq A] [DecidableEq E]

/-- Selected atoms whose chosen row uses the support edge `e`. -/
def edgeThrough (atoms : Finset A) (pathEdges : A → Finset E) (e : E) : Finset A :=
  atoms.filter fun a => e ∈ pathEdges a

/-- Positive duplicate count on genuine support-edge fibers. -/
def collisionZ (atoms : Finset A) (pathEdges : A → Finset E) (F : Finset E) : ℤ :=
  F.sum fun e => ((edgeThrough atoms pathEdges e).card - 1 : ℕ)

/-- Signed incidence excess before truncating unused support edges at zero. -/
def rawCollisionZ (atoms : Finset A) (pathEdges : A → Finset E) (F : Finset E) : ℤ :=
  F.sum fun e => ((edgeThrough atoms pathEdges e).card : ℤ) - 1

theorem rawCollisionZ_le_collisionZ
    (atoms : Finset A) (pathEdges : A → Finset E) (F : Finset E) :
    rawCollisionZ atoms pathEdges F ≤ collisionZ atoms pathEdges F := by
  unfold rawCollisionZ collisionZ
  push_cast
  exact Finset.sum_le_sum fun e he => by omega

theorem sum_card_edgeThrough_eq
    (atoms : Finset A) (pathEdges : A → Finset E) (F : Finset E)
    (hsub : ∀ a ∈ atoms, pathEdges a ⊆ F) :
    F.sum (fun e => (edgeThrough atoms pathEdges e).card) =
      atoms.sum (fun a => (pathEdges a).card) := by
  calc
    F.sum (fun e => (edgeThrough atoms pathEdges e).card) =
        F.sum (fun e => atoms.sum fun a => if e ∈ pathEdges a then 1 else 0) := by
          apply Finset.sum_congr rfl
          intro e he
          simp [edgeThrough]
    _ = atoms.sum (fun a => F.sum fun e => if e ∈ pathEdges a then 1 else 0) := by
          exact Finset.sum_comm
    _ = atoms.sum (fun a => (pathEdges a).card) := by
          apply Finset.sum_congr rfl
          intro a ha
          have hinter : F ∩ pathEdges a = pathEdges a :=
            Finset.inter_eq_right.mpr (hsub a ha)
          simpa [hinter]

theorem rawCollisionZ_eq
    (atoms : Finset A) (pathEdges : A → Finset E) (F : Finset E)
    (hsub : ∀ a ∈ atoms, pathEdges a ⊆ F) :
    rawCollisionZ atoms pathEdges F =
      (atoms.sum (fun a => ((pathEdges a).card : ℤ))) - F.card := by
  unfold rawCollisionZ
  rw [Finset.sum_sub_distrib]
  have hcountZ :
      F.sum (fun e => ((edgeThrough atoms pathEdges e).card : ℤ)) =
        atoms.sum (fun a => ((pathEdges a).card : ℤ)) := by
    exact_mod_cast sum_card_edgeThrough_eq atoms pathEdges F hsub
  rw [hcountZ]
  simp

/-- In a defect-one support core, one four-edge row per atom creates at least
`3m+1` genuine support-edge repetitions. -/
theorem collisionZ_ge_three_mul_add_one
    (atoms : Finset A) (pathEdges : A → Finset E) (F : Finset E)
    (hsub : ∀ a ∈ atoms, pathEdges a ⊆ F)
    (hfour : ∀ a ∈ atoms, (pathEdges a).card = 4)
    (hdefect : F.card + 1 = atoms.card) :
    3 * (atoms.card : ℤ) + 1 ≤ collisionZ atoms pathEdges F := by
  have hraw := rawCollisionZ_le_collisionZ atoms pathEdges F
  rw [rawCollisionZ_eq atoms pathEdges F hsub] at hraw
  have hsum :
      atoms.sum (fun a => ((pathEdges a).card : ℤ)) =
        4 * (atoms.card : ℤ) := by
    calc
      atoms.sum (fun a => ((pathEdges a).card : ℤ)) =
          atoms.sum (fun _a => (4 : ℤ)) := by
            apply Finset.sum_congr rfl
            intro a ha
            exact_mod_cast hfour a ha
      _ = 4 * (atoms.card : ℤ) := by simp [mul_comm]
  rw [hsum] at hraw
  have hdefectZ : (F.card : ℤ) + 1 = (atoms.card : ℤ) := by
    exact_mod_cast hdefect
  omega

end Ell5SupportEdgeCollision
end Erdos23Delta0
