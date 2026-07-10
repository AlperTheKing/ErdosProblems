import Erdos23Delta0.CapacitatedHallFlow
import Erdos23Delta0.Ell5ActiveComponentFlow
import Erdos23Delta0.Ell5BlockBankFlow

/-!
# Active-component Hall routing to generic bank sinks

Hall's condition is imposed only on non-Door edges and the generic bank pool.
Door edges are added afterwards using their separate edge-indexed sinks.
-/

namespace Erdos23Delta0
namespace Ell5ActiveComponentBankHall

open Finset MaxCutVertexIneq
open Ell5FullBankInterface Ell5FullBankAssignedSink Ell5BlockSingleton
open Ell5ActiveComponentFlow
open Ell5BlockBankFlow

variable {V Comp JT : Type*} [DecidableEq V]
  [Fintype Comp] [DecidableEq Comp] [Fintype JT] [DecidableEq JT]

/-- Non-Door off-support edges. -/
abbrev E0 (O D : Finset (Sym2 V)) :=
  {e : Sym2 V // e ∈ O ∧ e ∉ D}

/-- The actual active-component block load of a non-Door edge. -/
noncomputable def demand [Fintype V]
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (s : V → Bool) (C : Finset V)
    (comp : V → Comp) (active : Comp → Bool)
    {O D : Finset (Sym2 V)} (e : E0 O D) : ℚ :=
  blockLoad G s C (componentOwner comp active) e.1

/-- The combined incidence relation keeps the non-Door pool and Door pool in
separate summands. -/
def combinedInc
    (incBase : Sym2 V → JT → Prop)
    (incDoor : Sym2 V → Sym2 V → Prop)
    (e : Sym2 V) : BlockBankSink JT V → Prop
  | Sum.inl j => incBase e j
  | Sum.inr d => incDoor e d

/-- Capacities for the disjoint non-Door and Door sink pools. -/
def combinedCap
    (kapBase : JT → ℚ) (kapDoor : Sym2 V → ℚ) :
    BlockBankSink JT V → ℚ
  | Sum.inl j => kapBase j
  | Sum.inr e => kapDoor e

/-- Weighted Hall condition for the actual block loads of `O \ D`, using
only the generic sink family `JT`. -/
noncomputable def ActiveComponentBankHall [Fintype V]
    (G : SimpleGraph V) [Fintype G.edgeSet]
    (s : V → Bool) (C : Finset V)
    (comp : V → Comp) (active : Comp → Bool)
    (O D : Finset (Sym2 V))
    (incBase : Sym2 V → JT → Prop)
    (kapBase : JT → ℚ) : Prop := by
  classical
  exact ∀ T : Finset (E0 O D),
    (∑ e ∈ T, demand G s C comp active e) ≤
      ∑ j ∈ Finset.univ.filter
        (fun j : JT => ∃ e ∈ T, incBase e.1 j), kapBase j

private def extendE0 {M : Type*} [Zero M]
    (O D : Finset (Sym2 V)) (f : E0 O D → M) (e : Sym2 V) : M :=
  if heO : e ∈ O then
    if heD : e ∈ D then 0 else f ⟨e, heO, heD⟩
  else 0

private def e0FilterEquiv (O D : Finset (Sym2 V)) :
    E0 O D ≃ {e : Sym2 V // e ∈ O.filter fun e => e ∉ D} where
  toFun e := ⟨e.1, by simpa only [Finset.mem_filter] using e.2⟩
  invFun e := ⟨e.1, by simpa only [Finset.mem_filter] using e.2⟩
  left_inv e := Subtype.ext rfl
  right_inv e := Subtype.ext rfl

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

section Graph

variable (G : SimpleGraph V) [Fintype G.edgeSet]

/-- Hall routing on the generic bank pool, followed by edge-specific Door
routing, constructs the active-component full-bank certificate. -/
noncomputable def certificate_of_activeComponent_mixedDoorBankHall
    [Fintype V]
    (s : V → Bool) (C : Finset V)
    (comp : V → Comp) (active : Comp → Bool)
    (S F O D : Finset (Sym2 V))
    (incBase : Sym2 V → JT → Prop)
    (kapBase : JT → ℚ)
    (incDoor : Sym2 V → Sym2 V → Prop)
    (kapDoor : Sym2 V → ℚ)
    (hkapBase : ∀ j, 0 ≤ kapBase j)
    (hkapDoor : ∀ e, 0 ≤ kapDoor e)
    (hD : D ⊆ O)
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧ e ∈ C.sym2)
    (hactive : ∀ e ∈ S, ∀ u v, e = s(u, v) →
      comp u ≠ comp v ∨ active (comp u) = true)
    (hF : ∀ e ∈ F, e ∈ G.edgeFinset ∧ edgeCut s e = true)
    (hHall : ActiveComponentBankHall G s C comp active O D incBase kapBase)
    (hincDoor : ∀ e ∈ D, incDoor e e)
    (hdoor : ∀ e ∈ D,
      blockLoad G s C (componentOwner comp active) e ≤ kapDoor e) :
    FullBankRelaxedCoverCert S F O Finset.univ Finset.univ
      (fun b => deltaM G s (blockSet C (componentOwner comp active) b))
      (fun b => deltaB G s (blockSet C (componentOwner comp active) b))
      (combinedInc incBase incDoor) (combinedCap kapBase kapDoor) := by
  classical
  have hdemand0 :
      ∀ e : E0 O D, 0 ≤ demand G s C comp active e := by
    intro e
    simpa [demand, blockLoad] using
      load_nonneg Finset.univ blockWeight
        (fun b => deltaB G s (blockSet C (componentOwner comp active) b))
        (by intro b hb; norm_num [blockWeight]) e.1
  have hflow_exists :=
    capacitatedBipartiteFlow_exists
      (fun e : E0 O D => demand G s C comp active e)
      kapBase
      (fun e : E0 O D => fun j : JT => incBase e.1 j)
      hdemand0 hkapBase
      (by simpa [ActiveComponentBankHall] using hHall)
  let flow0 : E0 O D → JT → ℚ := hflow_exists.choose
  have hflow0_nonneg := hflow_exists.choose_spec.1
  have hflow0_support := hflow_exists.choose_spec.2.1
  have hflow0_route := hflow_exists.choose_spec.2.2.1
  have hflow0_cap := hflow_exists.choose_spec.2.2.2
  let qBase : Sym2 V → JT → ℚ := fun e j =>
    extendE0 O D (fun e0 => flow0 e0 j) e
  have hqBase_nonneg :
      ∀ e ∈ O, e ∉ D → ∀ j, 0 ≤ qBase e j := by
    intro e heO heD j
    simpa [qBase, extendE0, heO, heD] using
      hflow0_nonneg (⟨e, heO, heD⟩ : E0 O D) j
  have hroute :
      ∀ e ∈ O, e ∉ D →
        blockLoad G s C (componentOwner comp active) e ≤ ∑ j, qBase e j := by
    intro e heO heD
    let e0 : E0 O D := ⟨e, heO, heD⟩
    calc
      blockLoad G s C (componentOwner comp active) e =
          demand G s C comp active e0 := by simp [demand, e0]
      _ ≤ ∑ j, flow0 e0 j := hflow0_route e0
      _ = ∑ j, qBase e j := by
        apply Finset.sum_congr rfl
        intro j _
        simp [qBase, extendE0, heO, heD, e0]
  have hcap :
      ∀ j, (∑ e ∈ O, if e ∈ D then 0 else qBase e j) ≤ kapBase j := by
    intro j
    calc
      (∑ e ∈ O, if e ∈ D then 0 else qBase e j) =
          ∑ e ∈ O, extendE0 O D (fun e0 => flow0 e0 j) e := by
        apply Finset.sum_congr rfl
        intro e heO
        by_cases heD : e ∈ D <;>
          simp [qBase, extendE0, heO, heD]
      _ = ∑ e : E0 O D, flow0 e j :=
        sum_extendE0 O D (fun e => flow0 e j)
      _ ≤ kapBase j := hflow0_cap j
  have hincBase :
      ∀ e ∈ O, e ∉ D → ∀ j,
        0 < qBase e j → incBase e j := by
    intro e heO heD j hpos
    let e0 : E0 O D := ⟨e, heO, heD⟩
    by_contra hlegal
    have hzero : flow0 e0 j = 0 := hflow0_support e0 j hlegal
    have heq : qBase e j = flow0 e0 j := by
      simp [qBase, extendE0, heO, heD, e0]
    rw [heq, hzero] at hpos
    exact (lt_irrefl 0) hpos
  have hkap : ∀ j : BlockBankSink JT V,
      0 ≤ combinedCap kapBase kapDoor j := by
    intro j
    cases j with
    | inl j => exact hkapBase j
    | inr e => exact hkapDoor e
  apply certificate_of_blockCore_mixedDoorBankFlow
    G s C (componentOwner comp active) S F O D
    (combinedInc incBase incDoor) (combinedCap kapBase kapDoor) qBase
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
  · exact hqBase_nonneg
  · exact hroute
  · intro j
    simpa [combinedCap] using hcap j
  · intro e heO heD j hpos
    simpa [combinedInc] using hincBase e heO heD j hpos
  · intro e heD
    simpa [combinedInc] using hincDoor e heD
  · intro e heD
    simpa [combinedCap] using hdoor e heD

end Graph

end Ell5ActiveComponentBankHall
end Erdos23Delta0
