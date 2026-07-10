import Erdos23Delta0.CapacitatedHallFlow
import Erdos23Delta0.Ell5ActiveComponentFlow

namespace Erdos23Delta0
namespace Ell5ActiveComponentHall

open Finset MaxCutVertexIneq
open Ell5FullBankInterface Ell5FullBankAssignedSink
open Ell5BlockSingleton Ell5BlockEndpointFlow Ell5ActiveComponentFlow

variable {V Comp : Type*} [DecidableEq V]
  [Fintype Comp] [DecidableEq Comp]

/-- Non-Door off-support edges. -/
abbrev E0 (O D : Finset (Sym2 V)) :=
  {e : Sym2 V // e ∈ O ∧ e ∉ D}

/-- Core vertices available as endpoint-flow sinks. -/
abbrev V0 (C : Finset V) :=
  {x : V // x ∈ C}

/-- The load which a non-Door off-support edge must route. -/
noncomputable def demand [Fintype V]
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (s : V → Bool) (C : Finset V)
    (comp : V → Comp) (active : Comp → Bool)
    {O D : Finset (Sym2 V)} (e : E0 O D) : ℚ :=
  blockLoad G s C (componentOwner comp active) e.1

/-- Capacity of a core-vertex sink. -/
def capV (kap : (V ⊕ Sym2 V) → ℚ)
    {C : Finset V} (x : V0 C) : ℚ :=
  kap (Sum.inl x.1)

/-- Restricted legal incidence between non-Door edges and core vertices. -/
def legalInc (inc : Sym2 V → (V ⊕ Sym2 V) → Prop)
    {O D : Finset (Sym2 V)} {C : Finset V}
    (e : E0 O D) (x : V0 C) : Prop :=
  inc e.1 (Sum.inl x.1)

/-- Hall's condition for routing every active-component block load to the
legal core-vertex sinks without exceeding their capacities. -/
noncomputable def ActiveComponentHall [Fintype V]
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (s : V → Bool) (C : Finset V)
    (comp : V → Comp) (active : Comp → Bool)
    (O D : Finset (Sym2 V))
    (inc : Sym2 V → (V ⊕ Sym2 V) → Prop)
    (kap : (V ⊕ Sym2 V) → ℚ) : Prop := by
  classical
  exact ∀ T : Finset (E0 O D),
    (∑ e ∈ T, demand G s C comp active e) ≤
      ∑ x ∈ Finset.univ.filter
        (fun x : V0 C => ∃ e ∈ T, legalInc inc e x), capV kap x

private def e0FilterEquiv (O D : Finset (Sym2 V)) :
    E0 O D ≃ {e : Sym2 V // e ∈ O.filter fun e => e ∉ D} where
  toFun e := ⟨e.1, by simpa only [Finset.mem_filter] using e.2⟩
  invFun e := ⟨e.1, by simpa only [Finset.mem_filter] using e.2⟩
  left_inv e := Subtype.ext rfl
  right_inv e := Subtype.ext rfl

private def extendE0 {M : Type*} [Zero M]
    (O D : Finset (Sym2 V)) (f : E0 O D → M) (e : Sym2 V) : M :=
  if heO : e ∈ O then
    if heD : e ∈ D then 0 else f ⟨e, heO, heD⟩
  else 0

private def extendV0 {M : Type*} [Zero M]
    (C : Finset V) (f : V0 C → M) (x : V) : M :=
  if hx : x ∈ C then f ⟨x, hx⟩ else 0

private theorem sum_extendE0 [Fintype V] {M : Type*} [AddCommMonoid M]
    (O D : Finset (Sym2 V)) (f : E0 O D → M) :
    (∑ e ∈ O, extendE0 O D f e) = ∑ e : E0 O D, f e := by
  classical
  calc
    (∑ e ∈ O, extendE0 O D f e) =
        ∑ e ∈ O.filter (fun e => e ∉ D), extendE0 O D f e := by
      rw [Finset.sum_filter]
      apply Finset.sum_congr rfl
      intro e heO
      by_cases heD : e ∈ D <;> simp [extendE0, heO, heD]
    _ = ∑ e : {e : Sym2 V // e ∈ O.filter fun e => e ∉ D},
          f ((e0FilterEquiv O D).symm e) := by
      rw [Finset.univ_eq_attach]
      rw [← Finset.sum_attach
        (O.filter fun e => e ∉ D) (extendE0 O D f)]
      apply Finset.sum_congr rfl
      intro e _
      have he : e.1 ∈ O ∧ e.1 ∉ D := by
        simpa only [Finset.mem_filter] using e.2
      simp [extendE0, e0FilterEquiv, he.1, he.2]
    _ = ∑ e : E0 O D, f e :=
      Equiv.sum_comp (e0FilterEquiv O D).symm f

private theorem sum_extendV0 {M : Type*} [AddCommMonoid M]
    (C : Finset V) (f : V0 C → M) :
    (∑ x ∈ C, extendV0 C f x) = ∑ x : V0 C, f x := by
  classical
  rw [Finset.univ_eq_attach]
  rw [← Finset.sum_attach C (extendV0 C f)]
  apply Finset.sum_congr rfl
  intro x _
  simp [extendV0]

section Graph

variable (G : SimpleGraph V) [Fintype G.edgeSet]

/-- Hall's condition constructs the endpoint flow needed by the canonical
active-component full-bank certificate. -/
noncomputable def certificate_of_activeComponent_mixedDoorEndpointHall
    [Fintype V]
    (s : V → Bool) (C : Finset V)
    (comp : V → Comp) (active : Comp → Bool)
    (S F O D : Finset (Sym2 V))
    (inc : Sym2 V → (V ⊕ Sym2 V) → Prop)
    (kap : (V ⊕ Sym2 V) → ℚ)
    (hkap : ∀ j, 0 ≤ kap j)
    (hD : D ⊆ O)
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧ e ∈ C.sym2)
    (hactive : ∀ e ∈ S, ∀ u v, e = s(u, v) →
      comp u ≠ comp v ∨ active (comp u) = true)
    (hF : ∀ e ∈ F, e ∈ G.edgeFinset ∧ edgeCut s e = true)
    (hHall : ActiveComponentHall G s C comp active O D inc kap)
    (hincDoor : ∀ e ∈ D, inc e (Sum.inr e))
    (hdoor : ∀ e ∈ D,
      blockLoad G s C (componentOwner comp active) e ≤ kap (Sum.inr e)) :
    FullBankRelaxedCoverCert S F O Finset.univ Finset.univ
      (fun b => deltaM G s (blockSet C (componentOwner comp active) b))
      (fun b => deltaB G s (blockSet C (componentOwner comp active) b)) inc kap := by
  classical
  have hdemand0 :
      ∀ e : E0 O D, 0 ≤ demand G s C comp active e := by
    intro e
    simpa [demand, blockLoad] using
      load_nonneg Finset.univ blockWeight
        (fun b => deltaB G s (blockSet C (componentOwner comp active) b))
        (by intro b hb; norm_num [blockWeight]) e.1
  have hcap0 :
      ∀ x : V0 C, 0 ≤ capV kap x := by
    intro x
    simpa [capV] using hkap (Sum.inl x.1)
  have hflow_exists :=
    capacitatedBipartiteFlow_exists
      (fun e : E0 O D => demand G s C comp active e)
      (fun x : V0 C => capV kap x)
      (fun e : E0 O D => fun x : V0 C => legalInc inc e x)
      hdemand0 hcap0 (by simpa [ActiveComponentHall] using hHall)
  let flow0 : E0 O D → V0 C → ℚ := hflow_exists.choose
  have hflow0_nonneg := hflow_exists.choose_spec.1
  have hflow0_support := hflow_exists.choose_spec.2.1
  have hflow0_route := hflow_exists.choose_spec.2.2.1
  have hflow0_cap := hflow_exists.choose_spec.2.2.2
  let flow : Sym2 V → V → ℚ := fun e x =>
    extendE0 O D (fun e0 => extendV0 C (flow0 e0) x) e
  have hflow_nonneg :
      ∀ e ∈ O, e ∉ D → ∀ x ∈ C, 0 ≤ flow e x := by
    intro e heO heD x hx
    simpa [flow, extendE0, extendV0, heO, heD, hx] using
      hflow0_nonneg (⟨e, heO, heD⟩ : E0 O D) (⟨x, hx⟩ : V0 C)
  have hflow_route :
      ∀ e ∈ O, e ∉ D →
        blockLoad G s C (componentOwner comp active) e ≤
          ∑ x ∈ C, flow e x := by
    intro e heO heD
    let e0 : E0 O D := ⟨e, heO, heD⟩
    calc
      blockLoad G s C (componentOwner comp active) e =
          demand G s C comp active e0 := by simp [demand, e0]
      _ ≤ ∑ x : V0 C, flow0 e0 x := hflow0_route e0
      _ = ∑ x ∈ C, flow e x := by
        symm
        simpa [flow, extendE0, heO, heD, e0] using
          sum_extendV0 C (flow0 e0)
  have hflow_cap :
      ∀ x ∈ C,
        (∑ e ∈ O, if e ∈ D then 0 else flow e x) ≤ kap (Sum.inl x) := by
    intro x hx
    let x0 : V0 C := ⟨x, hx⟩
    calc
      (∑ e ∈ O, if e ∈ D then 0 else flow e x) =
          ∑ e ∈ O, extendE0 O D (fun e0 => flow0 e0 x0) e := by
        apply Finset.sum_congr rfl
        intro e heO
        by_cases heD : e ∈ D
        · simp [flow, extendE0, heO, heD]
        · simp [flow, extendE0, extendV0, heO, heD, hx, x0]
      _ = ∑ e : E0 O D, flow0 e x0 :=
        sum_extendE0 O D (fun e => flow0 e x0)
      _ ≤ capV kap x0 := hflow0_cap x0
      _ = kap (Sum.inl x) := by simp [capV, x0]
  have hincFlow :
      ∀ e ∈ O, e ∉ D → ∀ x ∈ C,
        0 < flow e x → inc e (Sum.inl x) := by
    intro e heO heD x hx hpos
    let e0 : E0 O D := ⟨e, heO, heD⟩
    let x0 : V0 C := ⟨x, hx⟩
    by_contra hlegal
    have hnot0 : ¬legalInc inc e0 x0 := by
      simpa [legalInc, e0, x0] using hlegal
    have hzero : flow0 e0 x0 = 0 := hflow0_support e0 x0 hnot0
    have heq : flow e x = flow0 e0 x0 := by
      simp [flow, extendE0, extendV0, heO, heD, hx, e0, x0]
    rw [heq, hzero] at hpos
    exact (lt_irrefl 0) hpos
  exact certificate_of_activeComponent_mixedDoorEndpointFlow
    G s C comp active S F O D inc kap flow
    hkap hD hS hactive hF
    hflow_nonneg hflow_route hflow_cap hincFlow hincDoor hdoor

end Graph

end Ell5ActiveComponentHall
end Erdos23Delta0
