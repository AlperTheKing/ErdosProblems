import Erdos23Delta0.Ell5ActiveComponentBankHall

/-!
# Zero-load active-component Hall branch

The collision-transfer matching is only one sufficient construction for the
full-bank flow.  If the canonical active-component partition already makes
every non-Door off-support block load zero, the actual weighted Hall condition
is immediate.  This branch is important for inactive-component examples such
as the R22 double-star family: their unrestricted collision matching may fail
even though the full-bank primal has no non-Door demand to route.
-/

namespace Erdos23Delta0
namespace Gamma
namespace ActiveComponentZeroLoadHall

open Finset
open Ell5ActiveComponentFlow
open Ell5ActiveComponentBankHall

variable {V Comp JT : Type*} [DecidableEq V]
  [Fintype Comp] [DecidableEq Comp] [Fintype JT]

/-- Pointwise zero demand implies every weighted Hall shore inequality. -/
theorem activeComponentBankHall_of_demand_zero
    [Fintype V]
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (s : V → Bool) (C : Finset V)
    (comp : V → Comp) (active : Comp → Bool)
    (O D : Finset (Sym2 V))
    (incBase : Sym2 V → JT → Prop)
    (kapBase : JT → ℚ)
    (hzero : ∀ e : E0 O D, demand G s C comp active e = 0)
    (hkap : ∀ j, 0 ≤ kapBase j) :
    ActiveComponentBankHall G s C comp active O D incBase kapBase := by
  classical
  intro T
  have hlhs : (∑ e ∈ T, demand G s C comp active e) = 0 := by
    apply Finset.sum_eq_zero
    intro e he
    exact hzero e
  rw [hlhs]
  exact Finset.sum_nonneg fun j hj => hkap j

/-- Graph-facing form: it is enough to show that each relevant block load is
zero before packaging it as the `E0` subtype demand. -/
theorem activeComponentBankHall_of_blockLoad_zero
    [Fintype V]
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (s : V → Bool) (C : Finset V)
    (comp : V → Comp) (active : Comp → Bool)
    (O D : Finset (Sym2 V))
    (incBase : Sym2 V → JT → Prop)
    (kapBase : JT → ℚ)
    (hzero : ∀ e, e ∈ O → e ∉ D →
      Ell5BlockSingleton.blockLoad G s C (componentOwner comp active) e = 0)
    (hkap : ∀ j, 0 ≤ kapBase j) :
    ActiveComponentBankHall G s C comp active O D incBase kapBase := by
  apply activeComponentBankHall_of_demand_zero
    G s C comp active O D incBase kapBase
  · intro e
    simpa [demand] using hzero e.1 e.2.1 e.2.2
  · exact hkap

end ActiveComponentZeroLoadHall
end Gamma
end Erdos23Delta0
