import Mathlib

/-!
# Relaxed cut-cover soundness: Hall defect ≤ external load ≤ bank (2026-07-08)

GPT-Pro's corrected Farkas/discharging mechanism for `Ell5SupportExpansion`/`FullBankHall`
(archive: `GAP1_SSE_RELAXEDCUTCOVER_GPTPRO.md`). A *relaxed cut-cover* for a row set `S` with support `F` is a
weighted family of cuts `(K, λ)` such that every row is separated with total weight ≥ 1 (coverage) and every
support edge carries weight ≤ 1 (in-support congestion); off-support cut edges may carry arbitrary load `r(c)`.
Summing the per-cut max-cut inequalities `|sep(U)| ≤ |δ_B(U)|` (weighted by `λ_U ≥ 0`) gives the **defect bound**

    |S| ≤ |F| + Σ_{c ∉ F} r(c)

— the Hall defect is paid by off-support (external) load. If additionally the external load is absorbed by the
legal bank (Door + vertexSlack + C5/base + Prune, NEVER the top cage's η_C), the full-bank Hall inequality follows
(**bank absorption**). This module machine-checks both steps at the abstract `Finset`/`ℚ` level; the graph
instantiation plugs `sep k := S-rows separated by U_k` and `dB k := δ_B(U_k)` with
`MaxCutVertexIneq.deltaM_card_le_deltaB_card` providing the per-cut hypothesis `hmcap`.

The OPEN core after this module is exactly the certificate-existence theorem `Ell5FullBankRelaxedCover_exists`
(a cover + bank assignment exists for every minimal full-closure obstruction) — everything else is compiled algebra.
No forbidden proof shortcuts; axiom-probe expected `⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace RelaxedCutCover

open Finset

variable {α β ι : Type*} [DecidableEq α] [DecidableEq β]

/-- The load a weighted cut family places on an edge `c`: total weight of the cuts whose boundary contains `c`. -/
def load (K : Finset ι) (lam : ι → ℚ) (dB : ι → Finset β) (c : β) : ℚ :=
  ∑ k ∈ K, if c ∈ dB k then lam k else 0

/-- **Relaxed cut-cover defect bound.** Rows `S`, support edges `F`, off-support edges `X` (disjoint from `F`),
    weighted cut family `(K, λ)` with: nonnegative weights, boundaries inside `F ∪ X`, the per-cut max-cut
    inequality `|sep k| ≤ |dB k|`, row coverage ≥ 1, in-support congestion ≤ 1. Then the Hall defect is bounded by
    the external load: `|S| ≤ |F| + Σ_{c ∈ X} load(c)`. -/
theorem relaxed_cutcover_defect_bound
    (S : Finset α) (F X : Finset β) (hFX : Disjoint F X)
    (K : Finset ι) (lam : ι → ℚ) (sep : ι → Finset α) (dB : ι → Finset β)
    (hlam : ∀ k ∈ K, 0 ≤ lam k)
    (hdB : ∀ k ∈ K, dB k ⊆ F ∪ X)
    (hmcap : ∀ k ∈ K, ((sep k).card : ℚ) ≤ ((dB k).card : ℚ))
    (hcov : ∀ e ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if e ∈ sep k then lam k else 0)
    (hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ 1) :
    (S.card : ℚ) ≤ (F.card : ℚ) + ∑ c ∈ X, load K lam dB c := by
  -- coverage: |S| ≤ Σ_e Σ_k λ·[e separated by k]
  have h1 : (S.card : ℚ) ≤ ∑ e ∈ S, ∑ k ∈ K, if e ∈ sep k then lam k else 0 := by
    calc (S.card : ℚ) = ∑ _e ∈ S, (1 : ℚ) := by
          rw [Finset.sum_const, nsmul_eq_mul, mul_one]
      _ ≤ _ := Finset.sum_le_sum hcov
  -- swap to cut side: Σ_k λ_k · |S-rows separated by k|
  have h2 : ∑ e ∈ S, ∑ k ∈ K, (if e ∈ sep k then lam k else 0)
      = ∑ k ∈ K, ((S.filter (fun e => e ∈ sep k)).card : ℚ) * lam k := by
    rw [Finset.sum_comm]
    refine Finset.sum_congr rfl fun k _ => ?_
    rw [← Finset.sum_filter, Finset.sum_const, nsmul_eq_mul]
  -- per-cut: |S-rows separated| ≤ |sep k| ≤ |dB k|, weighted by λ_k ≥ 0
  have h3 : ∀ k ∈ K, ((S.filter (fun e => e ∈ sep k)).card : ℚ) * lam k
      ≤ ((dB k).card : ℚ) * lam k := by
    intro k hk
    have hfilter : S.filter (fun e => e ∈ sep k) ⊆ sep k := fun x hx =>
      (Finset.mem_filter.mp hx).2
    have hcard : ((S.filter (fun e => e ∈ sep k)).card : ℚ) ≤ ((dB k).card : ℚ) :=
      le_trans (by exact_mod_cast Finset.card_le_card hfilter) (hmcap k hk)
    exact mul_le_mul_of_nonneg_right hcard (hlam k hk)
  -- resum the boundary side over edges: Σ_k λ_k·|dB k| = in-support congestion + external load
  have hperk : ∀ k ∈ K, ((dB k).card : ℚ) * lam k
      = ∑ c ∈ F ∪ X, if c ∈ dB k then lam k else 0 := by
    intro k hk
    rw [Finset.sum_ite_mem, Finset.inter_eq_right.mpr (hdB k hk), Finset.sum_const, nsmul_eq_mul]
  have h4 : ∑ k ∈ K, ((dB k).card : ℚ) * lam k
      = (∑ c ∈ F, ∑ k ∈ K, if c ∈ dB k then lam k else 0)
        + ∑ c ∈ X, ∑ k ∈ K, if c ∈ dB k then lam k else 0 := by
    calc ∑ k ∈ K, ((dB k).card : ℚ) * lam k
        = ∑ k ∈ K, ∑ c ∈ F ∪ X, if c ∈ dB k then lam k else 0 :=
          Finset.sum_congr rfl hperk
      _ = ∑ c ∈ F ∪ X, ∑ k ∈ K, if c ∈ dB k then lam k else 0 := Finset.sum_comm
      _ = _ := Finset.sum_union hFX
  -- in-support total ≤ |F| by congestion
  have h5 : (∑ c ∈ F, ∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ (F.card : ℚ) := by
    calc (∑ c ∈ F, ∑ k ∈ K, if c ∈ dB k then lam k else 0)
        ≤ ∑ _c ∈ F, (1 : ℚ) := Finset.sum_le_sum hcong
      _ = (F.card : ℚ) := by rw [Finset.sum_const, nsmul_eq_mul, mul_one]
  -- assemble
  have hmain : (S.card : ℚ) ≤ ∑ k ∈ K, ((dB k).card : ℚ) * lam k := by
    rw [h2] at h1
    exact le_trans h1 (Finset.sum_le_sum h3)
  rw [h4] at hmain
  have hload : ∑ c ∈ X, (∑ k ∈ K, if c ∈ dB k then lam k else 0) = ∑ c ∈ X, load K lam dB c :=
    rfl
  linarith [hmain, h5, hload ▸ le_refl (∑ c ∈ X, load K lam dB c)]

/-- **Bank absorption.** If moreover the (25-scaled) external load is within the legal bank capacity `B`
    (Door + vertexSlack + C5/base + Prune — never the top cage's `η_C`), the full-bank Hall inequality follows:
    `25·|S| ≤ 25·|F| + B`. With `B = 0` this is exactly the pure support expansion `|S| ≤ |F|`. -/
theorem hall_absorbed_of_bank
    (S : Finset α) (F X : Finset β) (hFX : Disjoint F X)
    (K : Finset ι) (lam : ι → ℚ) (sep : ι → Finset α) (dB : ι → Finset β)
    (hlam : ∀ k ∈ K, 0 ≤ lam k)
    (hdB : ∀ k ∈ K, dB k ⊆ F ∪ X)
    (hmcap : ∀ k ∈ K, ((sep k).card : ℚ) ≤ ((dB k).card : ℚ))
    (hcov : ∀ e ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if e ∈ sep k then lam k else 0)
    (hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ 1)
    (B : ℚ) (hbank : 25 * (∑ c ∈ X, load K lam dB c) ≤ B) :
    25 * (S.card : ℚ) ≤ 25 * (F.card : ℚ) + B := by
  have h := relaxed_cutcover_defect_bound S F X hFX K lam sep dB hlam hdB hmcap hcov hcong
  linarith

/-- **Pure expansion from a zero-external-load cover.** A relaxed cut-cover whose external load vanishes yields the
    unbanked Hall expansion `|S| ≤ |F|` directly (the strict cut-cover special case, subsumed). -/
theorem expansion_of_zero_load
    (S : Finset α) (F X : Finset β) (hFX : Disjoint F X)
    (K : Finset ι) (lam : ι → ℚ) (sep : ι → Finset α) (dB : ι → Finset β)
    (hlam : ∀ k ∈ K, 0 ≤ lam k)
    (hdB : ∀ k ∈ K, dB k ⊆ F ∪ X)
    (hmcap : ∀ k ∈ K, ((sep k).card : ℚ) ≤ ((dB k).card : ℚ))
    (hcov : ∀ e ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if e ∈ sep k then lam k else 0)
    (hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ 1)
    (hzero : ∑ c ∈ X, load K lam dB c = 0) :
    (S.card : ℚ) ≤ (F.card : ℚ) := by
  have h := relaxed_cutcover_defect_bound S F X hFX K lam sep dB hlam hdB hmcap hcov hcong
  rw [hzero, add_zero] at h
  exact h


end RelaxedCutCover
end Erdos23Delta0
