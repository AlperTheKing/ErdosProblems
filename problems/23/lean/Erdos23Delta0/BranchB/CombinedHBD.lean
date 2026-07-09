import Mathlib

/-!
# Branch-B layer 22: combined HBD single-spend ledger

This is pure bookkeeping.  A ledger gives nonnegative per-atom demands,
nonnegative capacities, nonnegative transfer weights `q a t`, and nonnegative
unused capacity at each token.  If every demand is exactly decomposed into
token transfers and every capacity is exactly transfer-in plus unused, total
demand is bounded by total capacity.
-/

namespace Erdos23Delta0
namespace BranchB
namespace CombinedHBD

open Finset

variable {α τ : Type*} [DecidableEq τ]

/-- Per-atom and per-token data for the HBD ledger. -/
structure HBDChargeData (α τ : Type*) where
  demand : α → ℚ
  cap : τ → ℚ
  q : α → τ → ℚ
  unused : τ → ℚ

/-- Exact ledger conditions on atom set `A` and token set `T`. -/
def HBDLedgerChecked (A : Finset α) (T : Finset τ) (D : HBDChargeData α τ) : Prop :=
  (∀ a ∈ A, 0 ≤ D.demand a) ∧
  (∀ t ∈ T, 0 ≤ D.cap t) ∧
  (∀ a ∈ A, ∀ t ∈ T, 0 ≤ D.q a t) ∧
  (∀ t ∈ T, 0 ≤ D.unused t) ∧
  (∀ a ∈ A, D.demand a = ∑ t ∈ T, D.q a t) ∧
  (∀ t ∈ T, D.cap t = (∑ a ∈ A, D.q a t) + D.unused t)

theorem hbd_demand_sum_eq_q_sum (A : Finset α) (T : Finset τ)
    (D : HBDChargeData α τ) (hD : HBDLedgerChecked A T D) :
    (∑ a ∈ A, D.demand a) = ∑ a ∈ A, ∑ t ∈ T, D.q a t := by
  exact Finset.sum_congr rfl fun a ha => (hD.2.2.2.2.1 a ha)

theorem hbd_capacity_sum_eq_q_sum_plus_unused (A : Finset α) (T : Finset τ)
    (D : HBDChargeData α τ) (hD : HBDLedgerChecked A T D) :
    (∑ t ∈ T, D.cap t) =
      (∑ a ∈ A, ∑ t ∈ T, D.q a t) + ∑ t ∈ T, D.unused t := by
  calc
    (∑ t ∈ T, D.cap t)
        = ∑ t ∈ T, ((∑ a ∈ A, D.q a t) + D.unused t) := by
          exact Finset.sum_congr rfl fun t ht => (hD.2.2.2.2.2 t ht)
    _ = (∑ t ∈ T, ∑ a ∈ A, D.q a t) + ∑ t ∈ T, D.unused t := by
          rw [Finset.sum_add_distrib]
    _ = (∑ a ∈ A, ∑ t ∈ T, D.q a t) + ∑ t ∈ T, D.unused t := by
          rw [Finset.sum_comm]

/-- **HBD ledger soundness:** total HBD demand is paid by total capacity. -/
theorem hbd_ledger_sound (A : Finset α) (T : Finset τ)
    (D : HBDChargeData α τ) (hD : HBDLedgerChecked A T D) :
    (∑ a ∈ A, D.demand a) ≤ ∑ t ∈ T, D.cap t := by
  rw [hbd_demand_sum_eq_q_sum A T D hD,
      hbd_capacity_sum_eq_q_sum_plus_unused A T D hD]
  exact le_add_of_nonneg_right (Finset.sum_nonneg fun t ht => hD.2.2.2.1 t ht)

theorem hbd_capacity_sum_nonneg (A : Finset α) (T : Finset τ)
    (D : HBDChargeData α τ) (hD : HBDLedgerChecked A T D) :
    0 ≤ ∑ t ∈ T, D.cap t :=
  Finset.sum_nonneg fun t ht => hD.2.1 t ht


end CombinedHBD
end BranchB
end Erdos23Delta0
