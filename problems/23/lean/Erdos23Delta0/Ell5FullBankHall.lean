import Erdos23Delta0.Ell5FullBankInterface
import Erdos23Delta0.RelaxedCutCover

/-!
# Numeric Hall consequence of a full-bank relaxed-cover certificate

`Ell5FullBankInterface` packages the primal certificate primarily as a
`BankedCutDomination` / no-Farkas-dual object.  This module records the
parallel numeric consequence used by Branch-B and Gap#1 assembly:

if the same cut family satisfies the per-cut cardinal bound and all boundaries
lie in support plus off-support bank edges, then

  `25 * |S| <= 25 * |F| + 25 * Σ kap`.

The proof is still purely certificate algebra: off-support load is bounded by
the routed `q` flow, and the `q` flow is bounded by the sink capacities.
-/

namespace Erdos23Delta0
namespace Ell5FullBankHall

open Finset
open Ell5FullBankInterface

variable {R E JT ι : Type*} [DecidableEq R] [DecidableEq E]

/-- The off-support cut load of a full-bank certificate is bounded by total sink capacity. -/
theorem external_load_le_bank_of_cert
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ)
    (cert : FullBankRelaxedCoverCert S F O J K sep dB inc kap) :
    (∑ c ∈ O, RelaxedCutCover.load K cert.lam dB c) ≤ ∑ j ∈ J, kap j := by
  have hrouteSum :
      (∑ c ∈ O, RelaxedCutCover.load K cert.lam dB c)
        ≤ ∑ c ∈ O, ∑ j ∈ J, cert.q c j := by
    refine Finset.sum_le_sum fun c hc => ?_
    simpa [RelaxedCutCover.load] using cert.hroute c hc
  have hcapSum :
      (∑ c ∈ O, ∑ j ∈ J, cert.q c j) ≤ ∑ j ∈ J, kap j := by
    calc
      (∑ c ∈ O, ∑ j ∈ J, cert.q c j)
          = ∑ j ∈ J, ∑ c ∈ O, cert.q c j := by
            rw [Finset.sum_comm]
      _ ≤ ∑ j ∈ J, kap j := by
            exact Finset.sum_le_sum fun j hj => cert.hcap j hj
  exact le_trans hrouteSum hcapSum

/-- A full-bank certificate plus the per-cut cardinal bound gives the scaled Hall/bank inequality. -/
theorem hall_bound_of_fullBank_cert
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ)
    (cert : FullBankRelaxedCoverCert S F O J K sep dB inc kap)
    (hFO : Disjoint F O)
    (hdB : ∀ k ∈ K, dB k ⊆ F ∪ O)
    (hmcap : ∀ k ∈ K, ((sep k).card : ℚ) ≤ ((dB k).card : ℚ)) :
    25 * (S.card : ℚ) ≤ 25 * (F.card : ℚ) + 25 * (∑ j ∈ J, kap j) := by
  have hbankLoad :
      25 * (∑ c ∈ O, RelaxedCutCover.load K cert.lam dB c)
        ≤ 25 * (∑ j ∈ J, kap j) := by
    have h := external_load_le_bank_of_cert S F O J K sep dB inc kap cert
    nlinarith
  exact RelaxedCutCover.hall_absorbed_of_bank S F O hFO K cert.lam sep dB
    cert.hlam hdB hmcap cert.hcov cert.hcong (25 * (∑ j ∈ J, kap j)) hbankLoad


end Ell5FullBankHall
end Erdos23Delta0
