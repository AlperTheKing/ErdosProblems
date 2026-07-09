import Erdos23Delta0.Ell5FullBankHall

/-!
# Branch-B layer 24: pure UPO k=0 banked soundness wrapper

This layer does **not** assert existence of the full-bank certificate.  It is the
thin soundness wrapper requested by `BRANCH_B_LAYERS_V2_GPTPRO.md`: once a
full-bank relaxed-cover certificate is supplied, and the row-specific pure
demand is translated to the corresponding Hall defect, the legal bank capacities
absorb the pure UPO k=0 residual.
-/

namespace Erdos23Delta0
namespace BranchB
namespace PureUPOK0

open Finset
open Ell5FullBankInterface

variable {R E JT ι : Type*} [DecidableEq R] [DecidableEq E]

/-- Numeric bank frame for the pure UPO k=0 residual.  The four caps are the
legal bank currencies: door, vertex slack, C5/base, and prune. -/
structure PureUPOK0Frame where
  pureDemand : ℚ
  doorCap : ℚ
  vertexSlackCap : ℚ
  c5Cap : ℚ
  pruneCap : ℚ

/-- The target Branch-B pure-UPO bound: no top-cage eta reserve appears here. -/
def PureUPOK0Bound (fr : PureUPOK0Frame) : Prop :=
  fr.pureDemand ≤ fr.doorCap + fr.vertexSlackCap + fr.c5Cap + fr.pruneCap

/-- Total legal bank in the frame. -/
def totalBank (fr : PureUPOK0Frame) : ℚ :=
  fr.doorCap + fr.vertexSlackCap + fr.c5Cap + fr.pruneCap

theorem pureUPOK0Bound_iff (fr : PureUPOK0Frame) :
    PureUPOK0Bound fr ↔ fr.pureDemand ≤ totalBank fr := by
  rfl

/-- Soundness of a supplied full-bank certificate for the pure UPO k=0 residual.

The two row-specific translation obligations are explicit:
* `hdemand`: pure demand is at most the scaled Hall defect `25|S|-25|F|`;
* `hbank`: total sink capacity is paid by the legal bank currencies in `fr`.
-/
theorem pureUPOK0_of_fullBankCert
    (fr : PureUPOK0Frame)
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E)
    (inc : E → JT → Prop) (kap : JT → ℚ)
    (cert : FullBankRelaxedCoverCert S F O J K sep dB inc kap)
    (hFO : Disjoint F O)
    (hdB : ∀ k ∈ K, dB k ⊆ F ∪ O)
    (hmcap : ∀ k ∈ K, ((sep k).card : ℚ) ≤ ((dB k).card : ℚ))
    (hdemand : fr.pureDemand ≤ 25 * (S.card : ℚ) - 25 * (F.card : ℚ))
    (hbank : 25 * (∑ j ∈ J, kap j) ≤ totalBank fr) :
    PureUPOK0Bound fr := by
  rw [pureUPOK0Bound_iff]
  have hHall := Ell5FullBankHall.hall_bound_of_fullBank_cert
    S F O J K sep dB inc kap cert hFO hdB hmcap
  linarith


end PureUPOK0
end BranchB
end Erdos23Delta0
