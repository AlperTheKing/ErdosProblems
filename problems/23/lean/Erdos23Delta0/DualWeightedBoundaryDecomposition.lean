import Erdos23Delta0.DualWeightedHallReduction

/-!
# Exact boundary decomposition for the dual-scaled Hall obstruction

The dual-scaled Hall deficiency has three routing pieces: unmatched port
price, D2 reserve, and unused scaled sink capacity.  The first two reserves
are nonnegative for a checked dual and a feasible partial routing.  This file
separates those exact arithmetic terms from the sole graph-side obligation:
constructing one cut whose dual-weighted boundary pays the unmatched price.
-/

namespace Erdos23Delta0
namespace Wall
namespace DualWeightedBoundaryDecomposition

open scoped BigOperators
open PortHall DualWeightedHallReduction

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP}

/-- Port mass already sent by a partial routing. -/
noncomputable def routedPortMass (P : Finset I.Port)
    (u : I.Port -> I.Sink -> ℚ) (p : I.Port) : ℚ :=
  ∑ s in legalNbr I P, u p s

/-- Sink mass received from the selected port shore. -/
noncomputable def routedSinkMass (P : Finset I.Port)
    (u : I.Port -> I.Sink -> ℚ) (s : I.Sink) : ℚ :=
  ∑ p in P, u p s

/-- Price of the selected load not yet represented by the partial routing. -/
noncomputable def unmatchedPortPrice (d : Dual I) (L : I.Port -> ℚ)
    (P : Finset I.Port) (u : I.Port -> I.Sink -> ℚ) : ℚ :=
  ∑ p in P, (L p - routedPortMass P u p) * d.gamma p

/-- Reserve supplied by the checked D2 inequalities on routed legal arcs. -/
noncomputable def d2Reserve (d : Dual I) (P : Finset I.Port)
    (u : I.Port -> I.Sink -> ℚ) : ℚ :=
  ∑ p in P, ∑ s in legalNbr I P, u p s * (d.delta s - d.gamma p)

/-- Reserve supplied by unused sink capacity in the dual-scaled LP. -/
noncomputable def unusedCapacityReserve (d : Dual I) (P : Finset I.Port)
    (u : I.Port -> I.Sink -> ℚ) : ℚ :=
  ∑ s in legalNbr I P, (I.cap s - routedSinkMass P u s) * d.delta s

/-- The signed dual value of one routed cut. -/
def cutGap (d : Dual I) (X : I.Cut) : ℚ :=
  cutAlpha d X - cutBeta d X - cutGamma d X

private theorem dualScaled_legalNbr (d : Dual I) (P : Finset I.Port) :
    legalNbr (dualScaledLP I d) P = legalNbr I P := by
  ext s
  simp only [mem_legalNbr]
  rfl

/-- Exact routing decomposition of the dual-scaled Hall deficiency.  No
positivity or legality hypothesis is needed for this identity. -/
theorem scaledDeficiency_eq_unmatched_sub_reserves
    (d : Dual I) (L : I.Port -> ℚ) (P : Finset I.Port)
    (u : I.Port -> I.Sink -> ℚ) :
    deficiencyQ (dualScaledLP I d) (dualScaledLoad d L) P =
      unmatchedPortPrice d L P u - d2Reserve d P u -
        unusedCapacityReserve d P u := by
  have hcomm :
      (∑ p in P, ∑ s in legalNbr I P, u p s * d.delta s) =
        ∑ s in legalNbr I P, ∑ p in P, u p s * d.delta s := by
    rw [Finset.sum_comm]
  rw [deficiencyQ, dualScaled_legalNbr]
  simp only [loadQ, capQ, dualScaledLoad_apply, dualScaledLP_cap]
  unfold unmatchedPortPrice d2Reserve unusedCapacityReserve
    routedPortMass routedSinkMass
  rw [hcomm]
  ring

/-- Exact cut-gap decomposition.  The graph geometry is confined to the
single signed boundary term `cutGap d X - unmatchedPortPrice ...`. -/
theorem cutGap_eq_scaledDeficiency_add_boundary_and_reserves
    (d : Dual I) (L : I.Port -> ℚ) (P : Finset I.Port)
    (u : I.Port -> I.Sink -> ℚ) (X : I.Cut) :
    cutGap d X =
      deficiencyQ (dualScaledLP I d) (dualScaledLoad d L) P +
        (cutGap d X - unmatchedPortPrice d L P u) +
        d2Reserve d P u + unusedCapacityReserve d P u := by
  rw [scaledDeficiency_eq_unmatched_sub_reserves]
  ring

/-- The weakest direct boundary inequality needed to turn the exact
decomposition into a D1-violating cut. -/
theorem scaledDeficiency_le_cutGap_of_boundary_bound
    (d : Dual I) (L : I.Port -> ℚ) (P : Finset I.Port)
    (u : I.Port -> I.Sink -> ℚ) (X : I.Cut)
    (hboundary :
      unmatchedPortPrice d L P u - cutGap d X <=
        d2Reserve d P u + unusedCapacityReserve d P u) :
    deficiencyQ (dualScaledLP I d) (dualScaledLoad d L) P <= cutGap d X := by
  rw [scaledDeficiency_eq_unmatched_sub_reserves]
  linarith

/-- D2 reserve is nonnegative when every positive routed entry is legal. -/
theorem d2Reserve_nonneg (d : Dual I) (hd : d.Checked)
    (P : Finset I.Port) (u : I.Port -> I.Sink -> ℚ)
    (hu_nonneg : forall p s, 0 <= u p s)
    (hu_legal : forall p s, u p s != 0 -> I.legal p s) :
    0 <= d2Reserve d P u := by
  unfold d2Reserve
  refine Finset.sum_nonneg fun p _ => Finset.sum_nonneg fun s _ => ?_
  by_cases hzero : u p s = 0
  · simp [hzero]
  · exact mul_nonneg (hu_nonneg p s) (sub_nonneg.mpr (hd.d2 p s (hu_legal p s hzero)))

/-- Unused-capacity reserve is nonnegative under the partial-routing sink
bounds. -/
theorem unusedCapacityReserve_nonneg (d : Dual I) (hd : d.Checked)
    (P : Finset I.Port) (u : I.Port -> I.Sink -> ℚ)
    (hu_sink : forall s : I.Sink, routedSinkMass P u s <= I.cap s) :
    0 <= unusedCapacityReserve d P u := by
  unfold unusedCapacityReserve
  exact Finset.sum_nonneg fun s _ =>
    mul_nonneg (sub_nonneg.mpr (hu_sink s)) (hd.delta_nonneg s)

#print axioms scaledDeficiency_eq_unmatched_sub_reserves
#print axioms cutGap_eq_scaledDeficiency_add_boundary_and_reserves
#print axioms scaledDeficiency_le_cutGap_of_boundary_bound
#print axioms d2Reserve_nonneg
#print axioms unusedCapacityReserve_nonneg

end DualWeightedBoundaryDecomposition
end Wall
end Erdos23Delta0
