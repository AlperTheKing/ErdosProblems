import Mathlib

/-!
# No-dual skeleton, provable layers: L1 quotient payment + L2 closure localization (2026-07-08)

GPT-Pro reply 5 (archive `GAP1_SSE_RELAXEDCUTCOVER_GPTPRO.md`): of the three-lemma skeleton for
`BankedCutDomination`, L1 and L2 are provable now at the abstract `Finset`/`ℚ` level.

* **L1 `quotient_cuts_pay_alpha`** — for a *zero-γ* (quotient-style) cut family `KQ` (boundaries inside the
  support `F`, so the D1 price-domination inequalities carry no γ term), any nonnegative fractional cover of the
  rows by `KQ` pays the whole row-price mass out of the weighted support boundaries. No β-congestion bound is
  used: payment is via D1 directly.
* **L2 `remaining_alpha_le_closure_alpha`** — interface form: the only graph-level content of "remaining α lies
  in the full escape closure" is the membership fact `hRemClosure` (rows not separated by any quotient cut belong
  to the closure); the α-mass comparison is then pure `Finset` algebra.
* **`alpha_paid_or_in_closure`** — the combined skeleton shape: the whole row-price mass is bounded by the
  quotient payment plus the closure α-mass. What remains open beyond this module is exactly L3
  (`full_closure_bank_dominates_dual` = BankedCutDomination for the closure part = the wall).

No forbidden proof shortcuts; axiom-probe expected `⊆ {propext, Classical.choice, Quot.sound}`.
-/

namespace Erdos23Delta0
namespace RelaxedCoverSkeleton

open Finset

variable {R E ι : Type*} [DecidableEq R] [DecidableEq E]

/-- **L1: quotient cuts pay the α-mass they cover.** `KQ` is a zero-γ family: its D1 inequalities bound the
    separated row prices by support-boundary β-prices alone. Given a nonnegative fractional row cover by `KQ`,
    the total row price is paid by the weighted boundary prices. -/
