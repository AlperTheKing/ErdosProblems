import Mathlib

/-!
# Branch-B layer 23: CD telescope bookkeeping

This layer is the explicit start/finish form of the cancellation-difference
telescope.  The geometric layers supply the step equalities; here we only use
the checked endpoint identity `start = finish + gain` and nonnegativity of
`gain`.
-/

namespace Erdos23Delta0
namespace BranchB
namespace CDTelescope

open Finset

variable {α : Type*}

/-- Per-atom CD telescope endpoint data. -/
structure CDTelescopeData (α : Type*) where
  start : α → ℚ
  finish : α → ℚ
  gain : α → ℚ

/-- Checked endpoint form: each atom has nonnegative gain and start is finish plus gain. -/
def CDTelescopeChecked (A : Finset α) (D : CDTelescopeData α) : Prop :=
  ∀ a ∈ A, 0 ≤ D.gain a ∧ D.start a = D.finish a + D.gain a

theorem cd_atom_sound (A : Finset α) (D : CDTelescopeData α)
    (hD : CDTelescopeChecked A D) {a : α} (ha : a ∈ A) :
    D.finish a ≤ D.start a := by
  have hgain : 0 ≤ D.gain a := (hD a ha).1
  have hstart : D.start a = D.finish a + D.gain a := (hD a ha).2
  linarith

theorem cd_sum_start_eq_finish_plus_gain (A : Finset α) (D : CDTelescopeData α)
    (hD : CDTelescopeChecked A D) :
    (∑ a ∈ A, D.start a) =
      (∑ a ∈ A, D.finish a) + ∑ a ∈ A, D.gain a := by
  calc
    (∑ a ∈ A, D.start a)
        = ∑ a ∈ A, (D.finish a + D.gain a) := by
          exact Finset.sum_congr rfl fun a ha => (hD a ha).2
    _ = (∑ a ∈ A, D.finish a) + ∑ a ∈ A, D.gain a := by
          rw [Finset.sum_add_distrib]

/-- **CD telescope soundness:** total finish is bounded by total start. -/
theorem cd_telescope_sound (A : Finset α) (D : CDTelescopeData α)
    (hD : CDTelescopeChecked A D) :
    (∑ a ∈ A, D.finish a) ≤ ∑ a ∈ A, D.start a := by
  rw [cd_sum_start_eq_finish_plus_gain A D hD]
  exact le_add_of_nonneg_right (Finset.sum_nonneg fun a ha => (hD a ha).1)

theorem cd_gain_sum_nonneg (A : Finset α) (D : CDTelescopeData α)
    (hD : CDTelescopeChecked A D) :
    0 ≤ ∑ a ∈ A, D.gain a :=
  Finset.sum_nonneg fun a ha => (hD a ha).1


end CDTelescope
end BranchB
end Erdos23Delta0
