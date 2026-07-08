import Mathlib

/-!
# BankedCutDomination: the exact remaining gap#1 core, formally stated (2026-07-08)

GPT-Pro reply 3 (archive `GAP1_SSE_RELAXEDCUTCOVER_GPTPRO.md`): eliminating the sink prices δ from the Farkas
dual (cheapest legal spend per sink = the max off-support price it must cover) reduces "no dual certificate" to
the single inequality **BankedCutDomination**:

    ∀ α, β, γ ≥ 0 satisfying per-cut price domination (D1) over the full family:
        Σ α  ≤  Σ_F β + BankCost(γ),        BankCost(γ) = Σ_j κ_j · max{γ_c : incidence (c,j)} (0 if none).

This module makes that reduction machine-checked: `sinkPrice`/`bankCost` definitions, their optimality
(`sinkPrice_le`, `le_sinkPrice`), the Prop `BankedCutDomination`, the dual-certificate Prop `IsDualCert`, and the
exact equivalence `dualCert_iff_not_bankedCutDomination`. Together with `RelaxedCoverDuality` (weak duality) and
`RelaxedCoverSkeleton` (L1+L2), the entire gap#1 dual frame is compiled with `BankedCutDomination` as the single
named open hypothesis (= L3 = the wall). No `sorry`/`admit`/`native_decide`; axiom-probe expected
`⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace BankedCutDominationCore

open Finset

variable {R E JT ι : Type*} [DecidableEq R] [DecidableEq E]

open Classical in
/-- The price a sink `j` must charge to cover all off-support edges allowed to spend it: the maximum allowed
    `γ`-price (and at least `0`). -/
noncomputable def sinkPrice (O : Finset E) (inc : E → JT → Prop) (gam : E → ℚ) (j : JT) : ℚ :=
  (insert (0 : ℚ) ((O.filter fun c => inc c j).image gam)).max'
    (Finset.insert_nonempty _ _)

open Classical in
/-- δ-eliminated bank cost of a price system `γ`: each sink pays its capacity times its `sinkPrice`. -/
noncomputable def bankCost (J : Finset JT) (kap : JT → ℚ) (O : Finset E)
    (inc : E → JT → Prop) (gam : E → ℚ) : ℚ :=
  ∑ j ∈ J, kap j * sinkPrice O inc gam j

theorem sinkPrice_nonneg (O : Finset E) (inc : E → JT → Prop) (gam : E → ℚ) (j : JT) :
    0 ≤ sinkPrice O inc gam j := by
  classical
  exact Finset.le_max' _ _ (Finset.mem_insert_self _ _)

/-- The sink price covers every allowed edge price. -/
theorem le_sinkPrice (O : Finset E) (inc : E → JT → Prop) (gam : E → ℚ) {c : E} {j : JT}
    (hc : c ∈ O) (hinc : inc c j) :
    gam c ≤ sinkPrice O inc gam j := by
  classical
  refine Finset.le_max' _ _ ?_
  exact Finset.mem_insert_of_mem
    (Finset.mem_image_of_mem gam (Finset.mem_filter.mpr ⟨hc, hinc⟩))

/-- `sinkPrice` is the CHEAPEST legal sink price: any `d ≥ 0` dominating all allowed edge prices dominates it. -/
theorem sinkPrice_le (O : Finset E) (inc : E → JT → Prop) (gam : E → ℚ) {j : JT} {d : ℚ}
    (hd : 0 ≤ d) (h : ∀ c ∈ O, inc c j → gam c ≤ d) :
    sinkPrice O inc gam j ≤ d := by
  classical
  refine Finset.max'_le _ _ _ ?_
  intro x hx
  rcases Finset.mem_insert.mp hx with rfl | hx
  · exact hd
  · obtain ⟨c, hc, rfl⟩ := Finset.mem_image.mp hx
    obtain ⟨hcO, hcInc⟩ := Finset.mem_filter.mp hc
    exact h c hcO hcInc

/-- **The wall, as a Prop.** Every nonnegative price system `(α, β, γ)` satisfying per-cut price domination (D1)
    over the family `K` is globally paid by support prices plus the δ-eliminated bank cost. -/
def BankedCutDomination (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E) (inc : E → JT → Prop) (kap : JT → ℚ) : Prop :=
  ∀ alpha : R → ℚ, ∀ beta : E → ℚ, ∀ gam : E → ℚ,
    (∀ r ∈ S, 0 ≤ alpha r) → (∀ c ∈ F, 0 ≤ beta c) → (∀ c ∈ O, 0 ≤ gam c) →
    (∀ k ∈ K, (∑ r ∈ S, if r ∈ sep k then alpha r else 0)
        ≤ (∑ c ∈ F, if c ∈ dB k then beta c else 0) + ∑ c ∈ O, if c ∈ dB k then gam c else 0) →
    (∑ r ∈ S, alpha r) ≤ (∑ c ∈ F, beta c) + bankCost J kap O inc gam

/-- A Farkas dual certificate: nonnegative prices with per-cut domination (D1), bank-coverability (D2), and
    strict objective violation (D3). -/
def IsDualCert (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E) (inc : E → JT → Prop) (kap : JT → ℚ)
    (alpha : R → ℚ) (beta : E → ℚ) (gam : E → ℚ) (del : JT → ℚ) : Prop :=
  (∀ r ∈ S, 0 ≤ alpha r) ∧ (∀ c ∈ F, 0 ≤ beta c) ∧ (∀ c ∈ O, 0 ≤ gam c) ∧
  (∀ j ∈ J, 0 ≤ del j) ∧
  (∀ k ∈ K, (∑ r ∈ S, if r ∈ sep k then alpha r else 0)
      ≤ (∑ c ∈ F, if c ∈ dB k then beta c else 0) + ∑ c ∈ O, if c ∈ dB k then gam c else 0) ∧
  (∀ c ∈ O, ∀ j ∈ J, inc c j → gam c ≤ del j) ∧
  ((∑ c ∈ F, beta c) + (∑ j ∈ J, kap j * del j) < ∑ r ∈ S, alpha r)

/-- **δ-elimination equivalence.** A dual certificate exists iff BankedCutDomination FAILS. Forward: the
    certificate's `δ` is a legal sink pricing, so `bankCost ≤ Σ κδ` and D3 contradicts domination. Backward: a
    violating `(α,β,γ)` yields the certificate with the optimal prices `δ_j := sinkPrice j`. Needs `κ ≥ 0`. -/
theorem dualCert_iff_not_bankedCutDomination
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E) (inc : E → JT → Prop) (kap : JT → ℚ)
    (hkap : ∀ j ∈ J, 0 ≤ kap j) :
    (∃ alpha beta gam del, IsDualCert S F O J K sep dB inc kap alpha beta gam del)
      ↔ ¬ BankedCutDomination S F O J K sep dB inc kap := by
  constructor
  · rintro ⟨alpha, beta, gam, del, hA, hB, hG, hD, hD1, hD2, hD3⟩ hdom
    have hle := hdom alpha beta gam hA hB hG hD1
    have hbank : bankCost J kap O inc gam ≤ ∑ j ∈ J, kap j * del j := by
      refine Finset.sum_le_sum fun j hj => ?_
      refine mul_le_mul_of_nonneg_left ?_ (hkap j hj)
      exact sinkPrice_le O inc gam (hD j hj) (fun c hc hcj => hD2 c hc j hj hcj)
    linarith
  · intro hnot
    unfold BankedCutDomination at hnot
    push_neg at hnot
    obtain ⟨alpha, beta, gam, hA, hB, hG, hD1, hviol⟩ := hnot
    refine ⟨alpha, beta, gam, fun j => sinkPrice O inc gam j,
      hA, hB, hG, fun j _ => sinkPrice_nonneg O inc gam j, hD1,
      fun c hc j hj hcj => le_sinkPrice O inc gam hc hcj, ?_⟩
    unfold bankCost at hviol
    linarith

#print axioms sinkPrice_le
#print axioms le_sinkPrice
#print axioms dualCert_iff_not_bankedCutDomination

end BankedCutDominationCore
end Erdos23Delta0
