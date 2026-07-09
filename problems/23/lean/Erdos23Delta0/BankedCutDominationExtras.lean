import Erdos23Delta0.BankedCutDominationCore

/-!
# Banked cut-domination wrappers

Small interface lemmas for the Gap#1 no-Farkas route.  The core module proves
`dualCert_iff_not_bankedCutDomination`; downstream code usually wants the
contrapositive package: if no exact rational dual certificate exists, then the
banked domination inequality holds.
-/

namespace Erdos23Delta0
namespace BankedCutDominationExtras

open Finset
open BankedCutDominationCore

variable {R E JT ι : Type*} [DecidableEq R] [DecidableEq E]

/-- The δ-eliminated bank cost is nonnegative when all capacities are nonnegative. -/
theorem bankCost_nonneg (J : Finset JT) (kap : JT → ℚ) (O : Finset E)
    (inc : E → JT → Prop) (gam : E → ℚ)
    (hkap : ∀ j ∈ J, 0 ≤ kap j) :
    0 ≤ bankCost J kap O inc gam := by
  refine Finset.sum_nonneg fun j hj => ?_
  exact mul_nonneg (hkap j hj) (sinkPrice_nonneg O inc gam j)

/-- No exact rational dual certificate is equivalent to banked cut-domination. -/
theorem not_dualCert_iff_bankedCutDomination
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E) (inc : E → JT → Prop) (kap : JT → ℚ)
    (hkap : ∀ j ∈ J, 0 ≤ kap j) :
    (¬ ∃ alpha beta gam del, IsDualCert S F O J K sep dB inc kap alpha beta gam del)
      ↔ BankedCutDomination S F O J K sep dB inc kap := by
  classical
  constructor
  · intro hno
    by_contra hnot
    exact hno ((dualCert_iff_not_bankedCutDomination S F O J K sep dB inc kap hkap).mpr hnot)
  · intro hdom hcert
    exact (dualCert_iff_not_bankedCutDomination S F O J K sep dB inc kap hkap).mp hcert hdom

/-- Forward-use form of `not_dualCert_iff_bankedCutDomination`. -/
theorem bankedCutDomination_of_no_dualCert
    (S : Finset R) (F O : Finset E) (J : Finset JT) (K : Finset ι)
    (sep : ι → Finset R) (dB : ι → Finset E) (inc : E → JT → Prop) (kap : JT → ℚ)
    (hkap : ∀ j ∈ J, 0 ≤ kap j)
    (hno : ¬ ∃ alpha beta gam del,
      IsDualCert S F O J K sep dB inc kap alpha beta gam del) :
    BankedCutDomination S F O J K sep dB inc kap :=
  (not_dualCert_iff_bankedCutDomination S F O J K sep dB inc kap hkap).mp hno


end BankedCutDominationExtras
end Erdos23Delta0
