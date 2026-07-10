import Erdos23Delta0.Ell5SingletonVertexSlack

/-!
# Endpoint slack plus collision-reserve Hall

This module is the exact finite Hall adapter for the collision-reserve route.
Each internal edge contributes one half-unit at each endpoint.  Ordinary
vertex slack and a nonnegative endpoint-to-token reserve jointly pay the
endpoint incidence degree.  A global no-double-spend inequality on every
token then implies the full subset Hall inequalities.

The module does not construct the reserve.  In the graph application that is
the sole `c5Base`/`prune` collision-assignment obligation.
-/

namespace Erdos23Delta0
namespace EndpointReserveHall

open scoped BigOperators
open Ell5SingletonVertexSlack

variable {V JT : Type*} [Fintype V] [DecidableEq V]
  [Fintype JT] [DecidableEq JT]

attribute [local instance] Classical.propDecidable

/-- Half of the number of selected edges incident with `x`. -/
def halfDegree (E : Finset (Sym2 V)) (x : V) : ℚ :=
  ((E.filter fun e => x ∈ e).card : ℚ) / 2

/-- A combined sink is either the endpoint's vertex-slack sink or a reserve
token receiving positive mass at one endpoint. -/
def endpointReserveInc (eta : V → JT → ℚ)
    (e : Sym2 V) : V ⊕ JT → Prop
  | Sum.inl x => x ∈ e
  | Sum.inr t => ∃ x, x ∈ e ∧ 0 < eta x t

def endpointReserveCap (slack : V → ℚ) (cap : JT → ℚ) : V ⊕ JT → ℚ
  | Sum.inl x => slack x
  | Sum.inr t => cap t

noncomputable def endpointReserveRHS
    (T : Finset (Sym2 V)) (slack : V → ℚ)
    (eta : V → JT → ℚ) (cap : JT → ℚ) : ℚ :=
  (∑ x : V, if (∃ e ∈ T, x ∈ e) then slack x else 0) +
    ∑ t : JT,
      if (∃ e ∈ T, ∃ x, x ∈ e ∧ 0 < eta x t) then cap t else 0

noncomputable def endpointReserveNeighborCap
    (T : Finset (Sym2 V)) (slack : V → ℚ)
    (eta : V → JT → ℚ) (cap : JT → ℚ) : ℚ :=
  ∑ j ∈ Finset.univ.filter
    (fun j : V ⊕ JT => ∃ e ∈ T, endpointReserveInc eta e j),
    endpointReserveCap slack cap j

theorem endpointReserveRHS_eq_neighborCap
    (T : Finset (Sym2 V)) (slack : V → ℚ)
    (eta : V → JT → ℚ) (cap : JT → ℚ) :
    endpointReserveRHS T slack eta cap =
      endpointReserveNeighborCap T slack eta cap := by
  classical
  unfold endpointReserveRHS endpointReserveNeighborCap
  rw [Finset.sum_filter, Fintype.sum_sum_type]
  simp only [endpointReserveInc, endpointReserveCap]

/-- Every genuine non-loop edge contributes exactly one unit when split into
two endpoint half-units. -/
def EndpointHalfExact (E : Finset (Sym2 V)) : Prop :=
  ∀ e ∈ E, (∑ x : V, endpointQ e x) = 1

theorem card_eq_sum_halfDegree
    {E T : Finset (Sym2 V)} (hT : T ⊆ E)
    (hends : EndpointHalfExact E) :
    (T.card : ℚ) = ∑ x : V, halfDegree T x := by
  calc
    (T.card : ℚ) = ∑ e ∈ T, (1 : ℚ) := by simp
    _ = ∑ e ∈ T, ∑ x : V, endpointQ e x := by
      apply Finset.sum_congr rfl
      intro e he
      rw [hends e (hT he)]
    _ = ∑ x : V, ∑ e ∈ T, endpointQ e x := by
      rw [Finset.sum_comm]
    _ = ∑ x : V, halfDegree T x := by
      apply Finset.sum_congr rfl
      intro x _
      exact sum_endpointQ_eq_half_incident_card T x

theorem halfDegree_mono {E T : Finset (Sym2 V)} (hT : T ⊆ E) (x : V) :
    halfDegree T x ≤ halfDegree E x := by
  unfold halfDegree
  apply div_le_div_of_nonneg_right
  · exact_mod_cast Finset.card_le_card (Finset.filter_subset_filter _ hT)
  · norm_num

private theorem halfDegree_eq_zero_of_no_endpoint
    (T : Finset (Sym2 V)) (x : V)
    (h : ¬∃ e ∈ T, x ∈ e) :
    halfDegree T x = 0 := by
  unfold halfDegree
  have hempty : T.filter (fun e => x ∈ e) = ∅ := by
    rw [Finset.filter_eq_empty_iff]
    intro e heT hxe
    exact h ⟨e, heT, hxe⟩
  simp [hempty]

