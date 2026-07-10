import Erdos23Delta0.Ell5BlockSingleton

/-!
# Partition cuts with mixed Door and endpoint-flow routing

This combines the two canonical primal constructions.  A finite partition of
the core supplies half-weight block cuts.  Boundary edges in `D` use their own
Door sink; every other off-support edge may route its actual block-cut load
fractionally to legal core vertex sinks.

Choosing singleton blocks recovers endpoint-flow singleton routing.  Choosing
off-support components makes every same-component edge have zero load.  A
mixed owner partition can therefore use singleton blocks only in components
which contain a selected bad edge and leave all other components collapsed.
-/

namespace Erdos23Delta0
namespace Ell5BlockEndpointFlow

open Finset MaxCutVertexIneq
open Ell5FullBankInterface Ell5FullBankAssignedSink
open Ell5BlockSingleton

variable {V Block : Type*} [DecidableEq V]
  [Fintype Block] [DecidableEq Block]

section Graph

variable (G : SimpleGraph V) [Fintype G.edgeSet]

/-- Door routing on `D`; arbitrary core-vertex routing elsewhere. -/
def mixedDoorBlockFlowQ
    (s : V → Bool) (C : Finset V) (block : V → Block)
    (D : Finset (Sym2 V)) (flow : Sym2 V → V → ℚ)
    (c : Sym2 V) : V ⊕ Sym2 V → ℚ
  | Sum.inl x =>
      if c ∈ D then 0 else if x ∈ C then flow c x else 0
  | Sum.inr e =>
      if c ∈ D then
        if c = e then blockLoad G s C block c else 0
      else 0

/-- General partition-cut certificate with mixed Door and fractional endpoint
flow.  The caller need only cover the actual `blockLoad` of each non-Door
edge; same-block edges may use the zero flow because their load is zero. -/
noncomputable def certificate_of_blockCore_mixedDoorEndpointFlow
    [Fintype V]
    (s : V → Bool) (C : Finset V) (block : V → Block)
    (S F O D : Finset (Sym2 V))
    (inc : Sym2 V → (V ⊕ Sym2 V) → Prop)
    (kap : (V ⊕ Sym2 V) → ℚ)
    (flow : Sym2 V → V → ℚ)
    (hkap : ∀ j, 0 ≤ kap j)
    (hD : D ⊆ O)
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧
        e ∈ C.sym2 ∧ BlocksApart block e)
    (hF : ∀ e ∈ F, e ∈ G.edgeFinset ∧ edgeCut s e = true)
    (hflow_nonneg : ∀ e ∈ O, e ∉ D → ∀ x ∈ C, 0 ≤ flow e x)
    (hflow_route : ∀ e ∈ O, e ∉ D →
      blockLoad G s C block e ≤ ∑ x ∈ C, flow e x)
    (hflow_cap : ∀ x ∈ C,
      (∑ e ∈ O, if e ∈ D then 0 else flow e x) ≤ kap (Sum.inl x))
    (hincFlow : ∀ e ∈ O, e ∉ D → ∀ x ∈ C,
      0 < flow e x → inc e (Sum.inl x))
    (hincDoor : ∀ e ∈ D, inc e (Sum.inr e))
    (hdoor : ∀ e ∈ D, blockLoad G s C block e ≤ kap (Sum.inr e)) :
    FullBankRelaxedCoverCert S F O Finset.univ Finset.univ
      (fun b => deltaM G s (blockSet C block b))
      (fun b => deltaB G s (blockSet C block b)) inc kap where
  lam := blockWeight
  q := mixedDoorBlockFlowQ G s C block D flow
  hlam := by intro b hb; norm_num [blockWeight]
  hq := by
    intro e he j hj
    cases j with
    | inl x =>
        by_cases heD : e ∈ D
        · simp [mixedDoorBlockFlowQ, heD]
        · by_cases hx : x ∈ C
          · simpa [mixedDoorBlockFlowQ, heD, hx] using
              hflow_nonneg e he heD x hx
          · simp [mixedDoorBlockFlowQ, heD, hx]
    | inr d =>
        by_cases heD : e ∈ D
        · by_cases hed : e = d
          · subst d
            simpa [mixedDoorBlockFlowQ, heD, blockLoad] using
              load_nonneg Finset.univ blockWeight
                (fun b => deltaB G s (blockSet C block b))
                (by intro b hb; norm_num [blockWeight]) e
          · simp [mixedDoorBlockFlowQ, heD, hed]
        · simp [mixedDoorBlockFlowQ, heD]
  hkap := by intro j hj; exact hkap j
  hcov := by
    intro e he
    obtain ⟨heG, hbad, hcore, hapart⟩ := hS e he
    exact le_of_eq (block_bad_coverage G s C block heG hbad hcore hapart).symm
  hcong := by
    intro e he
    obtain ⟨heG, hcut⟩ := hF e he
    exact block_cut_load_le_one G s C block heG hcut
  hroute := by
    intro e he
    change blockLoad G s C block e ≤ _
    rw [Fintype.sum_sum_type]
    by_cases heD : e ∈ D
    · simp [mixedDoorBlockFlowQ, heD]
    · calc
        blockLoad G s C block e ≤ ∑ x ∈ C, flow e x :=
          hflow_route e he heD
        _ = _ := by simp [mixedDoorBlockFlowQ, heD]
  hcap := by
    intro j hj
    cases j with
    | inl x =>
        by_cases hx : x ∈ C
        · simpa [mixedDoorBlockFlowQ, hx] using hflow_cap x hx
        · simpa [mixedDoorBlockFlowQ, hx] using hkap (Sum.inl x)
    | inr d =>
        by_cases hd : d ∈ D
        · have hdO : d ∈ O := hD hd
          calc
            (∑ e ∈ O,
                mixedDoorBlockFlowQ G s C block D flow e (Sum.inr d)) =
                blockLoad G s C block d := by
                  rw [Finset.sum_eq_single d]
                  · simp [mixedDoorBlockFlowQ, hd]
                  · intro e he hne
                    simp [mixedDoorBlockFlowQ, hne]
                  · intro hnot
                    exact False.elim (hnot hdO)
            _ ≤ kap (Sum.inr d) := hdoor d hd
        · simpa [mixedDoorBlockFlowQ, hd] using hkap (Sum.inr d)
  hqinc := by
    intro e he j hj hpos
    cases j with
    | inl x =>
        by_cases heD : e ∈ D
        · simp [mixedDoorBlockFlowQ, heD] at hpos
        · by_cases hx : x ∈ C
          · apply hincFlow e he heD x hx
            simpa [mixedDoorBlockFlowQ, heD, hx] using hpos
          · simp [mixedDoorBlockFlowQ, heD, hx] at hpos
    | inr d =>
        by_cases heD : e ∈ D
        · by_cases hed : e = d
          · simpa [hed] using hincDoor e heD
          · simp [mixedDoorBlockFlowQ, heD, hed] at hpos
        · simp [mixedDoorBlockFlowQ, heD] at hpos

end Graph

end Ell5BlockEndpointFlow
end Erdos23Delta0
