import Erdos23Delta0.Gamma.MinimumCollisionGlobalHallReduction

/-!
# Optimal partial flows for the global soft-cap Hall system

`IntegralGroupedCapFlow` represents the zero-defect endpoint.  Rotor and
minimum-defect arguments also need an exact witness at positive defect.  This
module records such a witness without reintroducing component coherence or
active-scoped demand: it is a partial injection on the real obligations, with
the literal unit key capacities, the aggregate capacity two on each active
edge, and an optimality equation against the existing grouped Hall defect.
-/

namespace Erdos23Delta0
namespace Gamma
namespace OptimalGroupedCapPartialFlow

open CheckedSoftCollisionTwoCover
open MinimumCollisionGlobalHallReduction

universe uObligation uEdge uBase

abbrev PhysicalKey
    (ActiveEdge : Type uEdge) (DirectBase : Type uBase) :=
  EdgeCappedPhysicalKey ActiveEdge DirectBase

/-- Number of selected real demands assigned inside one active four-key
block.  The definition is noncomputable only because the carrier types are
abstract finite types. -/
noncomputable def activeLoad
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype Obligation] [DecidableEq Obligation]
    [Fintype ActiveEdge] [Fintype DirectBase]
    (matched : Finset Obligation)
    (assign : {d // d ∈ matched} → PhysicalKey ActiveEdge DirectBase)
    (edge : ActiveEdge) : Nat := by
  classical
  exact (Finset.univ.filter fun d : {d // d ∈ matched} =>
    KeyOnActiveEdge edge (assign d)).card

/-- An exact maximum partial flow in the adaptive grouped-cap model. -/
structure Flow
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype Obligation] [DecidableEq Obligation]
    [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation → PhysicalKey ActiveEdge DirectBase → Prop) where
  matched : Finset Obligation
  assign : {d // d ∈ matched} → PhysicalKey ActiveEdge DirectBase
  injective : Function.Injective assign
  supported : ∀ d, Eligible d.1 (assign d)
  active_load_le_two : ∀ edge : ActiveEdge,
    activeLoad matched assign edge ≤ 2
  optimal : Fintype.card Obligation - matched.card = hallDefect Eligible

namespace Flow

variable {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
variable {DirectBase : Type uBase}
variable [Fintype Obligation] [DecidableEq Obligation]
variable [Fintype ActiveEdge] [Fintype DirectBase]
variable {Eligible : Obligation → PhysicalKey ActiveEdge DirectBase → Prop}

variable (F : Flow Eligible)

/-- Number of real collision obligations left unmatched by the exact flow. -/
def unmatchedCount : Nat :=
  Fintype.card Obligation - F.matched.card

/-- A literal physical key is occupied by the selected optimal flow. -/
def Uses (key : PhysicalKey ActiveEdge DirectBase) : Prop :=
  ∃ d : {d // d ∈ F.matched}, F.assign d = key

/-- Both half keys over one oriented/direct base are occupied. -/
def BothHalvesUsed
    (base : (ActiveEdge × Fin 2) ⊕ DirectBase) : Prop :=
  ∀ half : Fin 2, F.Uses (base, half)

theorem matched_card_le :
    F.matched.card ≤ Fintype.card Obligation := by
  classical
  simpa using Finset.card_le_univ F.matched

theorem unmatchedCount_eq_hallDefect :
    F.unmatchedCount = hallDefect Eligible :=
  F.optimal

theorem assign_supported (d : {d // d ∈ F.matched}) :
    Eligible d.1 (F.assign d) :=
  F.supported d

theorem assigned_demand_unique
    {d e : {d // d ∈ F.matched}}
    (h : F.assign d = F.assign e) : d = e :=
  F.injective h

theorem activeLoad_le_two (edge : ActiveEdge) :
    activeLoad F.matched F.assign edge ≤ 2 :=
  F.active_load_le_two edge

/-- The global Hall defect is exactly one; this is not R55's local residual unit-core equation. -/
def GlobalDefectOne : Prop :=
  F.unmatchedCount = 1

theorem hallDefect_eq_one (h : F.GlobalDefectOne) :
    hallDefect Eligible = 1 := by
  rw [← F.unmatchedCount_eq_hallDefect]
  exact h

/-- Saturating both physical halves really occupies two distinct demands. -/
theorem exists_distinct_demands_of_bothHalvesUsed
    (base : (ActiveEdge × Fin 2) ⊕ DirectBase)
    (h : F.BothHalvesUsed base) :
    ∃ d0 d1 : {d // d ∈ F.matched},
      d0 ≠ d1 ∧
      F.assign d0 = (base, (0 : Fin 2)) ∧
      F.assign d1 = (base, (1 : Fin 2)) := by
  obtain ⟨d0, hd0⟩ := h 0
  obtain ⟨d1, hd1⟩ := h 1
  refine ⟨d0, d1, ?_, hd0, hd1⟩
  intro heq
  subst d1
  have hkey :
      (base, (0 : Fin 2)) = (base, (1 : Fin 2)) :=
    hd0.symm.trans hd1
  have hhalf := congrArg Prod.snd hkey
  simp at hhalf

end Flow

#print axioms Flow.unmatchedCount_eq_hallDefect
#print axioms Flow.hallDefect_eq_one
#print axioms Flow.exists_distinct_demands_of_bothHalvesUsed

end OptimalGroupedCapPartialFlow
end Gamma
end Erdos23Delta0
