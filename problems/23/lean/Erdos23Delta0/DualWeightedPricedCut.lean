import Erdos23Delta0.DualWeightedBoundaryDecomposition

/-!
# Exact dual-priced cut certificate

After the dual-scaled routing decomposition, all dependence on the chosen
partial routing cancels.  The remaining graph-side datum is one actual cut
whose checked dual price dominates the scaled Hall deficiency.  A certificate
therefore contains only the cut key; every rational quantity is recomputed.
-/

namespace Erdos23Delta0
namespace Wall
namespace DualWeightedPricedCut

open scoped BigOperators
open PortHall DualWeightedHallReduction
open DualWeightedBoundaryDecomposition

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP}

/-- The only supplied datum is an actual routed-cut key of the finite wall LP. -/
structure PricedCutCert (I : BankedWallLP) where
  cut : I.Cut

/-- Exact rational checker for the sole remaining boundary inequality. -/
noncomputable def checkPricedCut (d : Dual I) (L : I.Port → ℚ)
    (P : Finset I.Port) (cert : PricedCutCert I) : Bool :=
  decide (
    deficiencyQ (dualScaledLP I d) (dualScaledLoad d L) P ≤
      cutGap d cert.cut)

/-- The transfer routing cannot change the remaining signed margin. -/
theorem routingMargin_eq_cutGap_sub_scaledDeficiency
    (d : Dual I) (L : I.Port → ℚ) (P : Finset I.Port)
    (u : I.Port → I.Sink → ℚ) (X : I.Cut) :
    d2Reserve d P u + unusedCapacityReserve d P u -
        (unmatchedPortPrice d L P u - cutGap d X) =
      cutGap d X -
        deficiencyQ (dualScaledLP I d) (dualScaledLoad d L) P := by
  rw [scaledDeficiency_eq_unmatched_sub_reserves]
  ring

/-- Soundness exposes an exact nonnegative reserve; no claimed value is read
from the certificate. -/
theorem checkPricedCut_sound
    (d : Dual I) (L : I.Port → ℚ) (P : Finset I.Port)
    (cert : PricedCutCert I)
    (hcheck : checkPricedCut d L P cert = true) :
    ∃ r : ℚ,
      0 ≤ r ∧
        cutGap d cert.cut =
          deficiencyQ (dualScaledLP I d) (dualScaledLoad d L) P + r := by
  have hle :
      deficiencyQ (dualScaledLP I d) (dualScaledLoad d L) P ≤
        cutGap d cert.cut := by
    exact of_decide_eq_true hcheck
  refine ⟨cutGap d cert.cut -
      deficiencyQ (dualScaledLP I d) (dualScaledLoad d L) P,
    sub_nonneg.mpr hle, ?_⟩
  ring

/-- A positive scaled deficiency and an accepted priced cut contradict the D1
row indexed by that exact cut. -/
theorem noCheckedDual_of_pricedCut
    (d : Dual I) (hd : d.Checked)
    (L : I.Port → ℚ) (P : Finset I.Port)
    (hdef : 0 < deficiencyQ (dualScaledLP I d) (dualScaledLoad d L) P)
    (cert : PricedCutCert I)
    (hcert : checkPricedCut d L P cert = true) :
    False := by
  obtain ⟨r, hr, hgap⟩ := checkPricedCut_sound d L P cert hcert
  have hD1 : cutGap d cert.cut ≤ 0 := by
    unfold cutGap
    have h := hd.d1 cert.cut
    linarith
  linarith

/-- Existence of a checked key is definitionally the finite maximization
target `some cutGap ≥ scaled deficiency`. -/
theorem exists_pricedCut_iff
    (d : Dual I) (L : I.Port → ℚ) (P : Finset I.Port) :
    (∃ cert : PricedCutCert I, checkPricedCut d L P cert = true) ↔
      ∃ X : I.Cut,
        deficiencyQ (dualScaledLP I d) (dualScaledLoad d L) P ≤
          cutGap d X := by
  constructor
  · rintro ⟨cert, hcert⟩
    exact ⟨cert.cut, of_decide_eq_true hcert⟩
  · rintro ⟨X, hX⟩
    exact ⟨⟨X⟩, by exact decide_eq_true hX⟩

#print axioms routingMargin_eq_cutGap_sub_scaledDeficiency
#print axioms checkPricedCut_sound
#print axioms noCheckedDual_of_pricedCut
#print axioms exists_pricedCut_iff

end DualWeightedPricedCut
end Wall
end Erdos23Delta0
