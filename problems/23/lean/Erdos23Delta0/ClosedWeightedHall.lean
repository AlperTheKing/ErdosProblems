import Erdos23Delta0.BankedWallRoutingFailure
import Erdos23Delta0.ClosedShoreExtraction

/-!
# Closed weighted Hall bridge

This module isolates the R3 closed-Hall dependency without pretending to prove
the graph-side completeness theorem.  The hard statement is named as
`ClosedWeightedHallCompleteness`: every weighted routing failure has a
full-escape-closed minimal deficient shore.

Given that hard statement and `PositiveRootBlockClosedExtraction`, the existing
closed-shore uncrossing theorem immediately gives a unique legal root for the
minimal closed deficiency.  This is the bookkeeping bridge consumed by the
later bank-rooted exchange/Farkas layer.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

open scoped BigOperators
open PortHall

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP}

/-- Closed weighted-Hall completeness for the concrete forced-escape closure.
This is a genuine wall-side hypothesis: the module records the exact shape
needed downstream, but does not assert the graph theorem. -/
def ClosedWeightedHallCompleteness (Q : AbstractEscapeQuotient I) : Prop :=
  ∀ {d : Dual I} {L : I.Port → ℚ},
    WeightedRoutingFailure d L →
      ∃ U : Finset Q.QComp,
        Q.fullClosure U = U ∧
          MinimalClosedDeficient Q L (Q.exposedPorts U)

/-- A closed weighted-Hall failure supplied by the completeness theorem has
one legal-incidence root, provided the positive-root extraction theorem is
available for the concrete closure. -/
theorem uniqueRoot_of_closedWeightedHallCompleteness
    {Q : AbstractEscapeQuotient I}
    (hHall : ClosedWeightedHallCompleteness Q)
    (hExtract : PositiveRootBlockClosedExtraction Q)
    {d : Dual I} {L : I.Port → ℚ}
    (hFail : WeightedRoutingFailure d L) :
    ∃ U : Finset Q.QComp,
      Q.fullClosure U = U ∧
        MinimalClosedDeficient Q L (Q.exposedPorts U) ∧
          ∀ D : LegalComponentPartition I (Q.exposedPorts U),
            Fintype.card D.K = 1 := by
  obtain ⟨U, hUclosed, hMin⟩ := hHall hFail
  refine ⟨U, hUclosed, hMin, ?_⟩
  intro D
  exact minimalClosedDeficient_has_unique_root_of_positiveExtraction
    hExtract L U hUclosed hMin D

end ClosedShore
end Wall
end Erdos23Delta0
