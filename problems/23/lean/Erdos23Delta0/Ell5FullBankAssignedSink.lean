import Erdos23Delta0.Ell5FullBankInterface
import Erdos23Delta0.RelaxedCutCover

/-!
# Assigned-sink full-bank constructor

This module packages the common Gap#1 certificate pattern where each
off-support edge is routed to one legal bank sink.  Downstream work then only
has to prove the row-cover, support-congestion, and per-sink capacity
inequalities; the `q c j` matrix is constructed mechanically.
-/

namespace Erdos23Delta0
namespace Ell5FullBankAssignedSink

open Finset
open Ell5FullBankInterface

variable {R E JT ι : Type*} [DecidableEq R] [DecidableEq E] [DecidableEq JT]

/-- The cut-family load on an edge is nonnegative when all cut weights are nonnegative. -/
theorem load_nonneg
    (K : Finset ι) (lam : ι → ℚ) (dB : ι → Finset E)
    (hlam : ∀ k ∈ K, 0 ≤ lam k) (c : E) :
    0 ≤ RelaxedCutCover.load K lam dB c := by
  unfold RelaxedCutCover.load
  refine Finset.sum_nonneg fun k hk => ?_
  by_cases h : c ∈ dB k
  · simpa [h] using hlam k hk
  · simp [h]

/-- Route the full load of `c` to its assigned sink and zero to all others. -/
def assignedSinkQ
    (K : Finset ι) (lam : ι → ℚ) (dB : ι → Finset E)
    (sink : E → JT) (c : E) (j : JT) : ℚ :=
  if sink c = j then RelaxedCutCover.load K lam dB c else 0

/-- Summing the assigned-sink route over a sink set containing `sink c` recovers the full load. -/
theorem sum_assignedSinkQ_eq_load
    (K : Finset ι) (lam : ι → ℚ) (dB : ι → Finset E)
    (sink : E → JT) (J : Finset JT) {c : E} (hcJ : sink c ∈ J) :
    (∑ j ∈ J, assignedSinkQ K lam dB sink c j) =
      RelaxedCutCover.load K lam dB c := by
  classical
  rw [Finset.sum_eq_single (sink c)]
  · simp [assignedSinkQ]
  · intro j _hj hne
    have hneq : ¬ sink c = j := by
      intro h
      exact hne h.symm
    simp [assignedSinkQ, hneq]
  · intro hnot
    exact False.elim (hnot hcJ)

/-- Build a full-bank relaxed-cover certificate from a deterministic legal sink assignment. -/
def cert_of_assignedSink
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ)
    (lam : ι → ℚ) (sink : E → JT)
    (hlam : ∀ k ∈ K, 0 ≤ lam k)
    (hkap : ∀ j ∈ J, 0 ≤ kap j)
    (hcov : ∀ r ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if r ∈ sep k then lam k else 0)
    (hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ 1)
    (hsink : ∀ c ∈ O, sink c ∈ J)
    (hinc : ∀ c ∈ O, inc c (sink c))
    (hcap : ∀ j ∈ J,
      (∑ c ∈ O, assignedSinkQ K lam dB sink c j) ≤ kap j) :
    FullBankRelaxedCoverCert S F O J K sep dB inc kap where
  lam := lam
  q := assignedSinkQ K lam dB sink
  hlam := hlam
  hq := by
    intro c _hc j _hj
    by_cases h : sink c = j
    · simp [assignedSinkQ, h, load_nonneg K lam dB hlam c]
    · simp [assignedSinkQ, h]
  hkap := hkap
  hcov := hcov
  hcong := hcong
  hroute := by
    intro c hc
    rw [sum_assignedSinkQ_eq_load K lam dB sink J (hsink c hc)]
    rfl
  hcap := hcap
  hqinc := by
    intro c hc j _hj hpos
    by_cases h : sink c = j
    · simpa [h] using hinc c hc
    · have hzero : assignedSinkQ K lam dB sink c j = 0 := by
        simp [assignedSinkQ, h]
      rw [hzero] at hpos
      linarith

/-- Assigned-sink certificates imply banked cut-domination. -/
theorem bankedCutDomination_of_assignedSink
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ)
    (lam : ι → ℚ) (sink : E → JT)
    (hlam : ∀ k ∈ K, 0 ≤ lam k)
    (hkap : ∀ j ∈ J, 0 ≤ kap j)
    (hcov : ∀ r ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if r ∈ sep k then lam k else 0)
    (hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ 1)
    (hsink : ∀ c ∈ O, sink c ∈ J)
    (hinc : ∀ c ∈ O, inc c (sink c))
    (hcap : ∀ j ∈ J,
      (∑ c ∈ O, assignedSinkQ K lam dB sink c j) ≤ kap j) :
    BankedCutDominationCore.BankedCutDomination S F O J K sep dB inc kap := by
  exact bankedCutDomination_of_cert S F O J K sep dB inc kap
    (cert_of_assignedSink S F O J K sep dB inc kap lam sink
      hlam hkap hcov hcong hsink hinc hcap)

/-- Assigned-sink certificates exclude exact rational Farkas dual certificates. -/
theorem no_dualCert_of_assignedSink
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ)
    (lam : ι → ℚ) (sink : E → JT)
    (hlam : ∀ k ∈ K, 0 ≤ lam k)
    (hkap : ∀ j ∈ J, 0 ≤ kap j)
    (hcov : ∀ r ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if r ∈ sep k then lam k else 0)
    (hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ 1)
    (hsink : ∀ c ∈ O, sink c ∈ J)
    (hinc : ∀ c ∈ O, inc c (sink c))
    (hcap : ∀ j ∈ J,
      (∑ c ∈ O, assignedSinkQ K lam dB sink c j) ≤ kap j) :
    ¬ ∃ alpha beta gam del,
      BankedCutDominationCore.IsDualCert S F O J K sep dB inc kap alpha beta gam del := by
  exact no_dualCert_of_cert S F O J K sep dB inc kap
    (cert_of_assignedSink S F O J K sep dB inc kap lam sink
      hlam hkap hcov hcong hsink hinc hcap)


end Ell5FullBankAssignedSink
end Erdos23Delta0
