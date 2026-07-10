import Erdos23Delta0.Ell5SingletonVertexSlack

/-!
# Fractional endpoint routing for the half-singleton cover

The fixed endpoint split in `Ell5SingletonVertexSlack` is sufficient but not
necessary.  An internal off-support edge has singleton load one and may route
that load fractionally between any legal endpoint vertex-slack sinks.  Boundary
edges in `D` still use their individual Door sink.

This module isolates the exact weaker obligation: provide a nonnegative
endpoint flow, cover each non-Door edge's singleton load, and respect each
vertex capacity.
-/

namespace Erdos23Delta0
namespace Ell5SingletonEndpointFlow

open Finset MaxCutVertexIneq
open Ell5FullBankInterface
open Ell5FullBankAssignedSink
open Ell5SingletonVertexSlack

variable {V : Type*} [DecidableEq V]

section Graph

variable (G : SimpleGraph V) [Fintype G.edgeSet]

/-- Mixed Door/endpoint-flow routing.  Only core vertices are exposed as
vertex sinks; values of `flow` outside `C` are ignored. -/
def mixedDoorEndpointFlowQ
    (s : V → Bool) (C : Finset V) (D : Finset (Sym2 V))
    (flow : Sym2 V → V → ℚ) (c : Sym2 V) : V ⊕ Sym2 V → ℚ
  | Sum.inl x =>
      if c ∈ D then 0 else if x ∈ C then flow c x else 0
  | Sum.inr e =>
      if c ∈ D then
        if c = e then
          RelaxedCutCover.load C halfWeight
            (fun x => deltaB G s ({x} : Finset V)) c
        else 0
      else 0

/-- Half-singleton certificate with arbitrary fractional endpoint routing for
the non-Door off-support edges. -/
noncomputable def certificate_of_singletonCore_mixedDoorEndpointFlow
    [Fintype V]
    (s : V → Bool) (C : Finset V)
    (S F O D : Finset (Sym2 V))
    (inc : Sym2 V → (V ⊕ Sym2 V) → Prop)
    (kap : (V ⊕ Sym2 V) → ℚ)
    (flow : Sym2 V → V → ℚ)
    (hkap : ∀ j, 0 ≤ kap j)
    (hD : D ⊆ O)
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧ e ∈ C.sym2)
    (hF : ∀ e ∈ F,
      e ∈ G.edgeFinset ∧ edgeCut s e = true ∧ e ∈ C.sym2)
    (hO : ∀ e ∈ O, e ∈ G.edgeFinset ∧ edgeCut s e = true)
    (hflow_nonneg : ∀ e ∈ O, e ∉ D → ∀ x ∈ C, 0 ≤ flow e x)
    (hflow_route : ∀ e ∈ O, e ∉ D →
      RelaxedCutCover.load C halfWeight
          (fun x => deltaB G s ({x} : Finset V)) e ≤
        ∑ x ∈ C, flow e x)
    (hflow_cap : ∀ x ∈ C,
      (∑ e ∈ O, if e ∈ D then 0 else flow e x) ≤ kap (Sum.inl x))
    (hincFlow : ∀ e ∈ O, e ∉ D → ∀ x ∈ C,
      0 < flow e x → inc e (Sum.inl x))
    (hincDoor : ∀ e ∈ D, inc e (Sum.inr e))
    (hdoor : ∀ e ∈ D,
      RelaxedCutCover.load C halfWeight
        (fun x => deltaB G s ({x} : Finset V)) e ≤ kap (Sum.inr e)) :
    FullBankRelaxedCoverCert S F O Finset.univ C
      (fun x => deltaM G s ({x} : Finset V))
      (fun x => deltaB G s ({x} : Finset V)) inc kap where
  lam := halfWeight
  q := mixedDoorEndpointFlowQ G s C D flow
  hlam := by intro x hx; norm_num [halfWeight]
  hq := by
    intro e he j hj
    cases j with
    | inl x =>
        by_cases heD : e ∈ D
        · simp [mixedDoorEndpointFlowQ, heD]
        · by_cases hx : x ∈ C
          · simpa [mixedDoorEndpointFlowQ, heD, hx] using
              hflow_nonneg e he heD x hx
          · simp [mixedDoorEndpointFlowQ, heD, hx]
    | inr d =>
        by_cases heD : e ∈ D
        · by_cases hed : e = d
          · subst d
            simpa [mixedDoorEndpointFlowQ, heD] using
              load_nonneg C halfWeight
                (fun x => deltaB G s ({x} : Finset V))
                (by intro x hx; norm_num [halfWeight]) e
          · simp [mixedDoorEndpointFlowQ, heD, hed]
        · simp [mixedDoorEndpointFlowQ, heD]
  hkap := by intro j hj; exact hkap j
  hcov := by
    intro e he
    obtain ⟨heG, hbad, hcore⟩ := hS e he
    exact le_of_eq (singleton_bad_coverage G s C heG hbad hcore).symm
  hcong := by
    intro e he
    obtain ⟨heG, hcut, hcore⟩ := hF e he
    exact le_of_eq (singleton_cut_congestion G s C heG hcut hcore)
  hroute := by
    intro e he
    obtain ⟨heG, hcut⟩ := hO e he
    change RelaxedCutCover.load C halfWeight
      (fun x => deltaB G s ({x} : Finset V)) e ≤ _
    rw [Fintype.sum_sum_type]
    by_cases heD : e ∈ D
    · simp [mixedDoorEndpointFlowQ, heD]
    · calc
        RelaxedCutCover.load C halfWeight
            (fun x => deltaB G s ({x} : Finset V)) e ≤
            ∑ x ∈ C, flow e x := hflow_route e he heD
        _ = _ := by simp [mixedDoorEndpointFlowQ, heD]
  hcap := by
    intro j hj
    cases j with
    | inl x =>
        by_cases hx : x ∈ C
        · simpa [mixedDoorEndpointFlowQ, hx] using hflow_cap x hx
        · simpa [mixedDoorEndpointFlowQ, hx] using hkap (Sum.inl x)
    | inr d =>
        by_cases hd : d ∈ D
        · have hdO : d ∈ O := hD hd
          calc
            (∑ e ∈ O,
                mixedDoorEndpointFlowQ G s C D flow e (Sum.inr d)) =
                RelaxedCutCover.load C halfWeight
                  (fun x => deltaB G s ({x} : Finset V)) d := by
                    rw [Finset.sum_eq_single d]
                    · simp [mixedDoorEndpointFlowQ, hd]
                    · intro e he hne
                      simp [mixedDoorEndpointFlowQ, hne]
                    · intro hnot
                      exact False.elim (hnot hdO)
            _ ≤ kap (Sum.inr d) := hdoor d hd
        · simpa [mixedDoorEndpointFlowQ, hd] using hkap (Sum.inr d)
  hqinc := by
    intro e he j hj hpos
    cases j with
    | inl x =>
        by_cases heD : e ∈ D
        · simp [mixedDoorEndpointFlowQ, heD] at hpos
        · by_cases hx : x ∈ C
          · apply hincFlow e he heD x hx
            simpa [mixedDoorEndpointFlowQ, heD, hx] using hpos
          · simp [mixedDoorEndpointFlowQ, heD, hx] at hpos
    | inr d =>
        by_cases heD : e ∈ D
        · by_cases hed : e = d
          · simpa [hed] using hincDoor e heD
          · simp [mixedDoorEndpointFlowQ, heD, hed] at hpos
        · simp [mixedDoorEndpointFlowQ, heD] at hpos

end Graph

end Ell5SingletonEndpointFlow
end Erdos23Delta0
