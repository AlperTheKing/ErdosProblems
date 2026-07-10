import Erdos23Delta0.Ell5BlockSingleton
import Erdos23Delta0.Ell5FullBankInterface

/-!
# Partition cuts with generic bank-flow routing

A finite block partition supplies the usual half-weight cuts. Non-Door
off-support load may route to any finite family of bank sinks; Door edges use
their own edge-indexed sinks in a disjoint summand.
-/

namespace Erdos23Delta0
namespace Ell5BlockBankFlow

open Finset MaxCutVertexIneq
open Ell5FullBankInterface Ell5FullBankAssignedSink Ell5BlockSingleton

variable {V Block JT : Type*} [DecidableEq V]
  [Fintype Block] [DecidableEq Block] [Fintype JT] [DecidableEq JT]

/-- Generic non-Door bank sinks together with edge-specific Door sinks. -/
abbrev BlockBankSink (JT V : Type*) := JT ⊕ Sym2 V

section Graph

variable (G : SimpleGraph V) [Fintype G.edgeSet]

/-- Route non-Door edges through `qBase`; route each Door edge only to its
own edge-indexed sink. -/
def mixedDoorBlockBankQ
    (s : V → Bool) (C : Finset V) (block : V → Block)
    (D : Finset (Sym2 V)) (qBase : Sym2 V → JT → ℚ)
    (c : Sym2 V) : BlockBankSink JT V → ℚ
  | Sum.inl j => if c ∈ D then 0 else qBase c j
  | Sum.inr e =>
      if c ∈ D then
        if c = e then blockLoad G s C block c else 0
      else 0

/-- General partition-cut certificate with arbitrary finite non-Door bank
sinks and edge-specific Door sinks. -/
noncomputable def certificate_of_blockCore_mixedDoorBankFlow
    [Fintype V]
    (s : V → Bool) (C : Finset V) (block : V → Block)
    (S F O D : Finset (Sym2 V))
    (inc : Sym2 V → BlockBankSink JT V → Prop)
    (kap : BlockBankSink JT V → ℚ)
    (qBase : Sym2 V → JT → ℚ)
    (hkap : ∀ j, 0 ≤ kap j)
    (hD : D ⊆ O)
    (hS : ∀ e ∈ S,
      e ∈ G.edgeFinset ∧ edgeCut s e = false ∧
        e ∈ C.sym2 ∧ BlocksApart block e)
    (hF : ∀ e ∈ F, e ∈ G.edgeFinset ∧ edgeCut s e = true)
    (hqBase_nonneg : ∀ e ∈ O, e ∉ D → ∀ j, 0 ≤ qBase e j)
    (hroute : ∀ e ∈ O, e ∉ D →
      blockLoad G s C block e ≤ ∑ j, qBase e j)
    (hcap : ∀ j,
      (∑ e ∈ O, if e ∈ D then 0 else qBase e j) ≤ kap (Sum.inl j))
    (hincBase : ∀ e ∈ O, e ∉ D → ∀ j,
      0 < qBase e j → inc e (Sum.inl j))
    (hincDoor : ∀ e ∈ D, inc e (Sum.inr e))
    (hdoor : ∀ e ∈ D,
      blockLoad G s C block e ≤ kap (Sum.inr e)) :
    FullBankRelaxedCoverCert S F O Finset.univ Finset.univ
      (fun b => deltaM G s (blockSet C block b))
      (fun b => deltaB G s (blockSet C block b)) inc kap where
  lam := blockWeight
  q := mixedDoorBlockBankQ G s C block D qBase
  hlam := by intro b hb; norm_num [blockWeight]
  hq := by
    intro e he j hj
    cases j with
    | inl j =>
        by_cases heD : e ∈ D
        · simp [mixedDoorBlockBankQ, heD]
        · simpa [mixedDoorBlockBankQ, heD] using
            hqBase_nonneg e he heD j
    | inr d =>
        by_cases heD : e ∈ D
        · by_cases hed : e = d
          · subst d
            simpa [mixedDoorBlockBankQ, heD, blockLoad] using
              load_nonneg Finset.univ blockWeight
                (fun b => deltaB G s (blockSet C block b))
                (by intro b hb; norm_num [blockWeight]) e
          · simp [mixedDoorBlockBankQ, heD, hed]
        · simp [mixedDoorBlockBankQ, heD]
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
    · simp [mixedDoorBlockBankQ, heD]
    · calc
        blockLoad G s C block e ≤ ∑ j, qBase e j := hroute e he heD
        _ = _ := by simp [mixedDoorBlockBankQ, heD]
  hcap := by
    intro j hj
    cases j with
    | inl j =>
        simpa [mixedDoorBlockBankQ] using hcap j
    | inr d =>
        by_cases hd : d ∈ D
        · have hdO : d ∈ O := hD hd
          calc
            (∑ e ∈ O,
                mixedDoorBlockBankQ G s C block D qBase e (Sum.inr d)) =
                blockLoad G s C block d := by
                  rw [Finset.sum_eq_single d]
                  · simp [mixedDoorBlockBankQ, hd]
                  · intro e he hne
                    simp [mixedDoorBlockBankQ, hne]
                  · intro hnot
                    exact False.elim (hnot hdO)
            _ ≤ kap (Sum.inr d) := hdoor d hd
        · simpa [mixedDoorBlockBankQ, hd] using hkap (Sum.inr d)
  hqinc := by
    intro e he j hj hpos
    cases j with
    | inl j =>
        by_cases heD : e ∈ D
        · simp [mixedDoorBlockBankQ, heD] at hpos
        · apply hincBase e he heD j
          simpa [mixedDoorBlockBankQ, heD] using hpos
    | inr d =>
        by_cases heD : e ∈ D
        · by_cases hed : e = d
          · simpa [hed] using hincDoor e heD
          · simp [mixedDoorBlockBankQ, heD, hed] at hpos
        · simp [mixedDoorBlockBankQ, heD] at hpos

end Graph

end Ell5BlockBankFlow
end Erdos23Delta0