theorem quotient_cuts_pay_alpha
    (S : Finset R) (F : Finset E) (KQ : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (alpha : R → ℚ) (beta : E → ℚ) (lam : ι → ℚ)
    (halpha : ∀ r ∈ S, 0 ≤ alpha r)
    (hlam : ∀ k ∈ KQ, 0 ≤ lam k)
    (hcov : ∀ r ∈ S, (1 : ℚ) ≤ ∑ k ∈ KQ, if r ∈ sep k then lam k else 0)
    (hD1 : ∀ k ∈ KQ, (∑ r ∈ S, if r ∈ sep k then alpha r else 0)
        ≤ ∑ c ∈ F, if c ∈ dB k then beta c else 0) :
    (∑ r ∈ S, alpha r) ≤ ∑ k ∈ KQ, lam k * ∑ c ∈ F, if c ∈ dB k then beta c else 0 := by
  have h1 : (∑ r ∈ S, alpha r)
      ≤ ∑ r ∈ S, alpha r * (∑ k ∈ KQ, if r ∈ sep k then lam k else 0) := by
    refine Finset.sum_le_sum fun r hr => ?_
    have := mul_le_mul_of_nonneg_left (hcov r hr) (halpha r hr)
    simpa using this
  have h2 : (∑ r ∈ S, alpha r * (∑ k ∈ KQ, if r ∈ sep k then lam k else 0))
      = ∑ k ∈ KQ, (∑ r ∈ S, if r ∈ sep k then alpha r else 0) * lam k := by
    calc (∑ r ∈ S, alpha r * (∑ k ∈ KQ, if r ∈ sep k then lam k else 0))
        = ∑ r ∈ S, ∑ k ∈ KQ, alpha r * (if r ∈ sep k then lam k else 0) := by
          refine Finset.sum_congr rfl fun r _ => Finset.mul_sum ..
      _ = ∑ k ∈ KQ, ∑ r ∈ S, alpha r * (if r ∈ sep k then lam k else 0) := Finset.sum_comm
      _ = ∑ k ∈ KQ, (∑ r ∈ S, if r ∈ sep k then alpha r else 0) * lam k := by
          refine Finset.sum_congr rfl fun k _ => ?_
          rw [Finset.sum_mul]
          refine Finset.sum_congr rfl fun r _ => ?_
          by_cases h : r ∈ sep k <;> simp [h]
  have h3 : (∑ k ∈ KQ, (∑ r ∈ S, if r ∈ sep k then alpha r else 0) * lam k)
      ≤ ∑ k ∈ KQ, (∑ c ∈ F, if c ∈ dB k then beta c else 0) * lam k := by
    refine Finset.sum_le_sum fun k hk => ?_
    exact mul_le_mul_of_nonneg_right (hD1 k hk) (hlam k hk)
  have h4 : (∑ k ∈ KQ, (∑ c ∈ F, if c ∈ dB k then beta c else 0) * lam k)
      = ∑ k ∈ KQ, lam k * ∑ c ∈ F, if c ∈ dB k then beta c else 0 := by
    refine Finset.sum_congr rfl fun k _ => mul_comm _ _
  calc (∑ r ∈ S, alpha r)
      ≤ ∑ r ∈ S, alpha r * (∑ k ∈ KQ, if r ∈ sep k then lam k else 0) := h1
    _ = ∑ k ∈ KQ, (∑ r ∈ S, if r ∈ sep k then alpha r else 0) * lam k := h2
    _ ≤ ∑ k ∈ KQ, (∑ c ∈ F, if c ∈ dB k then beta c else 0) * lam k := h3
    _ = _ := h4

open Classical in
/-- Rows of `S` not separated by any cut of the family `KQ`. -/
noncomputable def remainingRows (S : Finset R) (KQ : Finset ι) (sep : ι → Finset R) : Finset R :=
  S.filter fun r => ¬ ∃ k ∈ KQ, r ∈ sep k

/-- **L2 (interface form): remaining α-mass is dominated by the closure α-mass.** The only graph-level content
    is `hRemClosure`: a row not separated by any quotient cut belongs to the closure. -/
theorem remaining_alpha_le_closure_alpha
    (S Closure : Finset R) (KQ : Finset ι) (sep : ι → Finset R) (alpha : R → ℚ)
    (hRemClosure : ∀ r ∈ S, (¬ ∃ k ∈ KQ, r ∈ sep k) → r ∈ Closure)
    (hnonneg : ∀ r ∈ Closure, 0 ≤ alpha r) :
    (∑ r ∈ remainingRows S KQ sep, alpha r) ≤ ∑ r ∈ Closure, alpha r := by
  classical
  refine Finset.sum_le_sum_of_subset_of_nonneg ?_ ?_
  · intro r hr
    rw [remainingRows, Finset.mem_filter] at hr
    exact hRemClosure r hr.1 hr.2
  · intro r hrC _
    exact hnonneg r hrC

open Classical in
/-- **Combined skeleton split.** The whole row-price mass is bounded by the quotient payment (on the separated
    rows, L1) plus the closure α-mass (on the remaining rows, L2). The open core beyond this statement is exactly
    L3: bounding the closure α-mass by support + bank (BankedCutDomination for the full closure). -/
theorem alpha_paid_or_in_closure
    (S Closure : Finset R) (F : Finset E) (KQ : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (alpha : R → ℚ) (beta : E → ℚ) (lam : ι → ℚ)
    (halpha : ∀ r ∈ S, 0 ≤ alpha r)
    (hlam : ∀ k ∈ KQ, 0 ≤ lam k)
    (hcovSep : ∀ r ∈ S, (∃ k ∈ KQ, r ∈ sep k) →
        (1 : ℚ) ≤ ∑ k ∈ KQ, if r ∈ sep k then lam k else 0)
    (hD1 : ∀ k ∈ KQ, (∑ r ∈ S, if r ∈ sep k then alpha r else 0)
        ≤ ∑ c ∈ F, if c ∈ dB k then beta c else 0)
    (hRemClosure : ∀ r ∈ S, (¬ ∃ k ∈ KQ, r ∈ sep k) → r ∈ Closure)
    (hnonnegC : ∀ r ∈ Closure, 0 ≤ alpha r) :
    (∑ r ∈ S, alpha r)
      ≤ (∑ k ∈ KQ, lam k * ∑ c ∈ F, if c ∈ dB k then beta c else 0)
        + ∑ r ∈ Closure, alpha r := by
  classical
  set P : R → Prop := fun r => ∃ k ∈ KQ, r ∈ sep k with hP
  have hsplit : (∑ r ∈ S, alpha r)
      = (∑ r ∈ S.filter P, alpha r) + ∑ r ∈ S.filter (fun r => ¬ P r), alpha r :=
    (Finset.sum_filter_add_sum_filter_not S P alpha).symm
  -- L1 on the separated part
  have hL1 : (∑ r ∈ S.filter P, alpha r)
      ≤ ∑ k ∈ KQ, lam k * ∑ c ∈ F, if c ∈ dB k then beta c else 0 := by
    refine quotient_cuts_pay_alpha (S.filter P) F KQ sep dB alpha beta lam
      (fun r hr => halpha r (Finset.mem_filter.mp hr).1)
      hlam
      (fun r hr => hcovSep r (Finset.mem_filter.mp hr).1 (Finset.mem_filter.mp hr).2)
      (fun k hk => ?_)
    -- D1 restricted to the filtered subset follows from D1 on S (terms are nonnegative)
    refine le_trans (Finset.sum_le_sum_of_subset_of_nonneg (Finset.filter_subset P S) ?_) (hD1 k hk)
    intro r hrS _
    by_cases h : r ∈ sep k
    · simpa [h] using halpha r hrS
    · simp [h]
  -- L2 on the remaining part
  have hL2 : (∑ r ∈ S.filter (fun r => ¬ P r), alpha r) ≤ ∑ r ∈ Closure, alpha r := by
    refine Finset.sum_le_sum_of_subset_of_nonneg ?_ ?_
    · intro r hr
      have h := Finset.mem_filter.mp hr
      exact hRemClosure r h.1 h.2
    · intro r hrC _
      exact hnonnegC r hrC
  calc (∑ r ∈ S, alpha r)
      = (∑ r ∈ S.filter P, alpha r) + ∑ r ∈ S.filter (fun r => ¬ P r), alpha r := hsplit
    _ ≤ _ := add_le_add hL1 hL2


end RelaxedCoverSkeleton
end Erdos23Delta0
