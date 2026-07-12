import Erdos23Delta0.CanonicalTightCorner

/-!
# Cross-state opposite-corner uncrossing

The cut functional below is attached only to the fixed labelled graph, not
to a selected row tuple.  Consequently two protection prefixes extracted in
different trace states may be uncrossed directly.  This file isolates the
algebraic R56 step: strict opposite-corner overweight forces a negative
intersection or union cut, and is therefore incompatible with nonnegative
switch loss.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CrossStateOppositeCorner

open CanonicalTightCorner

variable {V L : Type*} [DecidableEq V]

/-- If the two prefix losses are strictly smaller than twice the signed
opposite-corner weight, one of the two uncrossed corner cuts is negative. -/
theorem exists_negative_corner_of_overweight
    (labels : Finset L) (edge : L → Sym2 V) (weight : L → ℚ)
    (X Y : Finset V)
    (hoverweight :
      weightedCut labels edge weight X + weightedCut labels edge weight Y <
        2 * weightedBetween labels edge weight (X \ Y) (Y \ X)) :
    weightedCut labels edge weight (X ∩ Y) < 0 ∨
      weightedCut labels edge weight (X ∪ Y) < 0 := by
  have hcorner := weightedCut_four_corner labels edge weight X Y
  by_contra hnonnegative
  simp only [not_or] at hnonnegative
  have hI : 0 ≤ weightedCut labels edge weight (X ∩ Y) :=
    le_of_not_gt hnonnegative.1
  have hU : 0 ≤ weightedCut labels edge weight (X ∪ Y) :=
    le_of_not_gt hnonnegative.2
  linarith

/-- Nonnegative switch loss for every fixed-graph mask forbids strict
cross-state opposite-corner overweight. -/
theorem not_overweight_of_cut_nonnegative
    (labels : Finset L) (edge : L → Sym2 V) (weight : L → ℚ)
    (hnonnegative : ∀ S : Finset V,
      0 ≤ weightedCut labels edge weight S)
    (X Y : Finset V) :
    ¬(weightedCut labels edge weight X +
        weightedCut labels edge weight Y <
      2 * weightedBetween labels edge weight (X \ Y) (Y \ X)) := by
  intro hoverweight
  rcases exists_negative_corner_of_overweight
      labels edge weight X Y hoverweight with hI | hU
  · exact (not_lt_of_ge (hnonnegative (X ∩ Y))) hI
  · exact (not_lt_of_ge (hnonnegative (X ∪ Y))) hU

#print axioms exists_negative_corner_of_overweight
#print axioms not_overweight_of_cut_nonnegative

end CrossStateOppositeCorner
end Gamma
end Erdos23Delta0