private theorem used_eta_le_cap
    (T : Finset (Sym2 V)) (eta : V → JT → ℚ) (cap : JT → ℚ)
    (heta : ∀ x t, 0 ≤ eta x t)
    (hcap : ∀ t, (∑ x : V, eta x t) ≤ cap t)
    (t : JT) :
    (∑ x : V, if (∃ e ∈ T, x ∈ e) then eta x t else 0) ≤
      if (∃ e ∈ T, ∃ x, x ∈ e ∧ 0 < eta x t) then cap t else 0 := by
  classical
  by_cases ht : ∃ e ∈ T, ∃ x, x ∈ e ∧ 0 < eta x t
  · simp only [ht, if_true]
    calc
      (∑ x : V, if (∃ e ∈ T, x ∈ e) then eta x t else 0) ≤
          ∑ x : V, eta x t := by
        apply Finset.sum_le_sum
        intro x _
        by_cases hx : ∃ e ∈ T, x ∈ e
        · simp [hx]
        · simp [hx, heta x t]
      _ ≤ cap t := hcap t
  · simp only [ht, if_false]
    apply le_of_eq
    apply Finset.sum_eq_zero
    intro x _
    by_cases hx : ∃ e ∈ T, x ∈ e
    · have hnot : ¬0 < eta x t := by
        intro hpos
        obtain ⟨e, heT, hxe⟩ := hx
        exact ht ⟨e, heT, x, hxe, hpos⟩
      have hzero : eta x t = 0 :=
        le_antisymm (not_lt.mp hnot) (heta x t)
      simp [hx, hzero]
    · simp [hx]

set_option maxHeartbeats 2000000 in
/-- Finite-set Hall form. `U` is any set containing every endpoint used by
`T`; `R` is any set containing every reserve token receiving positive mass
from `U`.  Supplying these sets explicitly avoids expanding large existential
neighbor predicates in the kernel. -/
theorem endpointReserveHallOn
    (E T : Finset (Sym2 V)) (U : Finset V) (R : Finset JT)
    (slack : V → ℚ) (eta : V → JT → ℚ) (cap : JT → ℚ)
    (hT : T ⊆ E)
    (hends : EndpointHalfExact E)
    (heta : ∀ x t, 0 ≤ eta x t)
    (hcap : ∀ t, (∑ x : V, eta x t) ≤ cap t)
    (hbudget : ∀ x, halfDegree E x ≤ slack x + ∑ t : JT, eta x t)
    (hU : ∀ e ∈ T, ∀ x, x ∈ e → x ∈ U)
    (hR : ∀ x ∈ U, ∀ t, 0 < eta x t → t ∈ R) :
    (T.card : ℚ) ≤ (∑ x ∈ U, slack x) + ∑ t ∈ R, cap t := by
  classical
  have hout : ∀ x, x ∉ U → halfDegree T x = 0 := by
    intro x hx
    apply halfDegree_eq_zero_of_no_endpoint
    rintro ⟨e, heT, hxe⟩
    exact hx (hU e heT x hxe)
  have hvertex :
      (∑ x : V, halfDegree T x) ≤
        ∑ x ∈ U, (slack x + ∑ t : JT, eta x t) := by
    calc
      (∑ x : V, halfDegree T x) = ∑ x ∈ U, halfDegree T x := by
        symm
        apply Finset.sum_subset (Finset.subset_univ U)
        intro x _ hx
        exact hout x hx
      _ ≤ ∑ x ∈ U, (slack x + ∑ t : JT, eta x t) := by
        exact Finset.sum_le_sum fun x _ =>
          (halfDegree_mono hT x).trans (hbudget x)
  have htoken :
      (∑ x ∈ U, ∑ t : JT, eta x t) ≤ ∑ t ∈ R, cap t := by
    calc
      (∑ x ∈ U, ∑ t : JT, eta x t) =
          ∑ t : JT, ∑ x ∈ U, eta x t := by
        rw [Finset.sum_comm]
      _ ≤ ∑ t : JT, if t ∈ R then cap t else 0 := by
        apply Finset.sum_le_sum
        intro t _
        by_cases ht : t ∈ R
        · simp only [ht, if_true]
          calc
            (∑ x ∈ U, eta x t) ≤ ∑ x : V, eta x t := by
              exact Finset.sum_le_sum_of_subset_of_nonneg
                (Finset.subset_univ U) (fun _ _ _ => heta _ _)
            _ ≤ cap t := hcap t
        · simp only [ht, if_false]
          apply le_of_eq
          apply Finset.sum_eq_zero
          intro x hx
          have hnot : ¬0 < eta x t := fun hpos => ht (hR x hx t hpos)
          exact le_antisymm (not_lt.mp hnot) (heta x t)
      _ = ∑ t ∈ R, cap t := by
        rw [← Finset.sum_filter]
        simp
  rw [card_eq_sum_halfDegree hT hends]
  calc
    (∑ x : V, halfDegree T x) ≤
        ∑ x ∈ U, (slack x + ∑ t : JT, eta x t) := hvertex
    _ = (∑ x ∈ U, slack x) + ∑ x ∈ U, ∑ t : JT, eta x t := by
      rw [Finset.sum_add_distrib]
    _ ≤ (∑ x ∈ U, slack x) + ∑ t ∈ R, cap t := by
      simpa [add_comm] using
        (add_le_add_left htoken (∑ x ∈ U, slack x))

#print axioms card_eq_sum_halfDegree
#print axioms endpointReserveHallOn

end EndpointReserveHall
end Erdos23Delta0
