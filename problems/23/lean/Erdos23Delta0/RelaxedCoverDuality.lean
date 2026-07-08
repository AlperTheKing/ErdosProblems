import Mathlib
import Erdos23Delta0.RelaxedCutCover

/-!
# Weak duality for the relaxed-cover + bank LP (2026-07-08)

GPT-Pro reply 3 (archive `GAP1_SSE_RELAXEDCUTCOVER_GPTPRO.md`): a Farkas dual certificate
`(α, β, γ, δ)` — per-cut price domination (D1), bank-coverability of off-support prices (D2, here folded into
the support condition `hqsupp` on the primal flows), and strict objective violation (D3) — refutes the existence
of a primal cover + bank certificate. This module machine-checks that **weak duality**: a primal certificate and
a dual certificate cannot coexist (`relaxed_cover_weak_duality : ... → False`).

Consequences compiled here:
* any claimed decisive falsifier (dual certificate on a cage-legal config) is machine-checkably incompatible
  with cover existence — the verification path for `_claude_rcc_dual_verify.py` outputs;
* `bankCost_le_of_pointwise` — the δ-elimination step (`BankCost(γ) = Σ_j κ_j · max{γ_c}` is optimal) is
  represented through the flow-supported form.

No `sorry`/`admit`/`native_decide`; axiom-probe expected `⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace RelaxedCoverDuality

open Finset RelaxedCutCover

variable {R E JT ι : Type*} [DecidableEq R] [DecidableEq E]

/-- **Weak duality.** A primal certificate (cover `lam` with coverage ≥ 1, congestion ≤ 1, flows `q` routing the
    off-support load within sink capacities `kap`) and a dual certificate (`alpha, beta, gam, del ≥ 0` with per-cut
    price domination D1 and strict objective violation D3) cannot coexist. `hqsupp` encodes D2 along the support
    of the flows: wherever `q c j > 0` the edge price is dominated by the sink price. -/
theorem relaxed_cover_weak_duality
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (lam : ι → ℚ) (q : E → JT → ℚ)
    (alpha : R → ℚ) (beta : E → ℚ) (gam : E → ℚ) (del : JT → ℚ) (kap : JT → ℚ)
    (hlam : ∀ k ∈ K, 0 ≤ lam k)
    (halpha : ∀ e ∈ S, 0 ≤ alpha e)
    (hbeta : ∀ c ∈ F, 0 ≤ beta c)
    (hgam : ∀ c ∈ O, 0 ≤ gam c)
    (hdel : ∀ j ∈ J, 0 ≤ del j)
    (hq : ∀ c ∈ O, ∀ j ∈ J, 0 ≤ q c j)
    -- primal certificate
    (hcov : ∀ e ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if e ∈ sep k then lam k else 0)
    (hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ 1)
    (hroute : ∀ c ∈ O, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ ∑ j ∈ J, q c j)
    (hcap : ∀ j ∈ J, (∑ c ∈ O, q c j) ≤ kap j)
    -- D2 along the flow support
    (hqsupp : ∀ c ∈ O, ∀ j ∈ J, 0 < q c j → gam c ≤ del j)
    -- dual certificate
    (hD1 : ∀ k ∈ K, (∑ e ∈ S, if e ∈ sep k then alpha e else 0)
        ≤ (∑ c ∈ F, if c ∈ dB k then beta c else 0) + ∑ c ∈ O, if c ∈ dB k then gam c else 0)
    (hD3 : (∑ c ∈ F, beta c) + (∑ j ∈ J, kap j * del j) < ∑ e ∈ S, alpha e) :
    False := by
  -- edge-side swap helper: Σ_k (Σ_{c∈T} ite·w) · λ_k = Σ_{c∈T} w_c · (Σ_k ite·λ_k)
  have hedge : ∀ (T : Finset E) (w : E → ℚ),
      (∑ k ∈ K, (∑ c ∈ T, if c ∈ dB k then w c else 0) * lam k)
      = ∑ c ∈ T, w c * (∑ k ∈ K, if c ∈ dB k then lam k else 0) := by
    intro T w
    calc (∑ k ∈ K, (∑ c ∈ T, if c ∈ dB k then w c else 0) * lam k)
        = ∑ k ∈ K, ∑ c ∈ T, (if c ∈ dB k then w c else 0) * lam k := by
          refine Finset.sum_congr rfl fun k _ => Finset.sum_mul ..
      _ = ∑ c ∈ T, ∑ k ∈ K, (if c ∈ dB k then w c else 0) * lam k := Finset.sum_comm
      _ = ∑ c ∈ T, w c * (∑ k ∈ K, if c ∈ dB k then lam k else 0) := by
          refine Finset.sum_congr rfl fun c _ => ?_
          rw [Finset.mul_sum]
          refine Finset.sum_congr rfl fun k _ => ?_
          by_cases h : c ∈ dB k <;> simp [h]
  -- Step 1: coverage lifts Σα into the weighted family
  have h1 : (∑ e ∈ S, alpha e)
      ≤ ∑ e ∈ S, alpha e * (∑ k ∈ K, if e ∈ sep k then lam k else 0) := by
    refine Finset.sum_le_sum fun e he => ?_
    have := mul_le_mul_of_nonneg_left (hcov e he) (halpha e he)
    simpa using this
  -- Step 2: swap to cut side and factor λ_k
  have h2 : (∑ e ∈ S, alpha e * (∑ k ∈ K, if e ∈ sep k then lam k else 0))
      = ∑ k ∈ K, (∑ e ∈ S, if e ∈ sep k then alpha e else 0) * lam k := by
    calc (∑ e ∈ S, alpha e * (∑ k ∈ K, if e ∈ sep k then lam k else 0))
        = ∑ e ∈ S, ∑ k ∈ K, alpha e * (if e ∈ sep k then lam k else 0) := by
          refine Finset.sum_congr rfl fun e _ => Finset.mul_sum ..
      _ = ∑ k ∈ K, ∑ e ∈ S, alpha e * (if e ∈ sep k then lam k else 0) := Finset.sum_comm
      _ = ∑ k ∈ K, (∑ e ∈ S, if e ∈ sep k then alpha e else 0) * lam k := by
          refine Finset.sum_congr rfl fun k _ => ?_
          rw [Finset.sum_mul]
          refine Finset.sum_congr rfl fun e _ => ?_
          by_cases h : e ∈ sep k <;> simp [h]
  -- Step 3: apply D1 per cut, weighted by λ_k ≥ 0
  have h3 : (∑ k ∈ K, (∑ e ∈ S, if e ∈ sep k then alpha e else 0) * lam k)
      ≤ ∑ k ∈ K, ((∑ c ∈ F, if c ∈ dB k then beta c else 0)
          + ∑ c ∈ O, if c ∈ dB k then gam c else 0) * lam k := by
    refine Finset.sum_le_sum fun k hk => ?_
    exact mul_le_mul_of_nonneg_right (hD1 k hk) (hlam k hk)
  -- Step 4: split and resum edge-side
  have h4 : (∑ k ∈ K, ((∑ c ∈ F, if c ∈ dB k then beta c else 0)
          + ∑ c ∈ O, if c ∈ dB k then gam c else 0) * lam k)
      = (∑ c ∈ F, beta c * (∑ k ∈ K, if c ∈ dB k then lam k else 0))
        + ∑ c ∈ O, gam c * (∑ k ∈ K, if c ∈ dB k then lam k else 0) := by
    calc (∑ k ∈ K, ((∑ c ∈ F, if c ∈ dB k then beta c else 0)
            + ∑ c ∈ O, if c ∈ dB k then gam c else 0) * lam k)
        = (∑ k ∈ K, (∑ c ∈ F, if c ∈ dB k then beta c else 0) * lam k)
          + ∑ k ∈ K, (∑ c ∈ O, if c ∈ dB k then gam c else 0) * lam k := by
          rw [← Finset.sum_add_distrib]
          refine Finset.sum_congr rfl fun k _ => ?_
          rw [add_mul]
      _ = _ := by rw [hedge F beta, hedge O gam]
  -- Step 5a: support side bounded by Σβ via congestion
  have h5a : (∑ c ∈ F, beta c * (∑ k ∈ K, if c ∈ dB k then lam k else 0)) ≤ ∑ c ∈ F, beta c := by
    refine Finset.sum_le_sum fun c hc => ?_
    have := mul_le_mul_of_nonneg_left (hcong c hc) (hbeta c hc)
    simpa using this
  -- Step 5b: off-support side bounded by the bank via routing, D2-on-support, capacity
  have h5b : (∑ c ∈ O, gam c * (∑ k ∈ K, if c ∈ dB k then lam k else 0))
      ≤ ∑ j ∈ J, kap j * del j := by
    have hb1 : (∑ c ∈ O, gam c * (∑ k ∈ K, if c ∈ dB k then lam k else 0))
        ≤ ∑ c ∈ O, gam c * (∑ j ∈ J, q c j) := by
      refine Finset.sum_le_sum fun c hc => ?_
      exact mul_le_mul_of_nonneg_left (hroute c hc) (hgam c hc)
    have hb2 : (∑ c ∈ O, gam c * (∑ j ∈ J, q c j))
        = ∑ c ∈ O, ∑ j ∈ J, gam c * q c j := by
      refine Finset.sum_congr rfl fun c _ => Finset.mul_sum ..
    have hb3 : (∑ c ∈ O, ∑ j ∈ J, gam c * q c j)
        ≤ ∑ c ∈ O, ∑ j ∈ J, del j * q c j := by
      refine Finset.sum_le_sum fun c hc => Finset.sum_le_sum fun j hj => ?_
      rcases lt_or_eq_of_le (hq c hc j hj) with hpos | hzero
      · exact mul_le_mul_of_nonneg_right (hqsupp c hc j hj hpos) (le_of_lt hpos)
      · rw [← hzero, mul_zero, mul_zero]
    have hb4 : (∑ c ∈ O, ∑ j ∈ J, del j * q c j) = ∑ j ∈ J, del j * (∑ c ∈ O, q c j) := by
      rw [Finset.sum_comm]
      refine Finset.sum_congr rfl fun j _ => ?_
      rw [Finset.mul_sum]
    have hb5 : (∑ j ∈ J, del j * (∑ c ∈ O, q c j)) ≤ ∑ j ∈ J, del j * kap j := by
      refine Finset.sum_le_sum fun j hj => ?_
      exact mul_le_mul_of_nonneg_left (hcap j hj) (hdel j hj)
    have hb6 : (∑ j ∈ J, del j * kap j) = ∑ j ∈ J, kap j * del j := by
      refine Finset.sum_congr rfl fun j _ => mul_comm _ _
    calc (∑ c ∈ O, gam c * (∑ k ∈ K, if c ∈ dB k then lam k else 0))
        ≤ ∑ c ∈ O, gam c * (∑ j ∈ J, q c j) := hb1
      _ = ∑ c ∈ O, ∑ j ∈ J, gam c * q c j := hb2
      _ ≤ ∑ c ∈ O, ∑ j ∈ J, del j * q c j := hb3
      _ = ∑ j ∈ J, del j * (∑ c ∈ O, q c j) := hb4
      _ ≤ ∑ j ∈ J, del j * kap j := hb5
      _ = ∑ j ∈ J, kap j * del j := hb6
  -- assemble: Σα ≤ Σβ + Σκδ, contradicting D3
  have hfinal : (∑ e ∈ S, alpha e) ≤ (∑ c ∈ F, beta c) + ∑ j ∈ J, kap j * del j := by
    calc (∑ e ∈ S, alpha e)
        ≤ ∑ e ∈ S, alpha e * (∑ k ∈ K, if e ∈ sep k then lam k else 0) := h1
      _ = ∑ k ∈ K, (∑ e ∈ S, if e ∈ sep k then alpha e else 0) * lam k := h2
      _ ≤ ∑ k ∈ K, ((∑ c ∈ F, if c ∈ dB k then beta c else 0)
            + ∑ c ∈ O, if c ∈ dB k then gam c else 0) * lam k := h3
      _ = (∑ c ∈ F, beta c * (∑ k ∈ K, if c ∈ dB k then lam k else 0))
            + ∑ c ∈ O, gam c * (∑ k ∈ K, if c ∈ dB k then lam k else 0) := h4
      _ ≤ (∑ c ∈ F, beta c) + ∑ j ∈ J, kap j * del j := add_le_add h5a h5b
  linarith

#print axioms relaxed_cover_weak_duality

end RelaxedCoverDuality
end Erdos23Delta0
