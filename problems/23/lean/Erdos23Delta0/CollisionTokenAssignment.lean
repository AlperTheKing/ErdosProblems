import Erdos23Delta0.EndpointReserveHall

/-!
# Collision reserve to legal bank tokens

This module isolates the sole semantic obligation left by the collision-reserve
route. A provider must turn a pointwise reserve into nonnegative mass on finite
tokens, respect every token capacity globally, and prove endpoint legality.

The theorem below converts such a provider into exact subset Hall inequalities.
It does not assert that a provider exists.
-/

namespace Erdos23Delta0
namespace CollisionTokenAssignment

open scoped BigOperators
open EndpointReserveHall

variable {V JT : Type*} [Fintype V] [DecidableEq V]
  [Fintype JT] [DecidableEq JT]

attribute [local instance] Classical.propDecidable

/-- A graph-semantic collision reserve assignment. Positive mass at an endpoint
may be offered to every relevant edge incident with that endpoint. -/
structure Assignment
    (E : Finset (Sym2 V)) (legal : Sym2 V → JT → Prop)
    (cap : JT → ℚ) (need : V → ℚ) where
  eta : V → JT → ℚ
  eta_nonneg : ∀ x t, 0 ≤ eta x t
  no_double_spend : ∀ t, (∑ x : V, eta x t) ≤ cap t
  pays_need : ∀ x, need x ≤ ∑ t : JT, eta x t
  legal_at_endpoint :
    ∀ x t, 0 < eta x t → ∀ e ∈ E, x ∈ e → legal e t

/-- Vertices used by a selected edge subfamily. -/
noncomputable def usedEndpoints (T : Finset (Sym2 V)) : Finset V :=
  Finset.univ.filter fun x => ∃ e ∈ T, x ∈ e

/-- Actual legal token neighbors of a selected edge subfamily. -/
noncomputable def usedTokens
    (T : Finset (Sym2 V)) (legal : Sym2 V → JT → Prop) : Finset JT :=
  Finset.univ.filter fun t => ∃ e ∈ T, legal e t

/-- A collision-token assignment plus ordinary endpoint slack proves the
weighted Hall inequality for every selected edge subfamily. -/
theorem hall_of_assignment
    (E T : Finset (Sym2 V))
    (slack need : V → ℚ) (legal : Sym2 V → JT → Prop) (cap : JT → ℚ)
    (hT : T ⊆ E) (hends : EndpointHalfExact E)
    (hneed : ∀ x, halfDegree E x ≤ slack x + need x)
    (A : Assignment E legal cap need) :
    (T.card : ℚ) ≤
      (∑ x ∈ usedEndpoints T, slack x) +
        ∑ t ∈ usedTokens T legal, cap t := by
  classical
  apply endpointReserveHallOn E T (usedEndpoints T) (usedTokens T legal)
    slack A.eta cap hT hends A.eta_nonneg A.no_double_spend
  · intro x
    calc
      halfDegree E x ≤ slack x + need x := hneed x
      _ ≤ slack x + ∑ t : JT, A.eta x t := by
        simpa [add_comm] using
          (add_le_add_left (A.pays_need x) (slack x))
  · intro e heT x hxe
    simp only [usedEndpoints, Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨e, heT, hxe⟩
  · intro x hx t hpos
    simp only [usedEndpoints, Finset.mem_filter, Finset.mem_univ, true_and] at hx
    obtain ⟨e, heT, hxe⟩ := hx
    have hlegal : legal e t :=
      A.legal_at_endpoint x t hpos e (hT heT) hxe
    simp only [usedTokens, Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨e, heT, hlegal⟩

#print axioms hall_of_assignment

end CollisionTokenAssignment
end Erdos23Delta0
