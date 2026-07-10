import Erdos23Delta0.Ell5SingletonVertexSlack

/-!
# Internal endpoint slack with boundary Doors

This file bridges an explicit internal-endpoint-slack bound to the mixed
Door/vertex singleton certificate.  Boundary off-support edges use their own
explicitly legal Door; only internal off-support incidence consumes vertex
slack.
-/

namespace Erdos23Delta0

open Finset MaxCutVertexIneq
open RelaxedCoverGraphBridge
open Ell5FullBankInterface Ell5SingletonVertexSlack

variable {V : Type*} [DecidableEq V]

private theorem mem_sym2_iff_edgeBoundary_ne_true_of_incident
    (C : Finset V) {e : Sym2 V} {x : V} (hxC : x ∈ C) (hxe : x ∈ e) :
    e ∈ C.sym2 ↔ edgeBoundary C e ≠ true := by
  induction e using Sym2.ind with
  | _ u v =>
      rw [Sym2.mem_iff] at hxe
      rw [Finset.mk_mem_sym2_iff]
      rcases hxe with rfl | rfl
      · by_cases hv : v ∈ C <;>
          simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, hxC, hv]
      · by_cases hu : u ∈ C <;>
          simp [edgeBoundary, edgeBool, memBool, Sym2.lift_mk, hxC, hu]

/-- At a core vertex, the non-boundary members of `O` incident to that vertex
are exactly the internal members of `O` incident to it. -/
theorem nonDoor_incident_filter_eq_internal_incident_filter
    (O : Finset (Sym2 V)) (C : Finset V) (x : V) (hxC : x ∈ C) :
    let D := O.filter fun e => edgeBoundary C e = true
    let I := O.filter fun e => e ∈ C.sym2
    (O.filter fun e => e ∉ D).filter (fun e => x ∈ e) =
      I.filter (fun e => x ∈ e) := by
  dsimp only
  ext e
  simp only [Finset.mem_filter]
  constructor
  · rintro ⟨⟨heO, heD⟩, hxe⟩
    refine ⟨⟨heO, ?_⟩, hxe⟩
    apply (mem_sym2_iff_edgeBoundary_ne_true_of_incident C hxC hxe).2
    intro hboundary
    exact heD ⟨heO, hboundary⟩
  · rintro ⟨⟨heO, heI⟩, hxe⟩
    refine ⟨⟨heO, ?_⟩, hxe⟩
    intro heD
    exact (mem_sym2_iff_edgeBoundary_ne_true_of_incident C hxC hxe).1 heI
      heD.2

/-- Count normalization for internal endpoint slack.  Here
`O = cutEdges G s \ F`, `D` is its boundary filter, and `I` its internal
filter. -/
theorem internalEndpoint_nonDoor_count_normalization
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (s : V → Bool) (C : Finset V) (F : Finset (Sym2 V))
    (x : V) (hxC : x ∈ C) :
    let O := cutEdges G s \ F
    let D := O.filter fun e => edgeBoundary C e = true
    let I := O.filter fun e => e ∈ C.sym2
    ((((O.filter fun e => e ∉ D).filter fun e => x ∈ e).card : ℚ) / 2) =
      (((I.filter fun e => x ∈ e).card : ℚ) / 2) := by
  dsimp only
  rw [nonDoor_incident_filter_eq_internal_incident_filter
    (cutEdges G s \ F) C x hxC]

/-- Build the mixed singleton certificate from explicit internal endpoint
slack and explicit boundary own-Door eligibility.  No endpoint or Door
existence is inferred by this bridge. -/
noncomputable def certificate_of_internalEndpointSlack_boundaryDoors
    [Fintype V]
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (s : V → Bool) (C : Finset V)
    (S F : Finset (Sym2 V))
    (inc : Sym2 V → (V ⊕ Sym2 V) → Prop)
    (kap : (V ⊕ Sym2 V) → ℚ)
    (slack : V → ℚ)
    (hkap : ∀ j, 0 ≤ kap j)
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧ e ∈ C.sym2)
    (hF : ∀ e ∈ F,
      e ∈ G.edgeFinset ∧ edgeCut s e = true ∧ e ∈ C.sym2)
    (hIESDegree : ∀ x ∈ C,
      (((((cutEdges G s \ F).filter fun e => e ∈ C.sym2).filter
          fun e => x ∈ e).card : ℚ) / 2) ≤ slack x)
    (hslack : ∀ x ∈ C, slack x ≤ kap (Sum.inl x))
    (hendpointLegal : ∀ e ∈ (cutEdges G s \ F).filter (fun e => e ∈ C.sym2),
      ∀ x ∈ C, x ∈ e → inc e (Sum.inl x))
    (hboundaryDoorLegal : ∀ e ∈ cutEdges G s \ F,
      edgeBoundary C e = true → inc e (Sum.inr e))
    (hboundaryDoorCapacity : ∀ e ∈ cutEdges G s \ F,
      edgeBoundary C e = true → (1 / 2 : ℚ) ≤ kap (Sum.inr e)) :
    FullBankRelaxedCoverCert S F (cutEdges G s \ F) Finset.univ C
      (fun x => deltaM G s ({x} : Finset V))
      (fun x => deltaB G s ({x} : Finset V)) inc kap := by
  let O := cutEdges G s \ F
  let D := O.filter fun e => edgeBoundary C e = true
  let I := O.filter fun e => e ∈ C.sym2
  apply certificate_of_singletonCore_mixedDoorVertexCount
    G s C S F O D inc kap hkap
  · intro e heD
    exact (Finset.mem_filter.1 heD).1
  · exact hS
  · exact hF
  · intro e heO
    have heCut : e ∈ cutEdges G s := (Finset.mem_sdiff.1 heO).1
    simpa [cutEdges] using heCut
  · intro e heO heD x hxC hxe
    apply hendpointLegal e
    · change e ∈ I
      have hfiltered : e ∈ I.filter (fun c => x ∈ c) := by
        rw [← nonDoor_incident_filter_eq_internal_incident_filter O C x hxC]
        exact Finset.mem_filter.2 ⟨Finset.mem_filter.2 ⟨heO, heD⟩, hxe⟩
      exact (Finset.mem_filter.1 hfiltered).1
    · exact hxC
    · exact hxe
  · intro e heD
    obtain ⟨heO, hboundary⟩ := Finset.mem_filter.1 heD
    exact hboundaryDoorLegal e heO hboundary
  · intro x hxC
    rw [internalEndpoint_nonDoor_count_normalization G s C F x hxC]
    exact le_trans (hIESDegree x hxC) (hslack x hxC)
  · intro e heD
    obtain ⟨heO, hboundary⟩ := Finset.mem_filter.1 heD
    have heCut : e ∈ cutEdges G s := (Finset.mem_sdiff.1 heO).1
    have heData : e ∈ G.edgeFinset ∧ edgeCut s e = true := by
      simpa [cutEdges] using heCut
    rw [singleton_boundary_port_load G s C heData.1 heData.2 hboundary]
    exact hboundaryDoorCapacity e heO hboundary

end Erdos23Delta0
