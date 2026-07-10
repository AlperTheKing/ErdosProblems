import Erdos23Delta0.Ell5BlockEndpointFlow

/-!
# Active-component owner partition

For an off-support component partition, components which contain both
endpoints of a selected bad atom are singletonized; every other component is
kept as one block.  This is the canonical mixed partition behind the
componentwise block/flow construction.
-/

namespace Erdos23Delta0
namespace Ell5ActiveComponentFlow

open Finset MaxCutVertexIneq
open Ell5FullBankInterface Ell5BlockSingleton Ell5BlockEndpointFlow

variable {V Comp : Type*} [DecidableEq V]
  [Fintype Comp] [DecidableEq Comp]

/-- Active components use vertex-singleton owners; inactive components use
their component label. -/
def componentOwner (comp : V → Comp) (active : Comp → Bool) (x : V) : V ⊕ Comp :=
  if active (comp x) then Sum.inl x else Sum.inr (comp x)

omit [DecidableEq V] [Fintype Comp] [DecidableEq Comp] in
theorem componentOwner_ne
    (comp : V → Comp) (active : Comp → Bool) {u v : V}
    (hne : u ≠ v)
    (hclass : comp u ≠ comp v ∨ active (comp u) = true) :
    componentOwner comp active u ≠ componentOwner comp active v := by
  by_cases hu : active (comp u) = true
  · by_cases hv : active (comp v) = true
    · simp [componentOwner, hu, hv, hne]
    · simp [componentOwner, hu, hv]
  · have hcomp : comp u ≠ comp v := by
      rcases hclass with hcomp | hactive
      · exact hcomp
      · exact (hu hactive).elim
    by_cases hv : active (comp v) = true
    · simp [componentOwner, hu, hv]
    · simp [componentOwner, hu, hv, hcomp]

section Graph

variable (G : SimpleGraph V) [Fintype G.edgeSet]

/-- Canonical active-component specialization of the general block/flow
certificate.  The graph-side active condition says that every selected bad
edge either joins two components or lies in a component marked active. -/
noncomputable def certificate_of_activeComponent_mixedDoorEndpointFlow
    [Fintype V]
    (s : V → Bool) (C : Finset V)
    (comp : V → Comp) (active : Comp → Bool)
    (S F O D : Finset (Sym2 V))
    (inc : Sym2 V → (V ⊕ Sym2 V) → Prop)
    (kap : (V ⊕ Sym2 V) → ℚ)
    (flow : Sym2 V → V → ℚ)
    (hkap : ∀ j, 0 ≤ kap j)
    (hD : D ⊆ O)
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧ e ∈ C.sym2)
    (hactive : ∀ e ∈ S, ∀ u v, e = s(u, v) →
      comp u ≠ comp v ∨ active (comp u) = true)
    (hF : ∀ e ∈ F, e ∈ G.edgeFinset ∧ edgeCut s e = true)
    (hflow_nonneg : ∀ e ∈ O, e ∉ D → ∀ x ∈ C, 0 ≤ flow e x)
    (hflow_route : ∀ e ∈ O, e ∉ D →
      blockLoad G s C (componentOwner comp active) e ≤
        ∑ x ∈ C, flow e x)
    (hflow_cap : ∀ x ∈ C,
      (∑ e ∈ O, if e ∈ D then 0 else flow e x) ≤ kap (Sum.inl x))
    (hincFlow : ∀ e ∈ O, e ∉ D → ∀ x ∈ C,
      0 < flow e x → inc e (Sum.inl x))
    (hincDoor : ∀ e ∈ D, inc e (Sum.inr e))
    (hdoor : ∀ e ∈ D,
      blockLoad G s C (componentOwner comp active) e ≤ kap (Sum.inr e)) :
    FullBankRelaxedCoverCert S F O Finset.univ Finset.univ
      (fun b => deltaM G s (blockSet C (componentOwner comp active) b))
      (fun b => deltaB G s (blockSet C (componentOwner comp active) b)) inc kap := by
  apply certificate_of_blockCore_mixedDoorEndpointFlow
    G s C (componentOwner comp active) S F O D inc kap flow
    hkap hD
  · intro e he
    obtain ⟨heG, hbad, hcore⟩ := hS e he
    refine ⟨heG, hbad, hcore, ?_⟩
    intro u v huv
    have hadj : G.Adj u v := by
      rw [huv] at heG
      rw [SimpleGraph.mem_edgeFinset, SimpleGraph.mem_edgeSet] at heG
      exact heG
    exact componentOwner_ne comp active (G.ne_of_adj hadj)
      (hactive e he u v huv)
  · exact hF
  · exact hflow_nonneg
  · exact hflow_route
  · exact hflow_cap
  · exact hincFlow
  · exact hincDoor
  · exact hdoor

end Graph

end Ell5ActiveComponentFlow
end Erdos23Delta0
