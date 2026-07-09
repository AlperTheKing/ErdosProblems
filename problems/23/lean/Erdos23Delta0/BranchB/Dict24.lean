import Mathlib

/-!
# Branch-B layer 21: the typed 24-signature dictionary (2026-07-09)

First layer of the Branch-B stack (design: `BRANCH_B_LAYERS_V2_GPTPRO.md`; build order 21→26 feeding the
already-green `BranchB.ODLBridge`). Pure bookkeeping: every Branch-B atom's demand splits exactly into its
pure / HBD / CD parts, all nonnegative, with a signature index below 24. The sum-level split
(`dict24_sum_split`) and nonnegativity of the part-sums are what layer 25 (`BankedUPO`) consumes.
No graph theory, no row geometry, no bank theorem. No forbidden proof shortcuts;
axiom-probe expected `⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace BranchB
namespace Dict24

open Finset

variable {α : Type*}

/-- Per-atom dictionary data: signature index and the three demand components. -/
structure Dict24AtomData (α : Type*) where
  sig : α → ℕ
  demand : α → ℚ
  pure : α → ℚ
  hbd : α → ℚ
  cd : α → ℚ

/-- The checked dictionary conditions on an atom set `A`. -/
def Dict24Checked (A : Finset α) (D : Dict24AtomData α) : Prop :=
  ∀ a ∈ A, D.sig a < 24 ∧ 0 ≤ D.demand a ∧ 0 ≤ D.pure a ∧ 0 ≤ D.hbd a ∧ 0 ≤ D.cd a ∧
    D.demand a = D.pure a + D.hbd a + D.cd a

theorem dict24_sig_lt (A : Finset α) (D : Dict24AtomData α) (hD : Dict24Checked A D)
    {a : α} (ha : a ∈ A) : D.sig a < 24 :=
  (hD a ha).1

/-- **Sum-level split:** total demand = total pure + total HBD + total CD. -/
theorem dict24_sum_split (A : Finset α) (D : Dict24AtomData α) (hD : Dict24Checked A D) :
    (∑ a ∈ A, D.demand a)
      = (∑ a ∈ A, D.pure a) + (∑ a ∈ A, D.hbd a) + (∑ a ∈ A, D.cd a) := by
  calc (∑ a ∈ A, D.demand a)
      = ∑ a ∈ A, (D.pure a + D.hbd a + D.cd a) :=
        Finset.sum_congr rfl fun a ha => (hD a ha).2.2.2.2.2
    _ = _ := by rw [Finset.sum_add_distrib, Finset.sum_add_distrib]

/-- All three part-sums are nonnegative. -/
theorem dict24_part_sums_nonneg (A : Finset α) (D : Dict24AtomData α) (hD : Dict24Checked A D) :
    0 ≤ (∑ a ∈ A, D.pure a) ∧ 0 ≤ (∑ a ∈ A, D.hbd a) ∧ 0 ≤ (∑ a ∈ A, D.cd a) :=
  ⟨Finset.sum_nonneg fun a ha => (hD a ha).2.2.1,
   Finset.sum_nonneg fun a ha => (hD a ha).2.2.2.1,
   Finset.sum_nonneg fun a ha => (hD a ha).2.2.2.2.1⟩

theorem dict24_demand_sum_nonneg (A : Finset α) (D : Dict24AtomData α)
    (hD : Dict24Checked A D) : 0 ≤ ∑ a ∈ A, D.demand a :=
  Finset.sum_nonneg fun a ha => (hD a ha).2.1


end Dict24
end BranchB
end Erdos23Delta0
